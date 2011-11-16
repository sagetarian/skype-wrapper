#!/usr/bin/env python
# -*- coding: latin-1 -*-
#

from gi.repository import Unity, Gio, Dbusmenu
import time

    
import atexit

class SkypeWrapperLauncher:
  # initialize skype
  def __init__(self):
    self.launcher = Unity.LauncherEntry.get_for_desktop_id ("skype-wrapper.desktop")
    self.unread_quicklist = {}
    self.quicklist = self.launcher.get_property("quicklist")
    self.clear(True)
  
  def __del__(self):    
    self.clear()
    
  def clear(self, New = False):
    if self.quicklist:
        for child in self.quicklist.get_children():
            self.quicklist.child_delete(child)
    else:
        if New and not self.quicklist:
            self.quicklist = Dbusmenu.Menuitem.new ()
            self.launcher.set_property("quicklist", self.quicklist)
    
  def count(self, count) :
    if count:
        self.launcher.set_property("count", count)
        self.launcher.set_property("count_visible", True)
    else :
        self.launcher.set_property("count_visible", False)
  
  def progress(self, progress):
    if progress >= 0:
        self.launcher.set_property("progress", progress)
        self.launcher.set_property("progress_visible", True)
    else :
        self.launcher.set_property("progress_visible", False)
        
  def urgent(self, urgent = None) :
    if urgent == None:
        self.launcher.set_property("urgent", True)
        self.launcher.set_property("urgent", False)
    else:
        self.launcher.set_property("urgent", urgent)

  def createUnreadMessageQuickList(self, unread_conversations, cb_unread_message_click):
    global unread_quicklist
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
        
  def redrawQuicklist(self) :
    if not len(self.unread_quicklist):
        self.clear()
        return
    self.clear(True)
    if len(self.unread_quicklist):
        for cql in self.unread_quicklist:
            self.quicklist.child_append (self.unread_quicklist[cql])
            
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
    
def createCallQuicklist(call) :
    #
    return

def redrawQuicklist() :
    global launcher
    launcher.redrawQuicklist()

