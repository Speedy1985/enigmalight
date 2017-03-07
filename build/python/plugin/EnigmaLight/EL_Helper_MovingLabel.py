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
#=================================
#IMPORT
#=================================

#noinspection PyUnresolvedReferences
from enigma import eTimer
from Components.Label import MultiColorLabel
from skin import parseColor
from __common__ import EnigmaLight_log as log
from EL_Helper_Singleton import Singleton

class EL_Helper_HorizontalMenu(object):

	#===============================================================================
	#
	#===============================================================================
	def setHorMenuElements(self, depth):
		self.depth = depth

		self.setRangeList()

		highlighted = parseColor("#e17e76")
		normal = parseColor("#ffffff")

		for i in self.rangeList:
			self[str(i)] = MultiColorLabel()
			self[str(i)].foreColors = [highlighted, normal]
			self[str(i)].show()

	#===============================================================================
	#
	#===============================================================================
	def setRangeList(self):
		rangeList = []
		for i in range(1,(self.depth+1)):
			rangeList.append("-" + str(i))
			rangeList.append("+" + str(i))

		rangeList.append("0")

		self.rangeList = rangeList

	#===============================================================================
	#
	#===============================================================================
	def translateNames(self):
		for i in self.rangeList:
			self.translatePositionToName(int(i), str(i))

	#===============================================================================
	#
	#===============================================================================
	def refreshOrientationHorMenu(self, value=None):
		if value == 1:
			self["menu"].selectNext()
		elif value == -1:
			self["menu"].selectPrevious()

		currentIndex = self["menu"].index
		content = self["menu"].list

		count = len(content)

		self[self.translatePositionToName(0)].setText(content[currentIndex][0])
		self[self.translatePositionToName(0)].setForegroundColorNum(0)
		for i in range(1,(self.depth+1)):
			targetIndex = currentIndex + i
			if targetIndex < count:
				self[self.translatePositionToName(+i)].setText(content[targetIndex][0])
			else:
				firstResult = targetIndex - count
				
				if firstResult >= count:
					firstResult = currentIndex

				self[self.translatePositionToName(+i)].setText(content[firstResult][0])

			targetIndex = currentIndex - i
			if targetIndex >= 0:
				self[self.translatePositionToName(-i)].setText(content[targetIndex][0])
			else:
				secondResult = count + targetIndex

				self[self.translatePositionToName(-i)].setText(content[secondResult][0])

		return True

	_translatePositionToName = {}
	#===============================================================================
	#
	#===============================================================================
	def translatePositionToName(self, name, value=None):
		if value is None:
			
			return self._translatePositionToName[name]
		else:
			self._translatePositionToName[name] = value
