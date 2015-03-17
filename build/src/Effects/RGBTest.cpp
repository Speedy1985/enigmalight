#include "Effects/RGBTest.h"

using namespace std;

CRgbTest::CRgbTest(CEffect* effect, CEnigmaLight* enigmalight)
{
      m_enigmalight = enigmalight;
      m_effect = effect;
}

bool CRgbTest::Run()
{
      Log("RGB Test");

      while(!m_effect->e_stop && m_effect->GetMode() == 3)
      {
            
            int red[3]   = {255, 0, 0};
            int green[3] = {0, 255, 0};
            int blue[3]  = {0, 0, 255};
            
            Log("RGB Test: red");
            m_enigmalight->AddPixel( -1, red);
            m_enigmalight->SendRGB(1, NULL, m_effect->m_client, 1);
            sleep(1);
            
            Log("RGB Test: green");
            m_enigmalight->AddPixel( -1, green);
            m_enigmalight->SendRGB(1, NULL, m_effect->m_client, 1);
            sleep(1);
            
            Log("RGB Test: blue");
            m_enigmalight->AddPixel( -1, blue);
            m_enigmalight->SendRGB(1, NULL, m_effect->m_client, 1);
            sleep(1);
            
      }
}            