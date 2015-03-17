#ifndef CENIGMALIGHT
#define CENIGMALIGHT

#include <string>
#include <vector>

#include "Util/TcpSocket.h"
#include "Util/MessageQueue.h"

#include "Lights/Light.h"

class CClient;
class CMainLoop;

class CLightOption
{
    public:
        CLightOption();

        std::string                 SetOption(const char* option, bool& send);
        std::string                 GetOption(const char* option, std::string& output);

        void                        SetScanRange(int width, int height);
 
        void                        AddPixel(int* rgb);
        void                        SetColorSequence(int color_sequence)  { m_color_sequence = color_sequence; }
        
        std::string                 m_name;
        std::string                 m_pos;
        float                       m_speed;
        float                       m_autospeed;
        float                       m_singlechange;

        bool                        m_interpolation;
        bool                        m_use;

        float                       m_value;
        float                       m_valuerange[2];
        float                       m_saturation;
        float                       m_satrange[2];
        int                         m_threshold;
        float                       m_gamma;
        float                       m_gammacurve[256];
        int                         m_color_sequence;

        float                       m_rgb[3];
        int                         m_rgbcount;
        float                       m_prevrgb[3];
        void                        GetRGB(float* rgb);

        float                       m_hscan[2];
        float                       m_vscan[2];
        float                       m_hscan_orginal[2];
        float                       m_vscan_orginal[2];

        int                         m_width;
        int                         m_height;
        int                         m_hscanscaled[2];
        int                         m_vscanscaled[2];
};

class CEnigmaLight
{
    public:
        CEnigmaLight();            
        
        int                         rgbBuffer[3][500][256]; // [RGB][LEDS][POINTER]
        unsigned char               pointer;

        void                        SetLocal        (bool local)    { m_local = local; }
        int                         Connect(const char* address, int port, int usectimeout);
        const char*                 GetError()                      { return m_error.c_str(); }

        int                         GetNrLights()                   { return m_lights.size(); }
        const char*                 GetLightName    (int lightnr);
        int                         SetAdjust       (bool use, int *adjust);
        
        void                        SetVscanDepth   (int depth, int xres, int yres);
        void                        SetHscanDepth   (int depth, int xres, int yres);
        
        int                         SetPriority     (int priority);
        void                        SetScanRange    (int width,   int height);

        int                         AddPixel(int lightnr, int* rgb);
        void                        AddPixel(int* rgb, int x, int y);
        
        void                        FillBuffer();
        void                        ProcessImage(unsigned char* image, int xsize, int ysize, unsigned char delay);
        void                        SetColorSequence(int color_sequence);

        int                         SendRGB(int sync, int* outputused, CClient* client, int cluster_leds);
        int                         Ping(int* outputused, bool send);

        int                         GetNrOptions();
        const char*                 GetOptionDescription(int option);
        int                         SetOption(int lightnr, const char* option);
        int                         GetOption(int lightnr, const char* option, const char** output);
        
        bool                        CheckLightExists(int lightnr, bool printerror = true);
        
        int                         m_color_sequence;
        bool                        m_local; //this bool is true when grabber is used as local.
        std::vector<CLightOption>   m_lights;
        std::vector<CLight>         c_lights;
        
        std::vector<std::string>    m_options;
        std::string                 m_lastoption; //place to store the last option retrieved by GetOption

        CMainLoop*                  m_mainloop;
        bool                        InitLocal(std::vector<CLight>& lights, CMainLoop& mainloop);       

    private:
        CTcpClientSocket            m_socket;

        bool                        usocket;
        std::string                 m_address;
        int                         m_port;
        std::string                 m_error;
        CMessageQueue               m_messagequeue;
        int                         m_usectimeout;

        bool                        ReadDataToQueue();
        bool                        WriteDataToSocket(std::string strdata);
        bool                        ParseWord(CMessage& message, std::string wordtocmp);
        bool                        ParseLights(CMessage& message);        
        
};

#endif //CEnigmaLight