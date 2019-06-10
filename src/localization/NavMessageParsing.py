"""
"   Program name:   NavMessageParsing
"   Developer:      Jeremy Maxey-Vesperman
"   Modified:       06/10/2019
"   Purpose:        Library for parsing navigation messages
"""

from collections import namedtuple


class NavMessageParsing:
    # Constructor
    def __init__(self):
        # Structure of navigation message object
        self.LOC_MSG = namedtuple("LocMsg",
                                  "Latitude "
                                  "LatDirection "
                                  "Longitude "
                                  "LongDirection "
                                  "Altitude "
                                  "Speed Course "
                                  "TurningRate "
                                  "LastSignalTime "
                                  "Confidence")
        self.LAST_LAT = "0"
        self.LAST_LAT_DIRECTION = "-"
        self.LAST_LONG = "0"
        self.LAST_LONG_DIRECTION = "-"
        self.LAST_ALT = "0"
        self.LAST_SPEED = "0"
        self.LAST_COURSE = "0"
        self.LAST_TURNING_RATE = "0"
        self.LAST_GNSS_POS_TIME = "-1"
        self.LAST_CONFIDENCE = "-1"

    # IMU data message
    def parsePSTI(self, fields):
        self.LAST_TURNING_RATE = fields[11]  # Deg/sec

        print("Z-Axis Angular Rate: {}°/sec".format(self.LAST_TURNING_RATE))

    # Course and speed over ground message
    def parseGNRMC(self, fields):
        self.LAST_COURSE = fields[8]  # 000.0 - 359.9
        self.LAST_SPEED = fields[7]  # 0000.0 - 1800.0 kph
        mode = fields[12][0:1]

        print("Course over ground: {}°".format(self.LAST_COURSE))
        print("Speed over ground: {}kph".format(self.LAST_SPEED))
        print("Mode: {}".format(mode))

    # Course and speed message
    def parseGNVTG(self, fields):
        self.LAST_COURSE = fields[1]  # 000.0 - 359.9
        self.LAST_SPEED = fields[7]  # 0000.0 - 1800.0
        mode = fields[9][0:1]

        print("Course: {}°".format(self.LAST_COURSE))
        print("Speed: {}kph".format(self.LAST_SPEED))
        print("Mode: {}".format(mode))

    # GNSS localization message
    def parseGNGGA(self, fields):
        self.LAST_LAT = fields[2]
        self.LAST_LAT_DIRECTION = fields[3]  # N / S of equator
        self.LAST_LONG = fields[4]
        self.LAST_LONG_DIRECTION = fields[5]  # E / W of Prime Meridian
        self.LAST_ALT = fields[9]
        self.LAST_CONFIDENCE = fields[6]

        utcTime = fields[1]
        utcHH = utcTime[0:2]
        utcMM = utcTime[2:4]
        utcSS = utcTime[4:6]

        latDeg = int(self.LAST_LAT[0:2]) # 00-90 deg
        latMin = int(self.LAST_LAT[2:4]) # 00-59
        latSec = round((float(self.LAST_LAT[4:9]) * 60), 3)  # 0000-9999

        longDeg = int(self.LAST_LONG[0:3])  # 000-180 deg
        longMin = int(self.LAST_LONG[3:5])  # 00-59
        longSec = (float(self.LAST_LONG[5:10]) * 60)  # 0000-9999

        solutionTypeInt = int(self.LAST_CONFIDENCE)

        print("Time: {}:{}:{} UTC".format(utcHH, utcMM, utcSS))
        print("Latitude: {:2d}°{:02d}'{:02.3f}\" {}".format(latDeg, latMin, latSec, self.LAST_LAT_DIRECTION))
        print("Longitude: {:3d}°{:02d}'{:02.3f}\" {}".format(longDeg, longMin, longSec, self.LAST_LONG_DIRECTION))
        print("Altitude: {} meters MSL".format(self.LAST_ALT))

        if (solutionTypeInt != 0):
            self.LAST_GNSS_POS_TIME = utcTime

    # Ignore tags of unhandled messages
    def unhandledMsg(self, fields):
        pass

    # Splits message received over serial into fields
    def splitMsg(msg):
        fields = msg.split(',')
        return fields

    # Handles interpreting serial messages received from receiver
    def parseNavMessage(self, recvMsgs):
        msgType = { '$GNRMC' :   self.parseGNRMC,
                    '$GNVTG' :   self.parseGNVTG,
                    '$GNGGA' :   self.parseGNGGA,
                    '$PSTI'  :   self.parsePSTI
        }

        tag = None

        for msg in recvMsgs:
            fields = self.splitMsg(msg.decode())
            tag = fields[0]
            msgType.get(tag, self.unhandledMsg)(fields)

        return tag

    # Returns last known localization values
    def getLocPacket(self):
        return self.LOC_MSG(Latitude=self.LAST_LAT,
                            LatDirection=self.LAST_LAT_DIRECTION,
                            Longitude=self.LAST_LONG,
                            LongDirection=self.LAST_LONG_DIRECTION,
                            Altitude=self.LAST_ALT,
                            Speed=self.LAST_SPEED,
                            Course=self.LAST_COURSE,
                            TurningRate=self.LAST_TURNING_RATE,
                            LastSignalTime=self.LAST_GNSS_POS_TIME,
                            Confidence=self.LAST_CONFIDENCE)

    # Parses UDP packet fields
    def parseField(self, packet, packetName):
        searchStr = packetName + "='"
        startOffset = len(searchStr)
        startIdx = packet.index(searchStr) + startOffset
        stopIdx = len(packet) - 1
        data = packet[startIdx:stopIdx]

        return data

    # Decodes localization packet received over UDP
    def parseLocPacket(self, locMsg):
        # Make sure this is a localization packet
        if locMsg.startswith("LocMsg"):
            dataStartIdx = locMsg.index("(") + 1
            dataStopIdx = locMsg.index(")")
            data = locMsg[dataStartIdx:dataStopIdx]
            fields = data.split(', ')

            latPacket = fields[0]
            latitude = self.parseField(latPacket, "Latitude")

            latDirPacket = fields[1]
            latDirection = self.parseField(latDirPacket, "LatDirection")

            longPacket = fields[2]
            longitude = self.parseField(longPacket, "Longitude")

            longDirPacket = fields[3]
            longDirection = self.parseField(longDirPacket, "LongDirection")

            altPacket = fields[4]
            altitude = self.parseField(altPacket, "Altitude")

            speedPacket = fields[5]
            speed = self.parseField(speedPacket, "Speed")

            coursePacket = fields[6]
            course = self.parseField(coursePacket, "Course")

            turningRatePacket = fields[7]
            turningRate = self.parseField(turningRatePacket, "TurningRate")

            lastSignalTimePacket = fields[8]
            lastSignalTime = self.parseField(lastSignalTimePacket, "LastSignalTime")

            confidencePacket = fields[9]
            confidence = self.parseField(confidencePacket, "Confidence")

            return self.LOC_MSG(Latitude=latitude,
                                LatDirection=latDirection,
                                Longitude=longitude,
                                LongDirection=longDirection,
                                Altitude=altitude,
                                Speed=speed,
                                Course=course,
                                TurningRate=turningRate,
                                LastSignalTime=lastSignalTime,
                                Confidence=confidence)
