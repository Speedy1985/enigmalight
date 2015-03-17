/*
 * EnigmaLight (c) 2014 Speedy1985, Oktay Oeztueter (Based on Boblight from Bob Loosen)
 * parts of this code were taken from
 *
 * - aiograb        (http://schwerkraft.elitedvb.net/projects/aio-grab/)
 * - boblight (c) 2009 Bob Loosen
 * 
 * EnigmaLight is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * EnigmaLight is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along
 * with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef CLIGHT
#define CLIGHT

#include "Util/Inclstdint.h"

#include <string>
#include <vector>
#include <string.h>
#include <utility>

#include "Util/Misc.h"
#include "Lights/Color.h"

class CDevice; //forward declare
    
class CLight
{
  public:
    CLight();
    
    void        SetName(std::string name)      { m_name = name; }
    void        SetPosition(std::string pos)   { m_pos  = pos;  }
    std::string GetName()                      { return m_name; }
    std::string GetPosition()                  { return m_pos;  }
    
    void        SetRgb(float (&rgb)[3], int64_t time);

    void        SetUse(bool use)                     { m_use = use; }
    void        SetInterpolation(bool interpolation) { m_interpolation = interpolation; }
    void        SetSpeed(float speed)                { m_speed = Clamp(speed, 0.0, 100.0); }
    void        SetThreshold(int threshold)          { m_threshold = Clamp(threshold, 0, 255); }
    void        SetSingleChange(float singlechange);
    void        SetAdjust(float *adjust);
    
    bool        GetUse()                             { return m_use; }
    bool        GetInterpolation()                   { return m_interpolation; }
    float       GetSpeed()                           { return m_speed; }
    int         GetThreshold()                       { return m_threshold; }
    float       GetSingleChange(CDevice* device);
    void        ResetSingleChange(CDevice* device);

    void        AddColor(CColor& color)              { m_colors.push_back(color); }
    int         GetNrColors()                        { return m_colors.size(); };
    
    
    std::string GetColorName(int colornr)            { return m_colors[colornr].GetName(); } //Function to read the colorname from CColor
    float       GetAdjust(int colornr)               { return m_colors[colornr].GetAdjust(); }    
            
    float       GetGamma(int colornr)                { return m_colors[colornr].GetGamma(); }
    float       GetBlacklevel(int colornr)           { return m_colors[colornr].GetBlacklevel(); }
    float       GetColorValue(int colornr, int64_t time);

    void        SetHscan(float* hscan) { m_hscan[0] = hscan[0]; m_hscan[1] = hscan[1]; }
    void        SetVscan(float* vscan) { m_vscan[0] = vscan[0]; m_vscan[1] = vscan[1]; }
    float*      GetVscan()                           { return m_vscan; }
    float*      GetHscan()                           { return m_hscan; }

    int         GetNrUsers()                         { return m_users.size(); }
    void        AddUser(CDevice* device);
    void        ClearUser(CDevice* device);
    CDevice*    GetUser(unsigned int user)           { return m_users[user].first; }
    
  private:
    std::string m_name;
    std::string m_pos;
    
    int64_t     m_time;        //current write time
    int64_t     m_prevtime;    //previous write time

    float       m_rgb[3];
    float       m_prevrgb[3];
    float       m_speed;
    int         m_threshold;

    bool        m_interpolation;
    bool        m_use;

    std::vector<CColor>     m_colors;

    float       m_hscan[2];
    float       m_vscan[2];
    
    float       FindMultiplier(float *rgb, float ceiling);
    float       FindMultiplier(float *rgb, float *ceiling);

    std::vector<std::pair<CDevice*, float> > m_users; //devices using this light
};

#endif //CLIGHT