#include "Effects/Static.h"

using namespace std;


CStatic::CStatic(CEffect* effect, CEnigmaLight* enigmalight)
{
	m_enigmalight = enigmalight;
	m_effect = effect;
}

bool CStatic::Run()
{
	Log("Static color");

	while(!m_effect->e_stop && m_effect->GetMode() == 1)
	{
		//load the color into int array
        int rgb[3] = {(m_effect->m_guiserver.m_color >> 16) & 0xFF, (m_effect->m_guiserver.m_color >> 8) & 0xFF, m_effect->m_guiserver.m_color & 0xFF};

        //set all lights to the color we want and send it
        m_enigmalight->AddPixel(-1, rgb);
        
        m_enigmalight->SendRGB(1, NULL, m_effect->m_client, 1);
        
        //sleep some ms
        usleep(50000);
	}
}