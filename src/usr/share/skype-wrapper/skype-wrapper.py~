#!/usr/bin/env python

import subprocess
import time
import os
	
def start_skype():
	start = time.time()
	print "Starting Skype"
	ret = subprocess.call(['python','indicator-applet-skype.py'])
	end = time.time()
	print "applet closed"
	if end - start < 5:
		print "API crash detected"
		start_skype()
	return


if __name__ == "__main__":
	os.chdir('/usr/share/skype-wrapper')
	start_skype()
