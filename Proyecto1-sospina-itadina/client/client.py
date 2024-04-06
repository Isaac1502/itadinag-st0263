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
