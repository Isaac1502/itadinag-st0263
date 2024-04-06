import sys
import rpyc
import os

# Methods exposed to clients using rpyc
class StorageServerService(rpyc.Service):
  ROOT = "/ken"

  def __init__(self):
    print("StorageServerService initialized...")

  def log_new_connection(self, conn):
    sock = conn._channel.stream.sock
    print("Connection established with", sock.getpeername())

  def log_connection_termination(self, conn):
    sock = conn._channel.stream.sock
    print("Connection closed with", sock.getpeername())

  def parse_path(self, path): # ensure_root_directory
    if path[:4]!=self.ROOT: 
      path = os.path.join(self.ROOT, path)
    return path
  
  def exposed_put(self, block_path, data): # store_data
    # put given file to this path
    path = self.ensure_root_directory(block_path)
    
    self.exposed_run_shell_cmd('sudo echo "">{}'.format(block_path))
    with open(block_path, 'wb') as f:
      f.write(data)
    print('Block "{}" stored.'.format(block_path))

  def exposed_get(self, block_path): # retrieve_data
    if not os.path.isfile(block_path): 
      return None
    with open(block_path, 'rb') as file:
      data = file.read()
    print('Block "{}" requested.'.format(block_path.rsplit("/", 1)[1]))
    return data

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
