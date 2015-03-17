#include "MainLoop.h" //Mainloop
#include "Util/Log.h"

#ifndef CEFFECT
#define CEFFECT

//Forward declarations
class CGuiServer; 

class CEffect
{
	public: 
        CEffect(CMainLoop* mainloop, CGuiServer& g_guiserver, CEnigmaLight* g_enigmalight, CClient* g_client, volatile bool& stop);
        int GetMode();
        bool Run();

        CMainLoop*		m_mainloop;

        volatile bool&  e_stop;  

    	CEnigmaLight*	m_enigmalight; 	//Pointer
    	CClient*		m_client;
    	CGuiServer&     m_guiserver;
};

#endif //CEFFECT
