#!   /usr/bin/env   python
# -*- coding: utf-8 -*
'''
This file contains the eb1 class which is a child
of the abstract class GenDrv (gendrvr.py)


@date Created on Apr 24, 2014
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
import subprocess
import os
# Import common modules
from gendrvr import *

class EB1(GenDrvr):
    '''
    The EB1 class has been created to interface WB access within
    the WRS. 
    
    We have create a simple library that open the device and can perform
    read/write on the WB bus.
    The read/write block data function are not implemented for this driver
    to keep it as simple as possible. 
    '''
    
    def __init__(self,LUN, show_dbg=False):
        '''
        Constructor 
        @param LUN the logical unit, with this driver it is not need as we should have only one 
        WB bus on the FPGA connected to the ARM CPU
        '''
        self.show_dbg=show_dbg
        self.load_lib("libeb1.so")
        
        if self.show_dbg: print self.info()+"\n"
        self.open(LUN)
        
    def open(self, LUN):
        '''
        Open the device and map to the FPGA bus
        '''
        self.hdev=self.lib.EB1_open()
        if self.hdev==0:
            raise NameError("Could not open device")
        
    def close(self):
        '''
        Close the device and unmap
        '''
        self.lib.EB1_close()
        
    def devread(self, bar, offset, width):
        '''
        Method that do a read on the devices using /dev/mem device
        @param bar BAR used by PCIe bus
        @param offset address within bar
        @param width data size (1, 2, or 4 bytes)
        '''
        address = offset
        INTP = POINTER(c_uint)
        data = c_uint(0xBADC0FFE)
        pData = cast(addressof(data), INTP)
        ret=self.lib.EB1_wishbone_RW(self.hdev,c_uint(address),pData,0)
        if self.show_dbg: print "R@x%08X > 0x%08x" %(address, pData[0])
        if ret !=0:
            raise NameError('Bad Wishbone Read') 
        return pData[0]
        
        
    def devwrite(self, bar, offset, width, datum):
        '''
        Method that do a write on the devices using /dev/mem device
        @param bar BAR used by PCIe bus
        @param offset address within bar
        @param width data size (1, 2, or 4 bytes)
        @param datum data value that need to be written
        '''
        address = offset
        INTP = POINTER(c_uint)
        data = c_uint(datum)
        pData = cast(addressof(data), INTP)
        if self.show_dbg: print "W@x%08X < 0x%08x" %( address, pData[0])
        ret=self.lib.EB1_wishbone_RW(self.hdev,c_uint(address),pData,1)
        if ret !=0:
            raise NameError('Bad Wishbone Write @0x%08x > 0x%08x (ret=%d)' %(address,datum, ret)) 
        return pData[0]
    
    def info(self):
        """get a string describing the interface the driver is bound to """
        inf = (c_char*60)()
        self.lib.EB1_version(inf)
        return "EB1 library (%s): git rev %s" % (self.libname,inf.value)


