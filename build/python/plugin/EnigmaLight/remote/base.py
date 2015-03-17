# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Plugins.Extensions.EnigmaLight.__common__ import EnigmaLight_log as log, rgbToHex, showMessage, showError

from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS

from models.info import getBasePath, getPublicPath, getViewsPath

from twisted.web import server, http, static, resource, error
from Cheetah.Template import Template

import imp
import sys
import json
import gzip
import cStringIO

class BaseController(resource.Resource):
	isLeaf = False
	
	def __init__(self, path = ""):
		log("",self)
		resource.Resource.__init__(self)
		
		self.path = path
		self.isJson = False
		self.isCustom = False
		self.isGZ = False
		self.instance = None
	
	def error404(self, request):
		log("",self)
		request.setHeader("content-type", "text/html")
		request.setResponseCode(http.NOT_FOUND)
		request.write("<html><head><title>Enigmalight Webremote</title></head><body><h1>Error 404: Page not found</h1><br />The requested URL was not found on this server.</body></html>")
		request.finish()
		
	def loadTemplate(self, path, module, args):
		log("",self)
		if fileExists(getViewsPath(path + ".py")) or fileExists(getViewsPath(path + ".pyo")):
			if fileExists(getViewsPath(path + ".pyo")):
				template = imp.load_compiled(module, getViewsPath(path + ".pyo"))
			else:
				template = imp.load_source(module, getViewsPath(path + ".py"))
			mod = getattr(template, module, None)
			if callable(mod):
				return str(mod(searchList=args))
		elif fileExists(getViewsPath(path + ".tmpl")):
			return str(Template(file=getViewsPath(path + ".tmpl"), searchList=[args]))
		return None
		
	def getChild(self, path, request):
		log("",self)
		return self.__class__(self.session, path)
		
	def compressBuf(self, buf):
		log("",self)
		zbuf = cStringIO.StringIO()
		zfile = gzip.GzipFile(mode = 'wb',  fileobj = zbuf, compresslevel = 6)
		zfile.write(buf)
		zfile.close()
		return zbuf.getvalue()
		
	def render(self, request):
		log("",self)
		# cache data
		path = self.path
		isJson = self.isJson
		isCustom = self.isCustom
		isGZ = self.isGZ
		
		if self.path == "":
			self.path = "index"
		
		self.suppresslog = False
		self.path = self.path.replace(".", "")
		func = getattr(self, "P_" + self.path, None)

		if callable(func):

			request.setResponseCode(http.OK)
			
			# call prePageLoad function if exist
			plfunc = getattr(self, "prePageLoad", None)
			if callable(plfunc):
				plfunc(request)
				
			data = func(request)
			if data is None:
#				if not self.suppresslog:
#					log("",self,"page " + request.uri + " without content")
				self.error404(request)
			elif self.isCustom:
#				if not self.suppresslog:
#					log("",self,"page " + request.uri + " ok (custom)")
				request.write(data)
				request.finish()
			elif self.isJson:
#				if not self.suppresslog:
#					log("",self,"page " + request.uri + " ok (json)")
				supported=[]
				if self.isGZ:
					acceptHeaders = request.requestHeaders.getRawHeaders('Accept-Encoding', [])
					supported = ','.join(acceptHeaders).split(',')
				if 'gzip' in supported:
					encoding = request.responseHeaders.getRawHeaders('Content-Encoding')
					if encoding:
						encoding = '%s,gzip' % ','.join(encoding)
					else:
						encoding = 'gzip'
					request.responseHeaders.setRawHeaders('Content-Encoding',[encoding])
					compstr = self.compressBuf(json.dumps(data))
					request.setHeader('Content-Length', '%d' % len(compstr))
					request.write(compstr)
				else:
					request.setHeader("content-type", "text/plain")
					request.write(json.dumps(data))
				request.finish()
			elif type(data) is str:
#				if not self.suppresslog:
#					log("",self,"page " + request.uri + " ok (simple string)")
				request.setHeader("content-type", "text/plain")
				request.write(data)
				request.finish()
			else:
#				log("",self,"page " + request.uri + " ok (cheetah template)")
				module = request.path
				if module[-1] == "/":
					module += "index"
				elif module[-5:] != "index" and self.path == "index":
					module += "/index"
				module = module.strip("/")
				module = module.replace(".", "")
				out = self.loadTemplate(module, self.path, data)
				if out is None:
					log("",self,"] ERROR! Template not found for page " + request.uri)
					self.error404(request)
				else:
					request.write(out)
					request.finish()
				
		else:
			log("",self,"page " + request.uri  + " not found")

			self.error404(request)
		
		# restore cached data
		self.path = path
		self.isJson = isJson
		self.isCustom = isCustom
		self.isGZ = isGZ
		
		return server.NOT_DONE_YET

	def prepareMainTemplate(self):
		# here will be generated the dictionary for the main template
		ret = getCollapsedMenus()
		
		extras = []
		extras.append({ 'key': 'ajax/settings','description': _("Settings")})
		
		ret['extras'] = extras

		return ret
