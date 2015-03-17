#include <stdio.h>
#include <cstdlib> 
#include <fstream>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <iostream>
#include <cstring>      // Needed for memset
#include <sys/socket.h> // Needed for the socket functions
#include <netdb.h>      // Needed for the socket functions
#include <unistd.h>
#include "Util/Misc.h"
#include "ElightTalk/Main.h"

using namespace std;

void         PrintHelpMessage();
    
bool         m_printhelp;                               
bool         m_printoptions;   
    
std::vector<std::string> m_options;

void         ParseFlags(int tempargc, char** tempargv); 
void         ParseOptions();

std::string  m_flags;                                   
std::string  m_straddress;

void PostGetopt(int optind, int argc, char** argv) {};                              
void SetOption(const char* option);

//Socket vars
int socketfd;
int status;
struct addrinfo host_info;       // The struct that getaddrinfo() fills up with data.
struct addrinfo *host_info_list; // Pointer to the to the linked list of host_info's.

int main(int argc, char* argv[])
{
    m_printhelp = false;
    m_flags = "h::o:";
    
    if (m_printhelp) //print help message
    {
        PrintHelpMessage();
        exit(1);
    }
    
    try
    {
        ParseFlags(argc, argv);
    }
    catch (string error)
    {
        PrintError(error);
        PrintHelpMessage();
        exit(1);
    }

    memset(&host_info, 0, sizeof host_info);

    std::cout << "Setting up the structs..."  << std::endl;

    host_info.ai_family = AF_UNSPEC;     // IP version not specified. Can be both.
    host_info.ai_socktype = SOCK_STREAM; // Use SOCK_STREAM for TCP or SOCK_DGRAM for UDP.

    // Now fill up the linked list of host_info structs with google's address information.
    status = getaddrinfo("127.0.0.1", "6767", &host_info, &host_info_list);
    // getaddrinfo returns 0 on succes, or some other value when an error occured.
    // (translated into human readable text by the gai_gai_strerror function).
    if (status != 0)  std::cout << "getaddrinfo error" << gai_strerror(status) ;


    std::cout << "Creating a socket..."  << std::endl;
    socketfd = socket(host_info_list->ai_family, host_info_list->ai_socktype,
                      host_info_list->ai_protocol);
    if (socketfd == -1)  std::cout << "socket error " ;


    std::cout << "Connecting..."  << std::endl;
    status = connect(socketfd, host_info_list->ai_addr, host_info_list->ai_addrlen);
    if (status == -1){
      std::cout << "Connect error" << std::endl;
      exit(1);
    }
    else
    {
      std::cout << "Succesfull Connected." << std::endl;
    }


    
    if(m_options.size() > 0)
    {
      std::cout << "ParseOptions: " << m_options.size() << std::endl;
      ParseOptions();
    }
    
    freeaddrinfo(host_info_list);
    close(socketfd);

    std::cout << "Disconnected..." << std::endl;
    std::cout << "Exit." << std::endl;

    return 0;
}

//very simple, store a copy of argc and argv
CArguments::CArguments(int argc, char** argv)
{
  m_argc = argc;

  if (m_argc == 0)
  {
    m_argv = NULL;
  }
  else
  {
    m_argv = new char*[m_argc];
    for (int i = 0; i < m_argc; i++)
    {
      m_argv[i] = new char[strlen(argv[i]) + 1];
      strcpy(m_argv[i], argv[i]);
    }
  }
}

//delete the copy of argv
CArguments::~CArguments()
{
  if (m_argv)
  {
    for (int i = 0; i < m_argc; i++)
    {
      delete[] m_argv[i];
    }
    delete[] m_argv;
  }
}

std::vector<std::string> split(std::string str,std::string sep){
    char* cstr=const_cast<char*>(str.c_str());
    char* current;
    std::vector<std::string> arr;
    current=strtok(cstr,sep.c_str());
    while(current!=NULL){
        arr.push_back(current);
        current=strtok(NULL,sep.c_str());
    }
    return arr;
}

void ParseFlags(int tempargc, char** tempargv)
{
  //that copy class sure comes in handy now!

  string option;
  int    c;

  opterr = 0; //we don't want to print error messages
  
  while ((c = getopt(tempargc, tempargv, m_flags.c_str())) != -1)
  {
    if (c == 'h')
    {
      m_printhelp = true;
      return;
    }
    else if (c == 'o') //option
    {
        //cout << optarg << endl;
        m_options.push_back(optarg);
    }
    else if (c == '?') //unknown option
    {
      //check if we know this option, but expected an argument
      if (m_flags.find(ToString((char)optopt) + ":") != string::npos)
      {
        throw string("-- Option " + ToString((char)optopt) + " requires an argument\n");
      }
      else
      {
        throw string("-- Unkown option " + ToString((char)optopt) + "\n");
      }
    }
  }

  PostGetopt(optind, tempargc, tempargv); //some postprocessing
}

void ParseOptions()
{

    for (int i = 0; i < m_options.size(); i++)
    {
        string option = m_options[i];
        string optionname;
        string optionvalue;

        //check if '=' exists and it's not at the end of the string
        if (option.find('=') == string::npos || option.find('=') == option.size() - 1)
        {
          throw string("wrong option \"" + option + "\", syntax is -o option=value");
        }

        optionname = option.substr(0, option.find('='));   //option name is everything before = (already shaved off the lightname here)
        optionvalue = option.substr(option.find('=') + 1); //value is everything after =

        option = "set " + optionname + " " + optionvalue + "\n";
        
        //bitch if we can't set this option
        SetOption(option.c_str());
        
    }
}

void SetOption(const char* option)
{

    std::cout << "sending message..."  << std::endl;
    int len;
    ssize_t bytes_sent;
    len = strlen(option);
    
    if (send(socketfd, option, len, 0) == -1) {
      perror("send");
      exit(1);
    }else{
      cout << "Command [" << option << "] sended.." << "\n";
    }    
}

void PrintHelpMessage()
{
  cout << "Usage: elight-talk [OPTION]\n";
  cout << "\n";
  cout << "  options:\n";
  cout << "\n";
  cout << "  -o  Set option, -o speed=30 -o value=3\n";
  cout << "  -h  help\n";
}