#!   /usr/bin/env   python
#    coding: utf8
'''
Script to write the SFP calibration values to a WR Device (using WRCORE commands)

@file
@author Felipe Torres
@date Sep. 22, 2015
@copyright LGPL v2.1
@see http://www.ohwr.org
@see http://www.sevensols.com
@ingroup tools
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
import argparse as arg
import urllib2
import time
import sys

sys.path.append('../../')

from py7slib.bridges.VUART_bridge import *
from py7slib.bridges.serial_bridge import *

def main():
    '''
    Tool for writing the SFP Data Base and Init script of a WR Device (with WRCORE)
    '''
    sfp_db = {}
    sfp_db['wr0-blue'] = []
    sfp_db['wr1-blue'] = []
    sfp_db['wr0-violet'] = []
    sfp_db['wr1-violet'] = []

    SFP_BLUE = "sfp add AXGE-1254-0531"
    SFP_VIOLET = "sfp add AXGE-3454-0531"

    parser = arg.ArgumentParser(description='EEPROM writing tool for WRCORE')

    parser.add_argument('--bus','-b',help='Bus',choices=['ethbone','serial'], \
    required=True)
    parser.add_argument('--lun','-l',help='Logical Unit (IP/Serial Port)',type=str,required=True)
    parser.add_argument('--url','-u',help='Url with the calibration parameters')
    parser.add_argument('--init','-i',help='Init script file')
    parser.add_argument('--debug','-d',help='Enable debug output',action="store_true", \
    default=False)
    args = parser.parse_args()

    if args.bus == 'ethbone':
        uart = VUART_bridge('eth', args.lun, args.debug)
    else:
        uart = Serial_bridge(port="/dev/ttyUSB%s" % args.lun, verbose=args.debug)
    uart.open()

    if args.url:
        attemps = 0
        print("Fetching data for delays...")
        try:
            response = urllib2.urlopen(args.url, timeout=5)
            content = response.read()
            if len(content.splitlines())-1 != 4:
                print("Retrieved SFP DB csv is not well formed. Skipping SFP DB writing.")
            else:
                lines = content.splitlines()
                for i in range(1, 5):
                    line = lines[i].split(',')
                    sfp_db[line[0]] = line[1:]

                print("Writing SFP data to the WR Device...")

                uart.sendCommand("sfp erase")
                for key in sfp_db:
                    cur_sfp = SFP_BLUE if "blue" in key else SFP_VIOLET
                    cmd = "%s %s %s %s %s" % (cur_sfp, key[:3], sfp_db[key][2], \
                    sfp_db[key][1], sfp_db[key][0])
                    uart.sendCommand(cmd)
                    time.sleep(0.5)  # For serial

        except urllib2.URLError as e:
            attemps += 1
            if attemps >= 4:
                print("Could not retrieve data from the given url. SFP DB is not going to be writed.")
            print("Error retrieving data from url: %s, retrying..." % (e.message))

    if args.init:
        print("Writing init script...")
        uart.sendCommand("init erase")
        with open(args.init) as file:
            for line in file.readlines():
                uart.sendCommand("init add %s" % line[:-1])  # Remove the \n

    print("All the configuration is writed to the device.")


if __name__ == '__main__':
    main()
