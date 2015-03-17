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
 //

// General includes
#include <iostream>
#include <stdio.h>
#include <stdlib.h>

// Util includes
#include "Util/Inclstdint.h"
#include "Util/Misc.h"
#include "Util/TimeUtils.h"
#include "Util/Lock.h"
#include "Util/Log.h"

// Grabber includes
#include "Grabber/FrameGrabber.h"

using namespace std;

CStb m_stb;

CFrameGrabber::CFrameGrabber(CGrabber* grabber) : m_grabber(grabber)
{	
	xres_tmp    = 0;
	yres_tmp    = 0;
	m_last_res_process  = 0.0;
}

CFrameGrabber::~CFrameGrabber()
{
	// close handle on memory
	Log("Close memory /dev/mem"); 
	close(mem_fd);
}

bool CFrameGrabber::Setup()
{
	try
  	{    	
		//Detect stb	    
		if (!m_stb.DetectSTB()) { //If unknown then return.
			LogError("STB Detection failed!");
			return false; //Stop enigmalight
		}
		else
		{      
	        if(m_grabber->m_debug){
	            Log("DBG -> settings: chr_luma_stride %x", m_stb.chr_luma_stride);
	            Log("DBG -> settings: chr_luma_register_offset %x", m_stb.chr_luma_register_offset);
	            Log("DBG -> settings: registeroffset %x", m_stb.registeroffset);
	            Log("DBG -> settings: mem2memdma_register %x", m_stb.mem2memdma_register);
	        }
	        
	        Log("Open memory /dev/mem");                        
			mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
			if (mem_fd < 0) {
			    LogError("Can't open memory....");
				return false;
			}			
		}

		if(m_grabber->m_3d_mode != 1)
	    	Log("3D mode: %i",m_grabber->m_3d_mode);		
		if (m_grabber->m_debug) 
			Log("Debug mode: enabled");          
	    	    
		// Set some vars to default values
		m_errorGiven = false;
		m_fps=0;

		if(m_grabber->m_debug)
		{
		    //Set fps counters
		    fps_lastupdate		= GetTimeUs();
		    fps_framecount		= 0;
		    m_lastupdate		= GetTimeSec<long double>();
		    m_lastmeasurement	= m_lastupdate;
		    m_measurements 		= 0.0;
		    m_nrmeasurements 	= 0.0;
		}

		return true; // All ok? then return true and start Run();
  	}
  	catch (string error)
  	{
    	PrintError(error);
    	return false;
  	}  
}

