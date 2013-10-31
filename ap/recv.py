#
# Example program to receive packets from the radio
#
# J Paulo Barraca <jpbarraca@gmail.com>
#
# Test comment to test git
from nrf24 import NRF24
import time

pipes = [[0x32, 0x33, 0x34, 0x35, 0x36], [0x32, 0x33, 0x34, 0x35, 0x36]]

radio = NRF24()

# We have CE on GPIO 22 (pin 15)
# and IRQ on GPIO 24 (pin 18)
# Pin numbers are to be used if GPIO pin mode is changed to BOARD
#  in the constructor of NRF24
radio.begin(0, 0, 15, 18) 

radio.setCRCLength(NRF24.CRC_DISABLED)

radio.setRetries(15,15)

radio.setPayloadSize(16)
radio.setChannel(0x02)
radio.setDataRate(NRF24.BR_250KBPS)
radio.setPALevel(NRF24.PA_MAX)

radio.setAutoAck(0) 

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

radio.startListening()
radio.stopListening()

radio.printDetails()


#buf = [0x00, 0x00, 0x01, 'd', 'e', 'f', 'g', 'h', 'i', 'l', 'm', 'n', 'o', 'p', 'q', 'r']
#while True:
#    radio.write(buf)
#    time.sleep(1)


radio.startListening()

try:
 while True:
    pipe = [0]
    while not radio.available(pipe, True): # Changed irq wait to False
        time.sleep(1000/1000000.0)
    print "Available"
    recv_buffer = []
    radio.read(recv_buffer)

    print recv_buffer
except KeyboardInterrupt:
 print "Terminating"
finally:
 radio.close()

