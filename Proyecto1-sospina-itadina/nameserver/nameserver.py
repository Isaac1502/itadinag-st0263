try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

import os, json, copy, time
import random
from uuid import uuid4
from functools import reduce
from operator import getitem
import rpyc

from threading import Thread


def run_cmd_storage_servers(formatted_cmd_str, storage_servers):
    for ss in storage_servers:
        ss = ss.split(":")
        try:
            conn = rpyc.connect(ss[0], ss[2])
            conn.root.run_shell_cmd(formatted_cmd_str)
            print('Run "{}" in {}'.format(formatted_cmd_str, ss[0] + ":" + ss[2]))
        except ConnectionRefusedError:
            print(
                'Error while trying to connect to {} to run cmd "{}"'.format(
                    ss, formatted_cmd_str
                )
            )


def ask_ss_to_forward_blocks(source, destinations, blocks):
    print("Asking {} to distribute {} to ss {}".format(source, blocks, destinations))
    src = src.split(":")
    try:
        conn = rpyc.connect(source[0], source[2])
        conn.root.forward_my_blocks(blocks, destinations)
    except ConnectionRefusedError:
        print(
            "Connection refused by {} while trying to ask to forward blocks.".format(
                source
            )
        )


def send_directory_structure_to_sync(target, structure):
    ss = target.split(":")
    try:
        conn = rpyc.connect(ss[0], ss[2])
        conn.root.adapt_this_directory_structure(json.dumps(structure))
        print("Send directory structure to {} for syncing".format(target))
    except ConnectionRefusedError:
        print(
            "Connection refused by {} while trying to send dir structure".format(target)
        )


def this_ss_is_alive(ip, port):
    try:
        conn = rpyc.connect(ip, int(port))
        conn.close()
        return True
    except ConnectionRefusedError:
        return False


