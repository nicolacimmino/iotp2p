
import dns.resolver # http://www.dnspython.org
from datagramtalk import datagramtalk

class iotp2p:

  #
  # Attempts to get a boostrap node for the given domain.
  def getBootstrapNode(self, domain ):
    try:
      answers = dns.resolver.query('_iot._tcp.' + domain, 'SRV')
      if len( answers ) > 0:
        return str(answers[0]).split(' ')[3],  str(answers[0]).split(' ')[2]
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
      
      # Register with the net
      dtg = datagramtalk( server, port )
      return dtg.sendMessage( "REG " + uri + " " + url )
    except:
      return "NOK"



