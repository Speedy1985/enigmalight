# -*- coding: utf-8 -*- 
"""
/*
 * EnigmaLight
 * Copyright (C) Martijn Vos (speedy1985) 2014
 *
*/

"""
from __init__ import _
import sys, time, socket, os, commands, threading
from time import sleep
from Screens.MessageBox import MessageBox
from Components.ConfigList import ConfigListScreen
from Components.config import *
from enigma import eConsoleAppContainer

from __common__ import EnigmaLight_log as log
from __init__ import _ # _ is translation

class ELightTimer(threading.Thread):

	def __init__(self):
		log("",self)
		threading.Thread.__init__(self)
		self.session = None 
		self.dialog  = None
		self.active  = False
		self.timer   = config.plugins.enigmalight.timer_onoff.value
		self.timer_running = False
		self.start_hour = None
		self.start_min  = None
		self.end_hour   = None
		self.end_min	= None
		self.thread_timer = None
		self.thread_running = True
		self.isStandby = False
		self.setDaemon(True)
		self.controller = None

	def run(self):
		log("",self)
		try:
			if self.timer_running == False:
				log("",self,"Timer thread started..")

				while(self.thread_running):
					#check if timer is true
					self.timer = config.plugins.enigmalight.timer_onoff.value
					if self.timer:
						log("",self,"Timer start")

						while self.timer != False:
							
							#time correction
							self.start_hour = str(config.plugins.enigmalight.time_start.value[0])
							if len(self.start_hour) == 1:
								self.start_hour = "0"+self.start_hour
							self.end_hour = str(config.plugins.enigmalight.time_end.value[0])
							if len(self.end_hour) == 1:
								self.end_hour = "0"+self.end_hour
							self.start_min = str(config.plugins.enigmalight.time_start.value[1])
							if len(self.start_min) == 1:
								self.start_min = "0"+self.start_min
							self.end_min = str(config.plugins.enigmalight.time_end.value[1])
							if len(self.end_min) == 1:
								self.end_min = "0"+self.end_min
									  
							self.start_time = self.start_hour+":"+self.start_min+":00"
							self.stop_time  = self.end_hour+":"+self.end_min+":00" 
							
							self.timer_running = True
							
							log("",self,"Time: "+ str(time.strftime("%H:%M:%S")));

							if self.controller != None:
								log("",self,"controller: not none");

								#check if we can use the timer function if box is in standby
								if self.controller.isStandby == True and config.plugins.enigmalight.timer_standby_onoff.value == True or self.controller.isStandby == False:

									log("",self,"Check......");

									if self.start_time == time.strftime("%H:%M:%S"):
										log("",self,"Timer, enable lights..")
										if self.controller.connectedAddres == None:
											self.controller.Control("start", "dynamic")

									if self.stop_time == time.strftime("%H:%M:%S"):
										log("",self,"Timer, Stop lights..")
										if self.controller.connectedAddres == None:
											self.controller.Control("grabber", "stop")

							#update timer true or false
							self.timer = config.plugins.enigmalight.timer_onoff.value
							time.sleep(1)

						log("",self,"Timer stop")

						self.timer_running = False
					#check every 8 seconds
					time.sleep(8)
				log("",self,"Timer thread killed..")
		except:
			from traceback import format_exc
			log("",self,"Error: "+format_exc() )
			try:
				open(crashFile,"w").write(format_exc())
			except:
				pass

	def setSession(self, session):
		log("",self,"")
		self.session = session
		
	def setController(self, controller):
		log("",self,"")
		self.controller = controller
