#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
#Copyright 2011 Shannon Black
#
#Authors:
#    Andreas Happe <andreashappe@snikt.net>
#    Shannon A Black <shannon@netforge.co.za>
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

import helpers
import unitylauncher
import indicate
import gobject
import gtk
import Skype4Py
import shared
import settings

import os
import sys
import commands
import time
import dbus

from PIL import Image
import StringIO
import binascii

import threading

bus = dbus.SessionBus()

def do_nothing(indicator):
    True
    
    
AppletRunning = True
    
CB_INTERVALS = 500

FOCUSDEBUG = 4
ERROR = 3
WARNING = 2
INFO = 1

LOGTYPES = {
    0:"",
    1:"INFO: ",
    2:"WARNING: ",
    3:"ERROR: ",
    4:"DEVELOPER DEBUG: ",
}

STATUSLIST = {
    1: "Offline",
    2: "Online",
    3: "Away",
    4: "Extended_Away",
    5: "Invisible",
    6: "Busy"
}

SKYPESTATUS = {
    1: Skype4Py.cusOffline,
    2: Skype4Py.cusOnline,
    3: Skype4Py.cusAway,
    4: Skype4Py.cusNotAvailable,
    5: Skype4Py.cusInvisible,
    6: Skype4Py.cusDoNotDisturb,
}

SKYPETOTELEPATHY = {
    Skype4Py.cusOffline:1,
    Skype4Py.cusOnline:2,
    Skype4Py.cusAway:3,
    Skype4Py.cusNotAvailable:4,
    Skype4Py.cusInvisible:5,
    Skype4Py.cusDoNotDisturb:6,
    Skype4Py.cusLoggedOut:1,
    Skype4Py.cusSkypeMe:3,
}

DONOTDISTURB = False

# only display errors
LOGLEVEL = WARNING
LOGFILE = os.getenv("HOME")+"/.skype-wrapper/log.txt"

def createLogFile(retry=None):
    try :
        if not os.path.isfile(LOGFILE):
            f = open(LOGFILE, mode="w")
            f.write("python-skype: "+helpers.version("python-skype")+"\n")
            f.write("python-imaging: "+helpers.version("python-imaging")+"\n")
            f.close()
    except IOError:
        if retry:
            pass
        else:
            os.mkdir(os.getenv("HOME")+"/.skype-wrapper")
            createLogFile(1)

createLogFile()

