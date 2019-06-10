"""
"   Program name:   Receiver
"   Developer:      Jeremy Maxey-Vesperman
"   Modified:       06/10/2019
"   Purpose:        Parses localization message UDP packets.
"                   Currently prints out message to console.
"                   In future, could be incorporated into control logic for GEM car.
"""

# Library for navigation message parsing
from NavMessageParsing import NavMessageParsing

import socket

# Device IP address and port we expect data on
UDP_IP = "192.168.1.139"
UDP_PORT = 5005

# Create UDP socket
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT)) # Rx

# Run forever...
while True:
    # Get data
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    msg = data.decode()

    # Decode message and store in navigation message object
    parser = NavMessageParsing()
    navMsg = parser.parseLocPacket(msg)

    # Print message to console
    print(navMsg)
    print()

