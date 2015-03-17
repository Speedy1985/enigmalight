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

#ifndef CLOCK
#define CLOCK

#include "Mutex.h"
#include "Condition.h"

class CLock
{
  public:
  CLock(CMutex& mutex) : m_mutex(mutex)
  {
    m_haslock = false;
    Enter();
  }

  ~CLock()
  {
    Leave();
  }

  void Enter()
  {
    if (!m_haslock)
    {
      m_mutex.Lock();
      m_haslock = true;
    }
  }

  void Leave()
  {
    if (m_haslock)
    {
      m_mutex.Unlock();
      m_haslock = false;
    }
  }

  private:
    CMutex& m_mutex;
    bool    m_haslock;
};

#endif //CLOCK