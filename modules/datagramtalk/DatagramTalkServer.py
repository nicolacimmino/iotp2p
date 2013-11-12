#
# DatagramTalk provides simple yet reliable network communication between two parties.
# In DatagramTalk every transaction is constituted by a message, terminated by a \n send
#  from the talker and one response terminated by \n by the other party. Connection is
#  then terminated.
#
from threading import Thread
import socket
import select

class DatagramTalkServer:

  # When set causes the listening thread to terminate.
  __server_term = False

  # Receiver timeout in mS, max time waited for data once a connection is extablished.
  __rx_timeout = 1000

  # Default constructor, doesn't listen only allows to send messages. 
  def __init__ ( self ):
    print "ok"

  # This constructor initializes the server and listens for messages.
  def __init__ ( self, ip, port, msg_hook ):
    print "ok2"

    # Start a thread listeining for incoming messages.
    thread = Thread( target = self.startServer, args = ( ip, port, msg_hook ) )
    thread.start()
  
  # Stop listening for incoming commands.
  def stopListening( self ):
    self.__server_term = True

  # Send a command and get the reply.
  def sendCommand( self, ip, port, command ):
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
      return response[0:-1] # Remove trailing \n

    except:
      # Something went wrong, convention is to return empty string.
      return ""


  def startServer ( self, ip, port, msg_hook ):
   print "ok3"
   print ip, port
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.bind( ( ip, port ) )
   s.listen( 1 )
   while not self.__server_term:
    conn, addr = s.accept()
    conn.setblocking(0)
    query = ""
    timeout = False;
    while  not query.endswith("\n") and len(query) < 1024 and not timeout:
     ready = select.select( [conn], [], [], self.__rx_timeout / 1000 )
     if ready[0]:
      data = conn.recv(1024)
      query += data
     else:
      conn.close()      
      timeout = True
     if not timeout:
      response = msg_hook(query[0:-1]) # Process the command and get the response
      conn.send(response + "\n")
      conn.close()


