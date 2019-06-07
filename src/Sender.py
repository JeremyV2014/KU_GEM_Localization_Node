# Sender script for Localization

import NavMessageParsing

import time
import socket
import serial

# Serial Configuration
SER_BAUD = 38400
SER_PORT = '/dev/ttyUSB0'
SER_RETRY_DELAY = 1 # seconds to wait

# GNSS UDP Socket Configuration
UDP_IP = "192.168.1.100"
UDP_PORT = 5005

def openSerial(port, bdrate):
    # Open and configure serial port
    ser = serial.Serial()
    ser.baudrate = bdrate
    ser.port = port

    # Attempt to open the serial port
    attemptSerialOpen(ser)
    # Keep trying until successful
    i = 1
    while (not ser.is_open):
        print("Reconnect Attempt: {} - Failed to open serial device. Trying again in {} second(s)...".format(i, SER_RETRY_DELAY))
        time.sleep(SER_RETRY_DELAY)
        attemptSerialOpen(ser)
        i += 1

    # Connection successful. Return serial object to caller so they can work with it
    print("Successfully connected to serial device after {} attempt(s)".format(i))
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
    ser = openSerial(SER_PORT, SER_BAUD)
    sock = createUDPSocket()

    while True:
        if (ser.is_open):
            try:
                msgs = ser.readlines(10) # Just read everything for now
                tag = NavMessageParsing.parseNavMessage(msgs)
                if (tag == '$GNGGA'):
                    sock.sendto(str(NavMessageParsing.getLocPacket()).encode(), (UDP_IP, UDP_PORT))
            except (serial.serialutil.SerialException):
                ser.close()
                print("Bad serial read. Resetting connection...")

            # TODO - processing of velocity data
        else:
            ser.close()
            print("Serial connection interrupted. Attempting reconnect.")
            sock.sendto(str(NavMessageParsing.getLocPacket()).encode(), (UDP_IP, UDP_PORT)) # Broadcast last location message
            ser = openSerial(SER_PORT, SER_BAUD)

    ser.close() # Good practice to close this... not that we'll ever reach this

if __name__== "__main__":
    main()
