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
from __init__ import getBoxInformation, getVersion, _ # _ is translation

from threading import currentThread
from EL_ThreadHelper import callOnMainThread

#===============================================================================
#
#===============================================================================		
class EL_Screen_About(Screen):
	_session = None

	#===========================================================================
	#
	#===========================================================================
	def __init__(self, session):
		try:
			Screen.__init__(self, session)
			
			self._session = session
			
			self["content"] = Label()
			self["content2"] = Label()

			self.controller = None

			self["statusbar"] = Pixmap()
			self["txt_statusbar"] = Label()
			self["txt_statusbar_info"] = Label()

			self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.keyCancel,
			}, -2)
			
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
		self.setTitle(_("About EnigmaLight / Box information"))

		self["content"].setText(self.getContentText())

		boxinfo = getBoxInformation()
		boxContent = "Brand:\r %s \nModel:\r %s\nChipset:\r %s\nArch:\r %s %s\n" %(str(boxinfo[0]),str(boxinfo[1]),str(boxinfo[2]),str(boxinfo[3]),str(boxinfo[4]))
		#boxContent = "BoxType:\r %s\nChipset:\r %s\nArch:\r %s %s\n" %(str(boxinfo[0]),str(boxinfo[1]),str(boxinfo[2]),str(boxinfo[3]))
		self["content2"].setText(boxContent)

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
	def keyCancel(self):
		self.close()
		
	#===========================================================================
	# 
	#===========================================================================
	def setController(self, controller):
		self.controller = controller
		self.controller.setSession(self.session)

	#===========================================================================
	# 
	#===========================================================================
	def getContentText(self):
		content = ""
		content += "EnigmaLight - Ambilight for Enigma2 \n\n" 
		content += "Version: \t" + getVersion() + "\n\n"
		content += "Autors: \t Speedy1985 and Oktay Oeztueter\n"
		content += "Translations: \t HolyMoly and Speedy1985 and Dimitrij\n"
		content += "Some GUI Code: \t DonDavici (c) 2012\n"
		content += "\n"
		content += "For support you can send me an email or use the chat function at http://www.enigmalight.net/\n\n"
		content += "If you like EnigmaLight and want support me, you can buy me a beer :-)"
		
		
		return content