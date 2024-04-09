try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

import os, json, copy, time
import random
from uuid import uuid4
from functools import reduce
from operator import getitem
import rpyc

from threading import Thread


# to perform same operation on each server, thereby syncing structure
def run_cmd_storage_servers(formatted_cmd_str, data_nodes):
    for datanode in data_nodes:
        datanode = datanode.split(":")
        try:
            conn = rpyc.connect(datanode[0], datanode[2])
            conn.root.run_shell_cmd(formatted_cmd_str)
            print(
                'Run "{}" in {}'.format(
                    formatted_cmd_str, datanode[0] + ":" + datanode[2]
                )
            )
        except ConnectionRefusedError:
            print(
                'Error while trying to connect to {} to run cmd "{}"'.format(
                    datanode, formatted_cmd_str
                )
            )


# ask storage server to forward these blocks from him to targets randomly
def ask_dn_to_forward_blocks(src, dests, blocks):
    print("Asking {} to distribute {} to datanode {}".format(src, blocks, dests))
    src = src.split(":")
    try:
        conn = rpyc.connect(src[0], src[2])
        conn.root.forward_my_blocks(blocks, dests)
    except ConnectionRefusedError:
        print(
            "Connection refused by {} while trying to ask to forward blocks".format(src)
        )


def send_directory_structure_to_sync(target, structure):
    datanode = target.split(":")
    try:
        conn = rpyc.connect(datanode[0], datanode[2])
        conn.root.adapt_this_directory_structure(json.dumps(structure))
        print("Send dir structure to {} for syncing.".format(target))
    except ConnectionRefusedError:
        print(
            "Connection refused by {} while trying to send dir structure.".format(
                target
            )
        )


