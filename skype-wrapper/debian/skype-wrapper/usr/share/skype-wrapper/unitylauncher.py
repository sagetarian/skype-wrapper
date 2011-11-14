#!/usr/bin/env python
# -*- coding: latin-1 -*-
#

from gi.repository import Unity, Gio, Dbusmenu

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
    item1 = Dbusmenu.Menuitem.new ()
    item1.property_set (Dbusmenu.MENUITEM_PROP_LABEL, "Item 1")
    item1.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
    item2 = Dbusmenu.Menuitem.new ()
    item2.property_set (Dbusmenu.MENUITEM_PROP_LABEL, "Item 2")
    item2.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
    ql.child_append (item1)
    ql.child_append (item2)
    launcher.set_property("quicklist", ql)
