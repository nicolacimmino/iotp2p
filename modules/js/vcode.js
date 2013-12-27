// VCode provides helper functions to work on VCodes
//  Copyright (C) 2013 Nicola Cimmino
//
//   This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see http://www.gnu.org/licenses/.


function generateHMAC(key, rawdata)
{
  var shaObj = new jsSHA(rawdata, 'TEXT');
  return shaObj.getHMAC(key, "B64", "SHA-256", "B64");
}
	
function getVCode(key, nonce, rawdata)
{
  var hmac = generateHMAC(key, rawdata);
  return {"vc_version":0, "vc_nonce": nonce, "vc_hmac":hmac};
}
 
function validateStatement(key, statement)
{
  // The rawdata is a concatenation of all parameters
  //  names and values excluding parameters with names 
  //  prefixed by a ".".
  var rawdata=""
  for(var key in statement)
    if(!key.startsWith("."))
       rawdata = rawdata + key + "=" + statement[key] + "|";
       
  var hmac = generateHMAC(key, rawdata);
   
  return hmac == statement['.hmac'];
}