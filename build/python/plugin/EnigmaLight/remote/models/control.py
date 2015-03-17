# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from Components.config import config
from enigma import eServiceReference, eActionMap, eServiceCenter
from urllib import unquote

from Plugins.Extensions.EnigmaLight.__common__ import EnigmaLight_log as log, rgbToHex, showMessage, showError


def setLightOn(session, controller):
	log("",None,"models.control::setLightOn()")
	controller.Control("start","dynamic")

def setLightOff(session, controller):
	log("",None,"models.control::setLightOff()")
	controller.Control("stop","stop")

def setOption(session, request, controller):
	log("",None,"models.control::setOption(" + request.args["set"][0] + ")")

	if request.args["set"][0] == "brightness":
		return controller.handleWebRemote("brightness", request.args["v"][0])
	if request.args["set"][0] == "saturation":
		return controller.handleWebRemote("saturation", request.args["v"][0])
	if request.args["set"][0] == "speed":
		return controller.handleWebRemote("speed", request.args["v"][0])
		

def getLightState(session, controller):
	log("",None,"models.control::getLightState()")

	return {
		"result": True,
		"lightsEnabled": controller.lightsEnabled
	}

def getOptionValue(session, request, controller):
	log("",None,"models.control::getOptionValue() return = "+ ret)

	ret = controller.getOptionValue(request.args["get"][0])

	return {
		"result": True,
		"value": ret
	}

