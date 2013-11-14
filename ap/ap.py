#!/usr/bin/env python
# Proof of concept implementation of a iotp2p Access Point. Provides no security.
#   Copyright (C) 2013 Nicola Cimmino
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.

import socket
import shelve
import sys
from iotp2pran import iotp2pran
from threading import Thread

# Expect the first parameter to be the port to listen to
if len(sys.argv) != 3:
 print "Usage: ap uri port"
 sys.exit(1)

global owntrackeraddr
global owntrackerport
global ownuri
global ownport
global APP_TERMINATING


def acceptRadioMessages():
  while not APP_TERMINATING:
    msg = RAN.readMessage([0])
    if msg != "":
      print msg
    if owntracker != "":
     msgtokens = msg.split(" ")
     if len(msgtokens)==2 and msgtokens[0] == "REG":
       # Forward the REG query and add our URL so messages for the
       #  new node can come here.
       s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       s.connect((owntrackeraddr, owntrackerport)) 
       print "conntected"
       s.send(msg + " 192.168.0.8:" + str(ownport) + "\n")
       print "sent"
       response = s.recv(1024)
       print "received"
       s.close()
       RAN.sendMessage(response + "\n")
    else:
     RAN.sendMessage("OFFLINE\n")
# Accept messages relayed from other APs
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

#if __name__ == "__main__":
#    thread = Thread(target = acceptMessages, args = (0,))
#    thread.start()


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


ownuri = sys.argv[1]
ownport = long(sys.argv[2],10)

# Figure out who our tracker is
try:
 s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 s.connect(('192.168.0.250', 3000)) # Bootstrap node, cannot be hardcoded
 s.send('TRK ' + ownuri + '\n')
 owntracker = s.recv(1024)
 owntrackertokens = owntracker.split(':')
 owntrackeraddr = owntrackertokens[0]
 owntrackerport = long(owntrackertokens[1],10)
 print 'Own tracker: ' + owntracker
 s.close()
except:
 print "Tracknet not available, commands will not be forwarded"
 owntracker = ""

urlcache = shelve.open("data/url_cache_"+ownuri)


APP_TERMINATING = False
RAN = iotp2pran()

RAN.startNetwork()

if __name__ == "__main__":
  thread = Thread(target = acceptRadioMessages)
  thread.start()


wait=raw_input("Enter to terminate")
RAN.stopNetwork()
APP_TERMINATING = True
exit()




