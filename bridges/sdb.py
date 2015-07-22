#!   /usr/bin/env   python
# -*- coding: utf-8 -*
'''
Create all the structures to parse the Self-Describe-Bus format

This file is based on the official version 1.1 of sdb.h 

@file
@date Created on Jul 20, 2015
@author Benoit Rat (benoit<AT>sevensols.com)
@copyright LGPL v2.1
@see http://www.ohwr.org/projects/fpga-config-space/wiki
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

#---------------------------------------------------------- --------------------
#                                   Import                                    --
#-------------------------------------------------------------------------------

# Import system modules
import os
from ctypes import *

# Define specific for SDB Flags
SDB_MAGIC                   = 0x5344422d
SDB_WB_WIDTH_MASK           = 0x0f
SDB_WB_ACCESS8              = 0x01
SDB_WB_ACCESS16             = 0x02
SDB_WB_ACCESS32             = 0x04
SDB_WB_ACCESS64             = 0x08
SDB_WB_LITTLE_ENDIAN        = 0x80
SDB_DATA_READ               = 0x04
SDB_DATA_WRITE              = 0x02
SDB_DATA_EXEC               = 0x01

class sdb_product(Structure):
    """
    product information: 40 bytes, 8-byte alignment
    """
    _fields_ = [
        ("vendor_id",  c_uint64),
        ("device_id", c_uint32),
        ("version",  c_uint32),
        ("date", c_uint32),
        ("name", (c_char * 19)),
        ("record_type", c_uint8),
    ]

class sdb_component(Structure):
    """
    component information: address + product information
    """
    _fields_ = [
        ("addr_first",  c_uint64),
        ("addr_end", c_uint64),
        ("product",  sdb_product),
    ]

class sdb_empty(Structure):
    """
    empty component information: 64bit
    """
    _fields_ = [
        ("reserved",  c_int8 * 63),
        ("record_type", c_uint8),
    ]

class sdb_interconnect(Structure):
    """
    sdb_interconnect
    This header prefixes every SDB table.
    It's component describes the interconnect root complex/bus/crossbar.
    """
    _fields_ = [
        ("sdb_magic",  c_uint32),  ##0x5344422D
        ("sdb_records", c_uint16), ##Length of the SDB table (including header)
        ("sdb_version", c_uint8),  
        ("sdb_bus_type", c_uint8),
        ("sdb_component", sdb_component),
    ]


class sdb_integration(Structure):
    """
    This meta-data record describes the aggregate product of the bus.
    For example, consider a manufacturer which takes components from 
    various vendors and combines them with a standard bus interconnect.
    The integration component describes aggregate product.
    """
    _fields_ = [
        ("reserved",  c_int8 * 24),  ##0x5344422D
        ("sdb_product", sdb_product),
    ]

class sdb_device(Structure):
    """
    This component record describes a device on the bus.
    
    abi_class describes the published standard register interface, if any.
    """
    _fields_ = [
        ("abi_class",  c_uint16),  # 0 = custom device
        ("abi_ver_major", c_uint8),
        ("abi_ver_minor", c_uint8),
        ("bus_specific", c_uint32),  
        ("sdb_component", sdb_component),
    ]


class sdb_bridge(Structure):
    """
    This component describes a bridge which embeds a nested bus.
    
    This does NOT include bus controllers, which are *devices* that
    indirectly control a nested bus.
    """
    _fields_ = [
        ("sdb_child",  c_uint64),  #Nested SDB table
        ("sdb_component", sdb_component),
    ]
    
class sdb_repo_url(Structure):
    """
     Top module repository url
    
    An informative field that software can ignore.
    """
    _fields_ = [
        ("repo_url",  c_char * 63),
        ("record_type", c_uint8),
    ]

class sdb_synthesis(Structure):
    """
     Top module repository url
    
    An informative field that software can ignore.
    """
    _fields_ = [
        ("syn_name",  c_char * 16),
        ("commit_id", c_char * 16),
        ("tool_name", c_char * 8),
        ("tool_version", c_uint32),
        ("date", c_uint32),
        ("user_name", c_char * 15),
        ("record_type", c_uint8),
    ]


class sdb_record(Union):
    """
    Generic sdb record with all possible SDB structure.
    """
    _fields_ = [
        ("empty",       sdb_empty),
        ("device",      sdb_device),
        ("bridge",      sdb_bridge),
        ("integration", sdb_integration),
        ("interconnect",sdb_interconnect),
    ]
    
    TYPE_INTERCONNECT = 0x00
    TYPE_DEVICE       = 0x01
    TYPE_BRIDGE       = 0x02
    TYPE_INTEGRATION  = 0x80
    TYPE_REPO_URL     = 0x81
    TYPE_SYNTHESIS    = 0x82
    TYPE_EMPTY        = 0xFF
    
    FLAG_BUS_WISHBONE = 0x00
    FLAG_BUS_DATA     = 0x01
    
    def __str__(self):
        if self.empty.record_type==self.TYPE_INTERCONNECT:
            return self.interconnect.__str()__
        elif self.empty.record_type==self.TYPE_DEVICE:
            return self.device.__str()__
        elif self.empty.record_type==self.TYPE_BRIDGE:
            return self.bridge.__str()__
        elif self.empty.record_type==self.TYPE_INTEGRATION:
            return self.integration.__str()__
        else:
            return self.empty.__str()__


class sdb_table(Structure):
    """
    Complete bus description.
    """
    _fields_ = [
        ("interconnect",  sdb_interconnect),
        ("record", sdb_record * 1), # bus.sdb_records-1 elements (not 1)
    ]


