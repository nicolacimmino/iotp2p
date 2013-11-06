#!/usr/bin/env python
#
#

import sys
import subprocess
import shlex
import random
import socket
import select
import shelve
import os

DATA_PATH = "~/.iotp2p/" # This is the most likely writeale place, we store here persistent data

#
# Send a command and get the reply.
def sendCommand(ip, port, command):
  s = socket.socket()
  s.connect((ip, port))
  s.send(command + "\n")
  response = ""
  timeout = False;
  while not response.endswith("\n") and len(response) < 1024 and not timeout:
   ready = select.select([s], [], [], 100)
   if ready[0]:
     data = s.recv(1024)
     response += data
   else:
     response = ""
     timeout = True
  s.close()
  return response[0:-1] # Remove trailing \n


cmd = sys.argv[1]
verbose = "-v" in sys.argv

# Flushes the cache
if cmd == "flush":
  os.remove(DATA_PATH + "cache")
  exit()

# Make sure we have a directory where to write to
if not os.path.exists(DATA_PATH):
  os.makedirs(DATA_PATH)
  print "created folder"

# Open the cache of previously resolved queries
cache = shelve.open(DATA_PATH + "cache")

# Since we are a tool we don't have a real URI. Nonetheless to be good tracker net
#  citizens we randomize our URI so that the load or queries done trough this tool
#  is speread across the tracker net.
# We do cache this URI though otherwise we will prevent all following cache to function
if not cache.has_key("ownuri"):
 ownuri = "iotp2ptoool" + str(random.randrange(1000))
 cache["ownuri"] = ownuri
else:
 ownuri = cache["ownuri"]
 
if cmd == "tracker" and len(sys.argv) >= 3:
  try:
    uri = sys.argv[2]
    uid = uri.split("@")[0]
    trackernet = uri.split("@")[1]
  except:
    print "Invalid URI"
    exit()

  # Get boostrap nodes from the cache or dig them if we don't have them
  if cache.has_key("__bsnodes__" + trackernet):
    results = cache["__bsnodes__" + trackernet]
  else:
    # Find SRV records for the tracker net
    results = subprocess.check_output(["dig", "+short", "-t", "SRV", "_iot._tcp." + trackernet]).split("\n")
    cache["__bsnodes__" + trackernet] = results

  # Find the boostrap node. Here we just take the first from the list
  #  ignoring the weights. This should be changed.
  resulttokens = results[0].split(" ")
  bootstrapnode = resulttokens[3][0:-1] + ":" + resulttokens[2]

  tracker = ""

  if cache.has_key("__tracker__" + ownuri):
    print cache["__tracker__" + ownuri]
    exit()

  try:
    bsnodeaddress = bootstrapnode.split(":")[0]
    bsnodeport = int(bootstrapnode.split(":")[1],10)
    # Contact the boostrap node and see which tracker can serve us.
    # This is all that matters for the track command, not the URI of the node
    #  that is used just to get the tacker net.
    tracker = sendCommand(bsnodeaddress, bsnodeport, "TRK " + ownuri)
    cache["__tracker__" + ownuri] = tracker
    cache.sync()
  except:
    print "Cannot contact tracker net"
    if verbose:
      print "Connection to %s failed" % bootstrapnode
    exit()
  
  if tracker != "":
    print tracker
  else:
    print "Cannot find a tracker"

