#!/usr/bin/env python
# VCode provides helper functions to work on VCodes
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

from hashlib import sha256
import hmac
import binascii

def generateHMAC(key, statement):
  # The rawdata is a concatenation of all parameters
  #  names and values excluding parameters with names 
  #  prefixed by a ".".
  rawdata=""
  datagram_params = sorted(statement.datagram)
  for datagram_param in datagram_params:
    if not datagram_param[0] == ".":
       rawdata = rawdata + datagram_param + "=" + statement.datagram[datagram_param] + "|"
  
  print rawdata
  
  hashed = hmac.new(binascii.a2b_base64(key), rawdata, sha256)
  return binascii.b2a_base64(hashed.digest())[:-1]
  
def getVCode(key, nonce, rawdata):
  hmac = generateHMAC(key, rawdata)
  return {"vc_version":0, "vc_nonce": nonce, "vc_hmac":hmac}
  
def validateStatement(key, statement):
     
  hmac = generateHMAC(key, rawdata)
  
  print "Raw data:" + rawdata
  print "HMAC:" + hmac
  
  return hmac == statement['.hmac']
  
