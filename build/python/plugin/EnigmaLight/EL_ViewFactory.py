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
#=================================
#IMPORT
#=================================
import copy

from EL_Helper_Singleton import Singleton

from __common__ import EnigmaLight_log as log


def translateValues(value):
	# translate xml value to real true or false
	if value == "true" or value == "True":
		value = True

	if value == "false" or value == "False":
		value = False

	return value

#===========================================================================
#
#===========================================================================
def getGuiElements():
	tree = Singleton().getSkinParamsInstance()

	guiElements = {}
	for guiElement in tree.findall('guiElement'):
		name = str(guiElement.get('name'))
		path = str(guiElement.get('path'))
		guiElements[name] = path

	return guiElements
