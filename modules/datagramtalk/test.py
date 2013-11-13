from datagramtalk import datagramtalk

def reply_command( cmd ):
  return cmd

dts = datagramtalk("127.0.0.1", 3001, reply_command )
#dts.sendCommand("127.0.0.1", 3000, "bla")
while True:
 x=1

