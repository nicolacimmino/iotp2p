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
# A Datagram message conveniently split into its tokens
class datagramTalkMessage:

  # Constrocut the object starting from a string message
  def __init__ ( self, message ):
    message_tokens = message.split(' ')

    # Store the statement
    if len( message_tokens ) > 0:
      self.statement = message_tokens[0]

    # Store the arguments
    if len( message_tokens ) > 1:
      self.arguments =  message_tokens[1:]

    # Store the raw message
    self.raw = message

  # The statement part of the message.
  statement = ""

  # The arguments of the statement.
  arguments = []

  # The raw message as it was received.  
  raw = ""

class datagramtalk:

  # When set causes the listening thread to terminate.
  __server_term = False

  # Receiver timeout in mS, max time waited for data once a connection is extablished.
  __rx_timeout = 10000

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

  # Send a message and get the reply.
  def sendMessage( self, ip, port, command ):
    try:
      s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
      s.connect( ( ip, port ) )
      s.send( command + "\n" )
      response = ""
      timeout = False;
      while not response.endswith( "\n" ) and len( response ) < 1024 and not timeout:
       
       # Allow data to come in chunks but don't wait more than rx_timeout
       ready = select.select( [s], [], [], self.__rx_timeout / 1000 )
       if ready[0]:
         data = s.recv(1024)
         response += data
       else:
         response = ""
         timeout = True

      # Whatever happened we end communication and return response if any
      s.close()
      return datagramTalkMessage(response[0:-1]) # Remove trailing \n

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
        while  not query.endswith("\n") and len(query) < 1024 and not timeout:
         ready = select.select( [client_socket], [], [], self.__rx_timeout / 1000 )
         if ready[0]:
          data = client_socket.recv(1024)
          query += data
         else:
          client_socket.close()      
          timeout = True
         if not timeout:
          query = query.translate(None, '\r\n')
          response = msg_hook(datagramTalkMessage(query)) # Process the command and get the response
          client_socket.send(response + "\n")
          client_socket.close()
          break;
    except:
      # Something went wrong, keep going with other connections
      print "Error while serving incoming traffic."


