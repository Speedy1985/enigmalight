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
 
#ifndef CCMAINLOOP
#define CCMAINLOOP

#include "Util/Inclstdint.h"

#include <vector>
#include <map>

//Utils
#include "Util/Misc.h"
#include "Util/Mutex.h"
#include "Util/Thread.h"
#include "Util/TcpSocket.h"
#include "Util/MessageQueue.h"

#include "FlagManager.h"

//Socket headers
#include "GuiServer/GuiServer.h"

//Light headers
#include "Lights/Light.h"

//Device headers
#include "Device/Device.h"

class CFlagManager; // Forward Class
class CGuiServer;

class CClient
{
  public:
    CClient();
    
    CTcpClientSocket        m_socket;       //tcp socket for the client
    
    CMessageQueue           m_messagequeue; //stores client messages
    int                     m_priority;     //priority of the client, 255 means an inactive client
    void                    SetPriority(int priority) { m_priority = Clamp(priority, 0, 255); }
    
    int64_t                 m_connecttime;  //when a client connected, used to decide which is the oldest client in case of same priority

    std::vector<CLight>        m_lights;    //lights of the clientstd::vector<CLight> m_lights;    //lights of the client
    std::map<std::string, int> m_lightnrs;  //tree for light names to light nr conversion for faster searching

    void                    InitLights(std::vector<CLight>& lights);
    
    int                     LightNameToInt(std::string& lightname);
    void                    SetSocket(bool socket) { usocket = socket; }
    bool                    usocket;
};

class CMainLoop
{
  public:
    CMainLoop(std::vector<CLight>& lights, CFlagManager& g_flagmanager, CEnigmaLight* g_enigmalight, CGuiServer& g_guiserver);
    
    void                    SetInterface(std::string address, int port) { m_address = address; m_port = port; }
    void                    FillChannels(std::vector<CChannel>& channels, int64_t time, CDevice* device); //called by devices
    void                    Process();

    void                    Cleanup();
    void                    SetSocket(bool socket) { usocket = socket; }
    bool                    ParseSync(CClient* client);
    void                    SetAdjust(int *adjust);
    void                    useLiveAdjust(bool useLiveAdjust) { m_useLiveAdjust = useLiveAdjust; }
    
    bool                    m_useLiveAdjust;
    
    std::vector<CClient*>   m_clients;
    CEnigmaLight*           m_enigmalight;

    CFlagManager&           m_flagmanager;
    CGuiServer&             m_guiserver;

  private:
  	
    //where clients will connect to
    CTcpServerSocket m_socket;

    std::string      m_address;
    int              m_port;
    bool             usocket;

    //clients we have, note that it's a vector of pointers so we can use a client outside a lock
    //and the pointer stays valid even if the vector changes
    
    std::vector<CLight>&  m_lights;
    
    float    m_adjust_r;
    float    m_adjust_g;
    float    m_adjust_b;

    CMutex   m_mutex; //lock for the clients
    void     AddClient(CClient* client);
    void     GetReadableFd(std::vector<int>& sockets); //does select on all the sockets
    CClient* GetClientFromSock(int sock);     //gets a client from a socket fd
    void     RemoveClient(int sock);          //removes a client based on socket
    void     RemoveClient(CClient* client);   //removes a client based on pointer
    bool     HandleMessages(CClient* client); //handles client messages
    bool     ParseMessage(CClient* client, CMessage& message); //parses client messages
    bool     ParseGet(CClient* client, const char *message, CMessage& messageOrg);
    bool     ParseSet(CClient* client, const char *message, CMessage& messageOrg);
    bool     ParseSetLight(CClient* client, const char* message, CMessage& messageOrg);

    bool     SendLights(CClient* client);     //sends light info, like name and area
    bool     SendPing(CClient* client);
};

#endif //CMAINLOOP
