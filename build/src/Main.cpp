/*
 * EnigmaLight (c) 2014 Speedy1985, Oktay Oeztueter (Based on Boblight from Bob Loosen)
 * parts of this code were taken from
 *
 * - aiograb		(http://schwerkraft.elitedvb.net/projects/aio-grab/)
 * - boblight (c) 2009 Bob Loosen
 * 
 * EnigmaLight is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * EnigmaLight is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along
 * with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <string>
#include <iostream>
#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <sstream>
#include <stdlib.h>

#include "Config.h"
#include "Configuration.h"
#include "FlagManager.h"

#include "MainLoop.h"

#include "Util/Log.h"
#include "Util/TcpSocket.h"
#include "Util/MessageQueue.h"
#include "Util/Daemonize.h"

#include "Device/Device.h"

using namespace std;

volatile bool g_stop = false;
bool usocket;

void SignalHandler(int signum);

//Call flagmanager
CFlagManager g_flagmanager;

int main (int argc, char *argv[])
{

  printf("\nEnigmaLight (c) 2014 Speedy1985 and Oktay Oeztueter.\n(Based on Boblight (c) 2009 by Bob Loosen)\n\n",PACKAGE_VERSION);
  
  FILE* pipe = popen("pidof enigmalight |wc -w", "r");
  std::string result = "";
  if (!pipe) result = "999";
  char buffer[128];
  while(!feof(pipe)) {
    if(fgets(buffer, 128, pipe) != NULL)
      result += buffer;
  }
  pclose(pipe);
  
  //Check if EnigmaLight already runnning
  if (atoi(result.c_str()) == 999)
  {
      cout << "ERROR: missing [pidof] Can't check if EnigmaLight is already running, Exit..." << endl;
      exit(1);
  }
  else if (atoi(result.c_str()) == 2) {
      cout << "ERROR: EnigmaLight is already running, Exit..." << endl;
      exit(1);
  }

  //try to parse the flags and bitch to stderr if there's an error
  try
  {
    g_flagmanager.ParseFlags(argc, argv);
  }
  catch (string error)
  {
    PrintError(error);
    g_flagmanager.PrintHelpMessage();
    return 1;
  }
  
  if (g_flagmanager.m_printhelp) //print help message
  {
    g_flagmanager.PrintHelpMessage();
    return 1;
  }

  if (g_flagmanager.m_printoptions) //print enigmalight options (-o [light:]option=value)
  {
    g_flagmanager.PrintEnigmaLightOptions();
    return 1;
  }

  //New pointer to CEnigmaLight
  CEnigmaLight* g_enigmalight = new CEnigmaLight;
  

  //Start socket for enigma2 GUI
  CGuiServer g_guiserver(g_enigmalight);

  //init our logfile
  logtostderr = true;
  SetLogFile("enigmalight.log");                                //Set Logfile

  //set up signal handlers
  signal(SIGTERM, SignalHandler);
  signal(SIGINT, SignalHandler);
  
  
  //Check configfile before fork
  if(!g_flagmanager.m_network)
  {
      //load and parse config
      //save some ram by removing CConfig from the stack when it's not needed anymore
      {
        CConfig config;

        if (!config.LoadConfigFromFile(g_flagmanager.m_configfile))
          return 1;
        if (!config.CheckConfig())
          return 1;
      }
  }

  if (g_flagmanager.m_fork)                                                     //Fork enigmalight in background
    Daemonize();
    
  vector<CDevice*>  devices;                                                    //where we store devices
  vector<CLight>    lights;                                                     //lights pool  
  CMainLoop         mainloop(lights, g_flagmanager, g_enigmalight, g_guiserver);//mainloop instance   

  if(!g_flagmanager.m_network)
  {
    {                                       //save some ram by removing CConfig from the stack when it's not needed anymore
      CConfig config;                       //class for loading and parsing config

      if (!config.LoadConfigFromFile(g_flagmanager.m_configfile))
        return 1;
      if (!config.BuildConfig(mainloop, devices, lights))
        return 1;
    }

    //start the devices, each device has his own thread
    //Log("Try to start devices");
    for (int i = 0; i < devices.size(); i++){
      Log("Start device %i from %i",i+1,devices.size());
      devices[i]->StartThread();   
    }

    //Set the socket
    mainloop.SetSocket(usocket);

    g_enigmalight->SetLocal(true);  //Set m_local to true
  
    if(!g_enigmalight->InitLocal(lights,mainloop)){ //Init Lights for local use
      LogError("InitLocal error!\n");
      return 1;
    }
  }
  
  //Start mainprocess
  while(!g_stop)
    mainloop.Process();

  if(!g_flagmanager.m_network)
  {
    //signal that the devices should stop
    Log("Signaling devices to stop");
    for (int i = 0; i < devices.size(); i++)
      devices[i]->AsyncStopThread();

    
    //stop the devices
    Log("Waiting for devices to stop");
    for (int i = 0; i < devices.size(); i++){
    	Log("Stop device %i from %i",i+1,devices.size());
      devices[i]->StopThread();
    }

    if(!g_flagmanager.m_grabber_enabled)
      mainloop.Cleanup();
  }  

  // Delete enigmalight
  delete g_enigmalight;

  Log("Exiting EnigmaLight...");
  
  return 0;
}

void PrintFlags(int argc, char *argv[])
{
  string flags = "starting";
  
  for (int i = 0; i < argc; i++)
  {
    flags += " ";
    flags += argv[i];
  }

  Log("%s", flags.c_str());
}

void SignalHandler(int signum)
{
  if (signum == SIGTERM)
  {
    Log("caught SIGTERM");
    g_stop = true;
  }
  else if (signum == SIGINT)
  {
    Log("caught SIGINT");
    g_stop = true;
  }
  else
  {
    Log("caught %i", signum);
  }
}
