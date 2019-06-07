# Library for parsing Navigation messages

from collections import namedtuple  # Possible structure to utilize for constructing the message

LOC_MSG = namedtuple("LocMsg", "Latitude LatDirection Longitude LongDirection Altitude Speed Course TurningRate LastSignalTime Confidence")

LAST_LAT = "0"
LAST_LAT_DIRECTION = "-"
LAST_LONG = "0"
LAST_LONG_DIRECTION = "-"
LAST_ALT = "0"
LAST_SPEED = "0"
LAST_COURSE = "0"
LAST_TURNING_RATE = "0"
LAST_GNSS_POS_TIME = "-1"
LAST_CONFIDENCE = "-1"


def parsePSTI(fields):
    global LAST_TURNING_RATE

    LAST_TURNING_RATE = fields[11]  # Deg/sec

    print("Z-Axis Angular Rate: {}°/sec".format(LAST_TURNING_RATE))


def parseGNRMC(fields):
    global LAST_COURSE, LAST_SPEED

    LAST_COURSE = fields[8]  # 000.0 - 359.9
    LAST_SPEED = fields[7]  # 0000.0 - 1800.0 kph
    mode = fields[12][0:1]

    print("Course over ground: {}°".format(LAST_COURSE))
    print("Speed over ground: {}kph".format(LAST_SPEED))
    print("Mode: {}".format(mode))


def parseGNVTG(fields):
    global LAST_COURSE, LAST_SPEED

    LAST_COURSE = fields[1]  # 000.0 - 359.9
    LAST_SPEED = fields[7]  # 0000.0 - 1800.0
    mode = fields[9][0:1]

    print("Course: {}°".format(LAST_COURSE))
    print("Speed: {}kph".format(LAST_SPEED))
    print("Mode: {}".format(mode))


def parseGNGGA(fields):
    global LAST_GNSS_POS_TIME, \
        LAST_LAT, \
        LAST_LAT_DIRECTION, \
        LAST_LONG, \
        LAST_LONG_DIRECTION, \
        LAST_ALT, \
        LAST_CONFIDENCE

    LAST_LAT = fields[2]
    LAST_LAT_DIRECTION = fields[3]  # N / S of equator
    LAST_LONG = fields[4]
    LAST_LONG_DIRECTION = fields[5]  # E / W of Prime Meridian
    LAST_ALT = fields[9]
    LAST_CONFIDENCE = fields[6]

    utcTime = fields[1]
    utcHH = utcTime[0:2]
    utcMM = utcTime[2:4]
    utcSS = utcTime[4:6]

    latDeg = int(LAST_LAT[0:2]) # 00-90 deg
    latMin = int(LAST_LAT[2:4]) # 00-59
    latSec = round((float(LAST_LAT[4:9]) * 60), 3)  # 0000-9999

    longDeg = int(LAST_LONG[0:3])  # 000-180 deg
    longMin = int(LAST_LONG[3:5])  # 00-59
    longSec = (float(LAST_LONG[5:10]) * 60)  # 0000-9999

    solutionTypeInt = int(LAST_CONFIDENCE)

    print("Time: {}:{}:{} UTC".format(utcHH, utcMM, utcSS))
    print("Latitude: {:2d}°{:02d}'{:02.3f}\" {}".format(latDeg, latMin, latSec, LAST_LAT_DIRECTION))
    print("Longitude: {:3d}°{:02d}'{:02.3f}\" {}".format(longDeg, longMin, longSec, LAST_LONG_DIRECTION))
    print("Altitude: {} meters MSL".format(LAST_ALT))

    if (solutionTypeInt != 0):
        LAST_GNSS_POS_TIME = utcTime


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


def getLocPacket():
    global LOC_MSG
    return LOC_MSG(Latitude=LAST_LAT,
                   LatDirection=LAST_LAT_DIRECTION,
                   Longitude=LAST_LONG,
                   LongDirection=LAST_LONG_DIRECTION,
                   Altitude=LAST_ALT,
                   Speed=LAST_SPEED,
                   Course=LAST_COURSE,
                   TurningRate=LAST_TURNING_RATE,
                   LastSignalTime=LAST_GNSS_POS_TIME,
                   Confidence=LAST_CONFIDENCE)


def parseLocPacket(locMsg):  #  LocMsg(Latitude='0000.0000', LatDirection='N', Longitude='00000.0000', LongDirection='E', Altitude='0.0', Speed='000.0', Course='000.0', TurningRate='0.01', LastSignalTime='-1', Confidence='0')
    global LOC_MSG

    if locMsg.startswith("LocMsg"):
        dataStartIdx = locMsg.index("(") + 1
        dataStopIdx = locMsg.index(")")
        data = locMsg[dataStartIdx:dataStopIdx]
        fields = data.split(', ')

        latPacket = fields[0]
        latitude = parseField(latPacket, "Latitude")
        latVal = float(latitude)

        latDirPacket = fields[1]
        latDirection = parseField(latDirPacket, "LatDirection")

        longPacket = fields[2]
        longitude = parseField(longPacket, "Longitude")
        longVal = float(longitude)

        longDirPacket = fields[3]
        longDirection = parseField(longDirPacket, "LongDirection")

        altPacket = fields[4]
        altitude = parseField(altPacket, "Altitude")
        altVal = float(altitude)

        speedPacket = fields[5]
        speed = parseField(speedPacket, "Speed")
        speedVal = float(speed)

        coursePacket = fields[6]
        course = parseField(coursePacket, "Course")
        courseVal = float(course)

        turningRatePacket = fields[7]
        turningRate = parseField(turningRatePacket, "TurningRate")
        turningRateVal = float(turningRate)

        lastSignalTimePacket = fields[8]
        lastSignalTime = parseField(lastSignalTimePacket, "LastSignalTime")

        confidencePacket = fields[9]
        confidence = parseField(confidencePacket, "Confidence")
        confidenceVal = int(confidence)

        return LOC_MSG(Latitude=latitude,
                       LatDirection=latDirection,
                       Longitude=longitude,
                       LongDirection=longDirection,
                       Altitude=altitude,
                       Speed=speed,
                       Course=course,
                       TurningRate=turningRate,
                       LastSignalTime=lastSignalTime,
                       Confidence=confidence)


def parseField(packet, packetName):
    searchStr = packetName + "='"
    startOffset = len(searchStr)
    startIdx = packet.index(searchStr) + startOffset
    stopIdx = len(packet) - 1
    data = packet[startIdx:stopIdx]

    return data