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



#include <iostream>
#include <float.h>
#include <assert.h>
#include <stdlib.h>
#include <stdarg.h>
#include <iostream>
 
#include "Util/ColorTransform.h"

float* SwapRGB(int color_sequence, float* rgb)
{
	//Swap the colors to given sequence
	float save;
	
	switch (color_sequence)
	{
		case 0: //RGB   
			return rgb; //return, because grabbed images are default in rgb color.
		case 1: //BGR
			save   = rgb[0];
			rgb[0] = rgb[2];
			rgb[1] = rgb[1];
			rgb[2] = save;
		case 2: //GBR
			save   = rgb[0];
			rgb[0] = rgb[1];
			rgb[1] = rgb[2];
			rgb[2] = save;     
		case 3: //GRB
			save   = rgb[0];
			rgb[0] = rgb[1];
			rgb[1] = save;
		case 4: //BRG
			save   = rgb[1];
			rgb[0] = rgb[2];
			rgb[1] = rgb[0];
			rgb[2] = save;
		case 5: //RBG
			save   = rgb[1];
			rgb[1] = rgb[2];
			rgb[2] = save;
		default: 
			break;
	}
}