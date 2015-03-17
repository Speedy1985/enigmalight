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

#include <iostream> //debug
#include <vector>
#include <string>
#include <sstream>
#include <iterator>
#include <algorithm>
#include <list>
#include <locale.h>
#include <stdlib.h>

#include "Config.h"
#include "MainLoop.h"

#include "Grabber/Grabber.h"
#include "Effects/Effects.h"
 
#include "Util/Lock.h"
#include "Util/Log.h"
#include "Util/TimeUtils.h"

using namespace std;

extern volatile bool g_stop;
volatile bool grabber_stop = false;

CClient::CClient()
{
	m_priority = 255;
	m_connecttime = -1;	
}

void CClient::InitLights(std::vector<CLight>& lights)
{
	m_lights = lights;
	//generate a tree for fast lightname->lightnr conversion
	for (int i = 0; i < m_lights.size(); ++i)
        m_lightnrs[m_lights[i].GetName()] = i;
}

int CClient::LightNameToInt(std::string& lightname)
{
  map<string, int>::iterator it = m_lightnrs.find(lightname);
  if (it == m_lightnrs.end())
    return -1;

  return it->second;
}

CMainLoop::CMainLoop(std::vector<CLight>& lights, CFlagManager& g_flagmanager, CEnigmaLight* g_enigmalight, CGuiServer& g_guiserver) :m_lights(lights), m_flagmanager(g_flagmanager), m_enigmalight(g_enigmalight), m_guiserver(g_guiserver)
{
	//Default Adjustment settings
	m_adjust_r = 1.0;
	m_adjust_g = 1.0;
	m_adjust_b = 1.0;

	m_useLiveAdjust = false;
}

/////////////////////////
//
// this is called from a loop from main()
// the mainloop
//
/////////////////////////

