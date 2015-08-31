#!   /usr/bin/env   python
#    coding: utf8
'''
The VUART_bridge class allows to connect with WR devices over Etherbone or PCI bus.

@file
@author Felipe Torres
@date August 24, 2015
@copyright LGPL v2.1
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

# Imports
import os
import math
from subprocess import check_output
from pts_core.bridges.consolebridge import *

class VUART_bridge(ConsoleBridge) :
    '''
    Class to handle connection with WR devices through the Virtual UART.

    This class implements the interface defined in ConsoleBridge abstract class
    for devices connected on the PCI bus or Ethernet (using Etherbone).
    '''

    def open(self, interface, port) :
        '''
        Method to open a new connection with a WR device.

        Args:
            interface (str) : Specifies the connection type: "eth" or "pci".
            port (str) : Specifies the port/ip direction for the device.

        Raises:
            ConsoleError : When the specified device fails opening.
        '''

    PCI_DEVICE_ID_SPEC = 0x018d
    PCI_VENDOR_ID_CERN = 0x10dc

    def close(self) :
        '''
        Method to close an existing connection with a WR device.

        Raises:
            ConsoleError : When the connection fails closing.
        '''

    def ask(self, cmd) :
        '''
        Method for reading the value of a parameter of the device.

        This method writes a command to the input of the device and retrieves
        the response of it.

        Args:
            cmd (str) : Command

        Raises:
            CmdNotValid : When the passed command is not accepted by the device.
            ConsoleError : When an error was occured while reading/writing.
        '''

    def cmd(self, cmd) :
        '''
        Method to set the value of a parameter of the device.

        This method writes a command to the input and retrieves the device
        response (if any).

        Args:
            cmd (str) : Command

        Returns:
            A string with the device's response. A empty string is returned when
            there isn't response from device.

        Raises:
            CmdNotValid : When the passed command is not accepted by the device.
            ConsoleError : When an error was occured while reading/writing.
        '''

    @staticmethod
    def scan(bus="all", subnet="192.168.7.0/24") :
        '''
        Method to scan WR devices connected to the PC.

        This method look for devices connected through the following interfaces:
        · Serial interface
        · PCIe bus.
        · Ethernet in devices with Etherbone included.

        Args:
            bus (str) : Scan in all interfaces, or only for a specific interface.
            Options available:
                · "all" : Scan all interfaces.
                · "pci" : Scan only devices conneted to the PCI bus.
                · "eth" : Scan only devices conneted to Ethernet with Etherbone.
            subnet(str) : Subnet IP address to scan for devices. Only used with
            option "eth" or "all". Example: subnet="192.168.7.0/24".

        Returns:
            A dict where the keys are the seen before. The value is a list with
            ports/ip dirs. availables. When there're no conneted devices, an
            empty list is returned. A example:
            {'pci':[], 'eth':["192.168.1.3"]}

        Raises:
            ConsoleError : When one of the specified interfaces could not be scanned.
        '''

        devices = {'eth':[], 'pci':[]}

        if bus == 'all' :
            devices['pci'] = VUART_bridge.scan(bus='pci')['pci']
            devices['eth'] = VUART_bridge.scan(bus='eth')['eth']

        elif bus == "pci" :
            # Current search filters by SPEC boards : device 018d
            cmd = ["""lspci | grep %02x | cut -d' ' -f 1""" % VUART_bridge.PCI_DEVICE_ID_SPEC]
            raw_devices = check_output(cmd, shell=True).splitlines()
            # Check vendor id -> CERN: 0x10dc
            for dev in raw_devices :
                cmd = ["cat", "/sys/bus/pci/devices/0000:%s/vendor" % dev]
                ret = check_output(cmd)[:-1]
                if int(ret,16) == VUART_bridge.PCI_VENDOR_ID_CERN :
                    devices['pci'].append(dev)

        elif bus == "eth" :
            # If fping is installed, only check with eb-discover alive IPs
            if not os.system("command -v fping > /dev/null") :   # FAST MODE
                # Retrieve a list of alive devices in the subnet
                cmd = """fping -C 1 -q -g %s 2>&1 | grep -v \": -\"""" % (subnet)
                raw_alive_devs = check_output(cmd,shell=True).splitlines()
                unknown_devices = [None, ] * len(raw_alive_devs)
                i = 0
                for dev in raw_alive_devs :
                    unknown_devices[i] = dev.split(":")[0].rstrip(' ')
                    i += 1
                raw_alive_devs = None

                # Now check which ones are WR devices using eb-discover
                for udev in unknown_devices :
                    args = "udp/%s" % (udev)
                    ret = check_output(["eb-discover", args])
                    if ret != '' : # is a WR device
                        devices['eth'].append(udev)

            else :                                               # SLOW MODE
                # Scan to find WR devices in the network
                ip, bcast = subnet.split("/")
                end = int( (( math.ceil((32-int(bcast)) / 8.0) % 3) * 2) % 3 )
                lip = ip.split(".")[:end+1]

                buildNextSubnet = lambda root : root.append('0')
                # Generate next ip
                nextIP = lambda ip : ip.append( str( int(ip.pop())+1 ) ) if int(ip[-1]) < 255 else False
                # Check wether a ip direction is complete
                isLastByte = lambda ip : (len(ip) == 4) if (type(ip) == type(list())) else (len(ip.split(".")) == 4)

                def checkDevices(ip,devices) :
                    for i in range(1,255) :
                        ip[-1] = str(i)
                        print "probando ip: %s" % ('.'.join(ip))
                        if isLastByte(ip) :
                            args = "udp/%s" % (ip if type(ip) == type("") else '.'.join(ip))
                            ret = check_output(["eb-discover", args])
                            if ret != '' : # is a WR device
                                devices['eth'].append('.'.join(ip))
                            if int(ip[-1]) == 254 : return

                        else :
                            checkDevices( buildNextSubnet(ip) )


                buildNextSubnet(lip)
                checkDevices(lip,devices)

        return devices
