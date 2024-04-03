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

    def exposed_refresh(self):
        pass

    def check_aliveness(self):
        pass


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    port = 18860

    t = ThreadedServer(NameServerService(), port=port)
    print("Server details ({}, {})".format(t.host, port))
    t.start()
