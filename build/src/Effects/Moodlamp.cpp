
#include <stdlib.h>
#include "Effects/Moodlamp.h"

using namespace std;

CMoodlamp::CMoodlamp(CEffect* effect, CEnigmaLight* enigmalight)
{
	m_enigmalight = enigmalight;
    m_effect = effect;
}

bool CMoodlamp::Run()
{
    Log("Moodlamp");
    Log("Moodlamp, brightness: %d", m_effect->m_guiserver.m_brightness);

	int i;
    int m_brightness_save = m_effect->m_guiserver.m_brightness;
    int m_brightness_old = m_brightness_save;
    int rgb[3] = {m_brightness_save , m_brightness_save , m_brightness_save};
    int newRGB[3] = {m_brightness_save , m_brightness_save , m_brightness_save};

    float factor = 0.0;
    float actualBrightness;

	while(!m_effect->e_stop && m_effect->GetMode() == 4)
    {
        if(m_effect->m_guiserver.m_brightness != m_brightness_save){
            m_brightness_save = m_effect->m_guiserver.m_brightness;
            Log("Moodlamp, brightness: %d", m_effect->m_guiserver.m_brightness);
        }

		if(m_effect->m_guiserver.m_brightness != m_brightness_old)
        {
            for (int a=0; a < 3; a++)
            {
               rgb[a] = m_effect->m_guiserver.m_brightness;
               newRGB[a] = m_effect->m_guiserver.m_brightness;
            } 
             
            m_brightness_old = m_effect->m_guiserver.m_brightness;
        }
        
        while((!m_effect->e_stop) && (m_effect->GetMode() == 4) && (rgb[0] != newRGB[0] || rgb[1] != newRGB[1] || rgb[2] != newRGB[2]))
        {

	        for(i =0; i < 3; i++)
	        {
		        if(rgb[i] < newRGB[i])
		        {
			        rgb[i]++;
		        } else if(rgb[i] > newRGB[i])
		        {
			        rgb[i]--;
		        }
	        }		

	        m_enigmalight->AddPixel( -1, rgb);

	        if (!m_enigmalight->SendRGB(1, NULL, m_effect->m_client, 1))
	            PrintError(m_enigmalight->GetError());
	        
	        usleep(100 * 1000);

        }
        newRGB[0] = rand() % 0xFF;       
        newRGB[1] = rand() % 0xFF;       
        newRGB[2] = rand() % 0xFF;       

        actualBrightness = sqrt(newRGB[0] * newRGB[0] * 0.299 + newRGB[1] * newRGB[1] * 0.578 + newRGB[2] * newRGB[2] * 0.114);
        factor = m_effect->m_guiserver.m_brightness / actualBrightness;
        newRGB[0] *= factor;
        newRGB[1] *= factor;
        newRGB[2] *= factor;	

        newRGB[0] =  MIN(0xFF, newRGB[0]);
        newRGB[1] =  MIN(0xFF, newRGB[1]);
        newRGB[2] =  MIN(0xFF, newRGB[2]);
	}
}	        