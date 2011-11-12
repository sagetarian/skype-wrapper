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
