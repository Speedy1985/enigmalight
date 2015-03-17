#ifndef CCOLOR
#define CCOLOR

#include "Util/Inclstdint.h"

#include <string>
#include <vector>
#include <string.h>
#include <utility>


class CDevice; //forward declare

class CColor
{
  public:
    CColor();

    void        SetName(std::string name) { m_name = name; }
    std::string GetName()                 { return m_name; }

    void SetGamma(float gamma)           { m_gamma = gamma; }
    
    void SetAdjust(float adjust);
    
    void SetBlacklevel(float blacklevel) { m_blacklevel = blacklevel; }
    void SetRgb(float (&rgb)[3])         { memcpy(m_rgb, rgb, sizeof(m_rgb)); }
    
    float  GetGamma()      { return m_gamma; }
    float  GetAdjust()     { return m_adjust; }
    float  GetBlacklevel() { return m_blacklevel; }
    float* GetRgb()        { return m_rgb; }
    
  private:
    std::string m_name;
    
    float m_rgb[3];
    float m_gamma;
    float m_adjust;
    float m_blacklevel;
};
#endif //CCOLOR