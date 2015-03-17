#ifndef CRGBTEST
#define CRGBTEST

#include "Effects/Effects.h"
#include "Lights/EnigmaLightOptions.h"


class CRgbTest
{
	public: 
        CRgbTest(CEffect* effect, CEnigmaLight* enigmalight);
        bool Run();
        
    private:

    	CEnigmaLight*	m_enigmalight; 	//Pointer
    	CEffect* 		m_effect;
};

#endif //CRGBTEST

