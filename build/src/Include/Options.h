/*
 * EnigmaLight (c) 2014 Speedy1985, Oktay Oeztueter (Based on Boblight from Bob Loosen)
 * parts of this code were taken from
 *
 * - aiograb		(http://schwerkraft.elitedvb.net/projects/aio-grab/)
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

//              name           type    min  max    default variable         post-process
ENIGMALIGHT_OPTION(speed,         float,  0.0, 100.0,  100.0,   m_speed,         m_speed = Clamp(m_speed, 0.0, 100.0); send = true;)
ENIGMALIGHT_OPTION(autospeed,     float,  0,   100.0, 0.0,    m_autospeed,     m_autospeed = Max(m_autospeed, 0.0);)
ENIGMALIGHT_OPTION(interpolation, bool,   false, true, false, m_interpolation, send = true;)
ENIGMALIGHT_OPTION(use,           bool,   false, true, true,  m_use,           send = true;)
ENIGMALIGHT_OPTION(saturation,    float,  0.0, 20.0,  1.0,    m_saturation,    m_saturation = Max(m_saturation, 0.0);)
ENIGMALIGHT_OPTION(saturationmin, float,  0.0, 1.0,   0.0,    m_satrange[0],   m_satrange[0] = Clamp(m_satrange[0], 0.0, m_satrange[1]);)
ENIGMALIGHT_OPTION(saturationmax, float,  0.0, 1.0,   1.0,    m_satrange[1],   m_satrange[1] = Clamp(m_satrange[1], m_satrange[0], 1.0);)
ENIGMALIGHT_OPTION(value,         float,  0.0, 20.0,  1.0,    m_value,         m_value = Max(m_value, 0.0);)
ENIGMALIGHT_OPTION(valuemin,      float,  0.0, 1.0,   0.0,    m_valuerange[0], m_valuerange[0] = Clamp(m_valuerange[0], 0.0, m_valuerange[1]);)
ENIGMALIGHT_OPTION(valuemax,      float,  0.0, 1.0,   1.0,    m_valuerange[1], m_valuerange[1] = Clamp(m_valuerange[1], m_valuerange[0], 1.0);)
ENIGMALIGHT_OPTION(threshold,     int,    0,   255,   0,      m_threshold,     m_threshold = Clamp(m_threshold, 0, 255); send = false;)

ENIGMALIGHT_OPTION(gamma,         float,  0.0, 10.0,  1.0,    m_gamma,         m_gamma = Max(m_gamma, 0.0); \
  for (int i = 0; i < GAMMASIZE; i++) \
    m_gammacurve[i] = pow((float)i / ((float)GAMMASIZE - 1.0f), m_gamma) * (GAMMASIZE - 1.0f);)

ENIGMALIGHT_OPTION(hscanstart,    float,  0.0, 100.0, -1.0,   m_hscan[0],      m_hscan[0] = Clamp(m_hscan[0], 0.0, m_hscan[1]);    SetScanRange(m_width, m_height);)
ENIGMALIGHT_OPTION(hscanend,      float,  0.0, 100.0, -1.0,   m_hscan[1],      m_hscan[1] = Clamp(m_hscan[1], m_hscan[0], 100.0);  SetScanRange(m_width, m_height);)
ENIGMALIGHT_OPTION(vscanstart,    float,  0.0, 100.0, -1.0,   m_vscan[0],      m_vscan[0] = Clamp(m_vscan[0], 0.0, m_vscan[1]);    SetScanRange(m_width, m_height);)
ENIGMALIGHT_OPTION(vscanend,      float,  0.0, 100.0, -1.0,   m_vscan[1],      m_vscan[1] = Clamp(m_vscan[1], m_vscan[0], 100.0);  SetScanRange(m_width, m_height);)


