from DatagramTalkServer import DatagramTalkServer

def reply_command( cmd ):
  return cmd

dts = DatagramTalkServer("127.0.0.1", 3001, reply_command )
#dts.sendCommand("127.0.0.1", 3000, "bla")
while True:
 x=1

