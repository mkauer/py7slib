#!  /usr/bin/env python
#   :vi:ts=4 sw=4 et

from ctypes import *
import os, errno, re, sys, struct
import os.path

# python 2.4 kludge
if not 'SEEK_SET' in dir(os):
    os.SEEK_SET = 0

# unsigned formats to unpack words
fmt = { 1: 'B', 2: 'H', 4: 'I', 8: 'L' }

# some defaults from rawrabbit.h
RR_DEVSEL_UNUSED    = 0xffff
RR_DEFAULT_VENDOR     = 0x1a39
RR_DEFAULT_DEVICE     = 0x0004

RR_BAR_0      = 0x00000000

bar_map = {
    0 : RR_BAR_0,
}

# classes to interface with the driver via ctypes

Plist = c_int * 256

class BusException(Exception):
    pass

class BusWarning(Exception):
    pass

class RR_Devsel(Structure):
    _fields_ = [
        ("vendor",     c_ushort),
        ("device",     c_ushort),
        ("subvendor",     c_ushort),
        ("subdevice",     c_ushort),
        ("bus",     c_ushort),
        ("devfn",     c_ushort),
    ]

class RR_U(Union):
    _fields_ = [
        ("data8",     c_ubyte),
        ("data16",     c_ushort),
        ("data32",     c_uint),
        ("data64",     c_ulonglong),
    ]

class RR_Iocmd(Structure):
    _anonymous_ = [ "data", ]
    _fields_ = [
        ("address",    c_uint),
        ("datasize",    c_uint),
        ("data",     RR_U),
    ]

def set_ld_library_path():
    libpath = os.getenv('LD_LIBRARY_PATH')
    here = os.getcwd()
    libpath = here if not libpath else here + ':' + libpath
    os.environ['LD_LIBRARY_PATH'] = libpath

class X1052:
    libname = 'libx1052_api.so'

    def __init__(self, slot=0):
        """get a file descriptor for the Gennum device"""
        set_ld_library_path()
        print self.libname
        self.slot=slot
        self.lib = cdll.LoadLibrary(self.libname)
        self.errno=self.lib.X1052_LibInit()
        self.hdev = self.lib.X1052_DeviceOpen(self.slot)
        if self.hdev != 0:
            self.errno = -1

    def iread(self, bar, offset, width):
        """do a read by means of the ioctl interface

            bar = 0
            offset = address within bar
            width = data size (1, 2, or 4 bytes)
        """
        address = bar_map[bar] + offset
        INTP = POINTER(c_uint)
        data = c_uint(0xBADC0FFE)
        pData = cast(addressof(data), INTP)
        ret=self.lib.X1052_Wishbone_CSR(self.hdev,c_uint(address),pData,0)
        #print "R@x%08X > 0x%08x" %(address, pData[0])
        if ret !=0:
            raise NameError('Bad Wishbone Read @0x%08x > 0x%08x (ret=0x%X %s)' %(address,pData[0], ret,os.strerror(ret))) 
        return pData[0]

    def read(self, offset):
        """do a read by means of lseek+read

            bar = 0
            offset = address within bar
            width = data size (1, 2, or 4 bytes)
        """
        return self.iread(0, offset, 4)

    def iwrite(self, bar, offset, width, datum):
        """do a write by means of the ioctl interface

            bar = 0
            offset = address within bar
            width = data size (1, 2, 4 or 8 bytes)
            datum = value to be written
        """
        address = bar_map[bar] + offset
        INTP = POINTER(c_uint)
        data = c_uint(datum)
        pData = cast(addressof(data), INTP)
        #print "W@x%08X < 0x%08x" %( address, pData[0])
        ret=self.lib.X1052_Wishbone_CSR(self.hdev,c_uint(address),pData,1)
        if ret !=0:
            raise NameError('Bad Wishbone Write @0x%08x > 0x%08x (ret=0x%X %s)' %(address,datum, ret,os.strerror(ret))) 
        return pData[0]

    def write(self,  offset, datum):
        """do a write by means of lseek+write

            bar = 0
            offset = address within bar
            width = data size (1, 2, 4 or 8 bytes)
            datum = value to be written
        """
        return self.iwrite(0, offset, 4, datum)

    def irqwait(self):
        """wait for an interrupt"""
        raise NameError('Undef function') 
        return 0;

    def irqena(self):
        """enable the interrupt line"""
        raise NameError('Undef function') 
        return 0;

    def getdmasize(self):
        """return the size of the allocated DMA buffer (in bytes)"""
        raise NameError('Undef function') 
        return 0;

    def getplist(self):
        """get a list of pages for DMA access

        The addresses returned, shifted by 12 bits, give the physical
        addresses of the allocated pages
        """
        raise NameError('Undef function') 
        plist = Plist()
        self.lib.rr_getplist(self.fd, plist);
        return plist

    def info(self,flag='a'):
        """get a string describing the interface the driver is bound to
        """
        inf = (c_char*250)()
        self.lib.X1052_GetInfo(inf,c_char(flag))
        if flag=='a':
            return "X1052 library (%s): %s" % (self.libname,inf.value)
        else:
            return inf.value
        
    def parse_addr(self, addr):
        """take a string of the form
               vendor:device[/subvendor:subdevice][@bus:devfn]
        and return a dictionary object with the corresponding values,
        initialized to RR_DEVSEL_UNUSED when absent
        """
        # address format
        reg = ( r'(?i)^'
                r'(?P<vendor>[a-f0-9]{1,4}):(?P<device>[a-f0-9]{1,4})'
                r'(/(?P<subvendor>[a-f0-9]{1,4}):(?P<subdevice>[a-f0-9]{1,4}))?'
                r'(@(?P<bus>[a-f0-9]{1,4}):(?P<devfn>[a-f0-9]{1,4}))?$' )
        match = re.match(reg, addr).groupdict()
        if not 'sub' in match:
            match['subvendor'] = match['subdevice'] = RR_DEVSEL_UNUSED
        if not 'geo' in match:
            match['bus'] = match['devfn'] = RR_DEVSEL_UNUSED
        for k, v in match.items():
            if type(v) is str:
                match[k] = int(v, 16)
        return match

    def bind(self, device):
        """bind the rawrabbit driver to a device

        The device is specified with a syntax described in parse_addr
        """
        d = self.parse_addr(device)
        self.errno=0
        return self.errno

if __name__ == '__main__':
    g = X1052()
    print g.parse_addr('1a39:0004/1a39:0004@0020:0000')
    print g.bind('1a39:0004/1a39:0004@0020:0000')
    print g.getdmasize()