def log(message, level):
    if level >= LOGLEVEL:
        if settings.get_debug_log():
            f = open(LOGFILE, mode="a")
            f.write(LOGTYPES[level] + message + "\n")
            f.close()
        print LOGTYPES[level] + message

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
    log("Display skype chat and remove missed chat from indicator", INFO)
    
    id = indicator.get_property("id")

    self.skype.remove_conversation(int(id))
    self.skype.show_chat_windows(int(id))
    
    self.reset_indicators()
    
  def show_conversation_quicklist(self, widget, data = None):
    log("Quicklist showing conversation", INFO)
    id = widget.property_get("id")

    self.skype.remove_conversation(int(id))
    self.skype.show_chat_windows(int(id))
    
    self.reset_indicators()
            
  def reset_indicators(self) :
    del self.indicators
    self.indicators = {}
    for _id in self.skype.unread_conversations:
        self.show_indicator(self.skype.unread_conversations[int(_id)])
    unitylauncher.count(len(self.indicators) + self.skype.incomingfilecount)
    unitylauncher.createUnreadMessageQuickList(self.skype.unread_conversations, self.show_conversation_quicklist)
    unitylauncher.redrawQuicklist()  
    unitylauncher.count(len(self.indicators) + self.skype.incomingfilecount)

  def show_indicator(self, conversation):
    log("Updating Indicator", INFO)
    new = False
    if not conversation.indicator_name in self.indicators:
        self.indicators[conversation.indicator_name] = indicate.Indicator()
        self.indicators[conversation.indicator_name].set_property_bool("draw-attention", True)    
        self.indicators[conversation.indicator_name].set_property("id", str(conversation.id))
        self.indicators[conversation.indicator_name].set_property("indicator_name", str(conversation.indicator_name))
        self.indicators[conversation.indicator_name].connect("user-display", self.show_conversation)
        new = True
    self.indicators[conversation.indicator_name].set_property("name", str(conversation.display_name))    
    self.indicators[conversation.indicator_name].set_property("timestamp", str(conversation.timestamp))
    self.indicators[conversation.indicator_name].set_property_time('time', conversation.timestamp)
    
    # check if the settings want avatars
    user_avatar = None
    if settings.get_display_indicator_avatars():
        user_avatar = SkypeAvatar(conversation.skypereturn.Sender.Handle)
    if user_avatar and user_avatar.filename:
        bitmapVersion = user_avatar.get_bitmap_version()
        if bitmapVersion != self.indicators[conversation.indicator_name].get_property("icon"):
            self.indicators[conversation.indicator_name].set_property("icon", str(user_avatar.get_bitmap_version()))
    else:
        self.indicators[conversation.indicator_name].set_property("icon", "")
        
    if new:
        self.indicators[conversation.indicator_name].show()
    
    
  def user_online_status(self, username, fullname, online_text):
    log("User "+username+" "+online_text, INFO)
    if not settings.get_notify_on_useronlinestatuschange() or self.skype.skype_presence == Skype4Py.cusDoNotDisturb or username == 'echo123':
        return
        
    icon = ""
    if settings.get_display_notification_avatars():
        avatar = SkypeAvatar(username)
        if avatar.filename:
            icon = '-i "'+avatar.filename+'" '
        else:
            icon = '-i "/usr/share/skype-wrapper/icons/skype-wrapper-48.svg" '
    
    if not fullname:
        fullname = username
        
    os.system('notify-send '+icon+'"'+fullname+'" "'+online_text+'"');
  
  def new_message(self, conversation):
    if not settings.get_notify_on_messagerecieve() or self.skype.skype_presence == Skype4Py.cusDoNotDisturb:
        return
    #conversation.skypereturn.Chat.Type == Skype4Py.chatTypeMultiChat and  
    if conversation.skypereturn.Chat.Topic:
        group_chat_title = unicode(conversation.skypereturn.Sender.FullName + " ► " + conversation.skypereturn.Chat.Topic)
    else:
        group_chat_title = unicode(conversation.display_name)
        
    icon = ""
    if settings.get_display_notification_avatars():
        avatar = SkypeAvatar(conversation.skypereturn.Sender.Handle)
        if avatar.filename:
            icon = '-i "'+avatar.filename+'" '
        else:
            icon = '-i "/usr/share/skype-wrapper/icons/skype-wrapper-48.svg" '
    fullname = conversation.skypereturn.Sender.FullName
    
    if not fullname:
        fullname = username
    
    #doesn't work
    unitylauncher.urgent(True)
    
    os.system(u'notify-send '+icon+'"'+group_chat_title+'" "'+conversation.skypereturn.Body+'"');
    
  def file_transfer_event(self, transfer, text):
    if self.skype.skype_presence == Skype4Py.cusDoNotDisturb:
        return
        
    if str(transfer.status) == 'INCOMING' and not settings.get_notify_on_incoming_filetransfer():
        return
        
    if str(transfer.status) == 'OUTGOING' and not settings.get_notify_on_outgoing_filetransfer():
        return
        
    icon = ""
    if settings.get_display_notification_avatars():
        avatar = SkypeAvatar(transfer.partner_username)
        if avatar.filename:
            icon = '-i "'+avatar.filename+'" '
        else:
            icon = '-i "/usr/share/skype-wrapper/icons/skype-wrapper-48.svg" '
            
    os.system(u'notify-send --urgency critical '+icon+'"File Transfer" "'+text+'"')

