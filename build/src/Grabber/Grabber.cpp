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
 
#include "Util/Inclstdint.h"
#include <iostream>
#include <fstream>
#include <sstream>

#include <stdio.h>
#include <stdlib.h>

#include "Util/Log.h"
#include "Util/Misc.h"
#include "Util/TimeUtils.h"

#include "Grabber/FrameGrabber.h"
#include "Effects/Effects.h"
#include "Util/BlackbarDetection.h"

using namespace std;

volatile bool m_stop = false;

CGrabber::CGrabber(CGuiServer& g_guiserver, CEnigmaLight* g_enigmalight, CClient* g_client, volatile bool& stop, bool sync) : m_guiserver(g_guiserver), m_enigmalight(g_enigmalight), m_client(g_client), m_stop(stop), m_timer(&stop)
{   

	// Set defaults
	m_cluster       = 1;        // Default	
	m_debug         = false;    // Default
	m_grabinfo      = false;    // Default
	m_interval      = 0.1f;     // Default interval is 10ms		
	
	stopLoop	= false;
	m_3d_mode       = 1;        // Normal mode
	m_delay         = 0;		// Video Delay	
	m_blackbar_h	= true;	//
	m_blackbar_v	= true;	//
	m_vscan_depth	= 60;
	m_hscan_depth	= 60;
	m_blackbar_f	= 10;
}

CGrabber::~CGrabber()
{    
	
}

bool CGrabber::Setup()
{
	//Get number off lights    
    nrlights = m_enigmalight->GetNrLights();
    int channels = nrlights*3;
   
	// set up for the timer
	if (m_interval > 0.0)
	{
        m_timer.SetInterval(Round64(m_interval * 1000000.0));
	}

	// Clear errors
	m_error.clear();

	Log("Lights: %d, Cluster leds: %d as one led",nrlights,m_cluster);
	Log("Channels: %d",channels);
	Log("Interval: %.2f",m_interval);
}

bool CGrabber::Run()
{
	//
    // Main loop
    //
    while(!m_stop && m_guiserver.GetMode() == 2 && !stopLoop)
	{
		//
	    // Write log and GuiInfo
	    //
    	Log("Mode -> Dynamic");

    	//
    	// New frameGrabber object
    	//
    	CFrameGrabber* m_framegrabber = new CFrameGrabber(this);	    	    	    		    

    	//
		// New bitmap object
		//
    	CBitmap* m_frameImage = new CBitmap((unsigned char*)malloc(2*2*4), 0, 0);

    	//
    	// New blackbar object
    	//
    	CBlackbarDetection* blackbarDetector = new CBlackbarDetection(m_frameImage);

    	//
    	// Setup the frameGrabber
    	//
    	if(!m_framegrabber->Setup())                           
    		return false;
    	
    	//
    	// Constructor for blackbardetection
    	//
    	Bounds m_bounds;

    	//
        // GrabLoop
        //
    	while(m_guiserver.GetMode() == 2 && !m_stop && !stopLoop)
    	{	 
    		//		    	
			// Get a RGB Frame from decoder
			//
    		if(!m_framegrabber->grabFrame(m_frameImage, 2))
    			if(!m_framegrabber->m_noVideo)
    				continue;
    		//
    		// Check resolution on changes
    		//
			if(m_framegrabber->CheckRes(m_frameImage)) // set scanrange and check if frame is blank
				continue;
			//
			// Detect blackbars
			//
			ProcessBlackbars(m_frameImage, blackbarDetector, m_bounds);

			//
            // ProcessImage , get rgb pixels and at them info buffer
            //
            m_enigmalight->ProcessImage(&m_frameImage->m_data[0], m_frameImage->GetXres(), m_frameImage->GetYres(), m_delay);  //Filter               
			
			//
			// Save image to /tmp if enabled
			//
            if (m_picdump)
            	m_frameImage->SaveImage();
           	
           	//    
            // Add filters and send to leds.
            //
            if (!SendRGB(1, NULL,m_cluster)) 
	            PrintError(m_enigmalight->GetError());	            

            //
    	    // Update fps and info for gui
    	    //
	        m_framegrabber->updateInfo(m_frameImage, m_guiserver);


	        //
	        // Wait for next loop (interval)                         
	        //
            m_timer.Wait();	  
    	}

    	//
    	// Delete objects
    	//
    	delete blackbarDetector;
    	delete m_framegrabber;
    	delete m_frameImage;
    }  
}

