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
 
#ifndef CGUISERVER
#define CGUISERVER

#include "Util/Inclstdint.h"

#include <vector>
#include <map>

//Utils
#include "Util/Misc.h"
#include "Util/Mutex.h"
#include "Util/Thread.h"
#include "Util/TcpSocket.h"
#include "Util/MessageQueue.h"

#include "Grabber/Grabber.h"
#include "MainLoop.h"

//Forward class
class CClient;
class CGrabber;


class CGuiClient
{
    public:
        CGuiClient();
        
        CTcpClientSocket        m_socket;       //tcp socket for the client        
        CMessageQueue           m_messagequeue; //stores client messages
        void                    SetSocket(bool socket) { usocket = socket; }
        bool                    usocket;
};

class CGuiServer: public CThread
{
	public: 
        CGuiServer(CEnigmaLight* g_enigmalight);

        //For TCPSocket
        void                    SetInterface(std::string address, int port) { m_address = address; m_port = port; }
        void                    Process();
        void                    Cleanup();
        void                    SetSocket(bool socket) { usocket = socket; }
        
        std::vector<CGuiClient*>    m_clients;

        //Other
        void 			SetClientHandler(CClient* g_client)				    { m_client = g_client; }
        void            SetGrabberHandler(CGrabber* g_grabber)              { m_grabber = g_grabber; }
        void            RemoveClientHandler()                               { m_client = NULL; }
        void            RemoveGrabberHandler()                              { m_grabber = NULL; }

        void            SetColorSequence(int seq)                           { m_color_sequence = seq; }
    
        //For effects
        void            SetFaderBrightness(int brightness)                  { m_brightness  = brightness; }  // Mode, fader brighness
        void            SetColor(int color)                                 { m_color       = color; }

        void            SetConnectAddress(std::string address, int port)    { m_connectedaddress = address; m_connectedport = port; }
        void            SetInfo(float fps, int xres, int yres, int xres_orig, int yres_orig) { m_fps = fps; m_xres = xres; m_yres = yres; m_xres_orig = xres_orig; m_yres_orig = yres_orig; }
        void            SetMode(int mode)                                   { m_mode = mode; }
        void            ClientConnected(bool b)                             { m_clientconnected = b; }
        int             GetMode()                                           { return m_mode; }

/*
        ///Write to GUI
        void            Write(int msgsock, std::string messsage);
        //
*/
    	bool			m_network;
        int             m_color_sequence;
        int             m_color;
        int             m_brightness;     

    private:

        //
        // For TCPSocket
        //
        
        CMutex   m_mutex; //lock for the clients
        CTcpServerSocket m_socket; //where clients will connect to

        std::string      m_address;
        int              m_port;
        bool             usocket;

        void     AddClient(CGuiClient* client);
        void     GetReadableFd(std::vector<int>& sockets);  //does select on all the sockets
        CGuiClient* GetClientFromSock(int sock);            //gets a client from a socket fd
        void     RemoveClient(int sock);                    //removes a client based on socket
        void     RemoveClient(CGuiClient* client);          //removes a client based on pointer

        bool     HandleMessages(CGuiClient* client);        //handles client messages
        bool     ParseMessage(CGuiClient* client, CMessage& message); //parses client messages
        bool     ParseGet(CGuiClient* client, const char *message, CMessage& messageOrg);
        bool     ParseSet(CGuiClient* client, const char *message, CMessage& messageOrg);
        bool     ParseSetMode(CGuiClient* client, const char *message);

        bool     SendPing(CGuiClient* client);

        bool     m_clientconnected;

        //Other
        int             m_mode;
        int             m_pidnr;
        int             m_xres, m_yres, m_xres_orig, m_yres_orig;

        float           m_fps;

        // Used when enigmalight is running as server
        int             m_connectedport;
        std::string     m_connectedaddress;

    	CClient*		m_client;
        CGrabber*       m_grabber;
    	CEnigmaLight* 	m_enigmalight;
};

#endif