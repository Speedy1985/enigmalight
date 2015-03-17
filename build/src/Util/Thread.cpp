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

#include "Util/Thread.h"

CThread::CThread()
{
  m_thread = 0;
  m_running = false;
}

CThread::~CThread()
{
  StopThread();
}

void CThread::StartThread()
{
  m_stop = false;
  m_running = true;
  pthread_create(&m_thread, 0, ThreadFunction, reinterpret_cast<void*>(this));
}

void* CThread::ThreadFunction(void* args)
{
  CThread* thread = reinterpret_cast<CThread*>(args);
  thread->Process();
  thread->m_running = false;
}

void CThread::Process()
{
}

void CThread::StopThread()
{
  AsyncStopThread();
  JoinThread();
}

void CThread::AsyncStopThread()
{
  m_stop = true;
}

void CThread::JoinThread()
{
  if (m_thread)
  {
    pthread_join(m_thread, 0);
    m_thread = 0;
  }
}

bool CThread::IsRunning()
{
  return m_running;
}

