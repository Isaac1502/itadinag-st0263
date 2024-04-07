from __future__ import unicode_literals, print_function
from prompt_toolkit import print_formatted_text as print, HTML
from prompt_toolkit.styles import Style

import os
import sys

if sys.version_info < (3, 5):
    print("> Please use Python version 3.5 or above!")
    sys.exit(0)

import math
import time
import random
from uuid import uuid4
import json

style = Style.from_dict(
    {
        "orange": "#ff7e0b",
        "red": "#e74c3c",
        "green": "#22b66c",
        "blue": "#0a84ff",
        "i": "italic",
        "b": "bold",
    }
)

try:
    import rpyc
except ModuleNotFoundError:
    print(HTML("> <red>Install <orange>rpyc</orange> module first.</red>"))
    sys.exit(0)

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    print(
        HTML(
            "> <red>Install <orange>tqdm</orange> module first.</red>\n > sudo pip3 install tqdm\n"
        )
    )
    sys.exit(0)

CONN = None
NS_IP = None
NS_PORT = None


def connect_to_ns(count_retry=1, max_retry=3):
    global CONN
    print(HTML("<orange>Connecting to nameserver...</orange>"))
    try:
        CONN = rpyc.connect(NS_IP, NS_PORT)
    except ConnectionError:
        CONN = None

    time.sleep(1)

    if CONN is None:
        print(HTML("<red>Connection couldn't be established.\n</red>"))
        time.sleep(1)
        if count_retry <= max_retry:
            print("Attempts so far = {}. Let's retry!".format(count_retry))
            return connect_to_ns(count_retry + 1, max_retry)
        else:
            print("Maximum allowed attempts made. Closing the application now!\n")
            return False
    else:
        print(HTML("<green>Connected!</green>"))
        time.sleep(1)
        return True


def ns_is_responding():
    global CONN
    try:
        temp = CONN.root.refresh()
        return True
    except EOFError:
        CONN = None
        print(HTML("<red>Error</red>: Connection to nameserver lost!"))
        time.sleep(0.7)
        print(HTML("<green>Retrying</green> in 5 seconds..."))
        time.sleep(5)

        return True if connect_to_ns() else False


def put_in_ss(ss, remote_path, block_name, block_data):
    ss = ss.split(":")
    try:
        conn = rpyc.connect(ss[1], ss[2])
        target_path = os.path.join(remote_path, block_name)
        conn.root.put(target_path, block_data)
    except ConnectionRefusedError:
        print(
            "Connection refused by {} while trying to put block {}".format(
                ss, block_name
            )
        )
    return None


def get_from_ss(ss, remote_path):
    ss = ss.split(":")
    try:
        conn = rpyc.connect(ss[1], ss[2])
        return conn.root.get(remote_path)
    except ConnectionRefusedError:
        print("Connection refused by {} while trying to get {}".format(ss, remote_path))


def parse_size_from_bytes(num):
    num = float(num)
    # this function will convert bytes to MB.... GB... etc
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return "%3.2f %s" % (num, x)
        num /= 1024.0


def prettyDictionary(t, s):
    for key in sorted(t.keys()):
        if "blocks" in t[key]:
            print(HTML("   " * (s) + "|- " + str(key)))
        else:
            key_str = "root" if key == "ken" else key
            if key_str == "root":
                print(HTML(" <b>ROOT</b>"))
            else:
                print(HTML("   " * s + "|- <b><green>" + str(key_str) + "</green></b>"))

            if not isinstance(t[key], list):
                prettyDictionary(t[key], s + 1)


from cmd import Cmd


class MyPrompt(Cmd):
    global CONN
    ABSOLUTE_ROOT = "/ken"
    CURRENT_DIR = "/ken"
    prompt = "[KEN-DFS] (.) >> "
    intro = "Welcome to KEN Distributed File System.\n > Type '?' or 'help' to see available commands.\n > The root volume is /ken/ \n"

    def preloop(self):
        print(HTML("\n------------- <green>Session Started</green> -------------\n"))

    def parse_args(self, cmd_name, args, min_required=0, max_required=float("inf")):
        args = args.strip()
        args = args.split(" ") if len(args) > 0 else args
        N = len(args)

        if N < min_required or N > max_required:
            if min_required == max_required:
                required = min_required
            else:
                required = "{} ".format(min_required)
                if math.isinf(max_required):
                    required += "or more"
                else:
                    required += "to {}".format(max_required)

            print(
                HTML(
                    "<red>Error</red>: <b>{}</b> expected <orange>{}</orange> args, got <orange>{}</orange>.".format(
                        cmd_name, required, N
                    )
                )
            )
            print(
                HTML(
                    "<green><b>TIP</b></green>: Try <b>help {}</b> for correct usage.\n".format(
                        cmd_name
                    )
                )
            )
            return None
        return args
