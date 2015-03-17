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
import thread, os
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

from __common__ import EnigmaLight_log as log, showMessage, Clamp, getAspect
from __init__ import getCrashFilePath, getVersion, _ # _ is translation

from EL_PathSelector import EL_Screen_PathSelector

from threading import currentThread
from EL_ThreadHelper import callOnMainThread

#===============================================================================
#
#===============================================================================
class EL_Screen_Tuning(Screen, ConfigListScreen, HelpableScreen):

	_hasChanged = False
	_session = None
	skins = None
	
	def __init__(self, session):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		
		self.cfglist = []
		ConfigListScreen.__init__(self, self.cfglist, session, on_change = self._changed)
		
		self._session = session
		self._hasChanged = False
		self.version = getVersion()
		self.controller = None
		self.selected = None
		self.sampleUse = False
		self.aspect = getAspect()
		self.old_service = self.session.nav.getCurrentlyPlayingServiceReference()	
			
		self["txt_green"] = Label()
		self["btn_green"] = Pixmap()

		self["statusbar"] = Pixmap()
		self["txt_arrows"] = Label()
		self["txt_statusbar"] = Label()
		self["txt_statusbar_info"] = Label()

		self["version"] = StaticText()

		self["txt_green"].setText(_("Save"))
		self["txt_arrows"].setText(_("Use < > to jump with 10 in slider"))
		self["version"].text = self.version
		
		# Disable OSD Transparency
		try:
			self.can_osd_alpha = open("/proc/stb/video/alpha", "r") and True or False
		except:
			self.can_osd_alpha = False
		
		if config.plugins.enigmalight.sampleBackground.getValue() == True:
			self.showBackground()

		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "EL_Settings"],
		{
			"green": self.keySave,
			"cancel": self.exitTuning,
			"ok": self.ok,
			"left": self.keyLeft,
			"right": self.keyRight,
			"bouquet_up":	self.keyBouquetUp,
			"bouquet_down":	self.keyBouquetDown,
			"jumpNextMark":	self.keyNext,
			"jumpPreviousMark": self.keyPrev,
		}, -2)

		self.createSetup()
		
		log("",self,"Finisch layout..")

		#self["config"].onSelectionChanged.append(self.updateHelp)
		self.onLayoutFinish.append(self.finishLayout)
	#===========================================================================
	# 
	#===========================================================================
	def setController(self, controller):
		self.controller = controller
		self.controller.setSession(self.session)

	#===========================================================================
	# 
	#===========================================================================
	def finishLayout(self):
		self.setTitle(_("Tuning"))

		if config.plugins.enigmalight.showstatusbar.getValue():
			if config.plugins.enigmalight.showstatusbar_tuning.getValue():
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
	def createSetup(self):
		separator = "".ljust(120,"_")
		
		self.cfglist = []

		# COLOR SETTINGS
		self.cfglist.append(getConfigListEntry(_("[ Color Tuning ]") + separator, config.plugins.enigmalight.about, _(" ")))
		self.cfglist.append(getConfigListEntry(_('- Profile:'), config.plugins.enigmalight.presets, _("Profile: \nCreate your own profiles.")))
		#self.cfglist.append(getConfigListEntry(_('- Smoothing:'),config.plugins.enigmalight.interpolation, _("Smoothing: \nThis option will make the image smoother.")))
		self.cfglist.append(getConfigListEntry(_('- Led speed:'), config.plugins.enigmalight.speed,_("Led speed/fade​​: \nGeneral setting for the led-speed how fast is changing the colour. 40 is a nice setting.")))
		self.cfglist.append(getConfigListEntry(_('- Auto speed:'),config.plugins.enigmalight.autospeed, _(" ")))
		self.cfglist.append(getConfigListEntry(_('- Brightness:'),config.plugins.enigmalight.value, _("Brightness:\nThis is a nice option, especially even more important than the saturation setting. Why? Simply because there are colours like brown, turquoise, purple and eggplant that only exist with the clarity they have. Huh! Well, for example, a dark brown orange and dark turquoise aqua. So if you set the brightness to 2.0 then multiply the brightness of the colour you see with 2.0 (I think) and therefore can not show brown Ambilight. A nice value is 1.0 otherwise it quickly distorts the colours.")))
		self.cfglist.append(getConfigListEntry(_('- Minimal Brightness:\r'),config.plugins.enigmalight.valuemin, _(" Min 0.00 | Max 1.00 | Default 0.00")))
		self.cfglist.append(getConfigListEntry(_('- Maximal Brightness:\r'),config.plugins.enigmalight.valuemax, _(" Min 0.00 | Max 1.00 | Default 1.00")))
		self.cfglist.append(getConfigListEntry(_('- Saturation 0-20:'),config.plugins.enigmalight.saturation, _(" Saturation:\nSimply a strengthening of the average colour planes. The best option is between 1:00 and 1:20. This is because you are going to reinforce colours and this is so unnatural. \nExample:\n many films have a colour grading over it. A well-known example is a blue tint. This affects all the colours on the screen so that even a light Gray sky has some blue tones in it. When you try saturation on 2, it will thus be seen as good this blue tint twice while it appears white on your screen.")))
		self.cfglist.append(getConfigListEntry(_('- Minimal Saturation 0.00-1.00:\r'),config.plugins.enigmalight.saturationmin, _("Minimal Brightness:\nIf you set this as example to 0.01, then the LEDs will not completely dark is there is black but soft grey")))
		self.cfglist.append(getConfigListEntry(_('- Maximal Saturation 0.00-1.00:\r'),config.plugins.enigmalight.saturationmax, _(" ")))
		self.cfglist.append(getConfigListEntry(_('- Gamma correction 1-10:\r'),config.plugins.enigmalight.gamma, _("Gamma correction:\n Set this to 2.2 for default, since this is a default value for movies.")))
		self.cfglist.append(getConfigListEntry(_('- Threshold: \r') ,config.plugins.enigmalight.threshold, _("Threshold:\nFilter/Remove the almost dark pixels, 15 is a nice value.")))		
		

		self.cfglist.append(getConfigListEntry(_("[ Color Adjustment, only local ]") + separator, config.plugins.enigmalight.about, _(" ")))
		self.cfglist.append(getConfigListEntry(_('- Use ColorAdjust Settings:'), config.plugins.enigmalight.use_live_adjust))		

		if config.plugins.enigmalight.use_live_adjust.getValue() == str("true"):

			r = config.plugins.enigmalight.adjustr.getValue()
			g = config.plugins.enigmalight.adjustg.getValue()
			b = config.plugins.enigmalight.adjustb.getValue()
			
			#if config.plugins.enigmalight.color_order.value == "0":
			self.cfglist.append(getConfigListEntry(_('- Adjust RED\t%s')% str(r), config.plugins.enigmalight.adjustr))
			self.cfglist.append(getConfigListEntry(_('- Adjust GREEN\t%s')% str(g), config.plugins.enigmalight.adjustg))
			self.cfglist.append(getConfigListEntry(_('- Adjust BLUE\t%s')% str(b), config.plugins.enigmalight.adjustb))
			# elif config.plugins.enigmalight.color_order.value == "1":
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust BLUE  %s\t   ')% str(r), config.plugins.enigmalight.adjustr))
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust GREEN %s\t   ')% str(g), config.plugins.enigmalight.adjustg))
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust RED   %s\t   ')% str(b), config.plugins.enigmalight.adjustb))
			# elif config.plugins.enigmalight.color_order.value == "2":
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust GREEN %s\t   ')% str(r), config.plugins.enigmalight.adjustr))
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust BLUE  %s\t   ')% str(g), config.plugins.enigmalight.adjustg))
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust RED   %s\t   ')% str(b), config.plugins.enigmalight.adjustb))
			# elif config.plugins.enigmalight.color_order.value == "3":
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust GREEN %s\t   ')% str(r), config.plugins.enigmalight.adjustr))
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust RED  %s\t   ')% str(g), config.plugins.enigmalight.adjustg))
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust BLUE   %s\t   ')% str(b), config.plugins.enigmalight.adjustb))
			# elif config.plugins.enigmalight.color_order.value == "4":
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust BLUE %s\t   ')% str(r), config.plugins.enigmalight.adjustr))
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust RED  %s\t   ')% str(g), config.plugins.enigmalight.adjustg))
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust GREEN   %s\t   ')% str(b), config.plugins.enigmalight.adjustb))
			# elif config.plugins.enigmalight.color_order.value == "5":
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust RED %s\t   ')% str(r), config.plugins.enigmalight.adjustr))
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust BLUE  %s\t   ')% str(g), config.plugins.enigmalight.adjustg))
			# 	self.cfglist.append(getConfigListEntry(_('- Adjust GREEN   %s\t   ')% str(b), config.plugins.enigmalight.adjustb))

		self.cfglist.append(getConfigListEntry(_('- Show sample pictures:'), config.plugins.enigmalight.sampleBackground))
		if config.plugins.enigmalight.sampleBackground.getValue() == True:
			self.cfglist.append(getConfigListEntry(_('- Sample picture:'), config.plugins.enigmalight.sampleBackground_mvi))

		self.cfglist.append(getConfigListEntry(_("[ Blackbar detection]") + separator, config.plugins.enigmalight.about, _(" ")))
		self.cfglist.append(getConfigListEntry(_('- Remove Blackbars top and bottom:\r'),config.plugins.enigmalight.blackbar_h, _("Remove horizontal blackbars from lights.")))
		self.cfglist.append(getConfigListEntry(_('- Remove Blackbars left and right:\r'),config.plugins.enigmalight.blackbar_v, _("Remove vertical blackbars from lights.")))
		self.cfglist.append(getConfigListEntry(_('- Delay before remove:\r'), config.plugins.enigmalight.blackbar_f, _("Count from 0 to given number\nif the blackbars are still there then remove them.")))
		
		self["config"].list = self.cfglist
		
		self.selected = self["config"].getCurrent()[1]
		
		#save profile

		if self.selected == config.plugins.enigmalight.presets:
			self.getCustom(config.plugins.enigmalight.presets.getValue());
			
	#===========================================================================
	# 
	#===========================================================================

	def getCustom(self,profilenr):
		try:
			log("",self)
			fo = open("/usr/lib/enigma2/python/Plugins/Extensions/EnigmaLight/profiles/custom_%s.profile" %(str(profilenr)), "r")
			customsettings = fo.read(256)
			fo.close()
			
			customsettings = customsettings.split("|")
			config.plugins.enigmalight.saturation.setValue(customsettings[0])
			config.plugins.enigmalight.value.setValue(customsettings[1])
			config.plugins.enigmalight.speed.setValue(customsettings[2])
			config.plugins.enigmalight.valuemax.setValue(customsettings[3])
			config.plugins.enigmalight.valuemin.setValue(customsettings[4])
			config.plugins.enigmalight.saturationmin.setValue(customsettings[5])
			config.plugins.enigmalight.saturationmax.setValue(customsettings[6])
			config.plugins.enigmalight.gamma.setValue(customsettings[7])
			config.plugins.enigmalight.threshold.setValue(customsettings[8])
			config.plugins.enigmalight.autospeed.setValue(customsettings[9])

			if self.controller.lightsEnabled:
				self.controller.writeSettings()

		except:
			from traceback import format_exc
			log("Error: " + format_exc(),self)
			try:
				open(getCrashFilePath(),"w").write(format_exc())
				showMessage(self._session,_("Can't get settings from profile...", "W", timeout = 10))
			except:
				pass
			
	
	#===========================================================================
	# 
	#===========================================================================

	def saveCustom(self,profilenr):
		try:
			log("",self)
			fo = open("/usr/lib/enigma2/python/Plugins/Extensions/EnigmaLight/profiles/custom_%s.profile" %(str(profilenr)), "wb")
			fo.write(str(config.plugins.enigmalight.saturation.value)+"|")
			fo.write(str(config.plugins.enigmalight.value.value)+"|")
			fo.write(str(config.plugins.enigmalight.speed.value)+"|")
			fo.write(str(config.plugins.enigmalight.valuemax.value)+"|")
			fo.write(str(config.plugins.enigmalight.valuemin.value)+"|")
			fo.write(str(config.plugins.enigmalight.saturationmin.value)+"|")
			fo.write(str(config.plugins.enigmalight.saturationmax.value)+"|")
			fo.write(str(config.plugins.enigmalight.gamma.value)+"|")
			fo.write(str(config.plugins.enigmalight.threshold.value)+"|")
			fo.write(str(config.plugins.enigmalight.autospeed.value))

			fo.close();
			
		except:
			from traceback import format_exc
			log("Error:" +format_exc(),self)
			try:
				open(getCrashFilePath(),"w").write(format_exc())
				showMessage(self._session,_("Can't write settings to profile...", "W", timeout = 10))
			except:
				pass

	#===========================================================================
	# 
	#===========================================================================

	def _changed(self):			
		self._hasChanged = True

		self.selected = self["config"].getCurrent()[1]

		#save profile
		if self.selected != config.plugins.enigmalight.presets:
			self.saveCustom(config.plugins.enigmalight.presets.getValue())

		#get profile
		if self.selected == config.plugins.enigmalight.presets:
			self.getCustom(config.plugins.enigmalight.presets.getValue());
		
			#refresch
			self.createSetup()

		if self.selected is config.plugins.enigmalight.sampleBackground or self.selected is config.plugins.enigmalight.sampleBackground_mvi:
			if config.plugins.enigmalight.sampleBackground.getValue() is True:
				self.showBackground()
				self.sampleUse = True
			else:
				self.showOldService()
				self.sampleUse = False

			self.createSetup()

		self.controller.changeValue(self.selected)
	
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
		self.sampleUse = False

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
		
		self.sampleUse = True
		### END TEST ###

	#===========================================================================
	# 
	#===========================================================================
	def ok(self):
		cur = self["config"].getCurrent()
		
	#===========================================================================
	# 
	#===========================================================================
	def keySave(self):
		self.saveAll()
		self.exitTuning()

	#===========================================================================
	# 
	#===========================================================================
	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.selected = self["config"].getCurrent()[1]
		if self.selected is config.plugins.enigmalight.use_live_adjust or self.selected is config.plugins.enigmalight.adjustr or self.selected is config.plugins.enigmalight.adjustg or self.selected is config.plugins.enigmalight.adjustb or self.selected is config.plugins.enigmalight.color_order:
			self.createSetup()
		
	#===========================================================================
	# 
	#===========================================================================
	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.selected = self["config"].getCurrent()[1]
		if self.selected is config.plugins.enigmalight.use_live_adjust or self.selected is config.plugins.enigmalight.adjustr or self.selected is config.plugins.enigmalight.adjustg or self.selected is config.plugins.enigmalight.adjustb or self.selected is config.plugins.enigmalight.color_order:
			self.createSetup()

	#===========================================================================
	# 
	#===========================================================================
	def keyBouquetUp(self):
		self["config"].instance.moveSelection(self["config"].instance.pageUp)
		
		
	#===========================================================================
	# 
	#===========================================================================
	def keyBouquetDown(self):
		self["config"].instance.moveSelection(self["config"].instance.pageDown)

	#===========================================================================
	# 
	#===========================================================================
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

	#===========================================================================
	# 
	#===========================================================================
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

	def exitTuning(self):

		if self.sampleUse:
			self.showOldService()
		self.close(None)