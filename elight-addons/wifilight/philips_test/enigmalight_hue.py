#!/usr/bin/env python

#Usage
#    Install enigmalight
#    Make your enigmalight.cfg
#    Copy the engimalight_hue.py in the folder you specified in the enigmalight.cfg
#    Get an Key from your Hue Bridge
#    Insert the Key and IP in the Script, import the right Gamut for your Hue.
#    Start enigmalight
#The script is prepared to use 3 Lamp

import sys
import os
import time 
import json
import httplib
from rgb_xy import Converter
from rgb_xy import GamutC # or GamutB, GamutC
counter = 9

def popen():
	converter = Converter(GamutC)
	spidev = file( os.getcwd()+'/aufruf.log', "wb")
	key = "PmjwE4NWFkA6mFA6agS1b5Wi2oeOeLPrNRGWcy72"
	ip = "192.168.1.175"
	url = '/api/' + key + '/lights/'
	lurl = url + '2/state'
	rurl = url + '1/state'
	burl = url + '4/state'
	#need to be sure that its not 0
	MINIMAL_VALUE=0.000000000

	while True:
		eingabe = sys.stdin.readline()

		if len(eingabe)>0:
			global counter
			counter += 1
			# Get Input
			try:
				lr,lg,lb,rr,rg,rb,br,bg,bb,x = eingabe.split(' ')
			except ValueError:
				spidev.write("Not enough input parameter, do you have the same amount of lights (channels) in your enigmalight config?")
				spidev.flush()
				raise

			lr = (float(lr))*255
			lg = (float(lg))*255
			lb = (float(lb))*255 
			rr = (float(rr))*255
			rg = (float(rg))*255
			rb = (float(rb))*255
			br = (float(br))*255
			bg = (float(bg))*255
			bb = (float(bb))*255

			lll = calcLuminance(lr,lg,lb)
			llr = calcLuminance(rr,rg,rb)
			llb = calcLuminance(br,bg,bb)

			if (counter>=10):
				connection = httplib.HTTPConnection(ip, timeout=10)

				#lparams = {'xy': converter.rgb_to_xy(lr,lg,lb), 'colormode': 'xy', 'bri': int(lll), 'on': True}
				#connection.request('PUT', lurl, json.dumps(lparams))
				#response = connection.getresponse()
				
				#rparams = {'xy': converter.rgb_to_xy(rr,rg,rb), 'colormode': 'xy', 'bri': int(llr), 'on': True}
				#connection.request('PUT', rurl, json.dumps(rparams))
				#response = connection.getresponse()

				bparams = {'xy': converter.rgb_to_xy(br,bg,bb), 'colormode': 'xy', 'bri': int(llb), 'on': True}
				connection.request('PUT', burl, json.dumps(bparams))
				response = connection.getresponse()

				connection.close()
				counter=0
		else:
			break


def calcLuminance(r,g,b):
	LUM_VALUE=50
	luminance=1
	if (r + g + b > 10):
		luminance= r + g + b + LUM_VALUE 
	if (luminance>=255):
		luminance=254

	return luminance

import time
time.sleep(1)
popen()
