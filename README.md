Enigmalight 
An Ambilight clone for broadcom based linux receivers.

You have to set compiler path manualy like in install file
-- obsolete --
-How to compile on Ubuntu
./bootstrap
./install

When [install] is started, it will download the needed compiler and compile the binary files for you.
After build it's found in your enigmalight_workdir/elight-addons/usr/bin/.
there are three files [elighttalk],[enigmalight_sf],[enigmalight_hf] mostly you need the hf version because this is for 
receivers with FPU support.
--- obsolete ---

- If you need to know if your receiver has the FPU support, then type in your terminal cat /proc/cpuinfo.
- the SF version is for receivers like dm800, this one has no FPU, use the SOFTFLOAT version.
- With Elighttalk you can talk to enigmalight and change the options over terminalcommands.

-Install Enigmalight manual on your receiver
copy the [elight-addons] dir to your receiver /home/
copy the [EnigmaLight] dir from build/python/plugin/ to your receiver /usr/lib/enigma2/python/Plugins/Extensions/

-For some devices like Atmolight,Karatelight,Adalight you need this kernel modules
To install this on your receiver type: opkg install kernel-module-cdc-acm kernel-module-ftdi-sio
Reboot your receiver and if all is succesfull you can make a configfile and run it.

Enjoy!
