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
import json
from flask import Flask
from flask import request
from datagramtalk import datagramTalk
from datagramtalk import datagramTalkMessage
from threading import Thread

# HTTP ReSTful API for tracker monitoring
app = Flask(__name__)

# Teacker operations statistics
reg_count = 0
loc_count = 0
err_count = 0

# Resource: /
# Contains a list of available resources
@app.route("/")
def _res_resources():

  res = [ 'stats', 'nodes' ]
  response = {}
  response['resources'] = res

  # Convert to json
  return json.dumps( response )

# Resource: stats
# Contains statistical information about tracker operation
@app.route("/stats")
def _res_stats():
  global reg_count
  global loc_count
  global err_count

  stats = {}
  stats['reg_count'] = reg_count
  stats['loc_count'] = loc_count
  stats['err_count'] = err_count

  # Convert to json
  return json.dumps( stats )

# Contains all registered nodes and their URLs
@app.route("/nodes")
def _res_nodes():
  global nodeslocation

  nodes = {}
  for node in nodeslocation:
    nodes[node] = nodeslocation[node]

  # Convert to json
  return json.dumps( nodes )

def startFlaskServer():
    app.run( host = "0.0.0.0", debug = False )

if __name__ == "__main__":
    thread = Thread( target = startFlaskServer  )
    thread.start()

def serve_request( request ):
  global reg_count
  global loc_count
  global err_count

  try:
    #print own_port, ">", request.raw + "\r"
    response = datagramTalkMessage( "" )
    response.protocol = "iotp2p.track"
    response.protocol_version = "0.0"

    # Client wants to register with the tracker
    if request.statement == "REG":
     reg_count = reg_count + 1
     uri=request.parameters['uri']
     url=request.parameters['url']
     
     if not uri == "" and not url == "":
       # TODO provide method to store secrets, this is just a test.
       nodessecrets[uri] = "this is a test secret" 
       vc_nonce=request.parameters['vc_nonce']
       vc_hmac=request.parameters['vc_hmac']
       key=nodessecrets[uri];
       
       # Fail the request is the HMAC is invalid.
       if(validateStatement(key, request)):
         # Cache the URL of this URI
         nodeslocation[str(uri)]=url
         nodeslocation.sync()
         response.parameters['result'] = "OK"
       else
         response.parameters['result'] = "NOK"
       
     return response

    # Client wants to locate a node
    if request.statement == "LOC":
     loc_count = loc_count + 1
     uri=str(request.parameters['uri'])
     
     if nodeslocation.has_key(uri):  
       response.parameters['result'] = "OK"
       response.parameters['url'] = nodeslocation[uri]
     else:
       response.parameters['result'] = "NOK"
       response.parameters['reason'] = "NOTHERE"
     return response  

    response.parameters['result'] = "NOK"
    response.parameters['reason'] = "UNKNOWN"
    return response
  except:
    err_count = err_count + 1
    response.parameters['result'] = "NOK"
    response.parameters['reason'] = "ERROR"
    return response
	
def stop_tracker():
    dts.stopListening()
    func = request.environ.get('werkzeug.server.shutdown')
    func()
	
# Expect the first parameter to be the port to listen to
if len(sys.argv) != 2:
 print "Usage: tracker port"
 sys.exit(1)

own_port = long(sys.argv[1],10)

# Open the cache of nodes location
nodeslocation = shelve.open("data/nodes_location_" + str( own_port ))

nodessecrets = shelve.open("data/nodes_secrets_" + str( own_port ))

print _res_nodes()

# Initialize the server.
dts = datagramTalk('', own_port, serve_request )

# Make sure we always stop listening even if we get killed.  
atexit.register( stop_tracker )

# Wait here for user to want to exit.
raw_input( "Press enter to stop...." )

# Stop listening. Note the atexit will not fire here since we have threads still running.
dts.stopListening()
