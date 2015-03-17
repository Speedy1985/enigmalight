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

from models.info import getFrontendStatus, getStatusInfo
from models.control import setLightOn, setLightOff, setOption

from base import BaseController

### All functions in this python document will forwards the the above models ###

class WebController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path)
		self.session = session

	def prePageLoad(self, request):
		request.setHeader("content-type", "text/xml")

	def testMandatoryArguments(self, request, keys):
		for key in keys:
			if key not in request.args.keys():
				return {
					"result": False,
					"message": _("Missing mandatory parameter '%s'") % key
				}

			if len(request.args[key][0]) == 0:
				return {
					"result": False,
					"message": _("The parameter '%s' can't be empty") % key
				}

		return None

	def P_statusinfo(self, request):
		# we don't need to fill logs with this api (it's called too many times)
		self.suppresslog = True
		return getStatusInfo(self, BaseController.instance)

	def P_light(self, request):
		#if "set" not in request.args.keys() or request.args["set"][0] == "state":
		#	return getLightStatus()
		if request.args["set"][0] == "on":
			return setLightOn(self.session, BaseController.instance)
		elif request.args["set"][0] == "off":
			return setLightOff(self.session, BaseController.instance)
		
		res = getLightState()
		res["result"] = False
		res["message"] = _("Unknown lights command %s") % request.args["set"][0]
		return res

	def P_option(self, request):
		if "set" in request.args.keys():
			return setOption(self.session, request, BaseController.instance)
		elif "get" in request.args.keys():
			return getOptionValue(self.session, request, BaseController.instance)

		res = {}
		res["result"] = False
		res["message"] = _("Unknown option command")
		return res
		
	def P_test(self, request):
		print "instance = " + str(BaseController.instance)
		print "instance.mode = " + str(BaseController.instance.current_mode)
