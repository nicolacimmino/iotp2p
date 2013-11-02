#
# Example program to receive packets from the radio
#
# J Paulo Barraca <jpbarraca@gmail.com>
#
from nrf24 import NRF24
import time

pipes = [[0x70, 0x70, 0x70, 0x70, 0x71], [0x70, 0x70, 0x70, 0x70, 0x70]]

radio = NRF24()

# We have CE on GPIO 22 (pin 15)
# and IRQ on GPIO 24 (pin 18)
# Pin numbers are to be used if GPIO pin mode is changed to BOARD
#  in the constructor of NRF24
radio.begin(0, 0, 15, 18) 

radio.setCRCLength(NRF24.CRC_8)

radio.setRetries(15,15)

radio.setPayloadSize(4)
radio.setChannel(0x0A)
#radio.setDataRate(NRF24.BR_250KBPS)
radio.setDataRate(NRF24.BR_2MBPS)

radio.setPALevel(NRF24.PA_MAX)

radio.setAutoAck(1) 

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

radio.startListening()
radio.stopListening()

radio.printDetails()


#buf = ['d', 'e', 'f', 'g']
#while True:
#    radio.write(buf)
#    time.sleep(1)


radio.startListening()

try:
 while True:
    pipe = [0]
    while not radio.available(pipe, False): # Changed irq wait to False
        time.sleep(1000/1000000.0)
    recv_buffer = []
    radio.read(recv_buffer)

    print recv_buffer
    radio.stopListening()
    time.sleep(0.01)
    buf = ['d', 'e', 'f', 'g']
    radio.write(buf)
    radio.startListening()
except KeyboardInterrupt:
 print "Terminating"
finally:
 radio.close()

