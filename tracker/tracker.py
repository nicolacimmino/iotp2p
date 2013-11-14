#!/usr/bin/env python
# Proof of concept implementation of a iotp2p tracker. Provides no security.
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

import sys
import socket
import shelve
import select
from hash_ring import HashRing
from datagramtalk import datagramtalk

#global dts
#global nodeslocation

#
# Gets the tracker URL, IP and port for a given URI
def getTracker(uri):
  trackeraddr = ring.get_node(uri)
  trackeraddrtokens = trackeraddr.split(":")
  return trackeraddr, trackeraddrtokens[0], int(trackeraddrtokens[1],10)


def reply_to_message( query ):
  #global dts
  #global nodeslocation
  try:
    print ownport, ">", query.raw + "\r"
    response = "UNKNOWN"

    # Client wants to find the proper tracker for a given URL
    if len(query.arguments) == 1 and query.statement == "TRK":
     response = ring.get_node(query.arguments[0])

    # Client wants to register with the tracker
    if len(query.arguments) == 2 and  query.statement == "REG":
     uri=query.arguments[0]
     url=query.arguments[1]   
     trackerurl, trackerip, trackerport = getTracker(uri)

     if trackerurl != ownuri:
      # Not our node, rely the query
      response = dts.sendMessage(trackerip, trackerport, query.raw).raw
     else:
      # Cache the URL of this URI
      nodeslocation[uri]=url
      nodeslocation.sync()
      response = "OK"
 
    # Client wants to locate a node
    if len(query.arguments) == 1 and  query.statement == "LOC":
     uri=query.arguments[0]
     trackerurl, trackerip, trackerport = getTracker(uri)
   
     if trackerurl != ownuri:
      # Not our node, rely the query
      response = dts.sendMessage(trackerip, trackerport, query.raw)
     else:
      if nodeslocation.has_key(uri):  
       response = nodeslocation[uri]
      else:
       print uri+"|"
       response = "NOTHERE"

    print ownport, "<", response + "\n\r"
    return response
  except:
    return ""


# Expect the first parameter to be the port to listen to
if len(sys.argv) != 3:
 print "Usage: tracker extip port"
 sys.exit(1)

ownport = long(sys.argv[2],10)
ownaddr = sys.argv[1]
ownuri = sys.argv[1] + ":" + sys.argv[2]

#Get the trackers roster from file
try:
  trackers_urls = open("data/trackers_roster").read().splitlines()
except:
  print "Could not find trackers roster"
  print "Please create file data/trackers_roster and add trackers to it."
  sys.exit(1)

#And place the valid lines into a list of trackers
trackers = []
for tracker_url in trackers_urls:
 if tracker_url != "":
  trackers.append(tracker_url)

# Open the cache of nodes location
nodeslocation = shelve.open("data/nodes_location_"+ownuri)

#Distribute the trackers along the ring with 3 replicas for each
# this helps to improve distribution.
ring = HashRing(trackers,3)

# Initialize the server.
dts = datagramtalk('', ownport, reply_to_message )

# Wait here for user to want to exit.
raw_input( "Press enter to stop...." )

# We need to stop listening before leaving, otherwise the
#  serving thread will stay in memory.
dts.stopListening()


