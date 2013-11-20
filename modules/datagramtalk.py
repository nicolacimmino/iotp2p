# Datagram-Talk provides simple TCP based stateless messaging between two applications
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

from threading import Thread
import socket
import select
import sys

#
# A Datagram message conveniently split into its parts and with the 
#  ability to reasseamble a raw message starting from the parts.
class datagramTalkMessage:
 
  # The statement part of the message.
  statement = ""

  # The higer level protocol
  protocol = ""
  
  # The higher level protocol version
  protocol_version = ""
  
  # The parameters of the statement.
  parameters = {}

  # The raw message as it was received.  
  raw = ""
  
  # Constrocut the object starting from a string representing the all message
  def __init__ ( self, message ):
    
    try:
      if not message == "":
        # Tolerate \r\n, split lines on \n
        message_lines = message.translate(None, 'r').split('\n')

        # The first line is:
        # protocol version statement
        tokens = message_lines[0].split( ' ' )
        self.protocol = tokens[0]
        self.protocol_version = tokens[1]
        self.statement = tokens[2]
        
        # Find all parameters
        for message_line in message_lines:
          if '=' in message_line:
            tokens = message_line.split( '=' )
            self.parameters[tokens[0]] = tokens[1]
    except:
       # Something went wrong just store the raw message
       print "Exception while parsing dtalk message"
       
    # Store the raw message
    self.raw = message
  
  def toRaw( self ):
    self.raw = ""
    
    # First line has protocol, version and statement
    self.raw += self.protocol + " " + self.protocol_version + " " + self.statement + "\n"
    
    # Following lines are the params
    for key in self.parameters.keys():
      self.raw += key + "=" + self.parameters[key] + "\n"

    # Close the message with an empty line
    self.raw += "\n"

    # Als return the raw message
    return self.raw
    
class datagramtalk:

  # When set causes the listening thread to terminate.
  __server_term = False

  # Timeout in seconds for waiting from data from a requester
  # See DatagramTalk section Timers Ta.
  __timer_Ta_timeout = 10

  # Timeout in seconds for waiting for a response to a request
  # See DatagramTalk section Timers Tb.
  __timer_Tb_timeout = 10
  
  # Receiver buffer size, no message can be larger than this.
  __rx_buffer_size = 1024
  
  # Default constructor, doesn't listen only allows to send messages. 
  def __init__( self ):
    print "ok"

  # This constructor initializes the server and listens for messages.
  def __init__( self, ip, port, msg_hook ):
    # Nothing to do

    # Start a thread listeining for incoming messages.
    thread = Thread( target = self.startServer, args = ( ip, port, msg_hook ) )
    thread.start()
  
  # Stop listening for incoming commands.
  def stopListening( self ):
    self.__server_term = True

  # Sends a datagram and gets the response datagram.
  def sendDatagram( self, ip, port, datagram ):
    try:
      s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
      s.connect( ( ip, port ) )
      s.send( datagram.toRaw() )
      response = ""
      timeout = False;
      while not (response.endswith("\n\n") or response.endswith("\r\n\r\n")) and len( response ) < __rx_buffer_size and not timeout:
       
       # Allow data to come in chunks but don't wait more than rx_timeout
       ready = select.select( [s], [], [], self.__timer_Tb_timeout )
       if ready[0]:
         data = s.recv( __rx_buffer_size )
         response += data
       else:
         response = ""
         timeout = True

      # Whatever happened we end communication and return response if any
      s.close()
      return datagramTalkMessage( response )

    except:
      # Something went wrong, convention is to return empty string.
      return datagramTalkMessage("")


  # Starts to serve connections until __server_term is set.
  def startServer ( self, ip, port, msg_hook ):

   server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   server_socket.bind( ( ip, port ) )
   server_socket.listen( 1 )

   while not self.__server_term:
    try:
      ready = select.select( [server_socket], [], [], 1 )
      if ready[0]:
        client_socket, address = server_socket.accept()
        query = ""
        timeout = False;
        while  not (query.endswith("\n\n") or query.endswith("\r\n\r\n")) and len(query) < 1024 and not timeout:
         ready = select.select( [client_socket], [], [], self.__timer_Ta_timeout )
         if ready[0]:
          data = client_socket.recv(1024)
          query += data
         else:
          client_socket.close()      
          timeout = True
         if not timeout:
          response = msg_hook( datagramTalkMessage( query ) ) # Process the request and get the response
          client_socket.send(response)
          client_socket.close()
          break;
    except:
      # Something went wrong, keep going with other connections
      print "Error while serving incoming traffic."


