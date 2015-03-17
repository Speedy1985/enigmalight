#ifndef CMOODLAMP
#define CMOODLAMP
#define MIN(a, b) ((a) < (b)) ? (a) : (b)

#include "Effects/Effects.h"
#include "Lights/EnigmaLightOptions.h"

class CMoodlamp
{
	public: 
        CMoodlamp(CEffect* effect, CEnigmaLight* enigmalight);
        bool Run();

    private:

    	CEnigmaLight*	m_enigmalight; 	//Pointer
    	CEffect*		m_effect;
};

#endif //CMOODLAMP

