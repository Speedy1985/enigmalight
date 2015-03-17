/*
 * EnigmaLight (c) 2014 Speedy1985, Oktay Oeztueter (Based on Boblight from Bob Loosen)
 * parts of this code were taken from
 *
 * - aiograb        (http://schwerkraft.elitedvb.net/projects/aio-grab/)
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


#ifndef CBLACKBAR
#define CBLACKBAR

#include <string>
#include <sys/resource.h>

#include "Config.h"
#include "Util/Bitmap.h"

typedef struct { 
  int Y;
  int X;
  int Height;
  int Width;

} Bounds;

class CBlackbarDetection
{

    public:
        CBlackbarDetection(CBitmap* bitmapObject);

        Bounds FindBounds(bool debug, bool picdump);
        void ScanLine(int line, int start, int end, bool horizontal);
        void ResetHistograms();
        bool IsContent(int start, int end);
        void DrawLine(int line, int start, int end, int color, bool horizontal);
        
        int m_blackCounter_h;
        int m_blackCounter_v;
        
    private:        

        int Bitmap_xres;
        int Bitmap_yres;

        int topStart;
        int topEnd;
        int bottomStart;
        int bottomEnd;

        int leftStart;
        int leftEnd;
        int rightStart;
        int rightEnd;

        int maxBrightnessTreshold;
        int minBrightnessTreshold;

        double topScanStartFraction;
        double topScanEndFraction;
        double bottomScanEndFraction;
        double bottomScanStartFraction;

        double leftScanStartFraction;
        double leftScanEndFraction;
        double rightScanStartFraction;
        double rightScanEndFraction;

        bool m_debug;

        unsigned char* imageFrame;

        int histR[256];
        int histG[256];
        int histB[256];        

        CBitmap* bitmapInstance;

};

#endif //CBLACKBAR