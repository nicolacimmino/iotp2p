
import dns.resolver # http://www.dnspython.org
from datagramtalk import datagramTalk

class iotp2p:

  # DatagramTalk object used to send commands.
  dtg = datagramTalk( None, None, None )

  #
  # Attempts to get a boostrap node for the given domain.
  def getBootstrapNode(self, domain ):
    try:
      answers = dns.resolver.query('_iot._tcp.' + domain, 'SRV')
      if len( answers ) > 0:
        return str(answers[0]).split(' ')[3][0:-1],  int(str(answers[0]).split(' ')[2],10)
      else:
        # User default 3333 port if no SRV record is found.
        return domain, 3333
    except:
        # User default 3333 port if no SRV record is found.
        return domain, 3333
 
  
  def registerNode(self, uri, url ):
    try:
      uid, domain = uri.split( "@" )
      # Find a bootstrap node for the tracker net      
      server, port = self.getBootstrapNode( domain )
      print "Attempting to register on ", server, port      
      # Register with the net
      print  "REG " + uri + " " + url
      return self.dtg.sendMessage( server, port, "REG " + uri + " " + url )
    except:
      return "NOK"

  def sendMessage( self, uri, message ):
      try:
        # TODO: add cache here for now we always lookup
        uid, domain = uri.split("@")
        taddress, tport = self.getBootstrapNode( domain )
        response = self.dtg.sendMessage( taddress, tport, "LOC " + uri )
        naddress = response.raw.split(":")[0]
        nport = int(response.raw.split(":")[1],10)
        return self.dtg.sendMessage( naddress, nport, "MSG " + message )
      except:
        return "NOK"
	

