# -*- coding: utf-8 -*-
"""
EnigmaLight Plugin by Speedy1985, 2014
 
https://github.com/speedy1985

Parts of the code is from other plugins:
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
#===============================================================================
# IMPORT
#===============================================================================
import sys
import os
import datetime
import shutil
import math
from Tools.Directories import fileExists, pathExists

from time import gmtime, strftime
from Screens.MessageBox import MessageBox

from enigma import addFont, loadPNG, loadJPG, getDesktop
from skin import loadSkin, readSkin
from Components.config import config
from Components.AVSwitch import AVSwitch

from EL_Helper_Singleton import Singleton
from . import _

vu4k = False
ultimo4k = False
if os.path.exists("/proc/stb/info/vumodel"):
	try:
		f = open("/proc/stb/info/vumodel",'r')
		model = f.read().strip()
		ultimo4k = 'ultimo4k' in model
		vu4k = '4k' in model
	except:
		pass
	f.close()

#===============================================================================
# import cProfile
#===============================================================================
try:
# Python 2.5
	import xml.etree.cElementTree as etree
#printl2("running with cElementTree on Python 2.5+", __name__, "D")
except ImportError:
	try:
		# Python 2.5
		import xml.etree.ElementTree as etree
	#printl2("running with ElementTree on Python 2.5+", __name__, "D")
	except ImportError:
		#printl2("something went wrong during etree import" + str(e), self, "E")
		etree = None
		raise Exception

def rmFile(fn):
	EnigmaLight_log("",None,"__common__::rmFile()")
	if os.path.isfile(fn):
		try:
			os.remove(fn)
			EnigmaLight_log("",None,"__common__::rmFile() > Delete old log file " +fn)
		except:
			EnigmaLight_log("",None,"__common__::rmFile() > Error delete " +fn)

#===============================================================================
# 
#===============================================================================
def EnigmaLight_log(level="", parent=None,string=""):
	if config.plugins.enigmalight.EnableEventLog.value != "0": #if not off

			try:
				
				if len(string) > 0:
					string = " > " + string

				if len(level) == 0:
					level = "D" #debug

				if parent is None:
					out = str(string)
				else:
					classname = str(parent.__class__).rsplit(".", 1)
					if len(classname) == 2:
						classname = classname[1]
						classname = classname.rstrip("\'>")
						classname += "::"

						out = str(classname) + str(sys._getframe(1).f_code.co_name) + str(string)
					else:
						out = str(parent) + str(string)
				
				if level == "D":
					print ("[EnigmaLight] [" + level + "] " + str(out))

					if config.plugins.enigmalight.EnableEventLog.value != "1":
						f = open("/tmp/enigmalight_gui.log","a")
						try:
							if string == None:
								string = ""

							f.write(strftime("%H:%M:%S") + " [%s] %s\r\n" % (str(level),str(out)))
						finally:
							f.close()

			except IOError:
				print "",strftime("%H:%M:%S"),"Logging-Error"

#===============================================================================
# 
#===============================================================================
def testInetConnectivity(target="http://www.google.com"):
	"""
	test if we get an answer from the specified url
	
	@param target:
	@return: bool
	"""

	EnigmaLight_log("",None," __common__::testInetConnectivity()")

	import urllib2
	from sys import version_info
	import socket

	try:
		opener = urllib2.build_opener()

		if version_info[1] >= 6:
			page = opener.open(target, timeout=2)
		else:
			socket.setdefaulttimeout(2)
			page = opener.open(target)
		if page is not None:
			return True
		else:
			return False
	except:
		return False

#===============================================================================
# 
#===============================================================================
def testDaemonConnectivity(ip, port):
	"""
	test if the light server (boblightd) is online on the specified port
	
	@param ip: e.g. 192.168.0.1
	@param port: e.g. 32400
	@return: bool
	"""
	EnigmaLight_log("",None,"__common__::testDaemonConnectivity()")

	import socket

	sock = socket.socket()

	try:
		sock.settimeout(5)
		sock.connect((ip, port))
		sock.close() 
		return True
	except socket.error, e:
		sock.close()

		return False

def loadEnigmalightSkin():
	"""
	loads the corresponding skin.xml file
	
	@param: none 
	@return none
	"""
	
	width = getDesktop(0).size().width()
	height = getDesktop(0).size().height()

	skin = "/usr/lib/enigma2/python/Plugins/Extensions/EnigmaLight/skins/default/skin-hd.xml" 

	#load fullhd skin when fullhd framebuffer is used.
	if width > 1280 and height > 720:
		skin = "/usr/lib/enigma2/python/Plugins/Extensions/EnigmaLight/skins/default/skin-fullhd.xml"
		
	if skin:
		loadSkin(skin)

	EnigmaLight_log("",None,"__common__::loadEnigmalightSkin() > Load Skin: " + skin)

	if skin:
		try:
			loadSkin(skin)
		except:
			from traceback import format_exc
			EnigmaLight_log("",None,"__common__::loadEnigmalightSkin > ERROR: " +format_exc() )
			try:
				open(getCrashFilePath(),"w").write(format_exc())
			except:
				pass

def registerEnigmalightFonts():
	"""
	registers fonts for skins
	
	@param: none 
	@return none
	"""
	EnigmaLight_log("",None,"__common__::registerEnigmalightFonts()")

	tree = Singleton().getSkinParamsInstance()

	for font in tree.findall('font'):
		path = str(font.get('path'))
		size = int(font.get('size'))
		name = str(font.get('name'))
		addFont(path, name, size, False)

#===============================================================================
# 
#===============================================================================
def checkDirectory(directory):
	"""
	checks if dir exists. if not it is added
	
	@param directory: e.g. /media/hdd/
	@return: none
	"""
	EnigmaLight_log("checking ... " + directory, "__ common__  > checkDirectory()")

	try:
		if not os.path.exists(directory):
			os.makedirs(directory)

	except Exception, ex:
		pass

#===============================================================================
# 
#===============================================================================
def getBoxInformation():

	EnigmaLight_log("",None,"__common__::getBoxInformation()")

	#readboxtype

	fpu = False
	brand = "Dream Multimedia"
	model = "unknown"
	chipset = "unknown"

	if fileExists("/etc/.box"):
		brand = "HDMU"
		f = open("/etc/.box",'r')
		model = f.readline().strip().lower()
		if model.startswith("et"):
			brand = "Xtrend"
		elif model.startswith("vu"):
			brand = "VuPlus"
		elif model.startswith("gb"):
			brand = "GigaBlue"
		elif model.startswith("ufs") or model.startswith("ufc"):
			brand = "Kathrein"
			if model in ("ufs910", "ufs922", "ufc960"):
				chipset = "SH4 @266MHz"
			else:
				chipset = "SH4 @450MHz"
		elif model.startswith("xpeed"):
			brand = "GoldenInterstar"
		elif model.startswith("topf"):
			brand = "Topfield"
			chipset = "SH4 @266MHz"
		elif model.startswith("azbox"):
			brand = "AZBox"
			f = open("/proc/stb/info/model",'r')
			model = f.readline().strip().lower()
			f.close()
			if model == "me":
				chipset = "SIGMA 8655"
			elif model == "minime":
				chipset = "SIGMA 8653"
			else:
				chipset = "SIGMA 8634"
		elif model.startswith("spark"):
			brand = "Fulan"
			chipset = "SH4 @450MHz"
	elif fileExists("/proc/stb/info/boxtype"):
		brand = "Xtrend"
		f = open("/proc/stb/info/boxtype",'r')
		model = f.readline().strip().lower()
		if model.startswith("et"):
			brand = "Xtrend"
		elif model.startswith("ini"):
			if model.endswith("9000ru"):
 				brand = "Sezam"
				model = "Marvel"
			elif model.endswith("5000ru"):
				brand = "Sezam"
				model = "hdx"
			elif model.endswith("1000ru"):
				brand = "Sezam"
				model = "hde"
			elif model.endswith("5000sv"):
				brand = "Miraclebox"
				model = "mbtwin"
			elif model.endswith("1000sv"):
				brand = "Miraclebox"
				model = "mbmini"
			elif model.endswith("1000de"):
				brand = "Golden Interstar"
				model = "xpeedlx"
			elif model.endswith("1000lx"):
				brand = "Golden Interstar"
				model = "xpeedlx"
			elif model.endswith("9000de"):
				brand = "Golden Interstar"
				model = "xpeedlx3"
			elif model.endswith("1000am"):
				brand = "Atemio"
				model = "5x00"
			elif model.endswith("de"):
				brand = "Golden Interstar"
			else:
				brand = "Venton"
				model = "Venton-hdx"
		elif model.startswith("xp"):
			brand = "MaxDigital"
		elif model.startswith("ixuss"):
			brand = "Medialink"
			model = model.replace(" ", "")
		elif model.startswith("formuler"):
			brand = "Formuler"
 		f.close()
	elif fileExists("/proc/stb/info/vumodel") and not fileExists("/proc/stb/info/boxtype"):
		brand = "VuPlus"
		f = open("/proc/stb/info/vumodel",'r')
		model = f.readline().strip().lower()
		f.close()
	elif fileExists("/proc/stb/info/azmodel"):
		brand = "AZBox"
		f = open("/proc/stb/info/model",'r')
		model = f.readline().strip().lower()
		f.close()
		if model == "me":
			chipset = "SIGMA 8655"
		elif model == "minime":
			chipset = "SIGMA 8653"
		else:
			chipset = "SIGMA 8634"
	elif fileExists("/proc/stb/info/hwmodel"):
		f = open("/proc/stb/info/hwmodel",'r')
		model = f.readline().strip().lower()
		f.close()
	elif fileExists("/proc/stb/info/gbmodel"):
		f = open("/proc/stb/info/gbmodel",'r')
		model = f.readline().strip().lower()
		f.close()
	elif fileExists("/proc/stb/info/model"):
		f = open("/proc/stb/info/model",'r')
		model = f.readline().strip().lower()
		f.close()
		if model == "tf7700hdpvr":
			brand = "Topfield"
			chipset = "SH4 @266MHz"
		elif model == "nbox":
			brand = "Advanced Digital Broadcast"
			chipset = "SH4 @266MHz"
		elif model in ("adb2850", "adb2849"):
			brand = "Advanced Digital Broadcast"
			chipset = "SH4 @450MHz"
		elif model in ("esi88", "uhd88", "dsi87"):
			brand = "SagemCom"
			chipset = "SH4 @450MHz"

	if fileExists("/proc/stb/info/chipset"):
		f = open("/proc/stb/info/chipset",'r')
		chipset = f.readline().strip()
		f.close()


	version = getBoxArch()
	arch_linux = "mipsel"
	try:
		arch_linux = os.popen("uname -m").read()
	except:
		pass

	boxData = (brand, model, chipset, arch_linux, version)

	EnigmaLight_log("",None,"__common__::getBoxInformation() > " + str(boxData))

	return boxData

#===============================================================================
# 
#===============================================================================
def getBoxArch():

	EnigmaLight_log("",None,"__common__::getBoxArch()")

	ARCH = "unknown"

	if (2, 6, 8) > sys.version_info > (2, 6, 6):
		ARCH = "oe16"

	if (2, 7, 4) > sys.version_info > (2, 7, 0):
		ARCH = "oe20"

	EnigmaLight_log("",None,"__common__::getBoxArch() > " + ARCH)

	return ARCH

def checkBinary():

	EnigmaLight_log("",None,"__common__::checkBinary()")

	if os.path.exists("/usr/bin/enigmalight"):
		return True
	else:
		return False

def checkSymbolic():

	EnigmaLight_log("",None,"__common__::checkSymbolic()")

	if not os.path.lexists("/usr/bin/enigmalight"):
		arch = getBoxArch()
		fpu  = False

		#read fpu
		if os.path.exists("/proc/cpuinfo"):
			filePointer = open("/proc/cpuinfo")
			cpuinfo = str(filePointer.read())
			#print cpuinfo

			if cpuinfo.find("FPU") != -1:
				fpu = True
			filePointer.close()

		if arch != "unknown":
			if not checkBinary():
				if fpu == True:
					config.plugins.enigmalight.bintype.setValue("enigmalight_" + arch + "_hf") #hardfloat, fpu support
				else:
					config.plugins.enigmalight.bintype.setValue("enigmalight_" + arch + "_sf") #softfloat for receivers without fpu

				config.plugins.enigmalight.save()

		setSymbolic()

def setSymbolic():
	EnigmaLight_log("",None,"__common__::setSymbolic()")
	arch = os.popen("uname -m").read()
	if 'mips' in arch:
		binary = "/home/elight-addons/usr/bin/enigmalight_mips"
		if os.path.exists(binary):
			os.system("chmod 755 %s" % binary)
			LinkFile(binary, "/usr/bin/enigmalight")
		binary = "/home/elight-addons/usr/bin/elighttalk_mips"
		if os.path.exists(binary):
			os.system("chmod 755 %s" % binary)
			LinkFile(binary, "/usr/bin/elighttalk")
	elif 'armv7l' in arch:
		binary = "/home/elight-addons/usr/bin/enigmalight_arm"
		if config.plugins.enigmalight.bintype_arm.value == "2":
			file = "/home/elight-addons/usr/bin/enigmalight_arm_ultimo4k"
			if os.path.exists(file):
				binary = file
		if os.path.exists(binary):
			os.system("chmod 755 %s" % binary)
			LinkFile(binary, "/usr/bin/enigmalight")
		binary = "/home/elight-addons/usr/bin/elighttalk_arm"
		if os.path.exists(binary):
			os.system("chmod 755 %s" % binary)
			LinkFile(binary, "/usr/bin/elighttalk")
	elif 'sh4' in arch:
		binary = "/home/elight-addons/usr/bin/enigmalight_sh4"
		if os.path.exists(binary):
			os.system("chmod 755 %s" % binary)
			LinkFile(binary, "/usr/bin/enigmalight")
		binary = "/home/elight-addons/usr/bin/elighttalk_sh4"
		if os.path.exists(binary):
			os.system("chmod 755 %s" % binary)
			binary = "/home/elight-addons/usr/bin/elighttalk_sh4"
			LinkFile(binary, "/usr/bin/elighttalk")
	else:
		EnigmaLight_log("__common__::setSymbolic() > ERROR!")
	#LinkFile("/home/elight-addons/usr/bin/"+ config.plugins.enigmalight.bintype.getValue(), "/usr/bin/enigmalight")

def LinkFile(src, dst):
	EnigmaLight_log("",None,"__common__::LinkFile() > Create symlink: "+ src + " >>> " + dst)

	try:
		if os.path.lexists(dst):
			os.unlink(dst)

		if (os.symlink(src, dst)):
			EnigmaLight_log("__common__::LinkFile() > Create symlink: Done!")

	except Exception, e:
		raise

def DeleteLink(dst):
	try:
		if os.path.exists(dst):
			EnigmaLight_log("",None,"__common__::DeleteLink() > Delete symlink. "+ dst)
			if os.unlink(dst):
					EnigmaLight_log("",None,"__common__::DeleteLink() > Delete Done!")
	except Exception, e:
		raise

#===============================================================================
#
#===============================================================================
def prettyFormatTime(msec):
	EnigmaLight_log("",None,"__common__::prettyFormatTime()")

	seconds = msec / 1000
	hours = seconds // (60 * 60)
	seconds %= (60 * 60)
	minutes = seconds // 60
	seconds %= 60
	hrstr = "hour"
	minstr = "min"
	secstr = "sec"

	if hours != 1:
		hrstr += "s"

	if minutes != 1:
		minstr += "s"

	if seconds != 1:
		secstr += "s"

	if hours > 0:
		return "%i %s %02i %s %02i %s" % (hours, hrstr, minutes, minstr, seconds, secstr)

	elif minutes > 0:
		return "%i %s %02i %s" % (minutes, minstr, seconds, secstr)

	else:
		return "%i %s" % (seconds, secstr)

#===============================================================================
#
#===============================================================================
def formatTime(msec):
	EnigmaLight_log("",None,"__common__::formatTime()")

	seconds = msec / 1000
	hours = seconds // (60 * 60)
	seconds %= (60 * 60)
	minutes = seconds // 60
	seconds %= 60

	if hours > 0:
		return "%i:%02i:%02i" % (hours, minutes, seconds)

	elif minutes > 0:
		return "%i:%02i" % (minutes, seconds)

	else:
		return "%i" % seconds

#===============================================================================
# 
#===============================================================================
def getScale():
	EnigmaLight_log("",None,"__common__::getScale()")
	return AVSwitch().getFramebufferScale()

#===========================================================================
# 
#===========================================================================
def checkXmlFile(location):
	EnigmaLight_log("",None,"__common__::checkXmlFile()")
	if not os.path.isfile(location):
		with open(location, "a") as writefile:
			writefile.write("<xml></xml>")
#===========================================================================
# 
#===========================================================================
def getXmlContent(location):
	EnigmaLight_log("",None,"__common__::getXmlContent()")
	checkXmlFile(location)

	xml = open(location).read()

	tree = None

	try:
		tree = etree.fromstring(xml)
	except:
		from traceback import format_exc
		EnigmaLight_log("Error:",format_exc() )
		try:
			open(getCrashFilePath(),"w").write(format_exc())
		except:
			pass
	return tree

#===========================================================================
# 
#===========================================================================
def writeXmlContent(content, location):
	EnigmaLight_log("",None,"__common__::writeXmlContent()")
	indented = indentXml(content)
	xmlString = etree.tostring(indented)
	fobj = open(location, "w")
	fobj.write(xmlString)
	fobj.close()

#===========================================================================
# 
#===========================================================================
def indentXml(elem, level=0, more_sibs=False):
	EnigmaLight_log("",None,"__common__::indentXml()")
	i = "\n"
	if level:
		i += (level - 1) * '  '
	num_kids = len(elem)
	if num_kids:
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
			if level:
				elem.text += '  '
		count = 0
		for kid in elem:
			indentXml(kid, level + 1, count < num_kids - 1)
			count += 1
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
			if more_sibs:
				elem.tail += '  '
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i
			if more_sibs:
				elem.tail += '  '
	return elem

#===========================================================================
#
#===========================================================================
def durationToTime(duration):
	EnigmaLight_log("",None,"__common__::durationToTime()")

	m, s = divmod(int(duration)/1000, 60)
	h, m = divmod(m, 60)

	return "%d:%02d:%02d" % (h, m, s)


#===========================================================================
# 
#===========================================================================
def loadPicture(filename):
	EnigmaLight_log("",None,"__common__::loadPicture()")
	ptr = None
	if filename is None:
		return ptr

	if filename[-4:] == ".png":
		ptr = loadPNG(filename)
	elif filename[-4:] == ".jpg":
		ptr = loadJPG(filename)
		if not ptr:
			# kind of fallback if filetype is declared wrong
			ptr = loadPNG(filename)
	
	return ptr

def getRGB(r,g,b):
	EnigmaLight_log("",None,"__common__::getRGB()")
	return (r<<16)|(g<<8)|b

def Clamp(value,minv,maxv):
	EnigmaLight_log("",None,"__common__::Clamp()")
	if value > maxv:
		value = maxv
	elif value < minv:
		value = minv
	return value

def getAspect():
	EnigmaLight_log("",None,"__common__::getAspect()")
	val = AVSwitch().getAspectRatioSetting()
	return val/2

def rgbToHex(r,g,b):
	EnigmaLight_log("",None,"__common__::rgbToHex()")
	hexchars = "0123456789ABCDEF"
	return hexchars[r / 16] + hexchars[r % 16] + hexchars[g / 16] + hexchars[g % 16] + hexchars[b / 16] + hexchars[b % 16]

def validIP(address):
	EnigmaLight_log("",None,"__common__::validIP()")
	parts = address.split(".")
	if len(parts) != 4:
		return False
	for item in parts:
		if not 0 <= int(item) <= 255:
			return False
	return True

def showMessage(session, message, msg_type, timeout = 3):
	EnigmaLight_log("",None,"__common__::showMessage()")
	if session != None:
		s = "" 
		if msg_type == "I":
			msg_type = MessageBox.TYPE_INFO
			s = "" 
		elif msg_type == "W":
			s = "Warning: " 
			msg_type = MessageBox.TYPE_WARNING
		elif msg_type == "E":
			msg_type = MessageBox.TYPE_ERROR
		else:
			msg_type = MessageBox.TYPE_INFO
		
		session.open(MessageBox, _(s + message), msg_type, timeout)

def showError(session, ex, msg_type, timeout = 10):
	EnigmaLight_log("",None,"__common__::showError > UNEXPECTED ERROR: %s" %(str(ex)))

	if session != None:
		session.open(MessageBox, _("UNEXPECTED ERROR: \n\n") + str(ex), MessageBox.TYPE_ERROR , timeout)