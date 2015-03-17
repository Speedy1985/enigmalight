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
import os
from Screens.Screen import Screen
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap

from Components.FileList import FileList
from Components.Label import Label

from EL_ViewFactory import getGuiElements

from __common__ import EnigmaLight_log as log
from __init__ import _ # _ is translation

#===========================================================================
# 
#===========================================================================
class EL_Screen_PathSelector(Screen):

	#===========================================================================
	# 
	#===========================================================================
	def __init__(self, session, initDir, myType, title):
		Screen.__init__(self, session)

		self.guiElements = getGuiElements()

		self.myType = myType
		self.title = title

		if not os.path.exists(initDir):
			initDir = "/etc/"
		
		self.filelist = FileList("/dev/", showDirectories = True, showFiles = True, showMountpoints = True, isTop = False, matchingPattern = "")
		self["filelist"] = self.filelist

		#self["filelist"]  = FileList(initDir, showDirectories = True, showFiles = True, showMountpoints = False, isTop = True, matchingPattern = "^.*\.(conf|config)")
		self["filelist"].changeDir(initDir.rsplit('/', 1)[0] + "/", select = initDir.rsplit('/', 1)[1])
		self["help"] = Label()
		self["help"].setText(initDir)
		self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "EPGSelectActions"],
		{
			"back": self.cancel,
			"left": self.left,
			"right": self.right,
			"up": self.up,
			"down": self.down,
			"ok": self.ok,
			"green": self.green,
			"red": self.cancel
			
		}, -1)

		self["btn_red"]			= Pixmap()
		self["btn_redText"]		= Label()

		self["btn_green"]		= Pixmap()
		self["btn_greenText"]   = Label()

		self.onLayoutFinish.append(self.finishLayout)

	#===========================================================================
	#
	#===========================================================================
	def finishLayout(self):
		self["btn_red"].instance.setPixmapFromFile(self.guiElements["key_red"])
		self["btn_redText"].setText(_("Cancel"))

		self["btn_green"].instance.setPixmapFromFile(self.guiElements["key_green"])
		self["btn_greenText"].setText(_("Ok"))

		self.setTitle(_(self.title))

	#===========================================================================
	# 
	#===========================================================================
	def cancel(self):
		self.close(None, self.myType)
		
	#===========================================================================
	# 
	#===========================================================================
	def green(self):
		self.close(str(self["filelist"].getCurrentDirectory()) + str(self["filelist"].getSelection()[0]), self.myType)

	#===========================================================================
	# 
	#===========================================================================
	def up(self):
		self["filelist"].up()
		self.updateTarget()
		
	#===========================================================================
	# 
	#===========================================================================
	def down(self):
		self["filelist"].down()
		self.updateTarget()
		
	#===========================================================================
	# 
	#===========================================================================
	def left(self):
		self["filelist"].pageUp()
		self.updateTarget()
		
	#===========================================================================
	# 
	#===========================================================================
	def right(self):
		self["filelist"].pageDown()
		self.updateTarget()

	#===========================================================================
	# 
	#===========================================================================
	def ok(self):
		if self["filelist"].canDescent():
			self["filelist"].descent()
			self.updateTarget()
	
	#===========================================================================
	# 
	#===========================================================================
	def updateTarget(self):
		currFolder = str(self["filelist"].getCurrentDirectory())
		currFile = str(self.filelist.getCurrentDirectory()) + str(self.filelist.getFilename())
		if currFolder is not None:
			self["help"].setText(_("Selected file: %s") %(currFile))
		else:
			self["help"].setText(_("Invalid Location"))
			
		