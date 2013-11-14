#!/usr/bin/env python
# Datagram-Talk Server provides simple example of usage of the Datagram-Talk module.
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

# This will hanle incoming requests. 
# As an example we just reply "OK" followed by the original statement
def reply_to_message( cmd ):
  return "OK" + cmd.statement

# Initialize the server.
# Listen only on localhot, port 4000
# Use function reply_to_message to handle incoming requests.
dts = datagramtalk("127.0.0.1", 4000, reply_to_message )

# Wait here for user to want to exit.
raw_input( "Press enter to stop...." )

# We need to stop listening before leaving, otherwise the
#  serving thread will stay in memory.
dts.stopListening()

	

