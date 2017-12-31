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
#include "StbDetection/StbDetection.h"

CStb::CStb()
{
	//Default Values
	stb_type = UNKNOWN;

	chr_luma_stride				= 0x40;
	chr_luma_register_offset 	= 0;
	registeroffset				= 0;
	mem2memdma_register			= 0;
}

CStb::~CStb()
{

}

bool CStb::DetectSTB()
{

	Log("Detect STB-Type...");

	// detect STB
	char buf[256];
	FILE *pipe = fopen("/proc/fb","r");
	if (!pipe)
	{
		Log("No framebuffer, unknown STB .. quit.");
		return false;
	}
	stb_type = UNKNOWN;

	if (stb_type == UNKNOWN)
	{
		FILE *file = fopen("/tmp/chipset", "r");
		if (file)
		{
			char buf[32];
			while (fgets(buf, sizeof(buf), file))
			{
				if (strstr(buf,"TEST1"))
				{
					stb_type = TEST1;
					break;
				}
				else if (strstr(buf,"TEST2"))
				{
					stb_type = TEST2;
					break;
				}
				else if (strstr(buf,"TEST3"))
				{
					stb_type = TEST3;
					break;
				}
				else if (strstr(buf,"TEST4"))
				{
					stb_type = TEST4;
					break;
				}
				else if (strstr(buf,"TEST5"))
				{
					stb_type = TEST5;
					break;
				}
				else if (strstr(buf,"TEST6"))
				{
					stb_type = TEST6;
					break;
				}
				else if (strstr(buf,"TEST7"))
				{
					stb_type = TEST7;
					break;
				}
				else if (strstr(buf,"TEST8"))
				{
					stb_type = TEST8;
					break;
				}
			}
			fclose(file);
		}
	}

	if (stb_type == UNKNOWN)
	{
		FILE *file = fopen("/proc/stb/info/chipset", "r");
		if (file)
		{
			char buf[32];
			while (fgets(buf, sizeof(buf), file))
			{
				if (strstr(buf,"7400"))
				{
					stb_type = BRCM7400;
					break;
				}
				else if (strstr(buf,"7401"))
				{
					stb_type = BRCM7401;
					break;
				}
				else if (strstr(buf,"7403"))
				{
					stb_type = BRCM7401;
					break;
				}
				else if (strstr(buf,"7405"))
				{
					stb_type = BRCM7405;
					break;
				}
				else if (strstr(buf,"7413"))
				{
					stb_type = BRCM7405;
					break;
				}
				else if (strstr(buf,"7335"))
				{
					stb_type = BRCM7335;
					break;
				}
				else if (strstr(buf,"7325"))
				{
					stb_type = BRCM7325;
					break;
				}
				else if (strstr(buf,"7358"))
				{
					stb_type = BRCM7358;
					break;
				}
				else if (strstr(buf,"7241"))
				{
					stb_type = BRCM7241;
					break;
				}
				else if (strstr(buf,"7346"))
 				{
 					stb_type = BRCM7346;
 					break;
 				}
				else if (strstr(buf,"73565"))
				{
					stb_type = BRCM73565;
					break;
				}
				else if (strstr(buf,"7356"))
				{
					stb_type = BRCM7356;
					break;
				}
				else if (strstr(buf,"73625"))
				{
					stb_type = BRCM73625;
					break;
				}
				else if (strstr(buf,"7362"))
				{
					stb_type = BRCM7362;
					break;
				}
				else if (strstr(buf,"7424"))
				{
					stb_type = BRCM7424;
					break;
				}
				else if (strstr(buf,"7425"))
				{
					stb_type = BRCM7425;
					break;
				}
				else if (strstr(buf,"7435"))
				{
					stb_type = BRCM7435;
					break;
				}
				else if (strstr(buf,"7376"))
				{
					stb_type = BRCM7376;
					break;
				}
				else if (strstr(buf,"7251"))
				{
					stb_type = BRCM7251;
					break;
				}
				else if (strstr(buf,"7252"))
				{
					stb_type = BRCM7252;
					break;
				}
				else if (strstr(buf,"7444"))
				{
					stb_type = BRCM7444;
					break;
				}
			}
			fclose(file);
		}
	}

	if (stb_type == UNKNOWN)
	{
		FILE *file = fopen("/proc/stb/info/model", "r");
		if (file)
		{
			char buf[32];
			while (fgets(buf, sizeof(buf), file))
			{
				if (strcasestr(buf,"DM500HD") || strcasestr(buf,"DM800SE") || strcasestr(buf,"DM7020HD"))
				{
					stb_type = BRCM7405;
					break;
				}
				else if (strcasestr(buf,"DM8000"))
				{
					stb_type = BRCM7400;
					break;
				}
				else if (strcasestr(buf,"DM7080") || strcasestr(buf,"DM820"))
				{
					stb_type = BRCM7435;
					break;
				}
				else if (strcasestr(buf,"DM800"))
				{
					stb_type = BRCM7401;
					break;
				}
				// Dreambox 900/920 ARM
				else if (strcasestr(buf,"DM900") || strcasestr(buf,"DM920"))
				{
					stb_type = BRCM7251;
					break;
				}
				// AX 4K HD51
				else if (strcasestr(buf,"hd51"))
				{
					stb_type = BRCM7251;
					break;
				}
				else if (strcasestr(buf, "DM520") || strcasestr(buf,"DM525"))
				{
					stb_type = BRCM73625;
					break;
				}
				else if (strcasestr(buf,"Gigablue"))
				{
					stb_type = BRCM7335;
					break;
				}
			}
			fclose(file);
		}
	}
	

	if (stb_type == UNKNOWN) {
		return false;
	}

	switch (stb_type)
	{
		case TEST1:
			registeroffset = 0xf0600000;
			chr_luma_stride = 0;
			chr_luma_register_offset = 0x3C;
			mem2memdma_register = 0;
			break;
		case TEST2:
			registeroffset = 0xf0600000;
			chr_luma_stride = 0x20;
			chr_luma_register_offset = 0x3C;
			mem2memdma_register = 0;
			break;
		case TEST3:
			registeroffset = 0xf0600000;
			chr_luma_stride = 0x40;
			chr_luma_register_offset = 0x3C;
			mem2memdma_register = 0;
			break;		
		case TEST4:
			registeroffset = 0xf0600000;
			chr_luma_stride = 0x60;
			chr_luma_register_offset = 0x3C;
			mem2memdma_register = 0;
			break;
		case TEST5:
			registeroffset = 0xf0600000;
			chr_luma_stride = 0x80;
			chr_luma_register_offset = 0x3C;
			mem2memdma_register = 0;
			break;
		case TEST6:
			registeroffset = 0xf0600000;
			chr_luma_stride = 0x120;
			chr_luma_register_offset = 0x3C;
			mem2memdma_register = 0;
			break;
		case TEST7:
			registeroffset = 0xf0600000;
			chr_luma_stride = 0x160;
			chr_luma_register_offset = 0x3C;
			mem2memdma_register = 0;
			break;
		case TEST8:
			registeroffset = 0xf0600000;
			chr_luma_stride = 0x400;
			chr_luma_register_offset = 0x3C;
			mem2memdma_register = 0;
			break;
		case BRCM7400:
			registeroffset = 0x10100000;
			chr_luma_stride = 0x40;
			chr_luma_register_offset = 0x20;
			mem2memdma_register = 0x10c02000;
			break;
		case BRCM7401:
			registeroffset = 0x10100000;
			chr_luma_stride = 0x40;
			chr_luma_register_offset = 0x20;
			mem2memdma_register = 0;
			break;
		case BRCM7405:
			registeroffset = 0x10100000;
			chr_luma_stride = 0x80;
			chr_luma_register_offset = 0x20;
			mem2memdma_register = 0;
			break;
		case BRCM7325:
			registeroffset = 0x10100000;
			chr_luma_stride = 0x80;
			chr_luma_register_offset = 0x20;
			mem2memdma_register = 0;
			break;
		case BRCM7335:
			registeroffset = 0x10100000;
			chr_luma_stride = 0x40;
			chr_luma_register_offset = 0x20;
			mem2memdma_register = 0x10c01000;
			break;
		case BRCM7358:
			registeroffset = 0x10600000;
			chr_luma_stride = 0x40;
			chr_luma_register_offset = 0x34;
			mem2memdma_register = 0;
			break;
		case BRCM7362:
			registeroffset = 0x10600000;
			chr_luma_stride = 0x40;
			chr_luma_register_offset = 0x34;
			mem2memdma_register = 0;
			break;
		case BRCM7241:
		case BRCM7346:
		case BRCM7356:
		case BRCM7424:
		case BRCM7425:
		case BRCM7435:
			registeroffset = 0x10600000;
			chr_luma_stride = 0x80;
			chr_luma_register_offset = 0x34;
			mem2memdma_register = 0;
			break;
		case BRCM73625:
		case BRCM73565:
			registeroffset = 0x10600000;
			chr_luma_stride = 0x40;
			chr_luma_register_offset = 0x3c;
			mem2memdma_register = 0;
			break;
		case BRCM7376:
		case BRCM7251:
		case BRCM7252:
		case BRCM7444:
			registeroffset = 0xf0600000;
			chr_luma_stride = 0x80;
			chr_luma_register_offset = 0x3c;
			mem2memdma_register = 0;
			break;
		default:
			break;
	}
	
	Log("Detected STB-Type: BCM%d",stb_type);

	return true;
}