# class for retrieving user avatars
class SkypeAvatar:
  def __init__(self, username):
    userfiles = {
        "user256", 
        "user1024", 
        "user4096", 
        "user16384", 
        "user32768", 
        "user65536",
        "profile256", 
        "profile1024", 
        "profile4096", 
        "profile16384", 
        "profile32768"
    }
    
    self.path = os.getenv("HOME")+"/.thumbnails/normal/"
    skypedir = os.getenv("HOME")+"/.Skype/"+skype.skype.CurrentUser.Handle+"/"
    
    self.image_data = ""
    self.filename = ""
    
    skbin = []
    n = 0
    for f in userfiles:
        fil = "%s%s.dbb" % (skypedir, f)
        try: skbin.append(file(fil, "rb").read())
        except: pass
        n = n + 1
        
    binary = "".join(skbin)
    self.get_icon(username, binary)
    if len(self.image_data) :
        f = open(self.path+"skype-wrapper-"+username+".jpg", mode="w")
        f.write(self.image_data)
        f.close()
        self.filename = self.path+"skype-wrapper-"+username+".jpg"
        log("Wrote avatar to file "+self.filename, INFO)
        
    self.imagepath = self.path+"skype-wrapper-"+username
    return
    
  def get_bitmap_version(self):
    if not self.filename:
        return ""
    im = Image.open(self.filename)
    s = StringIO.StringIO()
    im.save(s, "BMP")
    f = open(self.imagepath+".bmp", mode="w")
    f.write(s.getvalue())
    f.close()
    return binascii.b2a_base64(s.getvalue())#self.imagepath+".bmp"
    
  def get_icon(self, buddy, binary):
    startmark = "\xff\xd8"
    endmark = "\xff\xd9"

    startfix = 0
    endfix = 2

    nick_start = "\x03\x10%s" % buddy
    nick_end = "\x6C\x33\x33\x6C"

    nickstart = binary.find(bytes(nick_start))
    if nickstart == -1: return -1
    log("Found avatar for "+buddy, INFO)
    
    nickend = binary.find(nick_end, nickstart)
    handle = binary[nickstart+2:nickend]
    blockstart = binary.rfind("l33l", 0, nickend)
    imgstart = binary.find(startmark, blockstart, nickend)
    imgend = binary.find(endmark, imgstart)

    imgstart += startfix
    imgend += endfix

    if (imgstart < startfix): 
        return None
        
    self.image_data = binary[imgstart:imgend]
    return True
    

class Conversation:
  def __init__(self, display_name, timestamp, skype_id, mesg):
    self.id = mesg.Id
    self.display_name = display_name
    self.skypereturn = mesg
    self.count = 0
    self.timestamps = [timestamp]
    self.timestamp=timestamp
    self.indicator_name = mesg.Chat.Name
    self.Read = False
    
    
  def add_timestamp(self, timestamp):
    self.timestamps.append(timestamp)
    self.count += 1
    
class FileTransfer:
  def __init__(self, skype_transfer):
  
    # all the notifications that have been sent
    self.notifications = {}
    self.update(skype_transfer)
    
  def update(self, skype_transfer):
    self.Id = skype_transfer.Id
    self.display_name = skype_transfer.FileName
    self.skype_transfer = skype_transfer
    self.type = skype_transfer.Type
    self.status = skype_transfer.Status
    self.partner = skype_transfer.PartnerDisplayName
    self.partner_username = skype_transfer.PartnerHandle

def isSkypeRunning():
    output = commands.getoutput('ps -A | grep skype' )
    output = output.replace('skype-wrapper', '')
    return 'skype' in output.replace('indicator-skype', '')

