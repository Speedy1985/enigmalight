# -*- coding: utf-8 -*- 
"""
EnigmaLight Plugin by Speedy1985, 2014
 
https://github.com/speedy1985

Parts of the code is from other plugins:
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

import sys, time, os, threading, thread
import socket
from Components.ConfigList import ConfigListScreen
from Components.config import config, configfile, getConfigListEntry, ConfigFloat, ConfigSubsection, ConfigEnableDisable, ConfigSelection, ConfigSlider, ConfigDirectory, ConfigOnOff, ConfigNothing, ConfigInteger, ConfigYesNo
from __common__ import EnigmaLight_log as log
from __init__ import _ # _ is translation

HOST = '127.0.0.1' #Local
PORT = 6767

class EL_Socket(object):

	def __init__ (self):
		self.error = None
		self.hostip = -1
		self.hostport = None
		self.sock = None
		self.connected = False

	def checkDaemon(self,host,port):

		if config.plugins.enigmalight.network_onoff.value is True:

			log("",self,"Check daemon on address: %s:%s" %(str(host), str(port)))

			dsock = None
			try:
				dsock = socket.socket()
				dsock.settimeout(5)
				dsock.connect((host, port))
				return True
			except Exception, e:
				return False
			finally:
				if dsock != None:
					dsock.close()


	def checkConnection(self):
		if self.connected and self.sock != None:
			if self.ping():
				self.connected = True
			else:
				if self.sock != None:
					self.sock.close()
				self.connected = False
				self.sock = None

		return self.connected

	def connectedWithEnigmalight(self):
		if not self.connected and self.sock == None:
			try:
				self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.sock.settimeout(2)
				self.sock.connect((HOST, PORT))
				self.connected = True
			except socket.error, msg:
				log("E",self,"Exception(" + str(type(msg)) + "): " + str(msg))
				if self.sock != None:
					self.sock.close()
				self.sock = None
				self.connected = False

		return self.connected

	def getCommand(self, data):
		log("E",self,"")
		returned = None

		if self.connectedWithEnigmalight() is True:
			try:

				log("E",self,data)
				self.sock.send(data+"\n")

				returned = str(self.sock.recv(1024))
				log("E",self,"returned: %s " % (returned))

			except socket.error, msg:
				log("E",self,"Exception(" + str(type(msg)) + "): " + str(msg))
				returned = None
			finally:			
				return returned

	def setCommand(self, data):
		log("E",self,"")
		returned = None

		if self.connectedWithEnigmalight() is True:
			try:

				log("E",self,data)

				#Strings to lowercase
				data = data.lower()
				self.sock.send(data)

				#returned = str(self.sock.recv(1024))
				#log("",self,"returned: %s " % (returned))
				returned = 1
			except socket.error, msg:
				log("E",self,"Exception(" + str(type(msg)) + "): " + str(msg))
				returned = None
			finally:			
				return returned

	def ping(self):
		log("E",self,"")
		try:
			self.sock.send("ping\n")
			returned = str(self.sock.recv(1024))
			log("E",self,"returned: %s " % (returned))
			if returned == "ping":
				return True
			else:
				return False
		except:
			return None


	def serverRunning(self):
		log("E",self,"")
		if getMode() != None:
			return True
		else:
			return False

	def getMode(self):
		log("E",self,"")
		ret = self.getCommand("get mode")
		return ret

	def getFPS(self):
		log("E",self,"")
		ret = self.getCommand("get fps")

		#print("FPS: " + str(ret))
		return ret

	def getRes(self):
		log("E",self,"")
		ret = self.getCommand("get res")
		return ret
	
	def getConnectedAddress(self):
		log("E",self,"")
		ret = self.getCommand("get connectedaddress")
		return ret

	def getConnectedPort(self):
		log("E",self,"")
		ret = self.getCommand("get connectedport")
		return ret


	def getServerState(self):
		log("E",self,"")
		ret = self.getCommand("get clientconnected")
		if ret == "1":
			ret = True
		else:
			ret = False

		return ret