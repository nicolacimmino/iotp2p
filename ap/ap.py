#!/usr/bin/env python
#
# Proof of concept implementation of an Access Point for IoT P2P
#
# Nicola Cimmino 2013
#
# We make use of https://github.com/jpbarraca/pynrf24 for the NRF modules control

import socket
import shelve
import sys
from threading import Thread

# Expect the first parameter to be the port to listen to
if len(sys.argv) != 3:
 print "Usage: ap uri port"
 sys.exit(1)

global owntrackeraddr
global owntrackerport
global ownport

ownuri = sys.argv[1]
ownport = long(sys.argv[2],10)

def acceptMessages(args):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.bind(('', ownport))
   s.listen(1)
   try:
    while 1:
     conn, addr = s.accept()
     query = ""
     while  not query.endswith("\n") and len(query) < 1024:
      data = conn.recv(1024)
      query += data
     print ">", query
     #conn.send('OK\n')
     conn.close()
   except:
     raise
     print "Error while receving"

if __name__ == "__main__":
    thread = Thread(target = acceptMessages, args = (0,))
    thread.start()


def sendMessage(uri, message, mac):
  # See if we have cached the URL for this URI
  #  if not we get it from the tracker.
  if not urlcache.has_key(uri):
    ts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ts.connect((owntrackeraddr, owntrackerport))
    ts.send("LOC "+uri+'\n')
    url = ts.recv(1024)
    ts.close()
    urlcache[uri]=url;
  else:
    url = urlcache[uri]

  print 'Located to url: '+url

  # Send the message now that we know the URL
  urltokens = url.split(':')  
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((urltokens[0], long(urltokens[1],10)))
  s.send('MSG ' + uri + ' ' + mac+'\n')
  data = s.recv(1024)
  s.close()
  print data

# Figure out who our tracker is
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.0.250', 3000)) # Bootstrap node, cannot be hardcoded
s.send('TRK ' + ownuri + '\n')
owntracker = s.recv(1024)
owntrackertokens = owntracker.split(':')
owntrackeraddr = owntrackertokens[0]
owntrackerport = long(owntrackertokens[1],10)
print 'Own tracker: ' + owntracker
s.close()

urlcache = shelve.open("data/url_cache_"+ownuri)

while 1:
 uid = raw_input('UID:')
 msg = raw_input('MSG:')
 sendMessage(uid, msg, 'C0BBAA')

