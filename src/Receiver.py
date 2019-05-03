# Quick and dirty receiver script to test communication

import socket

UDP_IP = "127.0.0.1" # TODO - decide on address scheme
UDP_PORT = 5005 # TODO - decide on port

# Create UDP socket
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT)) # Rx

while True:
    # TODO - parse the message
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message:", data.decode()) # print out the message
    # TODO - do something with the message