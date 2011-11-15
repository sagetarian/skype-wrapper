#!/usr/bin/env python
# -*- coding: latin-1 -*-
#

from gi.repository import Unity, Gio, Dbusmenu
import time

# Pretend to be evolution for the sake of the example 
launcher = Unity.LauncherEntry.get_for_desktop_id ("skype-wrapper.desktop")

def count(count) :
    if count:
        launcher.set_property("count", count)
        launcher.set_property("count_visible", True)
    else :
        launcher.set_property("count_visible", False)

def progress(progress):
    if progress >= 0:
        # Set progress to 42% done 
        launcher.set_property("progress", progress)
        launcher.set_property("progress_visible", True)
    else :
        launcher.set_property("progress_visible", False)

def urgent(urgent) :
    launcher.set_property("urgent", urgent)
    
# keep around for future reference
def createQuickList():
    ql = Dbusmenu.Menuitem.new ()
    item = Dbusmenu.Menuitem.new ()
    item.property_set (Dbusmenu.MENUITEM_PROP_LABEL, str("test"))
    #item.property_set ("id", str(2))
    item.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
    ql.child_append (item)
    launcher.set_property("quicklist", ql)
    
unread_quicklist = {}

def createUnreadMessageQuickList(unread_conversations, cb_unread_message_click):
    global unread_quicklist
    unread_quicklist = {}
    for _id in unread_conversations:
        conversation = unread_conversations[int(_id)]
        if conversation.indicator_name in unread_quicklist:
            continue
        item = Dbusmenu.Menuitem.new ()
        item.property_set (Dbusmenu.MENUITEM_PROP_LABEL, str(conversation.display_name))
        item.property_set ("id", str(conversation.id))
        item.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
        if cb_unread_message_click:
            item.connect ("item-activated", cb_unread_message_click)
        unread_quicklist[conversation.indicator_name] = item
    
def createCallQuicklist(call) :
    #
    return
    
#createQuickList()

def redrawQuicklist() :
    global unread_quicklist
    ql = Dbusmenu.Menuitem.new ()
    if len(unread_quicklist):
        for cql in unread_quicklist:
            ql.child_append (unread_quicklist[cql])
    launcher.set_property("quicklist", ql)
    
import atexit

@atexit.register
def clearQuicklist() :
    ql = Dbusmenu.Menuitem.new ()
    launcher.set_property("quicklist", ql)
    
