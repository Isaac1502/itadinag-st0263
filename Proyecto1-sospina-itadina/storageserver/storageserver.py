import sys
import rpyc


class StorageServerService(rpyc.Service):
  ROOT = "/ken"

  def __init__(self):
    print("StorageServerService initialized...")

  def on_connect(self, conn):
    sock = conn._channel.stream.sock
    print("Connection established with", sock.getpeername())

  def on_disconnect(self, conn):
    sock = conn._channel.stream.sock
    print("Connection closed with", sock.getpeername())


def main(port=18861):
  from rpyc.utils.server import ThreadedServer

  t = ThreadedServer(StorageServerService(), port=port)
  print("Server details: ({}, {})".format(t.host, port))
  t.start()


  if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1:
        print("Wrong usage: You can only specify [port] as argument.")
        sys.exit(0)
    elif len(args) == 0:
        port = 18861
    else:
        port = int(args[0])
    main(port)
