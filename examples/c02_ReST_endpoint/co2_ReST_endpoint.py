#!/usr/bin/env python
# c02_ReST_endpoint provides proof of concept implementation of a iotp2p ReST endpoint node.
#   A CO2 sensor sends its readings periodically to this node which both logs them and offers
#    the latest reading trough a ReST HTTP interface.
#
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

from datagramtalk import datagramTalk
from datagramtalk import datagramTalkMessage
from iotp2p import iotp2p
import sys
import datetime
import atexit
import ConfigParser
from flask import Flask
from flask import request
from threading import Thread
import json

global dts
global iotp2p
global latestCO2
global uri

# HTTP ReSTful API to get latest readings
app = Flask(__name__)

# Resource: co2/latest
# Contains the latest C02 reading
@app.route("/co2/latest")
def c02_latest():
  global latestCO2
  
  response = {}
  response['co2'] = latestCO2
  
  # Convert to json
  return json.dumps( response )
  
# This will hanle incoming requests.
# We will process only messages that contain CO2 reports and ignore eventual
#   other messages.
def process_message( cmd ):
  global uri
  global latestCO2
  
  response = datagramTalkMessage( "" )
  try:
    f = open('/var/log/'+uri+'.log', 'a')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S,%03d")
    if cmd.statement == "MSG":
      message = cmd.parameters['message']
      if "CO2:" in message:
        latestCO2 = message[4:]
      f.write(timestamp + " " + cmd.raw + "\n")
      response.parameters['result'] = "ACK"
    else:
      f.write(timestamp + " Unknown command:" + cmd.raw + "\n")
      response.parameters['result'] = "NACK"	
      f.close()
  except Exception, e:
      print "Exception while processing command : " + str(e)
      
  return response

# We need to stop listening before leaving, otherwise the
#  serving thread will stay in memory.
def stop_server():
  dts.stopListening()
  
# Get command line parameters
if not len(sys.argv) == 2:
  print "Usage pynode uri"
  exit(1)

# First argument is the URI of the node.
uri = sys.argv[1]

# Get from the config file the settings for this URI
config = ConfigParser.RawConfigParser()
config.read('/etc/pynode/pynode.conf')

# Get the local port on which we listen.
# Note that this can be different than the one in the URI since
#  we could be reached trough a DNAT
port = config.getint(uri, 'localport')

# Get the url to which we can be reached
url = config.get(uri, 'url')

# iotp2p protocol library
iotp2p = iotp2p()

# Register our node on the trackernet so that we can receive messages
response = iotp2p.registerNode( uri, url )
print "response: ", response.raw

# Initialize the server.
# Use function process_message to handle incoming requests.
dts = datagramTalk( "0.0.0.0", port, process_message )

def startFlaskServer():
    app.run( host = "0.0.0.0", debug = False )

if __name__ == "__main__":
    thread = Thread( target = startFlaskServer  )
    thread.start()

latestCO2 = 0

# Make sure we always stop listening even if we get killed.  
atexit.register(stop_server)

# Wait here for user to want to exit.
raw_input( "Press enter to stop...." )

# Stop listening. Note the atexit will not fire here since we have threads still running.
stop_server();

