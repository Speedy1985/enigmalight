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
class Singleton(object):
	"""
	singlton config object
	"""
	__we_are_one = {}
	__eInstance = ""
	__logFileInstance = ""
	__skinParamsInstance = ""

	def __init__(self):
		#implement the borg patter (we are one)
		self.__dict__ = self.__we_are_one

	def getEInstance(self, value=None):
		"""with value you can set the singleton content"""
		if value:
			self.__eInstance = value
		else:
			pass

		return self.__eInstance

	def getSkinParamsInstance(self, value=None):
		"""with value you can set the singleton content"""
		if value:
			self.__skinParamsInstance = value
		else:
			pass

		return self.__skinParamsInstance
