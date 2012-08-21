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

from gi.repository import Unity, Gio, Dbusmenu
import time
import helpers
    
import atexit

class SkypeWrapperLauncher:
  # initialize skype
  def __init__(self):
    self.launcher_desktop = None
    self.launcher_wrapper = Unity.LauncherEntry.get_for_desktop_id ("skype-wrapper.desktop")
    self.launcher_main = Unity.LauncherEntry.get_for_desktop_id ("skype.desktop")
    self.launcher = None
    self.reset_launcher()
    self.unread_quicklist = {}
    self.calls_quicklist = {}
    self.quicklist = self.launcher.get_property("quicklist")
    self.clear(True)
    self.SkypeAgent = None
  
  def __del__(self):    
    self.clear()
    
  def reset_launcher(self):
    old = self.launcher_desktop
    is_skype_wrapper = helpers.isSkypeWrapperDesktopOnUnityLauncher()
    
    if(is_skype_wrapper):
        self.launcher_desktop = "skype-wrapper.desktop"
        self.launcher = self.launcher_wrapper
    else:
        self.launcher_desktop = "skype.desktop"
        self.launcher = self.launcher_main
    if not old or old == self.launcher_desktop:
        return
    
    # this crashes unity
    if(is_skype_wrapper):
        old = self.launcher_main
    else:
        old = self.launcher_wrapper
        
    self.launcher.set_property("quicklist", self.quicklist)
    self.launcher.set_property("count", self.mcount)
    self.launcher.set_property("count_visible", self.mcount_visible)
    self.launcher.set_property("progress", self.mprogress)
    self.launcher.set_property("progress_visible", self.mprogress_visible)
    self.launcher.set_property("urgent", self.murgent)
         
    # removing quicklist causes a unity to crash
    #quicklist = Dbusmenu.Menuitem.new ()
    #old.set_property("quicklist", quicklist)
    old.set_property("count_visible", False)
    old.set_property("progress_visible", False)
    old.set_property("urgent", False)
    
  def clear(self, New = False):
    if self.quicklist:
        for child in self.quicklist.get_children():
            self.quicklist.child_delete(child)
    else:
        if New and not self.quicklist:
            self.quicklist = Dbusmenu.Menuitem.new ()
            self.launcher.set_property("quicklist", self.quicklist)
    
  def count(self, count) :
    self.reset_launcher()
    self.mcount = count
    if count:
        self.launcher.set_property("count", count)
        self.launcher.set_property("count_visible", True)
        self.mcount_visible = True
    else :
        self.launcher.set_property("count_visible", False)
        self.mcount_visible = False
  
  def progress(self, progress):
    self.reset_launcher()
    self.mprogress = progress
    if progress >= 0:
        self.launcher.set_property("progress", progress)
        self.launcher.set_property("progress_visible", True)
        self.mprogress_visible = True
    else :
        self.launcher.set_property("progress_visible", False)
        self.mprogress_visible = False
        
  def urgent(self, urgent = None) :
    self.reset_launcher()
    self.murgent = urgent
    if urgent == None:
        self.launcher.set_property("urgent", True)
        self.launcher.set_property("urgent", False)
    else:
        self.launcher.set_property("urgent", self.murgent)

  def createUnreadMessageQuickList(self, unread_conversations, cb_unread_message_click):
    global unread_quicklist
    self.reset_launcher()
    self.unread_quicklist = {}
    for _id in unread_conversations:
        conversation = unread_conversations[int(_id)]
        if conversation.indicator_name in unread_quicklist or conversation.Read:
            continue
            
        self.unread_quicklist[conversation.indicator_name] = Dbusmenu.Menuitem.new ()
        self.unread_quicklist[conversation.indicator_name].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str(conversation.display_name))
        self.unread_quicklist[conversation.indicator_name].property_set ("id", str(conversation.id))
        self.unread_quicklist[conversation.indicator_name].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
        if cb_unread_message_click:
            self.unread_quicklist[conversation.indicator_name].connect ("item-activated", cb_unread_message_click)
            
  def createCallsQuickList(self, calls, cb_call_action):
    self.reset_launcher()
    self.calls_quicklist = {}
    priority = 0
    for _id in calls:
        call = calls[_id]
            
        if call.Status == "MISSED" or call.Status == "FINISHED":
            continue
            
        partner = call.PartnerDisplayName or call.PartnerHandle
            
        if call.Status == 'RINGING':
            priority = priority + 1
            self.calls_quicklist[str(priority)+"answer://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"answer://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("Answer Call: "+partner))
            self.calls_quicklist[str(priority)+"answer://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"answer://"+call.PartnerHandle].property_set ("action", "ANSWER")
            self.calls_quicklist[str(priority)+"answer://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            if cb_call_action:
                self.calls_quicklist[str(priority)+"answer://"+call.PartnerHandle].connect ("item-activated", cb_call_action)
                
            priority = priority + 1
            self.calls_quicklist[str(priority)+"reject://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"reject://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("Reject Call: "+partner))
            self.calls_quicklist[str(priority)+"reject://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"reject://"+call.PartnerHandle].property_set ("action", "FINISH")
            self.calls_quicklist[str(priority)+"reject://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            if cb_call_action:
                self.calls_quicklist[str(priority)+"reject://"+call.PartnerHandle].connect ("item-activated", cb_call_action)
                
        if call.Status == 'LOCALHOLD' and self.skype.Mute == False:
            priority = priority + 1
            self.calls_quicklist[str(priority)+"mute://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"mute://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("Mute Call: "+partner))
            self.calls_quicklist[str(priority)+"mute://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"mute://"+call.PartnerHandle].property_set ("action", "MUTE")
            self.calls_quicklist[str(priority)+"mute://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            
            if cb_call_action:
                self.calls_quicklist[str(priority)+"mute://"+call.PartnerHandle].connect ("item-activated", cb_call_action)    
        
            priority = priority + 1
            self.calls_quicklist[str(priority)+"resume://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"resume://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("Resume Call: "+partner))
            self.calls_quicklist[str(priority)+"resume://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"resume://"+call.PartnerHandle].property_set ("action", "RESUME")
            self.calls_quicklist[str(priority)+"resume://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            if cb_call_action:
                self.calls_quicklist[str(priority)+"resume://"+call.PartnerHandle].connect ("item-activated", cb_call_action)
                
            priority = priority + 1
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("End Call: "+partner))
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set ("action", "FINISH")
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            if cb_call_action:
                self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].connect ("item-activated", cb_call_action)
 
        if call.Status == 'LOCALHOLD' and self.skype.Mute == True:
            priority = priority + 1
            self.calls_quicklist[str(priority)+"unmute://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"unmute://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("Unmute Call: "+partner))
            self.calls_quicklist[str(priority)+"unmute://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"unmute://"+call.PartnerHandle].property_set ("action", "UNMUTE")
            self.calls_quicklist[str(priority)+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            
            if cb_call_action:
                self.calls_quicklist[str(priority)+"unmute://"+call.PartnerHandle].connect ("item-activated", cb_call_action)                   
        
            priority = priority + 1
            self.calls_quicklist[str(priority)+"resume://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"resume://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("Resume Call: "+partner))
            self.calls_quicklist[str(priority)+"resume://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"resume://"+call.PartnerHandle].property_set ("action", "RESUME")
            self.calls_quicklist[str(priority)+"resume://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            if cb_call_action:
                self.calls_quicklist[str(priority)+"resume://"+call.PartnerHandle].connect ("item-activated", cb_call_action)
                
            priority = priority + 1
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("End Call: "+partner))
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set ("action", "FINISH")
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            if cb_call_action:
                self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].connect ("item-activated", cb_call_action)
                 
        if call.Status == 'REMOTEHOLD' or call.Status == 'ROUTING':                 
            priority = priority + 1
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("End Call: "+partner))
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set ("action", "FINISH")
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            if cb_call_action:
                self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].connect ("item-activated", cb_call_action)
                
        if call.Status == 'INPROGRESS' and self.skype.Mute == False:
            priority = priority + 1
            self.calls_quicklist[str(priority)+"mute://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"mute://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("Mute Call: "+partner))
            self.calls_quicklist[str(priority)+"mute://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"mute://"+call.PartnerHandle].property_set ("action", "MUTE")
            self.calls_quicklist[str(priority)+"mute://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            
            if cb_call_action:
                self.calls_quicklist[str(priority)+"mute://"+call.PartnerHandle].connect ("item-activated", cb_call_action)         
                    
            priority = priority + 1
            self.calls_quicklist[str(priority)+"hold://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"hold://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("Hold Call: "+partner))
            self.calls_quicklist[str(priority)+"hold://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"hold://"+call.PartnerHandle].property_set ("action", "HOLD")
            self.calls_quicklist[str(priority)+"hold://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            if cb_call_action:
                self.calls_quicklist[str(priority)+"hold://"+call.PartnerHandle].connect ("item-activated", cb_call_action)
                
            priority = priority + 1
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("End Call: "+partner))
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set ("action", "FINISH")
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            if cb_call_action:
                self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].connect ("item-activated", cb_call_action)
                
        if call.Status == 'INPROGRESS'  and self.skype.Mute == True:
            priority = priority + 1
            self.calls_quicklist[str(priority)+"unmute://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"unmute://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("Unmute Call: "+partner))
            self.calls_quicklist[str(priority)+"unmute://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"unmute://"+call.PartnerHandle].property_set ("action", "UNMUTE")
            self.calls_quicklist[str(priority)+"unmute://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            
            if cb_call_action:
                self.calls_quicklist[str(priority)+"unmute://"+call.PartnerHandle].connect ("item-activated", cb_call_action)           
            
            priority = priority + 1
            self.calls_quicklist[str(priority)+"hold://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"hold://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("Hold Call: "+partner))
            self.calls_quicklist[str(priority)+"hold://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"hold://"+call.PartnerHandle].property_set ("action", "HOLD")
            self.calls_quicklist[str(priority)+"hold://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            if cb_call_action:
                self.calls_quicklist[str(priority)+"hold://"+call.PartnerHandle].connect ("item-activated", cb_call_action)
                
            priority = priority + 1
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle] = Dbusmenu.Menuitem.new ()
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("End Call: "+partner))
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set ("id", str(call.PartnerHandle))
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set ("action", "FINISH")
            self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            if cb_call_action:
                self.calls_quicklist[str(priority)+"end://"+call.PartnerHandle].connect ("item-activated", cb_call_action)
            
  def redrawQuicklist(self) :
    self.reset_launcher()
    self.clear(True)        
    
    if len(self.calls_quicklist):
        for cql in sorted(self.calls_quicklist.iterkeys()):
            self.quicklist.child_append (self.calls_quicklist[cql])
    
    if len(self.unread_quicklist):
        for cql in self.unread_quicklist:
            self.quicklist.child_append (self.unread_quicklist[cql])
            
    if self.SkypeAgent:
        #self.toggle_skype = Dbusmenu.Menuitem.new ()
        #self.toggle_skype.property_set (Dbusmenu.MENUITEM_PROP_LABEL, "Hide / Show Skype")
        #self.toggle_skype.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
        #self.toggle_skype.connect ("item-activated", self.cb_toggle_window_state)
        #self.quicklist.child_append (self.toggle_skype)
        
        self.quit_skype = Dbusmenu.Menuitem.new ()
        self.quit_skype.property_set (Dbusmenu.MENUITEM_PROP_LABEL, "Add Contact")
        self.quit_skype.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
        self.quit_skype.connect ("item-activated", self.cb_add_contact)
        self.quicklist.child_append (self.quit_skype)
        
        # python skype crashes with these
        
        #self.quit_skype = Dbusmenu.Menuitem.new ()
        #self.quit_skype.property_set (Dbusmenu.MENUITEM_PROP_LABEL, "Options")
        #self.quit_skype.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
        #self.quit_skype.connect ("item-activated", self.cb_options)
        #self.quicklist.child_append (self.quit_skype)
        
        #self.quit_skype = Dbusmenu.Menuitem.new ()
        #self.quit_skype.property_set (Dbusmenu.MENUITEM_PROP_LABEL, "Profile")
        #self.quit_skype.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
        #self.quit_skype.connect ("item-activated", self.cb_profile)
        #self.quicklist.child_append (self.quit_skype)
    
        self.quit_skype = Dbusmenu.Menuitem.new ()
        self.quit_skype.property_set (Dbusmenu.MENUITEM_PROP_LABEL, "Quit Skype")
        self.quit_skype.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
        self.quit_skype.connect ("item-activated", self.cb_quit_skype)
        self.quicklist.child_append (self.quit_skype)
  
  def cb_add_contact(self, widget, data = None):
    self.SkypeAgent.OpenAddContactDialog()
    
  def cb_options(self, widget, data = None):
    self.SkypeAgent.OpenOptionsDialog()
    
  def cb_profile(self, widget, data = None):
    self.SkypeAgent.OpenProfileDialog()
  
  def cb_quit_skype(self, widget, data = None):
    self.SkypeAgent.Shutdown()
    self.redrawQuicklist()
  
  def cb_toggle_window_state(self, widget, data = None):
    if self.SkypeAgent.WindowState == "HIDDEN":
        self.SkypeAgent.Focus
    else:
        self.SkypeAgent.WindowState = "HIDDEN"
    self.redrawQuicklist()
            
launcher = SkypeWrapperLauncher()

def count(count) :
    global launcher
    launcher.count(count)

def progress(progress):
    global launcher
    launcher.progress(progress)

def urgent(urgent = None) :
    global launcher
    launcher.urgent(urgent)
    
unread_quicklist = {}

def createUnreadMessageQuickList(unread_conversations, cb_unread_message_click):
    global launcher
    launcher.createUnreadMessageQuickList(unread_conversations, cb_unread_message_click)
    
def createCallsQuickList(calls, cb_call_action):
    global launcher
    launcher.createCallsQuickList(calls, cb_call_action)
    
def createCallQuicklist(call) :
    #
    return

def redrawQuicklist() :
    global launcher
    launcher.redrawQuicklist()