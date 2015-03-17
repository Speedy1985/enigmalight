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

#ifndef FLAGMANAGER
#define FLAGMANAGER

#define VIDEOGAMMA 2.2
#define DEFAULTCONF "/etc/enigmalight.conf"

#include <string>
#include <vector>
#include "Lights/EnigmaLightOptions.h"

//class for making a copy of argc and argv
class CArguments
{
  public:
    CArguments(int argc, char** argv);
    ~CArguments();

    int    m_argc;
    char** m_argv;
};

class CFlagManager
{
  public:
    CFlagManager();

	void         PrintHelpMessage();
	
    bool         m_printhelp;                               //if we need to print the help message
    bool         m_printoptions;      			            //if we need to print the EnigmaLight options

    const char*  m_address;                                 //address to connect to, set to NULL if none given for default
    int          m_port;                                    //port to connect to, set to -1 if none given for default
    int          m_priority;                                //priority, set to 128 if none given for default
    bool         m_fork;                                    //if we should fork
    bool         m_sync;                                    //if sync mode is enabled

    void         ParseFlags(int tempargc, char** tempargv); //parsing commandline flags

    void         PrintEnigmaLightOptions();                    //printing of EnigmaLight options (-o [light:]option=value)
    void         ParseEnigmaLightOptions(CEnigmaLight* enigmalight);      //parsing of EnigmaLight options
    bool         SetVideoGamma();                           //set gamma to 2.2 if not given, returns true if done
    
    double  	m_interval;           //grab interval in seconds, or vertical blanks when negative
    int         m_pixels;             //number of pixels on lines to capture
    bool       	m_debug;              
    bool       	m_picdump;
    bool       	m_blackbar;
    bool       	m_grabinfo;
    int         m_mode;
    int         m_brightness;
    int         m_cluster;
    int         m_color;
    int         m_3d_mode;
    int         m_delay;
    int         m_adjust[3];
    int         m_color_sequence;
	bool	    m_grabber_enabled;
    bool        m_server_enabled;
    bool        m_network;
    bool		m_use_manual_adjust;

    bool        m_interpolation;
    float       m_speed;
    bool        m_use;

    std::string m_configfile;
    
    std::vector<std::string> m_options;                     //place to store EnigmaLight options
    
  protected:

    std::string  m_flags;                                   //string to pass to getopt, for example "c:r:a:p"
    std::string  m_straddress;                              //place to store address to connect to, because CArguments deletes argv

    //gets called after getopt
    virtual void PostGetopt(int optind, int argc, char** argv) {};
};

#endif //FLAGMANAGER
