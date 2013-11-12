#!/usr/bin/env python
#
# Proof of concept implementation of a tracker for IoT P2P
#
# Nicola Cimmino 2013
#
# This proof of concept tracker reads a roster of trackers and listens for TCP traffic on the 
#	specified port serving clients. No provision is made at the moment to update the roster.
#
# We make use of hash_ring by Amix (http://amix.dk/blog/post/19367)
#
import sys
import socket
import shelve
import select
from hash_ring import HashRing


#
# Send a command and get the reply.
def sendCommand(ip, port, command):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

#
# Wait a query. Bloks until a valid query is received.
def waitCommand(s):
 while True:
  conn, addr = s.accept()
  conn.setblocking(0)
  query = ""
  timeout = False;
  while  not query.endswith("\n") and len(query) < 1024 and not timeout:
   ready = select.select([conn], [], [], 100)
   if ready[0]:
    data = conn.recv(1024)
    query += data
   else:
    conn.close()
    timeout = True
   if not timeout:
    return conn, query[0:-1] # Remove trailing \n

#
# Send a response to a query previously received by waitCommand
def sendResponse(conn, response):
  conn.send(response + "\n")
  conn.close()

#
# Gets the tracker URL, IP and port for a given URI
def getTracker(uri):
  trackeraddr = ring.get_node(uri)
  trackeraddrtokens = trackeraddr.split(":")
  return trackeraddr, trackeraddrtokens[0], int(trackeraddrtokens[1],10)

# Expect the first parameter to be the port to listen to
if len(sys.argv) != 3:
 print "Usage: tracker extip port"
 sys.exit(1)

ownport = long(sys.argv[2],10)
ownaddr = sys.argv[1]
ownuri = sys.argv[1] + ":" + sys.argv[2]

#Get the trackers roster from file
trackers_urls = open("data/trackers_roster").read().splitlines()

#And place the valid lines into a list of trackers
trackers = []
for tracker_url in trackers_urls:
 if tracker_url != "":
  trackers.append(tracker_url)

# Open the cache of nodes location
nodeslocation = shelve.open("data/nodes_location_"+ownaddr)

#Distribute the trackers along the ring with 3 replicas for each
# this helps to improve distribution.
ring = HashRing(trackers,3)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', ownport))
s.listen(1)
try:
 while True:
  conn, query = waitCommand(s)
  print ownport, ">", query + "\r"
  response = "UNKNOWN"

  # Tokenize on white spaces 
  querytokens = query.split();

  # Client wants to find the proper tracker for a given URL
  if len(querytokens) == 2 and querytokens[0] == "TRK":
   response = ring.get_node(querytokens[1])

  # Client wants to register with the tracker
  if len(querytokens) == 3 and  querytokens[0] == "REG":
   uri=querytokens[1]
   url=querytokens[2]   
   trackerurl, trackerip, trackerport = getTracker(uri)

   if trackerurl != ownuri:
    # Not our node, rely the query
    response = sendCommand(trackerip, trackerport, query)
   else:
    # Cache the URL of this URI
    nodeslocation[uri]=url
    nodeslocation.sync()
    response = "OK"
 
  # Client wants to locate a node
  if len(querytokens) == 2 and  querytokens[0] == "LOC":
   uri=querytokens[1]
   trackerurl, trackerip, trackerport = getTracker(uri)
   
   if trackerurl != ownuri:
    # Not our node, rely the query
    response = sendCommand(trackerip, trackerport, query)
   else:
    if nodeslocation.has_key(uri):  
     response = nodeslocation[uri]
    else:
     response = "NOTHERE"

  print ownport, "<", response + "\n\r"
  sendResponse(conn, response)  
except:
  print "Terminating."
  s.close()
  raise

s.close()
