#!   /usr/bin/env   python
# -*- coding: utf-8 -*
'''
Custom exceptions

@file
@date Created on Jul 20, 2015
@author Benoit Rat (benoit<AT>sevensols.com)
@copyright LGPL v2.1
@see http://www.ohwr.org/projects/fpga-config-space/wiki
@see http://www.sevensols.com
@ingroup core
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

class p7sException(Exception) :
    # definir los códigos de error

class Retry(p7sException) :
    '''
    This exception indicates to caller that the operation failed and it should be retried.
    '''
    pass

class BadData(p7sException) :
    '''
    Exception used to indicate that any of the passed parameters are invalid.
    '''
class Error(p7sException) :
    '''
    Exception used for critical errors that should stop the execution of the caller.
    '''
