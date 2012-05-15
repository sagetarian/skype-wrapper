#!/usr/bin/env python
# -*- coding: latin-1 -*-
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
