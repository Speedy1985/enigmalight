from hue import Hue;

h = Hue(); # Initialize the class
h.station_ip = "192.168.1.222"  # Your base station IP
h.get_state(); # Authenticate, bootstrap your lighting system
l = h.lights.get('l3') # get bulb number 3
l.bri(0) # Dimmest
l.bri(255) # Brightest
l.rgb(120, 120, 0) # [0-255 rgb values]
l.rgb("#9af703") # Hex string
l.on()
time.sleep(1)
l.off()
l.toggle()
l.alert() # short alert
l.alert("lselect") # long alert
l.setState({"bri": 220, "alert": "select"}) # Complex send