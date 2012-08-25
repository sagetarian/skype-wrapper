#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; mode: python -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: t -*-
# vi: set ft=python sts=4 ts=4 sw=4 noet
#
# Copyright 2012 Shannon Black
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
import subprocess

BASE_KEY = "apps.skype-wrapper"
setting = Gio.Settings.new(BASE_KEY)

class DialogAdvanced(Gtk.Dialog):
				
		def __init__(self, parent):		
				Gtk.Dialog.__init__(self, "Remove sni-qt", parent, 0,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OK, Gtk.ResponseType.OK))

        		self.set_default_size(300, 100)

        		label = Gtk.Label("This will remove sni-qt. The Skype-Icon will not be shown in the panel any longer. This may also affects other applications. To revert the change reinstall sni-qt in the software-center")
				label.set_line_wrap(True)
        		box = self.get_content_area()
       			box.add(label)
       			self.show_all()

class uisettings(Gtk.Window):
        def switch(self, table, label, option):
                self.row += 1
                gtk_label = Gtk.Label ( label )
                gtk_label.set_alignment(0.0,0.5)

                table.attach ( gtk_label, 0, 3, self.row, self.row+1, xpadding=10, ypadding = 2 )
                gtk_switch = Gtk.Switch()
                table.attach ( gtk_switch, 3, 4, self.row, self.row+1, xpadding=10, ypadding = 2 )
                setting.bind( option, gtk_switch, "active", Gio.SettingsBindFlags.DEFAULT )

        def __init__(self):
                Gtk.Window.__init__(self, title="Skype Wrapper Options")
                table = Gtk.Table(2, 4, True)
                table.set_row_spacings(5)
                table.set_col_spacings(1)
                self.row = -1
        		self.add(table)
        		
        		
                self.switch( table, "Notify when someone goes on or offline", "notify-on-useronlinestatuschange")
                self.switch( table, "Notify when you recieve a message","notify-on-messagerecieve")
                self.switch( table, "Notify about all online contacts during startup", "notify-on-initializing")
                self.switch( table, "Display avatars next to indicator message", "display-indicator-avatars")
                self.switch( table, "Display avatars in the notifications", "display-notification-avatars")
                self.switch( table, "Notify on incoming File Transfer", "notify-on-incoming-filetransfer" )
                self.switch( table, "Notify on outgoing File Transfer", "notify-on-outgoing-filetransfer" )
                self.switch( table, "Show outgoing File Transfer progress in the Launcher", "show-outgoing-file-progress" )
                self.switch( table, "Show incoming File Transfer progress in the Launcher", "show-incoming-file-progress" )
                self.switch( table, "Use the global online status of the system", "use-global-status" )
                self.switch( table, "Toggle music playback before and after a call", "control-music-player" )
                self.switch( table, "Restore the volume to the level prior the call", "restore-volume" )

                gtk_btn_adv = Gtk.Button("Remove the panel icon")
                gtk_btn = Gtk.Button("Close")
                gtk_btn.connect("clicked", Gtk.main_quit)
                gtk_btn_adv.connect("clicked", self.on_advanced_clicked)

                self.row += 1
                table.attach ( gtk_btn, 3, 4, self.row, self.row+1,xpadding=10, ypadding = 2 )
                table.attach ( gtk_btn_adv, 0, 2, self.row, self.row+1,xpadding=10, ypadding = 2 )



		def on_advanced_clicked(self, widget):
        		dialog = DialogAdvanced(self)
        		response = dialog.run()

        		if response == Gtk.ResponseType.OK:
           			subprocess.call(['gksudo','python /usr/share/skype-wrapper/uninstallsni.py'])

           			           			
        		elif response == Gtk.ResponseType.CANCEL:
            		print "The Cancel button was clicked"

        		dialog.destroy()


win = uisettings()
win.set_border_width(10)
win.connect("delete-event", Gtk.main_quit)
win.connect("destroy", Gtk.main_quit)
win.show_all()

Gtk.main()


