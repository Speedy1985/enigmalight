# -*- coding: utf-8 -*-
"""
EnigmaLight Plugin by Speedy1985, 2014
 
https://github.com/speedy1985

Parts of the code are from other plugins:
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
#===============================================================================
# IMPORT
#===============================================================================

import sys, time, socket, os, threading, commands
from threading import Thread

from Components.Console import Console
from Screens import Standby
from Components.ConfigList import ConfigListScreen
from Components.config import config, configfile, getConfigListEntry, ConfigFloat, ConfigSubsection, ConfigEnableDisable, ConfigSelection, ConfigSlider, ConfigDirectory, ConfigOnOff, ConfigNothing, ConfigInteger, ConfigYesNo
from EL_Socket import EL_Socket
from EL_HttpServer import HttpdStart, HttpdStop

from __common__ import EnigmaLight_log as log, rgbToHex, showMessage, showError

from __init__ import getCrashFilePath, _ # _ is translation

elightconf_notfound   = _("File /etc/enigmalight.conf not found.")

class Controller(threading.Thread):

	def __init__ (self):
		log("",self)
		threading.Thread.__init__(self)
		self.sockClass = EL_Socket()
		
		self.session = None
		self.global_session = None
		self.checkedForUpdates = False
		self.currentScreen = None
		self.mainScreen = None
		self.clearStatusInfo = None

		self.checkConsole = None
		self.startConsole = None
		self.processID = None
		self.callback = None
		self.callbackArgs = None

		self.isStandby = False
		self.processRunning = False
		self.lightsEnabled = False

		self.current_mode = None
		self.current_resolution = "0x0"
		self.current_fps = 0
		self.current_cpu = 0
		self.current_state = "??"
		self.connectedAddres = None
		self.status_text = ""
		self.serverstate = False

		self.thread_running = True 

		#Run this thread as daemon
		self.setDaemon(True)
		
		#Standby notifier
		config.misc.standbyCounter.addNotifier(self.enterStandby, initial_call = False)
	
	def setScreen(self, screenInstance):
		self.currentScreen = screenInstance

	def setMainScreen(self, value):
		self.mainScreen = value	

	def run(self):
		log("",self,"ControlThread: Running...")
		
		checkLoop = 4 # check every 2 sec for cpu usage
		loopCount = 0

		while(self.thread_running):

			#Check connection
			self.sockClass.checkConnection()

			#if not connected then connect with it.
			if self.sockClass.connectedWithEnigmalight():
				self.readInfo() #get runninginfo				
			else:
				self.lightsEnabled = False
				self.current_fps = "0"
				self.current_resolution = "0x0"
				self.current_mode = "Off"
				self.current_cpu = "0"

			#when checkloop is 2 then getcpu
			
		 	if(loopCount == checkLoop):		 		
		 		#self.getCpu()
		 		loopCount = 0
		 	else:
		 		loopCount += 1
		 	

		 	#check mode
		 	if config.plugins.enigmalight.network_onoff.value:
		 		ext = "Daemon %s:%s" %(str(config.plugins.enigmalight.address.getText()),str(config.plugins.enigmalight.port.getText()))
		 	elif config.plugins.enigmalight.type.value == "WifiLight": 
		 		ext = "Local [Wifilight] %s:%s" %(str(config.plugins.enigmalight.wifilight_ip.getText()),str(config.plugins.enigmalight.wifilight_port.getText()))
		 	else:
		 		ext = "Local"
		 	

		 	

			if(self.current_mode == "0" and not self.serverstate):
				mode = _("[Server] Idle")
				self.lightsEnabled = False
			elif(self.current_mode == "0" and self.serverstate):
				mode = _("[Server] Client connected (%s)" %(self.connectedAddres))
				self.lightsEnabled = False
			elif(self.current_mode == "1"):
				mode = _("[Moodlamp] %s | Static color" %(ext))
				self.lightsEnabled = True
			elif(self.current_mode == "2"):
				mode = _("[Dynamic] %s | %s") %(ext,self.current_resolution)
				self.lightsEnabled = True
			elif(self.current_mode == "3"):
				mode = _("[Moodlamp] %s | RGBtest" %(ext))
				self.lightsEnabled = True
			elif(self.current_mode == "4"):
				mode = _("[Moodlamp] %s | ColorFader" %(ext))
				self.lightsEnabled = True
			elif(self.current_mode == "5"):
				mode = _("[Moodlamp] %s | Rainbow" %(ext))
				self.lightsEnabled = True
			else:
				mode = "Off"
				self.lightsEnabled = False
			

			if self.currentScreen != None and self.mainScreen != None:
				self.currentScreen.handleFromThread(self.currentScreen.showButtons)

			#Set StatusBar text
			if not self.lightsEnabled and not self.sockClass.connected:
				status = _("Not Running")
				mode   = "Off"
			elif self.lightsEnabled and self.sockClass.connected:
				status = _("LightsOn")
			elif not self.lightsEnabled and self.sockClass.connected:
				status = _("LightsOff")
			

			#Statusbar
			if self.currentScreen != None:
				stContent = _("Status: %s | Current mode: %s | FPS: %s") %(status,mode,self.current_fps)
				try:
					#self.currentScreen.handleFromThread("setStatusBarTxt",stContent)
					self.currentScreen.handleFromThread(self.currentScreen.setStatusBarTxt,stContent)
				except:
					from traceback import format_exc
					log("",self,"Error: "+format_exc())
					try:
						open(getCrashFilePath(),"w").write(format_exc())
						if config.plugins.enigmalight.message_error_onoff.value:
							showError(self.session, (format_exc()), "E")
					except:
						pass

				#clear info
				if self.clearStatusInfo != None and self.clearStatusInfo == loopCount:
					try:
						#self.currentScreen.handleFromThread("setStatusBarInfo","")
						self.currentScreen.handleFromThread(self.currentScreen.setStatusBarInfo,"")
						#clear info
						self.clearStatusInfo = None
					except:
						from traceback import format_exc
						log("",self,"Error: "+format_exc())
						try:
							open(getCrashFilePath(),"w").write(format_exc())
							if config.plugins.enigmalight.message_error_onoff.value:
								showError(self.session, (format_exc()), "E")
						except:
							pass

			time.sleep(0.5)

		log("ControlThread: exit...")
		self.thread_running = False

	def setStatusBarInfo(self,info):
		log("",self)
		try:
			if self.currentScreen != None:
				self.currentScreen.handleFromThread(self.currentScreen.setStatusBarInfo,_("Info: ["+ info +"]"))
				pass
			#clear info
			self.clearStatusInfo = 2
		except:
			from traceback import format_exc
			log("",self,"Error: "+format_exc())
			try:
				open(getCrashFilePath(),"w").write(format_exc())
				if config.plugins.enigmalight.message_error_onoff.value:
					showError(self.session, (format_exc()), "E")
			except:
				pass

	#===============================================================================
	# Read info from enigmalight.info
	#===============================================================================
	def readInfo(self):
		#log("",self)

		try:
			self.serverstate = self.sockClass.getServerState()

			self.current_mode = str(self.sockClass.getMode())
			self.current_fps = str(self.sockClass.getFPS())
			self.current_resolution = str(self.sockClass.getRes())

			if self.current_mode == "0" and self.serverstate:
				self.connectedAddres = self.sockClass.getConnectedAddress()
			else:
				self.connectedAddres = None
		except:
			self.current_fps = "0"
			self.current_resolution = "0x0"
			self.current_mode = "Off"
			self.current_cpu = "0"

			from traceback import format_exc
			log("",self,"Error: "+format_exc())
			try:
				open(getCrashFilePath(),"w").write(format_exc())
			except:
				pass

	#===============================================================================
	# Get CPU Usage of EnigmaLight
	#===============================================================================
	def getCpu(self):
		#log("",self)
		try:
			cpu = commands.getstatusoutput('top -n1 | grep "enigmalight" | awk \'{print $7}\'')
			cpu_split = str(cpu).split("'")
			cpu = cpu_split[1][:3]#remove new line and other stuff
			cpu = cpu.replace("\\","")
			#print ("[EnigmaLight] Cpu usage [" + cpu + "]")
			self.current_cpu = cpu
		except:
			from traceback import format_exc
			log("",self,"Error: "+format_exc())
			try:
				open(getCrashFilePath(),"w").write(format_exc())
				if config.plugins.enigmalight.message_error_onoff.value:
					showError(self.session, (format_exc()), "E")
			except:
				pass

	#===============================================================================
	# Set Session
	#===============================================================================
	def setSession(self, session = None):
		if session == None:
			self.session = self.global_session
		else:
			self.session = session
	
	def setGlobalSession(self, session):
		self.global_session = session

	#===============================================================================
	# Call function on Standby
	#===============================================================================
	def enterStandby(self, configElement):
		log("",self)
		if not self.isStandby and self.lightsEnabled:
			Standby.inStandby.onClose.append(self.leaveStandby)
			self.isStandby = True
			log("",self,"ControlThread: enterStandby..")
			self.Control("grabber","sleep")
	
	#===============================================================================
	# Call function on wakeup from standby
	#===============================================================================
	def leaveStandby(self):
		log("",self)
		if self.isStandby is True:
			self.isStandby = False
			log("ControlThread: leaveStandby..",self)
			self.Control("grabber","wakeup")

	#===============================================================================
	# Control functions (start 	... stop)
	#===============================================================================
	def Control(self, command, value, startcommand = "enigmalight -m 0 -f", callback = None):
		log("",self,"Control: c:%s v:%s" %(command, value))

		#Set ConfigFile
		s_command = startcommand + " -c " + str(config.plugins.enigmalight.configfilepath.value)		

		#Don't use config file for client -> host
		if config.plugins.enigmalight.network_onoff.value:
			host = str(config.plugins.enigmalight.address.getText())
			port = str(config.plugins.enigmalight.port.getText())
			s_command = "enigmalight -s " + host + ":" + port

		if value == "configtest":
			s_command = startcommand + " -c /tmp/enigmalight.conf.new"

		control = { 'command': command, 'value': value, 'startcommand': s_command}

		if config.plugins.enigmalight.network_onoff.value == True:
			#self.getPid(control,None,self.checkIfRunningFinisched) #only network mode
			self.checkIfRunningFinisched(control,None)
		elif os.path.isfile(str(config.plugins.enigmalight.configfilepath.value)) is True:
			# getpid and execute command self.checkIfRunning -> DoControl
			self.checkIfRunningFinisched(control,None) 					
		else:
			showMessage(self.session, _(elightconf_notfound), "W")
			self.setStatusBarInfo(_("Configfile not found!"))

	def checkIfRunningFinisched(self, control, callback = None):
		log("",self)
		log("",self,"control[command] = " + str(control['command']))
		log("",self,"control[value] = " + str(control['value']))
		log("",self,"control[startcommand] = " + str(control['startcommand']))
		log("",self,"callback = " + str(callback))

		pid = self.sockClass.getCommand("get pidnr")
		log("",self,"pid = " + str(pid))

		checkResult = False

		try:
			if pid is None:

				#Check if engimalight is running
				#it it's not running, then start it.
				if control['value'] != "stop" and control['value'] != "sleep" and control['value'] != "network":
					log("",self,"[/usr/bin/enigmalight] not running, Starting..")

					checkResult = True
					self.startConsole = Console()
					self.startConsole.ePopen(str(control['startcommand']), self.DoControl, [checkResult, control, callback])
				
				#If network mode is used
				elif control['command'] == "network":
					#connect client with host
					log("",self,"network")
			else:
				#Enigmalight is already running
				log("",self,"[/usr/bin/enigmalight] already running with pid " + str(pid))
				self.DoControl(None, None, [checkResult, control, callback])
		except:
			from traceback import format_exc
			log("",self,"Error: "+format_exc())
			try:
				open(getCrashFilePath(),"w").write(format_exc())
			except:
				pass

	def showResult(self, result):
		s = showMessage(self.session,_("Error while starting EnigmaLight:\n\n%s") %(result),"E",10)

	def DoControl(self, result, retval, extra_args = None):
		log("",self)
		(checkResult, control, callback) = extra_args
		ret = 0
		error = False

		commandResult = str(result)

		if checkResult:
			#sleep one sec before do next step.
			time.sleep(1)
			if commandResult.find("ERROR:") != -1:
				self.showResult(str(result))
				error = True

		if error is False:
			try:
			
				if control['value'] == "stop":
					
					self.setStatusBarInfo(_("Stop lights.."))

					if config.plugins.enigmalight.server.value is True and config.plugins.enigmalight.network_onoff.value == False:
						#Switch to server
						log("",self,"config.plugins.enigmalight.server.value is true, Start server")
						data = "set mode 0\n"
						ret = self.sockClass.setCommand(data)

					else:
						#kill enigmalight
						data = "set mode stop\n"
						self.sockClass.setCommand(data)
					if config.plugins.enigmalight.message_onoff.getValue():
						showMessage(self.session,_("Control: Lights disabled."),"I")
				
				elif control['value'] == "dynamic":

					self.setStatusBarInfo(_("Start lights.."))

					ret = self.controlMode()		

					if config.plugins.enigmalight.message_onoff.getValue():
						showMessage(self.session,_("Control: Lights enabled."),"I")

				elif control['value'] == "configtest":

					self.setStatusBarInfo(_("Change mode"))

					data = "set mode 3\n"
					ret = self.sockClass.setCommand(data) #3 test

					if config.plugins.enigmalight.message_onoff.getValue():
						showMessage(self.session,_("Control: Lights enabled, mode[test]"),"I")

				elif control['value'] == "server":

					self.setStatusBarInfo(_("Change mode"))

					data = "set mode 0\n"
					ret = self.sockClass.setCommand(data)

				elif control['value'] == "moodlamp":

					self.setStatusBarInfo(_("Change mode"))

					ret = self.writeMoodlamp()
					
					if config.plugins.enigmalight.message_onoff.getValue():
						showMessage(self.session,_("Control: Lights enabled, mode[%s]") %(str(config.plugins.enigmalight.moodlamp_mode.getText())),"I")
						
				elif control['value'] == "sleep":
					
					if config.plugins.enigmalight.standbymode.value == str(1):
						#Start Moodlamp
						ret = self.writeMoodlamp()

					elif config.plugins.enigmalight.standbymode.value == str(0):

						if config.plugins.enigmalight.server.value is True and config.plugins.enigmalight.network_onoff.value == False:
							#Switch to server
							log("",self,"config.plugins.enigmalight.server.value is true, Start server")
							data = "set mode 0\n"
							ret = self.sockClass.setCommand(data)
						else:
							#disable lights
							data = "set mode stop\n"
							ret = self.sockClass.setCommand(data)


				elif control['value'] == "wakeup":
					ret = self.controlMode()


				if self.currentScreen != None and self.mainScreen != None:
					self.currentScreen.handleFromThread(self.currentScreen.showButtons)


				#Send all values
				if ret == 1:
					if control['value'] == "dynamic" or control['value'] == "restart" or control['value'] == "wakeup":
						self.sendAll(True)

				if control['value'] != "stop" and control['value'] != "sleep":
					self.writeSettings()

				return ret

			except:
				from traceback import format_exc
				log("",self,"Error: "+format_exc())
				try:
					open(getCrashFilePath(),"w").write(format_exc())
					if config.plugins.enigmalight.message_error_onoff.value:
						showError(self.session, (format_exc()), "E")
				except:
					pass
			
	def controlMode(self):
		log("",self)
		if config.plugins.enigmalight.mode.value == str(1):
			data = "set mode " + str(config.plugins.enigmalight.moodlamp_mode.getValue()) +"\n"
			ret = self.sockClass.setCommand(data)
		elif config.plugins.enigmalight.mode.value == str(2):
			data = "set mode 2\n"
			ret = self.sockClass.setCommand(data)

		return ret


	#===============================================================================
	# Switch from network to normal or normal to network
	#===============================================================================
	def switchtoNetwork(self):
		log("",self)
		host = str(config.plugins.enigmalight.address.getText())
		port = str(config.plugins.enigmalight.port.getText())
		self.Control("start","dynamic","enigmalight -f -s " + host + ":" + port)

	#===============================================================================
	# Functions to forcekill enigmalight with pidnr
	#===============================================================================
	def killEnigmalight(self, args = None, callback = None, command = None):
		log("",self)
		self.setStatusBarInfo(_("killEnigmalight.."))
		
		data = "set mode stop\n"
		self.sockClass.setCommand(data)

		if callback != None:
			self.callback = callback #save callback for later
		if args != None:
			self.callbackArgs = args

		#self.getPid(None,None,self.killEnimgalightNow) #getpid and kill enigmalight
		self.killEnigmalightNow(None,None)
	
	def killEnigmalightNow(self, values = None, callback = None):
		log("",self)

		try:
			self.checkConsole = Console()
			command = "killall -9 enigmalight"

			#set callback from saved callback
			if callback == None and self.callback != None:
				callback = self.callback
				self.callback = None

			self.checkConsole.ePopen(command, self.killEnigmalightFinisched, [values, callback])
		except:
			from traceback import format_exc
			log("Error:",format_exc() )
			try:
				open(getCrashFilePath(),"w").write(format_exc())
			except:
				pass
		
	def killEnigmalightFinisched(self, result, retval, extra_args = None):
		log("",self)
		(values, callback) = extra_args
		log("",self,"values " + str(values))
		log("",self,"result " + str(result))
		log("",self,"retval " + str(retval))
		log("",self,"callback " + str(callback))

		time.sleep(1)
		
		if len(str(result)) == 0:
			self.setStatusBarInfo(_("Enigmalight killed."))

			if config.plugins.enigmalight.message_onoff.getValue():
				showMessage(self.session,_("Enigmalight killed.","I"))
		else:			
			self.setStatusBarInfo(_("Enigmalight not killed!"))
			
			if config.plugins.enigmalight.message_onoff.getValue():
				showMessage(self.session,_("Enigmalight not killed\nresult: %s") %(str(result)),"I")	
		
		if callback != None:
			if self.callbackArgs != None:
				callback(self.callbackArgs) # now do callback from saved callback
			else:
				callback()

	#===============================================================================
	#
	#===============================================================================
	def Toggle(self, **kwargs):
		log("",self)
		if self.lightsEnabled:
			self.Control("mode","stop")
		else:
			self.Control("start","dynamic")

	def StartServer(self):
		HttpdStart(self.global_session, self) #self gives the instances of this controller

	def StopServer(self):
		HttpdStop(self.global_session)

	#===============================================================================
	#
	#===============================================================================
	def writeMoodlamp(self):
		log("",self)		
		self.setStatusBarInfo("writeMoodlamp")

		# Moodlamp, set threshold to 0
		data ="set threshold 0\n"		
  
		if config.plugins.enigmalight.moodlamp_mode.getValue() == str(1):									

			###############
			# Static color
			###############

			color = self.getColor()
			data +="set mode 1\n"
			data +="set static_color "+ str(color) +"\n"			

		elif config.plugins.enigmalight.moodlamp_mode.getValue() == str(3):

			###############
			# Rgb test
			###############
			
			data +="set mode 3\n"

		elif config.plugins.enigmalight.moodlamp_mode.getValue() == str(4):

			###############
			# Color fader
			###############

			#set brightness

			data +="set mode 4\n"
			data +="set moodlamp_brightness "+ str(config.plugins.enigmalight.moodlamp_fader_brightness.getValue()) +"\n"	

		elif config.plugins.enigmalight.moodlamp_mode.getValue() == str(5):

			###############
			# Rainbow
			###############

			#set brightness
			data +="set mode 5\n"

		self.sockClass.setCommand(data)	
		return 1
		
	#===============================================================================
	#
	#===============================================================================
	def writeDynamic(self):
		log("",self)
		self.setStatusBarInfo("writeDynamic")

		data ="set threshold " + str(config.plugins.enigmalight.threshold.getValue()) + "\n"
		data +="set mode 2\n"
		self.sockClass.setCommand(data)	

	#===============================================================================
	#
	#===============================================================================
	def writeServer(self):
		log("",self)
		self.setStatusBarInfo("writeServer")

		data ="set threshold 0\n"
		data +="set mode 0\n"
		self.sockClass.setCommand(data)	
	#===============================================================================
	#
	#===============================================================================
	def writeAdjust(self):
		log("",self)
		self.setStatusBarInfo("writeAdjust")
		data =""

		#only send it to local client
		if config.plugins.enigmalight.network_onoff.value == False:
			if config.plugins.enigmalight.use_live_adjust.getValue() == "true":
				data +="set adjust "+ str(str(config.plugins.enigmalight.adjustr.getValue()) + " " + str(config.plugins.enigmalight.adjustg.getValue()) + " " + str(config.plugins.enigmalight.adjustb.getValue()) + " " + str(config.plugins.enigmalight.use_live_adjust.getValue())) + "\n"
			else:
				data +="set adjust "+ str(0) + " " + str(0) + " " + str(0) + " false " + "\n"

		return data
	#===============================================================================
	#	Change the current selected value
	#===============================================================================
	def changeValue(self, currentoption):
		log("",self)
		color = None
		value = str(currentoption.getValue())
		text  = str(currentoption.getText())
		
		self.setStatusBarInfo("changeValue")

		try:

			if self.lightsEnabled == True:
				if currentoption == config.plugins.enigmalight.mode:
					if text == _("Moodlamp"):
						if self.current_mode == "2" or self.current_mode != None:
							self.writeMoodlamp()

					elif text == _("Dynamic") and self.current_mode != "2":
						self.writeDynamic()

				elif currentoption == config.plugins.enigmalight.moodlamp_mode:  #Change mode only when mode is set to moodlamp
					if self.current_mode != "2" and self.current_mode != None:				
						self.writeMoodlamp()

				#elif currentoption == config.plugins.enigmalight.presets: #send all setting
				#	self.sendAll()
					
				elif currentoption == config.plugins.enigmalight.moodlamp_static_color_r or currentoption == config.plugins.enigmalight.moodlamp_static_color_g or currentoption == config.plugins.enigmalight.moodlamp_static_color_b or currentoption == config.plugins.enigmalight.moodlamp_fader_brightness or currentoption == config.plugins.enigmalight.adjustr or currentoption == config.plugins.enigmalight.adjustg or currentoption == config.plugins.enigmalight.adjustb or currentoption == config.plugins.enigmalight.use_live_adjust:
					
					data = self.writeAdjust()
					
					#data +="set color_sequence " + str(config.plugins.enigmalight.color_sequence.getValue()) + "\n"

					if self.current_mode != "2" and self.current_mode != None:
						color = self.getColor()
											
						data +="set static_color " + str(color) + "\n"
						data +="set moodlamp_brightness" + str(config.plugins.enigmalight.moodlamp_fader_brightness.getValue()) + "\n"

					self.sockClass.setCommand(data)					

				elif currentoption == config.plugins.enigmalight.saturation:
					data ="set saturation "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.saturationmin:
					data ="set saturationmin "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.saturationmax:
					data ="set saturationmax "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.value:
					data ="set value "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.valuemin:
					data ="set valuemin "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.valuemax:
					data ="set valuemax "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.speed:
					data ="set speed "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.delay:
					data ="set delay "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.autospeed:
					data ="set autospeed "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.interval:
					data ="set interval "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.gamma:
					data ="set gamma "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.m_3dmode:
					data ="set 3dmode "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.interpolation:
					data ="set saturation "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.blackbar_h:
					data ="set blackbar_h "+ str(value) + "\n"
					data +="set blackbar_f "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.blackbar_v:
					data ="set blackbar_v "+ str(value) + "\n"
					data +="set blackbar_f "+ str(value) + "\n"
					self.sockClass.setCommand(data)					
				elif currentoption == config.plugins.enigmalight.blackbar_f:
					data ="set blackbar_f "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.threshold:
					data ="set threshold "+ str(value) + "\n"
					self.sockClass.setCommand(data)
				elif currentoption == config.plugins.enigmalight.cluster:
					data ="set cluster "+ str(value) + "\n"
					self.sockClass.setCommand(data)

		except:
			from traceback import format_exc
			log("",self,"Error: "+format_exc())
			try:
				open(getCrashFilePath(),"w").write(format_exc())
				if config.plugins.enigmalight.message_error_onoff.value:
					showError(self.session, (format_exc()), "E")
			except:
				pass

	def writeSettings(self):
		log("",self)

		self.setStatusBarInfo("Write settings.")
	
		##################################
		# Write adjust settings
		##################################
		
		data = self.writeAdjust()

		##################################
		# Write some values
		##################################

		#data +="set color_sequence "+ str(config.plugins.enigmalight.color_sequence.getValue()) + "\n"
		data +="set saturation "+ str(config.plugins.enigmalight.saturation.getValue()) + "\n"
		data +="set saturationmin "+ str(config.plugins.enigmalight.saturationmin.getValue()) + "\n"
		data +="set saturationmax "+ str(config.plugins.enigmalight.saturationmax.getValue()) + "\n"
		data +="set value "+ str(config.plugins.enigmalight.value.getValue()) + "\n"
		data +="set valuemin "+ str(config.plugins.enigmalight.valuemin.getValue()) + "\n"
		data +="set valuemax "+ str(config.plugins.enigmalight.valuemax.getValue()) + "\n"
		data +="set speed "+ str(config.plugins.enigmalight.speed.getValue()) + "\n"
		data +="set autospeed "+ str(config.plugins.enigmalight.autospeed.getValue()) + "\n"
		data +="set gamma "+ str(config.plugins.enigmalight.gamma.getValue()) + "\n"
		#data +="set interpolation "+ str(config.plugins.enigmalight.interpolation.getValue()) + "\n"
		data +="set threshold "+ str(config.plugins.enigmalight.threshold.getValue()) + "\n"
		data +="set interval "+ str(config.plugins.enigmalight.interval.getValue()) + "\n"
		data +="set blackbar_h "+ str(config.plugins.enigmalight.blackbar_h.getValue()) + "\n"
		data +="set blackbar_v "+ str(config.plugins.enigmalight.blackbar_v.getValue()) + "\n"
		data +="set blackbar_f "+ str(config.plugins.enigmalight.blackbar_f.getValue()) + "\n"
		data +="set 3dmode "+ str(config.plugins.enigmalight.m_3dmode.getValue()) + "\n"
		data +="set cluster "+ str(config.plugins.enigmalight.cluster.getValue()) + "\n"
		data +="set delay "+ str(config.plugins.enigmalight.delay.getValue()) + "\n"

		self.sockClass.setCommand(data)
				
		
	#===============================================================================
	# Send all values
	#===============================================================================
	def sendAll(self,sendValues=False):
		log("",self)

		if sendValues == True or self.current_mode != "99" and self.current_mode != "off": #only send values if grabber or moodlamp is running
			
			if self.sockClass.ping():
				self.setStatusBarInfo("Set all values..")											
				
				##################################
				# Set mode, color etc...
				##################################

				if self.lightsEnabled and self.current_mode  != "0":
					if config.plugins.enigmalight.mode.getValue() == str(1):

						###############
						# Moodlamp
						###############

						self.writeMoodlamp()

					elif config.plugins.enigmalight.mode.getValue() == str(2):

						###############
						# Dynamic
						###############

						self.writeDynamic()
					
	#===============================================================================
	#
	#===============================================================================
	def checkMode(self):
		log("",self)
		return str(config.plugins.enigmalight.mode.value)

	#===============================================================================
	#
	#===============================================================================
	def getColor(self):
		log("",self)

		color = rgbToHex(config.plugins.enigmalight.moodlamp_static_color_r.getValue(),config.plugins.enigmalight.moodlamp_static_color_g.getValue(),config.plugins.enigmalight.moodlamp_static_color_b.getValue())

		return color



	#===============================================================================
	#
	#
	#
	#			 Webremote handling, get values and change values
	#
	#
	#
	#===============================================================================
	def handleWebRemote(self, option, value):

		#
		# Color tuning
		#
		if option == "brightness":
			data ="set value "+ str(value) + "\n"
			config.plugins.enigmalight.value.setValue(value)
			config.plugins.enigmalight.value.save()
		elif option == "brightnessmin":
			data ="set valuemin "+ str(value) + "\n"
			config.plugins.enigmalight.valuemin.setValue(value)
			config.plugins.enigmalight.valuemin.save()
		elif option == "brightnessmax":
			data ="set valuemax "+ str(value) + "\n"
			config.plugins.enigmalight.valuemax.setValue(value)
			config.plugins.enigmalight.valuemax.save()
		elif option == "saturation":
			data ="set saturation "+ str(value) + "\n"
			config.plugins.enigmalight.saturation.setValue(value)
			config.plugins.enigmalight.saturation.save()
		elif option == "saturationmax":
			data ="set saturationmax "+ str(value) + "\n"
			config.plugins.enigmalight.saturationmax.setValue(value)
			config.plugins.enigmalight.saturationmax.save()
		elif option == "saturationmin":
			data ="set saturationmin "+ str(value) + "\n"
			config.plugins.enigmalight.saturationmin.setValue(value)
			config.plugins.enigmalight.saturationmin.save()
		elif option == "speed":
			data ="set speed "+ str(value) + "\n"
			config.plugins.enigmalight.speed.setValue(value)
			config.plugins.enigmalight.speed.save()
		elif option == "gamma":
			data ="set gamma "+ str(value) + "\n"
			config.plugins.enigmalight.gamma.setValue(value)
			config.plugins.enigmalight.gamma.save()

		self.sockClass.setCommand(data)

	def getOptionValue(self, option):
		ret = ""

		#
		# Control / Mode
		#
		if option == "lights_onoff":
			if self.lightsEnabled:
				ret = "on"
			else:
				ret = "off"
		elif option == "mode":
			ret = str(self.current_mode)

		#
		# Color tuning
		#
		elif option == "saturation":
			ret = str(config.plugins.enigmalight.saturation.getValue())
		elif option == "saturationmin":
			ret = str(config.plugins.enigmalight.saturationmin.getValue())
		elif option == "saturationmax":
			ret = str(config.plugins.enigmalight.saturationmax.getValue())
		elif option == "brightness":
			ret = str(config.plugins.enigmalight.value.getValue())
		elif option == "brightnessmin":
			ret = str(config.plugins.enigmalight.valuemin.getValue())
		elif option == "brightnessmax":
			ret = str(config.plugins.enigmalight.valuemax.getValue())
		elif option == "speed":
			ret = str(config.plugins.enigmalight.speed.getValue())
		elif option == "gamma":
			ret = str(config.plugins.enigmalight.gamma.getValue())
		else:
			ret = "Unknown option"

		return ret