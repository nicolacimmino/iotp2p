#!/usr/bin/env python
#
# Proof of concept implementation of a tracker for IoT P2P
#
# Nicola Cimmino 2013
#
# This proof of concept tracker reads a roster of trackers and listens for UDP traffic on the 
#	specified port serving clients. No provision is made at the moment to update the roster.
#
# We make use of hash_ring by Amix (http://amix.dk/blog/post/19367)
#
# TODO! We make use of shelve this has apparently the risk of allowing arbitrary code execution if malicious data
#	is loaded. This proof of concept doens't validate REG URLs so we actualy allow to remotely
#	place anything in the cache!
# 
import sys
import socket
import shelve
import select
from hash_ring import HashRing

# Expect the first parameter to be the port to listen to
if len(sys.argv) != 3:
 print "Usage: tracker extip port"
 sys.exit(1)

port = long(sys.argv[2],10)
ownaddr = sys.argv[1] + ":" + sys.argv[2]

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
s.bind(('', port))
s.listen(1)
try:
 while 1:
  conn, addr = s.accept()
  conn.setblocking(0)
  query = ""
  while  not query.endswith("\n") and len(query) < 1024:
   ready = select.select([conn], [], [], 100)
   if ready[0]:
    data = conn.recv(1024)
    query += data
   else:
    conn.close()
    continue

  print ">", query

  response = "UNKNOWN\n"

  # Tokenize on white spaces 
  querytokens = query.split();

  # Client wants to find the proper tracker for a given UID
  if len(querytokens) == 2 and querytokens[0] == "TRK":
   response = ring.get_node(query[4:])

  # Client wants to register with the tracker
  if len(querytokens) == 3 and  querytokens[0] == "REG":
   uid=querytokens[1]
   url=querytokens[2]
   trackeraddr = ring.get_node(uid)
   trackeraddrtokens = trackeraddr.split(":")

   if trackeraddr != ownaddr:
    # Not our node, refuse registration
    response = "USE " + trackeraddr + "\n"
   else:
    nodeslocation[uid]=url
    response = "OK\n"
 
  # Client wants to locate a node
  if len(querytokens) == 2 and  querytokens[0] == "LOC":
   uid=querytokens[1]
   trackeraddr = ring.get_node(uid)
   trackeraddrtokens = trackeraddr.split(":")
   
   if trackeraddr != ownaddr:
    # Not our node, rely the query
    ts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ts.connect((trackeraddrtokens[0], long(trackeraddrtokens[1],10)))
    ts.send(query)
    response = ts.recv(1024)
    ts.close()    
   else:
    if nodeslocation.has_key(uid):  
     response = nodeslocation[uid]
    else:
     response = "NOTHERE\n"

  print "<", response
  conn.send(response)  
  conn.close()
except:
  print "Terminating."
  s.close()
  raise

s.close()
