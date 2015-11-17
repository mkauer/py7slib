#!   /usr/bin/env   python
#    coding: utf8
'''
Tool for opening an interactive shell through virtual UART.

@file
@author Felipe Torres González<ftorres@sevensols.com>
@date November 17, 2015
@copyright LGPL v2.1
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

# Imports
import argparse as arg
import sys

sys.path.append('../../')

from py7slib.tools.vuart-shell.vuart import *

def main():
    '''
    Tool for opening an interactive shell through virtual UART.
    '''

    parser = arg.ArgumentParser(description='VUART shell for WR-LEN')

    parser.add_argument('ip', metavar='IP', type=str, nargs='1', help='IP of the device')
    parser.add_argument('--input','-i',help='Execute an input script of WRPC commands', \
    required=True)

    args = parser.parse_args()
