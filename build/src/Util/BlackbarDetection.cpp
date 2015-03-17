/*
 * EnigmaLight (c) 2014 Speedy1985, Oktay Oeztueter (Based on Boblight from Bob Loosen)
 * parts of this code were taken from
 *
 * - aiograb    (http://schwerkraft.elitedvb.net/projects/aio-grab/)
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

  /// <summary>
  /// The FrameAnalyzer class provides functionality to decide
  /// the bounding box of a given Bitmap object containing
  /// letterboxed video material.
  /// </summary>

#include "Util/BlackbarDetection.h"

CBlackbarDetection::CBlackbarDetection(CBitmap* bitmapObject)
{

	//Set instance
	bitmapInstance = bitmapObject;

	/*topScanStartFraction    = (double)(100-0)/200.0; //??
	topScanEndFraction      = 1.0 - topScanStartFraction;
	bottomScanStartFraction = topScanStartFraction;
	bottomScanEndFraction   = topScanEndFraction;

	leftScanStartFraction   = (double)(100-0)/200.0; // ??
	leftScanEndFraction     = 1.0 - topScanStartFraction;                                             
	rightScanStartFraction  = leftScanStartFraction;
	rightScanEndFraction    = leftScanEndFraction;*/

	topStart = 0;
	topEnd = 0;
	bottomStart = 0;
	bottomEnd = 0;

	leftStart = 0;
	leftEnd = 0;
	rightStart = 0;
	rightEnd = 0;

	maxBrightnessTreshold = 15;
	minBrightnessTreshold = 5;

	topScanStartFraction = 0.3;
	topScanEndFraction = 0.3;
	bottomScanEndFraction = 0.3;
	bottomScanStartFraction = 0.3;

	leftScanStartFraction = 0.3;
	leftScanEndFraction = 0.7;
	rightScanStartFraction = 0.3;
	rightScanEndFraction = 0.7;

  m_blackCounter_h = 0;
  m_blackCounter_v = 0;

	m_debug = false;  

}


