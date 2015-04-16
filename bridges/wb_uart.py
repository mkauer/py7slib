#!   /usr/bin/env   python
#    coding: utf8
'''
Implement the access to wishbone UART

@file
@author Felipe Torres
@copyright LGPL v2.1
@see http://www.ohwr.org
@see http://www.sevensols.com
@ingroup bridges
'''


#------------------------------------------------------------------------------|
#                   GNU LESSER GENERAL PUBLIC LICENSE                          |
#                 ------------------------------------                         |
# This source file is free software; you can redistribute it and/or modify it  |
# under the terms of the GNU Lesser General Public License as published by the |
# Free Software Foundation; either version 2.1 of the License, or (at your     |
# option) any later version. This source is distributed in the hope that it    |
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant   |
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser   |
# General Public License for more details. You should have received a copy of  |
# the GNU Lesser General Public License along with this  source; if not,       |
# download it from http://www.gnu.org/licenses/lgpl-2.1.html                   |
#------------------------------------------------------------------------------|

from pts_core.main.ptsexcept import *
from pts_core.misc.serial_str_cleaner import *
from gendrvr import *
import subprocess
import os
import serial
import time
import string

class wb_UART(GenDrvr) :
    '''
    Class that simplifies serial communication for use with WR LEN PTS.

    Example of use:
    '''

    def __init__(self, baudrate=115200, wrtimeout=None, interchartimeout=None, rdtimeout=None) :
        '''
        Class constructor

        '''
        self.PORT = "/dev/ttyUSB"
        self.BAUDRATE = baudrate
        self.WRTIMEOUT = wrtimeout
        self.INTERCHARTIMEOUT = interchartimeout
        self.RDTIMEOUT = rdtimeout
        self._serial = None

    def open(self, LUN=0) :
        '''
        Open serial communication

        Args:
            LUN (str) : Logical Unit Number
            baudrate (int) :  Baud rate such as 9600 or 115200 (default)
            timeout (int) : Set a read timeout value. By default is
            set to 1 second to do blocking writes
        '''
        self.PORT += str(LUN)

        try :
            self._serial = serial.Serial(port=self.PORT, baudrate=self.BAUDRATE,\
            timeout=self.RDTIMEOUT, writeTimeout=self.WRTIMEOUT, interCharTimeout=self.INTERCHARTIMEOUT)
            self._serial.flushOutput()
            print ("Port %s succesfully opened " % (self.PORT))
        except ValueError as e:
            print ("ERROR opening serial port %s: %s" % (self.PORT,e))
            print e
        except serial.SerialException as e:
            print ("ERROR: can't open %s port: %s" % (self.PORT,e))

    def close(self) :
        '''
        Close serial communication
        '''
        self._serial.close()
        print ("Port %s succesfully closed " % self.PORT)

    def devread(self, bar, offset, width) :
        '''
        Method that interfaces with wb read

        Args:
            bar : BAR used by PCIe bus
            offset : address within bar
            width : data size (1, 2, or 4 bytes)
        '''
        cmd = "wb read 0x%X\r" % (offset)
        # print(">\t %s" % (cmd))

        try :
            self._serial.flushInput()
            self._serial.flushOutput()
            bwr = 0
            # Is necessary to write char by char because is needed to make a
            # timeout between each write
            for c in cmd :
                bwr += self._serial.write(c)
                time.sleep(self.INTERCHARTIMEOUT) # Intern interCharTimeout isn't working, so put a manual timeout
            self._serial.flush()

            if bwr != len(cmd):
                raise PtsError("ERROR: Write of command string %s failed. \
                Bytes writed : %d of %d." % (cmd, bwr,len(cmd)))

            # First line readed is the previous command
            rd = self._serial.readline()

            cleaner = str_Cleaner() # Class to help cleaning control characters from str
            clean = cleaner.cleanStr(rd)

            # Remember: '\r' is inserted to cmd
            if cmd[:-1] != clean :
                raise PtsError("ERROR: Write of command %s failed : %s." % (cmd, clean))

            rd = self._serial.readline()

            return int(rd[:-1],0)

        except serial.SerialTimeoutException as e :
            print ("Error: Write timout (%d sec) exceeded : %s" % (self.WRTIMEOUT,e))



    def devwrite(self, bar, offset, width, datum, check=False) :
        '''
        Method that interfaces with wb write
            bar : BAR used by PCIe bus
            offset : address within bar
            width : data size (1, 2, or 4 bytes)
            datum : data value that need to be written
            check : Enables check of writed data
        '''
        cmd = "wb write 0x%X 0x%X\r" % (offset, datum)

        try :
            self._serial.flushInput()
            self._serial.flushOutput()
            bwr = 0
            # Is necessary to write char by char because is needed to make a
            # timeout between each write
            for c in cmd :
                bwr += self._serial.write(c)
                time.sleep(self.INTERCHARTIMEOUT) # Intern interCharTimeout isn't working, so put a manual timeout
            self._serial.flush()

            if bwr != len(cmd):
                raise PtsError("ERROR: Write of string %s failed. Bytes writed : %d of %d." % (cmd, bwr,len(cmd)))

            # Read first line, which is the command we previously send, check it!!
            cleaner = str_Cleaner() # Class to help cleaning control characters from str

            rd = self._serial.readline()

            clean = cleaner.cleanStr(rd)

            # Remember: '\r' is inserted to cmd
            if cmd[:-1] != clean and check:
                raise PtsError("ERROR: Write of command %s failed : %s." % (cmd, clean))


            # Read another line to check if there was any errors
            rd = self._serial.readline()

            # If erros read another line
            if "Error" in rd and check:
                expected = self._serial.readline()
                found = self._serial.readline()
                raise PtsError("ERROR: %s, %s" % (expected[:-4], found[:-4]))

            return bwr

        except serial.SerialTimeoutException as e :
            print ("Error: Write timout (%d sec) exceeded : %s" % (self.WRTIMEOUT,e))


    def cmd_w(self, cmd, output=True) :
        '''
        Method for write commands to WR-LEN
            cmd (str) : A valid command
            output (Boolean) : When enabled, readed lines from serial com. will be returned.

        Returns:
            Outputs a list of str from WR-LEN.
        '''
        cmd = "%s\r" % cmd

        try :
            self._serial.flushInput()
            self._serial.flushOutput()
            bwr = 0
            # Is necessary to write char by char because is needed to make a
            # timeout between each write
            for c in cmd :
                bwr += self._serial.write(c)
                time.sleep(self.INTERCHARTIMEOUT) # Intern interCharTimeout isn't working, so put a manual timeout
            self._serial.flush() # Wait until all data is written

            if bwr != len(cmd):
                raise PtsError("ERROR: Write of string %s failed. Bytes writed : %d of %d." % (cmd, bwr,len(cmd)))

            # Read first line, which is the command we previously send, check it!!
            cleaner = str_Cleaner() # Class to help cleaning control characters from str
            clean = cleaner.cleanStr(self._serial.readline())
            # Remember: '\r' is inserted to cmd
            if cmd[:-1] != clean and check:
                raise PtsError("ERROR: Write of command %s failed : %s." % (cmd, clean))

            # Attempt to read more from input buffer
            # read 1 SFPs in DB
            ret = ""

            if output :
                # while self._serial.inWaiting() > 0 :
                # Read(1000) : Reading byte by byte is not a good idea because
                # inWaiting() gives a lower value than real is. Attempt to read
                # a high number of bytes (more than really would be) so you ensure
                # that always you are reading all data returned by WR-LEN.
                # Reading must be seted to blocking with timeout.
                ret += self._serial.read(1000)
                ret = ret[:-6] # Remove prompt from returned string


            return ret

        except serial.SerialTimeoutException as e :
            print ("Error: Write timout (%d sec) exceeded : %s" % (self.WRTIMEOUT,e))
