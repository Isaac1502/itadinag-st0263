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

    def check_aliveness(self):
        pass

    def get_return():
        pass


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    port = 18860

    t = ThreadedServer(NameServerService(), port=port)
    print("Server details ({}, {})".format(t.host, port))
    t.start()