class SkypeBehaviour:
  # initialize skype
  def __init__(self):
    log("Initializing Skype API", INFO)
    self.skype = Skype4Py.Skype()
    self.skype.Timeout = 500
    
    if not isSkypeRunning() and settings.get_start_skype_cmd_params():
        os.system("skype "+settings.get_start_skype_cmd_params())
    else:
        self.skype.Client.Start(Minimized=True)

    log("Waiting for Skype Process", INFO)
    while True:
      output = commands.getoutput('ps -A | grep skype' )
      if 'skype' in output.replace('skype-wrapper', ''):
        break

    log("Attaching skype-wrapper to Skype process", INFO)
    while True:
        time.sleep(4)
        try:
            self.skype.Attach(Wait=True)
            break
        except:
            # we tell the parent process that the skype couldn't attached
            sys.exit(2) 
                        
    log("Attached complete", INFO)
    time.sleep(2)
    self.skype.Client.Minimize()
    self.name_mappings = {}
    self.unread_conversations = {}
    
    # we will store all outdated messages here, anything not here will get net notified
    self.conversations = {}
    
    # store all the users online for notifying if they're on
    self.usersonline = {}
    
    # stor all file transfers
    self.filetransfers = {}
    self.incomingfilecount = 0
    
    self.cb_show_conversation = None
    self.cb_show_indicator = None
    self.cb_user_status_change = None
    self.cb_log_message = None
    self.cb_read_within_skype = None
    self.cb_log_transfer = None
    
    self.telepathy_presence = self.getPresence()
    if self.telepathy_presence:
        self.skype.ChangeUserStatus(SKYPESTATUS[self.telepathy_presence])
    self.skype_presence = self.skype.CurrentUserStatus
    
    if not settings.get_notify_on_initializing():
        self.initOnlineUserList()
    gobject.timeout_add(CB_INTERVALS, self.checkUnreadMessages)
    gobject.timeout_add(CB_INTERVALS, self.checkOnlineUsers)
    gobject.timeout_add(CB_INTERVALS, self.checkOnlineStatus)
    gobject.timeout_add(CB_INTERVALS, self.checkFileTransfers)

  def SetShowConversationCallback(self, func):
    self.cb_show_conversation = func

  def SetShowIndicatorCallback(self, func):
    self.cb_show_indicator = func
    
  def SetUserOnlineStatusChangeCallback(self, func):
    self.cb_user_status_change = func
    
  def SetNewMessageCallback(self, func):
    self.cb_log_message = func
    
  def SetFileTransferCallback(self, func):
    self.cb_log_transfer = func
    
  def SetSkypeReadCallback(self, func):
    self.cb_read_within_skype = func

  def remove_conversation(self, id):
    #skype_name = self.name_mappings[display_name]
    #self.unread_conversations[display_name].skypereturn.Seen = True
    #del self.unread_conversations[id]
    try :
        display_name = self.unread_conversations[int(id)].display_name
        for _id in self.unread_conversations:
            if display_name == self.unread_conversations[int(_id)].display_name:
                self.unread_conversations[int(_id)].Read = True
        self.unread_conversations[int(id)].Read = True
    except:
        # tried to access a non existent conversation
        pass
    return
   
  def logMessage(self, conversation):
    if not conversation:
        return
    id = conversation.id
    if not id in self.conversations:
        log("Logging Message", INFO)
        self.conversations[id] = conversation
        if self.cb_log_message:
            self.cb_log_message(conversation)
    return
   
  def initOnlineUserList(self) :
    if self.skype.Friends:
        for friend in self.skype.Friends:
            if not friend.Handle in self.usersonline:
                if friend.OnlineStatus != "OFFLINE":
                    self.usersonline[friend.Handle] = friend.FullName
    return
  
  def checkFileTransfers(self) :
    try : 
        log("Checking file transfers", INFO)
        for transfer in self.skype.ActiveFileTransfers:
            if not transfer.Id in self.filetransfers:
                self.filetransfers[transfer.Id] = FileTransfer(transfer)
        
        for transfer in self.skype.FileTransfers:
            if transfer.Id in self.filetransfers:
                self.filetransfers[transfer.Id].update(transfer)
             
        oldincoming = self.incomingfilecount
        self.incomingfilecount = 0
        self.filetransfer = {
            "total" : -1,
            "current" : 0    
        }
        # should we send out notifications
        for k in self.filetransfers:
            v = self.filetransfers[k]
            if str(v.type) == "INCOMING":
                if "NEW" in str(v.status):
                    self.incomingfilecount = self.incomingfilecount + 1
                    unitylauncher.urgent(True)
                else:
                    unitylauncher.urgent(False)
                
                if settings.get_show_incoming_filetransfer_progress():
                    if "TRANSFERRING" in str(v.status) or "PAUSED" in str(v.status):
                        self.filetransfer['total'] = self.filetransfer['total'] + v.skype_transfer.FileSize
                        self.filetransfer['current'] = self.filetransfer['current'] + v.skype_transfer.BytesTransferred
                        self.incomingfilecount = self.incomingfilecount + 1
                
                    
                if not str(v.status) in v.notifications:
                    if "NEW" in v.status:
                        self.filetransfers[k].notifications[str(v.status)] = str(v.status)
                        if self.cb_log_transfer:
                            self.cb_log_transfer(v, "* " + v.partner+ " wants to send you a file")
                    if "TRANSFERRING" in v.status:
                        self.filetransfers[k].notifications[str(v.status)] = str(v.status)
                        if self.cb_log_transfer:
                            self.cb_log_transfer(v, "* " + v.partner+ " is busy sending you a file")
                    if "CANCELLED" in v.status:
                        self.filetransfers[k].notifications[str(v.status)] = str(v.status)
                        if self.cb_log_transfer:
                            self.cb_log_transfer(v, "* file transfer with " + v.partner+ " has been cancelled")
                    if "COMPLETED" in v.status:
                        self.filetransfers[k].notifications[str(v.status)] = str(v.status)
                        if self.cb_log_transfer:
                            self.cb_log_transfer(v, "* " + v.partner+ " finished sending you a file")
                        unitylauncher.urgent(True)
                    if "FAILED" in v.status:
                        self.filetransfers[k].notifications[str(v.status)] = str(v.status)
                        if self.cb_log_transfer:
                            self.cb_log_transfer(v, "* " + v.partner+ " failed to send you a file")
                else:
                    if "COMPLETED" in v.status:
                        unitylauncher.urgent(False)
                        
            if str(v.type) == "OUTGOING":                
                if settings.get_show_outgoing_filetransfer_progress():
                    if "TRANSFERRING" in str(v.status) or "PAUSED" in str(v.status) or "REMOTELY_PAUSED" in str(v.status):
                        self.filetransfer['total'] = self.filetransfer['total'] + v.skype_transfer.FileSize
                        self.filetransfer['current'] = self.filetransfer['current'] + v.skype_transfer.BytesTransferred
                        self.incomingfilecount = self.incomingfilecount + 1
                        
                if not str(v.status) in v.notifications:
                    if "TRANSFERRING" in v.status:
                        self.filetransfers[k].notifications[str(v.status)] = str(v.status)
                        if self.cb_log_transfer:
                            self.cb_log_transfer(v, "* " + v.partner+ " is busy receiving your file")
                    if "CANCELLED" in v.status:
                        self.filetransfers[k].notifications[str(v.status)] = str(v.status)
                        if self.cb_log_transfer:
                            self.cb_log_transfer(v, "* file transfer with " + v.partner+ " has been cancelled")
                    if "COMPLETED" in v.status:
                        self.filetransfers[k].notifications[str(v.status)] = str(v.status)
                        if self.cb_log_transfer:
                            self.cb_log_transfer(v, "* " + v.partner+ " has received your file")                        
                    if "FAILED" in v.status:
                        self.filetransfers[k].notifications[str(v.status)] = str(v.status)
                        if self.cb_log_transfer:
                            self.cb_log_transfer(v, "* " + v.partner+ " failed to receive your file")
               
        if self.filetransfer['total'] > -1:
            currentprogress = float(self.filetransfer['current']) / float(self.filetransfer['total'])
            unitylauncher.progress(currentprogress)
        else:
            unitylauncher.progress(-1)
            
        if oldincoming != self.incomingfilecount and self.cb_read_within_skype:
            self.cb_read_within_skype()  
    except Exception, e:
        log("Checking file transfers failed ("+str(e)+")", WARNING)
        raise
    return AppletRunning
   
  def checkOnlineUsers(self) :
    try :
        log("Checking online status changing users", INFO)
        #check who is now offline
        tmp = self.usersonline
        for friend, v in tmp.items():
            for skypefriends in self.skype.Friends:
                if skypefriends.OnlineStatus == "OFFLINE" and friend == skypefriends.Handle:
                    del self.usersonline[skypefriends.Handle]
                    if not helpers.isUserBlacklisted(friend.Handle) and self.cb_user_status_change:
                            self.cb_user_status_change(skypefriends.Handle, skypefriends.FullName, "went offline")
        
        #check who is now online
        if self.skype.Friends:
            for friend in self.skype.Friends:
                if not friend.Handle in self.usersonline:
                    if friend.OnlineStatus != "OFFLINE":
                        self.usersonline[friend.Handle] = friend
                        if not helpers.isUserBlacklisted(friend.Handle) and self.cb_user_status_change:
                            self.cb_user_status_change(friend.Handle, friend.FullName, "is online")
        
    except:
        log("Checking online status changing users failed", WARNING)
    return AppletRunning
  
  def checkUnreadMessages(self):
    try :
        log("Checking unread messages", INFO)
        missedmessages = []
        if self.skype.MissedMessages:
            for mesg in self.skype.MissedMessages:
                missedmessages.append(mesg)
                
        unread = self.unread_conversations
        self.unread_conversations = {}
        if missedmessages and self.cb_show_indicator:
            for mesg in reversed(missedmessages):
                try:
                    id = mesg.Id
                    display_name = mesg.Chat.FriendlyName
                except:
                    log("Couldn't get missed message Chat object", ERROR)
                    continue
                if not id in self.unread_conversations:
                    conversation = Conversation(display_name, mesg.Timestamp, mesg.Sender.Handle, mesg)
                    self.name_mappings[id] = mesg.Sender.Handle
                    self.unread_conversations[id] = conversation
                else:
                    self.unread_conversations[id].add_timestamp(mesg.Timestamp)
                
                if helpers.isUserBlacklisted(mesg.Sender.Handle):
                    self.unread_conversations[id].Read = True
                    
                if not self.unread_conversations[id].Read:
                    self.logMessage(self.unread_conversations[id])
                    self.cb_show_indicator(self.unread_conversations[id]) 
        if len(unread) != len(self.unread_conversations) and self.cb_read_within_skype:
            self.cb_read_within_skype()
            unitylauncher.urgent(True)
            unitylauncher.urgent(False)
    except Exception, e:
        log("Checking unread messages failed: "+str(e), WARNING)
    return AppletRunning
  
  def checkOnlineStatus(self):
    try :
        log("Checking online presence", INFO)
        
        new_telepathy_presence = self.getPresence()
        if new_telepathy_presence and new_telepathy_presence != self.telepathy_presence:
            self.telepathy_presence = new_telepathy_presence
            self.skype.ChangeUserStatus(SKYPESTATUS[self.telepathy_presence])
            self.skype_presence = SKYPESTATUS[self.telepathy_presence]
            return AppletRunning
            
        new_skype_presence = self.skype.CurrentUserStatus
        if self.skype_presence != new_skype_presence:
            self.skype_presence = new_skype_presence
            new_telepathy_presence = SKYPETOTELEPATHY[self.skype_presence]
            self.setPresence(new_telepathy_presence)
            self.telepathy_presence = new_telepathy_presence
    except:
        log("Checking online presence failed", WARNING)
    return AppletRunning

  def show_chat_windows(self, id):
    try :
        self.unread_conversations[id].skypereturn.Chat.OpenWindow()
    except Exception, e:
        log("Couldn't open chat window ("+str(e)+")", WARNING)
    
  def setPresence(self, presence):
    if not helpers.isInstalled('telepathy-mission-control-5'):
        return
        
    account_manager = bus.get_object('org.freedesktop.Telepathy.AccountManager',
                         '/org/freedesktop/Telepathy/AccountManager')
    accounts = account_manager.Get(
        'org.freedesktop.Telepathy.AccountManager', 'ValidAccounts')

    for account_path in accounts:
        if str(account_path) == '/org/freedesktop/Telepathy/Account/ring/tel/ring':
            continue
        account = bus.get_object('org.freedesktop.Telepathy.AccountManager', account_path)
        enabled = account.Get('org.freedesktop.Telepathy.Account', 'Enabled')
        if not enabled:
            continue
        presence_text = ""
        if presence in STATUSLIST:
            presence_text = STATUSLIST[presence]
        account.Set('org.freedesktop.Telepathy.Account', 'RequestedPresence', \
            dbus.Struct((dbus.UInt32(presence), presence_text, ''), signature='uss'),
            dbus_interface='org.freedesktop.DBus.Properties')
  
  def getPresence(self) :
    if not helpers.isInstalled('telepathy-mission-control-5'):
        return None
        
    account_manager = bus.get_object('org.freedesktop.Telepathy.AccountManager',
                         '/org/freedesktop/Telepathy/AccountManager')
    accounts = account_manager.Get(
        'org.freedesktop.Telepathy.AccountManager', 'ValidAccounts')

    for account_path in accounts:
        if str(account_path) == '/org/freedesktop/Telepathy/Account/ring/tel/ring':
            continue
        account = bus.get_object('org.freedesktop.Telepathy.AccountManager', account_path)
        enabled = account.Get('org.freedesktop.Telepathy.Account', 'Enabled')
        if not enabled:
            continue
        i,s,t = account.Get('org.freedesktop.Telepathy.Account', 'RequestedPresence')
        return i
    return None

