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
#ifndef CDEVICEUSB
#define CDEVICEUSB 

#include "Device/Device.h"
#include <string>

#define USBDEVICE_SERIAL_SIZE 256

class CDeviceUsb: public CDevice
{
  public:
    CDeviceUsb(CMainLoop& mainloop): CDevice(mainloop), m_busnumber(-1), m_deviceaddress(-1) {}

    void SetBusNumber(int num)         { m_busnumber = num;         }
    void SetDeviceAddress(int address) { m_deviceaddress = address; }
    void SetSerial(std::string &serial){ strncpy(m_serial, serial.data(), USBDEVICE_SERIAL_SIZE); }

  protected:
    int  m_busnumber;
    int  m_deviceaddress;
    char m_serial[USBDEVICE_SERIAL_SIZE];
};

#endif //CDEVICEUSB 