void CMainLoop::Process()
{	
	m_guiserver.StartThread();

	//Set color sequence default or from commandline
	m_guiserver.SetColorSequence(m_flagmanager.m_color_sequence);

	//Default static color
	m_guiserver.SetColor(m_flagmanager.m_color);

	//Default fader brightness for effects
	m_guiserver.SetFaderBrightness(m_flagmanager.m_brightness);
	
	//Default Mode is Dynamic is nothing is set
	m_guiserver.SetMode(m_flagmanager.m_mode);

	//Default color sequence RGB
	m_enigmalight->SetColorSequence(m_flagmanager.m_color_sequence);

	//if we can't parse the option lines (given with -o) properly, just exit
	try
	{
		m_flagmanager.ParseEnigmaLightOptions(m_enigmalight);
	}
	catch (string error)
	{
		PrintError(error);
		g_stop=true;
	}


	//Start mainloop
	while(!g_stop)
	{

		///////////////////////////
		//
		//	Server
		//
		///////////////////////////
		if(m_guiserver.GetMode() == 0) //open listening socket if it's not already
		{
			if (!m_socket.IsOpen())
			{

				Log("Start EnigmaLight Server");

				Log("Opening listening socket on %s:%i", m_address.empty() ? "*" : m_address.c_str(), m_port);
				if (!m_socket.Open(m_address, m_port, 1000000))
				{
				  LogError("%s", m_socket.GetError().c_str());
				  m_socket.Close();
				}
			}

			//see if there's a socket we can read from
			vector<int> sockets;
			GetReadableFd(sockets);

			for (vector<int>::iterator it = sockets.begin(); it != sockets.end(); ++it)
			{
				int sock = *it;
				if (sock == m_socket.GetSock()) //we can read from the listening socket
				{
				  CClient* client = new CClient;
				  int returnv = m_socket.Accept(client->m_socket);
				  if (returnv == SUCCESS)
				  {
				  	m_guiserver.ClientConnected(true);
				    m_guiserver.SetConnectAddress(client->m_socket.GetAddress().c_str(),client->m_socket.GetPort());

				    Log("Client %s:%i connected successful.", client->m_socket.GetAddress().c_str(), client->m_socket.GetPort());
				    AddClient(client);				  
				  }
				  else
				  {
				    delete client;
				    m_guiserver.ClientConnected(false);
				    Log("%s", m_socket.GetError().c_str());
				  }
				}
				else
				{
					//get the client the sock fd belongs to
					CClient* client = GetClientFromSock(sock);
					if (client == NULL) //guess it belongs to nobody
			            continue;

					//try to read data from the client
					CTcpData data;
					int returnv = client->m_socket.Read(data);
					if (returnv == FAIL)
					{ //socket broke probably
						m_guiserver.ClientConnected(false);
						Log("%s", client->m_socket.GetError().c_str());
						RemoveClient(client);
						continue;
					}

					char* sth_data;
					int sth_size;

					sth_data=data.GetData();
					sth_size=data.GetSize();

					if( sth_size < 0 ) 
						continue;

					//add data to the messagequeue
					client->m_messagequeue.AddData(sth_data, sth_size);

					//check messages from the messaqueue and parse them, if it fails remove the client
					if (!HandleMessages(client))
						RemoveClient(client);
		    	}
		    }
		}

		//////////////////////////////////////////////
		//
		//	Dynamic / Effects (Moodlamp)
		//
		//////////////////////////////////////////////
		else if(m_guiserver.GetMode() != 0 && m_guiserver.GetMode() != 100)
		{			
			//Network mode, connect with daemon on host.
		    if(m_flagmanager.m_network)
		    {
		      //Connect with external grabber
		      Log("Connecting to external daemon...");

		      //try to connect, if we can't then bitch to stderr
		      if (!m_enigmalight->Connect(m_flagmanager.m_address, m_flagmanager.m_port, 5000000) ||
		          !m_enigmalight->SetPriority(122))
		      {
		        PrintError(m_enigmalight->GetError());
		        exit(1);

		      }else{
		        Log("Connection to host [%s:%i] opened!",m_flagmanager.m_address,m_flagmanager.m_port);
		  	  }	
		    }

			// Clean socket if opened
			if (m_socket.IsOpen())
			{
				Cleanup();
			}

			//Set priority on server
			if(m_flagmanager.m_network)
		    {
		    	m_enigmalight->SetPriority(122);
		    }

			// Add client
			CClient* client = new CClient;
			AddClient(client);

			//Set clientHandler for CGuiServer
			m_guiserver.SetClientHandler(client);
			
			// Set speed for client
			for (int i = 0; i < client->m_lights.size(); ++i)
    		{
				client->m_lights[i].SetSpeed(m_flagmanager.m_speed);
			}

			//Only use this for local client
			if(!m_flagmanager.m_network)
				if(m_flagmanager.m_use_manual_adjust == true)
					m_enigmalight->SetAdjust(true,m_flagmanager.m_adjust);

			// Set gamma, if gamma is not set then use standard 2.2 since this is standard for video.
			m_flagmanager.SetVideoGamma();
			
			///////////////////////////
			//
			//	Dynamic
			//
			///////////////////////////
			if(m_guiserver.GetMode() == 2)
			{
				// New grabber
	    		CGrabber* m_grabber = new CGrabber(m_guiserver, m_enigmalight, client, g_stop, m_flagmanager.m_sync);
	    		
	    		// New grabberHandler for CGuiServer
		    	m_guiserver.SetGrabberHandler(m_grabber);

		    	// Set grabber settings from commandline
				m_grabber->SetInterval(m_flagmanager.m_interval);             // Set interval.
				m_grabber->SetDebug(m_flagmanager.m_debug);                   // Set debug enabled or disabled.
				m_grabber->SetPicdump(m_flagmanager.m_picdump);               
				m_grabber->Set3DMode(m_flagmanager.m_3d_mode); 
				
				m_grabber->SetGrabInfo(m_flagmanager.m_grabinfo);             // Testing....
				//m_grabber->SetBlackbar(m_flagmanager.m_blackbar);           // Set blackbardetection enabled or disabled/
				m_grabber->SetDelay(m_flagmanager.m_delay);                   // Set delay for slow hdmi transfer
				m_grabber->SetCluster(m_flagmanager.m_cluster);               // Set cluster			
				m_grabber->SetManAdjust(m_flagmanager.m_use_manual_adjust);   // Manual Ajust on or off

				Log("Starting grabber..");

		      	// Start grabberloop
		      	if(m_grabber->Setup())
		        	m_grabber->Run();

		        // Remove grabber
		        delete m_grabber;

		        // Remove handler from CGuiServer
	        	m_guiserver.RemoveGrabberHandler();

			}
			///////////////////////////
			//
			//	Effects
			//
			///////////////////////////
			else if(m_guiserver.GetMode() != 0 && m_guiserver.GetMode() != 100)
			{
				//Init Effects
	   			CEffect* m_effect = new CEffect(this, m_guiserver, m_enigmalight, client, g_stop); 

	   			//Start effects
	        	m_effect->Run();

	        	delete m_effect;
			}			

	        // Remove clients
	        RemoveClient(client);

	        // Remove clientHandler from CGuiServer
	        m_guiserver.RemoveClientHandler();	    

	        // Reset fps and other info
	        m_guiserver.SetInfo(0.0,0,0,0,0);

	        //Set priority on server
	        if(m_flagmanager.m_network)
		    {
		    	m_enigmalight->SetPriority(255);
		    }

		}		
		else if(m_guiserver.GetMode() == 100)
		{
			g_stop = true;
			break;
		}


		///////////////////////////
		//
		//	Nothing, wait...
		//
		///////////////////////////
		else
		{
			// Clean socket if opened
			if (m_socket.IsOpen())
			{
				Cleanup();
			}

			//Log("Sleep, no mode defined...");			

			#define SLEEPTIME 100000
			CLock lock(m_mutex);
			
			USleep(SLEEPTIME, &g_stop);

			// Reset fps and other info
	        m_guiserver.SetInfo(0.0,0,0,0,0);

			lock.Leave();
		}
	}

	// Stop listeningsocket for GUI
	//m_guiserver.Close();
	m_guiserver.Cleanup();
	m_guiserver.StopThread();
	
}

