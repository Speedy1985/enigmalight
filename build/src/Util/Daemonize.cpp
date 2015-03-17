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

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "Util/Daemonize.h"
#include "Util/Misc.h"

void Daemonize()
{
  //fork a child process
  pid_t pid = fork();
  if (pid == -1)
    fprintf(stderr, "fork(): %s", GetErrno().c_str());
  else if (pid > 0)
    exit(0); //this is the parent process, exit

  //detach the child process from the parent
  if (setsid() < 0)
    fprintf(stderr, "setsid(): %s", GetErrno().c_str());

  //route stdout and stderr to /dev/null
  fclose(stdout);
  stdout = fopen("/dev/null", "w");
  fclose(stderr);
  stderr = fopen("/dev/null", "w");
}