bool CGrabber::SendRGB(int sync, int* outputused, int cluster_leds = 1)
{	
	if (!m_enigmalight->SendRGB(sync, outputused, m_client, cluster_leds))
   		return false;
   	
   	return true;
}

void CGrabber::ProcessBlackbars(CBitmap* m_frameImage, CBlackbarDetection* blackbarDetector, Bounds m_bounds)
{
	//
	// Detect blackbars
	//
	if(m_blackbar_v || m_blackbar_h)
		m_bounds = blackbarDetector->FindBounds(m_debug, m_picdump);
		
	//
	// Set vertical scandepth
	//
	if(m_blackbar_h) //horizontal lines, top and bottom, depth is vertical
	{
		if(m_bounds.Y > 4)
		{

			blackbarDetector->m_blackCounter_h += 1;
		
			if(blackbarDetector->m_blackCounter_h > m_blackbar_f)
				blackbarDetector->m_blackCounter_h = m_blackbar_f;
			
			//Set scanning depth vertical
			if(m_vscan_depth != m_bounds.Y and blackbarDetector->m_blackCounter_h == m_blackbar_f){
				m_enigmalight->SetVscanDepth(m_bounds.Y, m_frameImage->GetXres(), m_frameImage->GetYres());
				m_vscan_depth = m_bounds.Y;
			}

		}else{

			blackbarDetector->m_blackCounter_h -= 1;
			
			if(blackbarDetector->m_blackCounter_h < 0)
				blackbarDetector->m_blackCounter_h = 0;

			//Restore default scanning depth
			if(m_vscan_depth != 0 and blackbarDetector->m_blackCounter_h == 0){
				m_enigmalight->SetVscanDepth(0, m_frameImage->GetXres(), m_frameImage->GetYres());;
				m_vscan_depth = 0;
			}
		}
	}

	//
	//Set horizontal scandepth
	//
	if(m_blackbar_v) //vertical lines left and right, depth is horizontal
	{
		if(m_bounds.X > 4){	
			//Set scanning depth horizontal

			blackbarDetector->m_blackCounter_v += 1;
		
			if(blackbarDetector->m_blackCounter_v > m_blackbar_f)
				blackbarDetector->m_blackCounter_v = m_blackbar_f;

			if(m_hscan_depth != m_bounds.X and blackbarDetector->m_blackCounter_v == m_blackbar_f){
				m_enigmalight->SetHscanDepth(m_bounds.X, m_frameImage->GetXres(), m_frameImage->GetYres());
				m_hscan_depth = m_bounds.X;
			}
		}
		else{

			blackbarDetector->m_blackCounter_v -= 1;
			
			if(blackbarDetector->m_blackCounter_v < 0)
				blackbarDetector->m_blackCounter_v = 0;

			//Restore default scanning depth
			if(m_hscan_depth != 0 and blackbarDetector->m_blackCounter_v == 0){
				m_enigmalight->SetHscanDepth(0, m_frameImage->GetXres(), m_frameImage->GetYres());;
				m_hscan_depth = 0;
			}					
		}
	}

	//
	// Restore default scanning depth
	//
	if(!m_blackbar_h) //horizontal lines, top and bottom
	{
		if(m_vscan_depth != 0){
			m_enigmalight->SetVscanDepth(0, m_frameImage->GetXres(), m_frameImage->GetYres());;
			m_vscan_depth = 0;
			blackbarDetector->m_blackCounter_h =0;
		}	
	}

	if(!m_blackbar_v) //vertical lines left and right
	{
		if(m_hscan_depth != 0){
			m_enigmalight->SetHscanDepth(0, m_frameImage->GetXres(), m_frameImage->GetYres());;
			m_hscan_depth = 0;
			blackbarDetector->m_blackCounter_v =0;
		}
	}
}

