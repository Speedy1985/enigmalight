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
#=================================
#IMPORT
#=================================
import time

from Components.ActionMap import HelpableActionMap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.config import config, configfile
from Components.Label import Label
from Components.Pixmap import Pixmap

from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

from EL_Settings import EL_Screen_Settings
from EL_Tuning import EL_Screen_Tuning
from EL_Moodlamp import EL_Screen_Moodlamp
from EL_About import EL_Screen_About
from EL_Help import EL_Screen_Help
from EL_ConfigEditor import EL_Screen_ConfigEditor

from EL_Helper_MovingLabel import EL_Helper_HorizontalMenu
from EL_Helper_Singleton import Singleton
from EL_Check import EL_Screen_Check

from __common__ import checkSymbolic, EnigmaLight_log as log, showMessage, showError
from __plugin__ import Plugin
from __init__ import getCrashFilePath, _ # _ is translation

from threading import currentThread
from EL_ThreadHelper import callOnMainThread

TIMER_INSTANCE = None
CONTROLLER_INSTANCE = None

#===============================================================================
#
#===============================================================================
class EL_Screen_MainMenu(Screen, EL_Helper_HorizontalMenu):

	selectedEntry = None
	nextExitIsQuit = True

	def __init__(self, session, allowOveride=True):

		try:
			log("",self,"Menu Opened succesfull..")

			#check if enigmalight is pointed to good OE Version, if not then make the link
			checkSymbolic()

			Screen.__init__(self, session)		
			self.session = session
			
			#Set screen
			self.currentScreen = self

			#Set controller and session
			self.controller = CONTROLLER_INSTANCE
			self.controller.setSession(self.session)
			self.controller.setMainScreen(True)

			#Timer class
			self.timer_class = TIMER_INSTANCE
			TIMER_INSTANCE.setController(CONTROLLER_INSTANCE)

			#Set horizontal menu items
			self.setHorMenuElements(depth=2)
			self.translateNames()

			# Menu
			self["menu"]= List(enableWrapAround=True)
			
			# Buttons
			self["txt_green"] = Label()
			self["btn_green"] = Pixmap()
			self["txt_red"] = Label()
			self["btn_red"] = Pixmap()
			self["txt_blue"] = Label()
			self["btn_blue"] = Pixmap()
			self["txt_yellow"] = Label()
			self["btn_yellow"] = Pixmap()
			self["txt_check"] = Label()

			self["statusbar"] = Pixmap()
			self["txt_statusbar"] = Label()
			self["txt_statusbar_info"] = Label()

			self["actions"] = HelpableActionMap(self, "EL_MainMenuActions", 
				{
					"ok":		(self.okbuttonClick, ""),
					"left":		(self.left, ""),
					"right":	(self.right, ""),
					"up":		(self.up, ""),
					"down":		(self.down, ""),
					"cancel":	(self.cancel, ""),
					"green": 	(self.keyGreen, ""),
					"red": 		(self.keyRed, ""),
					"blue":		(self.keyBlue, ""),
					"yellow":	(self.keyYellow, ""),
					"key_0":	(self.key0, ""),
				}, -2)
			
			self.onLayoutFinish.append(self.finishLayout)

		except:
			from traceback import format_exc
			log("Error:",format_exc() )
			try:
				open(getCrashFilePath(),"w").write(format_exc())
			except:
				pass

	def finishLayout(self):

		log("",self,"Finisch layout....")

		try:

			self["txt_green"].setText(_("Turn lights on"))
			self["txt_red"].setText(_("Lights off"))
			self["txt_blue"].setText(_("Switch to dynamic mode"))
			self["txt_yellow"].setText(_("Switch to moodlamp mode"))

			self["txt_check"].setText(_("Busy...."))

			self.mainMenuList = []

			self.mainMenuList.append((_("Settings"), "EL_Screen_Settings", "settingsEntry"))
			self.mainMenuList.append((_("Tuning"), "EL_Screen_Tuning", "tuningEntry"))
			self.mainMenuList.append((_("Moodlamp"), "EL_Screen_Moodlamp", "moodlampEntry"))
			self.mainMenuList.append((_("Config Editor"), "EL_Screen_ConfigEditor", "editorEntry"))
			self.mainMenuList.append((_("Box Info & About"), "EL_Screen_About", "aboutEntry"))
			self.mainMenuList.append((_("Help"), "EL_Screen_Help", "helpEntry"))

			# now that our mainMenuList is populated we set the list element
			self["menu"].setList(self.mainMenuList)

			# save the mainMenuList for later usage
			self.menu_main_list = self["menu"].list

			self.hideOnOff()
			self.controller.setScreen(self)

			self.refreshMenu()

			if not config.plugins.enigmalight.showstatusbar.getValue():			
				self["statusbar"].hide()
				self["txt_statusbar"].hide()
				self["txt_statusbar_info"].hide()			
			else:
				self["statusbar"].show()
				self["txt_statusbar"].show()
				self["txt_statusbar_info"].show()			
			
			log("",self,"Layout Finisched!")

		except:
			from traceback import format_exc
			log("Error:",format_exc() )
			try:
				open(getCrashFilePath(),"w").write(format_exc())
			except:
				pass

		#if config.plugins.enigmalight.checkForUpdateOnStartup.value and not self.controller.checkedForUpdates:
		#		EL_Screen_Check(self.session).checkForUpdate(self.controller)
		#		self.controller.setStatusBarInfo("Check for update...")
		#		self.controller.checkedForUpdates = True


	def okbuttonClick(self):
		log("",self)
		selection = self["menu"].getCurrent()
			
		if selection is not None:
			
			self.selectedEntry = selection[1]

			if type(self.selectedEntry) is str:

				self.controller.setMainScreen(None)

				log("",self,"Selected item %s" %(str(self.selectedEntry)))

				if selection[1] == "EL_Screen_Settings":
					self.currentScreen = self.session.openWithCallback(self.refreshMenu,EL_Screen_Settings)
					self.currentScreen.setController(self.controller)
					
				elif selection[1] == "EL_Screen_Tuning":
					self.currentScreen = self.session.openWithCallback(self.refreshMenu,EL_Screen_Tuning)
					self.currentScreen.setController(self.controller)

				elif selection[1] == "EL_Screen_Moodlamp":
					self.currentScreen = self.session.openWithCallback(self.refreshMenu,EL_Screen_Moodlamp)
					self.currentScreen.setController(self.controller)

				elif selection[1] == "EL_Screen_About":
					self.currentScreen = self.session.openWithCallback(self.refreshMenu,EL_Screen_About)
					self.currentScreen.setController(self.controller)

				elif selection[1] == "EL_Screen_ConfigEditor":
					self.currentScreen = self.session.open(EL_Screen_ConfigEditor)
					self.currentScreen.setController(self.controller)
					#showMessage(self.session,"Coming Soon! :)","I",6)

				elif selection[1] == "EL_Screen_Help":
					self.currentScreen = self.session.openWithCallback(self.refreshMenu,EL_Screen_Help)
					self.currentScreen.setController(self.controller)					

				self.controller.setScreen(self.currentScreen)

			else:
				pass

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

	def showButtons(self):
		#self.printWithThread("showButtons())")
		if self.controller != None:
			if self.controller.lightsEnabled == True:
				self["txt_check"].hide()					
				self["btn_green"].hide()
				self["txt_green"].hide()
				self["btn_red"].show()
				self["txt_red"].show()

				if self.controller.current_mode == "2" and self.controller.current_mode != None:
					self["btn_yellow"].show()
					self["txt_yellow"].show()
					self["btn_blue"].hide()
					self["txt_blue"].hide()
				elif self.controller.current_mode != "2" and self.controller.current_mode != None:
					self["btn_yellow"].hide()
					self["txt_yellow"].hide()
					self["btn_blue"].show()
					self["txt_blue"].show()

			if self.controller.lightsEnabled == False:
				#print "[EnigmaLight] ControlThread: lightsEnabled false..."
				self["txt_check"].hide()
				self["btn_red"].hide()
				self["txt_red"].hide()

				#switch buttons
				self["btn_blue"].hide()
				self["txt_blue"].hide()
				self["btn_yellow"].hide()
				self["txt_yellow"].hide()
				
				self["btn_green"].show()
				self["txt_green"].show()
		else:
			self["txt_check"].show()

			self["txt_check"].hide()
			self["btn_red"].hide()
			self["txt_red"].hide()

			#switch buttons
			self["btn_blue"].hide()
			self["txt_blue"].hide()
			self["btn_yellow"].hide()
			self["txt_yellow"].hide()
			
			self["btn_green"].hide()
			self["txt_green"].hide()

	def showStatusBar(self,value):
		if value:
			self["statusbar"].hide()
			self["txt_statusbar_info"].hide()
			self["txt_statusbar"].hide()
		else:
			self["statusbar"].show()
			self["txt_statusbar_info"].show()
			self["txt_statusbar"].show()

	#==========================================================================
	# 
	#==========================================================================
	def up(self):
		log("",self)
		self.left()

	#===========================================================================
	# 
	#===========================================================================
	def down(self):
		log("",self)
		self.right()

	#===============================================================================
	# 
	#===============================================================================
	def right(self):
		log("",self)
		try:
			self.refreshOrientationHorMenu(+1)
		except:
			from traceback import format_exc
			log("Error:",format_exc() )
			try:
				open(getCrashFilePath(),"w").write(format_exc())
			except:
				pass
		
	#===========================================================================
	# 
	#===========================================================================
	def left(self):
		log("",self)
		try:
			self.refreshOrientationHorMenu(-1)
		except:
			from traceback import format_exc
			log("Error:",format_exc() )
			try:
				open(getCrashFilePath(),"w").write(format_exc())
			except:
				pass
		
		
	#===========================================================================
	# 
	#===========================================================================
	def exit(self):
		log("",self," Main Exit..")
		
		self.controller.setSession(None) #Set background session
		self.controller.setScreen(None)
		self.controller.setMainScreen(None)
		self.currentScreen = None

		self.close((True,) )

	#===========================================================================
	# 
	#===========================================================================
	def cancel(self):
		log("",self)
		if self.nextExitIsQuit:
			self.exit()
		else:
			self["menu"].setList(self.menu_main_list)
			self.nextExitIsQuit = True

			self.refreshOrientationHorMenu(0)

	#===========================================================================
	# 
	#===========================================================================
	def keyGreen(self):
		#Enabled lights
		log("",self)
		#self.hideOnOff()
		self["txt_check"].hide()					
		self["btn_green"].hide()
		self["txt_green"].hide()
		self["btn_red"].show()
		self["txt_red"].show()
		self.controller.Control("start", "dynamic")
		
	#===========================================================================
	# 
	#===========================================================================
	def keyRed(self):
		#Disabled lights
		log("",self)
		#self.hideOnOff()

		self["btn_red"].hide()
		self["txt_red"].hide()

		#switch buttons
		self["btn_blue"].hide()
		self["txt_blue"].hide()
		self["btn_yellow"].hide()
		self["txt_yellow"].hide()
		
		self["btn_green"].show()
		self["txt_green"].show()

		self.controller.Control("grabber", "stop")		

		
		
	#===========================================================================
	# 
	#===========================================================================
	def keyBlue(self):
		log("",self)
		if self.controller.lightsEnabled:
			#self.hideOnOff()
			self["btn_yellow"].show()
			self["txt_yellow"].show()
			self["btn_blue"].hide()
			self["txt_blue"].hide()
								
			config.plugins.enigmalight.mode.setValue(2)
			config.plugins.enigmalight.mode.save()
			configfile.save()

			self.controller.Control("start", "dynamic")	
		else:
			showMessage(self.session,"Can't switch mode, Lights are disabled.","I",3)
		
	#===========================================================================
	# 
	#===========================================================================
	def keyYellow(self):
		log("",self)
		if self.controller.lightsEnabled:
			#self.hideOnOff()
			self["btn_yellow"].hide()
			self["txt_yellow"].hide()
			self["btn_blue"].show()
			self["txt_blue"].show()
			self.controller.Control("grabber", "moodlamp")
		
			config.plugins.enigmalight.mode.setValue(1)
			config.plugins.enigmalight.mode.save()
			configfile.save()
		else:
			showMessage(self.session,"Can't switch mode, Lights are disabled.","I",3)
		
	
	#===========================================================================
	# 
	#===========================================================================
	def refreshMenu(self, s = None):
		log("",self)
		self.refreshOrientationHorMenu(0)
		self.currentScreen = self
		self.controller.setScreen(self)
		self.controller.setMainScreen(True)

		self.controller.sendAll()
		self.controller.writeSettings()
		
	def key0(self):
		log("",self)
		self.hideOnOff()
		self.controller.killEnigmalight()

	def hideOnOff(self):
		log("",self)
		self["btn_green"].hide()
		self["txt_green"].hide()
		self["btn_red"].hide()
		self["txt_red"].hide()
		self["btn_blue"].hide()
		self["txt_blue"].hide()
		self["btn_yellow"].hide()
		self["txt_yellow"].hide()
		self["txt_check"].show()