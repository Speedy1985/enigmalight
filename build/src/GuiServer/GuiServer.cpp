/*
 * EnigmaLight (c) 2014 Speedy1985, Oktay Oeztueter (Based on Boblight from Bob Loosen)
 * parts of this code were taken from
 *
 * - aiograb    (http://schwerkraft.elitedvb.net/projects/aio-grab/)
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
 
#include <stdio.h>
#include <stdlib.h>

#include <math.h>       /* log10 */
#include <string.h>

#include "Util/Misc.h"
#include "Util/Lock.h"
#include "Util/Log.h"
#include "Util/TimeUtils.h"

#include "GuiServer/GuiServer.h"

using namespace std;
extern volatile bool g_stop;

CGuiClient::CGuiClient()
{
}

CGuiServer::CGuiServer(CEnigmaLight* g_enigmalight) : m_enigmalight(g_enigmalight)
{ 
  m_grabber = NULL;
  m_client  = NULL;
  m_mode = 0;
  m_pidnr = 0;
  m_xres=m_yres=m_xres_orig=m_yres_orig = 0;
  m_fps = 0.0;
  m_clientconnected = false;

  //get pidnr
  FILE* pipe = popen("pidof enigmalight","r");
  std::string result = "";
  if (!pipe) result = "-1";
  char buffer[128];
  while(!feof(pipe)) {
    if(fgets(buffer, 128, pipe) != NULL)
      result += buffer;
  }
  pclose(pipe);

  m_pidnr = atoi(result.c_str());

  //Set socket address and port
  SetInterface("127.0.0.1",6767);
}

