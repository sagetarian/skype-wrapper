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

import commands
import time
import settings
import shared
import pynotify
import wnck

PyNotify = True
if not pynotify.init("Skype Wrapper"):
    PyNotify = False

installed_packages = {}

def isSkypeWrapperDesktopOnUnityLauncher():
    return "skype-wrapper.desktop" in commands.getoutput("gsettings get com.canonical.Unity.Launcher favorites")

def isInstalled(package_name):
    global installed_packages
    if package_name in installed_packages:
        return installed_packages[package_name]
    shortened = package_name
    if len(package_name) > 5:
        shortened = package_name[0:5]
        
    installed_packages[package_name] = len(commands.getoutput("dpkg -l "+package_name+" | grep \"ii  "+package_name+"\"")) > 0
    return installed_packages[package_name]
    
def haveUnity():
    return isInstalled('unity') or isInstalled('unity-2d')
    
def version(package_name):
    if not isInstalled(package_name):
        return "not installed"
    description = commands.getoutput("dpkg -l "+package_name+" | grep \"ii  "+package_name+"\"")
    clip = description[description.find(" "):].strip()
    clip = clip[clip.find(" "):].strip()
    clip = clip[:clip.find(" ")].strip()
    return clip
    
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

pynotifications = {}

def notify(title, body, icon, uid, critical, replace, chattopic = None):
    if PyNotify:
        global pynotifications
        n = None
        tmp = None
        
        # check if this guy is after someone else in a chat room / i.e break messages in a chatroom up by replicant
        while True:
            if chattopic and uid in pynotifications and "chat://"+chattopic in pynotifications and not pynotifications["chat://"+chattopic] == uid:
                uid = uid+"/"
            else:
                break
        
        if uid and uid in pynotifications:
            tmp = pynotifications[uid]
            # check time lapse
            n = tmp['n']
            now = time.time()
            time_lapse = now - tmp['start']
            if replace or time_lapse > 10:
                body = body
            else:
                body = tmp['body'] + "\n" + body
            n.update(title, body, icon)
            n.set_timeout(pynotify.EXPIRES_DEFAULT)
        else:
            n = pynotify.Notification(title, body, icon)
            if uid:
                pynotifications[uid] = {}
                pynotifications[uid]['n'] = n
        if critical:
            n.set_urgency(pynotify.URGENCY_CRITICAL)
        n.show()
        if uid:
            pynotifications[uid]['body'] = body
            pynotifications[uid]['start'] = time.time()
            if chattopic:
                pynotifications["chat://"+chattopic] = uid
            
    else:
        if icon:
            icon = '-i "'+icon+'" '
        os.system('notify-send '+icon+'"'+fullname+'" "'+online_text+'"');
        
def isAuthorizationRequestOpen():
    """Used to determine if the authorization dialog is still open. Fixes the multiple authorization requests."""
    wnck.screen_get_default().force_update()
    window_list = wnck.screen_get_default().get_windows()
    if len(window_list) == 0:
    	return False
    for win in window_list:
        if "Skype API Authorisation Request" in win.get_name():
            return True
    return False    

