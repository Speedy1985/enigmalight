## Process this file with automake to produce Makefile.in
ACLOCAL_AMFLAGS=-I m4
AUTOMAKE_OPTIONS = subdir-objects

C_INCLUDE_PATH=Include

CPLUS_INCLUDE_PATH=Include

AM_CPPFLAGS= 

AM_CFLAGS = 

bin_PROGRAMS = \
	enigmalight \
	elighttalk

enigmalight_SOURCES = \
	Main.cpp \
	MainLoop.cpp \
	FlagManager.cpp \
	Configuration.cpp \
	Util/Condition.cpp \
	Util/Log.cpp \
	Util/Misc.cpp \
	Util/Mutex.cpp \
	Util/Thread.cpp \
	Util/Timer.cpp \
	Util/Bitmap.cpp \
	Util/SerialPort.cpp \
	Util/TimeUtils.cpp \
	Util/TcpSocket.cpp \
	Util/MessageQueue.cpp \
	Util/SignalTimer.cpp \
	Util/Daemonize.cpp \
	Util/Modp_Numtoa.c \
	Util/ColorTransform.cpp \
	Util/BlackbarDetection.cpp \
	GuiServer/GuiServer.cpp \
	StbDetection/StbDetection.cpp \
	Grabber/Grabber.cpp \
	Grabber/FrameGrabber.cpp \
	Lights/EnigmaLightOptions.cpp \
	Lights/Light.cpp \
	Lights/Color.cpp \
	Effects/Effects.cpp \
	Effects/Static.cpp \
	Effects/Moodlamp.cpp \
	Effects/Rainbow.cpp \
	Effects/RGBTest.cpp \
	Device/Device.cpp \
	Device/DevicePopen.cpp \
	Device/DeviceRs232.cpp \
	Device/DeviceLTBL.cpp \
	Device/DeviceDioder.cpp \
	Device/DeviceAmbioder.cpp \
	Device/DeviceIbelight.cpp \
	Device/DeviceLightpack.cpp

elighttalk_SOURCES = \
	ElightTalk/Main.cpp \
	Util/Misc.cpp

## libusb used for LightPack and IBelight
enigmalight_LDFLAGS = -lusb-1.0