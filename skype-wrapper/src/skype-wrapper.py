#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; mode: python -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: t -*-
# vi: set ft=python sts=4 ts=4 sw=4 noet 
#
# Copyright 2011 Shannon Black
#
# Authors:
#    Shannon A Black <shannon@netforge.co.za>
#
# This program is free software: you can redistribute it and/or modify it 
# under the terms of either or both of the following licenses:
#
# 1) the GNU Lesser General Public License version 3, as published by the 
# Free Software Foundation; and/or
# 2) the GNU Lesser General Public License version 2.1, as published by 
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the applicable version of the GNU Lesser General Public 
# License for more details.
#
# You should have received a copy of both the GNU Lesser General Public 
# License version 3 and version 2.1 along with this program.  If not, see 
# <http://www.gnu.org/licenses/>
#

import subprocess
import time
import os
import commands
import dbus
import sys
	
def skypeRunning():
    USER = commands.getoutput('whoami')
    output = commands.getoutput('pgrep -x -l skype -u $USER')
    return 'skype' in output
	
skype_was_running = False
	
def start_skype():
    global skype_was_running
    
    # some one quit skype while it was still unattached
    if skype_was_running and not skypeRunning():
        return
    
    skype_was_running = skypeRunning()
    
    start = time.time()
    ret = subprocess.call(['python','indicator-applet-skype.py'])
    if ret == 2:
        start_skype()
        return
    end = time.time()
    print "Applet closed"
    if end - start < 5:
        print "API crash detected"
        print "Restarting skype-wrapper"
        start_skype()
    return


if __name__ == "__main__":
    os.chdir('/usr/share/skype-wrapper')
	
    USER = commands.getoutput('whoami')
    output = commands.getoutput('pgrep -x -l indicator-skype -u $USER')
    
    # until the dbus is working just disallow skype-wrapper
    if 'indicator-skype' in output:
        try:
	        # Try and set skype window to normal
            remote_bus = dbus.SessionBus()
            out_connection = remote_bus.get_object('com.Skype.API', '/com/Skype')
            out_connection.Invoke('NAME Skype4Py')
            out_connection.Invoke('PROTOCOL 5')
            #out_connection.Invoke('SET WINDOWSTATE MAXIMIZED')
            out_connection.Invoke('SET WINDOWSTATE NORMAL')
            out_connection.Invoke('FOCUS')
            sys.exit(0)
        except:
            sys.exit(0)

    print "Starting skype-wrapper"
    start_skype()
