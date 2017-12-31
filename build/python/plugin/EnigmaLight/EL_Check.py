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
import sys
import time

from os import system, popen
from Screens.Standby import TryQuitMainloop

from enigma import eConsoleAppContainer

from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.config import config
from Components.Label import Label

from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Console import Console as SConsole

from __common__ import showMessage, getBoxArch, EnigmaLight_log as log, testInetConnectivity

from . import _
from __init__ import getCrashFilePath, getVersion, _ # _ is translation

import urllib2
# Unfortunaly not everyone has twisted installed ...
try:
	from twisted.web.microdom import parseString
except Exception, e:
	print("import twisted.web.microdom failed")

#===============================================================================
#
#===============================================================================
class EL_Screen_Check(object):

	oeVersion = None
	check = None
	latestVersion = None

	def __init__(self, session):
		log("",self)
		#Screen.__init__(self, session)
		self.session = session
		self.controller = None
		self.oeVersion = getBoxArch()

	def checkForUpdate(self,controller):
		
		self.controller = controller

		log("",self,"Check for update....")

		self.controller.setStatusBarInfo(_("Check for update.."))

		if testInetConnectivity():
			self.url = config.plugins.enigmalight.url.value + config.plugins.enigmalight.updatexml.value
			log("",self,"Checking URL: " + self.url) 
			try:
				f = urllib2.urlopen(self.url)
				html = f.read()
				dom = parseString(html)
				update = dom.getElementsByTagName("update")[0]
				version = update.getElementsByTagName("version")[0]

				remoteversion = version.childNodes[0].data
				urls = update.getElementsByTagName("url")

				currentversion = getVersion()
				currentbeta = currentversion[-2:]
				remotebeta = remoteversion[-2:]

				self.remoteurl = ""
				for url in urls:
					self.remoteurl = url.childNodes[0].data

				#print("""Version: %s - URL: %s""" % (remoteversion, self.remoteurl))
				if currentbeta < remotebeta:
					self.latestVersion = remoteversion
					self.controller.setStatusBarInfo(_("New update available !!"))
					#if self.session != None:
					self.session.openWithCallback(self.startUpdate, MessageBox,_("Your current Version is ") + str(currentversion) + _("\nUpdate to ") + str(remoteversion) + _(" found!\n\nDo you want to update now?"), MessageBox.TYPE_YESNO)
				else:
					self.controller.setStatusBarInfo(_("No update available.."))
					#if self.session != None:
					showMessage(self.session, _("No update available.."), "I")
			except:
				from traceback import format_exc
				log("",self,"Error: " +format_exc())
				try:
					log("",self,"Could not download HTTP Page")
					open(getCrashFilePath(),"w").write(format_exc())
				except:
					pass
				
		else:
			self.controller.setStatusBarInfo(_("No Internetconnection.."))
			self.session.openWithCallback(self.close, MessageBox,_("No internet connection available or curl is not installed!"), MessageBox.TYPE_INFO)


	def startUpdate(self, answer):
		if answer is True:
			self.updateToLatestVersion()

	def startPluginUpdate(self):
		self.container=eConsoleAppContainer()
		self.container.appClosed.append(self.finishupdate)
		self.container.execute()

	#===========================================================================
	#
	#===========================================================================
	def updateToLatestVersion(self):
		remoteUrl = "http://enigmalight.net/updates/enigma2-plugin-extensions-enigmalight_" + str(self.latestVersion) + "_all.ipk"

		cmd = "opkg install --force-overwrite --force-depends " + str(remoteUrl)

		log("",self,"remoteUrl: " + str(remoteUrl))
		log("",self,"cmd: " + str(cmd))

		self.session.open(SConsole,"Executing command:", [cmd] , self.finishupdate)

	#===========================================================================
	#
	#===========================================================================
	def finishupdate(self):
		time.sleep(2)
		self.session.openWithCallback(self.e2restart, MessageBox,_("Enigma2 must be restarted!\nShould Enigma2 now restart?"), MessageBox.TYPE_YESNO)

	#===========================================================================
	#
	#===========================================================================
	def e2restart(self, answer):
		if answer is True:
			try:
				self.session.open(TryQuitMainloop, 3)
			except Exception, ex:
				log("",self,"Error: Exception -> " + str(ex))
				data = "TryQuitMainLoop is not implemented in your OS.\n Please restart your box manually."
				self.session.open(MessageBox, _("Information:\n") + data, MessageBox.TYPE_INFO)