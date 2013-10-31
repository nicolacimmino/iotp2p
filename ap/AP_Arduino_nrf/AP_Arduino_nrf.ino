/*
 * D3N Access Point (based on Arduino Yun)
 * Author: Nicola Cimmino
 * Date: V0  12.10.2013
 * 
 * Credits: we make use of a modified version of the cryptolib written by Cathedrow (https://github.com/Cathedrow/Cryptosuite)
 * Add proper credits and contact the author.
 * We make use of aJson (https://github.com/interactive-matter/aJson/)
 */

#include <sha256.h>
//#include <Process.h>
#include <aJSON.h>
#include <Ethernet.h>
#include <SPI.h>



int8_t ak[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x11, 0x11, 0x11, 0x11 };

byte mac[] = { 0x90, 0xA2, 0xDA, 0x0D, 0x63, 0x4F };
 
void setup() 
{
   //Bridge.begin();
   Ethernet.begin(mac);
   Serial.begin(9600);  
}

void loop() 
{
  Serial.println("a");
  // Send a pulse to inform we are alive.
  //PostD3NMessage("http://d3n.coelicloud.net/AP000/pulse.txt", "pulse", ak);
  RegisterNode("A000", "http://nicolacimmino.com");
  
  delay(1000);
}

/*
 * Register a node with its tracker
 */
 
String RegisterNode(String uri, String url)
{
  EthernetClient client;
  Serial.println("b");
  if (client.connect("192.168.0.250", 3000)) {
    Serial.println("connected");
    //client.println("REG "+uri+" "+url);
    client.println("OK");
  } else {
    Serial.println("connection failed");
  }
  
  while(client.available()) {
    char c = client.read();
    Serial.print(c);
  }  
  
  Serial.println("b1");
  /*
  if(client.connected())
  { 
  
  Serial.println("c");
  client.flush();
  Serial.println("d");
  client.stop();
  Serial.println("e");
  }*/
}


/*
String PostD3NMessage(String qid, String message, int8_t *ak)
{
  int seed = GetCurrentSeed(qid, "w");
  String mac = GenrateMAC(message, ak, seed);
  return ForwardD3NMessage(qid, message, mac, seed);
}
/*
int GetCurrentSeed(String qid, String op)
{
   Process p;
   p.begin("curl"); 
   String params = qid+"?info=getSeed&p1="+op;
   Serial.println(params);
   p.addParameter(params); 
   p.run();      

   char response[100];
   int px=0;
   while (p.available()>0) 
   {
     if(px<100)
     {
       response[px++] = p.read();
     }
   }
   response[px]=0;
  
   return atoi(response);
}
*/

/*
 * Forward a D3N message
 */
/*String ForwardD3NMessage(String qid, String message, String mac, int seed)
{
   Process p;
   p.begin("curl"); 
   String params = qid+"?message="+message+"&mac="+mac+"&seed="+String(seed, DEC);
   Serial.println(params);
   p.addParameter(params); 
   p.run();      

   String response="";
   while (p.available()>0) 
   {
     char c = p.read();
     response=response+String(c);
   }
   Serial.println(response);
   return response;
}
*/
/*
 * Generates a MAC given a message, AK and seed.
 */ 
/*String GenrateMAC(String message, int8_t* ak, int seed)
{
  Sha256.init();
  
  int p=0;
  
  // Four bytes for the seed
  for(p=0;p<4;p++)
  {
    Sha256.write((seed>>(p*8))&0xFF);  
  }
  
  // The AK
  for(p=0;p<16;p++)
  {
    Sha256.write(ak[p]);  
  }
  Serial.println();
  
  // The message
  for(p=0;p<message.length();p++)
  {
    Sha256.write((int8_t)message.charAt(p));  
  }

  uint8_t* mac = Sha256.result();
  
  // Hex encode the MAC
  String result="";
  for(p=0;p<32;p++)
  {
   if(mac[p]<=0xF)
   {
     result+="0"+String(mac[p],HEX);
   }
   else
   {
     result+=String(mac[p],HEX);     
   }
  }

  return result;  
}
*/

