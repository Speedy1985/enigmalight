# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from enigma import eEnv
from Components.config import config
from Tools.Directories import fileExists
from twisted.internet import reactor, ssl
from twisted.web import server, http, static, resource, error, version
from twisted.internet.error import CannotListenError

from remote.root import RootController
from socket import gethostname, has_ipv6

from twisted.internet.protocol import Factory, Protocol
from __common__ import EnigmaLight_log as log, rgbToHex, showMessage, showError

import os
import imp
import re

global listener, server_to_stop
listener = []

def buildRootTree(session):
	log("",None,"EL_HttpServer::buildRootTree()")
	root = RootController(session)
	return root

def HttpdStart(session, instance):
	log("",None,"EL_HttpServer::HttpdStart()")
	if config.plugins.enigmalight.remote_server.value:
		global listener
		port = config.plugins.enigmalight.remote_port.value

		root = buildRootTree(session)
		site = server.Site(root)

		#set controller instance
		root.setCInstance(instance)

		# start http webserver on configured port
		try:
			listener.append( reactor.listenTCP(port, site) )
			log("",None," EL_HttpServer::HttpdStart() -> Enigmalight Webremote started on port: " + str(port))
			BJregisterService('http',port)
		except CannotListenError:
			log("",None," EL_HttpServer::HttpdStart() -> Enigmalight Webremote failed to listen on port: " + str(port))

def HttpdStop(session):
	log("",None,"EL_HttpServer::HttpdStop()")
	StopServer(session).doStop()
#
# Helper class to stop running web servers; we use a class here to reduce use
# of global variables. Resembles code prior found in HttpdStop et. al.
# 
class StopServer:
	server_to_stop = 0

	def __init__(self, session, callback=None):
		self.session = session
		self.callback = callback

	def doStop(self):
		log("",self)
		global listener
		self.server_to_stop = 0
		for interface in listener:
			log("",self,"Stopping server on port " + str(interface.port))
			deferred = interface.stopListening()
			try:
				self.server_to_stop += 1
				deferred.addCallback(self.callbackStopped)
			except AttributeError:
				pass
		listener = []
		if self.server_to_stop < 1:
			self.doCallback()

	def callbackStopped(self, reason):
		log("",self)
		self.server_to_stop -= 1
		if self.server_to_stop < 1:
			self.doCallback()

	def doCallback(self):
		log("",self)
		if self.callback is not None:
			self.callback(self.session)

# BJ
def BJregisterService(protocol, port):
	log("",None,"EL_HttpServer::BJregisterService()")
	try:
		from Plugins.Extensions.Bonjour.Bonjour import bonjour
		service = bonjour.buildService(protocol, port, 'EnigmalightRemote')
		bonjour.registerService(service, True)
		return True

	except ImportError, e:
		return False
