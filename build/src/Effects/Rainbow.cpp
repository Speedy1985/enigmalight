#include "Effects/Rainbow.h"

using namespace std;


CRainbow::CRainbow(CEffect* effect, CEnigmaLight* enigmalight)
{
      m_enigmalight = enigmalight;
      m_effect = effect;
}

bool CRainbow::Run()
{
    Log("Rainbow");

    while(!m_effect->e_stop && m_effect->GetMode() == 5)
    {        
    	int rgb[7][3] = {{0xFF, 0, 0}, {0xFF, 0x80, 0}, {0xFF, 0xFF,  0}, {0, 0xFF, 0}, {0, 0, 0xFF}, {0x4B, 0, 0x82}, {0xEE, 0x82, 0xEE}};
        int numPix = m_enigmalight->GetNrLights();
        int  finalRGB[numPix][3];
        int i, j;

        for(i = 0; i < numPix; i++)
        {
	        finalRGB[i][0] = rgb[7 * i/numPix][0];
	        finalRGB[i][1] = rgb[7 * i/numPix][1];
	        finalRGB[i][2] = rgb[7 * i/numPix][2];
        }

        for(i = 0; i < numPix; i++)
        {
		        m_enigmalight->AddPixel( i, finalRGB[numPix - i]);
        }
        
        if (!m_enigmalight->SendRGB(1, NULL, m_effect->m_client, 1))
	            PrintError(m_enigmalight->GetError());
	        
	    usleep(20 * 1000);
  
    }
}           		   