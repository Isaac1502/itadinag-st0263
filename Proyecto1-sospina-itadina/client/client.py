from prompt_toolkit import print_formatted_text as print, HTML
from prompt_toolkit.styles import Style

import sys
if sys.version_info < (3, 5):
  print('> Please use Python version 3.5 or above!')
  sys.exit(0)

style = Style.from_dict({
  'orange': '#ff7e0b',
  'red': '#e74c3c',
  'green': '#22b66c',
  'blue': '#0a84ff',
  'i': 'italic',
  'b': 'bold',
})

try:
  import rpyc
except ModuleNotFoundError:
  print(HTML('> <red>Install <orange>rpyc</orange> module first.</red>'))
  sys.exit(0)

try:
  from tqdm import tqdm
except ModuleNotFoundError:
  print(HTML('> <red>Install <orange>tqdm</orange> module first.</red>\n > sudo pip3 install tqdm\n'))
  sys.exit(0)

CONN = None
NS_IP = None
NS_PORT = None