//Socket connection for GUI // Mainloop
void CGuiServer::Process()
{
  //
  // Loop
  //
  while(!m_stop)
  {
    if (!m_socket.IsOpen())
    {
      Log("Start GuiServer");

      Log("Opening listening socket for Enigma2 GUI on %s:%i", m_address.empty() ? "*" : m_address.c_str(), m_port);
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
        CGuiClient* client = new CGuiClient;
        int returnv = m_socket.Accept(client->m_socket);
        if (returnv == SUCCESS)
        {
          Log("GuiClient %s:%i connected successful.", client->m_socket.GetAddress().c_str(), client->m_socket.GetPort());
          AddClient(client);
        }
        else
        {
          delete client;
          Log("%s", m_socket.GetError().c_str());
        }
      }
      else
      {
        //get the client the sock fd belongs to
        CGuiClient* client = GetClientFromSock(sock);
        if (client == NULL) //guess it belongs to nobody
                continue;

        //try to read data from the client
        CTcpData data;
        int returnv = client->m_socket.Read(data);
        if (returnv == FAIL)
        { //socket broke probably
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
} // end process

void CGuiServer::Cleanup()
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
void CGuiServer::AddClient(CGuiClient* client)
{
  CLock lock(m_mutex);
    
  if (m_clients.size() >= 10) //maximum number of clients reached
  {
    LogError("Number of clients reached maximum %i", FD_SETSIZE);
    CTcpData data;
    data.SetData("full\n");
    client->m_socket.Write(data);
    delete client;
    return;
  }

  m_clients.push_back(client);
}

#define WAITTIME 100000
//does select on all the client sockets, with a timeout of 10 seconds
void CGuiServer::GetReadableFd(vector<int>& sockets)
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
CGuiClient* CGuiServer::GetClientFromSock(int sock)
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
void CGuiServer::RemoveClient(int sock)
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
void CGuiServer::RemoveClient(CGuiClient* client)
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
bool CGuiServer::HandleMessages(CGuiClient* client)
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
bool CGuiServer::ParseMessage(CGuiClient* client, CMessage& message)
{

  CTcpData data;

  string messagekey;

  const char *messageString = message.message.c_str();

  //Log("ParseMessage->%s", messageString);

  if (messageString[0] == 'g')
  {
    // get
    messageString = messageString + 4;
    return ParseGet(client, messageString, message);
  }
  else if (messageString[0] == 's')
  {
    // set
    messageString = messageString + 4;
    return ParseSet(client, messageString, message);
  }
  else if (messageString[0] == 'p' && messageString[3] == 'g') //ping
  {
    // ping
    return SendPing(client);
  }
  else
  {
    LogError("%s:%i Message (%s) unknown, ignored",
        client->m_socket.GetAddress().c_str(), client->m_socket.GetPort(), messageString);
    
    return true;
  }

  return true;
}

bool CGuiServer::ParseGet(CGuiClient* client, const char *message, CMessage& messageOrg)
{
  //Log("ParseGet->%s", message);
  CTcpData data;  

  if (message[0] == 'p' && message[3] == 'n') //pidnr
  {
    data.SetData(ToString(m_pidnr));
  }
  else if (message[0] == 'f' && message[1] == 'p') //fps
  {
    char fps[6];
    sprintf(fps, "%2.1f", m_fps);
    data.SetData(fps);//Get fps
  }
  else if (message[0] == 'r' && message[1] == 'e') //res
  {
    char res[20];
    sprintf(res, "%dx%d(%dx%d)", m_xres, m_yres, m_xres_orig, m_yres_orig);
    data.SetData(res);//resolution
  }
  else if (message[0] == 'e' && message[1] == 'r') //error
  {
    //error
  }
  else if (message[0] == 'c' && message[9] == 'p') //client port
  {
    data.SetData(ToString(m_connectedport));//client port
  }
  else if (message[0] == 'c' && message[9] == 'a') //client address
  {
    data.SetData(ToString(m_connectedaddress));//client address
  }
  else if (message[0] == 'c' && message[6] == 'c') //client connected
  {
    data.SetData(ToString(m_clientconnected));
  }
  else if (message[0] == 'm' && message[1] == 'o') //mode
  {
    data.SetData(ToString(m_mode));//mode
  }
  else
  {
    //Log("Message:%s---", message);
    LogError("%s:%i Message (%s) unknown, ignored",
        client->m_socket.GetAddress().c_str(), client->m_socket.GetPort(), message);
    
    return true;
  }

  if (client->m_socket.Write(data) != SUCCESS)
  {
    Log("%s", client->m_socket.GetError().c_str());
    return false;
  }

  return true;
  
}

bool CGuiServer::SendPing(CGuiClient* client)
{
  CTcpData data;
  data.SetData("ping");

  if (client->m_socket.Write(data) != SUCCESS)
  {
    Log("%s", client->m_socket.GetError().c_str());
    return false;
  }
  return true;
}

bool CGuiServer::ParseSet(CGuiClient* client, const char *message, CMessage& messageOrg)
{
  //Log("ParseSet->%s", message);
  CTcpData data;

  string messagekey;

  const char *messageString;

  if (message[0] == 'm' && message[3] == 'e') // Mode
  {
    messageString = message + 5; //- mode 1 space
    return ParseSetMode(client, messageString);
  }
  else if(message[0] == 'm' && message[3] == 'd') // Moodlamp_Brightness
  {
    messageString = message + 19;
    SetFaderBrightness(atoi(messageString));
  }
  else if(message[0] == '3' && message[1] == 'd') // 3Dmode
  {
    messageString = message + 6;
    if(m_grabber != NULL)
      m_grabber->Set3DMode(atoi(messageString));     
  }
  else if(message[0] == 'c' && message[1] == 'l') // Cluster
  {
    messageString = message + 7;
    if(m_grabber != NULL)
      m_grabber->SetCluster(atoi(messageString));     
  }
  else if(message[0] == 'd' && message[1] == 'e') // Delay
  {
    messageString = message + 5;
    if(m_grabber != NULL)
      m_grabber->SetDelay(atoi(messageString));
  }
  else if(message[0] == 'b' && message[9] == 'h') //Set blackbar_h
  {
    messageString = message + 10;   
        
    bool b;
    istringstream(messageString) >> std::boolalpha >> b;

    if(m_grabber != NULL)
      m_grabber->SetBlackbar_h(b);
  }
  else if(message[0] == 'b' && message[9] == 'v') //Set blackbar_v
  {
    messageString = message + 10;   
        
    bool b;
    istringstream(messageString) >> std::boolalpha >> b;

    if(m_grabber != NULL)
      m_grabber->SetBlackbar_v(b);
  }
  else if(message[0] == 'b' && message[9] == 'f') //Set blackbar_f
  {
    messageString = message + 10;   
        
    if(m_grabber != NULL)
      m_grabber->SetBlackbar_f(atoi(messageString));
  }
  else if(message[0] == 'i' && message[2] == 't') // Interval
  {
    messageString = message + 8;
    if(m_grabber != NULL)
    {
      m_grabber->m_interval = atof(messageString);
      m_grabber->m_timer.SetInterval(Round64(m_grabber->m_interval * 1000000.0));
    }
  }
  else if(message[0] == 'a' && message[1] == 'd') // Live Adjust
  {
    int adjust[3];

    string buff;
    stringstream ss;                 
    
    ss << message + 6;

    // Create vector to hold our words
    vector<string> tokens;      

    // Write to tokens
    while (ss >> buff)
        tokens.push_back(buff);

    adjust[0] = atoi(tokens[0].c_str());
    adjust[1] = atoi(tokens[1].c_str());
    adjust[2] = atoi(tokens[2].c_str());

    bool b;
    istringstream(tokens[3].c_str()) >> std::boolalpha >> b;
    m_enigmalight->SetAdjust(b, adjust);
  }
  else if(message[0] == 'c' && message[6] == 's') // Color_Sequence
  {
    messageString = message + 14;
    m_enigmalight->SetColorSequence(atoi(messageString));
  }
  else if(message[0] == 's' && message[7] == 'c') // Static_color
  {
    messageString = message + 12;
    int color;                        
    //Convert hex to int
    HexStrToInt(messageString, color);
    SetColor(color);
  }    
  else if(message[0] == 's' && message[1] == 'p' && message[2] == 'e') //Speed
  {
    messageString = message + 5;
    if(m_client != NULL)
      for (int i = 0; i < m_client->m_lights.size(); ++i)
        m_client->m_lights[i].SetSpeed(strtof(messageString,NULL));                
  }
  else
  {
    //Normal options
    if (!m_enigmalight->SetOption(-1, message))
    {
        LogError("%s:%i Message (%s) ignored",client->m_socket.GetAddress().c_str(), client->m_socket.GetPort(), messageString); 
    } 
  } 
  
  return true;      

}

bool CGuiServer::ParseSetMode(CGuiClient* client, const char *message)
{

  //Log("ParseSetMode->%s", message);

  if (message[0] == '0') // Mode
  {
    SetMode(0); //Run server
  }
  else if (message[0] == '1') // Mode
  {
    SetMode(1); //Static
  }
  else if (message[0] == '2') // Mode
  {
    SetMode(2); //Dynamic
    sleep(1); //Sleep 1sec to make the grabber instance.
  }
  else if (message[0] == '3') // Mode
  {
    SetMode(3); //Test RGB
  }
  else if (message[0] == '4') // Mode
  {
     SetMode(4); //Fader
  }
  else if (message[0] == '5') // Mode
  {
     SetMode(5); //Rainbow
  }
  else if (message[0] == '9') // Mode
  {
     SetMode(99); //Stop all
  }
  else if (message[0] == 's')
  {
    SetMode(100);

    if(m_grabber != NULL)
      m_grabber->stopLoop = true;
  }
  else
  {
    LogError("%s:%i Message ignored, Mode not supported. ",client->m_socket.GetAddress().c_str(), client->m_socket.GetPort());    
    return true;
  }
  return true;
}