class NameServerService(rpyc.Service):
    config = None
    struct = {}
    ss_blocks_map = {}
    ABSOLUTE_ROOT = None  # root directory in storage servers /ken
    STRUCT_ROOT = None
    searched_files = []

    def __init__(self):
        self.exposed_refresh()
        print("Name server started...")
        thread = Thread(target=self.check_aliveness, args=(0,), daemon=True)
        thread.start()

    def on_connect(self, conn):
        sock = conn._channel.stream.sock
        print("New connection: ", sock.getpeername())

    def on_disconnect(self, conn):
        sock = conn._channel.stream.sock
        print("Connection terminated: ", sock.getpeername())

    def exposed_refresh(self):
        configParser = ConfigParser()
        configParser.read("nameserver.conf")
        self.config = dict(configParser["default"])

        self.ABSOLUTE_ROOT = self.config["volume_name"]
        self.STRUCT_ROOT = self.ABSOLUTE_ROOT[1:]

        self.refresh_struct()
        self.refresh_ss_blocks_map()
        print("DFS Refreshed.")

        return self.get_return(1, "System refreshed.")

    def refresh_struct(self):
        # Load DFS Structure
        with open(self.config.get("dfs_struct_map_path"), "r") as input_file:
            try:
                data = json.load(input_file)
            except:
                data = None
        if data is None or data == "" or len(data) == 0:
            data = {}
        self.struct = data
        print("=== RELOADED: Directory Structure ===")

    def save_struct(self):
        with open(self.config.get("dfs_struct_map_path"), "w") as out_file:
            json.dump(self.struct, out_file)
        print("=== UPDATED: Directory Structure ===")
        self.refresh_struct()

    def refresh_ss_blocks_map(self):
        # Load storage server / storage node blocks map
        with open(self.config.get("ss_blocks_map_path"), "r") as input_file:
            self.ss_blocks_map = json.load(input_file)
        print("=== RELOADED: Server blocks mapping ===")

    def save_ss_blocks_map(self):
        with open(self.config.get("ss_blocks_map_path"), "w") as output_file:
            json.dump(self.ss_blocks_map, output_file)
        print("=== UPDATED: Server blocks mapping ===")
        self.refresh_ss_blocks_map()

    def path_list(self, path):
        path = (
            path.replace("/", " ").strip().split(" ")
        )  # eg. ken/outer/inner --> [ken, outer, inner]
        return [x for x in path if len(x.strip()) > 0]

    # parse absolute path corresponding to the /ken disk in storage servers
    def absolute_path(self, path):
        # check if already begins with /ken
        if path[:1] != "/":
            path = "/" + path
        if path[:4] != self.ABSOLUTE_ROOT:
            path = os.path.join(self.ABSOLUTE_ROOT, path)
        return path

    def exposed_get_alive_servers(self, max_needed=-1):
        out = []
        i = 0
        for name, value in self.ss_blocks_map.items():
            if value[0] == 1:
                out.append(name)
                i += 1
                if max_needed > 0 and i == max_needed:
                    return out
        return out

    def find_distribute_blocks(self, source, target_blocks):
        if len(target_blocks) == 0:
            return

        alive_servers = self.exposed_get_alive_servers()
        if source in alive_servers:
            alive_servers.remove(source)

        if len(alive_servers) < 1:
            print("No other alive servers to forward blocks from dead servers to.")
            return False

        for block in target_blocks:
            temp = alive_servers
            source_ss = self.exposed_get_ss_having_this_block(
                block, to_exclude=[source]
            )
            temp = list(set(temp) - set(source_ss))

            if source_ss in temp:
                temp.remove(source_ss)
            ask_ss_to_forward_blocks(source_ss[0], temp, [block])

        print("{} blocks found & distributed.".format(len(target_blocks)))
        return True

    def exposed_mark_new_block(self, block_id, ss):
        self.ss_blocks_map[ss][1].append(block_id)
        self.save_ss_blocks_map()
        print("New block {} at {}. Presence marked.".format(block_id, ss))

    def delete_block_from_ss(self, block_id, ss):
        if block_id in self.ss_blocks_map[ss][1]:
            self.ss_blocks_map[ss][1].remove(block_id)
            self.save_ss_blocks_map()
            print('Block "{}" deleted.'.format(block_id))

    def mark_server_alive(self, ss_id):
        self.ss_blocks_map[ss_id][0] = 1
        self.ss_blocks_map[ss_id][1] = []
        send_directory_structure_to_sync(ss_id, self.struct)
        print('Marked {} as "alive".'.format(ss_id))

    def check_aliveness(self, check_count):
        check_count += 1
        print("Checking aliveness of storage servers... ({})".format(check_count))
        modified = False
        for name, value in self.ss_blocks_map.items():
            ss = name.split(":")
            if this_ss_is_alive(ss[0], ss[2]):
                if int(value[0]) == 0:
                    self.mark_server_alive(name)
                    modified = True
            else:
                if int(value[0]) == 1:
                    self.ss_blocks_map[name][0] = 0
                    print("Marking {} as dead.".format(name))
                    if len(value[1]) > 1:
                        self.find_distribute_blocks(name, value[1])
                        modified = True

        if modified:
            self.save_ss_blocks_map()
        # aliveness check interval
        time.sleep(int(self.config.get("check_ss_aliveness_interval")))
        # repeat the process (dinamically)
        self.check_aliveness(check_count)

    def exposed_get_ss_having_this_block(self, block_id, max_needed=-1, to_exclude=[]):
        i = 0
        out = []
        for name, value in self.ss_blocks_map.items():
            if value[0] == 1 and block_id in value[1]:
                if name not in to_exclude:
                    i += 1
                    out.append(name)
                    if max_needed > 0 and i >= max_needed:
                        break
        return out

    def get_return(self, status=0, message="", data={}, nsconfig=False):
        result = {"status": status, "message": message, "data": data}
        if nsconfig:
            result["nsconfig"] = self.config
        result["dfs"] = self.struct
        return json.dumps(result)

    def exposed_initialize(self, forced=False):
        if forced or not bool(self.struct):
            self.struct[self.STRUCT_ROOT] = {}
            self.save_struct()

            for i, key in enumerate(self.ss_blocks_map.keys()):
                self.ss_blocks_map[key][1] = []
            self.save_ss_blocks_map()
            run_cmd_storage_servers(
                "sudo rm -rf {}/*".format(self.ABSOLUTE_ROOT),
                self.exposed_get_alive_servers(),
            )

            status = 1
            message = "Successfully initialized."
        else:
            status = 0
            message = "DFS already initialized."

        return self.get_return(
            status, message, {"alive_servers": self.exposed_get_alive_servers()}
        )

    def exposed_get(self, path):
        path = self.path_list(path)
        try:
            res = reduce(getitem, path, self.struct)
            status = 1
            message = "Resource found!"
            data = {} if not bool(res) or res == "" else res

        except:
            status = 0
            message = "No resource found on given path!"
            data = {}

        return self.get_return(status, message, data, nsconfig=True)

    def exposed_mkdir(self, path):
        path = self.path_lsit(path)
        data = self.struct
        for key in path:
            try:
                data = data[key]
            except:
                data[key] = {}
                data = data[key]
        self.save_struct()
        path - self.absolute_path("/".join(path))
        print(path)
        run_cmd_storage_servers(
            "sudo mkdir -p {}".format(path), self.exposed_get_alive_servers()
        )
        return self.get_return(1, "New directory created.")

    def exposed_new_file(self, struct_path, ss_block_map):
        path = self.path_list(struct_path)
        data = self.struct

        blocks = []
        for x in ss_block_map:
            if x[1] not in blocks:
                blocks.append(x[1])
            self.exposed_mark_new_block(x[1], x[0])

        for key in path[:-1]:
            data = data[key]
        data[path[-1]] = {}
        data["blocks"] = blocks

        self.save_struct()
        return self.get_return(1, "File put in remote directory.")

    def recursive_file_search(self, dir, struct_content):
        try:
            blocks = struct_content["blocks"]
            self.searched_files.append([dir, blocks])
            return
        except:
            for key, value in struct_content.items():
                temp = self.recursive_file_search(key, value)

    def exposed_files_in_directory(self, dir, struct_content, max_needed=-1):
        pass

    def exposed_delete(self):
        pass

    def exposed_copy(self):  # TODO
        pass

    def exposed_move(self):  # TODO
        pass


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    port = 18860

    t = ThreadedServer(NameServerService(), port=port)
    print("Server details ({}, {})".format(t.host, port))
    t.start()
