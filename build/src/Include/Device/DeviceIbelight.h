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

#ifndef CDEVICEIBELIGHT
#define CDEVICEIBELIGHT 

#include "DeviceUsb.h"
#include <libusb-1.0/libusb.h>

class CDeviceiBeLight : public CDeviceUsb
{
  public:
    CDeviceiBeLight(CMainLoop& mainloop);
    void Sync();

  protected:

    bool SetupDevice();
    bool WriteOutput();
    void CloseDevice();

    bool SetPixelCount();
    bool SetColors();
    int  BulkTransfer(struct libusb_device_handle* dev_handle, unsigned char endpoint,
                      unsigned char* data, int length, int* transferred, unsigned int timeout);

    const char* UsbErrorName(int errcode);

    CSignalTimer          m_timer;
    libusb_context*       m_usbcontext;
    libusb_device_handle* m_devicehandle;
    uint8_t*              m_chanbuffer;
};

#endif //CDEVICEIBELIGHT 
