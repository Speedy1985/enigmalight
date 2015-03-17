/*
 * EnigmaLight (c) 2014 Speedy1985, Oktay Oeztueter (Based on Boblight from Bob Loosen)
 * parts of this code were taken from
 *
 * - aiograb		(http://schwerkraft.elitedvb.net/projects/aio-grab/)
 * - Boblight (c) 2009 Bob Loosen
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

#include <iostream>
#include <time.h>
#include <assert.h> 
#include <stdio.h>
#include <stdlib.h>

#include "Util/Bitmap.h"
#include "Util/Misc.h"
#include "Util/Log.h"

/*
//Bitmap library
Author: Arash Partow - 2002                                             *
URL: http://partow.net/programming/bitmap/index.html
*/
#include "Util/Bitmap_Image.hpp"

using namespace std;

//Constructor
CBitmap::CBitmap(unsigned char* data, int xres=0, int yres=0)
{
    //Counter for saving images
    filename_count = 0;

    m_xres   = xres;
    m_yres   = yres;

    m_luma     = (unsigned char*)malloc(1920*300*3);
    m_chroma   = (unsigned char*)malloc(1920*300*3/2);

    m_data   = data;
    
    memset(m_data,0,m_yres*m_yres*4);    

    m_xres_old = 0;
    m_yres_old = 0;
}

CBitmap::~CBitmap()
{
  Log("[Bitmap] Destroy bitmaps..");

  // free all memory
  if (m_data && m_data != NULL)
    free(m_data);
  if (m_luma and m_luma != NULL)
    free(m_luma);
  if(m_chroma and m_chroma != NULL)
    free(m_chroma);
}

void CBitmap::SetData(unsigned char* data, int xres, int yres)
{
  //If m_data exists remove it
  if (m_data != NULL)
  {    
    free(m_data);
  }

  m_xres   = xres;
  m_yres   = yres;

  m_data = data;
  memset(m_data,0,xres*yres*4);
}

bool CBitmap::YUV2RGB()
{
  ///////////////////////////////////////////////////////////////////
  //
  //          Covert YUV to RGB image
  //
  ///////////////////////////////////////////////////////////////////

  int  posb, x, y;
  long pos_chr, pos_luma, pos_rgb, rgbskip; // relative position in chroma- and luma-map
  int  Y, U, V, RU, GU, GV, BV;             // YUV-Coefficients
  int  U2, V2, RU2, GU2, GV2, BV2;          // YUV-Coefficients
  
  // yuv2rgb conversion (4:2:0)
  rgbskip = m_xres * 3;
  
  pos_rgb = 0;

  for (y=0; y < m_yres; y+=2)
  {     
    for (x=0; x < m_xres; x+=2)
    {
      pos_luma = x + (y * m_xres);
      pos_chr  = x + (y * m_xres / 2);
      
      // chroma contains both U and V data
      
      U2=m_chroma[pos_chr+1]; //2
      V2=m_chroma[pos_chr+0]; //3 litte->big endian :)
    
      RU2=yuv2rgbtable_ru[V2]; 
      GU2=yuv2rgbtable_gu[U2];
      GV2=yuv2rgbtable_gv[V2];
      BV2=yuv2rgbtable_bv[U2];
    
      // now we do 4*2 pixels on each iteration this is more code but much faster 
      Y=yuv2rgbtable_y[m_luma[pos_luma]]; 
      m_data[pos_rgb+0]=CLAMP((Y + RU2)>>16);
      m_data[pos_rgb+1]=CLAMP((Y - GV2 - GU2)>>16);
      m_data[pos_rgb+2]=CLAMP((Y + BV2)>>16);
      
      Y=yuv2rgbtable_y[m_luma[m_xres+pos_luma]];
      m_data[pos_rgb+0+rgbskip]=CLAMP((Y + RU2)>>16);
      m_data[pos_rgb+1+rgbskip]=CLAMP((Y - GV2 - GU2)>>16);
      m_data[pos_rgb+2+rgbskip]=CLAMP((Y + BV2)>>16);
            
      pos_rgb  +=3; 

      Y=yuv2rgbtable_y[m_luma[pos_luma+1]];
      m_data[pos_rgb+0]=CLAMP((Y + RU2)>>16);
      m_data[pos_rgb+1]=CLAMP((Y - GV2 - GU2)>>16);
      m_data[pos_rgb+2]=CLAMP((Y + BV2)>>16);

      Y=yuv2rgbtable_y[m_luma[m_xres+pos_luma+1]];
      m_data[pos_rgb+0+rgbskip]=CLAMP((Y + RU2)>>16);
      m_data[pos_rgb+1+rgbskip]=CLAMP((Y - GV2 - GU2)>>16);
      m_data[pos_rgb+2+rgbskip]=CLAMP((Y + BV2)>>16);

      pos_rgb  +=3; // skip forward for the next group of 4 pixels
    }
    pos_rgb+=rgbskip; // skip a complete line
  }

  return true;
}

void CBitmap::SaveImage()
{
  //New bitmapimage
  bitmap_image image(m_xres, m_yres, m_data);

  //Bgr values to rgb
  image.bgr_to_rgb();

  //Set filename
  char filename [50]; // stores the filename
  sprintf (filename, "/tmp/enigmalight_%04d.bmp", filename_count++);

  Log("Bitmap saved to %s (%dx%d)",filename, m_xres, m_yres);   

  image.save_image(filename);
}

Color CBitmap::GetPixel(int x, int y)
{
  int offset = (y*m_xres+x)*3;
        
  Color c;

  c.R = m_data[offset+0];
  c.G = m_data[offset+1];
  c.B = m_data[offset+2];

  //cout << "GetPixel >> R:" << c.R << " G:" << c.G << " B:" << c.B << "\n";
  
  return c;
}

void CBitmap::SetPixel(int x, int y, int color)
{
  int offset = (y*m_xres+x)*3;
  //cout << "color hex " << color << "\n";
  //cout << "SetPixel @ X:"<< x << "Y:"<< y << " R:" << color / 0x10000 << " G:" << (color / 0x100) % 0x100 << " B:" << color % 0x10000 << "\n";
  m_data[offset+0] = Clamp(color / 0x10000,0,255);
  m_data[offset+1] = Clamp((color / 0x100) % 0x100,0,255);
  m_data[offset+2] = Clamp(color % 0x10000,0,255);  
}