
import dns.resolver # http://www.dnspython.org
from datagramtalk import datagramTalk
from datagramtalk import datagramTalkMessage

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
      dgtm = datagramTalkMessage( "" );
      dgtm.protocol = "iotp2p.tracker";
      dgtm.protocol_version = "0.0"
      dgtm.statement = "REG"
      dgtm.parameters['uri'] = uri;
      dgtm.parameters['uri'] = url;
      return self.dtg.sendDatagram( server, port, dgtm )
    except:
      dgtm = datagramTalkMessage( "" );
      dgtm.parameters['result'] = "NACK"
      return dgtm

  def sendMessage( self, uri, message ):
      try:
        # TODO: add cache here for now we always lookup
        uid, domain = uri.split("@")
        taddress, tport = self.getBootstrapNode( domain )

        dgtm = datagramTalkMessage( "" );
        dgtm.protocol = "iotp2p.tracker";
        dgtm.protocol_version = "0.0"
        dgtm.statement = "LOC"
        dgtm.parameters['uri'] = uri;

        response = self.dtg.sendDatagram( taddress, tport, "LOC " + uri )
        print response.raw
        naddress = response.parameters['url'].split(":")[0]
        nport = int(response.parameters['url'].split(":")[0],10)

        dgtm = datagramTalkMessage( "" );
        dgtm.protocol = "iotp2p.message";
        dgtm.protocol_version = "0.0"
        dgtm.statement = "MSG"
        dgtm.parameters['to'] = uri;
        dgtm.parameters['message'] = message;

        print naddress, nport
        return self.dtg.sendDatagram( naddress, nport, dtgm )
      except:
        return "NOK"
    

