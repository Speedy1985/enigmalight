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

from __common__ import EnigmaLight_log as log

#===============================================================================
# GLOBAL
#===============================================================================
gPlugins = []

#===============================================================================
# 
#===============================================================================
def registerPlugin(plugin):
	ps = []
	if type(plugin) is list:
		ps = plugin
	else:
		ps.append(plugin)
	for p in ps:
		if p not in gPlugins:
			gPlugins.append(p)
#===============================================================================
# 
#===============================================================================
def getPlugins(where = None):
	if where is None:
		return gPlugins
	else:
		plist = []
		for plugin in gPlugins:
			if plugin.where == where:
				plist.append(plugin)
		
		plist.sort(key=lambda x: x.weight)
		return plist
	
#===============================================================================
# 
#===============================================================================
def getPlugin(pid, where):
	for plugin in gPlugins:
		if plugin.pid == pid and plugin.where == where:
			

			return plugin

	return None

#===============================================================================
# 
#===============================================================================
class Plugin(object):
	# constants
	MENU_MAIN = 1
	MENU_TUNING = 2
	MENU_SETTINGS = 3
	MENU_MOODLAMP = 4

	pid = None
	name = None
	desc = None
	start = None
	fnc = None
	where = None

	#===========================================================================
	# 
	#===========================================================================
	def __init__(self, pid, name=None, desc=None, start=None, where=None, fnc=None):
		self.pid = pid
		self.name = name
		if desc is None:
			self.desc = self.name
		else:
			self.desc = desc
		self.start = start
		self.fnc = fnc
		self.where = where
