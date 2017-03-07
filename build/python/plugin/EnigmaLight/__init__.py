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
#===============================================================================
# IMPORT
#===============================================================================
import os
import gettext
from time import localtime, mktime
from enigma import getDesktop

from Components.config import config
from Components.config import ConfigSubsection
from Components.config import ConfigSelection
from Components.config import ConfigInteger
from Components.config import ConfigSubList
from Components.config import ConfigText
from Components.config import ConfigYesNo
from Components.config import ConfigOnOff
from Components.config import ConfigSlider
from Components.config import ConfigIP
from Components.config import ConfigFloat
from Components.config import ConfigClock
from Components.config import ConfigDirectory
from Components.config import ConfigFile
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN, SCOPE_CURRENT_SKIN, SCOPE_LANGUAGE

def localeInit():
	#log("",None,"__init__::localeInit()")
	lang = language.getLanguage()
	os.environ["LANGUAGE"] = lang[:2]
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain("EnigmaLight", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/EnigmaLight/locale/"))

localeInit()
language.addCallback(localeInit)

#===============================================================================
# 
#===============================================================================
def _(txt):
	if len(txt) == 0:
		return ""
	text = gettext.dgettext("EnigmaLight", txt)
	if text == txt:
		text = gettext.gettext(txt)
	return text

from EL_Helper_Singleton import Singleton

from __common__ import registerEnigmalightFonts, loadEnigmalightSkin, getBoxInformation , showError, EnigmaLight_log as log, getXmlContent

#===============================================================================
#
#===============================================================================

now = [x for x in localtime()]
now[3] = 20
now[4] = 00
def_start = mktime(now)
now[3] = 23
now[4] = 00
def_end = mktime(now)

# the currentVersion should be renewed every major update
enigmalight_config = "/etc/enigma2/enigmalight_config"
currentVersion  = "0.3-rc0"
defaultURL  = "http://www.enigmalight.net/updates/"
defaultUpdateXML= "update.xml"
crashFile= "/tmp/enigmalight_gui_crash.txt"

defaultPluginFolderPath = resolveFilename(SCOPE_PLUGINS, "Extensions/EnigmaLight/")
defaultSkinsFolderPath= resolveFilename(SCOPE_PLUGINS, "Extensions/EnigmaLight/skins")
defaultConfigfilePath = "/etc/enigmalight.conf"

###################################################################################################################

#===============================================================================
# 
#===============================================================================

config.plugins.enigmalight = ConfigSubsection()

config.plugins.enigmalight.about = ConfigSelection(default = "1", choices = [("1", " ")]) # need this for seperator in settings
config.plugins.enigmalight.clickOK = ConfigSelection(default = "1", choices = [("1", " ")])
config.plugins.enigmalight.sampleBackground = ConfigYesNo(default = False)
config.plugins.enigmalight.sampleBackground_mvi = ConfigSelection(default = "rgb_test", choices = [
("rgb_test", _("RGB Test")),("blackbar_test", _("Blackbar Test (horizontal)")),("blackbar_test2", _("Blackbar Test (vertical)")),("wallpaper_and", _("Blue wallpaper")),("bars_test", _("Bars Test")),("white", _("Solid: White")),
("aquamarine", _("Solid: Aquamarine")),("blue", _("Solid: Blue")),
("royalblue", _("Solid: Royalblue")),("red", _("Solid: Red")),
("green", _("Solid: Green")),("gray", _("Solid: Gray")),
("lightgray", _("Solid: Lightgray")),("magenta", _("Solid: Magenta")),
("yellow", _("Solid: Yellow")),("yellowdark", _("Solid: Dark yellow")),
("circles", _("Circles")),("rose", _("Rose"))])

config.plugins.enigmalight.checkForUpdateOnStartup  = ConfigYesNo(default = True)
config.plugins.enigmalight.version  = ConfigText(default = currentVersion)

config.plugins.enigmalight.bintype  = ConfigSelection(default = "enigmalight_oe20_hf", choices = [
("enigmalight_oe20_hf", _("Enigmalight OE2.0 with fpu support")),
("enigmalight_oe20_sf", _("Enigmalight OE2.0")),
("enigmalight_oe16_hf", _("Enigmalight OE1.6 with fpu support")),
("enigmalight_oe16_sf", _("Enigmalight OE1.6 "))])

config.plugins.enigmalight.arch = ConfigText(default = "")

config.plugins.enigmalight.showstatusbar = ConfigYesNo(default = True)
config.plugins.enigmalight.showstatusbar_tuning = ConfigYesNo(default = True) #remove statusbar from colortuning screen

config.plugins.enigmalight.remote_server = ConfigOnOff(default=True)
config.plugins.enigmalight.remote_port = ConfigInteger(default = 1414, limits=(1, 65535))

config.plugins.enigmalight.pluginfolderpath = ConfigText(default = defaultPluginFolderPath)
config.plugins.enigmalight.url = ConfigText(default = defaultURL)
config.plugins.enigmalight.updatexml = ConfigText(default = defaultUpdateXML)

config.plugins.enigmalight.debug = ConfigOnOff(default=False)
config.plugins.enigmalight.EnableEventLog = ConfigSelection(choices = [("0", _("off")), ("1", _("Debug -> Console")), ("2", _("Debug -> Console + Logfile"))], default = "0")
config.plugins.enigmalight.configfilepath = ConfigDirectory(default = defaultConfigfilePath, visible_width = 50)

config.plugins.enigmalight.update = ConfigOnOff(default=False)
config.plugins.enigmalight.server = ConfigOnOff(default=False)
config.plugins.enigmalight.mode = ConfigSelection(default = "2", choices = [
("1", _("Moodlamp")),
("2", _("Dynamic"))])

config.plugins.enigmalight.standbymode = ConfigSelection(default = "0", choices = [
("0", _("Lights off")),
("1", _("Moodlamp"))])

config.plugins.enigmalight.moodlamp_fader_brightness = ConfigSlider(default=100, increment=1, limits=(1,255))
config.plugins.enigmalight.moodlamp_static_color_r = ConfigSlider(default=255, increment=1, limits=(0,255))
config.plugins.enigmalight.moodlamp_static_color_g = ConfigSlider(default=025, increment=1, limits=(0,255))
config.plugins.enigmalight.moodlamp_static_color_b = ConfigSlider(default=002, increment=1, limits=(0,255))

config.plugins.enigmalight.moodlamp_static_color_r_int = ConfigInteger(default = 255, limits=(0, 255))
config.plugins.enigmalight.moodlamp_static_color_g_int = ConfigInteger(default = 025, limits=(0, 255))
config.plugins.enigmalight.moodlamp_static_color_b_int = ConfigInteger(default = 002, limits=(0, 255))

config.plugins.enigmalight.address = ConfigIP(default=[127,0,0,1])
config.plugins.enigmalight.android = ConfigOnOff(default=False)
config.plugins.enigmalight.android_port  = ConfigInteger(default = 50000, limits=(1, 65535))

config.plugins.enigmalight.port = ConfigInteger(default = 19333, limits=(1, 65535))
config.plugins.enigmalight.network_onoff = ConfigOnOff(default=False)

config.plugins.enigmalight.moodlamp_static = ConfigOnOff(default=False)
config.plugins.enigmalight.moodlamp_mode = ConfigSelection(default = "1", choices = [
("1", _("Static color")),
("3", _("RGBTest")),
("4", _("Color fader")),
("5", _("Rainbow"))])

config.plugins.enigmalight.use_live_adjust = ConfigSelection(default = "false", choices = [
("false", _("Automatic")),
("true", _("Manual"))])

config.plugins.enigmalight.adjustr = ConfigSlider(default=255, increment=1, limits=(0,255))
config.plugins.enigmalight.adjustg = ConfigSlider(default=255, increment=1, limits=(0,255))
config.plugins.enigmalight.adjustb = ConfigSlider(default=255, increment=1, limits=(0,255))

config.plugins.enigmalight.threshold = ConfigSelection(default = "0", choices = [("0", "0"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("10", "10"), ("11", "11"), ("12", "12"), ("13", "13"), ("14", "14"), ("15", "15"), ("16", "16"), ("17", "17"), ("18", "18"), ("19", "19"), ("20", "20"), ("21", "21"), ("22", "22"), ("23", "23"), ("24", "24"), ("25", "25"), ("26", "26"), ("27", "27"), ("28", "28"), ("29", "29"), ("30", "30"), ("31", "31"), ("32", "32"), ("33", "33"), ("34", "34"), ("35", "35"), ("36", "36"), ("37", "37"), ("38", "38"), ("39", "39"), ("40", "40"), ("41", "41"), ("42", "42"), ("43", "43"), ("44", "44"), ("45", "45"), ("46", "46"), ("47", "47"), ("48", "48"), ("49", "49"), ("50", "50"), ("51", "51"), ("52", "52"), ("53", "53"), ("54", "54"), ("55", "55"), ("56", "56"), ("57", "57"), ("58", "58"), ("59", "59"), ("60", "60"), ("61", "61"), ("62", "62"), ("63", "63"), ("64", "64"), ("65", "65"), ("66", "66"), ("67", "67"), ("68", "68"), ("69", "69"), ("70", "70"), ("71", "71"), ("72", "72"), ("73", "73"), ("74", "74"), ("75", "75"), ("76", "76"), ("77", "77"), ("78", "78"), ("79", "79"), ("80", "80"), ("81", "81"), ("82", "82"), ("83", "83"), ("84", "84"), ("85", "85"), ("86", "86"), ("87", "87"), ("88", "88"), ("89", "89"), ("90", "90"), ("91", "91"), ("92", "92"), ("93", "93"), ("94", "94"), ("95", "95"), ("96", "96"), ("97", "97"), ("98", "98"), ("99", "99"), ("100", "100")])
config.plugins.enigmalight.cluster = ConfigSelection(default = "1", choices = [("1", "1"),("2", "2"),("3", "3"),("4", "4"),("5", "5"),("6", "6"),("7", "7"),("8", "8"),("9", "9"),("10", "10")])

config.plugins.enigmalight.autostart = ConfigSelection(default = "0", choices = [
("0", _("Off")),("1", _("Start server on boot")),("2", _("Start Dynamic on boot")), ("3", _("Start Moodlamp on boot"))])

config.plugins.enigmalight.presets = ConfigSelection(default = "1", choices = [
("0", _("Custom Profile 0")),("1", _("Custom Profile 1")),("2", _("Custom Profile 2")), ("3", _("Custom Profile 3")), ("4", _("Custom Profile 4")),("5", _("Custom Profile 5")),
("6", _("Custom Profile 6"))])


config.plugins.enigmalight.interval = ConfigSelection(default = "0.10", choices = [
("0.01", "0.01"), ("0.02", "0.02"), ("0.03", "0.03"), ("0.04", "0.04"),("0.05", "0.05"),("0.06", "0.06"), ("0.07", "0.07"), ("0.08", "0.08"),("0.09", "0.09"),("0.10", "0.10"),("0.11", "0.11"),("0.12", "0.12"),("0.13", "0.13"),("0.14", "0.14"),("0.15", "0.15"),("0.16", "0.16"),("0.17", "0.17"),("0.18", "0.18"),("0.19", "0.19")
,("0.20", "0.20"),("0.21", "0.21"),("0.22", "0.22"),("0.23", "0.23"),("0.24", "0.24"),("0.25", "0.25"),("0.26", "0.26"),("0.27", "0.27"),("0.28", "0.28"),("0.29", "0.29"),("0.30", "0.30"),("0.31", "0.31"),("0.32", "0.32"),("0.33", "0.33"),("0.34", "0.34"),("0.35", "0.35"),("0.36", "0.36"),("0.37", "0.37"),("0.38", "0.38"),("0.39", "0.39")
,("0.40", "0.40"),("0.41", "0.41"),("0.42", "0.42"),("0.43", "0.43"),("0.44", "0.44"),("0.45", "0.45"),("0.46", "0.46"),("0.47", "0.47"),("0.48", "0.48"),("0.49", "0.49")
,("0.50", "0.50")])


config.plugins.enigmalight.value = ConfigSelection(default = "1.0", choices = [
("0.0", "0.0"),("0.1", "0.1"),("0.2", "0.2"),("0.3", "0.3"),("0.4", "0.4"),("0.5", "0.5"), 
("0.6", "0.6"),("0.7", "0.7"),("0.8", "0.8"),("0.9", "0.9"),("1.0", "1.0"),("1.1", "1.1"),
("1.2", "1.2"),("1.3", "1.3"),("1.4", "1.4"),("1.5", "1.5"),("1.6", "1.6"),("1.7", "1.7"),
("1.8", "1.8"),("1.9", "1.9"),("2.0", "2.0"),("2.1", "2.1"),("2.2", "2.2"),("2.3", "2.3"),
("2.4", "2.4"),("2.5", "2.5"),("2.6", "2.6"),("2.7", "2.7"),("2.8", "2.8"),("2.9", "2.9"),
("3.0", "3.0"),("3.1", "3.1"),("3.2", "3.2"),("3.3", "3.3"),("3.4", "3.4"),("3.5", "3.5"),
("3.6", "3.6"),("3.7", "3.7"),("3.8", "3.8"),("3.9", "3.9"),("4.0", "4.0"),("4.1", "4.1"),
("4.2", "4.2"),("4.3", "4.3"),("4.4", "4.4"),("4.5", "4.5"),("4.6", "4.6"),("4.7", "4.7"),
("4.8", "4.8"),("4.9", "4.9"),("5.0", "5.0"),("5.1", "5.1"),("5.2", "5.2"),("5.3", "5.3"),
("5.4", "5.4"),("5.5", "5.5"),("5.6", "5.6"),("5.7", "5.7"),("5.8", "5.8"),("5.9", "5.9"),
("6.0", "6.0"),("6.1", "6.1"),("6.2", "6.2"),("6.3", "6.3"),("6.4", "6.4"),("6.5", "6.5"),
("6.6", "6.6"),("6.7", "6.7"),("6.8", "6.8"),("6.9", "6.9"),("7.0", "7.0"),("7.1", "7.1"),
("7.2", "7.2"),("7.3", "7.3"),("7.4", "7.4"),("7.5", "7.5"),("7.6", "7.6"),("7.7", "7.7"),
("7.8", "7.8"),("7.9", "7.9"),("8.0", "8.0"),("8.1", "8.1"),("8.2", "8.2"),("8.3", "8.3"),
("8.4", "8.4"),("8.5", "8.5"),("8.6", "8.6"),("8.7", "8.7"),("8.8", "8.8"),("8.9", "8.9"),
("9.0", "9.0"),("9.1", "9.1"),("9.2", "9.2"),("9.3", "9.3"),("9.4", "9.4"),("9.5", "9.5"),
("9.6", "9.6"),("9.7", "9.7"),("9.8", "9.8"),("9.9", "9.9"),("10.0", "10.0"),("10.1", "10.1"),
("10.2", "10.2"),("10.3", "10.3"),("10.4", "10.4"),("10.5", "10.5"),("10.6", "10.6"),("10.7", "10.7"),
("10.8", "10.8"),("10.9", "10.9"),("11.0", "11.0"),("11.1", "11.1"),("11.2", "11.2"),("11.3", "11.3"),
("11.4", "11.4"),("11.5", "11.5"),("11.6", "11.6"),("11.7", "11.7"),("11.8", "11.8"),("11.9", "11.9"),
("12.0", "12.0"),("12.1", "12.1"),("12.2", "12.2"),("12.3", "12.3"),("12.4", "12.4"),("12.5", "12.5"),
("12.6", "12.6"),("12.7", "12.7"),("12.8", "12.8"),("12.9", "12.9"),("13.0", "13.0"),("13.1", "13.1"),
("13.2", "13.2"),("13.3", "13.3"),("13.4", "13.4"),("13.5", "13.5"),("13.6", "13.6"),("13.7", "13.7"),
("13.8", "13.8"),("14.9", "13.9"),("14.0", "14.0"),("14.1", "14.1"),("14.2", "14.2"),("14.3", "14.3"),
("14.4", "14.4"),("14.5", "14.5"),("14.6", "14.6"),("14.7", "14.7"),("14.8", "14.8"),("14.9", "14.9"),
("15.0", "15.0"),("15.1", "15.1"),("15.2", "15.2"),("15.3", "15.3"),("15.4", "15.4"),("15.5", "15.5"),
("15.6", "15.6"),("15.7", "15.7"),("15.8", "15.8"),("15.9", "15.9"),("16.0", "16.0"),("16.1", "16.1"),
("16.2", "16.2"),("16.3", "16.3"),("16.4", "16.4"),("16.5", "16.5"),("16.6", "16.6"),("16.7", "16.7"),
("16.8", "16.8"),("16.9", "16.9"),("17.0", "17.0"),("17.1", "17.1"),("17.2", "17.2"),("17.3", "17.3"),
("17.4", "17.4"),("17.5", "17.5"),("17.6", "17.6"),("17.7", "17.7"),("17.8", "17.8"),("17.9", "17.9"),
("18.0", "18.0"),("18.1", "18.1"),("18.2", "18.2"),("18.3", "18.3"),("18.4", "18.4"),("18.5", "18.5"),
("18.6", "18.6"),("18.7", "18.7"),("18.8", "18.8"),("18.9", "18.9"),("19.0", "19.0"),("19.1", "19.1"),
("19.2", "19.2"),("19.3", "19.3"),("19.4", "19.4"),("19.5", "19.5"),("19.6", "19.6"),("19.7", "19.7"),
("19.8", "19.8"),("19.9", "19.9"),("20.0", "20.0")])

config.plugins.enigmalight.saturation = ConfigSelection(default = "1.0", choices = [
("0.0", "0.0"),("0.1", "0.1"),("0.2", "0.2"),("0.3", "0.3"),("0.4", "0.4"),("0.5", "0.5"), 
("0.6", "0.6"),("0.7", "0.7"),("0.8", "0.8"),("0.9", "0.9"),("1.0", "1.0"),("1.1", "1.1"),
("1.2", "1.2"),("1.3", "1.3"),("1.4", "1.4"),("1.5", "1.5"),("1.6", "1.6"),("1.7", "1.7"),
("1.8", "1.8"),("1.9", "1.9"),("2.0", "2.0"),("2.1", "2.1"),("2.2", "2.2"),("2.3", "2.3"),
("2.4", "2.4"),("2.5", "2.5"),("2.6", "2.6"),("2.7", "2.7"),("2.8", "2.8"),("2.9", "2.9"),
("3.0", "3.0"),("3.1", "3.1"),("3.2", "3.2"),("3.3", "3.3"),("3.4", "3.4"),("3.5", "3.5"),
("3.6", "3.6"),("3.7", "3.7"),("3.8", "3.8"),("3.9", "3.9"),("4.0", "4.0"),("4.1", "4.1"),
("4.2", "4.2"),("4.3", "4.3"),("4.4", "4.4"),("4.5", "4.5"),("4.6", "4.6"),("4.7", "4.7"),
("4.8", "4.8"),("4.9", "4.9"),("5.0", "5.0"),("5.1", "5.1"),("5.2", "5.2"),("5.3", "5.3"),
("5.4", "5.4"),("5.5", "5.5"),("5.6", "5.6"),("5.7", "5.7"),("5.8", "5.8"),("5.9", "5.9"),
("6.0", "6.0"),("6.1", "6.1"),("6.2", "6.2"),("6.3", "6.3"),("6.4", "6.4"),("6.5", "6.5"),
("6.6", "6.6"),("6.7", "6.7"),("6.8", "6.8"),("6.9", "6.9"),("7.0", "7.0"),("7.1", "7.1"),
("7.2", "7.2"),("7.3", "7.3"),("7.4", "7.4"),("7.5", "7.5"),("7.6", "7.6"),("7.7", "7.7"),
("7.8", "7.8"),("7.9", "7.9"),("8.0", "8.0"),("8.1", "8.1"),("8.2", "8.2"),("8.3", "8.3"),
("8.4", "8.4"),("8.5", "8.5"),("8.6", "8.6"),("8.7", "8.7"),("8.8", "8.8"),("8.9", "8.9"),
("9.0", "9.0"),("9.1", "9.1"),("9.2", "9.2"),("9.3", "9.3"),("9.4", "9.4"),("9.5", "9.5"),
("9.6", "9.6"),("9.7", "9.7"),("9.8", "9.8"),("9.9", "9.9"),("10.0", "10.0"),("10.1", "10.1"),
("10.2", "10.2"),("10.3", "10.3"),("10.4", "10.4"),("10.5", "10.5"),("10.6", "10.6"),("10.7", "10.7"),
("10.8", "10.8"),("10.9", "10.9"),("11.0", "11.0"),("11.1", "11.1"),("11.2", "11.2"),("11.3", "11.3"),
("11.4", "11.4"),("11.5", "11.5"),("11.6", "11.6"),("11.7", "11.7"),("11.8", "11.8"),("11.9", "11.9"),
("12.0", "12.0"),("12.1", "12.1"),("12.2", "12.2"),("12.3", "12.3"),("12.4", "12.4"),("12.5", "12.5"),
("12.6", "12.6"),("12.7", "12.7"),("12.8", "12.8"),("12.9", "12.9"),("13.0", "13.0"),("13.1", "13.1"),
("13.2", "13.2"),("13.3", "13.3"),("13.4", "13.4"),("13.5", "13.5"),("13.6", "13.6"),("13.7", "13.7"),
("13.8", "13.8"),("14.9", "13.9"),("14.0", "14.0"),("14.1", "14.1"),("14.2", "14.2"),("14.3", "14.3"),
("14.4", "14.4"),("14.5", "14.5"),("14.6", "14.6"),("14.7", "14.7"),("14.8", "14.8"),("14.9", "14.9"),
("15.0", "15.0"),("15.1", "15.1"),("15.2", "15.2"),("15.3", "15.3"),("15.4", "15.4"),("15.5", "15.5"),
("15.6", "15.6"),("15.7", "15.7"),("15.8", "15.8"),("15.9", "15.9"),("16.0", "16.0"),("16.1", "16.1"),
("16.2", "16.2"),("16.3", "16.3"),("16.4", "16.4"),("16.5", "16.5"),("16.6", "16.6"),("16.7", "16.7"),
("16.8", "16.8"),("16.9", "16.9"),("17.0", "17.0"),("17.1", "17.1"),("17.2", "17.2"),("17.3", "17.3"),
("17.4", "17.4"),("17.5", "17.5"),("17.6", "17.6"),("17.7", "17.7"),("17.8", "17.8"),("17.9", "17.9"),
("18.0", "18.0"),("18.1", "18.1"),("18.2", "18.2"),("18.3", "18.3"),("18.4", "18.4"),("18.5", "18.5"),
("18.6", "18.6"),("18.7", "18.7"),("18.8", "18.8"),("18.9", "18.9"),("19.0", "19.0"),("19.1", "19.1"),
("19.2", "19.2"),("19.3", "19.3"),("19.4", "19.4"),("19.5", "19.5"),("19.6", "19.6"),("19.7", "19.7"),
("19.8", "19.8"),("19.9", "19.9"),("20.0", "20.0")])

config.plugins.enigmalight.valuemin = ConfigSelection(default = "0.00", choices = [
("0.00", "0.00"), ("0.01", "0.01"), ("0.02", "0.02"), ("0.03", "0.03"),
("0.04", "0.04"),("0.05", "0.05"), ("0.06", "0.06"), ("0.07", "0.07"),("0.08", "0.08"),("0.09", "0.09"),("0.1", "0.1"), ("0.2", "0.2"), 
("0.3", "0.3"),("0.4", "0.4"),("0.5", "0.5"), ("0.6", "0.6"), ("0.7", "0.7"),("0.8", "0.8"),("0.9", "0.9"), 
("1.0", "1.0")])

config.plugins.enigmalight.valuemax = ConfigSelection(default = "1.0", choices = [
("0.00", "0.00"), ("0.01", "0.01"), ("0.02", "0.02"), ("0.03", "0.03"),
("0.04", "0.04"),("0.05", "0.05"), ("0.06", "0.06"), ("0.07", "0.07"),("0.08", "0.08"),("0.09", "0.09"),("0.1", "0.1"), 
("0.2", "0.2"), ("0.3", "0.3"),("0.4", "0.4"),("0.5", "0.5"), ("0.6", "0.6"), ("0.7", "0.7"),("0.8", "0.8"),("0.9", "0.9"), 
("1.0", "1.0")])

config.plugins.enigmalight.gamma = ConfigSelection(default = "2.2", choices = [
("1.0", "1.0"),("1.1", "1.1"), ("1.2", "1.2"), ("1.3", "1.3"),("1.4", "1.4"),
("1.5", "1.5"),("1.6", "1.6"), ("1.7", "1.7"),("1.8", "1.8"),("1.9", "1.9"), ("2.0", "2.0"), ("2.1", "2.1"),("2.2", "2.2"),("2.3", "2.3"), 
("2.4", "2.4"),("2.5", "2.5"),("2.6", "2.6"),("2.7", "2.7"), ("2.8", "2.8"),("2.9", "2.9"),("3.0", "3.0"),
("3.1", "3.1"),("3.2", "3.2"),("3.3", "3.3"), ("3.4", "3.4"), ("3.5", "3.5"),("3.6", "3.6"),("3.7", "3.7"), ("3.8", "3.8"),("3.9", "3.9"),("4.0", "4.0"),("4.1", "4.1"),
("4.2", "4.2"),("4.3", "4.3"), ("4.4", "4.4"), ("4.5", "4.5"),("4.6", "4.6"),("4.7", "4.7"), ("4.8", "4.8"),
("4.9", "4.9"),("5.0", "5.0"),("5.1", "5.1"), ("5.2", "5.2"), ("5.3", "5.3"),("5.4", "5.4"),("5.5", "5.5"), ("5.6", "5.6"), ("5.7", "5.7"),("5.8", "5.8"),("5.9", "5.9"), 
("6.0", "6.0"),("6.1", "6.1"),("6.2", "6.2"),("6.3", "6.3"), ("6.4", "6.4"), ("6.5", "6.5"),("6.6", "6.6"),("6.7", "6.7"), ("6.8", "6.8"),("6.9", "6.9"),("7.0", "7.0"),
("7.1", "7.1"),("7.2", "7.2"),("7.3", "7.3"), ("7.4", "7.4"), ("7.5", "7.5"),("7.6", "7.6"),("7.7", "7.7"), ("7.8", "7.8"),("7.9", "7.9"),("8.0", "8.0"),
("8.1", "8.1"),("8.2", "8.2"),("8.3", "8.3"), ("8.4", "8.4"), ("8.5", "8.5"),("8.6", "8.6"),("8.7", "8.7"), ("8.8", "8.8"),("8.9", "8.9"),
("9.0", "9.0"),("9.1", "9.1"),("9.2", "9.2"),("9.3", "9.3"), ("9.4", "9.4"), ("9.5", "9.5"),("9.6", "9.6"),("9.7", "9.7"), ("9.8", "9.8"),("9.9", "9.9"),
("10.0", "10.0")
])

config.plugins.enigmalight.saturationmin = ConfigSelection(default = "0.0", choices = [
("0.00", "0.00"), ("0.01", "0.01"), ("0.02", "0.02"), ("0.03", "0.03"),("0.04", "0.04"),("0.05", "0.05"), ("0.06", "0.06"), ("0.07", "0.07"),("0.08", "0.08"),("0.09", "0.09"),("0.1", "0.1"), ("0.2", "0.2"), ("0.3", "0.3"),("0.4", "0.4"),("0.5", "0.5"), ("0.6", "0.6"), ("0.7", "0.7"),("0.8", "0.8"),("0.9", "0.9"), ("1.0", "1.0")])

config.plugins.enigmalight.saturationmax = ConfigSelection(default = "1.0", choices = [
("0.00", "0.00"), ("0.01", "0.01"), ("0.02", "0.02"), ("0.03", "0.03"),("0.04", "0.04"),("0.05", "0.05"), ("0.06", "0.06"), ("0.07", "0.07"),("0.08", "0.08"),("0.09", "0.09"),("0.1", "0.1"), ("0.2", "0.2"), ("0.3", "0.3"),("0.4", "0.4"),("0.5", "0.5"), ("0.6", "0.6"), ("0.7", "0.7"),("0.8", "0.8"),("0.9", "0.9"), ("1.0", "1.0")])

config.plugins.enigmalight.speed  = ConfigSelection(default="60", choices = [ 
("0", "0"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("10", "10"), ("11", "11"), ("12", "12"), ("13", "13"), ("14", "14"), ("15", "15"), ("16", "16"), ("17", "17"), ("18", "18"), ("19", "19"), ("20", "20"), ("21", "21"), ("22", "22"), ("23", "23"), ("24", "24"), ("25", "25"), ("26", "26"), ("27", "27"), ("28", "28"), ("29", "29"), ("30", "30"), ("31", "31"), ("32", "32"), ("33", "33"), ("34", "34"), ("35", "35"), ("36", "36"), ("37", "37"), ("38", "38"), ("39", "39"), ("40", "40"), ("41", "41"), ("42", "42"), ("43", "43"), ("44", "44"), ("45", "45"), ("46", "46"), ("47", "47"), ("48", "48"), ("49", "49"), ("50", "50"), ("51", "51"), ("52", "52"), ("53", "53"), ("54", "54"), ("55", "55"), ("56", "56"), ("57", "57"), ("58", "58"), ("59", "59"), ("60", "60"), ("61", "61"), ("62", "62"), ("63", "63"), ("64", "64"), ("65", "65"), ("66", "66"), ("67", "67"), ("68", "68"), ("69", "69"), ("70", "70"), ("71", "71"), ("72", "72"), ("73", "73"), ("74", "74"), ("75", "75"), ("76", "76"), ("77", "77"), ("78", "78"), ("79", "79"), ("80", "80"), ("81", "81"), ("82", "82"), ("83", "83"), ("84", "84"), ("85", "85"), ("86", "86"), ("87", "87"), ("88", "88"), ("89", "89"), ("90", "90"), ("91", "91"), ("92", "92"), ("93", "93"), ("94", "94"), ("95", "95"), ("96", "96"), ("97", "97"), ("98", "98"), ("99", "99"), ("100", "100")])

config.plugins.enigmalight.chase_speed= ConfigSelection(default="60", choices = [ 
("0", "0"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("10", "10"), ("11", "11"), ("12", "12"), ("13", "13"), ("14", "14"), ("15", "15"), ("16", "16"), ("17", "17"), ("18", "18"), ("19", "19"), ("20", "20"), ("21", "21"), ("22", "22"), ("23", "23"), ("24", "24"), ("25", "25"), ("26", "26"), ("27", "27"), ("28", "28"), ("29", "29"), ("30", "30"), ("31", "31"), ("32", "32"), ("33", "33"), ("34", "34"), ("35", "35"), ("36", "36"), ("37", "37"), ("38", "38"), ("39", "39"), ("40", "40"), ("41", "41"), ("42", "42"), ("43", "43"), ("44", "44"), ("45", "45"), ("46", "46"), ("47", "47"), ("48", "48"), ("49", "49"), ("50", "50"), ("51", "51"), ("52", "52"), ("53", "53"), ("54", "54"), ("55", "55"), ("56", "56"), ("57", "57"), ("58", "58"), ("59", "59"), ("60", "60"), ("61", "61"), ("62", "62"), ("63", "63"), ("64", "64"), ("65", "65"), ("66", "66"), ("67", "67"), ("68", "68"), ("69", "69"), ("70", "70"), ("71", "71"), ("72", "72"), ("73", "73"), ("74", "74"), ("75", "75"), ("76", "76"), ("77", "77"), ("78", "78"), ("79", "79"), ("80", "80"), ("81", "81"), ("82", "82"), ("83", "83"), ("84", "84"), ("85", "85"), ("86", "86"), ("87", "87"), ("88", "88"), ("89", "89"), ("90", "90"), ("91", "91"), ("92", "92"), ("93", "93"), ("94", "94"), ("95", "95"), ("96", "96"), ("97", "97"), ("98", "98"), ("99", "99"), ("100", "100")])

config.plugins.enigmalight.autospeed= ConfigSelection(default="0", choices = [ 
("0", "0"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("10", "10"), ("11", "11"), ("12", "12"), ("13", "13"), ("14", "14"), ("15", "15"), ("16", "16"), ("17", "17"), ("18", "18"), ("19", "19"), ("20", "20"), ("21", "21"), ("22", "22"), ("23", "23"), ("24", "24"), ("25", "25"), ("26", "26"), ("27", "27"), ("28", "28"), ("29", "29"), ("30", "30"), ("31", "31"), ("32", "32"), ("33", "33"), ("34", "34"), ("35", "35"), ("36", "36"), ("37", "37"), ("38", "38"), ("39", "39"), ("40", "40"), ("41", "41"), ("42", "42"), ("43", "43"), ("44", "44"), ("45", "45"), ("46", "46"), ("47", "47"), ("48", "48"), ("49", "49"), ("50", "50"), ("51", "51"), ("52", "52"), ("53", "53"), ("54", "54"), ("55", "55"), ("56", "56"), ("57", "57"), ("58", "58"), ("59", "59"), ("60", "60"), ("61", "61"), ("62", "62"), ("63", "63"), ("64", "64"), ("65", "65"), ("66", "66"), ("67", "67"), ("68", "68"), ("69", "69"), ("70", "70"), ("71", "71"), ("72", "72"), ("73", "73"), ("74", "74"), ("75", "75"), ("76", "76"), ("77", "77"), ("78", "78"), ("79", "79"), ("80", "80"), ("81", "81"), ("82", "82"), ("83", "83"), ("84", "84"), ("85", "85"), ("86", "86"), ("87", "87"), ("88", "88"), ("89", "89"), ("90", "90"), ("91", "91"), ("92", "92"), ("93", "93"), ("94", "94"), ("95", "95"), ("96", "96"), ("97", "97"), ("98", "98"), ("99", "99"), ("100", "100")])

config.plugins.enigmalight.delay = ConfigSelection(default="0", choices = [
("0", "0"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("10", "10"), ("11", "11"), ("12", "12"), ("13", "13"), ("14", "14"), ("15", "15"), ("16", "16"), ("17", "17"), ("18", "18"), ("19", "19"), ("20", "20")])

config.plugins.enigmalight.interpolation  = ConfigOnOff(default=False)

config.plugins.enigmalight.blackbar_h   = ConfigOnOff(default=False)
config.plugins.enigmalight.blackbar_v   = ConfigOnOff(default=False)
config.plugins.enigmalight.blackbar_f   = ConfigSelection(default="10", choices = [ 
("10", "10"), ("20", "20"), ("30", "30"), ("40", "40"), ("50", "50"), ("60", "60"), ("70", "70"), ("80", "80"), ("90", "90"), ("100", "100")])


config.plugins.enigmalight.type   = ConfigSelection(default = "Atmolight", choices = [
("Adalight/Momo", "Adalight/Momo"),
("Ambioder", "Ambioder"),
("Atmolight", "Atmolight"),
("Karatelight", "Karatelight"),
("Lightpack1", "Lightpack Firmware < 6.2"),
("Lightpack2", "Lightpack Firmware 6.3 >"),
("Oktolight", "Oktolight"),
("Sedulight 5A A0 A5", "Sedulight 96 channels"),
("Sedulight 5A A1 A5", "Sedulight 256 channels"),
("Sedulight 5A A2 A5", "Sedulight 512 channels"),
("Sedulight 5A B0 A5", "Sedulight 768 channels"),
("Adalight/Momo", "Adalight/Momo"),
("iBelight", "iBelight"),
("WifiLight", "WifiLight, limitlessled..")])

# 03eb:204f <-lightpack device
config.plugins.enigmalight.serial   = ConfigSelection(default = "5437231893F351C11700", choices = [
("5437231893F351C11700", "5437231893F351C11700"),
("649323139323515111C0", "649323139323515111C0")])

config.plugins.enigmalight.wifilight_ip = ConfigIP(default=[0,0,0,0])
config.plugins.enigmalight.wifilight_port = ConfigInteger(default = 50000, limits=(1, 65535))

config.plugins.enigmalight.bus = ConfigInteger(1,(1, 9))
config.plugins.enigmalight.laddress= ConfigInteger(6,(1, 9))

config.plugins.enigmalight.output  = ConfigDirectory(default="/dev/ttyUSB0")
config.plugins.enigmalight.threadpriority = ConfigInteger(99,(0, 99))

config.plugins.enigmalight.rate= ConfigInteger(057600,(0, 500000))
config.plugins.enigmalight.lights_left = ConfigInteger(0,(0, 99))
config.plugins.enigmalight.lights_top  = ConfigInteger(0,(0, 99))
config.plugins.enigmalight.lights_right= ConfigInteger(0,(0, 99))
config.plugins.enigmalight.lights_bottom   = ConfigInteger(0,(0, 99))
config.plugins.enigmalight.lights_bottom_right = ConfigInteger(0,(0, 99))
config.plugins.enigmalight.lights_bottom_left  = ConfigInteger(0,(0, 99))
config.plugins.enigmalight.lights_bottom_center= ConfigInteger(0,(0, 50))

config.plugins.enigmalight.scanl  = ConfigInteger(10,(0, 100))
config.plugins.enigmalight.scanr  = ConfigInteger(10,(0, 100))
config.plugins.enigmalight.scant  = ConfigInteger(10,(0, 100))
config.plugins.enigmalight.scanb  = ConfigInteger(10,(0, 100))

config.plugins.enigmalight.color_order  = ConfigSelection(default = "0", choices = [("0", "RGB"), ("1", "BGR"), ("2", "GBR"), ("3", "GRB"), ("4", "BRG"), ("5", "RBG")])

config.plugins.enigmalight.begincount_cw = ConfigSelection(default = "left-bottom", choices = [("left-bottom", _("LEFT [bottom]")), ("top-left", _("TOP [left]")),
("right-top", _("RIGHT [top]")), ("bottom-right", _("BOTTOM [right]")), ("bottom-middle-left", _("BOTTOM [middle]"))])

config.plugins.enigmalight.begincount_bw = ConfigSelection(default = "bottom-left", choices = [("bottom-left", _("BOTTOM [left]")), ("right-bottom", _("RIGHT [bottom]")), 
("top-right", _("TOP [right]")),("left-top", _("LEFT [top]")), ("bottom-middle-right", _("BOTTOM [middle]"))])

config.plugins.enigmalight.clockwise  = ConfigSelection(default = "1", choices = [("1", _("Clockwise")), ("2", _("Backwards"))])
config.plugins.enigmalight.floorstand = ConfigSelection(default = "1", choices = [("1", _("No")), ("2", _("Yes"))])
config.plugins.enigmalight.blacklevel = ConfigFloat(default = [0,0], limits = [(0,9),(0,99)])
config.plugins.enigmalight.overlap= ConfigOnOff(default=False)
config.plugins.enigmalight.precision  = ConfigInteger(255,(0, 255))

config.plugins.enigmalight.lastmode   = ConfigText(default = "-", fixed_size=10)
config.plugins.enigmalight.m_3dmode   = ConfigSelection(default = "1", choices = [("1", _("Disabled")), ("2", _("Top and Bottom")), ("3", _("SidebySide"))])

config.plugins.enigmalight.config_r_adjust = ConfigFloat(default = [1,00], limits = [(0,9),(00,99)])
config.plugins.enigmalight.config_r_gamma  = ConfigFloat(default = [0,91], limits = [(0,9),(00,99)])
config.plugins.enigmalight.config_r_blacklevel = ConfigFloat(default = [0,00], limits = [(0,9),(00,99)])
config.plugins.enigmalight.config_g_adjust = ConfigFloat(default = [0,96], limits = [(0,9),(00,99)])
config.plugins.enigmalight.config_g_gamma  = ConfigFloat(default = [0,86], limits = [(0,9),(00,99)])
config.plugins.enigmalight.config_g_blacklevel = ConfigFloat(default = [0,00], limits = [(0,9),(00,99)])

config.plugins.enigmalight.config_b_adjust = ConfigFloat(default = [0,80], limits = [(0,9),(00,99)])
config.plugins.enigmalight.config_b_gamma  = ConfigFloat(default = [0,95], limits = [(0,9),(00,99)])
config.plugins.enigmalight.config_b_blacklevel = ConfigFloat(default = [0,00], limits = [(0,9),(00,99)])

config.plugins.enigmalight.timer_standby_onoff = ConfigYesNo(default=False)
config.plugins.enigmalight.timer_onoff = ConfigOnOff(default=False)
config.plugins.enigmalight.time_start  = ConfigClock(default=def_start)
config.plugins.enigmalight.time_end= ConfigClock(default=def_end)

config.plugins.enigmalight.brightness_timer_onoff  = ConfigOnOff(default=False)
config.plugins.enigmalight.brightness_time_start   = ConfigClock(default=def_start)
config.plugins.enigmalight.brightness_time_end = ConfigClock(default=def_end)
config.plugins.enigmalight.message_onoff   = ConfigOnOff(default=False)
config.plugins.enigmalight.message_error_onoff = ConfigOnOff(default=False)

#===============================================================================
# Config functions
#===============================================================================
def getConfig():
	log("",None,"__init__::getConfig()")
	return EnigmaLight

def saveConfig():
	log("",None,"__init__::saveConfig()")
	config.plugins.enigmalight.save()
	config.plugins.enigmalight.saveToFile(enigmalight_config)

def loadConfig():
	log("",None,"__init__::loadConfig()")
	if os.path.isfile(enigmalight_config):
		config.plugins.enigmalight.loadFromFile(enigmalight_config)
		config.plugins.enigmalight.load()
	else:
		Logfile("no configfile found!")
#===============================================================================
# 
#===============================================================================
def getVersion():
	log("",None,"__init__::getVersion()")
	return "EnigmaLight V." + currentVersion

#===============================================================================
# 
#===============================================================================
def getCrashFilePath():
	log("",None,"__init__::getCrashFilePath()")
	return crashFile

#===============================================================================
# 
#===============================================================================
def registerSkinParamsInstance():
	log("",None,"__init__::registerSkinParamsInstance()")

	configXml = getXmlContent("/usr/lib/enigma2/python/Plugins/Extensions/EnigmaLight/skins/default/params")

	Singleton().getSkinParamsInstance(configXml)


#===============================================================================
# EXECUTE ON STARTUP
#===============================================================================
def Prepare():
	try:
		log("",None,"__init__::Prepare()")
		getBoxInformation()
		#localeInit()
		registerSkinParamsInstance()
		loadEnigmalightSkin()
		registerEnigmalightFonts()
	except:
		from traceback import format_exc
		log("",None,"__init__::Prepare > ERROR: " +format_exc() )
		try:
			open(crashFile,"w").write(format_exc())
		except:
			pass
