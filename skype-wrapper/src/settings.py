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

from gi.repository import Gio

BASE_KEY = "apps.skype-wrapper"
settings = Gio.Settings.new(BASE_KEY)

def get_notify_on_useronlinestatuschange():
    return settings.get_boolean("notify-on-useronlinestatuschange")
        
def get_notify_on_messagerecieve():
    return settings.get_boolean("notify-on-messagerecieve")
        
def get_notify_on_initializing():
    return settings.get_boolean("notify-on-initializing")
    
def get_display_indicator_avatars():
    return settings.get_boolean("display-indicator-avatars")
    
def get_display_notification_avatars():
    return settings.get_boolean("display-notification-avatars")
    
def get_notify_on_incoming_filetransfer():
    return settings.get_boolean("notify-on-incoming-filetransfer")
    
def get_notify_on_outgoing_filetransfer():
    return settings.get_boolean("notify-on-outgoing-filetransfer")

def get_show_outgoing_filetransfer_progress():
    return settings.get_boolean("show-outgoing-file-progress")
    
def get_show_incoming_filetransfer_progress():
    return settings.get_boolean("show-incoming-file-progress")

def get_start_skype_cmd_params():
    return settings.get_string("start-skype-cmd-params")
    
def get_list_of_silence():
    return settings.get_string("list-of-silence")
    
def get_debug_log():
    return settings.get_boolean("debug-log")
    
def get_debug_level():
    return settings.get_int("debug-level")
    
def get_cpu_limit():
    return float(settings.get_string("cpu-percentage-limit"))
    
def get_use_global_status():
    return settings.get_boolean("use-global-status")