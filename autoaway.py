# This code is licensed under GPLv2 FSF Licence
# Please read the accompanied LICENSE file for more information
# Contact: mr.vaibhavjain at gmail.com 

__module_name__ = "autoaway" 
__module_version__ = "1.0" 
__module_description__ = "Python module for xchat that autometically marks your nick as 'nick_away' when you lock your desktop" 

import xchat
import time
import dbus
import re

# timer handle provided by xchat
timer_hook = None 

# gobject proxy to connect to the screensaver daemon
bus = dbus.SessionBus()
screensaver = bus.get_object('org.gnome.ScreenSaver', '/org/gnome/ScreenSaver')
proxy = dbus.Interface(screensaver, 'org.gnome.ScreenSaver')
isactive = 0
re_away = re.compile(r"(.*)_away")

# Called when the module is aboute to be unloaded
def unload_cb(userdata): 
    global timer_hook 
    if timer_hook is not None: 
        xchat.unhook(timer_hook) 
        timer_hook = None
        #force the nick as away
        update_away_nick()
        print "[autoaway] Module Unloads!"

# Called every few seconds to see if any dbus events are pending
def timeout_cb(userdata): 
    global proxy
    global isactive
    if proxy is None:
        return 0
    #print "tick ", proxy.GetActive()," ", isactive
    # check if the status has changed
    if proxy.GetActive() != isactive :
        #update the flag and take actions
        isactive = proxy.GetActive()
        if isactive == 0:
            update_backfromaway_nick()
        else:
            update_away_nick()
    return 1 # Keep the timeout going 

#sets the nick as nick_away
def update_away_nick():
    lst = xchat.get_list('channels')
    if lst is None:
        return
    #iterate over connected servers and update the nick
    for chnl in lst:
        if chnl.type == 1:
            nick = chnl.context.get_info('nick')
            match = re_away.match(nick)
            if match is None:
                newnick = nick + "_away"
                print "[autoaway] Updating nick on server %s to %s" % (chnl.context.get_info('server'), newnick)
                chnl.context.command("NICK "+newnick)
            #update the away status
            nick = chnl.context.get_info('away')
            if nick is None:
                chnl.context.command("AWAY Not Available")
    return 0

#sets the nick_away as nick
def update_backfromaway_nick():
    lst = xchat.get_list('channels')
    if lst is None:
        return
    #iterate over connected servers and update the nick
    for chnl in lst:
        if chnl.type == 1:
            nick = chnl.context.get_info('nick')
            match = re_away.match(nick)
            if not (match is None):
                nick = match.group(1)
                print "[autoaway] Updating nick on server %s to %s" % (chnl.context.get_info('server'), nick)
                chnl.context.command("NICK "+nick)
            #reset the away status if needed
            nick = chnl.context.get_info('away')
            if nick is not None:
                chnl.context.command("BACK")
    return 0

#reset the the away status 
xchat.hook_timer(10000, update_backfromaway_nick)

# hook into module unload 
xchat.hook_unload(unload_cb)

#poll timer to lookout for screen saver
timer_hook = xchat.hook_timer(1000, timeout_cb)

print "[autoaway] Module Loaded"
