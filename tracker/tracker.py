#!/usr/bin/env python
# Rel.0 implementation of a iotp2p tracker. Rel.0 of iotp2p supports
#    single trackers that serve a single domain. There is no trackers
#    swarming at this stage.
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
import atexit
from datagramtalk import datagramtalk
from datagramtalk import datagramTalkMessage


def serve_request( request ):
 
  try:
    #print own_port, ">", request.raw + "\r"
    response = datagramTalkMessage( "" )
    response.protocol = "iotp2p.track"
    response.protocol_version = "0.0"
    
    # Client wants to register with the tracker
    if request.statement == "REG":
     uri=request.parameters['uri']
     url=request.parameters['url']   
     
     if not uri == "" and not url == "":
       # TODO: here we need to get the VCode and verify the MAC
       # against the stored secret for this node.
     
       # Cache the URL of this URI
       nodeslocation[str(uri)]=url
       nodeslocation.sync()
       response.parameters['result'] = "OK"
 
    # Client wants to locate a node
    if request.statement == "LOC":
     uri=request.arguments['uri']
     
     if nodeslocation.has_key(uri):  
       response.parameters['result'] = "OK"
       response.parameters['uri'] = nodeslocation[uri]
     else:
       response.parameters['result'] = "NOK"
       response.parameters['reason'] = "NOTHERE"
       

    print own_port, "<", response.raw + "\n\r"
    return response
  except:
    raise
    response.parameters['result'] = "NOK"
    response.parameters['reason'] = "ERROR"
    return response
	
def stop_dts():
    dts.stopListening()
	
# Expect the first parameter to be the port to listen to
if len(sys.argv) != 2:
 print "Usage: tracker port"
 sys.exit(1)

own_port = long(sys.argv[1],10)

# Open the cache of nodes location
nodeslocation = shelve.open("data/nodes_location_" + str( own_port ) )

# Initialize the server.
dts = datagramtalk('', own_port, serve_request )

# Make sure we always stop listening even if we get killed.  
atexit.register( stop_dts )

# Wait here for user to want to exit.
raw_input( "Press enter to stop...." )

# Stop listening. Note the atexit will not fire here since we have threads still running.
dts.stopListening()



