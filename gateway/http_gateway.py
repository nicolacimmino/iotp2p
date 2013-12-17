#!/usr/bin/env python
# Proof of concept implelentation of an iotp2p HTTP gateway.
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
import atexit
import json
from flask import Flask
from flask import request
from threading import Thread
from iotp2p import iotp2p

# HTTP ReSTful API for the HTTP gateway
app = Flask(__name__)

# Resource: /tests/senderforms/<uri>
# Contains a test form that can be used to send a message to the specified URI
# Not really for production good now for proof of concept testing.
@app.route("/tests/senderforms/<uri>")
def _res_resources_test_sender(uri):
  return "<form method='POST' action='/nodes/" + uri + "/messages'>Message:<input type='text' name='message'><input type='submit'></form>"

# Resource: /nodes/<uri>/messages POST
# Sends a message to the specified URI
@app.route("/nodes/<uri>/messages", methods=['POST'])
def _res_resource_node(uri):  
    message = request.form['message']
    iotp2p.sendMessage( uri, message )
    return ""
	
# iotp2p protocol library
iotp2p = iotp2p()

def startFlaskServer():
    app.run( host = "0.0.0.0", port=4400, debug = False )

if __name__ == "__main__":
    thread = Thread( target = startFlaskServer  )
    thread.start()
