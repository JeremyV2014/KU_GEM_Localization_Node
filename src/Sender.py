# Quick and dirty sender script for grabbing GNSS receiver messages via serial and passing them over UDP

import time
import socket
import serial
from collections import namedtuple  # Possible structure to utilize for constructing the message

# Serial Configuration
SER_BAUD = 38400
SER_PORT = '/dev/ttyUSB0'
SER_RETRY_DELAY = 1 # seconds to wait

# GNSS UDP Socket Configuration
UDP_IP = "127.0.0.1"  # TODO - Determine address scheme for vehicle
UDP_PORT = 5005  # TODO - Pick a port for the data

# Example of how we might construct a message
LOC_MSG = namedtuple("LocMsg", "Latitude Longitude Altitude LastSignalTime Confidence")
LAST_GNSS_POS_TIME = "-1"
LOC_PACKET = LOC_MSG(0, 0, 0, -1, -1)

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

def parsePSTI(fields):
    zAxisAngularRate = fields[11]  # Deg/sec

    print("Z-Axis Angular Rate: {}°/sec".format(zAxisAngularRate))

def parseGNRMC(fields):
    course = fields[8]  # 000.0 - 359.9
    speedKPH = fields[7]  # 0000.0 - 1800.0
    mode = fields[12][0:1]

    print("Course over ground: {}°".format(course))
    print("Speed over ground: {}kph".format(speedKPH))
    print("Mode: {}".format(mode))

def parseGNVTG(fields):
    course = fields[1]  # 000.0 - 359.9
    speedKPH = fields[7]  # 0000.0 - 1800.0
    mode = fields[9][0:1]

    print("Course: {}°".format(course))
    print("Speed: {}kph".format(speedKPH))
    print("Mode: {}".format(mode))

def parseGNGGA(fields):
    utcTime = fields[1]
    latitude = fields[2]
    latDirection = fields[3]  # N / S of equator
    longitude = fields[4]
    longDirection = fields[5]  # E / W of Prime Meridian
    solutionType = fields[6]
    altitude = fields[9]

    utcHH = utcTime[0:2]
    utcMM = utcTime[2:4]
    utcSS = utcTime[4:6]

    latDeg = int(latitude[0:2]) # 00-90 deg
    latMin = int(latitude[2:4]) # 00-59
    latSec = round((float(latitude[4:9]) * 60), 3)  # 0000-9999

    longDeg = int(longitude[0:3])  # 000-180 deg
    longMin = int(longitude[3:5])  # 00-59
    longSec = (float(longitude[5:10]) * 60)  # 0000-9999

    solutionTypeInt = int(solutionType)

    print("Time: {}:{}:{} UTC".format(utcHH, utcMM, utcSS))
    print("Latitude: {:2d}°{:02d}'{:02.3f}\" {}".format(latDeg, latMin, latSec, latDirection))
    print("Longitude: {:3d}°{:02d}'{:02.3f}\" {}".format(longDeg, longMin, longSec, longDirection))
    print("Altitude: {} meters MSL".format(altitude))

    global LAST_GNSS_POS_TIME
    if (solutionTypeInt != 0):
        LAST_GNSS_POS_TIME = utcTime

    global LOC_PACKET;  # TODO - Figure out a better way to do this...
    LOC_PACKET = LOC_MSG(Latitude=latitude, Longitude=longitude, Altitude=altitude, LastSignalTime=LAST_GNSS_POS_TIME, Confidence=solutionType)

def unhandledMsg(fields):
    #print("Message {} not handled".format(fields[0]))
    pass

def parseNavMessage(recvMsgs):
    msgType = { '$GNRMC' :   parseGNRMC,
                '$GNVTG' :   parseGNVTG,
                '$GNGGA' :   parseGNGGA,
                '$PSTI'  :   parsePSTI
    }

    for msg in recvMsgs:
        fields = splitMsg(msg.decode())
        tag = fields[0]
        msgType.get(tag, unhandledMsg)(fields)

    return tag


def splitMsg(msg):
    fields = msg.split(',')
    return fields

def main():
    ser = openSerial(SER_PORT, SER_BAUD)
    sock = createUDPSocket()

    while True:
        if (ser.is_open):
            try:
                msgs = ser.readlines(10) # Just read everything for now
                tag = parseNavMessage(msgs)
                if (tag == '$GNGGA'):
                    sock.sendto(str(LOC_PACKET).encode(), (UDP_IP, UDP_PORT))
            except (serial.serialutil.SerialException):
                ser.close()
                print("Bad serial read. Resetting connection...")

            # TODO - processing of velocity data
        else:
            ser.close()
            print("Serial connection interrupted. Attempting reconnect.")
            sock.sendto(str(LOC_PACKET).encode(), (UDP_IP, UDP_PORT)) # Broadcast last location message
            ser = openSerial(SER_PORT, SER_BAUD)

    ser.close() # Good practice to close this... not that we'll ever reach this

if __name__== "__main__":
    main()
