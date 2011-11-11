#!/usr/bin/python

import sys
import dbus

status_dict = {
    1: "Offline",
    2: "Online",
    3: "Away",
    4: "Extended_Away",
    5: "Invisible",
    6: "Busy"
}

status_dict_rev = {
    "off": 1,
    "offline": 1,
    "on": 2,
    "online": 2,
    "away": 3,
    "extended away": 4,
    "na": 4,
    "n/a": 4,
    "invisible": 5,
    "invis": 5,
    "busy": 6,
    "dnd": 6,
}

try:
    presence = sys.argv[1]
except IndexError:
    presence = None

if presence:
    try:
        presence_const = int(presence)
    except ValueError:
        try:
            presence_const = status_dict_rev[presence]
        except KeyError:
            sys.exit('Usage: %s off|on|away|na|invis|dnd')

    presence = status_dict[presence_const]

try:
    presence_text = sys.argv[2]
except IndexError:
    presence_text = ''

bus = dbus.SessionBus()
account_manager = bus.get_object('org.freedesktop.Telepathy.AccountManager',
                         '/org/freedesktop/Telepathy/AccountManager')
accounts = account_manager.Get(
        'org.freedesktop.Telepathy.AccountManager', 'ValidAccounts')

for account_path in accounts:
    if str(account_path) == '/org/freedesktop/Telepathy/Account/ring/tel/ring':
        continue
    account = bus.get_object('org.freedesktop.Telepathy.AccountManager',
            account_path)
    enabled = account.Get('org.freedesktop.Telepathy.Account', 'Enabled')
    if not enabled:
        continue
    if presence:
        account.Set('org.freedesktop.Telepathy.Account', 'RequestedPresence', \
           dbus.Struct((dbus.UInt32(presence_const), presence, presence_text),
                signature='uss'),
           dbus_interface='org.freedesktop.DBus.Properties')
    else:
        i,s,t = account.Get('org.freedesktop.Telepathy.Account', 'RequestedPresence')
        print s
