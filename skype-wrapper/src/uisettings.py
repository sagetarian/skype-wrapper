#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; mode: python -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: t -*-
# vi: set ft=python sts=4 ts=4 sw=4 noet 
#
# Copyright 2011 Shannon Black
#
# Authors:
#    Christian Rupp <christian@r-k-r.de>
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

from gi.repository import Gtk, Gio
import settings
import changesettings
BASE_KEY = "apps.skype-wrapper"
setting = Gio.Settings.new(BASE_KEY)

class uisettings(Gtk.Window):
	
	def __init__(self):
		Gtk.Window.__init__(self, title="Settings")
		table = Gtk.Table(10, 5, True)
        self.add(table)
        
        #All of the labels is their a better way to code it?        	
		Lnouoc = Gtk.Label("Send notifications when someone goes on or offline")
		table.attach(Lnouoc, 0,4, 0, 1)
		Snouoc = Gtk.Switch()
		table.attach(Snouoc, 4,5, 0, 1)
		
		setting.bind("notify-on-useronlinestatuschange", Snouoc, "active", Gio.SettingsBindFlags.DEFAULT)
		
		Lnomr = Gtk.Label("Send notifications when you recieve a message")
		table.attach(Lnomr, 0, 4, 1, 2)
		Snomr = Gtk.Switch()
		table.attach(Snomr, 4,5, 1, 2)
		
		setting.bind("notify-on-messagerecieve", Snomr, "active", Gio.SettingsBindFlags.DEFAULT)
		
		Lnoi = Gtk.Label("Send on startup notifications about all online contacts")
		table.attach(Lnoi, 0, 4, 2, 3)
		Snoi = Gtk.Switch()
		table.attach(Snoi, 4,5, 2, 3)
		
		setting.bind("notify-on-initializing", Snoi, "active", Gio.SettingsBindFlags.DEFAULT)
		
		Ldia = Gtk.Label("Show avatars next to the indicator message")
		table.attach(Ldia, 0, 4, 3, 4)
		Sdia = Gtk.Switch()
		table.attach(Sdia, 4,5, 3, 4)
		
		setting.bind("display-indicator-avatars", Sdia, "active", Gio.SettingsBindFlags.DEFAULT)
		
		Ldna = Gtk.Label("Show avatars in the notifications")
		table.attach(Ldna, 0, 4, 4, 5)
		Sdna = Gtk.Switch()
		table.attach(Sdna, 4,5, 4, 5)
		
		setting.bind("display-notification-avatars", Sdna, "active", Gio.SettingsBindFlags.DEFAULT)
		
		Lnoift = Gtk.Label("Notify on incoming filetransfer")
		table.attach(Lnoift, 0, 4, 5, 6)
		Snoift = Gtk.Switch()
		table.attach(Snoift, 4,5, 5, 6)
		
		setting.bind("notify-on-incoming-filetransfer", Snoift, "active", Gio.SettingsBindFlags.DEFAULT)
		
		Lnooft = Gtk.Label("Notify on outgoing filetransfer")
		table.attach(Lnooft, 0, 4, 6, 7)
		Snooft = Gtk.Switch()
		table.attach(Snooft, 4,5, 6, 7)
		
		setting.bind("notify-on-outgoing-filetransfer", Snooft, "active", Gio.SettingsBindFlags.DEFAULT)
		
		Lsoofp = Gtk.Label("Show outgoing filetransfer-progress in the Launcher")
		table.attach(Lsoofp, 0, 4, 7, 8)
		Ssoofp = Gtk.Switch()
		table.attach(Ssoofp, 4,5, 7, 8)
		
		setting.bind("show-outgoing-file-progress", Ssoofp, "active", Gio.SettingsBindFlags.DEFAULT)
		
		Lsifp = Gtk.Label("Show incoming filetransfer-progress in the Launcher")
		table.attach(Lsifp, 0, 4, 8, 9)
		Ssifp = Gtk.Switch()
		table.attach(Ssifp, 4,5, 8, 9)
		
		setting.bind("show-incoming-file-progress", Ssifp, "active", Gio.SettingsBindFlags.DEFAULT)
		
		Lugs = Gtk.Label("Use the global online status of the system")
		table.attach(Lugs, 0, 4, 9, 10)
		Sugs = Gtk.Switch()
		table.attach(Sugs, 4,5, 9, 10)
				
		setting.bind("use-global-status", Sugs, "active", Gio.SettingsBindFlags.DEFAULT)
		
	def printit(self, blaa):
 		print(str(blaa))
 		
win = uisettings()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