def runCheck():
    try :
        log("Check if Skype instance is running", INFO)
        #print self.skype.Client.IsRunning
        #calling self.skype.Client.IsRunning crashes. wtf. begin hack:
        output = commands.getoutput('ps -A | grep skype' )
        output = output.replace('skype-wrapper','')
        output = output.replace('indicator-skype','')
        
        if 'skype' not in output.replace('skype-wrapper',''):
            log("Skype instance has terminated, exiting", WARNING)
            gtk.main_quit()
        if 'defunct' in output:
            log("Skype instance is now defunct, exiting badly", ERROR)
            gtk.main_quit()
    except:
        log("Checking if skype is running failed", WARNING)
        
    return AppletRunning

if __name__ == "__main__":
  shared.set_proc_name('indicator-skype')
  os.chdir('/usr/share/skype-wrapper')
  
  skype = SkypeBehaviour();
  server = NotificationServer()
  gobject.timeout_add(CB_INTERVALS, runCheck)
  
  skype.SetShowConversationCallback(server.show_conversation)
  skype.SetShowIndicatorCallback(server.show_indicator)
  skype.SetUserOnlineStatusChangeCallback(server.user_online_status)
  skype.SetNewMessageCallback(server.new_message)
  skype.SetFileTransferCallback(server.file_transfer_event)
  skype.SetSkypeReadCallback(server.reset_indicators)
  
  server.connect(skype)
  
  #workaround_show_skype()

  # why is this needed?
  #server.activate_timeout_check()

  # check for newly unread messages..
  #skype.check_timeout(server)
  gtk.main()
  AppletRunning = False
