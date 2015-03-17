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

#ifndef MISCUTIL
#define MISCUTIL

#include "Inclstdint.h"

// istringstream constructors.
#include <iostream>     // std::cout
#include <sstream>      // std::istringstream
#include <string>       // std::string

#include <iostream>
#include <exception>
#include <stdexcept>

#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <math.h>

void          PrintError(const std::string& error);
bool          GetWord(std::string& data, std::string& word);
void          ConvertFloatLocale(std::string& strfloat);
int           hexFromFile(const char *filename);
const char*   file_getline(const char *filename);
int           file_scanf_line(const char *filename, const char *fmt, ...);

typedef struct {
  int R, G, B;
} Color;

template <class Value>
inline std::string ToString(Value value)
{
  std::string data;
  std::stringstream valuestream;
  valuestream << value;
  valuestream >> data;
  return data;
}

//Optimized Approximative pow() thanks to http://martin.ankerl.com/2012/01/25/optimized-approximative-pow-in-c-and-cpp/
/*inline double fastPow(double a, double b) {
  union {
    double d;
    int x[2];
  } u = { a };
  
  //Big indian
  u.x[1] = (int)(b * (u.x[1] - 1072632447) + 1072632447);
  u.x[0] = 0;
  
  //Litlle indian
  //u.x[1] = 0;
  //u.x[0] = (int)(b * (u.x[1] - 1072632447) + 1072632447);
  return u.d;
}*/

inline std::string GetErrno()
{
  return strerror(errno);
}

inline std::string GetErrno(int err)
{
  return strerror(err);
}

template <class A, class B, class C>
inline A Clamp(A value, B min, C max)
{
  return value < max ? (value > min ? value : min) : max;
}

template <class A, class B>
inline A Max(A value1, B value2)
{
  return value1 > value2 ? value1 : value2;
}

template <class A, class B, class C>
inline A Max(A value1, B value2, C value3)
{
  return (value1 > value2) ? (value1 > value3 ? value1 : value3) : (value2 > value3 ? value2 : value3);
}

template <class A, class B>
inline A Min(A value1, B value2)
{
  return value1 < value2 ? value1 : value2;
}

template <class A, class B, class C>
inline A Min(A value1, B value2, C value3)
{
  return (value1 < value2) ? (value1 < value3 ? value1 : value3) : (value2 < value3 ? value2 : value3);
}

template <class T>
inline T Abs(T value)
{
  return value > 0 ? value : -value;
}

template <class A, class B>
inline A Round(B value)
{
  if (value == 0.0)
  {
    return 0;
  }
  else if (value > 0.0)
  {
    return (A)(value + 0.5);
  }
  else
  {
    return (A)(value - 0.5);
  }
}

inline int32_t Round32(float value)
{
  return lroundf(value);
}

inline int32_t Round32(double value)
{
  return lround(value);
}

inline int64_t Round64(float value)
{
  return llroundf(value);
}

inline int64_t Round64(double value)
{
  return llround(value);
}

inline bool StrToInt(const std::string& data, int& value)
{
  return sscanf(data.c_str(), "%i", &value) == 1;
}

inline bool StrToInt(const std::string& data, int64_t& value)
{
  return sscanf(data.c_str(), "%" PRIi64, &value) == 1;
}

inline bool HexStrToInt(const std::string& data, int& value)
{
  return sscanf(data.c_str(), "%x", &value) == 1;
}

inline bool HexStrToInt(const std::string& data, int64_t& value)
{
  return sscanf(data.c_str(), "%" PRIx64, &value) == 1;
}

inline bool StrToFloat(const std::string& data, float& value)
{
  return sscanf(data.c_str(), "%f", &value) == 1;
}

inline bool StrToFloat(const std::string& data, double& value)
{
  return sscanf(data.c_str(), "%lf", &value) == 1;
}

inline bool StrToBool(const std::string& data, bool& value)
{
  std::string data2 = data;
  std::string word;
  if (!GetWord(data2, word))
    return false;
  
  if (word == "1" || word == "true" || word == "on" || word == "yes")
  {
    value = true;
    return true;
  }
  else if (word == "0" || word == "false" || word == "off" || word == "no")
  {
    value = false;
    return true;
  }
  else
  {
    int ivalue;
    if (StrToInt(word, ivalue))
    {
      value = ivalue != 0;
      return true;
    }
  }

  return false;
}

inline unsigned long createRGB(int r, int g, int b)
{   
    return ((r & 0xff) << 16) + ((g & 0xff) << 8) + (b & 0xff);
}

inline std::string RGBToHex(int rNum, int gNum, int bNum)
{
  std::string result;

  char r[255];  
  sprintf(r, "%.2X", rNum);
  result.append(r );

  char g[255];  
  sprintf(g, "%.2X", gNum);
  result.append(g );

  char b[255];  
  sprintf(b, "%.2X", bNum);
  result.append(b );
  
  return result;
}


#endif //MISCUTIL
