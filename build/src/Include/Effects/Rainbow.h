#ifndef CRAINBOW
#define CRAINBOW

#include "Effects/Effects.h"
#include "Lights/EnigmaLightOptions.h"


class CRainbow
{
	public: 
        CRainbow(CEffect* effect, CEnigmaLight* enigmalight);
        bool Run();
        
    private:

    	CEnigmaLight*	m_enigmalight; 	//Pointer
    	CEffect* 		m_effect;
};

#endif //CRAINBOW

