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


class NameServerService(rpyc.Service):
    config = None
    struct = {}
    ss_blocks_map = {}
    ABSOLUTE_ROOT = None  # root directory in storage servers /ken
    STRUCT_ROOT = None
    searched_files = []


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    port = 18860

    t = ThreadedServer(NameServerService(), port=port)
    print("Server details ({}, {})".format(t.host, port))
    t.start()
