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
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.config import config
from Components.Pixmap import Pixmap

from Screens.Screen import Screen

from __common__ import EnigmaLight_log as log
from __init__ import _ # _ is translation

from threading import currentThread
from EL_ThreadHelper import callOnMainThread
#===============================================================================
#
#===============================================================================		
class EL_Screen_Help(Screen):
	_session = None

	#===========================================================================
	#
	#===========================================================================
	def __init__(self, session):
		log("",self)
		Screen.__init__(self, session)
		
		self._session = session
		self.controller = None
		self["content"] = Label()

		self["statusbar"] = Pixmap()
		self["txt_statusbar"] = Label()
		self["txt_statusbar_info"] = Label()

		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"cancel": self.keyCancel,
		}, -2)
		
		self.onLayoutFinish.append(self.finishLayout)

	#===========================================================================
	# 
	#===========================================================================
	def finishLayout(self):
		log("",self)
		self.setTitle(_("Help"))

		self["content"].setText(self.getContentText())

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


	def setStatusBarInfo(self,text):
		self["txt_statusbar_info"].setText(text)

	def setStatusBarTxt(self,text):
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
		
	#===========================================================================
	# 
	#===========================================================================
	def keyCancel(self):
		log("",self)
		self.close()
		
	#===========================================================================
	# 
	#===========================================================================
	def getContentText(self):
		log("",self)
		content = ""
		content += "Q: I get only white color when i run EnigmaLight ?\n"
		content += "A: Try another version in settings, i gues a version with FPU.\n\n"

		content += "Q: Can i use the boblight.conf ?\n"
		content += "A: Yes you can use this, rename that file to enigmalight.conf.\n\n"

		content += "Q: Can i use the multiquickbutton plugin ? \n"
		content += "A: Yes for start and stop the lights\n\n"

		content += "Q: Enigmalight is freezed, what can i do ?\n"
		content += "A: In MainMenu press 0 to forcekill enigmalight.\n\n"

		content += "Q: How to get support ? \n"
		content += "A: Contact me over email info@enigmalight.net.\n\n"

		return content