/*
 * EnigmaLight (c) 2014 Speedy1985, Oktay Oeztueter (Based on Boblight from Bob Loosen)
 * parts of this code were taken from
 *
 * - aiograb		(http://schwerkraft.elitedvb.net/projects/aio-grab/)
 * - Boblight (c) 2009 Bob Loosen
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


#ifndef CGRABBER
#define CGRABBER

#include <string>
#include <sys/resource.h>

#include "Util/Timer.h"
#include "Util/Mutex.h"
#include "Util/Thread.h"
#include "Util/BlackbarDetection.h"

#include "Lights/EnigmaLightOptions.h"
#include "Config.h"
#include "FlagManager.h"

#include "MainLoop.h"

#ifndef FORWARD_GUISERVER
#define FORWARD_GUISERVER
class CGuiServer; //Forward declaration
#endif

class CGrabber : public CThread
{

  	public: 
        CGrabber(CGuiServer& g_guiserver, CEnigmaLight* g_enigmalight, CClient* g_client, volatile bool& stop, bool sync);
        ~CGrabber();

        std::string& GetError()           { return m_error; }        	  // retrieves the latest error  
        
        void SetInterval(double interval) { m_interval  = interval; } 	  // sets interval, negative means vblanks
        void SetDelay(int delay)          { m_delay     = delay; }        
        void SetDebug(bool debug)         { m_debug     = debug; }        // sets debug mode
        void SetPicdump(bool picdump)     { m_picdump   = picdump; }   	  // sets picdump mode
        void SetBlackbar_h(bool blackbar_h) { m_blackbar_h  = blackbar_h; }  // sets blackbar horizontal mode to enabled
        void SetBlackbar_v(bool blackbar_v) { m_blackbar_v  = blackbar_v; }  // sets blackbar vertical mode to enabled
        void SetBlackbar_f(int blackbar_f)  { m_blackbar_f = blackbar_f; } // when blackbar will be activated
        void Set3DMode(int _3dmode)       { m_3d_mode  = _3dmode; }       // 
        void SetGrabInfo(bool grabinfo)   { m_grabinfo  = grabinfo; }     // 

        void SetCluster(int cluster)      { m_cluster   = cluster; }      // Set cluster
        void SetManAdjust(bool manadjust) { m_manadjust = manadjust; }	


        bool Setup();                                                	  // base setup function
        bool Run();                       				             	  // main run function

        volatile bool   stopLoop;
        
        bool            SendRGB(int sync, int* outputused, int cluster_leds);                        
        void            ProcessBlackbars(CBitmap* m_frameImage, CBlackbarDetection* blackbarDetector, Bounds m_bounds);

        // Timer
        double          m_interval;                                // interval in seconds
        CTimer          m_timer;                                   // our timer

        std::string     m_error;                                   // latest error

        int             m_3d_mode;
        int             m_cluster;
        int             m_delay;
        int             m_adjust;
        int             m_vscan_depth; 
        int             m_hscan_depth; 
        int             nrlights;

        bool            m_noVideo;

        bool            m_grabinfo;
        bool            m_debug;                                   // if we have debug mode on
        bool            m_picdump;                                 // if we have picdump mode on

        bool            m_blackbar_h;
        bool            m_blackbar_v;
        int             m_blackbar_f;

        bool			m_manadjust;

        void            Fps();
        void            writeFPS(); 


        CEnigmaLight*   m_enigmalight;        
        CClient*        m_client;

        volatile bool&  m_stop;  

        CGuiServer&     m_guiserver;
};
#endif //CGRABBER