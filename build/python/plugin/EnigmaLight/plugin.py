# -*- coding: utf-8 -*-
"""
EnigmaLight Plugin by Speedy1985, 2014
 
https://github.com/speedy1985

Parts of the code are from DonDavici (c) 2012 and other plugins:
all credits to the coders :-)

EnigmaLight is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

EnigmaLight is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
"""
#===============================================================================
# IMPORT
#===============================================================================
from Plugins.Plugin import PluginDescriptor

from Components.config import config, configfile
from . import _
from __init__ import getCrashFilePath, Prepare, _ # _ is translation
from __common__ import checkSymbolic, showError, rmFile, EnigmaLight_log as log

from EL_Control import Controller
from EL_Timer import ELightTimer
from EL_About import EL_Screen_About

m_session = None

## Start timer thread
timer = ELightTimer()
timer.start()

## Start controller thread
controller = Controller()
controller.start()

#remove old files
rmFile(getCrashFilePath())
rmFile("/tmp/enigmalight_gui.log")

#check if enigmalight is pointed to good OE Version, if not then make the link
checkSymbolic()

#===============================================================================
# main
# Actions to take place when starting the plugin over extensions
#===============================================================================
#noinspection PyUnusedLocal
def main(session, **kwargs):
	log("",None,"plugin::sessionstart()")
	session.open(EnigmaLight_MainMenu)
	
def sessionstart(reason, **kwargs):

	try:
	    if reason == 0:
	        timer.setSession(kwargs["session"])
	        controller.setGlobalSession(kwargs["session"])
	except:
		from traceback import format_exc
		log("",None,"plugin::sessionstart() > Error: " +format_exc())
		try:
			open(getCrashFilePath(),"w").write(format_exc())
		except:
			pass
	   
def EnigmaLight_MainMenu(*args, **kwargs):
	try:
		log("",None,"plugin::EnigmaLight_MainMenu() > MainMenu..")
		import EL_MainMenu

		log("",None,"plugin::EnigmaLight_MainMenu() > Set Instances..")
		EL_MainMenu.TIMER_INSTANCE = timer
		EL_MainMenu.CONTROLLER_INSTANCE = controller

		return EL_MainMenu.EL_Screen_MainMenu(*args, **kwargs)
	except:
		from traceback import format_exc
		log("",None,"plugin::EnigmaLight_MainMenu() > Error: " +format_exc())
		try:
			open(getCrashFilePath(),"w").write(format_exc())
		except:
			pass


#noinspection PyUnusedLocal
def Autostart(reason, session=None, **kwargs):

	try:
		if reason == 0:
			Prepare()

			if config.plugins.enigmalight.autostart.getValue() != str(0):
				log("",None,"plugin::Autostart(reason, session=None, **kwargs)) > Autostart enigmalight..")
				
				if config.plugins.enigmalight.autostart.getValue() == str(1):				
					controller.Control("start", "server")
				elif config.plugins.enigmalight.autostart.getValue() == str(2):				
					controller.Control("start", "dynamic")
				elif config.plugins.enigmalight.autostart.getValue() == str(3):				
					controller.Control("start", "moodlamp")
			
			if config.plugins.enigmalight.remote_server.getValue():
				controller.StartServer()
			else:
				controller.StopServer()
	except:
		from traceback import format_exc
		log("",None,"plugin::Autostart()) > Error: " +format_exc())
		try:
			open(getCrashFilePath(),"w").write(format_exc())
		except:
			pass


#===============================================================================
# plugins
# Actions to take place in Plugins
#===============================================================================
#noinspection PyUnusedLocal
def Plugins(**kwargs):
	try:
		myList = [PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=sessionstart),
	    PluginDescriptor(name=_('EnigmaLight'), description=_('TV backlight'), where=PluginDescriptor.WHERE_PLUGINMENU, icon='button.png', needsRestart = False, fnc=main),
	    PluginDescriptor(name=_('EnigmaLight | on/off'), description=_('TV backlight'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon='button.png', needsRestart = False, fnc=controller.Toggle),
	    PluginDescriptor(name=_('EnigmaLight | Settings'), description=_('Enigmalight GUI'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon='button.png', needsRestart = False, fnc=main),
	    PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, fnc = Autostart)]
	    #PluginDescriptor(name=_('EnigmaLight | Switch Mode'), description=_('TV backlight'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon='button.png', needsRestart = False, fnc=LightToggle)]
	except:
		from traceback import format_exc
		log("",None,"plugin::Plugins(**kwargs) > Error: " +format_exc())
		try:
			open(getCrashFilePath(),"w").write(format_exc())
		except:
			pass

	return myList