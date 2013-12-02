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
from iotp2p import iotp2p
from datagramtalk import datagramTalkMessage

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
    msgtokens = msg.split(" ")
     
    if len(msgtokens)==2 and msgtokens[0] == "REG":
       response = iotp2p.registerNode( msgtokens[1], ownuri ) 
       RAN.sendMessage(response.raw + "\n")
	   
    if len(msgtokens)>2 and msgtokens[0] == "MSG":
	   # Send message trough iotp2p
	   uri = msgtokens[1]
	   message = " ".join(msgtokens[2:])
	   iotp2p.sendMessage( uri, message )
	 
ownuri = sys.argv[1]
ownport = long(sys.argv[2],10)
owntracker = "x"

# iotp2p protocol library
iotp2p = iotp2p()

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




