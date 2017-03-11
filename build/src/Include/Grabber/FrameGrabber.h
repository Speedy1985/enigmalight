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

#ifndef CFRAMEGRABBER
#define CFRAMEGRABBER

#include "Util/Inclstdint.h"

#include <iostream>
#include <fstream>
#include <sstream>
#include <stdio.h>
#include <stdlib.h>

#include "Util/Bitmap.h"
#include "Util/TimeUtils.h"
#include "Util/Lock.h"
#include "Util/Log.h"
#include "StbDetection/StbDetection.h"
#include "Grabber/Grabber.h"

// dont change SPARE_RAM and DMA_BLOCKSIZE until you really know what you are doing !!!
#define SPARE_RAM 252*1024*1024 // 0XFC00000 // the last 4 MB is enough...
#define DMA_BLOCKSIZE 0x3FF000 // should be big enough to hold a complete YUV 1920x1080 HD picture, otherwise it will not work properly on DM8000

class CGuiServer; //Forward declaration

class CFrameGrabber
{
	public:
                CFrameGrabber(CGrabber* grabber);
                ~CFrameGrabber();

                bool		Setup();
                bool            grabFrame(CBitmap* bitmap, int skiplines);
                bool            grabFrameOld(CBitmap* bitmap, int skiplines);
                bool            CheckRes(CBitmap* bitmap);
                
                void            sendBlank(CBitmap* bitmap);
                void            updateInfo(CBitmap* bitmap, CGuiServer& g_guiserver);

                void            getResolution(CBitmap* bitmap, int stride, long double now);

                int             mem_fd;                         // handle to the memory
                int             xres_tmp, yres_tmp;             // store resolution                
                int             m_old_3d_mode;

                bool            m_noVideo;
                bool            m_errorGiven;
                bool            m_stateBlank;

                long double     m_last_res_process;         
                long double     m_lastupdate;
                long double     m_lastmeasurement;
                long double     m_measurements;
                int64_t         fps_lastupdate;
                int             fps_framecount;
                int             m_nrmeasurements;
                long double     m_fps;     

                CTimer          m_timer;                                   // our timer
                std::string     m_error;                        // latest error

                CGrabber*       m_grabber;                      // Handler

};

#endif //CFRAMEGRABBER