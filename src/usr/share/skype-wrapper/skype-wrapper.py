#!/usr/bin/env python

import subprocess
import time
import os
	
def start_skype():
	start = time.time()
	ret = subprocess.call(['python','indicator-applet-skype.py'])
	end = time.time()
	print "Applet closed"
	if end - start < 5:
		print "API crash detected"
		print "Restarting skype-wrapper"
		start_skype()
	return


if __name__ == "__main__":
	os.chdir('/usr/share/skype-wrapper')
	print "Starting skype-wrapper"
	start_skype()
