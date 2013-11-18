
import dns.resolver # http://www.dnspython.org
from datagramtalk import datagramtalk

class iotp2p:

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
      dtg = datagramtalk( None, None, None )
      print  "REG " + uri + " " + url
      return dtg.sendMessage( server, port, "REG " + uri + " " + url )
    except:
      raise
      return "NOK"

    def sendMessage( self, uri, message ):
	  try:
	    # TODO: add cache here for now we always lookup
		uid, domain = uri.split("@")
		tracker = getBootstrapNode( domain )
		address, port = tracker.split(":")
		dgt = datagramtalk( None, None, None )
		retrun dtg.sendMessage( address, port, message)
	  except:
	    raise
		return "NOK"
		
# Add send message:
# lookup URL in chache
# send message to that url
# if not found or no reply find trackernet node
# issue LOC
# send message