bool CFrameGrabber::grabFrame(CBitmap* bitmap, int skiplines)
{
	m_noVideo = false;

    int stride = 0;

    unsigned char* memory_tmp;
    				
	//grab pic from decoder memory
	const unsigned char* data = (unsigned char*)mmap(0, 100, PROT_READ, MAP_SHARED, mem_fd, m_stb.registeroffset);
   
    if(data == MAP_FAILED){
	  if(m_errorGiven != true)
        LogError("Mainmemory data: <Memmapping failed>");
	  return false;
	}

    unsigned int adr,adr2,ofs,ofs2,offset,pageoffset,counter=0;
    
    // Wait till we get a sync from the videodecoder.
    while (1) {
        unsigned int val = ((volatile unsigned int*)data)[0x30/4];
        if (val & 1){
            nice(0);
            break;
        }        

        usleep(1000);
        counter++;
        
        if(counter > 50)
            break;
    }    

    //
    // Get data from decoder, offset, adres and stride(x resolution)
    //
	ofs 	= data[m_stb.chr_luma_register_offset + 8] << 4;      /* luma lines */
	ofs2 	= data[m_stb.chr_luma_register_offset + 12] << 4;    /* chroma lines */	
	adr 	= (data[0x1f] << 24 | data[0x1e] << 16 | data[0x1d] << 8); /* start of videomem */
	adr2 	= (data[m_stb.chr_luma_register_offset + 3] << 24 | data[m_stb.chr_luma_register_offset + 2] << 16 | data[m_stb.chr_luma_register_offset + 1] << 8);	
	stride 	= data[0x15] << 8 | data[0x14];
	
	//
	// Get actual resolution and save it.
	//
	getResolution(bitmap, stride, GetTimeSec<long double>());	
    
    int xres_orig = bitmap->GetXresOrig();
    int yres_orig = bitmap->GetYresOrig();

    //
	// Set offsets and adres
	//
	offset 		= adr2-adr;
    pageoffset 	= adr & 0xfff;
    adr 		-= pageoffset;
    adr2 		-= pageoffset;
	
	//
	// Unmap memory
	//
	munmap((void*)data, 100);

	//
    // Check that obtained values are sane and prevent segfaults.
    //
    if (!adr || !adr2 || (adr2 <= adr) || yres_orig <= 0 || xres_orig <= 0)
    {        
        // we need this m_errorGiven bool, others we get a loop of 1000 errors in some seconds.
        if(m_errorGiven != true){
            if(m_grabber->m_debug)
                LogError("Got invalid memory offsets, retry... (adr=0x%x,adr2=0x%x)", adr, adr2);             
            m_errorGiven = true;
        }

        // Reset orginal resolution
        bitmap->SetXresOrig(0);
        bitmap->SetYresOrig(0);
        
        m_noVideo = true;
        
        return false;
	}			
	else if (stride < bitmap->GetXresOrig()/2)
	{	    
	    if(m_errorGiven != true){
	        if(m_grabber->m_debug)
                LogError("X-Resolution != stride: %d",stride);
            m_errorGiven = true;
        }
		m_noVideo = true;
		return false;
	}
	 
	int memory_tmp_size = 0;
	
	//
	// set original resolution from stride
	//
	xres_orig = stride;
    
    //
    // Check wich resolution is higher
    //
    int skipres = yres_orig;
    if(xres_orig > yres_orig)
        skipres = xres_orig;
    
    //
    // Calculate skiplines (power of 2)
    //
    while(skipres/skiplines > 128){
        skiplines *= 2;
    }
 	
 	//
 	// Get frame from decoder
 	//
	if (!m_stb.mem2memdma_register)
	{ 	    
		// on dm800/dm500hd we have direct access to the decoder memory
		memory_tmp_size = offset + (stride + m_stb.chr_luma_stride) * ofs2;

		memory_tmp = (unsigned char*)mmap(0, memory_tmp_size, PROT_READ, MAP_SHARED, mem_fd, adr);
        
		if (memory_tmp == MAP_FAILED || memory_tmp == NULL) {
		    
		    if(m_errorGiven != true){
		        LogError("Mainmemory: <Memmapping failed>");
		        m_errorGiven = true;
		    }
			m_noVideo = true;return false;
		}

	}
	else
	{
        int tmp_size  = offset + (stride + m_stb.chr_luma_stride) * ofs2;
        
		if (tmp_size > 2 * DMA_BLOCKSIZE)
		{
		    if(m_errorGiven != true){
                LogError("Got invalid stride value from the decoder: %d", stride);
			    m_errorGiven = true;
			} 
			m_noVideo=true;return false;
		}
		
		memory_tmp_size = DMA_BLOCKSIZE + 0x1000;
		
		memory_tmp = (unsigned char*)mmap(0, DMA_BLOCKSIZE + 0x1000, PROT_READ|PROT_WRITE, MAP_SHARED, mem_fd, SPARE_RAM);
		volatile unsigned long *mem_dma;
		
		if(!(mem_dma = (volatile unsigned long*)mmap(0, 0x1000, PROT_READ|PROT_WRITE, MAP_SHARED, mem_fd, m_stb.mem2memdma_register)))
		{
		    if(m_errorGiven != true){
                LogError("Mainmemory: <Memmapping failed>");
                m_errorGiven = true;
            }    
			m_noVideo=true;return false;
		}

		int i = 0;
		int tmp_len = DMA_BLOCKSIZE;
		
		for (i=0; i < tmp_size; i += DMA_BLOCKSIZE)
		{
			unsigned long *descriptor = (unsigned long*)memory_tmp;

			if (i + DMA_BLOCKSIZE > tmp_size)
				tmp_len = tmp_size - i;
			
	        if(m_grabber->m_grabinfo)
    			Log("GrabInfo -> DMACopy: %x (%d) size: %d\n", adr+i, i, tmp_len);
			
			descriptor[0] = /* READ */ adr + i;
			descriptor[1] = /* WRITE */ SPARE_RAM + 0x1000;
			descriptor[2] = 0x40000000 | /* LEN */ tmp_len;
			//descriptor[3] = 0;
			descriptor[3] = 2;
			descriptor[4] = 0;
			descriptor[5] = 0;
			descriptor[6] = 0;
			descriptor[7] = 0;
			mem_dma[1] = /* FIRST_DESCRIPTOR */ SPARE_RAM;
			mem_dma[3] = /* DMA WAKE CTRL */ 3;
			mem_dma[2] = 1;
			while (mem_dma[5] == 1)
				usleep(2);
			mem_dma[2] = 0;
		}
	    
		munmap((void *)mem_dma, 0x1000);
		
		/* unmap the dma descriptor page, we won't need it anymore */
		munmap((void *)memory_tmp, 0x1000);
		/* adjust start and size of the remaining memory_tmp mmap */
		memory_tmp += 0x1000;
		memory_tmp_size -= 0x1000;
	}

	//
	// Extra debug info
	//
	if(m_grabber->m_grabinfo)
    printf("\nGrabInfo -> X-ResOrig: %i Y-ResOrig: %i FPS:%2.1f Adr: %X Adr2: %X OFS,OFS2: %d %d = %d C-offset:%d\n",xres_orig, yres_orig, m_fps, adr, adr2, ofs, ofs2, ofs+ofs2, offset);
    
    
	//
	// decode luma & chroma plane or lets say sort it
	//
	unsigned int x,y,luna_mem_pos = 0, chroma_mem_pos = 0, dat1 = 0;         
    
    int blocksize   = m_stb.chr_luma_stride;
    int skip        = (m_stb.chr_luma_stride)*skiplines; // Skip mem position
	int skipx		= skiplines;
	
	//
	// Fix for some strange resolution, from Oktay
	//
	if((stride/2)%2==1)
		stride-=2;

	for (x = 0; x < stride; x += m_stb.chr_luma_stride)
    {
        // check if we can still copy a complete block.
        if ((stride - x) <= m_stb.chr_luma_stride)
            blocksize = stride-x;

        dat1 = x;    // 1088    16 (68 x)
        for (y = 0; y < ofs; y+=skiplines)
        {
            int z1=0;
            int skipofs=0;
            for(int y1=0;y1<blocksize;y1+=skipx)
            {
                *(bitmap->m_luma + (dat1/skipx)+(y1/skipx))=*(y1+memory_tmp + pageoffset + luna_mem_pos);

                if (y < ofs2 && z1%2==0)
                {
                    skipofs=1;
                    bitmap->m_chroma[(dat1/skipx)+(y1/skipx)]=*(y1+memory_tmp + pageoffset + offset + chroma_mem_pos);
                    bitmap->m_chroma[(dat1/skipx)+(y1/skipx)+1]=*(1+y1+memory_tmp + pageoffset + offset + chroma_mem_pos);     
                }
                z1++;
            }

            if(skipofs==1)
                chroma_mem_pos += skip;
                
            skipofs=0;
            dat1 += stride;
            luna_mem_pos += skip;
                      
        }

        //Skipping invisble lines
        if ( (xres_orig == 1280 && yres_orig == 1080) ) luna_mem_pos += (ofs - yres_orig) * m_stb.chr_luma_stride;
    }

	if (yres_orig%2 == 1)
		yres_orig--;	// drop one line to make the numer even again
    
    //
    // Convert YUV toRGB
    //
	bitmap->YUV2RGB();

	//
    // Set new scaled resolution
    //
    bitmap->SetYres(yres_orig/skiplines);
    bitmap->SetXres(xres_orig/skiplines);

    //
    // Store orginal resolution
    //
	bitmap->SetYresOrig(yres_orig);
    bitmap->SetXresOrig(xres_orig);

	// un-map memory
	munmap(memory_tmp, memory_tmp_size);   

	return true;
}

