#!/usr/bin/env python

import subprocess
import time
import os
import commands
import dbus
import sys
	
def skypeRunning():
    output = commands.getoutput('ps -A | grep skype' )
    output = output.replace('skype-wrapper','')
    output = output.replace('indicator-skype','')
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

    output = commands.getoutput('ps -A | grep indicator-skype' )
    
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
