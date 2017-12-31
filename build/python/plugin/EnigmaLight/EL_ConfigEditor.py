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

from Screens.Screen import Screen
from __common__ import checkSymbolic, EnigmaLight_log as log, showMessage, showError
from __plugin__ import Plugin
from __init__ import getCrashFilePath, _ # _ is translation

from EL_PathSelector import EL_Screen_PathSelector

from threading import currentThread
from EL_ThreadHelper import callOnMainThread

#===============================================================================
#
#===============================================================================
class EL_Screen_ConfigEditor(Screen, ConfigListScreen):
	_session = None

	#===========================================================================
	#
	#===========================================================================
	def __init__(self, session):
		try:
			Screen.__init__(self, session)
			self.cfglist = []
			ConfigListScreen.__init__(self, self.cfglist, session, on_change = self.changedEntry)
			self._session = session
			self.controller = None
			#globals
			self.createfile = False
			self.controller = None
			self.devicepath = None
			self.begin = None
			self.floor = None
			self.seqq = None
			self.leds_top = None
			self.leds_right = None
			self.leds_left = None
			self.leds_bottom = None
			self.leds_bottom_left = None
			self.leds_bottom_right = None
			self.leds_bottom_center = None
			self.channels = None
			self.total = None
			self.current = None
			self.selected = None

			self["infoblock"] = Label()
			self["btn_greenText"] = Label()
			self["btn_yellowText"] = Label()

			self["btn_yellow"] = Pixmap()
			self["btn_green"] = Pixmap()
			self["pic_leftb"] = Pixmap()
			self["pic_leftt"] = Pixmap()
			self["pic_topl"] = Pixmap()
			self["pic_topr"] = Pixmap()
			self["pic_rightt"] = Pixmap()
			self["pic_rightb"] = Pixmap()
			self["pic_botr"] = Pixmap()
			self["pic_botml"] = Pixmap()
			self["pic_botmr"] = Pixmap()
			self["pic_botl"] = Pixmap()
			self["pic_floor"] = Pixmap()

			self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel":	self.keyCancel,
				"green":	self.keyGreen,
				"yellow":	self.keyYellow,
				"ok":		self.keyOk,
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
		self.setTitle(_("EnigmaLight ConfigEditor"))

		self["pic_leftb"].hide()
		self["pic_leftt"].hide()
		self["pic_topl"].hide()
		self["pic_topr"].hide()
		self["pic_rightt"].hide()
		self["pic_rightb"].hide()
		self["pic_botr"].hide()
		self["pic_botml"].hide()
		self["pic_botmr"].hide()
		self["pic_botl"].hide()
		self["pic_floor"].hide()

		self["infoblock"].setText(_("Infoblock, blablablabla"))
		self["btn_greenText"].setText(_("Create configfile"))
		self["btn_yellowText"].setText(_("Create and Test this config with [RGB Test]"))

		self.createSetup()
		self.setTv()

		if self.current != None:
			self.current.show()
	#==========================================================================
	# Functions for use from others thread
	#==========================================================================	
	def handleFromThread(self,func,*args):
		if args:
			callOnMainThread(func,args[0])
		else:
			callOnMainThread(func)

	def setStatusBarInfo(self,text):
		pass
	def setStatusBarTxt(self,text):
		pass

	#===========================================================================
	# 
	#===========================================================================
	def createSetup(self):
		separator = "".ljust(120,"_")

		self.cfglist = []

		# COLOR SETTINGS
		self.cfglist.append(getConfigListEntry(_("[ Device ]") , config.plugins.enigmalight.about, _(" ")))
		self.cfglist.append(getConfigListEntry(_('- Device type:'), config.plugins.enigmalight.type))

		if config.plugins.enigmalight.type.value != "WifiLight": 
			if config.plugins.enigmalight.type.value == "Lightpack1":
				self.cfglist.append(getConfigListEntry(_('- Bus:'), config.plugins.enigmalight.bus))
				self.cfglist.append(getConfigListEntry(_('- Address:'), config.plugins.enigmalight.laddress))
			elif config.plugins.enigmalight.type.value == "Lightpack2":
				self.cfglist.append(getConfigListEntry(_('- Serial:'), config.plugins.enigmalight.serial))
			else:
				self.devicepath = getConfigListEntry(_('- Device output:'), config.plugins.enigmalight.output)
				self.cfglist.append(self.devicepath)
				self.cfglist.append(getConfigListEntry(_('- Device rate:'), config.plugins.enigmalight.rate))

			if config.plugins.enigmalight.type.value == "Ambioder":
				self.cfglist.append(getConfigListEntry(_('- Ambioder precision:'), config.plugins.enigmalight.precision))
			else:
				self.cfglist.append(getConfigListEntry(_("[ Lights ]") , config.plugins.enigmalight.about, _(" ")))
				self.cfglist.append(getConfigListEntry(_('- With (floor) stand:'), config.plugins.enigmalight.floorstand))
				if config.plugins.enigmalight.floorstand.value == str(2):
					self.cfglist.append(getConfigListEntry(_('-- How many lights Bottom-left:'), config.plugins.enigmalight.lights_bottom_left))
					self.cfglist.append(getConfigListEntry(_('-- Bottom center (how many places are empty):'), config.plugins.enigmalight.lights_bottom_center))
					self.cfglist.append(getConfigListEntry(_('-- How many lights Bottom-right:'), config.plugins.enigmalight.lights_bottom_right))
				else:
					self.cfglist.append(getConfigListEntry(_('- How many lights Bottom:'), config.plugins.enigmalight.lights_bottom))

				self.cfglist.append(getConfigListEntry(_('- How many lights Top:'), config.plugins.enigmalight.lights_top))
				self.cfglist.append(getConfigListEntry(_('- How many lights Left:'), config.plugins.enigmalight.lights_left))
				self.cfglist.append(getConfigListEntry(_('- How many lights Right:'), config.plugins.enigmalight.lights_right))

				if config.plugins.enigmalight.clockwise.value is str(1):
					self.cfglist.append(getConfigListEntry(_('- Where starts led 1:'), config.plugins.enigmalight.begincount_cw))
				elif config.plugins.enigmalight.clockwise.value is str(2):
					self.cfglist.append(getConfigListEntry(_('- Where starts led 1:'), config.plugins.enigmalight.begincount_bw))

				self.cfglist.append(getConfigListEntry(_('- Clockwise or Backwards:'), config.plugins.enigmalight.clockwise))
				self.cfglist.append(getConfigListEntry(_('- Scan depth Left:'), config.plugins.enigmalight.scanl))
				self.cfglist.append(getConfigListEntry(_('- Scan depth Right:'), config.plugins.enigmalight.scanr))
				self.cfglist.append(getConfigListEntry(_('- Scan depth Top:'), config.plugins.enigmalight.scant))
				self.cfglist.append(getConfigListEntry(_('- Scan depth Bottom:'), config.plugins.enigmalight.scanb)) 
		else:
			self.cfglist.append(getConfigListEntry(_("[ WifiLight ]") , config.plugins.enigmalight.about, _(" ")))
			self.cfglist.append(getConfigListEntry(_('- WifiLight IP:'), config.plugins.enigmalight.wifilight_ip))
			self.cfglist.append(getConfigListEntry(_('- WifiLight PORT:'), config.plugins.enigmalight.wifilight_port)) 

		self.cfglist.append(getConfigListEntry(_("[ Color ]") , config.plugins.enigmalight.about, _(" ")))
		self.cfglist.append(getConfigListEntry(_('- Color order:'), config.plugins.enigmalight.color_order))
		self.cfglist.append(getConfigListEntry(_('- Red Adjust:'), config.plugins.enigmalight.config_r_adjust))
		self.cfglist.append(getConfigListEntry(_('- Red Gamma:'), config.plugins.enigmalight.config_r_gamma))
		self.cfglist.append(getConfigListEntry(_('- Red Blacklevel:'), config.plugins.enigmalight.config_r_blacklevel))
		self.cfglist.append(getConfigListEntry(_('- Green Adjust:'), config.plugins.enigmalight.config_g_adjust))
		self.cfglist.append(getConfigListEntry(_('- Green Gamma:'), config.plugins.enigmalight.config_g_gamma))
		self.cfglist.append(getConfigListEntry(_('- Green Blacklevel:'), config.plugins.enigmalight.config_g_blacklevel))
		self.cfglist.append(getConfigListEntry(_('- Blue Adjust:'), config.plugins.enigmalight.config_b_adjust))
		self.cfglist.append(getConfigListEntry(_('- Blue Gamma:'), config.plugins.enigmalight.config_b_gamma))
		self.cfglist.append(getConfigListEntry(_('- Blue Blacklevel:'), config.plugins.enigmalight.config_b_blacklevel))

		self["config"].list = self.cfglist
		
		self.selected = self["config"].getCurrent()[1]

	def setTv(self):

		self.begin = None

		if config.plugins.enigmalight.clockwise.value is str(1):
			self.begin = config.plugins.enigmalight.begincount_cw.value
		elif config.plugins.enigmalight.clockwise.value is str(2):
			self.begin = config.plugins.enigmalight.begincount_bw.value

		self.floor = config.plugins.enigmalight.floorstand.value
		self.seqq  = config.plugins.enigmalight.clockwise.value
		self.leds_top = config.plugins.enigmalight.lights_top.value
		self.leds_right = config.plugins.enigmalight.lights_right.value
		self.leds_left = config.plugins.enigmalight.lights_left.value
		self.leds_bottom = config.plugins.enigmalight.lights_bottom.value
		self.leds_bottom_center = config.plugins.enigmalight.lights_bottom_center.value

		if config.plugins.enigmalight.type.value == "WifiLight":
			self.leds_top = 1


		if self.floor == str(2):
			self.leds_bottom_left = config.plugins.enigmalight.lights_bottom_left.value
			self.leds_bottom_right = config.plugins.enigmalight.lights_bottom_right.value
		elif self.floor == str(1):
			self.leds_bottom_left = 0
			self.leds_bottom_right = 0

		self.total = self.leds_top + self.leds_right + self.leds_left + self.leds_bottom + self.leds_bottom_left + self.leds_bottom_right
		self.channels = (self.total)*3

		if self.begin == "left-bottom":
			if self.current != None:
				self.current.hide()
				self["pic_leftb"].show()
			self.current = self["pic_leftb"]
		elif self.begin == "left-top":
			if self.current != None:
				self.current.hide()
				self["pic_leftt"].show()
			self.current = self["pic_leftt"]
		elif self.begin == "top-right":
			if self.current != None:
				self.current.hide()
				self["pic_topr"].show()
			self.current = self["pic_topr"]
		elif self.begin == "top-left":
			if self.current != None:
				self.current.hide()
				self["pic_topl"].show()
			self.current = self["pic_topl"]
		elif self.begin == "right-top":
			if self.current != None:
				self.current.hide()
				self["pic_rightt"].show()
			self.current = self["pic_rightt"]
		elif self.begin == "right-bottom":
			if self.current != None:
				self.current.hide()
				self["pic_rightb"].show()
			self.current = self["pic_rightb"]
		elif self.begin == "bottom-left":
			if self.current != None:
				self.current.hide()
				self["pic_botl"].show()
			self.current = self["pic_botl"]
		elif self.begin == "bottom-right":
			if self.current != None:
				self.current.hide()
				self["pic_botr"].show()
			self.current = self["pic_botr"]
		elif self.begin == "bottom-middle-left":
			if self.current != None:
				self.current.hide()
				self["pic_botml"].show()
			self.current = self["pic_botml"]
		elif self.begin == "bottom-middle-right":
			if self.current != None:
				self.current.hide()
				self["pic_botmr"].show()
			self.current = self["pic_botmr"]

		if self.floor == str(2):
			self["pic_floor"].show()
		elif self.floor == str(1):
			self["pic_floor"].hide()

		if self.seqq == str(1):
			seq = "clockwise"
		else:
			seq = "backwards"

		self["infoblock"].setText("Leds: %s | Channels %s" %(str(self.total),str(self.channels)))

	def changedEntry(self):
		if self["config"].getCurrent() and self["config"].getCurrent()[1] == config.plugins.enigmalight.type:

			config.plugins.enigmalight.threadpriority.setValue(1)
			output = "/dev/ttyUSB0"
			if os.path.exists("/dev/ttyACM0"):
				output = "/dev/ttyACM0"
			if config.plugins.enigmalight.type.value == "Oktolight":
				config.plugins.enigmalight.rate.setValue(57600)
				config.plugins.enigmalight.color_order.setValue("1")
				config.plugins.enigmalight.output.setValue("/dev/ttyUSB0")
			elif config.plugins.enigmalight.type.value == "Karatelight":
				config.plugins.enigmalight.rate.setValue(57600)
				config.plugins.enigmalight.color_order.setValue("2")
				config.plugins.enigmalight.output.setValue(output)
			elif config.plugins.enigmalight.type.value == "Atmolight":
				config.plugins.enigmalight.rate.setValue(38400)
				config.plugins.enigmalight.color_order.setValue("0")
				config.plugins.enigmalight.output.setValue("/dev/ttyUSB0")
			elif config.plugins.enigmalight.type.value == "Adalight/Momo":
				config.plugins.enigmalight.rate.setValue(115200)
				config.plugins.enigmalight.color_order.setValue("0")
				config.plugins.enigmalight.threadpriority.setValue(99)
				config.plugins.enigmalight.output.setValue(output)
			elif config.plugins.enigmalight.type.value == "Sedulight 5A A0 A5":
				config.plugins.enigmalight.rate.setValue(500000)
				config.plugins.enigmalight.output.setValue("/dev/ttyUSB0")
			elif config.plugins.enigmalight.type.value == "Sedulight 5A A1 A5":
				config.plugins.enigmalight.rate.setValue(500000)
				config.plugins.enigmalight.output.setValue("/dev/ttyUSB0")
			elif config.plugins.enigmalight.type.value == "Sedulight 5A A2 A5":
				config.plugins.enigmalight.rate.setValue(500000)
				config.plugins.enigmalight.output.setValue("/dev/ttyUSB0")
			elif config.plugins.enigmalight.type.value == "Sedulight 5A B0 A5":
				config.plugins.enigmalight.rate.setValue(500000)
				config.plugins.enigmalight.output.setValue("/dev/ttyUSB0")
			elif config.plugins.enigmalight.type.value == "iBelight":
				config.plugins.enigmalight.output.setValue("/dev/usb/hiddev0")
			elif config.plugins.enigmalight.type.value == "Ambioder":
				config.plugins.enigmalight.output.setValue("/dev/ttyUSB0")
			elif config.plugins.enigmalight.type.value == "WifiLight":
				config.plugins.enigmalight.output.setValue("/home/elight-addons/wifilight/wifilight.py")
				config.plugins.enigmalight.lights_left.setValue(0)
				config.plugins.enigmalight.lights_top.setValue(0)
				config.plugins.enigmalight.lights_right.setValue(0)
				config.plugins.enigmalight.lights_bottom.setValue(0)
				config.plugins.enigmalight.lights_bottom_right.setValue(0)
				config.plugins.enigmalight.lights_bottom_left.setValue(0)
				config.plugins.enigmalight.lights_bottom_center.setValue(0)
				config.plugins.enigmalight.scanl.setValue(10)
				config.plugins.enigmalight.scanr.setValue(10)
				config.plugins.enigmalight.scant.setValue(10)
				config.plugins.enigmalight.scanb.setValue(10)
                					 
		self.setTv()

		self.save()
		self.createSetup()
		self["config"].setList(self.cfglist)

	def save(self):
		self.saveAll()

	#===========================================================================
	# 
	#===========================================================================
	def keyOk(self):
		cur = self["config"].getCurrent()

		if cur == self.devicepath:
			self.session.openWithCallback(self.SavePath,EL_Screen_PathSelector,self.devicepath[1].value, "devicepath", "Select devicepath")

	#===========================================================================
	# 
	#===========================================================================
	def SavePath(self, pathValue, myType):
		log("",self)
		log("",self,"pathValue: " + str(pathValue))
		log("",self,"type: " + str(myType))
		if pathValue is not None:

			if myType == "devicepath":
				self.devicepath[1].value = pathValue

	def keyGreen(self):
		self.save()
		self.createfile = True
		self.test = False
		self.BuildConfig(True)

	def keyYellow(self):
		self.save()
		self.createfile = True
		self.test = True
		self.BuildConfig(False) #start and give no message after complete

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
	#	Build configfile
	#===========================================================================
	def BuildConfig(self,message):
		prefix  = ""

		if self.createfile:
			postfix = ""
			type = ""
			blacklevel = str(config.plugins.enigmalight.blacklevel.value[0])+"."+str(config.plugins.enigmalight.blacklevel.value[1])
			interval= "interval 20000\n"
			delayafteropen  = ""

		#
		# Set sections and depth
		#

		leds_bottom = config.plugins.enigmalight.lights_bottom.value
		leds_top = config.plugins.enigmalight.lights_top.value
		leds_left = config.plugins.enigmalight.lights_left.value
		leds_right = config.plugins.enigmalight.lights_right.value
		scanl = config.plugins.enigmalight.scanl.value
		scanr = config.plugins.enigmalight.scanr.value
		scant = config.plugins.enigmalight.scant.value
		scanb = config.plugins.enigmalight.scanb.value

		#
		# Bottom values, for tv's with floorstand.
		#

		leds_bottom_center = config.plugins.enigmalight.lights_bottom_center.value
		leds_bottom_left = config.plugins.enigmalight.lights_bottom_left.value
		leds_bottom_right = config.plugins.enigmalight.lights_bottom_right.value
		leds_bottom_total = (leds_bottom_left + leds_bottom_right + leds_bottom_center)

		#
		# Total channels
		#

		channels = (leds_top + leds_left + leds_right + leds_bottom)*3

		#
		# Floorstand calculation
		#

		if config.plugins.enigmalight.floorstand.value == str(2):
			#print("[Boblight] Clockwise")
			#print("[Boblight] Set floorstand to true")

			channels = (leds_top + leds_left + leds_right + leds_bottom_total - leds_bottom_center)*3
			#print("[Boblight] Channels: "+str(channels))
 
			# total step
			hScanStep = 100.0 / leds_bottom_total; # 100 / 20 lights = 5
			hScan_center = (hScanStep*leds_bottom_center) # total center hscan // floorstand //  emptyplaces*hScanStep = ... 50
			hScan_right  = (hScanStep*leds_bottom_right) # total right hscan /// light rights*hScanStep = ... 25
 
			hScanCurrent = 0.0 + (hScan_center - hScan_right); # 25 
 
			hScanBottom_left  = hScanCurrent; # = 25 is plus
			hScanBottom_right = 100.0 # = 25 + 50 = 75 is min

			# debug
			#print("[Boblight] hScanBottom_left:"+str(hScanBottom_left)+" hScanBottom_right:"+str(hScanBottom_right))

			if config.plugins.enigmalight.clockwise.value == str(2): #backwards
				#print("[Boblight] Backwards")
				#print("[Boblight] Set floorstand to true")

				channels = (leds_top + leds_left + leds_right + leds_bottom_total - leds_bottom_center)*3
				#print("[Boblight] channels:"+str(channels))

				#total step
 				hScanStep = 100.0 / leds_bottom_total;				  # 100 / 20 lights = 5
				hScan_center = (hScanStep*leds_bottom_center) # total center hscan // floorstand //  emptyplaces*hScanStep = ... 50
				hScan_left = (hScanStep*leds_bottom_left) # total left hscan /// light left*hScanStep = ... 25
				hScan_right = (hScanStep*leds_bottom_right)

				hScanCurrent = (hScan_center + hScan_left); # 75

				hScanBottom_left  = 0.0; # = 75
				hScanBottom_right = hScanCurrent; # = 75 + 50 = 25

				#print("[Boblight] hScanBottom_left:"+str(hScanBottom_left)+" hScanBottom_right:"+str(hScanBottom_right))

		elif self.begin == "bottom-right" or self.begin == "bottom-middle-right" or self.begin == "bottom-middle-left" or self.begin == "bottom-left":
			leds_bottom_right = leds_bottom/2;
			leds_bottom_left = leds_bottom/2;

			if config.plugins.enigmalight.clockwise.value == str(2):

				hScanStep = 100.0 / leds_bottom;
				hScan_left = (hScanStep*leds_bottom) # total left hscan /// light left*hScanStep = ... 25
				hScan_right = (hScanStep*leds_bottom)

				hScanCurrent = (hScan_left); # 75

				hScanBottom_right = 100.0; # = 75
				hScanBottom_left = hScanCurrent; # = 75 + 50 = 25
			
			elif config.plugins.enigmalight.clockwise.value == str(1):
				hScanStep = 100.0 / leds_bottom;
				hScan_left = (hScanStep*leds_bottom) # total left hscan /// light left*hScanStep = ... 25
				hScan_right = (hScanStep*leds_bottom)

				hScanCurrent = (hScan_right); # 75

				hScanBottom_right = hScanCurrent; # = 75
				hScanBottom_left = 50.0; # = 75 + 50 = 25
		#
		# Atmolight need 4 channels more.
		#

		if config.plugins.enigmalight.type.value == "Atmolight":
			channels += 4

		total_lights = channels / 3;

		if self.createfile:
			#
			# Set some vars
			#
			
			colorr = ""
			colorg = ""
			colorb = ""

			if config.plugins.enigmalight.color_order.value == "1":
				colorr = "0000FF"
				colorg = "00FF00"
				colorb = "FF0000"
			if config.plugins.enigmalight.color_order.value == "0":
				colorr = "FF0000"
				colorg = "00FF00"
				colorb = "0000FF"
			if config.plugins.enigmalight.color_order.value == "2":
				colorr = "00FF00"
				colorg = "0000FF"
				colorb = "FF0000"

			#
			# Set prefix, type and interval
			#

			if config.plugins.enigmalight.type.value == "Lightpack":
				type = "lightpack\n"
				interval = "interval 20000\n"
				prefix = "\n"
			if config.plugins.enigmalight.type.value == "Oktolight":
				type = "karate\n"
				interval= "interval 16000\n"
				prefix = "\n"
			if config.plugins.enigmalight.type.value == "Karatelight":
				type = "karate\n"
				interval= "interval 16000\n"
				prefix = "\n"
			if config.plugins.enigmalight.type.value == "Atmolight":
				type = "atmo\n"
				prefix  = "prefix FF\n"
				interval= "interval 16000\n"
			if config.plugins.enigmalight.type.value == "Adalight/Momo":
				type = "momo\n"
				interval= "interval 20000\n"
				#delayafteropen = "delayafteropen  1000000\n"
				prefix = "\n"

				#
				# Prefix calculation [This only works for arduino boards]
				#

				os.system("/home/elight-addons/prefix "+str(total_lights)+" > /tmp/prefix.txt")

				fo = open("/tmp/prefix.txt", "r")
				reading = fo.read(1000)
				fo.close()

				# remove tmpfile
				os.system("rm /tmp/prefix.txt")

				reading = reading.split("LEDS:  ")
				if len(reading) > 1:
					prefix = "prefix "+str(reading[1])+"\n"
				# Removed the c binary used - moved to using python
				else:
					p = self.calc_prefix(int(total_lights))
					reading = " ".join([format(b, "02x") for b in p])
					prefix = "prefix "+str(reading)+"\n"

			if config.plugins.enigmalight.type.value == "iBelight":
				type = "ibelight\n"
				interval = "interval 20000\n"
				prefix = "\n"
			if config.plugins.enigmalight.type.value == "Sedulight 5A A0 A5":
				prefix = "prefix 5A A0\n"
				postfix = "postfix A5\n"
				type = "momo\n"
				interval = "interval 10000\n"
				delayafteropen = "delayafteropen 1000000\n"
			if config.plugins.enigmalight.type.value == "Sedulight 5A A1 A5":
				prefix = "prefix 5A A1\n"
				postfix = "postfix A5\n"
				type = "momo\n"
				interval = "interval 10000\n"
				delayafteropen = "delayafteropen 1000000\n"
			if config.plugins.enigmalight.type.value == "Sedulight 5A A2 A5":
				prefix = "prefix 5A A2\n"
				postfix = "postfix A5\n"
				type = "momo\n"
				interval = "interval 10000\n"
				delayafteropen = "delayafteropen 1000000\n"
			if config.plugins.enigmalight.type.value == "Sedulight 5A B0 A5":
				prefix = "prefix 5A B0\n"
				postfix = "postfix A5\n"
				type = "momo\n"
				interval = "interval 10000\n"
				delayafteropen = "delayafteropen 1000000\n"
				channels = "768"

			#
			# set the name
			#

			name = "ambilight"

		#
		# Create file
		#

		if self.createfile:

			fo = None

			fo = open("/tmp/enigmalight.conf.new", "wb")

			fo.write("[global]\n")
			fo.write("interface 127.0.0.1\n")
			fo.write("port 19333\n")
			fo.write("\n")

			fo.write("[device]\n")

			if config.plugins.enigmalight.type.value == "WifiLight":
				name = "wifilight"
				fo.write("name "+name+"\n")

				fo.write("output python /home/elight-addons/wifilight/wifilight.py\n")
				fo.write("type popen\n")
				fo.write("interval 100000\n")
				fo.write("channels 3\n")
			else:
				fo.write("name "+name+"\n")
				fo.write("output "+config.plugins.enigmalight.output.value+"\n")
				fo.write("type "+type)
				fo.write(interval)
				fo.write(prefix)
				fo.write(postfix)
				fo.write("channels "+str(channels)+"\n")

			if config.plugins.enigmalight.type.value != "iBelight" and config.plugins.enigmalight.type.value != "Lightpack":
				fo.write("rate "+str(config.plugins.enigmalight.rate.value)+"\n")

			fo.write("debug off\n")
			fo.write(delayafteropen)
			fo.write("\n")

			fo.write("[color]\n")
			fo.write("name red\n")
			fo.write("rgb "+colorr+"\n")
			fo.write("gamma "+str(config.plugins.enigmalight.config_r_gamma.value[0])+"."+str(config.plugins.enigmalight.config_r_gamma.value[1])+"\n")
			fo.write("adjust "+str(config.plugins.enigmalight.config_r_adjust.value[0])+"."+str(config.plugins.enigmalight.config_r_adjust.value[1])+"\n")
			fo.write("blacklevel "+str(config.plugins.enigmalight.config_r_blacklevel.value[0])+"."+str(config.plugins.enigmalight.config_r_blacklevel.value[1])+"\n")
			fo.write("\n")

			fo.write("[color]\n")
			fo.write("name green\n")
			fo.write("rgb "+colorg+"\n")
			fo.write("gamma "+str(config.plugins.enigmalight.config_g_gamma.value[0])+"."+str(config.plugins.enigmalight.config_g_gamma.value[1])+"\n")
			fo.write("adjust "+str(config.plugins.enigmalight.config_g_adjust.value[0])+"."+str(config.plugins.enigmalight.config_g_adjust.value[1])+"\n")
			fo.write("blacklevel "+str(config.plugins.enigmalight.config_g_blacklevel.value[0])+"."+str(config.plugins.enigmalight.config_b_blacklevel.value[1])+"\n")
			fo.write("\n")

			fo.write("[color]\n")
			fo.write("name blue\n")
			fo.write("rgb "+colorb+"\n")
			fo.write("gamma "+str(config.plugins.enigmalight.config_b_gamma.value[0])+"."+str(config.plugins.enigmalight.config_b_gamma.value[1])+"\n")
			fo.write("adjust "+str(config.plugins.enigmalight.config_b_adjust.value[0])+"."+str(config.plugins.enigmalight.config_b_adjust.value[1])+"\n")
			fo.write("blacklevel "+str(config.plugins.enigmalight.config_b_blacklevel.value[0])+"."+str(config.plugins.enigmalight.config_b_blacklevel.value[1])+"\n")
			fo.write("\n")

		#
		# begin to create lights section
		#

		# Set lightCount to 1
		lightCount   = 1
		channelCount = 1

		# Atmolight need to start @ 4
		if config.plugins.enigmalight.type.value == "Atmolight":
			channelCount = 4

		# Set v and h to 0
		vScanCurrent = 0
		hScanCurrent = 0

		#
		# Set the section order
		#

		if self.begin == "left-bottom" or self.begin == "left-top":
			if config.plugins.enigmalight.clockwise.value == str(1):
				order = "left,top,right,bottom" # Clockwise
			else:
				order = "left,bottom,right,top" # Backwards

			if config.plugins.enigmalight.floorstand.value == str(2):
				if config.plugins.enigmalight.clockwise.value == str(1):
					order = "left,top,right,bottom-right,bottom-center,bottom-left" # Clockwise
				else:
					order = "left,bottom-left,bottom-center,bottom-right,right,top" # Backwards

		if self.begin == "top-left" or self.begin == "top-right":
			if config.plugins.enigmalight.clockwise.value == str(1):
				order = "top,right,bottom,left" # Clockwise
			else:
				order = "top,left,bottom,right" # Backwards
				
			if config.plugins.enigmalight.floorstand.value == str(2):
				if config.plugins.enigmalight.clockwise.value == str(1):
					order = "top,right,bottom-right,bottom-center,bottom-left,left" # Clockwise
				else:
					order = "top,left,bottom-left,bottom-center,bottom-right,right" # Backwards

		if self.begin == "right-top" or self.begin == "right-bottom":
			if config.plugins.enigmalight.clockwise.value == str(1):
				order = "right,bottom,left,top" # Clockwise
			else:
				order = "right,top,left,bottom" # Backwards

			if config.plugins.enigmalight.floorstand.value == str(2):
				if config.plugins.enigmalight.clockwise.value == str(1):
					order = "right,bottom-right,bottom-center,bottom-left,left,top" # Clockwise
				else:
					order = "right,top,left,bottom-left,bottom-center,bottom-right" # Backwards

		if self.begin == "bottom-right" or self.begin == "bottom-middle-left" or self.begin == "bottom-middle-right" or self.begin == "bottom-left":
			if self.begin == "bottom-middle-left":
				if config.plugins.enigmalight.clockwise.value == str(1):
					order = "bottom-left,left,top,right,bottom-right" # Clockwise
				else:
					order = "bottom-right,right,top,left,bottom-left" # Backwards
			else:
				if config.plugins.enigmalight.clockwise.value == str(1):
					order = "bottom,left,top,right" # Clockwise
				else:
					order = "bottom,right,top,left" # Backwards
			if config.plugins.enigmalight.floorstand.value == str(2):
				if config.plugins.enigmalight.clockwise.value == str(1):
					order = "bottom-center,bottom-left,left,top,right,bottom-right" # Clockwise
				else:
					order = "bottom-center,bottom-right,right,top,left,bottom-left" # Backwards


		# Split the orderarray
		order = order.split(",")

		# Debug
		#print("[Boblight] order   = "+str(order))
		#print("[Boblight] begincount = "+config.plugins.enigmalight.begincount.value)

		# 100 0 100 0 0 100 0 100 clockwards
		# 0 100 100 0 100 0 0 100 backwards

		#
		# order loop
		#

		totalCount = 1
		for section in order:

			if section == "left":
				lights = leds_left
				vScanCurrent = 100.00 # From LEFT-bottom to LEFT-top # Clockwise
				if config.plugins.enigmalight.clockwise.value == str(2):
					vScanCurrent = 0.00 # From LEFT-top to LEFT-bottom # Backwards

			if section == "top":
				lights = leds_top
				hScanCurrent = 0.00 # From TOP-left to TOP-right  # Clockwise
				if config.plugins.enigmalight.clockwise.value == str(2): 
					hScanCurrent = 100.00 # From TOP-right to TOP-left # Backwards

			if section == "right":
				lights = leds_right
				vScanCurrent = 0.00 # From RIGHT-top to RIGHT-bottom # Clockwise
				if config.plugins.enigmalight.clockwise.value == str(2): 
					vScanCurrent = 100.00 # From RIGHT-bottom to RIGHT-top # Backwards

			if section == "bottom":
				lights = leds_bottom
				hScanCurrent = 100.00 # From BOTTOM-right to BOTTOM-left   # Clockwise
				if config.plugins.enigmalight.clockwise.value == str(2): 
					hScanCurrent = 0.00 # From BOTTOM-left to BOTTOM-right # Backwards

			if section == "bottom-right":
				lights = leds_bottom_right
				hScanCurrent = float(hScanBottom_right)
				if config.plugins.enigmalight.clockwise.value == str(2): 
					hScanCurrent = float(hScanBottom_right)

			if section == "bottom-left":
				lights = leds_bottom_left
				hScanCurrent = float(hScanBottom_left)
				if config.plugins.enigmalight.clockwise.value == str(2): 
					hScanCurrent = float(hScanBottom_left)

			'''###################  Bottom Center  ####################'''

			if self.begin == "bottom-middle-left" or self.begin == "bottom-middle-right":
				if section == "bottom":
					lights = leds_bottom
					lights = lights/2 # we start at middle so we need to deceide it.
					hScanCurrent = 50.00

				if section == "bottom-left":
					lights = leds_bottom_left
					hScanCurrent = hScanBottom_left 

				if section == "bottom-right":
					lights = leds_bottom_right
					hScanCurrent = hScanBottom_right 

			'''########################################################'''

			#
			# Set start value
			#

			if section == "left" and self.begin == "left-bottom":
				vScanCurrent = 100.00 # Start @ LEFT-bottom

			if section == "left" and self.begin == "left-top":
				vScanCurrent = 0.00 # Start @ LEFT-top

			if section == "top" and self.begin == "top-left":
				hScanCurrent = 0.00 # Start @ TOP-left

			if section == "top" and self.begin == "top-right":
				hScanCurrent = 100.00 # Start @ TOP-right

			if section == "right" and self.begin == "right-bottom":
				vScanCurrent = 100.00 # Start @ RIGHT-bottom

			if section == "right" and self.begin == "right-top":
				vScanCurrent = 0.00 # Start @ RIGHT-top

			if section == "bottom" and self.begin == "bottom-left":
				hScanCurrent = 0.00 # Start @ BOTTOM-left

			if section == "bottom" and self.begin == "bottom-right":
				hScanCurrent = 100.00 # Start @ BOTTOM-right


			lightCount = 1 #lights counter

			# Atmolight need to start @ 4
			if config.plugins.enigmalight.type.value == "Atmolight":
				lightCount = 4

			# Empty places for floorstand option
			if section == "bottom-center":
				lights = 0 #Set lights to 0, we want not into loop.

			#
			# check if section contains more then 0 lights
			#

			if lights > 0:

				# Steps
				vScanStep = 100.00 / lights;
				hScanStep = 100.00 / lights;


				# Set other step for floorstand option
				if config.plugins.enigmalight.floorstand.value == str(2):
					if section == "bottom-left" or section == "bottom-right" or section == "bottom-center":
						hScanStep  = 100.00 / leds_bottom_total
				elif self.begin == "bottom-middle-left" or self.begin == "bottom-middle-right":
					if section == "bottom-left" or section == "bottom-right":
						hScanStep  = 100.00 / leds_bottom

				# Loop
				while(lightCount <= lights):

					if section == "right" or section == "top":
						vScanEnd = vScanCurrent
						hScanEnd = hScanCurrent

						if config.plugins.enigmalight.clockwise.value == str(2): #backwards
							vScanStart = vScanCurrent - vScanStep
							hScanStart = hScanCurrent - hScanStep
						else:
							vScanStart = vScanCurrent + vScanStep
							hScanStart = hScanCurrent + hScanStep

						vScanCurrent = vScanStart
						hScanCurrent = hScanStart

					elif section == "left" or section == "bottom" or section == "bottom-left" or section == "bottom-right":
						vScanStart = vScanCurrent
						hScanStart = hScanCurrent

						if config.plugins.enigmalight.clockwise.value == str(2): #backwards
							vScanEnd = vScanCurrent + vScanStep
							hScanEnd = hScanCurrent + hScanStep
							if section == "bottom-right" and self.begin == "bottom-middle":
								hScanEnd = hScanCurrent - hScanStep
						else:
							vScanEnd = vScanCurrent - vScanStep
							hScanEnd = hScanCurrent - hScanStep

						vScanCurrent = vScanEnd
						hScanCurrent = hScanEnd

					if self.createfile:
						fo.write("\n")
						fo.write("\n")

					# Light name must be 3 chars
					s = str(totalCount)
					s += "XX"

					length = len(s)
					mini = length -3

					if length is 4 or length > 4:
						s = s[:-mini]

					if self.createfile:
						fo.write("[light]\n")
						section_name = section
						if section == "bottom-left" or section == "bottom-right" or section == "bottom-center":
							section_name = "bottom"
						fo.write("position "+str(section_name)+"\n")
						fo.write("name "+str(s)+"\n")

						fo.write("color red "+name+" "+str(channelCount)+"\n")
						channelCount += 1

						fo.write("color green "+name+" "+str(channelCount)+"\n")
						channelCount += 1

						fo.write("color blue "+name+" "+str(channelCount)+"\n")
						channelCount += 1

					# Swap end and start if it's clockwise
					if config.plugins.enigmalight.clockwise.value == str(1):
						v = vScanEnd
						vScanEnd = vScanStart
						vScanStart = v
						h = hScanEnd
						hScanEnd = hScanStart
						hScanStart = h

					# Set hscan and vscan
					if section == "right":
						vs = abs(round(vScanStart,2))
						ve = abs(round(vScanEnd,2))
						hd = 100.00 - scanr
						if self.createfile:
							fo.write("hscan "+str(hd)+" 100 \n")
							fo.write("vscan "+str(vs)+" "+str(ve)+"\n")

						#step = i * (300 / config.plugins.enigmalight.lights_right.value)
						#self.c.fill(390, vs*2, 5, 5, RGB(000,000,255))
						#print "step-right %s" %(str(vs*2))

						# Debug
						#print("[Boblight] vScanStart  :  "+str(vs))
						#print("[Boblight] vScanEnd :  "+str(ve))

					elif section == "bottom" or section == "bottom-left" or section == "bottom-right":
						hs = abs(round(hScanStart,2))
						he = abs(round(hScanEnd,2))
						vd = 100.00 - scanb

						if self.createfile:
							if he > hs:
								fo.write("hscan "+str(hs)+" "+str(he)+"\n")
							else:
								fo.write("hscan "+str(he)+" "+str(hs)+"\n")
							fo.write("vscan "+str(vd)+" 100\n")

						# Debug
						#print("[Boblight] hScanStart :  "+str(hs))
						#print("[Boblight] hScanEnd :  "+str(he))

					elif section == "top":
						hs = abs(round(hScanStart,2))
						he = abs(round(hScanEnd,2))
						vd = scant

						if self.createfile:
							if he > hs:
								fo.write("hscan "+str(hs)+" "+str(he)+"\n")
							else:
								fo.write("hscan "+str(he)+" "+str(hs)+"\n")
							fo.write("vscan 0 "+str(vd)+"\n")

						#self.c.fill(hs*4, 0, 5, 5, RGB(255,000,000))
						#print "step-top %s" %(str(hs*4))

						# Debug
						#print("[Boblight] hScanStart  :  "+str(hs))
						#print("[Boblight] hScanEnd	:  "+str(he))

					elif section == "left":
						vs = abs(round(vScanStart,2))
						ve = abs(round(vScanEnd,2))
						hd = scanl

						if self.createfile:
							fo.write("hscan 0 "+str(hd)+"\n")
							fo.write("vscan "+str(vs)+" "+str(ve)+"\n")

						#self.c.fill(0, vs*2, 5, 5, RGB(000,255,000))
						#print "step-left %s" %(str(vs*2))

						# Debug
						#print("[Boblight] vScanStart  :  "+str(vs))
						#print("[Boblight] vScanEnd	:  "+str(ve))

					lightCount += 1; # Counter for sections
					totalCount += 1;
				# End loop
		#self.c.flush()

		if config.plugins.enigmalight.type.value == "WifiLight":
			try:
				fowifi = open("/home/elight-addons/wifilight/wifilight.conf", "wb")
				fowifi.write(str(config.plugins.enigmalight.wifilight_ip.getText())+"|")
				fowifi.write(str(config.plugins.enigmalight.wifilight_port.getText()))
				fowifi.close()

			except:
				from traceback import format_exc
				log("Error:" +format_exc(),self)
				try:
					open(getCrashFilePath(),"w").write(format_exc())
					showMessage(self._session,_("Can't write settings to /home/elight-addons/wifilight/wifilight.conf..."), "W", timeout = 10)
				except:
					pass

		fo.close()

		if self.test:
			#kill enigmalight and start the test
			self.controller.killEnigmalight(None,self.doTest)
		else:
			self.MovetoEtc(True,True)

	def calc_prefix(self, num_leds):
		prefix = [ord(c) for c in "Ada"]
		high_byte = ((num_leds - 1) >> 8) & 0xff
		low_byte = (num_leds - 1) & 0xff
		checksum = high_byte ^ low_byte ^ 0x55
		prefix.extend([high_byte, low_byte, checksum])
		return prefix

	def doTest(self):
		log("",self,"Test Started...")
		self.controller.Control("grabber","configtest")
		self.session.openWithCallback(self.testConfirmed, MessageBox, _("Red,Green,Blue Test Started.\nAre the lights on and are color order ok ?"), MessageBox.TYPE_YESNO, timeout = 20, default = True)

	def testConfirmed(self, confirmed):
		log("",self)
		if self.test:
				self.controller.Control("grabber","stop")

		if confirmed:
			self.session.openWithCallback(self.MovetoEtc, MessageBox, _("Save this configfile to /etc/ ?"), MessageBox.TYPE_YESNO, timeout = 20, default = True)

	def MovetoEtc(self, confirmed, message = False):
		log("",self)
		if confirmed:
			exists = os.path.isfile("/tmp/enigmalight.conf.new")
			if exists:
				os.system("mv /tmp/enigmalight.conf.new /etc/enigmalight.conf")
				if message:
					self.session.open(MessageBox, _("enigmalight.conf succesfull saved in /etc/"), MessageBox.TYPE_INFO, timeout=4)
		self.createfile = False
		self.test = False
