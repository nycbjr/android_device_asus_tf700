#-------------------------------------------------------------------------------
# Name:        nvcstest.py
# Purpose:
#
# Created:     01/23/2012
#
# Copyright (c) 2007 - 2012 NVIDIA Corporation.  All rights reserved.
#
# NVIDIA Corporation and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA Corporation is strictly prohibited.
#
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import nvcamera
import string
import os
import time
import shutil
import math
import traceback
import re
import nvrawfile

# global variables
gTestDir = "/data/NVCSTest"
gImagerId = 0

# nvcstest module version
__version__ = "1.0.4"

def printVersionInformation():
    # print nvcstest version
    print "nvcstest version: %s" % __version__

    # print nvcamera module /nvcs version
    print "nvcamera version: %s" % nvcamera.__version__

class LogLevel(object):
    debug = 1
    info = 2
    warning = 3
    error = 4
    fatal = 5

class NvCSTestResult(object):
    SUCCESS = 1
    SKIPPED = 2
    ERROR = 3

class Singleton(object):
    """ A Pythonic Singleton """
    def __new__(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = object.__new__(cls, *args, **kwargs)
        return cls._inst

class Logger(Singleton):
    "Logger class"

    logLevel = LogLevel.debug
    logFileHandle = None
    logFileName = "summarylog.txt"

    def __init__(self):
        global gTestDir
        if(self.logFileHandle == None):
            if(os.path.isdir(gTestDir)):
                shutil.rmtree(gTestDir + "/")
            os.mkdir(gTestDir)
            logFilePath = os.path.join(gTestDir, self.logFileName)
            self.logFileHandle = open(logFilePath,"w")

    def __del__(self):
        if (self.logFileHandle != None):
            print "close file"
            self.logFileHandle.close()
            self.logFileHandle = None

    def __getLevelString(self, level):
        if (level == LogLevel.debug):
            return "DEBUG"
        elif (level == LogLevel.info):
            return "INFO"
        elif (level == LogLevel.warning):
            return "WARNING"
        elif (level == LogLevel.error):
            return "ERROR"
        elif (level == LogLevel.fatal):
            return "FATAL"

    def setLevel(self, level):
        self.setLevel = level

    def info(self, msg):
        self.__log(LogLevel.info, msg)

    def debug(self, msg):
        self.__log(LogLevel.debug, msg)

    def warning(self, msg):
        self.__log(LogLevel.warning, msg)

    def error(self, msg):
        self.__log(LogLevel.error, msg)

    def fatal(self, msg):
        self.__log(LogLevel.fatal, msg)

    def __log(self, level, msg):
        if (level < self.logLevel):
            return
        levelString = self.__getLevelString(level)
        print "%s: %s" % (levelString, msg)
        self.logFileHandle.write("%s: %s\n" % (levelString, msg))

class NvCSTestBase:
    "NvCSTest Base Class"

    testID = None
    imagerID = 0
    graphType = "JPEG"
    obCamera = None
    __obGraph = None
    testDir = None
    logger = None
    nvrf = None

    isPreviewRunning = False
    saveFiles = False
    concurrentRawDumpFlag = 0
    isGraphCreated = False
    concurrentRawImageDir = "/data/raw"

    def __init__(self, testID=None, graphType="Jpeg"):
        global gTestDir, gImagerId
        self.testID = testID
        self.imagerID = gImagerId
        self.graphType= graphType
        self.obCamera = nvcamera.Camera()
        self.__obGraph = nvcamera.Graph()
        self.testDir = os.path.join(gTestDir, testID)
        self.logger = Logger()
        self.nvrf = nvrawfile.NvRawFile()

    def __createGraph(self):
        self.__obGraph.setImager(self.imagerID)
        self.__obGraph.preview()
        self.__obGraph.still(0, 0, self.graphType)
        self.__obGraph.run()

        self.isGraphCreated = True

    def __deleteGraph(self):
        self.__obGraph.stop()
        self.__obGraph.close()
        self.isGraphCreated = False

    def captureJpegImage(self, imageName):
        self.logger.debug("capturing jpeg image")
        if(self.graphType == "Jpeg"):
            if (self.concurrentRawDumpFlag == 7):
                if os.path.exists(self.concurrentRawImageDir):
                    fileList = os.listdir(self.concurrentRawImageDir)
                    for fileName in fileList:
                        filePath = os.path.join(self.concurrentRawImageDir, fileName)
                        os.remove(filePath)
                else:
                    os.mkdir(self.concurrentRawImageDir)

            self.obCamera.halfpress(4000)
            self.obCamera.waitForEvent(12000, nvcamera.CamConst_ALGS)
            self.obCamera.still(os.path.join(self.testDir, imageName + ".jpg"))
            self.obCamera.waitForEvent(12000, nvcamera.CamConst_CAP_READY, nvcamera.CamConst_CAP_FILE_READY)

            if (self.concurrentRawDumpFlag == 7):
                # get the list of raw files in /data/raw directory
                rawFilesList = os.listdir(self.concurrentRawImageDir)

                # rename the file
                os.rename(os.path.join(self.concurrentRawImageDir, rawFilesList[0]),
                os.path.join(self.testDir, imageName + ".nvraw"))

            self.obCamera.hp_release()
            self.isPreviewRunning = False
        else:
            self.logger.error("Can't take Jpeg image with %s graph" % self.graphType)
            raise NvCSTestException("Can't take Jpeg image with %s graph" % self.graphType)

    def captureRAWImage(self, imageName):
        self.logger.debug("Capturing RAW image")
        if(self.graphType == "Bayer"):
            self.obCamera.halfpress(4000)
            self.obCamera.waitForEvent(12000, nvcamera.CamConst_ALGS)
            self.obCamera.still(os.path.join(self.testDir, imageName + ".nvraw"))
            self.obCamera.waitForEvent(12000, nvcamera.CamConst_CAP_READY)
            self.obCamera.hp_release()
        else:
            self.logger.error("Can't take RAW image with %s graph" % self.graphType)
            raise NvCSTestException("Can't take RAW image with %s graph" % self.graphType)

    def setConcurrentRawDumpFlag(self, flag):
        errVal = nvcamera.NvSuccess
        try:
            self.obCamera.setAttr(nvcamera.attr_concurrentrawdumpflag, flag)
        except NvCameraException, err:
            errVal = err.value
        if (errVal == nvcamera.NvSuccess):
            self.concurrentRawDumpFlag = flag
        return errVal

    def run(self, args=None):
        retVal = 0
        try:
            self.logger.info("############################################")
            self.logger.info("Running the %s test..." % self.testID)
            self.logger.info("############################################")

            # create test specific dir
            os.makedirs(self.testDir)
            self.__createGraph()

            retVal = self.runPreTest()
            if (retVal != NvCSTestResult.SUCCESS):
                return retVal

            retVal = self.runTest(args)

            self.stopTest()
            return retVal

        except Exception, err:
            self.logger.error("TEST FAILURE: %s" % self.testID)
            self.logger.error("Error: %s" % str(err))
            traceback.print_exc()
            self.stopTest()
            raise

        return retVal

    def stopTest(self):
        if (self.isPreviewRunning):
            self.logger.debug("Stop Preview")
            self.stopPreview()
        if (self.isGraphCreated):
            self.logger.debug("Delete graph...")
            self.__deleteGraph()

    def startPreview(self):
        self.obCamera.setAttr(nvcamera.attr_pauseaftercapture, 1)
        if (self.isPreviewRunning == False):
            self.obCamera.startPreview()
            self.isPreviewRunning = True

    def stopPreview(self):
        self.obCamera.stopPreview()
        self.obCamera.waitForEvent(12000, nvcamera.CamConst_PREVIEW_EOS)
        self.isPreviewRunning = False

    def runTest(self, args=None):
        return NvCSTestResult.SUCCESS

    def runPreTest(self, args=None):
        return NvCSTestResult.SUCCESS

class NvCSTestException(Exception):
    "NvCSTest Exception Class"

    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class NvCSJPEGCapTest(NvCSTestBase):
    "JPEG Capture Test"

    def __init__(self):
        NvCSTestBase.__init__(self, "Jpeg_Capture")

    def runTest(self, args):
        print "capturing jpeg image..."

        self.startPreview()
        self.captureJpegImage("out_%s_test" % self.testID)
        self.stopPreview()

        return NvCSTestResult.SUCCESS

class NvCSPropertyTest(NvCSTestBase):
    "Property verification test"

    def __init__(self):
        NvCSTestBase.__init__(self, "Property_Verification")

    def runTest(self, args):
        # take an image with contrast
        print "capturing jpeg image with contrast value %d..." % 100
        self.obCamera.setAttr(nvcamera.attr_contrast, 50)
        self.captureJpegImage("out_%s_%s_%d_test" % (self.testID, "contrast", 100))

        # take an image with brightness
        self.obCamera.setAttr(nvcamera.attr_brightness, 14.0)
        print "capturing jpeg image with brightness value %d..." % 50.0
        self.captureJpegImage("out_%s_%s_%d_test" % (self.testID, "brightness", 50.0))

        # take an image with max (5.0) saturation
        print "capturing jpeg image with saturation value %d..." % 0.0
        self.obCamera.setAttr(nvcamera.attr_saturation, 5.0)
        self.captureJpegImage("out_%s_%s_%f_test" % (self.testID, "saturation", 0.0))
        return NvCSTestResult.SUCCESS

class NvCSEffectTest(NvCSTestBase):
    "Effect verification test"
    effectValues = ["None",
                    "Noise",
                    "Emboss",
                    "Negative",
                    "Sketch",
                    "OilPaint",
                    "Hatch",
                    "Gpen",
                    "Antialias",
                    "DeRing",
                    "Solarize",
                    "Posterize",
                    "Sepia",
                    "BW"
                  ]
    def __init__(self):
        NvCSTestBase.__init__(self, "Effect_Verification")

    def runTest(self, args):
        for effectVal in self.effectValues:
            # take an image with specified effect
            print "capturing image with %s effect..." % effectVal
            self.obCamera.setAttr(nvcamera.attr_effect, effectVal)
            # take an image
            self.captureJpegImage("out_%s_%s_test" % (self.testID, effectVal))
        return NvCSTestResult.SUCCESS

class NvCSFlickerTest(NvCSTestBase):
    "Flicker verification test"

    flickerValues = ["off", "auto", "50", "60"]
    def __init__(self):
        NvCSTestBase.__init__(self, "Flicker")

    def runTest(self, args):
        for flickerVal in self.flickerValues:
            # take an image with specified Flicker effect
            print "capturing jpeg image flicker value %s..." % flickerVal
            self.obCamera.setAttr(nvcamera.attr_flicker, flickerVal)
            # take an image
            self.captureJpegImage("out_%s_%s_test" % (self.testID, flickerVal))
        return NvCSTestResult.SUCCESS

class NvCSAWBTest(NvCSTestBase):
    "Auto White Balance test"
    awbValues = ["Off",
                 "Auto",
                 "Tungsten",
                 "Fluorescent",
                 "Sunny",
                 "Shade",
                 "Cloudy",
                 "Incandescent",
                 "Flash",
                 "Horizon"]

    def __init__(self):
        NvCSTestBase.__init__(self, "AWB")

    def runTest(self, args):
        # take an image with specified AWB setting
        for awbValue in self.awbValues:
            print "capturing jpeg image with AWB set to %s..." % awbValue
            self.obCamera.setAttr(nvcamera.attr_whitebalance, awbValue)
            # take an image
            self.captureJpegImage("out_%s_%s_test" % (self.testID, awbValue))
        return NvCSTestResult.SUCCESS

class NvCSMeteringTest(NvCSTestBase):
    "Metering test"
    meteringmodeValues = ["center", "spot", "fullframe"]

    def __init__(self):
        NvCSTestBase.__init__(self, "Metering")

    def runTest(self, args):
        # take an image with specified meteringmode value
        for meteringMode in self.meteringmodeValues:
            print "capturing jpeg image with Metering set to %s..." % meteringMode
            self.obCamera.setAttr(nvcamera.attr_meteringmode, meteringMode)
            # take an image
            self.captureJpegImage("out_%s_%s_test" % (self.testID, meteringMode))
        return NvCSTestResult.SUCCESS

class NvCSAFTest(NvCSTestBase):
    "AF test"
    afValues = [-1, 0]
    def __init__(self):
        NvCSTestBase.__init__(self, "AF")

    def runTest(self, args):
        for afVal in self.afValues:
            # take an image with specified AF value
            print "capturing jpeg image with AF set to %d..." % afVal
            self.obCamera.setAttr(nvcamera.attr_autofocus, afVal)
            self.startPreview()
            # take an image
            self.captureJpegImage("out_%s_%d_test" % (self.testID, afVal))
        return NvCSTestResult.SUCCESS

class NvCSAutoFrameRateTest(NvCSTestBase):
    "FPS test"

    def __init__(self):
        NvCSTestBase.__init__(self, "FPS")

    def runTest(self, args):
        # take an image with 0 AFR
        self.obCamera.setAttr(nvcamera.attr_autoframerate, 0)
        self.startPreview()
        # take an image
        self.captureJpegImage("out_%s_%d_test" % (self.testID, 0))
        return NvCSTestResult.SUCCESS

class NvCSJpegRotationTest(NvCSTestBase):
    "JPEG Rotation test"

    rotationValues = ["None", "Rotate90", "Rotate180", "Rotate270"]

    def __init__(self):
        NvCSTestBase.__init__(self, "Jpeg_Rotation")

    def runTest(self, args):
        for rotationVal in self.rotationValues:
            # take an image specified rotation
            print "capturing jpeg image with rotation set to %s..." % rotationVal
            self.obCamera.setAttr(nvcamera.attr_transform, rotationVal)
            self.startPreview()
            # take an image
            self.captureJpegImage("out_%s_%s_test" % (self.testID, rotationVal))
        return NvCSTestResult.SUCCESS

class NvCSExposureTimeTest(NvCSTestBase):
    "Exposure Time Test"

    # set exposure values to test
    exposureTimeValues = [0.5, 1.0, 5, 10, 37.5, 100, 200]
    errMargin = 10.0/100.0

    def __init__(self):
        NvCSTestBase.__init__(self, "Exposure_Time")

    def runPreTest(self):
        err = self.setConcurrentRawDumpFlag(7)
        if (err != nvcamera.NvSuccess):
            self.logger.info("raw capture is not supported")
            return NvCSTestResult.SKIPPED
        else:
            return NvCSTestResult.SUCCESS

    def runTest(self, args):
        if (args != None):
            self.exposureTimeValues = args

        retVal = NvCSTestResult.SUCCESS

        for exposureTime in self.exposureTimeValues:
            # take an image specified rotation
            self.logger.info("capturing raw image with exposure time set to %d..." % exposureTime)
            self.startPreview()

            self.obCamera.setAttr(nvcamera.attr_exposuretime, float(exposureTime)/1000)
            # take an image
            rawFileName = "out_%s_%s_test" % (self.testID, exposureTime)
            self.captureJpegImage(rawFileName)

            self.stopPreview()

            rawFileName = os.path.join(self.testDir, rawFileName + ".nvraw")

            if not self.nvrf.readFile(rawFileName):
                self.logger.error("couldn't open the file: %s" % rawFileName)
                retVal = NvCSTestResult.ERROR
                break
            minExpectedExpTime = exposureTime - (exposureTime * self.errMargin)
            maxExpectedExpTime = exposureTime + (exposureTime * self.errMargin)

            # check SensorExposure value
            if (self.nvrf._exposureTime >= minExpectedExpTime and
                self.nvrf._exposureTime <= maxExpectedExpTime):
                self.logger.error( "exposure value is not correct in the raw header: %.2f" %
                                    self.nvrf._exposureTime)
                self.logger.error( "exposure value should be between %.2f and %.2f" %
                                    (minExpectedExpTime, maxExpectedExpTime))
                retVal = NvCSTestResult.ERROR
                break

            expTime = self.obCamera.getAttr(nvcamera.attr_exposuretime)
            if (expTime >= minExpectedExpTime and expTime <= maxExpectedExpTime):
                self.logger.error("exposuretime is not set int the driver...")
                self.logger.error( "exposure value should be between %.2f and %.2f" %
                                    (minExpectedExpTime, maxExpectedExpTime))
                retVal = NvCSTestResult.ERROR
                break

        return retVal

class NvCSGainTest(NvCSTestBase):
    "Gain test"

    startGainVal = 1.5
    stopGainVal = 10.5
    step = 1.5

    def __init__(self):
        NvCSTestBase.__init__(self, "Gain")

    def runPreTest(self):
        err = self.setConcurrentRawDumpFlag(7)
        if (err != nvcamera.NvSuccess):
            self.logger.info("raw capture is not supported")
            return NvCSTestResult.SKIPPED
        else:
            return NvCSTestResult.SUCCESS

    def runTest(self, args):
        while(self.startGainVal <= self.stopGainVal):
            self.startPreview()
            self.obCamera.setAttr(nvcamera.attr_bayergains, [self.startGainVal] * 4)

            # take an image
            fileName = "out_%s_%d_test" % (self.testID, self.startGainVal)
            self.logger.info("capturing jpeg image with gains set to %.2f..." % self.startGainVal)

            # take an image with specified ISO
            self.captureJpegImage(fileName)

            self.stopPreview()

            rawFileName = os.path.join(self.testDir, fileName + ".nvraw")

            if not self.nvrf.readFile(rawFileName):
                self.logger.error("couldn't open the file: %s" % rawFileName)
                return NvCSTestResult.ERROR

            if (self.nvrf._sensorGains[0] !=  float(self.startGainVal)):
                self.logger.error("SensorGains value is not correct in the raw header: %f" % self.nvrf._sensorGains[0])
                return NvCSTestResult.ERROR
            self.startGainVal = self.startGainVal + self.step

        return NvCSTestResult.SUCCESS

class NvCSFocusPosTest(NvCSTestBase):
    "Focus Position test"

    # Python range specified in this way is really [0,1000)
    # which means, excluding 1000. In this example: 0, 100, ... 900
    focusPosValues = range(0, 1000, 100)

    def __init__(self):
        NvCSTestBase.__init__(self, "Focus_Position")

    def runPreTest(self):

        # check if the focuser is supported
        try:
            self.obCamera.getAttr(nvcamera.attr_focuspos)
        except nvcamera.NvCameraException, err:
            if (err.value == nvcamera.NvError_NotSupported):
                self.logger.info("focuser is not present..")
                return NvCSTestResult.SKIPPED
            else:
                print err.value
                raise

        err = self.setConcurrentRawDumpFlag(7)
        if (err != nvcamera.NvSuccess):
            self.logger.info("raw capture is not supported")
            return NvCSTestResult.SKIPPED
        else:
            return NvCSTestResult.SUCCESS

    def runTest(self, args):
        retVal = NvCSTestResult.SUCCESS

        for focusPos in self.focusPosValues:
            # take an image with focus position set to 1
            self.logger.info("capturing jpeg image with focuspos set to %d..." % focusPos)

            self.startPreview()

            self.obCamera.setAttr(nvcamera.attr_focuspos, focusPos)

            # take an image
            fileName = "out_%s_%d_test" % (self.testID, focusPos)
            self.captureJpegImage(fileName)

            self.stopPreview()

            rawFileName = os.path.join(self.testDir, fileName + ".nvraw")

            if not self.nvrf.readFile(rawFileName):
                self.logger.error("couldn't open the file: %s" % rawFileName)
                retVal = NvCSTestResult.ERROR
                break

            if (self.nvrf._focusPosition !=  focusPos):
                self.logger.error("FocusPosition value is not correct in the raw header: %d" % self.nvrf._focusPosition)
                retVal = NvCSTestResult.ERROR
                break

            focusPosVal = self.obCamera.getAttr(nvcamera.attr_focuspos)
            if (focusPos != focusPosVal):
                self.logger.error("focus position value is not correct in the driver: %d..." % focusPosVal)
                retVal = NvCSTestResult.ERROR
                break

        return retVal

class NvCSMultipleRawTest(NvCSTestBase):
    "Multiple Raw Image Test"

    imageNumValues = range(1, 101)

    def __init__(self):
        NvCSTestBase.__init__(self, "Multiple_Raw")

    def __del__(self):
        if (os.path.exists(self.testDir)):
            shutil.rmtree(self.testDir)

    def runPreTest(self):
        err = self.setConcurrentRawDumpFlag(7)
        if (err != nvcamera.NvSuccess):
            self.logger.info("raw capture is not supported")
            return NvCSTestResult.SKIPPED
        else:
            return NvCSTestResult.SUCCESS

    def runTest(self, args):
        retVal = NvCSTestResult.SUCCESS

        for imageNum in self.imageNumValues:
            # take an image
            fileName = "out_%s_%d_test" % (self.testID, imageNum)
            filePath = os.path.join(self.testDir, fileName + ".nvraw")

            self.startPreview()

            self.logger.debug("capturing image: %d" % imageNum)
            self.captureJpegImage(fileName)

            self.stopPreview()

            if os.path.exists(filePath) != True:
                self.logger.error("couldn't find file: %s" % filePath)
                retVal = NvCSTestResult.ERROR
                break

            if not self.nvrf.readFile(filePath):
                self.logger.error("couldn't open the file: %s" % filePath)
                retVal = NvCSTestResult.ERROR

            pattern = ".*"
            if((imageNum % 10) == 0):
                regexOb = re.compile(pattern)
                for fname in os.listdir(self.testDir):
                    if regexOb.search(fname):
                        self.logger.debug("removing file %s" % fname)
                        os.remove(os.path.join(self.testDir, fname))

        return retVal

class NvCSRAWCapTest(NvCSTestBase):
    "RAW Capture Test"

    def __init__(self):
        NvCSTestBase.__init__(self, "RAW_Capture", "Bayer")

    def runTest(self, args):
        retVal = NvCSTestResult.SUCCESS

        self.startPreview()

        fileName = "out_%s_test" % self.testID
        filePath = os.path.join(self.testDir, fileName + ".nvraw")

        try:
            self.captureRAWImage(fileName)
        except NvCameraException, err:
            if (err.value == nvcamera.NvError_NotSupported):
                self.logger.info("raw capture is not supported")
                return NvCSTestResult.SKIPPED
            else:
                raise

        self.stopPreview()

        if (os.path.exists(filePath) != True):
            self.logger.error("Couldn't capture the raw image: %s.nvraw" % filePath)
            retVal = NvCSTestResult.ERROR

        return retVal

class NvCSConcurrentRawCapTest(NvCSTestBase):
    "Concurrent raw capture test"

    def __init__(self):
        NvCSTestBase.__init__(self, "Concurrent_Raw_Capture")

    def runPreTest(self):
        err = self.setConcurrentRawDumpFlag(7)
        if (err != nvcamera.NvSuccess):
            self.logger.info("raw capture is not supported")
            return NvCSTestResult.SKIPPED
        else:
            return NvCSTestResult.SUCCESS

    def runTest(self, args):
        retVal = NvCSTestResult.SUCCESS

        self.startPreview()

        fileName = "out_%s_test" % self.testID
        filePath = os.path.join(self.testDir, fileName + ".nvraw")

        self.captureJpegImage(fileName)

        self.stopPreview()

        if (os.path.exists(filePath) != True):
            self.logger.error("Couldn't capture the raw image: %s" % filePath)
            retVal = NvCSTestResult.ERROR

        if not self.nvrf.readFile(filePath):
            self.logger.error("couldn't open the file: %s" % filePath)
            retVal = NvCSTestResult.ERROR

        # Check no values over 2**bitsPerSample
        if (max(self.nvrf._pixelData.tolist()) > (2**self.nvrf._bitsPerSample)):
            self.logger.error("pixel value is over %d." % self.nvrf._bitsPerSample)
            retVal = NvCSTestResult.ERROR

        return retVal