void CFrameGrabber::getResolution(CBitmap* bitmap, int stride, long double now)
{
    ///Check for resolution every 10 seconds or if xres/yres is not ok    
    if (now - m_last_res_process >= 10.0 || m_last_res_process <= 0.0 || stride != xres_tmp || yres_tmp <= 0 || xres_tmp <= 0){
        m_last_res_process = now;
        
	    // get resolutions from the proc filesystem and save it to tmpvar
	    yres_tmp = hexFromFile("/proc/stb/vmpeg/0/yres");
	    xres_tmp = hexFromFile("/proc/stb/vmpeg/0/xres");
    }
    
    // Save orginal resolution
    bitmap->SetXresOrig(xres_tmp);
    bitmap->SetYresOrig(yres_tmp);
}

void CFrameGrabber::sendBlank(CBitmap* bitmap)
{
	int xres = bitmap->GetXres();
	int yres = bitmap->GetYres();

    // Set black
    m_stateBlank = true;

    // Set new bitmap size
    bitmap->SetData((unsigned char*)malloc(xres*yres*4), xres, yres);
    
    m_grabber->m_enigmalight->ProcessImage(&bitmap->m_data[0], xres, yres, m_grabber->m_delay);  //send bitmap, there it will filter al the values  
    if (!m_grabber->SendRGB(1, NULL,m_grabber->m_cluster))
        PrintError(m_grabber->m_enigmalight->GetError());
    
    yres_tmp=xres_tmp=0;
    
    if(m_grabber->m_debug)
        Log("Nothing to grab, Lights off");
        
}

