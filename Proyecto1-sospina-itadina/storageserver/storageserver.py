import sys
import rpyc

class StorageServerService(rpyc.Service):
    def __init__(self):
        self.storage = {}

def main(port=18861):
  from rpyc.utils.server import ThreadedServer
  t = ThreadedServer(StorageServerService(),port=port)
  print('Server details: ({}, {})'.format(t.host, port))
  t.start()

if __name__=="__main__":
  args = sys.argv[1:]
  if len(args)>1:
    print('Wrong usage: You can only specify [port] as argument.')
    sys.exit(0)
  elif len(args)==0:
    port = 18861
  else:
    port = int(args[0])
  main(port)