#ifndef CSTATIC
#define CSTATIC

#include "Effects/Effects.h"
#include "Lights/EnigmaLightOptions.h"

class CStatic
{
	public: 
        CStatic(CEffect* effect, CEnigmaLight* enigmalight);
		bool Run();
		
    private:
    	
    	CEnigmaLight*	m_enigmalight; 	//Pointer
    	CEffect* 		m_effect;
};

#endif //CSTATIC

