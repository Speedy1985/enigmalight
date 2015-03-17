#include <iostream>
#include <float.h>
#include <assert.h>
#include <stdlib.h>
#include <stdarg.h>
#include <iostream>

#include "Util/Misc.h"
#include "Lights/Light.h"

using namespace std;

CColor::CColor()
{
  memset(m_rgb, 0, sizeof(m_rgb));
  
  // Default values for r,g,b
  m_gamma = 1.0;
  m_adjust = 1.0; 
  m_blacklevel = 0.0;
}

void CColor::SetAdjust(float adjust)
{
    //printf("Test - SetAdjust: %f\n",adjust); 
    m_adjust = adjust;
}