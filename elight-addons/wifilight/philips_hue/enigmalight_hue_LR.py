import sys
import os
import time 
import json
import httplib
from rgb_xy import Converter
from rgb_xy import GamutC     # or GamutA, GamutB (you must look for the type of your lamps in rgb_xy.py from line 42)
counter = 12

			
def popen():
	converter = Converter(GamutC)
	spidev = file( os.getcwd()+'/aufruf.log', "wb")
	key = "HIER DEN KEY DER BRIDGE EINTRAGEN"
	ip = "xxx.xxx.xxx.xxx"
	url = '/api/' + key + '/lights/'
	lurl = url + '10/state'
	rurl = url + '11/state'
	
	MINIMAL_VALUE=0.000000000

	while True:
		eingabe = sys.stdin.readline()

		if len(eingabe)>0:
			global counter
			counter += 1
			
			try:
				lr,lg,lb,rr,rg,rb,x = eingabe.split(' ')
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

			lll = calcLuminance(lr,lg,lb)
			llr = calcLuminance(rr,rg,rb)

			if (counter>=13):
				connection = httplib.HTTPConnection(ip, timeout=10)

				lparams = {'xy': converter.rgb_to_xy(lr,lg,lb), 'colormode': 'xy', 'bri': int(lll), 'on': True}
				connection.request('PUT', lurl, json.dumps(lparams))
				response = connection.getresponse()
				
				rparams = {'xy': converter.rgb_to_xy(rr,rg,rb), 'colormode': 'xy', 'bri': int(llr), 'on': True}
				connection.request('PUT', rurl, json.dumps(rparams))
				response = connection.getresponse()

				connection.close()
				counter=0
		else:
			os.system("curl -d '{\"on\":false}' -X PUT  192.168.xxx.xxx/api/HIER DEN KEY DER BRIDGE EINTRAGEN/groups/0/action")
			break


def calcLuminance(r,g,b):
	LUM_VALUE=20
	luminance=1
	if (r + g + b > 2):
		luminance= r + g + b + LUM_VALUE 
	if (luminance>=255):
		luminance=254

	return luminance

import time
time.sleep(1)
popen()
