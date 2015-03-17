# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Tools.Directories import fileExists

from models.info import getBasePath, getPublicPath, getViewsPath

from base import BaseController
from control import WebController
from ajax import AjaxController
from api import ApiController

from twisted.web import static, http

class RootController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path)
		self.session = session
		self.controller = None

		self.putChild("control", WebController(session))
		self.putChild("ajax", AjaxController(session))
		self.putChild("api", ApiController(session))
		self.putChild("js", static.File(getPublicPath() + "/js"))
		self.putChild("css", static.File(getPublicPath() + "/css"))
		self.putChild("images", static.File(getPublicPath() + "/images"))

	def getCInstance(self):
		return instance

	def setCInstance(self, instance):
		self.instance = instance
		BaseController.instance = self.instance

	# this function will be called before a page is loaded
	def prePageLoad(self, request):
		pass

	# the "pages functions" must be called P_pagename
	# example http://boxip/index => P_index
	def P_index(self, request):
		mode = ''
		if "mode" in request.args.keys():
			mode = request.args["mode"][0]
		uagent = request.getHeader('User-Agent')
		return {}

	def P_settings(self, request):
		return {}

	def P_status(self, request):
		return {}

	def P_controller(self, request):
		return {}

	def P_about(self, request):
		return {}