void CMainLoop::Cleanup()
{
	//kick off all clients
	Log("Removing clients");
	CLock lock(m_mutex);
	while (m_clients.size())
	{
		RemoveClient(m_clients.front());
	}
	lock.Leave();

	Log("Closing listening socket");
	m_socket.Close();
}

//called by the server handler
void CMainLoop::AddClient(CClient* client)
{
	CLock lock(m_mutex);
    
    if(!m_flagmanager.m_network)
    {
		client->m_priority = 128;
		client->m_connecttime = GetTimeUs();
	}
	else
	{
		if (m_clients.size() >= 1) //maximum number of clients reached
		{
			LogError("Number of clients reached maximum %i", FD_SETSIZE);
			CTcpData data;
			data.SetData("full\n");
			client->m_socket.Write(data);
			delete client;
			return;
		}
	}	
	
	//assign lights and put the pointer in the clients vector
	client->InitLights(m_lights);
	m_clients.push_back(client);
}

#define WAITTIME 100000
//does select on all the client sockets, with a timeout of 10 seconds
void CMainLoop::GetReadableFd(vector<int>& sockets)
{
	CLock lock(m_mutex);

	//no clients so we just sleep
	if (m_clients.size() == 0 && !m_socket.IsOpen())
	{
		lock.Leave();
		USleep(WAITTIME, &g_stop);
		return;
	}

	//store all the client sockets
	vector<int> waitsockets;
	waitsockets.push_back(m_socket.GetSock());
	for (int i = 0; i < m_clients.size(); ++i)
		waitsockets.push_back(m_clients[i]->m_socket.GetSock());

	lock.Leave();

	int highestsock = -1;
	fd_set rsocks;

	FD_ZERO(&rsocks);
	for (int i = 0; i < waitsockets.size(); ++i)
	{
		FD_SET(waitsockets[i], &rsocks);
		if (waitsockets[i] > highestsock)
			highestsock = waitsockets[i];
	}

	struct timeval tv;
	tv.tv_sec = WAITTIME / 1000000;
	tv.tv_usec = (WAITTIME % 1000000);

	int returnv = select(highestsock + 1, &rsocks, NULL, NULL, &tv);

	if (returnv == 0) //select timed out
	{
		return;
	}
	else if (returnv == -1) //select had an error
	{
		//Log("[GetReadableFd] select() %s", GetErrno().c_str());
		return;
	}

	//return all sockets that can be read
	for (int i = 0; i < waitsockets.size(); ++i)
	{
		if (FD_ISSET(waitsockets[i], &rsocks))
			sockets.push_back(waitsockets[i]);
	}
}


