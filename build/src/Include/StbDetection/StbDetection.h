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

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/stat.h>

#include <assert.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include "Util/Log.h"

#ifndef CSTB
#define CSTB

// Supported STB-Types
#define UNKNOWN     0
#define PALLAS      0
#define VULCAN      0
#define XILLEON     0
#define BRCM7325    7325
#define BRCM7335    7335
#define BRCM7346    7346
#define BRCM7356    7356
#define BRCM7358    7358
#define BRCM7400    7400
#define BRCM7401    7401
#define BRCM7403    7403
#define BRCM7405    7405
#define BRCM7424    7424
#define BRCM7425    7425
#define BRCM7435	7435
#define BRCM7241	7241
#define BRCM7362	7362
#define GIGABLUE    0//12

class CStb
{
	public:
		CStb();
		~CStb();

		bool DetectSTB();
		
		int             stb_type;

		int             buffer_size;
        int             chr_luma_stride;
        int             chr_luma_register_offset;
        unsigned int    registeroffset;
        unsigned int    mem2memdma_register;

	private:

};
#endif //CSTB