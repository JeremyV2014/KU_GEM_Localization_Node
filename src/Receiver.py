# Receiver script for Localization

import NavMessageParsing

import socket

UDP_IP = "192.168.1.104"
UDP_PORT = 5005

# Create UDP socket
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT)) # Rx

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    msg = data.decode()

    navMsg = NavMessageParsing.parseLocPacket(msg)
    print(navMsg)
    print()

