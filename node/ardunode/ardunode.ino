// iotp2p provides decentralized, scalable messaging for the Internet of Things
//  Copyright (C) 2013 Nicola Cimmino
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//   This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see http://www.gnu.org/licenses/.

#include <SPI.h>
#include <RF24.h>
#include <EEPROM.h>

RF24 radio(9,10);
// Second was 71 in the end
const uint64_t pipes[2] = { 0x7070707070LL, 0x7070707071LL };

String uid = "N000";

// Indicates that we have entered a network and we can send data.
bool network_ok = false;

const byte EEPROM_RFCH = 0x01;

void setup(void)
{
  Serial.begin(9600);
  
  radio.begin();
  radio.setCRCLength(RF24_CRC_8);
  radio.setRetries(15,15);
  radio.setPayloadSize(4);
  radio.setChannel(EEPROM.read(EEPROM_RFCH)); // We start from the last known good channel
  radio.setDataRate(RF24_250KBPS);
  radio.setPALevel(RF24_PA_MAX);
  radio.setAutoAck(1);
  
  radio.openWritingPipe(pipes[0]);
  radio.openReadingPipe(1,pipes[1]);
  
  radio.startListening();
  radio.printDetails();
  
}


int lost_packets = 0;

void loop(void)
{
   while(!network_ok)
     scanForNet();
    
   radio.stopListening();
   bool ok = radio.sendMessage("MSG logger@nicolacimmino.com ping");
   radio.startListening();
   
   if(!ok)
   {
     lost_packets++;
   }
   else
   {
     lost_packets = 0;
   }
   
   if(lost_packets>5)
   {
     Serial.println("NO SERVICE");
     network_ok = false;
   }  
   
   delay(1000);
}

// Attempts to find an AP where to connect.
// And if found it enters the network.
void scanForNet()
{
  // Start the scan from the last known good channel.
  int scan_start = EEPROM.read(EEPROM_RFCH);
  if(scan_start>15)
   scan_start = 0;
  
  while(true)
  {   
    for(int ch=scan_start; ch<15; ch++)
    {
       Serial.print("SCAN CH ");
       Serial.println(ch);
       radio.setChannel(ch);
       String msg = radio.readMessage(1500);
       if(msg.startsWith("BCH"))
       {
         Serial.println("Found BCH");
         
         // Store this as last known good channel
         if(ch != EEPROM.read(EEPROM_RFCH))
           EEPROM.write(EEPROM_RFCH, ch);
           
         // We now need to register to the AP
         radio.stopListening();
         bool ok = radio.sendMessage("REG " + uid);
         radio.startListening();
         
         if(!ok)
           continue;
         
         msg = radio.readMessage(1500);
         if(msg != "OK")
         {
           Serial.println(msg);
           continue;    // Registration failed, continue to scan
         } 
         
         Serial.println("NET OK");
         network_ok = true;  
         return;
       }    
    }
    
    // Not found, start from the first channel.
    scan_start = 0;
  }
}
