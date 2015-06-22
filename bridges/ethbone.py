#!   /usr/bin/env   python
# -*- coding: utf-8 -*
'''
This file contains the etherbone class which is a child of the abstract class GenDrv (gendrvr.py)


Parse etherbone packet with wireshark
=====================================

Copy s4n.lua protocol.
-----------------------

Then if you want to read the lua protocol you need to copy the file `spec/etherbone.lua` from etherbone repo to the wireshark directory

    * Under windows: `C:\\Program Files\\Wireshark`
    * Under ubuntu: `/usr/share/wireshark/`


Activate LUA script.
----------------------

Go to the wireshark directory and edit the file: `init.lua`
You need to replace the begin of the file with:

run_user_scripts_when_superuser = true

-- disable potentialy harmful lua functions when running superuser
if running_superuser_back then


And add to the end of the file the line

    dofile(DATA_DIR.."etherbone.lua")

Install lua libraries
----------------------

    sudo apt-get install lua5.1 lua-bitop

Call back:
http://stackoverflow.com/questions/7259794/how-can-i-get-methods-to-work-as-callbacks-with-python-ctypes


@file
@date Created on Jun 16, 2015
@author Benoit Rat (benoit<AT>sevensols.com)
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

#-------------------------------------------------------------------------------
#                                   Import                                    --
#-------------------------------------------------------------------------------
# Import system modules
import subprocess
import os
import sys
from ctypes import *
import time
import struct





# Import common modules
from gendrvr import *
import binascii

EB_PROTOCOL_VERSION = 1
EB_ABI_VERSION      = 0x04
EB_BUS_MODEL        = [0x44,0x88][sys.maxsize > 2**32]
EB_MEMORY_MODEL     = 0x0000
EB_ABI_CODE         = ((EB_ABI_VERSION << 8) + EB_BUS_MODEL + EB_MEMORY_MODEL)

def py_cb_func(user, dev, op, status):
     if status: raise NameError('Callback Error: %s' % (status))
     print "%x" %(status)

# Import Etherbone structures
class eb_handler(Structure):
     _fields_ = [("sdb_dev", POINTER(c_uint)),
                 ("eb_data", POINTER(c_uint)),
                 ("eb_stat_r", POINTER(c_uint)),
                 ("eb_stat_w", POINTER(c_uint))]



class EthBone(GenDrvr):
    '''The EthBone class has been created to interface WB access using network and etherbone core.

    To use this class you must:
        * Have etherbone core installed as master of the WB crossbar
        * Have set an IP in the lm32 of your device (You might use bootp).
        * Have installed the libetherbone.so in your system

    The read/write block data functions are implemented using transaction.
    This need to be improved.
    '''

    EB_DATAX = 0x0F
    EB_ADDRX = 0xF0

    EB_ENDIAN_MASK   = 0x30
    EB_BIG_ENDIAN    = 0x10
    EB_LITTLE_ENDIAN = 0x20

    EB_OK        = 0  # success


    def __init__(self,LUN, verbose=False):
        '''Constructor

        Args:
            LUN : the logical unit, in etherbone we use a netaddress format given by:
            show_dbg : enables debug info
        '''

        print os.getenv('LD_LIBRARY_PATH')
        self.load_lib("libetherbone.so")

        ##Create empty ptr on structure used by ethbone
        self.socket    = c_uint(0)
        self.device    = c_uint(0)
        self.operation = c_uint(0)
        self.wcrc      = 0

        ##Setup arguments
        self.LUN=LUN
        self.verbose=verbose
        if self.verbose: print self.info()+"\n"

        ##Setup variables
        self.addr_width=self.EB_ADDRX
        self.data_width=self.EB_DATAX
        self.attempts=3
        self.silent=True
        self.format=c_uint8(self.EB_BIG_ENDIAN | self.data_width)


        ##Open the device
        if LUN!="": self.open(LUN)

    def __del__(self):
        self.close()

    def open(self, LUN):
        '''Open the device and map to the FPGA bus
        '''

        status=self.lib.eb_socket_open(EB_ABI_CODE, 0, self.addr_width|self.data_width, self.getPtrData(self.socket))
        if status: raise NameError('failed to open Etherbone socket: %s\n' % (self.eb_status(status)));

        if self.verbose: print "Connecting to '%s' with %d retry attempts...\n" % (LUN, self.attempts);
        status=self.lib.eb_device_open(self.socket, LUN, self.EB_ADDRX|self.EB_DATAX, self.attempts, self.getPtrData(self.device))
        if status: raise NameError("failed to open Etherbone device: %s\n" % (self.eb_status(status)));


    def close(self):
        '''Close the device and unmap
        '''
        status=self.lib.eb_device_close(self.device)
        if status: raise NameError("Close device: %s\n" % (self.eb_status(status)));
        self.device=c_uint(0)

        status=self.lib.eb_socket_close(self.socket)
        if status: raise NameError("Close socket: %s\n" % (self.eb_status(status)));
        self.socket=c_uint(0)


    def devread(self, bar, offset, width):
        '''Method that do a cycle read on the devices using ed_device_read()

        Convenience methods which create single-operation cycles and it is
        equivalent to: eb_cycle_open, eb_cycle_read, eb_cycle_close.


        Args:
            bar : BAR used by PCIe bus (Not used)
            offset : address within bar
            width : data size (1, 2, or 4 bytes) => Must be 4 bytes
        '''
        address = offset

        INTP = POINTER(c_uint32)
        data = c_uint32(0xBADC0FFE)
        pData = cast(addressof(data), INTP)

        user_data=c_uint32(0)
        cb=c_uint(0)


        status=self.lib.eb_device_read(self.device,c_uint(address),self.format,pData,user_data,cb)
        if self.verbose: print "R@x%08X > 0x%08x" %(address, pData[0])
        if status: raise NameError('Bad Etherbone Read: %s' % (self.eb_status(status)))
        return pData[0]


    def devwrite(self, bar, offset, width, datum):
        ''' Method that do a cycle write on the devices using ed_device_write()

        Convenience methods which create single-operation cycles and it is
        equivalent to: eb_cycle_open, eb_cycle_write, eb_cycle_close.

        Args:
            bar : BAR used by PCIe bus (Not used)
            offset : address within bar
            width : data size (1, 2, or 4 bytes) => Must be 4 bytes
            datum : data value that need to be written
        '''
        address = offset
        data = c_uint32(datum)

        user_data=c_uint32(0)
        cb=c_uint(0)

        if self.verbose: print "W@x%08X < 0x%08x" %( address, datum)
        status=self.lib.eb_device_write(self.device,c_uint(address),self.format,data,user_data,cb)
        if status: raise NameError('Bad Wishbone Write @0x%08x > 0x%08x : %s' % (address, datum, self.eb_status(status)))
        return data


    def devblockread(self, bar, offset, bsize, incr=0x4):
        '''
        Abstract method that do a read on the devices
            bar : BAR used by PCIe bus (Not used)
            offset : address within bar
            bsize : size in bytes

            @return The array with the data
        '''
        cycle       = c_uint(0)
        user_data   = c_uint32(0xDEADBEEF)
        CBFUNC = CFUNCTYPE(None, c_void_p, c_void_p, c_void_p,c_int)
        cb          = CBFUNC(py_cb_func)

        INTP = POINTER(c_uint32)
        data = c_uint32(0xBADC0FFE)
        pData = cast(addressof(data), INTP)
        pUData = cast(addressof(user_data), INTP)

        print "%s %x %x %x" % (pData,addressof(data),addressof(cb),addressof(user_data))

        ldata=[]
        actsize=bsize
        addr=offset
        status= self.lib.eb_cycle_open(self.device,pUData,cb,self.getPtrData(cycle))
        if status: raise NameError('Cycle open : 0x%x, %s' % (offset,self.eb_status(status)))
        while actsize>0:
            self.lib.eb_cycle_read(cycle,addr,self.format,pData)
            if self.verbose: print "@x%x < %x %s" % (addr, pData[0], pUData[0])
            break
            ldata.append(pData[0])
            addr=addr+incr
            actsize=actsize-4
        status=self.lib.eb_cycle_close(cycle)
        if status: raise NameError('Cycle close: %s' % (self.eb_status(status)))


        return 0;

    def devblockwrite(self, bar, offset, ldata, incr=0x4):
        '''
        Abstract method that do a read on the devices
            bar : BAR used by PCIe bus (Not used)
            offset : address within bar
            ldata : data structure in words
        '''

        cycle       = c_uint(0)
        user_data   = c_uint32(0)
        cb          = 0 #NULL pointer


        addr=offset
        status= self.lib.eb_cycle_open(self.device,user_data,cb,self.getPtrData(cycle))
        if status: raise NameError('Cycle open : 0x%x, %s' % (offset,self.eb_status(status)))
        for data in ldata:
            ##Chequear endianess de format
            if self.verbose: print "@x%x > %x" % (addr, data)
            self.lib.eb_cycle_write(cycle,addr,self.format,c_uint32(data))
            self.wcrc=binascii.crc32(c_uint32(data), self.wcrc)
            addr=addr+incr
        if self.silent:
            status=self.lib.eb_cycle_close_silently(cycle) #Close without asking acknowledgment of the device (faster)
        else:
            status=self.lib.eb_cycle_close(cycle)
        if status: raise NameError('Cycle close: %s' % (self.eb_status(status)))


        return 0;



    def eb_status(self,status):
        ''' Print the status code returned by libetherbone'''

        if status==0: return "OK"

        statab={}
        statab[1]=("EB_FAIL","system failure")
        statab[2]=("EB_ADDRESS","invalid address")
        statab[3]=("EB_WIDTH","impossible bus width")
        statab[4]=("EB_OVERFLOW","cycle length overflow")
        statab[5]=("EB_ENDIAN","remote endian required")
        statab[6]=("EB_BUSY","resource busy ")
        statab[7]=("EB_TIMEOUT","timeout")
        statab[8]=("EB_OOM","out of memory")
        statab[9]=("EB_ABI","library incompatible with application")
        statab[10]=("EB_SEGFAULT","one or more operations failed")

        if status<0 and status>-11:
            desc=statab[-status];
            return "%d=>%s (%s) " %(status,desc[0],desc[1])

        return "%d=>Unknown" %(status)

    def info(self):
        """get a string describing the interface the driver is bound to """
        return "Etherbone library (%s v%d): %s" % (self.libname,EB_PROTOCOL_VERSION,self.LUN)


    def test_rw(self,EP_offset=0x30100):
        '''
        Method to test read/write WB cycle using endpoint

        Args:
            EP_offset=The offset of the endpoint
        '''
        REG_MACL=0x28
        REG_ID=0x34

        bus=self

        ##Check the CafeBabe ID
        id=(bus.read(EP_offset | REG_ID))
        print "0x%X" % id
        if id != 0xcafebabe: raise("Error reading ID")
        else: print "OK"

        ## Toogle the lowest 16bit of MAC address.
        macaddr=EP_offset | REG_MACL
        oldmac=(bus.read(macaddr))
        newmac= (oldmac & 0xFFFF0000) | (~oldmac & 0xFFFF)
        print "old=0x%X > new=0x%X" % (oldmac,newmac)
        bus.write(macaddr,newmac)
        rbmac= bus.read(macaddr)
        print "0x%X" % rbmac
        if newmac!=rbmac:  raise("Error writing new MAC")
        else: print "OK"
        bus.write(macaddr,oldmac)
        rbmac=(bus.read(macaddr))
        if oldmac!=rbmac: raise("Error writing old MAC")
        else: print "OK"





    def dataToByteArray(self,data_list,bytearray_list):
        """Method for turning the Data lines strings into byte arrays
        """

        for i in range(0, len(data_list)):
            hex_line=data_list[i].decode("hex")
            hex_array=bytearray(hex_line)
            bytearray_list.append(hex_array)

        return bytearray_list




    def wordsToPackets(self,data_words,data_packets,packetLen=128):
        """Method for packing a list of words into a list of packets, each packet of length packetLen
        """
        # the 4 bytes words are grouped in "packetLen" words packets
        for i in range(0,len(data_words),packetLen):
            if i<(len(data_words)-len(data_words)%packetLen):
                tmpPacket=[]
                for k in range(0,packetLen):
                    tmpPacket.append(data_words[i+k])
                #tmpPacket.append(0xa0b1c2d4)
                data_packets.append(tmpPacket)
            else:
                last_packet=[]
                for l in range(0,len(data_words)%packetLen):
                    last_packet.append(data_words[i+l])
                data_packets.append(last_packet)
        return data_packets



    def test_rwblock(self,RAM_offset=0x0):

        print "test R/W block"
        dataw=[]
        for i in range (0,32):
            dataw.append(i<<24 | i << 16 | i << 8 | i)

        self.devblockwrite(0, RAM_offset, dataw,4)
        self.read(RAM_offset)
        self.read(RAM_offset+16*4)
        self.read(RAM_offset+32*4)

        datar=self.devblockread(0, RAM_offset, len(dataw)*4,4)

        return 0
        print datar
        if datar != dataw:
            for i in range(0,len(dataw)):
                print "%3d x%08x " % (i,dataw[i])