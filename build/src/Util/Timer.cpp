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

#include "Util/Timer.h"
#include "Util/Misc.h"
#include "Util/TimeUtils.h"

#include <iostream>
using namespace std;

CTimer::CTimer(volatile bool* stop /*=NULL*/)
{
  m_interval = -1;
  m_timerstop = stop;
}

void CTimer::SetInterval(int64_t usecs)
{
  m_interval = usecs;
  Reset();
}

int64_t CTimer::GetInterval()
{
  return m_interval;
}

void CTimer::Reset()
{
  m_time = GetTimeUs();
}

void CTimer::Wait()
{
  int64_t sleeptime;
  int64_t now = GetTimeUs();


  //keep looping until we have a timestamp that's not too old
  do
  {
    m_time += m_interval; //set by grabber-enigma2.cpp and increase in loop
    sleeptime = m_time - now; // total m_time - timenow
  }
  while(sleeptime <= m_interval * -2LL); //if sleeptime lower or smae then m_interval from grabber-enigma2.cpp * - long long
  
  if (sleeptime > m_interval * 2LL) //failsafe, m_time must be bork if we get here
  {
    sleeptime = m_interval * 2LL;
    Reset();
  }

  USleep(sleeptime, m_timerstop);
}