/// <summary>
/// Find top and bottom bounds of a given bitmap. Performs a top down and bottom down scan
/// to find the first top/bottom line that has content. Whether or not a line is 'content'
/// is decided by the IsContent() method.
/// </summary>
/// <param name="frame"></param>
/// <returns>True if analysis succeeded(ie is trustworthy) and false otherwise</returns>
Bounds CBlackbarDetection::FindBounds(bool debug, bool picdump)
{

  Bitmap_xres = bitmapInstance->GetXres();
  Bitmap_yres = bitmapInstance->GetYres();

  Bounds bounds;

  bounds.Y = 0;
  bounds.X = 0;

  bounds.Height = Bitmap_yres;
  bounds.Width =  Bitmap_xres;

  m_debug = debug;

  if(m_debug)
  {
    Log("DBG -> FindBounds");
  }

  int topLine       = 0;
  int bottomLine    = Bitmap_yres - 1;
  int leftLine      = 0;
  int rightLine     = Bitmap_xres - 1;

  bool foundTop     = false;
  bool foundBottom  = false;
  bool foundLeft    = false;
  bool foundRight   = false;

  topStart = (int)(topScanStartFraction * (double)Bitmap_xres);
  topEnd = (int)(topScanEndFraction * (double)Bitmap_xres);
  if (topEnd >= Bitmap_xres)
  {
    topEnd--;
  }

  bottomStart = (int)(bottomScanStartFraction * (double)Bitmap_xres);
  bottomEnd = (int)(bottomScanEndFraction * (double)Bitmap_xres);
  if (bottomEnd >= Bitmap_xres)
  {
    bottomEnd--;
  }

  leftStart = (int)(leftScanStartFraction * (double)Bitmap_yres);
  leftEnd = (int)(leftScanEndFraction * (double)Bitmap_yres);
  if (leftEnd >= Bitmap_yres)
  {
    leftEnd--;
  }

  rightStart = (int)(rightScanStartFraction * (double)Bitmap_yres);
  rightEnd = (int)(rightScanEndFraction * (double)Bitmap_yres);
  if (rightEnd >= Bitmap_yres)
  {
    rightEnd--;
  }

  if(m_debug)
  {
    Log("DBG ->  FindBounds: Scanning top: %i - %i, bottom: %i - %i, left: %i - %i, right: %i - %i",
              topStart, topEnd,
              bottomStart, bottomEnd, leftStart, leftEnd, rightStart, rightEnd);
  }

  //DrawLine(Bitmap_yres / 2, 0, Bitmap_xres - 1, 0X000099, true);

  //Top black bar binary search scan
  int mid = 1;
  int low = 1;
  int high = (int)((double)Bitmap_yres * 0.25);

  while (low <= high)
  {
    ScanLine(mid, topStart, topEnd, true);
    if (IsContent(topStart, topEnd))
    {
      high = mid - 1;
      topLine = mid;
      foundTop = true;

      if(m_debug)
      {
        Log("DBG ->  FindBounds: Found top line: %i", topLine);
        if(picdump)
          DrawLine(topLine, topStart, topEnd, 0xFF0000, true);
      }
    }
    else
    {
      low = mid + 1;
    }
    mid = (low + high) / 2;
  }
  if (topLine < 1)
  {
    topLine = 1;
  }

  //Left black bar binary search scan
  mid = 1;
  low = 1;
  high = (int)((double)Bitmap_xres * 0.25);

  while (low <= high)
  {
    ScanLine(mid, leftStart, leftEnd, false);
    if (IsContent(leftStart, leftEnd))
    {
      high = mid - 1;
      leftLine = mid;
      foundLeft = true;
      
      if(m_debug)
      {
        Log("DBG ->  FindBounds: Found left line: %i", leftLine);
        if(picdump)
          DrawLine(leftLine, leftStart, leftEnd, 0XFF0000, false);
      }
    }
    else
    {
      low = mid + 1;
    }
    mid = (low + high) / 2;
  }
  if (leftLine < 1)
  {
    leftLine = 1;
  }

  if (!foundLeft && !foundTop)
  {
    
    bounds.Y = 0;
    bounds.X = 0;
    bounds.Height = Bitmap_yres;
    bounds.Width =  Bitmap_xres;
    return bounds;
  }


  //Right black bar binary search scan
  low = (int)((double)Bitmap_xres * 0.75);
  high = Bitmap_xres - 1;
  mid = high;
  while (low <= high)
  {
    ScanLine(mid, rightStart, rightEnd, false);
    if (IsContent(rightStart, rightEnd))
    {
      low = mid + 1;
      rightLine = mid;
      foundRight = true;
      if(m_debug)
      {
        Log("DBG ->  FindBounds: Found right line: %i", rightLine);
        if(picdump)
          DrawLine(rightLine, rightStart, rightEnd, 0xFF0000, false);
      }
    }
    else
    {
      high = mid - 1;
    }
    mid = (low + high) / 2;
  }
  if (rightLine >= Bitmap_xres)
  {
    rightLine = Bitmap_xres - 1;
  }

  if (!foundLeft && !foundRight)
  {

    bounds.Y = 0;
    bounds.X = 0;
    bounds.Height = Bitmap_yres;
    bounds.Width =  Bitmap_xres;
    return bounds;
  }

  //Bottom black bar binary search scan
  low = (int)((double)Bitmap_yres * 0.75);
  high = Bitmap_yres - 1;
  mid = high;
  while (low <= high)
  {
    ScanLine(mid, bottomStart, bottomEnd, true);
    if (IsContent(bottomStart, bottomEnd))
    {
      low = mid + 1;
      bottomLine = mid;
      foundBottom = true;
      
      if(m_debug)
      {
        Log("DBG ->  FindBounds: Found bottom line: %i", bottomLine);
        if(picdump)
          DrawLine(bottomLine, bottomStart, bottomEnd, 0xFF0000, true);
      }
    }
    else
    {
      high = mid - 1;
    }
    mid = (low + high) / 2;
  }
  if (bottomLine >= Bitmap_yres)
  {
    bottomLine = Bitmap_yres - 1;
  }

  if (!foundBottom || (bottomLine - topLine) < (int)((double)Bitmap_yres * 0.25) ||
      (rightLine - leftLine) < (int)((double)Bitmap_xres * 0.25))
  {
    if(m_debug)
    {
      Log("DBG ->  FindBounds: Sanity check failed, analysis failed, returning null to skip frame");
      if(picdump)
        DrawLine(Bitmap_yres / 2, 0, Bitmap_xres - 1, 0XFFCC00, true); // indicate give up
    }
    
    return bounds;
  }

  //DrawLine(topLine, 0, Bitmap_xres - 1, 0xFF0000, true);
  //DrawLine(bottomLine, 0, Bitmap_xres - 1, 0XFFCC00, true);

  bounds.Y = topLine; //start line
  bounds.X = leftLine; //start line
  bounds.Height = bottomLine - topLine; //New height
  bounds.Width = rightLine - leftLine; // New width

  return bounds;
}

