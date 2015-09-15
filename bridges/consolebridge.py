#!   /usr/bin/env   python
#    coding: utf8
'''
ConsoleBridge abstract class

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
import abc

class ConsoleBridge() :
    '''
    Abstract class that defines the methods that must be implemented in order to connect to the console of a WR device.

    Attributes:
        port (str) : Port used for the connection
        interface (str) : Interface used for the connection
    '''

    @abc.abstractmethod
    def open(self) :
        '''
        Method to open a new connection with a WR device.

        Raises:
            ConsoleError : When the specified device fails opening.
        '''

    @abc.abstractmethod
    def close(self) :
        '''
        Method to close an existing connection with a WR device.

        Raises:
            ConsoleError : When the connection fails closing.
        '''

    @abc.abstractmethod
    def setCommand(self, cmd) :
        '''
        Method to pass a command to a WR device

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

    @abc.abstractmethod
    def isOpen(self) :
        '''
        This method checks wheter device connection is stablished.

        Returns:
            True if open() method has previously called, False otherwise.
        '''

    @staticmethod
    def scan(bus, subnet) :
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
                · "serial" : Scan only devices conneted to a serial port.
            subnet(str) : Subnet IP address to scan for devices. Only used with
            option "eth" or "all". Example: subnet="192.168.7.0/24".


        Returns:
            A dict where the keys are the seen before. The value is a list with
            ports/ip dirs. availables. When there're no conneted devices, an
            empty list is returned. A example:
            {'pci':[], 'eth':["192.168.1.3"], 'serial':["/dev/ttyUSB0",
            "dev/ttyUSB1"]}

        Raises:
            ConsoleError : When one of the specified interfaces could not be scanned.
        '''

        devices = {'eth':[], 'pci':[], 'serial':[]}

        # Call the child-classes' scan method
        try :
            if bus == "all" :
                vuart_devs = VUART_bridge.scan("all")
                devices['eth'] = vuart_devs['eth']
                devices['pci'] = vuart_devs['pci']

                devices['serial'] = Serial_bridge.scan()

            elif bus == "pci" :
                devices['pci'] = VUART_bridge.scan("pci")

            elif bus == "eth" :
                devices['eth'] = VUART_bridge.scan("eth")

            elif bus == "serial" :
                devices['serial'] = Serial_bridge.scan()

        except ConsoleError as error :
            # Throw it to a upper layer
            raise error

        return devices