bool CFrameGrabber::CheckRes(CBitmap* bitmap)
{	
	// Scaled resolution
	int xres = bitmap->GetXres();
	int yres = bitmap->GetYres();

	// Old saved resolution
	int yres_old = bitmap->GetYresOld();
	int xres_old = bitmap->GetXresOld();
	
	// Orginal resolution
	int xres_orig = bitmap->GetXresOrig();
	int yres_orig = bitmap->GetYresOrig();

	if  (m_old_3d_mode != m_grabber->m_3d_mode || (yres_old != yres) || (xres_old != xres) 
    	|| yres <= 1 || yres >= yres_orig/2 || xres <= 1 || xres >= xres_orig/2) 
    {  
        m_noVideo = true;
        if(m_old_3d_mode != m_grabber->m_3d_mode || xres > 2 && yres > 2)
        {   
            bitmap->SetYresOld(yres); bitmap->SetXresOld(xres);

            if(xres != xres_orig && yres != yres_orig && yres_orig > 0 && xres_orig > 0)
    		{
    			//
    			// Set new scanrange
    			//
			    if(m_grabber->m_3d_mode == 1)
			    {
			        m_grabber->m_enigmalight->SetScanRange(xres, yres); //normal
			        Log("Set Scanrange to %dx%d (Source %dx%d)",xres,yres,xres_orig,yres_orig);
			    }
			    else if(m_grabber->m_3d_mode == 2)
			    {
			        m_grabber->m_enigmalight->SetScanRange(xres, yres/2); //topandbottom
			        Log("Set Scanrange to %dx%d (Source %dx%d)",xres,yres/2,xres_orig,yres_orig/2);
			        Log("3D Mode: TAB");        
			    }
			    else if(m_grabber->m_3d_mode == 3)
			    {
			        m_grabber->m_enigmalight->SetScanRange(xres/2, yres); //sidebyside
			        Log("Set Scanrange to %dx%d (Source %dx%d)",xres/2,yres,xres_orig/2,yres_orig);
			        Log("3D Mode: SBS");
			    }    
    

    			//Saves the 3dmode to check every loop for changes
    			m_old_3d_mode = m_grabber->m_3d_mode;
    			
	            // Remove old bitmap and malloc a newone
	        	bitmap->SetData((unsigned char*)malloc(bitmap->GetXres()*bitmap->GetYres()*4), xres, yres);
	     	}       
        }
    }

    //
    // If there is no video or xres,yres are 1 or lower then send blankFrame
    //
    if(m_noVideo || yres <= 1 || xres <= 1){
        
        //If set_black is false then send once black to lights
        if(!m_stateBlank)
        {
        	sendBlank(bitmap);
        }
        
        #define SLEEPTIME 100000
		
		USleep(SLEEPTIME, &m_noVideo);

        return true; // Video is blank
    }
    else{
      
        // Set state m_noVideo to false
        m_stateBlank = false;

        // Set to false so we can receive new errors.
        m_errorGiven = false; 		    	
    }

    return false; // Video is not blank
}

void CFrameGrabber::updateInfo(CBitmap* bitmap, CGuiServer& g_guiserver)
{
	long double now = GetTimeSec<long double>(); 		// current timestamp
	m_measurements += now - m_lastmeasurement;			// diff between last time we were here
	m_nrmeasurements++;									// got another measurement
	m_lastmeasurement = now;							// save the timestamp
	
	if (now - m_lastupdate >= 1.0)						// if we've measured for one second, place fps on ouput.
	{
		m_lastupdate = now;

		if (m_nrmeasurements > 0) 
			m_fps = 1.0 / (m_measurements / m_nrmeasurements); // we need at least one measurement
		
		m_measurements = 0.0;
		m_nrmeasurements = 0;

		g_guiserver.SetInfo(m_fps,bitmap->GetXres(),bitmap->GetYres(),bitmap->GetXresOrig(),bitmap->GetYresOrig());
		
		if(m_grabber->m_debug)
		{                
		    if(!m_noVideo){
		         Log("DBG -> gFPS:%2.1f | Res:%dx%d (%dx%d)",m_fps,bitmap->GetXres(),bitmap->GetYres(),bitmap->GetXresOrig(),bitmap->GetYresOrig());
		    }else{
		         Log("DBG -> gFPS:%2.1f | No video input...",m_fps);		             
		    }
		}
	}
}