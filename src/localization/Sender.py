"""
"   Program name:   Sender
"   Developer:      Jeremy Maxey-Vesperman
"   Modified:       06/10/2019
"   Purpose:        Interfaces with S1216DR8P GNSS + IMU Reciever.
"                   Passively reads data on specified USB serial port.
"                   Parses data into a navigation message packet that is transmitted
"                   via UDP to specified desitination IP address on specified port.
"""

# Library for navigation message parsing
from NavMessageParsing import NavMessageParsing

import time
import socket
import serial

# Serial Configuration
SER_BAUD = 38400
SER_PORT = '/dev/ttyUSB0'
SER_RETRY_DELAY = 1  # seconds to wait

# GNSS UDP Socket Configuration
UDP_IP = "192.168.1.139"
UDP_PORT = 5005

MSG_ATTEMPT_RECONNECT = "Reconnect Attempt: {} - Failed to open serial device. Trying again in {} second(s)..."
MSG_RECONNECT_SUCCESS = "Successfully connected to serial device after {} attempt(s)"


def openSerial(sock, parser, port, bdrate):
    # Open and configure serial port
    ser = serial.Serial()
    ser.baudrate = bdrate
    ser.port = port

    # Attempt to open the serial port
    attemptSerialOpen(ser)
    # Keep trying until successful
    i = 1
    while (not ser.is_open):
        # Broadcast last location message
        sock.sendto(str(parser.getLocPacket()).encode(), (UDP_IP, UDP_PORT))
        print(MSG_ATTEMPT_RECONNECT.format(i, SER_RETRY_DELAY))
        print()
        time.sleep(SER_RETRY_DELAY)
        attemptSerialOpen(ser)
        i += 1

    # Connection successful. Return serial object to caller so they can work with it
    print(MSG_RECONNECT_SUCCESS.format(i))
    return ser


def attemptSerialOpen(serialObj):
    try:
        serialObj.open()
    except (serial.SerialException):
        pass


def createUDPSocket():
    # Create UDP socket
    return socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP


def main():
    sock = createUDPSocket()
    parser = NavMessageParsing()
    ser = openSerial(sock, parser, SER_PORT, SER_BAUD)

    # Run indefinitely...
    while True:
        if (ser.is_open):
            try:
                msgs = ser.readlines(10) # Just read everything for now
                tag = parser.parseNavMessage(msgs)
                # Avoid sending redundant packets by sending only on receiving one specific message
                if (tag == '$GNGGA'):
                    sock.sendto(str(parser.getLocPacket()).encode(), (UDP_IP, UDP_PORT))
            except (serial.serialutil.SerialException):
                ser.close()
                print("Bad serial read. Resetting connection...")
        else:
            ser.close()
            print("Serial connection interrupted. Attempting reconnect.")
            ser = openSerial(sock, parser, SER_PORT, SER_BAUD)  # Reattempt a connection


if __name__ == "__main__":
    main()
