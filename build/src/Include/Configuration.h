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

#ifndef CONFIGURATION
#define CONFIGURATION

#include <string>
#include <vector>

#include "Config.h"
#include "Lights/Light.h"
#include "MainLoop.h"
#include "Device/Device.h"
#include "Device/DeviceRs232.h"
#include "Device/DeviceDioder.h"
#include "Device/DeviceAmbioder.h"
#include "Device/DeviceIbelight.h"


//place to store relevant lines from the config file
class CConfigLine
{
  public:
    CConfigLine(std::string linestr, int iline)
    {
      linenr = iline;
      line = linestr;
    }
    
    int linenr;
    std::string line;
};

//place to group config lines
class CConfigGroup
{
  public:
    std::vector<CConfigLine> lines;
};

class CConfig
{
  public:
    bool LoadConfigFromFile(std::string file);
    bool CheckConfig(); //checks lines in the config file to make sure the syntax is correct

    //builds the config
    bool BuildConfig(CMainLoop& mainloop, std::vector<CDevice*>& devices, std::vector<CLight>& lights);

  private:
    std::string m_filename; //filename of the config file

    //config lines groups
    std::vector<CConfigLine>  m_globalconfiglines;
    std::vector<CConfigGroup> m_devicelines;
    std::vector<CConfigGroup> m_colorlines;
    std::vector<CConfigGroup> m_lightlines;

    //prints config to log
    void PrintConfig();
    void TabsToSpaces(std::string& line);

    //syntax config checks
    bool CheckGlobalConfig();
    bool CheckDeviceConfig();
    bool CheckColorConfig();
    bool CheckLightConfig();

    //gets a config line that starts with key
    int  GetLineWithKey(std::string key, std::vector<CConfigLine>& lines, std::string& line);

    void BuildServerConfig(CMainLoop& mainloop);
    bool BuildColorConfig(std::vector<CColor>& colors);
    bool BuildDeviceConfig(std::vector<CDevice*>& devices, CMainLoop& mainloop);
    bool BuildLightConfig(std::vector<CLight>& lights, std::vector<CDevice*>& devices, std::vector<CColor>& colors);

    bool BuildPopen(CDevice*& device, int devicenr, CMainLoop& mainloop);
    
    bool BuildRS232(CDevice*& device, int devicenr, CMainLoop& mainloop, const std::string& type);
    bool BuildLtbl(CDevice*& device,  int devicenr, CMainLoop& mainloop);
    bool BuildDioder(CDevice*& device, int devicenr, CMainLoop& mainloop);
    bool BuildAmbioder(CDevice*& device, int devicenr, CMainLoop& mainloop);
    bool SetDevicePrecision(CDeviceAmbioder*& device, int devicenr);

    //Using libusb
    bool BuildiBeLight(CDevice*& device, int devicenr, CMainLoop& mainloop);
    bool BuildLightpack(CDevice*& device, int devicenr, CMainLoop& mainloop);

    //For Lightpack and IBelight
    void SetDeviceBus(CDeviceUsb* device, int devicenr);
    void SetDeviceAddress(CDeviceUsb* device, int devicenr);
    void SetDeviceSerial(CDeviceUsb* device, int devicenr);

    bool SetDeviceName(CDevice* device, int devicenr);
    bool SetDeviceOutput(CDevice* device, int devicenr);
    bool SetDeviceChannels(CDevice* device, int devicenr);
    bool SetDeviceRate(CDevice* device, int devicenr);
    bool SetDeviceInterval(CDevice* device, int devicenr);
    void SetDevicePrefix(CDeviceRS232* device, int devicenr);
    void SetDevicePostfix(CDeviceRS232* device, int devicenr);

    void SetDeviceAllowSync(CDevice* device, int devicenr);
    void SetDeviceDebug(CDevice* device, int devicenr);
    bool SetDeviceBits(CDeviceRS232* device, int devicenr);
    bool SetDeviceMax(CDeviceRS232* device, int devicenr);
    void SetDeviceDelayAfterOpen(CDevice* device, int devicenr);
    void SetDeviceThreadPriority(CDevice* device, int devicenr);

    bool SetLightName(CLight& light, std::vector<CConfigLine>& lines, int lightnr);
    void SetLightScanRange(CLight& light, std::vector<CConfigLine>& lines);
};

#endif //CONFIGURATION
