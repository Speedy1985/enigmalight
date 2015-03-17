/*
 * EnigmaLight (c) 2014 Speedy1985, Oktay Oeztueter (Based on Boblight from Bob Loosen)
 * parts of this code were taken from
 *
 * - aiograb		(http://schwerkraft.elitedvb.net/projects/aio-grab/)
 * - enigmalight (c) 2009 Bob Loosen
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

#include "DeviceRs232.h"

#ifndef DEVICEAMBIODER
#define DEVICEAMBIODER

class CDeviceAmbioder : public CDeviceRS232
{
  public:
    CDeviceAmbioder(CMainLoop& mainloop);
    bool SetPrecision(int max);

  private:
    int m_precision;
    bool SetupDevice();
    bool WriteOutput();
    void CloseDevice();
    ~CDeviceAmbioder();
};

#endif //DEVICEAMBIODER
