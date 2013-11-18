#!/usr/bin/env python
# pynode provides proof of concept implementation of a iotp2p node.
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

from datagramtalk import datagramtalk
from iotp2p import iotp2p
import sys
import datetime
import atexit
import ConfigParser

global dts
global iotp2p

# This will hanle incoming requests.
# As an example we just reply "OK" and print the received message.
def reply_to_message( cmd ):
  f = open('/var/log/pynode.log', 'a')
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S")
  if cmd.statement == "MSG":
   f.write(timestamp + " " + cmd.raw + "\n")
   response = "OK"
  else:
   f.write(timestamp + " Unknown command:" + cmd.raw + "\n")
   response = "NOK"	
  f.close()
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
iotp2p.registerNode( uri, url )

# Initialize the server.
# Use function reply_to_message to handle incoming requests.
dts = datagramtalk( "0.0.0.0", port, reply_to_message )

# Make sure we always stop listening even if we get killed.  
atexit.register(stop_server)

# Wait here for user to want to exit.
raw_input( "Press enter to stop...." )

# Stop listening. Note the atexit will not fire here since we have threads still running.
stop_server();

