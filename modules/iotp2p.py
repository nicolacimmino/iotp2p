# iotp2p provides implementation of iotp2p primitive functiions.
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

import dns.resolver # http://www.dnspython.org
from datagramtalk import datagramTalk
from datagramtalk import datagramTalkMessage

class iotp2p:

  # DatagramTalk object used to send commands.
  dtg = datagramTalk( None, None, None )

  #
  # Attempts to find the tracker for the given domain.
  # Implements iotp2p.00.3 URI and URLs.
  def getTracker(self, domain ):
    try:
      # Try to get the SRV record for this domain.
      answers = dns.resolver.query('_iot._tcp.' + domain, 'SRV')
      
      # If we get an answer we attempt parsing it, else we default to domain:3333
      if len( answers ) > 0:
        # Record looks like:
        # _iot._tcp.example.com. 3600 IN    SRV     0 80 3000 192.0.2.1.
        return str(answers[0]).split(' ')[3][0:-1],  int(str(answers[0]).split(' ')[2],10)
      else:
        return domain, 3333
    except:
        # Something went wrong, we must assume domain:3333 according to iotp2p.00.3.
        return domain, 3333
 
  # Register a node on a tracker.
  # Implements iotp2p.02.3 Trackers Interface
  def registerNode(self, uri, url ):
    try:
      uid, domain = uri.split( "@" )
      # Find a tracker for this domain.      
      server, port = self.getTracker( domain )
      print "Attempting to register on ", server, port      
      # Register with the net
      dgtm = datagramTalkMessage( "" );
      dgtm.protocol = "iotp2p.tracker";
      dgtm.protocol_version = "0.0"
      dgtm.statement = "REG"
      dgtm.parameters['uri'] = uri;
      dgtm.parameters['url'] = url;
      return self.dtg.sendDatagram( server, port, dgtm )
    except:
      dgtm = datagramTalkMessage( "" );
      dgtm.parameters['result'] = "NACK"
      return dgtm

  def sendMessage( self, uri, message ):
      try:
        # TODO: add cache here for now we always lookup
        uid, domain = uri.split("@")
        taddress, tport = self.getTracker( domain )

        # TODO: move to own function as other callers will need
        #  to do LOC.
        dgtm = datagramTalkMessage( "" );
        dgtm.protocol = "iotp2p.tracker";
        dgtm.protocol_version = "0.0"
        dgtm.statement = "LOC"
        dgtm.parameters['uri'] = uri;

        response = self.dtg.sendDatagram( taddress, tport, dgtm )
        print response.raw
        naddress = response.parameters['url'].split(":")[0]
        nport = int(response.parameters['url'].split(":")[1],10)

        dgtm = datagramTalkMessage( "" );
        dgtm.protocol = "iotp2p.message";
        dgtm.protocol_version = "0.0"
        dgtm.statement = "MSG"
        dgtm.parameters['to'] = uri;
        dgtm.parameters['message'] = message;

        print naddress, nport
        return self.dtg.sendDatagram( naddress, nport, dgtm )
      except:
        return "NOK"
    

