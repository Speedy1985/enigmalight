#include "Effects/Effects.h"
#include "Effects/Static.h"
#include "Effects/Moodlamp.h"
#include "Effects/RGBTest.h"
#include "Effects/Rainbow.h"

using namespace std;

volatile bool e_stop = false;

CEffect::CEffect(CMainLoop* g_mainloop, CGuiServer& g_guiserver, CEnigmaLight* g_enigmalight, CClient* g_client, volatile bool& stop) :m_enigmalight(g_enigmalight), m_mainloop(g_mainloop), m_guiserver(g_guiserver), m_client(g_client), e_stop(stop)
{

}

int CEffect::GetMode()
{
  return m_guiserver.GetMode();
}

bool CEffect::Run()
{

  while(!e_stop && m_guiserver.GetMode() != 2 && m_guiserver.GetMode() != 0)
  {
  	if(m_guiserver.GetMode() == 1)    		//Static mode
    {
      CStatic* i_static = new CStatic(this,m_enigmalight);

      i_static->Run();
         
      delete i_static;
    }
    else if(m_guiserver.GetMode() == 3)  	//Test RGB
    {            
      CRgbTest* i_test = new CRgbTest(this,m_enigmalight);
       
     	i_test->Run();
       
     	delete i_test;
    }
    else if(m_guiserver.GetMode() == 4) 	// Moodlamp
    {
      CMoodlamp* i_mood = new CMoodlamp(this,m_enigmalight);
       
     	i_mood->Run();
       
     	delete i_mood;
    }
    else if(m_guiserver.GetMode() == 5) 	//Rainbow
    {
      CRainbow* i_rain = new CRainbow(this,m_enigmalight);
       
     	i_rain->Run();
       
     	delete i_rain;	    
  	}
  }	
}