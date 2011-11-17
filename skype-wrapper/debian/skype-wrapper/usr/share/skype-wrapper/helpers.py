#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
#Copyright 2011 Shannon Black
#
#Authors:
#    Shannon A Black <shannon@netforge.co.za>
#
#This program is free software: you can redistribute it and/or modify it 
#under the terms of either or both of the following licenses:
#
#1) the GNU Lesser General Public License version 3, as published by the 
#Free Software Foundation; and/or
#2) the GNU Lesser General Public License version 2.1, as published by 
#the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the applicable version of the GNU Lesser General Public 
#License for more details.
#
#You should have received a copy of both the GNU Lesser General Public 
#License version 3 and version 2.1 along with this program.  If not, see 
#<http://www.gnu.org/licenses/>
#



import commands
import time
import settings
import shared

def isInstalled(package_name):
    return not "not installed" in commands.getoutput("dpkg -s "+package_name)
    
def version(package_name):
    if not isInstalled(package_name):
        return "not installed"
    return commands.getoutput("dpkg -s "+package_name+" | grep Version:").replace("Version: ","")
    
def isChatBlacklisted(chat) :
    # doesnt work
    return len(chat.AlertString) > 0
    
def isUserBlacklisted(username) :
    return "'"+username+"'" in settings.get_list_of_silence()

class CPULimiter:
    def __init__(self, process):
        shared.set_proc_name('indicator-skype')
        self.process = process
        pidsearch = commands.getoutput("ps -A | grep "+self.process).strip()
        self.pid = None
        if " " in pidsearch:
            d = pidsearch.split(" ") 
            self.pid = d[0]
        
    def getCPUUsage(self):
        if not self.pid:
            raise Exception("No PID to check cpu usage for")
        desc, perc = commands.getoutput("ps -p "+self.pid+" -o %cpu").split("\n")
        self.percentage = float(perc.strip())
        return self.percentage
        
    def limit(self, percentage, Try = 2):
        while True:
            curr_percentage = self.getCPUUsage()
            if curr_percentage > percentage:
                time.sleep(0.5)
            else:
                break;


cpulimiter = CPULimiter("indicator-skype")
#skypelimitwatcher = CPULimiter("skype")

