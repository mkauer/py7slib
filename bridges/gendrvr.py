#!   /usr/bin/env   python
# -*- coding: utf-8 -*
'''
Generic abstract class for bus access


@date Created on Apr 14, 2014
@author: Benoit Rat (benoit<AT>sevensols.com)
@licence: LGPL v2.1
@ref: http://www.ohwr.org
@ref: http://www.sevensols.com
'''

##-------------------------------------------------------------------------------------------------
##                               GNU LESSER GENERAL PUBLIC LICENSE                                |
##                              ------------------------------------                              |
## This source file is free software; you can redistribute it and/or modify it under the terms of |
## the GNU Lesser General Public License as published by the Free Software Foundation; either     |
## version 2.1 of the License, or (at your option) any later version.                             |
## This source is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;       |
## without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.      |
## See the GNU Lesser General Public License for more details.                                    |
## You should have received a copy of the GNU Lesser General Public License along with this       |
## source; if not, download it from http://www.gnu.org/licenses/lgpl-2.1.html                     |
##-------------------------------------------------------------------------------------------------

##-------------------------------------------------------------------------------------------------
##                                            Import                                             --
##-------------------------------------------------------------------------------------------------
# Import system modules
import abc
import os
from ctypes import *


class BusException(Exception):
    pass

class BusWarning(Exception):
    pass


class GenDrvr(object):
    '''
    Abstract class that represent the Generic Driver to access from Python to the device.
    It is normally used in parallel with a library that call directly the system driver
    
    The following methods must be defined in the children class:
       * open()
       * close()
       * devwrite()
       * devread() 
    '''
    __metaclass__ = abc.ABCMeta
    
    hdev=-1
    bar=0
    ndev=1 ##Actual number detected device on the bus

        
    def load_lib(self,libname=""):
        ## First set library path
        libpath = os.getenv('LD_LIBRARY_PATH')
        here = os.getcwd()
        libpath = here if not libpath else here + ':' + libpath
        os.environ['LD_LIBRARY_PATH'] = libpath
        
        ##Then load the library
        self.libname=libname
        self.lib = cdll.LoadLibrary(self.libname)        


###################### Abstract method that MUST be redefine                                           --

        
    @abc.abstractmethod
    def open(self, LUN):
        '''
        Abstract method to open the device on which the driver perform
        @param LUN Logical Unit Number (i,e. with PCIe it is the slot)
        '''
        
    @abc.abstractmethod
    def close(self):
        '''
        Abstract method to close the device on which the driver perform
        '''
        
    @abc.abstractmethod
    def devread(self, bar, offset, width):
        '''
        Abstract method that do a read on the devices
        @param bar BAR used by PCIe bus
        @param offset address within bar
        @param width data size (1, 2, or 4 bytes)
        '''
        
    @abc.abstractmethod
    def devwrite(self, bar, offset, width, datum):
        '''
        Abstract method that do a read on the devices
        @param bar BAR used by PCIe bus
        @param offset address within bar
        @param width data size (1, 2, or 4 bytes)
        @param datum data value that need to be written
        '''

###################### Not implemented method that could be redefine
        
    def devblockread(self, bar, offset, bsize):
        '''
        Abstract method that do a read on the devices
        @param bar BAR used by PCIe bus
        @param offset address within bar
        @param bsize size in bytes
        '''
        raise NameError('Undef function') 
        return 0;
    
    def devblockwrite(self, bar, offset, ldata):
        '''
        Abstract method that do a read on the devices
        @param bar BAR used by PCIe bus
        @param offset address within bar
        @param ldata list of data to write
        '''
        raise NameError('Undef function') 
        return 0;
        
        
    def irqena(self):
        """enable the interrupt line"""
        raise NameError('Undef function') 
        return 0;

    def getblocksize(self,index=0):
        """return the size of the allocated DMA buffer (in bytes)"""
        raise NameError('Undef function') 
        return 0;

    def info(self):
        """get a string describing the interface the driver is bound to """
        return "%s" %(self.libname)
    
###################### Shortcut methods
        
    def read(self, offset):
        ''' Perform a simple 32b read '''
        return self.devread(self.bar, offset, 4)
        
    def read32(self, offset):
        ''' Perform a simple 32b read '''
        return self.devread(self.bar, offset, 4)
    
    def read16(self, offset):
        ''' Perform a simple 16b read '''
        return self.devread(self.bar, offset, 2)
    
    def read8(self, offset):
        ''' Perform a simple 8b read '''
        return self.devread(self.bar, offset, 1)
    
    def write(self, offset, datum):
        ''' Perform a simple 32b write '''
        self.devwrite(self.bar, offset, 4, datum)
        
    def write32(self, offset, datum):
        ''' Perform a simple 32b write '''
        self.devwrite(self.bar, offset, 4, datum)
    
    def write16(self, offset, datum):
        ''' Perform a simple 16b write '''
        self.devwrite(self.bar, offset, 2, datum)
    
    def write8(self, offset, datum):
        ''' Perform a simple 8b write '''
        self.devwrite(self.bar, offset, 1, datum)
    