//gets a client from a socket fd
CClient* CMainLoop::GetClientFromSock(int sock)
{
	CLock lock(m_mutex);
	for (int i = 0; i < m_clients.size(); ++i)
	{
		if (m_clients[i]->m_socket.GetSock() == sock)
			return m_clients[i];
	}
	return NULL;
}

//removes a client based on socket
void CMainLoop::RemoveClient(int sock)
{
	CLock lock(m_mutex);
	for (int i = 0; i < m_clients.size(); ++i)
	{
		if (m_clients[i]->m_socket.GetSock() == sock)
		{
			Log("Removing %s:%i",
					m_clients[i]->m_socket.GetAddress().c_str(), m_clients[i]->m_socket.GetPort());
			delete m_clients[i];
			m_clients.erase(m_clients.begin() + i);

			return;
		}
	}
}

//removes a client based on pointer
void CMainLoop::RemoveClient(CClient* client)
{
	CLock lock(m_mutex);
	for (int i = 0; i < m_clients.size(); ++i)
	{
		if (m_clients[i] == client)
		{
			//Log("removing %s:%i",m_clients[i]->m_socket.GetAddress().c_str(), m_clients[i]->m_socket.GetPort());
			delete m_clients[i];
			m_clients.erase(m_clients.begin() + i);
			
			return;
		}
	}
}

//handles client messages
bool CMainLoop::HandleMessages(CClient* client)
{
	if (client->m_messagequeue.GetRemainingDataSize() > MAXDATA) //client sent too much data
	{
		LogError("%s:%i sent too much data",
				client->m_socket.GetAddress().c_str(), client->m_socket.GetPort());
		return false;
	}

	//loop until there are no more messages
	while (client->m_messagequeue.GetNrMessages() > 0)
	{
		CMessage message = client->m_messagequeue.GetMessage();
		if (!ParseMessage(client, message))
			return false;
	}
	return true;
}

//parses client messages
bool CMainLoop::ParseMessage(CClient* client, CMessage& message)
{
	CTcpData data;

	string messagekey;

	const char *messageString = message.message.c_str();

	//Log("[ParseMessage] >>> %s", message.message.c_str());

	if (messageString[0] == 'h')
	{
		// hello
		Log("%s:%i said hello",
				client->m_socket.GetAddress().c_str(), client->m_socket.GetPort());
		data.SetData("hello\n");
		if (client->m_socket.Write(data) != SUCCESS)
		{
			Log("ERROR %s", client->m_socket.GetError().c_str());
			return false;
		}
		CLock lock(m_mutex);
		if (client->m_connecttime == -1)
			client->m_connecttime = message.time;
	}
	else if (messageString[0] == 'p')
	{
		// ping
		return SendPing(client);
	}
	else if (messageString[0] == 'g' && messageString[4] == 'v')
	{
		// version
		data.SetData("version 5\n");
		if (client->m_socket.Write(data) != SUCCESS)
		{
			Log("ERROR %s", client->m_socket.GetError().c_str());
			return false;
		}

	}
	else if (messageString[0] == 'g')
	{
		// get
		messageString = messageString + 4; // string = get xxxxx // messageString +4 means, set [0] to start from [4]
		return ParseGet(client, messageString, message);
	}
	else if (messageString[0] == 's' && messageString[1] == 'e')
	{
		// set
		messageString = messageString + 4;
		return ParseSet(client, messageString, message);
	}
	else if (messageString[0] == 's' && messageString[1] == 'y')
	{
		// sync
		return ParseSync(client);
	}
	else
	{
		//Log("Message:%s---", message);
		LogError("%s:%i Message unknown, ignored",
				client->m_socket.GetAddress().c_str(), client->m_socket.GetPort());
		
		return true;
	}

	return true;
}

