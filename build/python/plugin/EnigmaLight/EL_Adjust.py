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
import os
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_VALIGN_CENTER

from threading import Thread, Timer

from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Components.config import config, getConfigListEntry
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch

from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen

from __common__ import EnigmaLight_log as log, showMessage, validIP, Clamp, getAspect
from __init__ import getCrashFilePath, _ # _ is translation

from EL_PathSelector import EL_Screen_PathSelector

from threading import currentThread
from EL_ThreadHelper import callOnMainThread

#===============================================================================
#
#===============================================================================
class EL_Screen_Adjust(Screen, ConfigListScreen, HelpableScreen):

	_hasChanged = False
	_session = None
	skins = None
	
	def __init__(self, session):
		try:
			log("",self)
			Screen.__init__(self, session)
			HelpableScreen.__init__(self)
			
			self.cfglist = []
			ConfigListScreen.__init__(self, self.cfglist, session, on_change = self._changed)
			
			self._session = session
			self._hasChanged = False

			self.controller = None
			self.selected = None

			self.aspect = getAspect()
			self.old_service = self.session.nav.getCurrentlyPlayingServiceReference()	
			
			# Disable OSD Transparency
			try:
				self.can_osd_alpha = open("/proc/stb/video/alpha", "r") and True or False
			except:
				self.can_osd_alpha = False
			
			if config.plugins.enigmalight.sampleBackground.getValue() == True:
				self.showBackground()
			
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
				"jumpNextMark":	self.keyNext,
				"jumpPreviousMark": self.keyPrev,
			}, -2)

			self["txt_green"].setText(_("Save"))

			self.createSetup()
			
			self.onLayoutFinish.append(self.finishLayout)

		except:
			from traceback import format_exc
			log("",self,"Error:" + format_exc())
			try:
				open(getCrashFilePath(),"w").write(format_exc())
			except:
				pass
		
	#===========================================================================
	# 
	#===========================================================================
	def finishLayout(self):
		log("",self)
		self.setTitle(_("Live coloradjustment"))

		if config.plugins.enigmalight.showstatusbar.value == True: #remove it
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
			

	def keyNext(self):
		log("",self)
		self.selected = self["config"].getCurrent()[1] 
		if self.selected == config.plugins.enigmalight.adjustr:
			config.plugins.enigmalight.adjustr.setValue(Clamp(config.plugins.enigmalight.adjustr.getValue()+10,0,255))
		elif self.selected == config.plugins.enigmalight.adjustg:
			config.plugins.enigmalight.adjustg.setValue(Clamp(config.plugins.enigmalight.adjustg.getValue()+10,0,255))
		elif self.selected == config.plugins.enigmalight.adjustb:
			config.plugins.enigmalight.adjustb.setValue(Clamp(config.plugins.enigmalight.adjustb.getValue()+10,0,255))
		self.createSetup()
		self._changed()
	
	def keyPrev(self):
		log("",self)
		self.selected = self["config"].getCurrent()[1]
		if self.selected == config.plugins.enigmalight.adjustr:
			config.plugins.enigmalight.adjustr.setValue(Clamp(config.plugins.enigmalight.adjustr.getValue()-10,0,255))
		elif self.selected == config.plugins.enigmalight.adjustg:
			config.plugins.enigmalight.adjustg.setValue(Clamp(config.plugins.enigmalight.adjustg.getValue()-10,0,255))
		elif self.selected == config.plugins.enigmalight.adjustb:
			config.plugins.enigmalight.adjustb.setValue(Clamp(config.plugins.enigmalight.adjustb.getValue()-10,0,255))
		self.createSetup()
		self._changed()


	#===========================================================================
	# 
	#===========================================================================
	def createSetup(self):
		log("",self)
		
		self.list = []

		self.list.append(getConfigListEntry(_('- Use live Adjust Settings:'), config.plugins.enigmalight.use_live_adjust))
		self.list.append(getConfigListEntry(_('- Color sequence:'), config.plugins.enigmalight.color_sequence))

		if config.plugins.enigmalight.use_live_adjust.value is True:

			r = config.plugins.enigmalight.adjustr.getValue()
			g = config.plugins.enigmalight.adjustg.getValue()
			b = config.plugins.enigmalight.adjustb.getValue()
			
			if config.plugins.enigmalight.color_sequence.value == "0":
				self.list.append(getConfigListEntry(_('- Adjust RED   %s\t   ')% str(r), config.plugins.enigmalight.adjustr))
				self.list.append(getConfigListEntry(_('- Adjust GREEN %s\t   ')% str(g), config.plugins.enigmalight.adjustg))
				self.list.append(getConfigListEntry(_('- Adjust BLUE  %s\t   ')% str(b), config.plugins.enigmalight.adjustb))
			elif config.plugins.enigmalight.color_sequence.value == "1":
				self.list.append(getConfigListEntry(_('- Adjust BLUE  %s\t   ')% str(r), config.plugins.enigmalight.adjustr))
				self.list.append(getConfigListEntry(_('- Adjust GREEN %s\t   ')% str(g), config.plugins.enigmalight.adjustg))
				self.list.append(getConfigListEntry(_('- Adjust RED   %s\t   ')% str(b), config.plugins.enigmalight.adjustb))
			elif config.plugins.enigmalight.color_sequence.value == "2":
				self.list.append(getConfigListEntry(_('- Adjust GREEN %s\t   ')% str(r), config.plugins.enigmalight.adjustr))
				self.list.append(getConfigListEntry(_('- Adjust BLUE  %s\t   ')% str(g), config.plugins.enigmalight.adjustg))
				self.list.append(getConfigListEntry(_('- Adjust RED   %s\t   ')% str(b), config.plugins.enigmalight.adjustb))
			elif config.plugins.enigmalight.color_sequence.value == "3":
				self.list.append(getConfigListEntry(_('- Adjust GREEN %s\t   ')% str(r), config.plugins.enigmalight.adjustr))
				self.list.append(getConfigListEntry(_('- Adjust RED  %s\t   ')% str(g), config.plugins.enigmalight.adjustg))
				self.list.append(getConfigListEntry(_('- Adjust BLUE   %s\t   ')% str(b), config.plugins.enigmalight.adjustb))
			elif config.plugins.enigmalight.color_sequence.value == "4":
				self.list.append(getConfigListEntry(_('- Adjust BLUE %s\t   ')% str(r), config.plugins.enigmalight.adjustr))
				self.list.append(getConfigListEntry(_('- Adjust RED  %s\t   ')% str(g), config.plugins.enigmalight.adjustg))
				self.list.append(getConfigListEntry(_('- Adjust GREEN   %s\t   ')% str(b), config.plugins.enigmalight.adjustb))
			elif config.plugins.enigmalight.color_sequence.value == "5":
				self.list.append(getConfigListEntry(_('- Adjust RED %s\t   ')% str(r), config.plugins.enigmalight.adjustr))
				self.list.append(getConfigListEntry(_('- Adjust BLUE  %s\t   ')% str(g), config.plugins.enigmalight.adjustg))
				self.list.append(getConfigListEntry(_('- Adjust GREEN   %s\t   ')% str(b), config.plugins.enigmalight.adjustb))

		self.list.append(getConfigListEntry(_('- Show background sample picture:'), config.plugins.enigmalight.sampleBackground))
		if config.plugins.enigmalight.sampleBackground.getValue() == True:
			self.list.append(getConfigListEntry(_('- Sample picture:'), config.plugins.enigmalight.sampleBackground_mvi))
			
		self["config"].list = self.list
		#self["config"].l.setList(self.cfglist)
		
		
		
	#===========================================================================
	# 
	#===========================================================================
	def _changed(self):
		
		
		self._hasChanged = True
		self.selected = self["config"].getCurrent()[1]

		if self.selected is config.plugins.enigmalight.sampleBackground or self.selected is config.plugins.enigmalight.sampleBackground_mvi:
			if config.plugins.enigmalight.sampleBackground.getValue() is True:
				self.showBackground()
			else:
				self.showOldService()
  
		self.controller.changeValue(self["config"].getCurrent()[1])
		

	def showOldService(self):
		log("",self)
		# Restart old service
		self.session.nav.stopService()
		self.session.nav.playService(self.old_service)
		
		## Restore OSD Transparency Settings
		os.system("echo " + hex(0)[2:] + " > /proc/stb/vmpeg/0/dst_top")
		os.system("echo " + hex(0)[2:] + " > /proc/stb/vmpeg/0/dst_left")
		os.system("echo " + hex(720)[2:] + " > /proc/stb/vmpeg/0/dst_width")
		os.system("echo " + hex(576)[2:] + " > /proc/stb/vmpeg/0/dst_height")

		if self.can_osd_alpha:
			try:
				open("/proc/stb/video/alpha", "w").write(str(config.av.osd_alpha.value))
			except:
				print "Set OSD Transparacy failed"
		
	def showBackground(self):
		log("",self)
		### TEST ###	
		self.session.nav.stopService()

		# Disable OSD Transparency
		try:
			self.can_osd_alpha = open("/proc/stb/video/alpha", "r") and True or False
		except:
			self.can_osd_alpha = False
		
		if self.can_osd_alpha:
			open("/proc/stb/video/alpha", "w").write(str("255"))
		
		# Show Background MVI
		os.system("/usr/bin/showiframe /usr/lib/enigma2/python/Plugins/Extensions/EnigmaLight/mvi/"+str(config.plugins.enigmalight.sampleBackground_mvi.getValue())+".mvi &")
			
		### END TEST ###

	#===========================================================================
	# 
	#===========================================================================
	def updateHelp(self):
		log("",self)
		cur = self["config"].getCurrent()
		self["help"].text = cur and cur[2] or "empty"
		
	#==========================================================================
	# 
	#==========================================================================
	def setStatusBarInfo(self,text):
		self["txt_statusbar_info"].setText(text)

	#==========================================================================
	# 
	#==========================================================================
	def setStatusBarTxt(self,text):
		self["txt_statusbar"].setText(text)
	
	#===========================================================================
	# 
	#===========================================================================
	def ok(self):
		cur = self["config"].getCurrent()
		
	#===========================================================================
	# 
	#===========================================================================
	def keySave(self):
		log("",self)
		self.saveAll()
		self.close(None)

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

		