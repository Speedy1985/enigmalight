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

#ifndef CBITMAP
#define CBITMAP

#include <unistd.h>
#include <stdio.h>
#include "Util/Misc.h"
#include "Util/Log.h"

//Rgb Tables
#include "Util/RgbTables.h"

#define CLAMP(x)    ((x < 0) ? 0 : ((x > 255) ? 255 : x))
#define SWAP(x,y)	{ x ^= y; y ^= x; x ^= y; }
#define CLIP(x)     ((x < 0) ? 1 : ((x > 250) ? 250 : x))

class CBitmap
{
	public:
        CBitmap(unsigned char* data, int xres, int yres);
         ~CBitmap();

        void 				FreeMemory();
        bool				YUV2RGB();

		unsigned char* 		m_data;
		unsigned char*		m_luma;
		unsigned char*		m_chroma;

		void				SetData(unsigned char* data, int xres, int yres);

		void				SetXres(int xres)						{ m_xres = xres; }
		void				SetYres(int yres)						{ m_yres = yres; }
		void				SetXresOld(int xres_old)				{ m_xres_old = xres_old; }
		void				SetYresOld(int yres_old)				{ m_yres_old = yres_old; }
		void				SetXresOrig(int xres_orig)				{ m_xres_orig = xres_orig; }
		void				SetYresOrig(int yres_orig)				{ m_yres_orig = yres_orig; }
		void				SetResBounds(int xbound, int ybound)	{ m_xres_bounds = xbound; m_yres_bounds = ybound; }

		int					GetXres()								{ return m_xres; }
		int					GetYres()								{ return m_yres; }
		int					GetXresOld()							{ return m_xres_old; }
		int					GetYresOld()							{ return m_yres_old; }
		int					GetXresOrig()							{ return m_xres_orig; }
		int					GetYresOrig()							{ return m_yres_orig; }

		Color				GetPixel(int x, int y);
		void				SetPixel(int x, int y, int color);

		void 				SaveImage();

		                    // save bitmap image as BMP
		int                 filename_count;

	private:

		int					m_xres, m_yres;							// stored scaled resolution
		int             	m_xres_old, m_yres_old; 				// stored to detect resolution changes
		int             	m_xres_orig, m_yres_orig; 				// stored orginal resulution
		int					m_xres_bounds, m_yres_bounds; 			// stored resolution min bounds
};

#endif
