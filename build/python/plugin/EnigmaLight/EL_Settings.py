# -*- coding: utf-8 -*-
"""
EnigmaLight Plugin by Speedy1985, 2014
 
https://github.com/speedy1985

Parts of the code is from DonDavici (c) 2012 and other plugins:
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
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_VALIGN_CENTER

from threading import Thread, Timer

from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Components.config import config, getConfigListEntry
from Components.Label import Label
from Components.Pixmap import Pixmap

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.HelpMenu import HelpableScreen
from EL_Check import EL_Screen_Check

from __common__ import EnigmaLight_log as log, showMessage, validIP, testDaemonConnectivity, setSymbolic
from __init__ import getCrashFilePath, _ # _ is translation

from EL_PathSelector import EL_Screen_PathSelector

from threading import currentThread
from EL_ThreadHelper import callOnMainThread

#===============================================================================
#
#===============================================================================
class EL_Screen_Settings(Screen, ConfigListScreen, HelpableScreen):

	_hasChanged = False
	_session = None
	skins = None
	
	def __init__(self, session):
		log("",self,"Settings Opened succesfull..")

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		
		self.cfglist = []
		ConfigListScreen.__init__(self, self.cfglist, session, on_change = self._changed)
		
		self._session = session
		self._hasChanged = False
		self._hasNetworkChanged = False
		self._binTypeChanged = False
		self._restartBinary = False

		self.controller = None
		self.selected = None

		self["txt_green"] = Label()
		self["btn_green"] = Pixmap()

		self["statusbar"] = Pixmap()
		self["txt_statusbar"] = Label()
		self["txt_statusbar_info"] = Label()

		self["help"] = StaticText()

		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "EL_Settings"],
		{
			"green": self.keySave,
			"red": self.keyCancel,
			"cancel": self.keyCancel,
			"ok": self.ok,
			"left": self.keyLeft,
			"right": self.keyRight,
			"bouquet_up":	self.keyBouquetUp,
			"bouquet_down":	self.keyBouquetDown,
		}, -2)

		self["txt_green"].setText(_("Save"))
		self.createSetup()
		
		log("",self,"Finisch layout...")

		self["config"].onSelectionChanged.append(self.updateHelp)
		self.onLayoutFinish.append(self.finishLayout)

	#===========================================================================
	# 
	#===========================================================================
	def finishLayout(self):
		log("",self,"Layout finisched..")

		self.setTitle(_("Settings"))
		
		if not config.plugins.enigmalight.showstatusbar.getValue():			
			self["statusbar"].hide()
			self["txt_statusbar"].hide()
			self["txt_statusbar_info"].hide()			
		else:
			self["statusbar"].show()
			self["txt_statusbar"].show()
			self["txt_statusbar_info"].show()

	#===========================================================================
	# 
	#===========================================================================
	def setController(self, controller):
		self.controller = controller
		self.controller.setSession(self.session)

	#==========================================================================
	# Functions for use from others thread
	#==========================================================================	
	def handleFromThread(self,func,*args):
		if args:
			callOnMainThread(func,args[0])
		else:
			callOnMainThread(func)

	def printWithThread(self,res):
		print "%s :: {%s}" %(res, currentThread().getName())

	def setStatusBarInfo(self,text):
		#self.printWithThread("setStatusBarInfo())")
		self["txt_statusbar_info"].setText(text)

	def setStatusBarTxt(self,text):
		#self.printWithThread("setStatusBarTxt()")
		self["txt_statusbar"].setText(text)

	def showStatusBar(self,value):
		if value:
			self["statusbar"].hide()
			self["txt_statusbar_info"].hide()
			self["txt_statusbar"].hide()
		else:
			self["statusbar"].show()
			self["txt_statusbar_info"].show()
			self["txt_statusbar"].show()

	#===========================================================================
	# 
	#===========================================================================
	def createSetup(self):
		log("",self)
		self.cfglist = []

		# GENERAL SETTINGS
		self.cfglist.append(getConfigListEntry(_("[ General Settings ]"), config.plugins.enigmalight.about, _(" ")))
		self.cfglist.append(getConfigListEntry(_('- Type of EnigmaLight binary:\r'),config.plugins.enigmalight.bintype, _("Here you can select the type of enigmalight, the most receivers can use the fpu version but some receivers can't. For then use the normal version")))     
		self.configfilepath = getConfigListEntry(_("- Configuration File"), config.plugins.enigmalight.configfilepath, _("Select your configfile, default /etc/enigmalight.conf will be used "))
		self.cfglist.append(self.configfilepath)

		self.cfglist.append(getConfigListEntry(_('- Run EnigmaLight as server when lights are off:\r'),config.plugins.enigmalight.server, _("Run EnigmaLight as Server for Boblight or other clients ")))     
		self.cfglist.append(getConfigListEntry(_('- Check for update, press OK\r'),config.plugins.enigmalight.clickOK, _("Press OK to check for update.. "))),
		self.cfglist.append(getConfigListEntry(_('- Show message when turn on/off lights:\r'),config.plugins.enigmalight.message_onoff, _("Show a messagebox when you turn on/off the lights ")))
		self.cfglist.append(getConfigListEntry(_('- Enable lights on boot:\r'),config.plugins.enigmalight.autostart, _("Automatic turn on lights on boot ")))
		self.cfglist.append(getConfigListEntry(_('- Cluster Leds:\r'),config.plugins.enigmalight.cluster, _("Cluster [X] Leds as one led.\nDefault each led had is own color, with this option you can bundle/cluster this to 2 -> 10 leds.")))
		self.cfglist.append(getConfigListEntry(_('- Delay: \r'), config.plugins.enigmalight.delay, _(" Some tv's are slower then the lights. With this option you can make the output 1 -> 20 frames later.")))
		self.cfglist.append(getConfigListEntry(_('- Interval:\r'), config.plugins.enigmalight.interval, _("How fast Enigmalight wil run.\n0.01 = 15 -> 40fps | 0.10 = 10fps | 0.20 = 5fps: "))) 
		self.cfglist.append(getConfigListEntry(_('- 3D Mode:\r'), config.plugins.enigmalight.m_3dmode, _("Turn on/off 3D Mode, SBS or TAB")))
		self.cfglist.append(getConfigListEntry(_('- Default lightmode:\r'),config.plugins.enigmalight.mode, _(" ")))
		self.cfglist.append(getConfigListEntry(_('- Standby Mode:\r'),config.plugins.enigmalight.standbymode, _("Turn off lights or use moodlamp in standby ")))
		self.cfglist.append(getConfigListEntry(_('- Color order:'), config.plugins.enigmalight.color_order,  _(" Set the order as given in enigmalight.conf.")))
		
		self.cfglist.append(getConfigListEntry(_("[ Blackbars ]"), config.plugins.enigmalight.about, _(" ")))
		self.cfglist.append(getConfigListEntry(_('- Remove Blackbars top and bottom:\r'),config.plugins.enigmalight.blackbar_h, _("Remove horizontal blackbars from lights.")))
		self.cfglist.append(getConfigListEntry(_('- Remove Blackbars left and right:\r'),config.plugins.enigmalight.blackbar_v, _("Remove vertical blackbars from lights.")))
		self.cfglist.append(getConfigListEntry(_('- Delay before remove:\r'), config.plugins.enigmalight.blackbar_f, _("Count from 0 to given number\nif the blackbars are still there then remove them.\nif enigmalight runs on 10fps and you will wait 10sec before remove, then set it to 100")))
		#getConfigListEntry(_('Switch on/off lights when TV turns on/off:'), config.plugins.enigmalight.hdmicec_enabled),

				#Network
		self.cfglist.append(getConfigListEntry(_("[ Network Settings ]"), config.plugins.enigmalight.about, _(" ")))
		self.cfglist.append(getConfigListEntry(_('- Enable network mode (connect with other daemon):\r'), config.plugins.enigmalight.network_onoff, _("Use enigmalight as client and connect with other daemon over network (not for local use)")))
		
		if config.plugins.enigmalight.network_onoff.value is True: 
			self.cfglist.append(getConfigListEntry(_('- Host ipaddress:\r'), config.plugins.enigmalight.address, _(" ")))
			self.cfglist.append(getConfigListEntry(_('- Daemon port:\r'), config.plugins.enigmalight.port, _(" ")))

		#Timer
		self.cfglist.append(getConfigListEntry(_("[ Timer Settings ]"), config.plugins.enigmalight.about, _(" ")))
		self.cfglist.append(getConfigListEntry(_('- Use Timer:\r'), config.plugins.enigmalight.timer_onoff, _("Turn on/off lights @ given time ")))

		if config.plugins.enigmalight.timer_onoff.value is True:
			self.cfglist.append(getConfigListEntry(_('- Don\'t turn lights off/on in standby:\r'), config.plugins.enigmalight.timer_standby_onoff, _("Disable timer function in standbymode ")))
			self.cfglist.append(getConfigListEntry(_("- Enable lights:\r"), config.plugins.enigmalight.time_start, _("Time when lights go on ")))
			self.cfglist.append(getConfigListEntry(_("- Disable lights:\r"), config.plugins.enigmalight.time_end, _("Time when lights go off ")))

		#server
		self.cfglist.append(getConfigListEntry(_("[ Remote ]"), config.plugins.enigmalight.about, _(" ")))
		self.cfglist.append(getConfigListEntry(_("- Use remoteserver:\r"), config.plugins.enigmalight.remote_server, _("Control EnigmaLight from browser")))
		if config.plugins.enigmalight.remote_server.value:
			self.cfglist.append(getConfigListEntry(_("- Remoteserver Port:\r"), config.plugins.enigmalight.remote_port, _("Show status at bottomscreen fps, cpu usage and currentmode")))
		#Debug
		self.cfglist.append(getConfigListEntry(_("[ Misc ]"), config.plugins.enigmalight.about, _(" ")))
		self.cfglist.append(getConfigListEntry(_("- Show statusbar on bottom of screen:\r"), config.plugins.enigmalight.showstatusbar, _("Show status at bottomscreen fps, currentmode and other info")))
		if config.plugins.enigmalight.showstatusbar.getValue():			
			self.cfglist.append(getConfigListEntry(_("- Remove statusbar from tuningscreen:\r"), config.plugins.enigmalight.showstatusbar_tuning, _("Remove the statusbar from colortuning screen")))
		self.cfglist.append(getConfigListEntry(_("- Show errormessages:\r"), config.plugins.enigmalight.message_error_onoff, _("Turn on if you want to see error information")))		
		self.cfglist.append(getConfigListEntry(_("- Debug-Logging > /tmp/enigmalight_gui.log:\r"), config.plugins.enigmalight.EnableEventLog, _("")))

		#	self.cfglist.append(getConfigListEntry(_("- Log folder path:\r"), config.plugins.enigmalight.logfolderpath		, _("Default log wil be saved at /tmp/enigmalight_gui.log")))
		#	self.cfglist.append(self.logfolderpath)		

		self["config"].list = self.cfglist
		#self["config"].l.setList(self.cfglist)
		
	#===========================================================================
	# 
	#===========================================================================
	def _changed(self):
		self._hasChanged = True
		self.controller.changeValue(self["config"].getCurrent()[1])

		if self["config"].getCurrent()[1] == config.plugins.enigmalight.address or self["config"].getCurrent()[1] == config.plugins.enigmalight.port or self["config"].getCurrent()[1] == config.plugins.enigmalight.network_onoff:
			self._hasNetworkChanged = True
		elif self["config"].getCurrent()[1] == config.plugins.enigmalight.EnableEventLog:
			self._hasNetworkChanged = False
			self.saveAll()
		elif self["config"].getCurrent()[1] == config.plugins.enigmalight.remote_server or self["config"].getCurrent()[1] == config.plugins.enigmalight.remote_port:
			if config.plugins.enigmalight.remote_server.value:
				self.controller.StartServer()
			else:
				self.controller.StopServer()

		elif self["config"].getCurrent()[1] == config.plugins.enigmalight.bintype:
			self.saveAll()
			self._binTypeChanged = True

	#===========================================================================
	# 
	#===========================================================================
	def updateHelp(self):
		cur = self["config"].getCurrent()
		self["help"].text = cur and cur[2] or "empty"
		
	#===========================================================================
	# 
	#===========================================================================
	def ok(self):
		cur = self["config"].getCurrent()
		
		if cur == self.configfilepath:
			self.session.openWithCallback(self.savePathConfig,EL_Screen_PathSelector,self.configfilepath[1].value, "configfile", "Select configfile")
		elif self["config"].getCurrent()[1] == config.plugins.enigmalight.clickOK:
			EL_Screen_Check(self.session).checkForUpdate(self.controller)
			self.controller.setStatusBarInfo("Check for update...")
			self.controller.checkedForUpdates = True

	#===========================================================================
	# 
	#===========================================================================
	def savePathConfig(self, pathValue, myType):
		log("",self)
		log("",self,"pathValue: " + str(pathValue))
		log("",self,"type: " + str(myType))
		
		if pathValue is not None:

			if myType == "configfile":
				self.configfilepath[1].value = pathValue
				self._restartBinary = True
				
				if pathValue != None:
					message = self.session.openWithCallback(self.restartEnigmaLight,MessageBox,_("To reload the configfile EnigmaLight needs a restart, restart now ?"), MessageBox.TYPE_YESNO)
					message.setTitle(_("Reload configfile ?"))

					config.plugins.enigmalight.save()

	def restartEnigmaLight(self,answer):
		log("",self)
		#first kill enigmalight
		if answer:
			self.controller.killEnigmalight(None,self.KillEnigmaLightDone)

	def restartEnigma2(self,answer):
		log("",self)
		#first kill enigmalight
		if answer:
			self.session.open(TryQuitMainloop, 3)

	def KillEnigmaLightDone(self):
		log("",self)
		setSymbolic() #set new symbolic if needed
		self.controller.Control("grabber","start")
		self.close(None)

	#===========================================================================
	# 
	#===========================================================================
	def keySave(self):
		log("",self)
		#check ip if network is true, before save
		if config.plugins.enigmalight.network_onoff.getValue():
			#check ip
			if not validIP(str(config.plugins.enigmalight.address.getText())):
				showMessage(self.session,_("Ip address %s is not accepted, check your input and try again.") %(str(config.plugins.enigmalight.address.getText())),"W")
			else:
				#check connection
				if not testDaemonConnectivity(config.plugins.enigmalight.address.getText(),config.plugins.enigmalight.port.value):
					showMessage(self.session,_("Enigmalight can't connect with %s:%s,\ncheck your input and try again.") %(str(config.plugins.enigmalight.address.getText()),str(config.plugins.enigmalight.port.getValue())),"W")
				else:
					showMessage(self.session,_("Test Connection with %s:%s, succesfull!") %(str(config.plugins.enigmalight.address.getText()),str(config.plugins.enigmalight.port.getValue())),"I")
					self.saveAll()
					message = self.session.openWithCallback(self.startClient,MessageBox,_("Do you want to (re)start the client and connect with %s:%s ?") %(str(config.plugins.enigmalight.address.getText()),str(config.plugins.enigmalight.port.getValue())), MessageBox.TYPE_YESNO)
					message.setTitle(_("(Re)start client ?"))
		else:
			self.saveAll()
			if self._hasNetworkChanged:
				self._hasNetworkChanged = False

				if self.controller.lightsEnabled:
					self.controller.killEnigmalight(None,None)

				message = self.session.openWithCallback(self.startGrabber,MessageBox,_("Do you want to (re)start the client ?"), MessageBox.TYPE_YESNO)
				message.setTitle(_("(Re)start client ?"))
			elif self._binTypeChanged:
				message = self.session.openWithCallback(self.restartEnigmaLight,MessageBox,_("Type of enigmalight has changed, Start this type of Enigmalight ?"), MessageBox.TYPE_YESNO)
				message.setTitle(_("Start ?"))
			else:
				self.close(None)
		
	#===========================================================================
	# 
	#===========================================================================
	def startClient(self, answer):
		log("",self)
		if answer is True:
			self.controller.killEnigmalight(None,self.controller.switchtoNetwork())			
		else:
			self.close()

	def startGrabber(self, answer):
		log("",self)
		if answer is True:
			self.controller.Control("grabber","start")
		else:
			self.close()

	#===========================================================================
	# 
	#===========================================================================
	def keyLeft(self):
		log("",self)
		ConfigListScreen.keyLeft(self)
		self.createSetup()
		
	#===========================================================================
	# 
	#===========================================================================
	def keyRight(self):
		log("",self)
		ConfigListScreen.keyRight(self)
		self.createSetup()
		
	#===========================================================================
	# 
	#===========================================================================
	def keyBouquetUp(self):
		log("",self)
		self["config"].instance.moveSelection(self["config"].instance.pageUp)
		
	#===========================================================================
	# 
	#===========================================================================
	def keyBouquetDown(self):
		log("",self)
		self["config"].instance.moveSelection(self["config"].instance.pageDown)

		