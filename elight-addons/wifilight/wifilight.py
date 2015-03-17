import sys
import socket
import colorsys
import time

UDP_IP = None
UDP_PORT = None

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
try:
  fo = open("/home/elight-addons/wifilight/wifilight.conf" , "r")
  customsettings = fo.read(256)
  fo.close()

  customsettings = customsettings.split("|")
  UDP_IP = customsettings[0]
  UDP_PORT = int(customsettings[1])

  print "Try connection.." 

  sock.sendto("\x40\x00\x55", (UDP_IP, UDP_PORT))
  sock.sendto("\x42\x55", (UDP_IP, UDP_PORT))

  print "Talking to WifiLight @ %s:%s..." %(UDP_IP,UDP_PORT)

except:
  from traceback import format_exc
  print("Error: " + format_exc())

def popen():
  while True:
    eingabe = sys.stdin.readline()
    if len(eingabe)>0:
      r,g,b,x = eingabe.split(' ')
      r = float(r)
      g = float(g)
      b = float(b)
      h, l, s = colorsys.rgb_to_hls(r,g,b)
      if (l>=0.25):
        l=0.25
      l=l*4
      l=l*25
      l=l+2
      l = max(2,int(round(l)))
      rgbmin=min(r,g,b)
      rgbmax=max(r,g,b)
      difference=rgbmax-rgbmin
      grey=0.01
      if(difference<=grey): 
        MESSAGE1 = "\xC2\x00\x55"
        MESSAGE2 = "\x4E" + chr(l) + "\x55"
      else:
        h = int((h) * 255)
        h=h+85
        h=abs(h-255)
        h=int(h)
        MESSAGE1 = "\x40" + chr(h) + "\x55"
        MESSAGE2 = "\x4E" + chr(l) + "\x55"
      sock.sendto(MESSAGE1, (UDP_IP, UDP_PORT))
      sock.sendto(MESSAGE2, (UDP_IP, UDP_PORT))
    else:
      break

  print "Disconnected, Exit..."
import time
time.sleep(3)
print "Ready..."
popen()