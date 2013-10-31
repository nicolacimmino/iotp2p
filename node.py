#!/usr/bin/env python
#
# Helper to test tracker.py, modify freely to suite your needs
#

import socket

HOST = '192.168.0.250'    # The remote host
PORT = 3000              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
#s.send('TRK A000FFBB34BC45\n')
s.send('REG A001 192.168.0.250:4001\n')
#s.send('LOC 123123000\n')
data = s.recv(1024)
s.close()
print data

