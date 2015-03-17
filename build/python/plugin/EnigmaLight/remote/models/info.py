# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Plugins.Extensions.EnigmaLight.__init__ import _

from Components.config import config

from Tools.Directories import fileExists, pathExists
from time import time, localtime, strftime
from twisted.web import version

import os
import sys
import time
import string

def formatIp(ip):
	if ip is None or len(ip) != 4:
		return "0.0.0.0"
	return "%d.%d.%d.%d" % (ip[0], ip[1], ip[2], ip[3])

def getBasePath():
	path = os.path.dirname(sys.modules[__name__].__file__)
	chunks = path.split("/")
	chunks.pop()
	chunks.pop()
	return "/".join(chunks)

def getPublicPath(file = ""):
	return getBasePath() + "/remote/public/" + file

def getViewsPath(file = ""):
	return getBasePath() + "/remote/views/" + file

def getCurrentTime():
	t = time.localtime()
	return {
		"status": True,
		"time": "%2d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
	}

def getFrontendStatus():
	return {}

def getStatusInfo(self, controller):
	statusinfo = {}
	
	statusinfo['lights_onoff'] = controller.getOptionValue("lights_onoff")
	statusinfo['current_mode'] = controller.getOptionValue("mode")

	#Options
	statusinfo['option_brightness'] = controller.getOptionValue("brightness")
	statusinfo['option_brightnessmin'] = controller.getOptionValue("brightnessmin")
	statusinfo['option_brightnessmax'] = controller.getOptionValue("brightnessmax")
	statusinfo['option_saturation'] = controller.getOptionValue("saturation")
	statusinfo['option_saturationmin'] = controller.getOptionValue("saturationmin")
	statusinfo['option_saturationmax'] = controller.getOptionValue("saturationmax")
	statusinfo['option_speed'] = controller.getOptionValue("speed")
	statusinfo['option_gamma'] = controller.getOptionValue("gamma")

	return statusinfo