# checking if given storage server is accessible
def this_dn_is_alive(ip, port):
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
    ABSOLUTE_ROOT = None  # /ken    i.e. root in data nodes
    STRUCT_ROOT = None  # ken     i.e. root in file structure here
    searched_files = []

    def __init__(self):
        self.exposed_refresh()
        print("Name server started...")
        thread = Thread(target=self.check_aliveness, args=(0,), daemon=True)
        thread.start()

    def on_connect(self, conn):
        sock = conn._channel.stream.sock
        print("New connection:", sock.getpeername())

    def on_disconnect(self, conn):
        sock = conn._channel.stream.sock
        print("Connection terminated:", sock.getpeername())

    def exposed_refresh(self):
        # instantiate & read configuration file
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
        print("Directory structure RELOADED.")

    def save_struct(self):
        with open(self.config.get("dfs_struct_map_path"), "w") as out_file:
            json.dump(self.struct, out_file)
        print("Directory structure UPDATED.")
        self.refresh_struct()

    def refresh_ss_blocks_map(self):
        # Load Storage Server Blocks Map
        with open(self.config.get("ss_blocks_map_path"), "r") as input_file:
            self.ss_blocks_map = json.load(input_file)
        print("Server-blocks mapping RELOADED.")

    def save_ss_blocks_map(self):
        with open(self.config.get("ss_blocks_map_path"), "w") as out_file:
            json.dump(self.ss_blocks_map, out_file)
        print("Server-blocks mapping UPDATED.")
        self.refresh_ss_blocks_map()

    # given path a/b/c, return [a, b, c]
    def path_list(self, path):
        path = path.replace("/", " ").strip().split(" ")
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

    def find_distribute_blocks(self, src, target_blocks):
        if len(target_blocks) == 0:
            return

        alive_servers = self.exposed_get_alive_servers()
        if src in alive_servers:
            alive_servers.remove(src)

        if len(alive_servers) < 1:
            print("No other alive servers to forward blocks from dead servers to.")
            return False

        for block in target_blocks:
            temp = alive_servers
            source_dn = self.exposed_get_dn_having_this_block(block, to_exclude=[src])
            temp = list(set(temp) - set(source_dn))

            if source_dn in temp:
                temp.remove(source_dn)
            ask_dn_to_forward_blocks(source_dn[0], temp, [block])

        print("{} blocks found & distributed.".format(len(target_blocks)))
        return True

    def exposed_mark_new_block(self, block_id, dn):
        self.ss_blocks_map[dn][1].append(block_id)
        self.save_ss_blocks_map()
        print("New block {} at {}. Presence marked.".format(block_id, dn))

    def delete_block_from_dn(self, block_id, dn):
        if block_id in self.ss_blocks_map[dn][1]:
            self.ss_blocks_map[dn][1].remove(block_id)
            self.save_ss_blocks_map()
            print('Block "{}" deleted.'.format(block_id))

    # mark server alive as well as sync directory structure
    def mark_server_alive(self, dn_id):
        self.ss_blocks_map[dn_id][0] = 1
        self.ss_blocks_map[dn_id][1] = []
        send_directory_structure_to_sync(dn_id, self.struct)
        print('Marked {} as "alive".'.format(dn_id))

    def check_aliveness(self, check_count):
        # check aliveness & take actions
        check_count += 1
        print("Checking aliveness of data nodes...({})".format(check_count))
        modified = False
        for name, value in self.ss_blocks_map.items():
            dn = name.split(":")
            if this_dn_is_alive(dn[0], dn[2]):
                if int(value[0]) == 0:
                    self.mark_server_alive(name)  # set alive flag if was not before
                    modified = True
            else:
                if int(value[0]) == 1:
                    self.ss_blocks_map[name][0] = 0
                    print('Marking {} as "dead".'.format(name))
                    if len(value[1]) > 0:
                        self.find_distribute_blocks(name, value[1])
                    modified = True

        if modified:
            self.save_ss_blocks_map()

        # sleep for this time
        time.sleep(int(self.config.get("check_ss_aliveness_interval")))
        # repeat the process again
        self.check_aliveness(check_count)

    def exposed_get_dn_having_this_block(self, block_id, max_needed=-1, to_exclude=[]):
        i = 0
        out = []
        for key, value in self.ss_blocks_map.items():
            if value[0] == 1 and block_id in value[1]:
                if key not in to_exclude:
                    i += 1
                    out.append(key)
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

        except (KeyError, TypeError):
            status = 0
            message = "No resource found on given path!"
            data = {}

        return self.get_return(status, message, data=data, nsconfig=True)

    def exposed_mkdir(self, path):
        path = self.path_list(path)
        data = self.struct
        for key in path:
            try:
                data = data[key]
            except:
                data[key] = {}
                data = data[key]
        self.save_struct()
        path = self.absolute_path("/".join(path))
        print(path)
        run_cmd_storage_servers(
            "sudo mkdir -p {}".format(path), self.exposed_get_alive_servers()
        )
        return self.get_return(1, "New directory created.")

    # Note that client will send the file directly to the storage servers.
    def exposed_new_file(self, struct_path, ss_block_map):
        path = self.path_list(struct_path)
        data = self.struct

        blocks = []
        # ss_block_map is like [['ss1', 'sdjal83923s1'], ['ss2', 'sfaoir830ds2']]
        for x in ss_block_map:
            if x[1] not in blocks:
                blocks.append(x[1])
            self.exposed_mark_new_block(x[1], x[0])

        for key in path[:-1]:
            data = data[key]
        data[path[-1]] = {}
        data = data[path[-1]]

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
        self.searched_files = []
        self.recursive_file_search(dir, struct_content)
        result = copy.deepcopy(self.searched_files)
        self.searched_files = []

        total = len(result)
        result = (
            result[: int(max_needed)]
            if max_needed > 0 and total > max_needed
            else result
        )
        return result

    def exposed_delete(self, path, part_of_moving=False, force_delete=False):
        path = path[:-1] if path[-1] == "/" else path
        keys = self.path_list(path)

        temp = json.loads(self.exposed_get(path))
        if temp["status"] == 0:
            return self.get_return(0, "Resource not found at {}".format(path))

        # ask for confirmation before deleting if directory not empty.
        data = self.struct
        for key in keys[:-1]:
            data = data[key]

        # delete all block mappings before deleting the files if any
        temp = data
        files_inside = self.exposed_files_in_directory(keys[-1], temp[keys[-1]])
        print(files_inside)

        if len(files_inside) > 0:
            if not force_delete:
                return self.get_return(0, "A file or directory with files in it given!")

        target_dn = self.exposed_get_alive_servers()
        for file_name, blocks in files_inside:
            for dn in target_dn:
                for block in blocks:
                    self.delete_block_from_dn(block, dn)

        del data[keys[-1]]
        self.save_struct()

        if not part_of_moving:
            run_cmd_storage_servers(
                "sudo rm -rf {}".format(self.absolute_path(path)),
                self.exposed_get_alive_servers(),
            )
        return self.get_return(1, "Deleted resource at {}".format(path))


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    port = 18860
    t = ThreadedServer(NameServerService(), port=port)
    print("Server details ({}, {})".format(t.host, port))
    t.start()
