
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

from Components.Sources.CanvasSource import CanvasSource

from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Components.config import config, getConfigListEntry, configfile
from Components.Label import Label
from Components.Pixmap import Pixmap

from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from EL_Control import Controller

from __common__ import EnigmaLight_log as log, showMessage, Clamp, getRGB
from . import _
from __init__ import _ # _ is translation

from EL_PathSelector import EL_Screen_PathSelector

from threading import currentThread
from EL_ThreadHelper import callOnMainThread

#===============================================================================
#
#===============================================================================
class EL_Screen_Moodlamp(Screen, ConfigListScreen, HelpableScreen):

	_hasChanged = False
	_session = None
	skins = None
	
	def __init__(self, session):
		log("",self,"Moodlamp Opened succesfull..")
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		
		self.cfglist = []
		ConfigListScreen.__init__(self, self.cfglist, session, on_change = self._changed)
		
		self._session = session
		self._hasChanged = False
		
		self.selected = None
		self.controller = None

		self["txt_green"] = Label()
		self["txt_yellow"] = Label()

		self["canvas_text"] = StaticText()
		
		self["help"] = StaticText()

		self["btn_green"] = Pixmap()
		self["btn_yellow"] = Pixmap()

		self["statusbar"] = Pixmap()
		self["txt_statusbar"] = Label()
		self["txt_statusbar_info"] = Label()

		self["Canvas"] = CanvasSource()
		
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

		self["canvas_text"].text = _("Static color:")
		self.createList()

		log("",self,"Finisch layout..")
		
		self["config"].onSelectionChanged.append(self.updateHelp)
		self.onLayoutFinish.append(self.finishLayout)

	#===========================================================================
	# 
	#===========================================================================
	def finishLayout(self):
		log("",self,"Layout finsched..")
		self.setBackground()
		self.setTitle(_("Moodlamp configuration"))

		if not config.plugins.enigmalight.showstatusbar.getValue():
			self["statusbar"].hide()
			self["txt_statusbar"].hide()
			self["txt_statusbar_info"].hide()
		else:
			self["statusbar"].show()
			self["txt_statusbar"].show()
			self["txt_statusbar_info"].show()

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
	def setController(self, controller):
		self.controller = controller
		self.controller.setSession(self.session)

		if self.controller.lightsEnabled is True:
			self.controller.writeMoodlamp()

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
	def createList(self):
		log("",self)
		separator = "".ljust(120,"_")
		
		self.cfglist = []

		# COLOR SETTINGS
		self.cfglist.append(getConfigListEntry(_('- Standby mode:'), config.plugins.enigmalight.standbymode, _(" Use moodlamp or lights off in standby.")))
		self.cfglist.append(getConfigListEntry(_('- Moodlamp Mode:'), config.plugins.enigmalight.moodlamp_mode, _(" ")))
		#self.cfglist.append(getConfigListEntry(_('- Color order:'), config.plugins.enigmalight.color_order, _(" ")))

		if config.plugins.enigmalight.moodlamp_mode.value is str(1):

			r = config.plugins.enigmalight.moodlamp_static_color_r.getValue()
			g = config.plugins.enigmalight.moodlamp_static_color_g.getValue()
			b = config.plugins.enigmalight.moodlamp_static_color_b.getValue()

			#if config.plugins.enigmalight.color_order.getValue() == "0":
			self.cfglist.append(getConfigListEntry(_('- Color RED\t: %s') % str(r), config.plugins.enigmalight.moodlamp_static_color_r, _(" ")))
			self.cfglist.append(getConfigListEntry(_('- Color GREEN\t: %s') % str(g), config.plugins.enigmalight.moodlamp_static_color_g, _(" ")))
			self.cfglist.append(getConfigListEntry(_('- Color BLUE\t: %s') % str(b), config.plugins.enigmalight.moodlamp_static_color_b, _(" ")))
			"""
			elif config.plugins.enigmalight.color_order.getValue() == "1":
				self.cfglist.append(getConfigListEntry(_('- Color BLUE : %s\t') % str(r), config.plugins.enigmalight.moodlamp_static_color_r, _(" ")))
				self.cfglist.append(getConfigListEntry(_('- Color GREEN : %s\t') % str(g), config.plugins.enigmalight.moodlamp_static_color_g, _(" ")))
				self.cfglist.append(getConfigListEntry(_('- Color RED : %s\t') % str(b), config.plugins.enigmalight.moodlamp_static_color_b, _(" ")))
			elif config.plugins.enigmalight.color_order.getValue() == "2":
				self.cfglist.append(getConfigListEntry(_('- Color GREEN : %s\t') % str(r), config.plugins.enigmalight.moodlamp_static_color_r, _(" ")))
				self.cfglist.append(getConfigListEntry(_('- Color BLUE : %s\t') % str(g), config.plugins.enigmalight.moodlamp_static_color_g, _(" ")))
				self.cfglist.append(getConfigListEntry(_('- Color RED : %s\t') % str(b), config.plugins.enigmalight.moodlamp_static_color_b, _(" ")))
			elif config.plugins.enigmalight.color_order.getValue() == "3":
				self.cfglist.append(getConfigListEntry(_('- Color GREEN : %s\t') % str(r), config.plugins.enigmalight.moodlamp_static_color_r, _(" ")))
				self.cfglist.append(getConfigListEntry(_('- Color RED : %s\t') % str(g), config.plugins.enigmalight.moodlamp_static_color_g, _(" ")))
				self.cfglist.append(getConfigListEntry(_('- Color BLUE : %s\t') % str(b), config.plugins.enigmalight.moodlamp_static_color_b, _(" ")))
			elif config.plugins.enigmalight.color_order.getValue() == "4":
				self.cfglist.append(getConfigListEntry(_('- Color BLUE : %s\t') % str(r), config.plugins.enigmalight.moodlamp_static_color_r, _(" ")))
				self.cfglist.append(getConfigListEntry(_('- Color RED : %s\t') % str(g), config.plugins.enigmalight.moodlamp_static_color_g, _(" ")))
				self.cfglist.append(getConfigListEntry(_('- Color GREEN : %s\t') % str(b), config.plugins.enigmalight.moodlamp_static_color_b, _(" ")))
			elif config.plugins.enigmalight.color_order.getValue() == "5":
				self.cfglist.append(getConfigListEntry(_('- Color RED : %s\t') % str(r), config.plugins.enigmalight.moodlamp_static_color_r, _(" ")))
				self.cfglist.append(getConfigListEntry(_('- Color BLUE : %s\t') % str(g), config.plugins.enigmalight.moodlamp_static_color_g, _(" ")))
				self.cfglist.append(getConfigListEntry(_('- Color GREEN : %s\t') % str(b), config.plugins.enigmalight.moodlamp_static_color_b, _(" ")))
			"""

		if config.plugins.enigmalight.moodlamp_mode.value is str(4):
			self.cfglist.append(getConfigListEntry(_('- Fader brightness : %s\t') % str(config.plugins.enigmalight.moodlamp_fader_brightness.getValue()), config.plugins.enigmalight.moodlamp_fader_brightness, _(" ")))
		self["config"].list = self.cfglist
		self["config"].l.setList(self.cfglist)
		
	#===========================================================================
	# 
	#===========================================================================

	def _changed(self):
		self._hasChanged = True

		self.selected = self["config"].getCurrent()[1]

		#Send option
		self.controller.changeValue(self.selected)

		if config.plugins.enigmalight.moodlamp_mode.value is str(1):
			self.setBackground()
		

	#===========================================================================
	# 
	#===========================================================================
	def updateHelp(self):
		log("",self)
		cur = self["config"].getCurrent()
		self["help"].text = cur and cur[2] or "empty"
		
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
		self.createList()
		
	#===========================================================================
	# 
	#===========================================================================
	def keyRight(self):
		log("",self)
		ConfigListScreen.keyRight(self)
		self.createList()
		
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
	
	#===========================================================================
	# 
	#===========================================================================
	def setBackground(self):
		log("Set Canvas bg..",self)
		self.c = self["Canvas"]

		r = config.plugins.enigmalight.moodlamp_static_color_r.getValue()
		g = config.plugins.enigmalight.moodlamp_static_color_g.getValue()
		b = config.plugins.enigmalight.moodlamp_static_color_b.getValue()

		#if config.plugins.enigmalight.color_order.getValue() == "0":
		self.c.fill(0, 0, 950, 30, getRGB(r,g,b))
		# elif config.plugins.enigmalight.color_order.getValue() == "1":
		# 	self.c.fill(0, 0, 950, 30, getRGB(b,g,r))		   
		# elif config.plugins.enigmalight.color_order.getValue() == "2":
		# 	self.c.fill(0, 0, 950, 30, getRGB(g,b,r))
		# elif config.plugins.enigmalight.color_order.getValue() == "3":
		# 	self.c.fill(0, 0, 950, 30, getRGB(g,r,b))
		# elif config.plugins.enigmalight.color_order.getValue() == "4":
		# 	self.c.fill(0, 0, 950, 30, getRGB(b,r,g))
		# elif config.plugins.enigmalight.color_order.getValue() == "5":
		# 	self.c.fill(0, 0, 950, 30, getRGB(r,b,g))
		# self.c.flush()

	#===========================================================================
	# 
	#===========================================================================
	def keyNext(self):
		log("",self)
		self.selected = self["config"].getCurrent()[1] 
		if self.selected == config.plugins.enigmalight.moodlamp_static_color_r:
			config.plugins.enigmalight.moodlamp_static_color_r.setValue(Clamp(config.plugins.enigmalight.moodlamp_static_color_r.getValue()+10,0,255))
		elif self.selected == config.plugins.enigmalight.moodlamp_static_color_g:
			config.plugins.enigmalight.moodlamp_static_color_g.setValue(Clamp(config.plugins.enigmalight.moodlamp_static_color_g.getValue()+10,0,255))
		elif self.selected == config.plugins.enigmalight.moodlamp_static_color_b:
			config.plugins.enigmalight.moodlamp_static_color_b.setValue(Clamp(config.plugins.enigmalight.moodlamp_static_color_b.getValue()+10,0,255))
		self._changed() #Refresh list
		self.createList()
	
	#===========================================================================
	# 
	#===========================================================================
	def keyPrev(self):
		log("",self)
		self.selected = self["config"].getCurrent()[1]
		if self.selected == config.plugins.enigmalight.moodlamp_static_color_r:
			config.plugins.enigmalight.moodlamp_static_color_r.setValue(Clamp(config.plugins.enigmalight.moodlamp_static_color_r.getValue()-10,0,255))
		elif self.selected == config.plugins.enigmalight.moodlamp_static_color_g:
			config.plugins.enigmalight.moodlamp_static_color_g.setValue(Clamp(config.plugins.enigmalight.moodlamp_static_color_g.getValue()-10,0,255))
		elif self.selected == config.plugins.enigmalight.moodlamp_static_color_b:
			config.plugins.enigmalight.moodlamp_static_color_b.setValue(Clamp(config.plugins.enigmalight.moodlamp_static_color_b.getValue()-10,0,255))
		self._changed() #Refresh list
		self.createList()
