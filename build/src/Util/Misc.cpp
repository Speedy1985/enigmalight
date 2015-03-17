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
#include <iostream>
#include <fstream>
#include <sstream>

#include <locale.h>
#include <stdarg.h>
#include "Util/Misc.h"



using namespace std;

void PrintError(const std::string& error)
{
  std::cerr << "ERROR: " << error << "\n";
}

//get the first word (separated by whitespace) from string data and place that in word
//then remove that word from string data
bool GetWord(string& data, string& word)
{
  stringstream datastream(data);
  string end;

  datastream >> word;
  if (datastream.fail())
  {
    data.clear();
    return false;
  }

  size_t pos = data.find(word) + word.length();

  if (pos >= data.length())
  {
    data.clear();
    return true;
  }

  data = data.substr(pos);
  
  datastream.clear();
  datastream.str(data);

  datastream >> end;
  if (datastream.fail())
    data.clear();

  return true;
}

//convert . or , to the current locale for correct conversion of ascii float
void ConvertFloatLocale(std::string& strfloat)
{
  static struct lconv* locale = localeconv();
  
  size_t pos = strfloat.find_first_of(",.");

  while (pos != string::npos)
  {
    strfloat.replace(pos, 1, 1, *locale->decimal_point);
    pos++;

    if (pos >= strfloat.size())
      break;

    pos = strfloat.find_first_of(",.", pos);
  }
}

int hexFromFile(const char *filename)
{ 
  FILE* fd = fopen(filename, "r");
  if (!fd) return -1;
  int result = -1;
  fscanf(fd, "%x", &result);
  fclose(fd);
  return result;
}

const char *file_getline(const char *filename)
{
  static char *line = NULL;
  static size_t n = 0;
  size_t ret;
  FILE *f;

  f = fopen(filename, "r");
  if (f == NULL) {
    perror(filename);
    return NULL;
  }

  ret = getline(&line, &n, f);

  fclose(f);

  if (ret < 0)
    return NULL;

  while (ret-- > 0) {
    if ((line[ret] != '\n') &&
      (line[ret] != '\r'))
      break;
    line[ret] = '\0';
  }

  return line;
}

int file_scanf_line(const char *filename, const char *fmt, ...)
{
  const char *line = file_getline(filename);
  va_list ap;
  int ret;

  if (line == NULL)
    return -1;

  va_start(ap, fmt);
  ret = vsscanf(line, fmt, ap);
  va_end(ap);

  return ret;
}