bool CMainLoop::ParseGet(CClient* client, const char *message, CMessage& messageOrg)
{
	//Log("Get->%s", message);
	//Log("Get->%c", message[0]);
    
	if (message[0] == 'l')
	{
		return SendLights(client);  // light
	}
	else
	{
		//Log("Message:%s---", message);
		LogError("%s:%i Message unknown, ignored",
				client->m_socket.GetAddress().c_str(), client->m_socket.GetPort());
		
		return true;
	}
}

//sends light info, like name and area
bool CMainLoop::SendLights(CClient* client)
{
	CTcpData data;

	//build up messages by appending to CTcpData
	data.SetData("lights " + ToString(client->m_lights.size()) + "\n");
    
	for (int i = 0; i < client->m_lights.size(); ++i)
	{
		data.SetData("light " + client->m_lights[i].GetName() + " ", true);
		data.SetData("scan ", true);
		data.SetData(ToString(client->m_lights[i].GetVscan()[0]) + " ", true);
		data.SetData(ToString(client->m_lights[i].GetVscan()[1]) + " ", true);
		data.SetData(ToString(client->m_lights[i].GetHscan()[0]) + " ", true);
		data.SetData(ToString(client->m_lights[i].GetHscan()[1]), true);
		data.SetData("\n", true);
	}

	if (client->m_socket.Write(data) != SUCCESS)
	{
		Log("%s", client->m_socket.GetError().c_str());
		return false;
	}
	return true;
}

bool CMainLoop::SendPing(CClient* client)
{
	CLock lock(m_mutex);

	//check if any light is used
	int lightsused = 0;
	for (unsigned int i = 0; i < client->m_lights.size(); ++i)
	{
		if (client->m_lights[i].GetNrUsers() > 0)
		{
			lightsused = 1;
			break; //if one light is used we have enough info
		}
	}

	lock.Leave();

	CTcpData data;
	data.SetData("ping " + ToString(lightsused) + "\n");

	if (client->m_socket.Write(data) != SUCCESS)
	{
		Log("%s", client->m_socket.GetError().c_str());
		return false;
	}
	return true;
}

void CMainLoop::SetAdjust(int *adjust)
{
	CLock lock(m_mutex);
	//cout << "SetAdjust " << m_adjust_r << " " << m_adjust_g  << " " << m_adjust_b << " " << "\n";
	m_adjust_r = (float)adjust[0] / 255.0;
	m_adjust_g = (float)adjust[1] / 255.0;
	m_adjust_b = (float)adjust[2] / 255.0;

	lock.Leave();
}

bool CMainLoop::ParseSet(CClient* client, const char *message, CMessage& messageOrg)
{

	if (message[0] == 'p')
	{
		// priority XXX
		message = message + 9;
		int priority = atoi(message);

		CLock lock(m_mutex);
		client->SetPriority(priority);
		lock.Leave();
		Log("%s:%i priority set to %i",
				client->m_socket.GetAddress().c_str(), client->m_socket.GetPort(), client->m_priority);
	}
	else if (message[0] == 'l')
	{
		//light
		message = message + 6;
		return ParseSetLight(client, message, messageOrg);
	}
	else if (message[0] == 'a') //adjust
	{
		int adjust[3]; //can hold 3 values r g and b
		string value;
		message = message + 7; // Go to numbers and skip word adjust+space
	
		string s = message;
		istringstream iss(s);   
		int n;
	
		CLock lock(m_mutex);        
		for(int i=0; i < 3; ++i){
		    iss >> n;
		    adjust[i] = n;
		}
		
		SetAdjust(adjust);
	
		//Log("Message arrived -> ADJUST[0]:%f,ADJUST[1]:%f,ADJUST[2]:%f", m_adjust_r,m_adjust_g,m_adjust_b);		
	}
	else
	{
		LogError("%s:%i Message ignored",client->m_socket.GetAddress().c_str(), client->m_socket.GetPort());		
		return true;
	}
	return true;
}

