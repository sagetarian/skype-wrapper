#!/usr/bin/env python
#
#Copyright 2010 Andreas Happe
#
#Authors:
#    Andreas Happe <andreashappe@snikt.net>
#
#This program is free software: you can redistribute it and/or modify it 
#under the terms of either or both of the following licenses:
#
#1) the GNU Lesser General Public License version 3, as published by the 
#Free Software Foundation; and/or
#2) the GNU Lesser General Public License version 2.1, as published by 
#the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the applicable version of the GNU Lesser General Public 
#License for more details.
#
#You should have received a copy of both the GNU Lesser General Public 
#License version 3 and version 2.1 along with this program.  If not, see 
#<http://www.gnu.org/licenses/>
#


# Documentation:
# just start it

import indicate
import gobject
import gtk
import Skype4Py

import os
import sys
import commands
import time
import dbus


import threading

def do_nothing(indicator):
    True

# this is the high-level notification functionality
class NotificationServer:
  def __init__(self):
    self.server = indicate.indicate_server_ref_default()
    self.server.set_type("message.im")
#   this is kinda ugly, or?
    self.server.set_desktop_file("/usr/share/applications/skype-wrapper.desktop")
    self.server.show()
    self.indicators = {}
    pass

  def connect(self, skype):
    self.skype = skype
    self.server.connect("server-display", self.on_click)

  def on_click(self, server,data=None):
    self.skype.skype.Client.Focus()

  def show_conversation(self, indicator, timestamp):
    display_name = indicator.get_property("name")

    del self.indicators[display_name]
    print "showing"
    # this might blow up.. don't know why, seems like an error within skype
    self.skype.show_chat_windows(display_name)
    self.skype.remove_conversation(display_name)

  def show_indicator(self, conversation):      
    print "adding " + str(conversation.timestamp)

    self.indicators[conversation.display_name] = indicate.Indicator()
    self.indicators[conversation.display_name].set_property("name", conversation.display_name)
    self.indicators[conversation.display_name].set_property_time('time', conversation.timestamp)
    self.indicators[conversation.display_name].show()
   
    self.indicators[conversation.display_name].connect("user-display", self.show_conversation)


class UnreadConversation:
  def __init__(self, display_name, timestamp, skype_id, mesg):
    self.display_name = display_name
    self.skypereturn = mesg
    self.count = 0
    self.timestamps = [timestamp]
    self.timestamp=timestamp
    
  def add_timestamp(self, timestamp):
    self.timestamps.append(timestamp)
    self.count += 1

class SkypeBehaviour:
  # initialize skype
  def __init__(self):
    print "entering init, defining skype"  
    self.skype = Skype4Py.Skype()
    self.skype.Client.Start(Minimized=True)

    print "waiting for skype"
    while True:
      output = commands.getoutput('ps -A | grep skype' )
      if 'skype' in output.replace('skype-wrapper', ''):
        break
      print "."

    print "attaching..."
    time.sleep(4)
    while True:
        try:
            self.skype.Attach(Wait=True)
            break
        except:
            print "."
                        
    print "attached. bam!"
    time.sleep(2)
    self.skype.Client.Minimize()
    print "set OnMessageStatus"
    self.skype.OnMessageStatus = self.OnMessageStatus
    self.name_mappings = {}
    self.unread_conversations = {}
    self.cb_show_conversation = None
    self.cb_show_indicator = None

  def SetShowConversationCallback(self, func):
    self.cb_show_conversation = func

  def SetShowIndicatorCallback(self, func):
    self.cb_show_indicator = func
    self.checkUnreadMessages()

  def OnMessageStatus(self, mesg, Status):
    print 'message status'
    if Status == 'RECEIVED':
      print(mesg.FromDisplayName + "sent a message")

      display_name = mesg.Chat.FriendlyName
      if not display_name in self.unread_conversations:
        conversation = UnreadConversation(display_name, mesg.Timestamp, mesg.Sender.Handle, mesg)
        self.name_mappings[display_name] = mesg.Sender.Handle
        # TODO: should we do some sort of update for this?
        self.unread_conversations[display_name] = conversation
      else:
        self.unread_conversations[display_name].add_timestamp(mesg.Timestamp)
        
      if conversation:
        self.cb_show_indicator(conversation)

  def remove_conversation(self, display_name):
    skype_name = self.name_mappings[display_name]
    #self.unread_conversations[display_name].skypereturn.Seen = True
    del self.unread_conversations[display_name]
    return skype_name
  
  def checkUnreadMessages(self):
    print "checking messages..."
    
    if not self.cb_show_indicator:
      return
    
    if self.skype.MissedMessages:
       for mesg in self.skype.MissedMessages:
         display_name = mesg.Chat.FriendlyName
      
         if not display_name in self.unread_conversations:
             conversation = UnreadConversation(display_name, mesg.Timestamp, mesg.Sender.Handle, mesg)
             self.name_mappings[display_name] = mesg.Sender.Handle
        # TODO: should we do some sort of update for this?
             self.unread_conversations[display_name] = conversation
         else:
             self.unread_conversations[display_name].add_timestamp(mesg.Timestamp)
         self.cb_show_indicator(self.unread_conversations[display_name])  
      
      
    threading.Timer(5, self.checkUnreadMessages).start()
    return  

  def show_chat_windows(self, display_name):
    self.unread_conversations[display_name].skypereturn.Chat.OpenWindow()

  

def runCheck():
    print "in runcheck"
    print "checking if running"
    #print self.skype.Client.IsRunning
    #calling self.skype.Client.IsRunning crashes. wtf. begin hack:
    output = commands.getoutput('ps -A | grep skype' )
    
    if 'skype' not in output.replace('skype-wrapper',''):
        print "not running"
        gtk.main_quit()
    if 'defunct' in output:
        print "ZOMBIES!!!"
        gtk.main_quit()
    print "running - restarting timer"
    threading.Timer(5, runCheck).start()

if __name__ == "__main__":

  os.chdir('/usr/share/skype-wrapper')
  
  skype = SkypeBehaviour();
  server = NotificationServer()
  runCheck()
  skype.SetShowConversationCallback(server.show_conversation)
  skype.SetShowIndicatorCallback(server.show_indicator)
  server.connect(skype)
  
  #workaround_show_skype()

  # why is this needed?
  #server.activate_timeout_check()

  # check for newly unread messages..
  #skype.check_timeout(server)
  gtk.main()
