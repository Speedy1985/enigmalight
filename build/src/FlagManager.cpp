/*
 * EnigmaLight (c) 2014 Speedy1985, Oktay Oeztueter (Based on Boblight from Bob Loosen)
 * parts of this code were taken from
 *
 * - aiograb		(http://schwerkraft.elitedvb.net/projects/aio-grab/)
 * - enigmalight (c) 2009 Bob Loosen
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


#include <string.h>
#include <unistd.h>
#include <iostream>
#include <iostream>
#include <stdlib.h>

#include "Util/Misc.h"
#include "Util/Log.h"
#include "FlagManager.h"

using namespace std;

//very simple, store a copy of argc and argv
CArguments::CArguments(int argc, char** argv)
{
  m_argc = argc;

  if (m_argc == 0)
  {
    m_argv = NULL;
  }
  else
  {
    m_argv = new char*[m_argc];
    for (int i = 0; i < m_argc; i++)
    {
      m_argv[i] = new char[strlen(argv[i]) + 1];
      strcpy(m_argv[i], argv[i]);
    }
  }
}

//delete the copy of argv
CArguments::~CArguments()
{
  if (m_argv)
  {
    for (int i = 0; i < m_argc; i++)
    {
      delete[] m_argv[i];
    }
    delete[] m_argv;
  }
}

CFlagManager::CFlagManager()
{
  m_port = -1;                        //-1 tells to use default port
  m_address = NULL;               
  m_priority        = 128;            //default priority
  m_printhelp       = false;          //don't print helpmessage unless asked to
  m_printoptions    = false;         
  m_fork            = false;          //don't fork by default
  m_sync            = true;           //sync mode enabled by default
  
  m_color_sequence  = 0;              // Default 0 = RGB
  m_cluster         = 1;              // Default set 1 for cluster
  m_blackbar        = false;	        // Blackbar detection, default disabled
  m_interval        = 0.1;   	        // default interval is 100 milliseconds
  m_delay           = 0;
  m_debug 	        = false; 	        // no debugging by default
  m_grabinfo        = false;          // for debug
  m_picdump         = false;  	      // Picture dump, default false
  m_sync 	          = true;           // sync mode, enabled by default
  m_mode            = 2;              // dynamic or static, default is dynamic  
  m_brightness      = 255;            // Fader brightness
  m_3d_mode         = 1;              // normal
  m_grabber_enabled = true;           // Local grabber, default start grabber
  m_server_enabled  = false;          // LightServer
  m_network         = false;          // Connect grabber with daemon on network.
  m_speed           = 100.0;
  m_use             = true;
  m_interpolation   = false;

  m_configfile  = "/etc/enigmalight.conf";
  
  for(int i=0; i < 3; i++){
    m_adjust[i] = 0;
  } 
  
  m_use_manual_adjust = true;
  
  // default getopt flags, can be extended in derived classes
  // p = priority, s = address[:port], o = enigmalight option, l = list enigmalight options, h = print help message, f = fork
  m_flags = "lhfy:o:c:s:a:x:i:t:w:r:m:q:j:c:d::b::k::g::p::u::";
}

std::vector<std::string> split(std::string str,std::string sep){
    char* cstr=const_cast<char*>(str.c_str());
    char* current;
    std::vector<std::string> arr;
    current=strtok(cstr,sep.c_str());
    while(current!=NULL){
        arr.push_back(current);
        current=strtok(NULL,sep.c_str());
    }
    return arr;
}

void CFlagManager::ParseFlags(int tempargc, char** tempargv)
{
  //that copy class sure comes in handy now!
  CArguments arguments(tempargc, tempargv);
  int    argc = arguments.m_argc;
  char** argv = arguments.m_argv;

  string option;
  int    c;

  opterr = 0; //we don't want to print error messages
  
  while ((c = getopt(argc, argv, m_flags.c_str())) != -1)
  {
  	if (c == 'c')
    {
      m_configfile = optarg;
    }
    else if (c == 's') //address[:port]
    {

      option = optarg;
      //store address in string and set the char* to it
      m_straddress = option.substr(0, option.find(':'));
      m_address = m_straddress.c_str();

      if (option.find(':') != string::npos) //check if we have a port
      {
        option = option.substr(option.find(':') + 1);
        string word;
        if (!StrToInt(option, m_port) || m_port < 0 || m_port > 65535)
        {
          throw string("Wrong option " + string(optarg) + " for argument -s");
        }
      }

      m_network = true;
      m_server_enabled = false;
    }
    else if (c == 'o') //option
    {
      m_options.push_back(optarg);
    }
    else if (c == 'l') //list options
    {
      m_printoptions = true;
      return;
    }
    else if (c == 'h') //print help message
    {
      m_printhelp = true;
      return;
    }
    else if (c == 'f')
    {
      m_fork = true;
    }
    else if (c == 'y')
    {
      if (!StrToBool(optarg, m_sync))
      {
        throw string("Wrong value " + string(optarg) + " for sync mode");
      }
    }
    else if (c == 'a') //adjust
    {
    
      std::vector<std::string> arr;
      arr=split(string(optarg),"/");
      if(arr.size() < 3 || arr.size() > 3)
      {
          throw string("Wrong value " + string(optarg) + " for adjust");
      }
      else{
          for(size_t i=0;i<arr.size();i++){
              m_adjust[i] = Clamp(atoi(arr[i].c_str()),0,255);
          }
      }
    }
    else if (c == 'x') //cluster
    {
      if (!StrToInt(optarg, m_cluster) || m_cluster <= 0 || m_cluster > 10)
      {
        throw string("Wrong value " + string(optarg) + " for cluster");
      }
    }
    else if (c == 'i') //interval
    {
      if (!StrToFloat(optarg, m_interval) || m_interval <= 0.0)
      {
        throw string("Wrong value " + string(optarg) + " for interval");
      }
    }
    else if (c == 't') //delay to use
    {
      if (!StrToInt(optarg, m_delay) || m_delay <= 0)
      {
        throw string("Wrong value " + string(optarg) + " for delay");
      }
    }
    else if (c == 'r') //beta 3dmode
    {
      if (!StrToInt(optarg, m_3d_mode) || m_3d_mode <= 0)
      {
        throw string("Wrong value " + string(optarg) + " for 3dmode");
      }
    }
    else if (c == 'm') // mode
    {
      if (!StrToInt(optarg, m_mode) || m_mode < 0)
      {
        throw string("Wrong value " + string(optarg) + " for mode");
      }
    }
    else if (c == 'q') // color sequence
    {
      if (!StrToInt(optarg, m_color_sequence) || m_color_sequence < 0 || m_color_sequence > 5)
      {
        throw string("Wrong value " + string(optarg) + " for colorsequence");
      }
    }
    else if (c == 'j') // fader brightness
    {
      if (!StrToInt(optarg, m_brightness) || m_brightness <= 0 || m_brightness >= 255)
      {
        throw string("Wrong value " + string(optarg) + " for brightness");
      }
    }
    else if (c == 'w') // mode
    {  
      if (!HexStrToInt(optarg, m_color) || m_color & 0xFF000000)
      {
          throw string("wrong value " + string(optarg) + " for color");
      }
    }
    else if (c == 'd') //turn on debug mode
    {
      m_debug = true;
    }
    else if (c == 'k') //turn on grabinfo mode
    {
      m_grabinfo = true;
    }
    else if (c == 'p') //turn on picdump mode
    {
      m_picdump = true;
    }
    else if (c == 'g') //turn on local grabber
    {
      m_server_enabled = true;
      m_grabber_enabled = false;
    }
    else if (c == 'u') //turn on manual adjust mode (only for enigma2 with enigmalightd from speedy1985)
    {
      m_use_manual_adjust = false;
    }
    else if (c == '?') //unknown option
    {
      //check if we know this option, but expected an argument
      if (m_flags.find(ToString((char)optopt) + ":") != string::npos)
      {
        throw string("-- Option " + ToString((char)optopt) + " requires an argument\n");
      }
      else
      {
        throw string("-- Unkown option " + ToString((char)optopt) + "\n");
      }
    }
  }

  PostGetopt(optind, argc, argv); //some postprocessing
}

//go through all options and print the descriptions to stdout
void CFlagManager::PrintEnigmaLightOptions()
{
  CEnigmaLight* enigmalight = new CEnigmaLight();

  int nroptions = enigmalight->GetNrOptions();

  for (int i = 0; i < nroptions; i++)
  {
    cout << enigmalight->GetOptionDescription(i) << "\n";
  }

  delete enigmalight;
}

void CFlagManager::ParseEnigmaLightOptions(CEnigmaLight* enigmalight)
{
  int nrlights = enigmalight->GetNrLights();
  

  for (int i = 0; i < m_options.size(); i++)
  {
    string option = m_options[i];
    string lightname;
    string optionname;
    string optionvalue;

    int    lightnr = -1; // set option for all lights

    //check if we have a lightname, otherwise we use all lights
    if (option.find(':') != string::npos)
    {
      lightname = option.substr(0, option.find(':'));
      if (option.find(':') == option.size() - 1) //check if : isn't the last char in the string
      {
        throw string("wrong option \"" + option + "\", syntax is [light:]option=value");
      }
      option = option.substr(option.find(':') + 1); //shave off the lightname

      //check which light this is
      bool lightfound = false;
      for (int j = 0; j < nrlights; j++)
      {
        if (lightname == enigmalight->GetLightName(j))
        {
          lightfound = true;
          lightnr = j;
          break;
        }
      }
      if (!lightfound)
      {
        throw string("light \"" + lightname + "\" used in option \"" + m_options[i] + "\" doesn't exist");
      }
    }

    //check if '=' exists and it's not at the end of the string
    if (option.find('=') == string::npos || option.find('=') == option.size() - 1)
    {
      throw string("wrong option \"" + option + "\", syntax is [light:]option=value");
    }

    optionname = option.substr(0, option.find('='));   //option name is everything before = (already shaved off the lightname here)
    optionvalue = option.substr(option.find('=') + 1); //value is everything after =

    option = optionname + " " + optionvalue;           //libenigmalight wants syntax without =
    
    const char *optionString = option.c_str();

    if (optionString[0] == 's' && optionString[1] == 'p')
    {
      optionString = optionString + 6;
      m_speed = strtof(optionString, NULL);
    }
    else if (optionString[0] == 'i')
    {
      //interpolation
      optionString = optionString + 14;   
          
      bool b;
      istringstream(optionString) >> std::boolalpha >> b;          
      m_interpolation = b;
    }
    else if (optionString[0] == 'u')
    {
      optionString = optionString + 4;

      bool b;
      istringstream(optionString) >> std::boolalpha >> b;
      m_use = b;
    }
    
    //bitch if we can't set this option
    if (!enigmalight->SetOption(lightnr, option.c_str()))
    {
      throw string(enigmalight->GetError());
    }
  }
}

bool CFlagManager::SetVideoGamma()
{
  for (int i = 0; i < m_options.size(); i++)
  {
    string option = m_options[i];
    if (option.find(':') != string::npos)
      option = option.substr(option.find(':') + 1); //shave off the lightname

    if (option.find('=') != string::npos)
    {
      if (option.substr(0, option.find('=')) == "gamma")
        return false; //gamma set by user, don't override
    }
  }

  m_options.push_back("gamma=" + ToString(VIDEOGAMMA));

  Log("Gamma not set, using %2.1f since this is default for video",VIDEOGAMMA);

  return true;
}

void CFlagManager::PrintHelpMessage()
{
  cout << "Usage: enigmalight [OPTION]\n";
  cout << "Start grabber: enigmalight -m 2\n";
  cout << "Start server: enigmalight -m 0\n";
  cout << "\n";
  cout << "  options:\n";
  cout << "\n";
  cout << "  -c  Set the config file, default is " << DEFAULTCONF << ".\n";
  cout << "  -d  Enable debug mode. \n";
  cout << "  -s  Address:[port], start grabber and connect with network daemon.\n";
  cout << "  -f  Fork.\n\n";

  cout << "  -o  Set option, [-o speed=30]\n";
  cout << "  -l  List options\n";
    
  cout << "\n";
  cout << "  -i  set the interval in mseconds, default is 0.1 (100 milliseconds)\n";
  cout << "  -q  set colorsequence -q 0 is RGB, 1 = BGR, 2 = GBR, 3 = GRB, 4 = BRG, 5 = RBG, [Default 0 (RGB)]\n";
  cout << "  -a  adjust color, Example: -a 255/255/30 [default it wil use 1/1/1]\n";
  cout << "  -u  disable liveadjust for other deamons [Default it is enabled]\n";
  cout << "  -m  mode, 0 = server, 1 = static, 2 = dynamic, 3 = test rgb, 4 = rgb fader, [default 2]\n";
  cout << "  -x  cluster leds, cluster the X leds as one, [default 1]\n";
  cout << "  -w  color for static mode, is in RRGGBB hex notation [default 000000]\n";
  cout << "  -j  fader brightness [default 255]\n";  
  cout << "  -t  delay, set a syncdelay. for some tv's with slow hdmi buffering.\n";
  cout << "  -p  picture dump, this option saves a lot of pictures from grabber to /tmp. \n";
  cout << "  -r  3d mode, 1 = normal, 2 = top and bottom, 3 = sidebyside, [default 1] \n";
  cout << "  -k  enable grabinfo (offset,address). \n";
  cout << "\n";

}
