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
//
// Tested on a pro-mini is ATMega168 5V @16MHz and a nano.
// 
// Connections:
//
// Warning! There are at least two types of radio modules, these pins are for a specific one used in protos.
//  Please use signal names and check your module pinout.
//
//  Radio  Signal  Arduino
//  1      GND     GND
//  2      VCC     3.3V
//  3      CE      9
//  4      CSN     10
//  5      CLK     13
//  6      MOSI    11
//  7      MISO    12
//

#include <SPI.h>
#include <RF24.h>        // Copyright (C) 2011 J. Coliz <maniacbug@ymail.com>, GNU
#include <EEPROM.h>
#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>

//
// Change the following consts if your connections are arranged in different way.

#define radio_ce_pin 9        // CE pin for the NRF24L01+
#define radio_csn_pin 10      // CSN pin for the NRF24L01+

// EEPROM Memory map
const byte EEPROM_RFCH = 0x01;        // 0x01  Last known good RF channel
const byte EEPROM_URI  = 0x10;        // 0x10  Start of our URI, null terminated max 64 bytes including null
const byte EEPROM_URI_TO = 0x50;        // 0x50  Start of the URI we report to, null terminated max 64 bytes including null


// An instance of the NRF24L01+ chip controller.
RF24 radio(radio_ce_pin,radio_csn_pin);

// These are the pipes for communication, we make use only of one TX and one RX
//  pipe. These are just default values for the BCH, they are changed according
//  to radio time and current operation.
const uint64_t pipes[2] = { 0x1000000001LL, 0x1000000000LL };

// URI of this node, will be loaded from EEPROM_uri address.
String uri = "";

// URI to which we report. This is a single one in this test node, of course
//   different applications might need to talk to different URIs
String uri_to = "";

// Flag, indicates that we have entered a network and we can send data.
bool network_ok = false;

// Count of consecutive TX operation failures
int tx_fail = 0;

// The Interrupt Service Routine, this is called everytime the watchdog interrupt fires.
ISR(WDT_vect)
{
   //We don't do anything here at the moment.
   // Code will resume the execution after the sleep.
   Serial.println("ISR");
   return;
}

// Board setup.
void setup(void)
{
  // We sometimes still use serial for debuggin.
  // Keep high speeds and use sparingly as writing to serial puts off all timings.
  Serial.begin(115200);
  
  // These are fixed parameters in RAN.0, anyhow it would be good idea to move them
  //  to EEPROM so that eventual radio access network variants can be supported without
  //  changing the firware.
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
  
  // Read URI from EEPROM
  int ix=0;
  while(ix<64)
  {
    if(EEPROM.read(EEPROM_URI+ix)==0) break;
    uri = uri + (char)EEPROM.read(EEPROM_URI+ix);
    ix++; 
  }
  
  // Read URI_TO from EEPROM
  ix=0;
  while(ix<64)
  {
    if(EEPROM.read(EEPROM_URI_TO+ix)==0) break;
    uri_to = uri_to + (char)EEPROM.read(EEPROM_URI_TO+ix);
    ix++; 
  }
  
  // We setup here the Watchdog timer. Sleep duration will be set before sleep anyway.
  MCUSR &= ~(1<<WDRF);  // Clear reset flag 
  WDTCSR |= (1<<WDCE) | (1<<WDE); // Setting WDCE gives us 4 clock cycles time to change WDE
  WDTCSR =  1<<WDP2 | 1<<WDP1; // Set default sleep to 1 second.
  WDTCSR |= _BV(WDIE);  // Enable watchdog interrupt.
}

void sleep_0_5_s()
{
  MCUSR &= ~(1<<WDRF);
  WDTCSR |= (1<<WDCE) | (1<<WDE);
  WDTCSR =  1<<WDP2 | 1<<WDP0;
  WDTCSR |= _BV(WDIE);
  
  // Enter sleep mode
    //logMessage("Sleeping");
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);  
    sleep_enable();
    sleep_mode();
    
    // We come here after the WDT wakes us up
    // Disable sleep and power up all peripherals
    sleep_disable(); 
    power_all_enable();
}

void set_sleep_0_25_s()
{
  MCUSR &= ~(1<<WDRF);
  WDTCSR |= (1<<WDCE) | (1<<WDE);
  WDTCSR =  1<<WDP2;
  WDTCSR |= _BV(WDIE);    
}

void loop(void)
{
      sleep_0_5_s();
      
      unsigned long start = millis();
      int toff_correction = tx_slot();
      int tspent = (millis() - start) % 1000;
      if(tspent < 365 && (toff_correction + 365-tspent) > 0)
        delay(toff_correction + 365-tspent);
      else if(toff_correction + 1365-tspent > 0)
        delay(toff_correction + 1365-tspent);  
}

int tx_slot()
{
    int toff = 0;
    
    //logMessage("Powering up radio");
    radio.powerUp();
    
    while(!network_ok)
       scanForNet();
      
     radio.stopListening();
     bool ok = radio.sendMessage("MSG " + uri_to + " ping");
     radio.startListening();
     if(ok)
     {
       String toff_msg = radio.readMessage(100);
       char char_string[toff_msg.length()+1];
       toff_msg.toCharArray(char_string, toff_msg.length()+1);
       toff = atoi(char_string);
 
       if(toff >=0 && toff <=999)
       {
          toff = 350 - toff;  
       }
     }
     radio.powerDown(); 
     
     // Reset tx_fail if we got a message trough, increase otherwise.
     tx_fail=(ok)?0:tx_fail+1;  
     
     network_ok = (tx_fail<=5);
     
    return toff;
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
       radio.setChannel(ch);
       String msg = radio.readMessage(1500);
       if(msg.startsWith("BCH"))
       {        
         // Store this as last known good channel
         if(ch != EEPROM.read(EEPROM_RFCH))
           EEPROM.write(EEPROM_RFCH, ch);
           
         // We now need to register to the AP
         radio.stopListening();
         bool ok = radio.sendMessage("REG " + uri);
         radio.startListening();
         
         if(!ok)
           continue;
         
         msg = radio.readMessage(1500);
         // Check registration ACK here and continue scan if not ACK
         
         network_ok = true;  
         return;
       }    
    }
    
    // Not found, start from the first channel.
    scan_start = 0;
  }
}