/// <summary>
/// Scans a line in the frame, producing R,G and B histograms
/// </summary>
/// <param name="line"> The line to scan</param>
/// <param name="start"> How far into the line to start scan (to avoid logos etc)</param>
/// <param name="end"> How far into the line to stop the scan (to avoid logos etc) </param>
/// <param name="horizontal"> Decides if this is a horizontal line scan (or vertical) </param>
void CBlackbarDetection::ScanLine(int line, int start, int end, bool horizontal)
{

	if(m_debug)
  		Log("DBG ->  Scanning line %i",line);
	
	ResetHistograms();
	
  //Struct
  Color c;

	for (int p = start; p <= end; p++)
	{
	    if (horizontal) //horizontal line scan
	    {
	      c = bitmapInstance->GetPixel(p, line);
	    }
	    else //vertical line scan
	    {
	      c = bitmapInstance->GetPixel(line, p);
	    }

	    histR[0xff & c.R]++;
	    histG[0xff & c.G]++;
	    histB[0xff & c.B]++;
	}
}

/// <summary>
/// Resets the RGB histograms
/// </summary>
void CBlackbarDetection::ResetHistograms()
{
  for (int i = 0; i < 255; i++)
  {
    histR[i] = 0;
    histG[i] = 0;
    histB[i] = 0;
  }
}

/// <summary>
/// Determines if the last line scanned was content or not
/// </summary>
/// <returns></returns>
bool CBlackbarDetection::IsContent(int start, int end)
{
  int maxR = 0;
  int maxG = 0;
  int maxB = 0;
  int sumR = 0;
  int sumG = 0;
  int sumB = 0;

  //Check for brightest pixel value
  for (int i = 0; i < 255; i++)
  {
    if (histR[i] > 0 && i >= maxR)
    {
      maxR = i;
    }
    if (histG[i] > 0 && i >= maxG)
    {
      maxG = i;
    }
    if (histB[i] > 0 && i >= maxB)
    {
      maxB = i;
    }
    if (i >= minBrightnessTreshold)
    {
      sumR = sumR + histR[i];
      sumG = sumG + histG[i];
      sumB = sumB + histB[i];
    }
  }
  //if (ViewModeSwitcher.currentSettings.verboseLog)
  
  if(m_debug)
  	Log("DBG ->  IsContent: Max : R{0}, G{1}, B{2}", maxR, maxG, maxB);

  //At least one pixel with brightness level over 'LBMaxBlackLevel' is found
  if (maxR > maxBrightnessTreshold || maxG > maxBrightnessTreshold || maxB > maxBrightnessTreshold)
  {
    return true;
  }

  //if (ViewModeSwitcher.currentSettings.verboseLog)
  if(m_debug)
  	Log("DBG ->  IsContent: Number of pixel above treshold : R{0}, G{1}, B{2}", sumR, sumG, sumB);

  //Over 25% of the pixels in the line are above the minimum brightness treshold
  if (sumR > ((end - start) / 4) || sumG > ((end - start) / 4) || sumB > ((end - start) / 4))
  {
    return true;
  }

  //No content detected
  return false;
}

void CBlackbarDetection::DrawLine(int line, int start, int end, int color, bool horizontal)
{
  for (int p = start; p <= end; p++)
  {
    if (horizontal) //horizontal line scan
    {
      bitmapInstance->SetPixel(p, line, color);
    }
    else //vertical line scan
    {
      bitmapInstance->SetPixel(line, p, color);
    }
  }
}