bool CMainLoop::ParseSetLight(CClient* client, const char* message, CMessage& messageOrg)
{
	char *light = new char[4];
	strncpy(light, message, 3);
	light[3] = '\0';

	std::string lightName(light);
    
	//delete char
	delete(light);
  
	int lightnr = client->LightNameToInt(lightName);


	if (lightnr == -1)
	{
		return false;
	}

	message = message + 4;

	if (lightnr == -1)
	{
		//Log("Message:%s---", message);
		LogError("%s:%i Message unknown, ignored",
				client->m_socket.GetAddress().c_str(), client->m_socket.GetPort());
		
		return true;
	}

	if (message[0] == 'r')
	{
		float rgb[3];
		string value;
		message = message + 4;
		//Log("Floats:%s", message);

		char* pEnd1;
		char* pEnd2;
		rgb[0] = strtof(message, &pEnd1);
		rgb[1] = strtof(pEnd1, &pEnd2);
		rgb[2] = strtof(pEnd2, NULL);
		
		CLock lock(m_mutex);
		client->m_lights[lightnr].SetRgb(rgb, messageOrg.time);    
	}
    
	else if (message[0] == 's' && message[1] == 'p')
	{
		message = message + 6;
		float speed = strtof(message, NULL);

		CLock lock(m_mutex);
		client->m_lights[lightnr].SetSpeed(speed);
	}
	else if (message[0] == 't' && message[1] == 'h')
	{
	    //threshold	    
		message = message + 10;
		int threshold = atoi(message);
        //printf("set threshold to %i\n",threshold);
        
		CLock lock(m_mutex);
		client->m_lights[lightnr].SetThreshold(threshold);
	}
	else if (message[0] == 'i')
	{
		//interpolation
		message = message + 14;		
        
		bool b;
		istringstream(message) >> std::boolalpha >> b;
        
		CLock lock(m_mutex);
		client->m_lights[lightnr].SetInterpolation(b);
	}
	else if (message[0] == 'u')
	{
		message = message + 4;

		bool b;
		istringstream(message) >> std::boolalpha >> b;

		CLock lock(m_mutex);
		client->m_lights[lightnr].SetUse(b);
	}
	else if (message[0] == 's' && message[1] == 'i')
	{
		//singlechange
		message = message + 13;
		float singlechange = strtof(message, NULL);

		CLock lock(m_mutex);
		client->m_lights[lightnr].SetSingleChange(singlechange);
	}
	else
	{
		//Log("Message:%s---", message);
		LogError("%s:%i Message unknown, ignored",
				client->m_socket.GetAddress().c_str(), client->m_socket.GetPort());
		
		return true;
	}
  
  
	return true;
}

//wakes up all devices that use this client, so the client input and the device output is synchronized
bool CMainLoop::ParseSync(CClient* client)
{
	CLock lock(m_mutex);

	list<CDevice*> users;

	//build up a list of devices using this client's input
	for (unsigned int i = 0; i < client->m_lights.size(); ++i)
	{
		//printf("Sync %d\n",i);
		for (unsigned int j = 0; j < client->m_lights[i].GetNrUsers(); ++j){
			users.push_back(client->m_lights[i].GetUser(j));
		}	
	}

	lock.Leave();

	//remove duplicates
	users.sort();
	users.unique();

	//message all devices
	for (list<CDevice*>::iterator it = users.begin(); it != users.end(); ++it)
		(*it)->Sync();

	return true;
}

