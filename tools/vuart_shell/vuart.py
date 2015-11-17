#!   /usr/bin/env   python
#    coding: utf8
'''
Class that provides an interactive shell for the VUART_bridge driver.

@file
@author Felipe Torres González<ftorres@sevensols.com>
@author Fran Romero
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
from py7slib.bridges.ethbone import EthBone

class VUART_shell():
    '''
    This class provides an interactive shell to handle the VUART_bridge driver.

    It adds an abstraction layer over the VUART driver in order to show the user
    an interface like when connected through serial connection. It provides
    an interactive shell with a prompt where the user could insert the WRPC commands.

    Interactive commands (such as gui or stat cont) keeps the "ESC" key to stop
    the data output from the device. The shell can be closed using the key
    combination "ctrl-q".
    '''

    def __init__(self, ip):
        '''
        Constructor

        Args:
            ip (str) : IP direction for the device
        '''
        pass

    def run(self):
        '''
        Open the interactive shell
        '''
        print("TEST: running interactive mode")

    def run_script(self, script):
        '''
        Execute a bunch of WRPC commands.

        Args:
            script (file) : An instance of an opened file
        '''
        print("TEST: running script mode")
