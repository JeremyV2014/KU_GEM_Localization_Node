# Quick and dirty sender script for grabbing GNSS receiver messages via serial and passing them over UDP

import socket
import serial # /dev/ttyUSB0 38400 8 data bits, 1 stop bit, no parity
from collections import namedtuple # Possible structure to utilize for constructing the message

# Open and configure serial port
ser = serial.Serial()
ser.baudrate = 38400
ser.port = '/dev/ttyUSB0'
ser.open()
print(ser.is_open) # TODO - Implement serial check

UDP_IP = "127.0.0.1" # TODO - Determine address scheme for vehicle
UDP_PORT = 5005 # TODO - Pick a port for the data

# Example of how we might construct a message
LocMsg = namedtuple("LocMsg", "Longitude Latitude Altitude LostSignalTime Confidence")
# How you would init an instance of this object
msg = LocMsg(Longitude=10, Latitude=20, Altitude=350, LostSignalTime=0, Confidence=0.5)

# Create UDP socket
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

while True:
    # TODO - read data more elegantly and parse it
    s = ser.readlines(10) # Just read everything for now
    # TODO - processing of the data
    # TODO - store the data in the proper message format
    sock.sendto(s[0], (UDP_IP, UDP_PORT)) # Pass through over UDP

ser.close() # Good practice to close this... not that we'll ever reach this