//called by devices
void CMainLoop::FillChannels(std::vector<CChannel>& channels,
		int64_t time, CDevice* device)
{

	list<CLight*> usedlights;

	CLock lock(m_mutex);
    
	//get the oldest client with the highest priority
	for (int i = 0; i < channels.size(); ++i)
	{
		int64_t clienttime = 0x7fffffffffffffffLL;
		int priority = 255;
		int light = channels[i].GetLight();
		int color = channels[i].GetColor();		
		
		int clientnr = -1;

		if (light == -1 || color == -1){ //unused channel		
			continue;
		}

		for (int j = 0; j < m_clients.size(); ++j)
		{
			//printf("Clients: %d\n",m_clients.size());
			if (m_clients[j]->m_priority == 255
					|| m_clients[j]->m_connecttime == -1
					|| !m_clients[j]->m_lights[light].GetUse())
				continue; //this client we don't use

			//this client has a high priority (lower number) than the current one, or has the same and is older
			if (m_clients[j]->m_priority < priority
					|| (priority == m_clients[j]->m_priority
							&& m_clients[j]->m_connecttime < clienttime))
			{
				clientnr = j;
				clienttime = m_clients[j]->m_connecttime;
				priority = m_clients[j]->m_priority;
			}
		}

		if (clientnr == -1) //no client for the light on this channel
		{
			//printf("no client for the light on this channel:%d\n",i);
			channels[i].SetUsed(false);
			channels[i].SetValueToFallback();
			channels[i].SetAdjust(1.0);
			channels[i].SetValues(m_lights[light].GetSpeed(), 0.0, 1.0, 0.0);		
			continue;
		}

		//
		// Get all needed values
		//

		float colorValue  = m_clients[clientnr]->m_lights[light].GetColorValue(color,time);
		float speed 	  = m_clients[clientnr]->m_lights[light].GetSpeed();
		float gamma 	  = m_clients[clientnr]->m_lights[light].GetGamma(color);
        float blacklevel  = m_clients[clientnr]->m_lights[light].GetBlacklevel(color);
	
        //
		// Fill channel with values from the client
		//
	
		channels[i].SetValues(speed, colorValue, gamma, blacklevel);		
		

		if(m_adjust_r > 0 || m_adjust_g > 0 || m_adjust_b > 0)
		{
			std::string cname;
			cname = m_clients[clientnr]->m_lights[light].GetColorName(color);
		
			//cout << "Use live adjust "; 
		    if(cname == "red")
		        channels[i].SetAdjust(m_adjust_r);
		    else if(cname == "green")
		        channels[i].SetAdjust(m_adjust_g);
		    else if(cname == "blue")
		        channels[i].SetAdjust(m_adjust_b);
		}else{
    		//cout << "Use default adjust... color: " << cname << ":[" << m_clients[clientnr]->m_lights[light].GetAdjust(color) << "]\n";
		    //Use the values from configfile
		    channels[i].SetAdjust(m_clients[clientnr]->m_lights[light].GetAdjust(color));
        }        
        		
		//Debug
		
		channels[i].SetSingleChange(
				m_clients[clientnr]->m_lights[light].GetSingleChange(device));

		//save pointer to this light because we have to reset the singlechange later
		//more than one channel can use a light so can't do this from the loop
		usedlights.push_back(&m_clients[clientnr]->m_lights[light]);
	}

	//remove duplicate lights
	usedlights.sort();
	usedlights.unique();

	
	//reset singlechange
	for (list<CLight*>::iterator it = usedlights.begin();
			it != usedlights.end(); ++it)
		(*it)->ResetSingleChange(device);

	//update which lights we're using
	for (int i = 0; i < m_clients.size(); ++i)
	{
		for (int j = 0; j < m_clients[i]->m_lights.size(); ++j)
		{
			bool lightused = false;
			for (list<CLight*>::iterator it = usedlights.begin();
					it != usedlights.end(); ++it)
			{
				if (*it == &m_clients[i]->m_lights[j])
				{
					lightused = true;
					break;
				}
			}

			if (lightused){
				m_clients[i]->m_lights[j].AddUser(device);
			}else{
				m_clients[i]->m_lights[j].ClearUser(device);
			}
		}
	}
}
