#include <Winsock2.h>
#include <stdio.h>
#include <string.h>

//加载动态连接库ws2_32.dll,提供了网络相关API的支持
#pragma comment(lib,"ws2_32.lib")

// Server Side Configuration
const char* HOST_T = "192.168.1.163"
const unsigned short PORT_T =  10244

char request_buf[2048];
char reponse_buf[2048];

char result_buf[1024];

int dig_result(const char* src, char* store)
{
    if(!src || !store)
        return -1;

    char* ptr = strstr(src,"\'DATA\':\'");
    if (! ptr)
        return -1;

    ptr += strlen("\'DATA\':\'");

    while(*ptr != '\'')
    {
        *store++ = *ptr++;
    }

    *store = 0;

    return 0
}

int main( int argc, char* argv[])
{
    //加载套接字库
    WORD wVersionRequested;
    WSADATA wsaData;
    char *l_host = NULL;
    char *l_str_test = NULL;
    int err;

    // correct.exe [host_ip] "测试语句"
    // correct.exe "测试语句"
    if (argc == 3)
    {
        l_host = argv[1];
        l_str_test = argv[2];
    }
    else if (argc == 2)
    {
        l_host = HOST_T;
        l_str_test = argv[1];
    }
    else
    {
        printf("参数错误: correct.exe [host_ip] \"测试语句\" ");
        exit(-1);
    }


    wVersionRequested = MAKEWORD( 1, 1 );
    err = WSAStartup( wVersionRequested, &wsaData );//该函数的功能是加载一个Winsocket库版本
    if ( err != 0 ) 
    {
        return;
    }
    if ( LOBYTE( wsaData.wVersion ) != 1 ||
        HIBYTE( wsaData.wVersion ) != 1 ) 
    {
            WSACleanup( );
            return; 
    }

    //建立通讯 socket
    SOCKET sockClient=socket(AF_INET,SOCK_DGRAM,0);
    SOCKADDR_IN addrSrv;
    addrSrv.sin_addr.S_un.S_addr=inet_addr(HOST);
    addrSrv.sin_family=AF_INET;
    addrSrv.sin_port=htons(PORT);

    //发送数据
    const char* str_test = "对京东新人度大打折扣";
    memset((void*)request_buf,0,sizeof(request_buf));
    sprintf(request_buf,"{'CLIENT':7789,'TYPE':'REQ_COR','DATA':'%s'", str_test);
    printf("向服务器方发送数据:%s",request_buf);
    sendto(sockClient,request_buf,strlen(request_buf)+1,0,(SOCKADDR*)&addrSrv,sizeof(SOCKADDR));

    //接收数据
    memset((void*)response_buf,0,sizeof(response_buf));
    printf("等待对方发送数据... ");
    int len = sizeof(SOCKADDR);
    recvfrom(sockClient,response_buf,sizeof(response_buf),0,(SOCKADDR*)&addrSrv,&len);
    printf("接收的内容为:%s",response_buf);

    if( dig_result(response_buf, result_buf) == 0 )
    {
        printf("原测试语句:%s", l_str_test);
        printf("纠正结果:%s", result_buf)
    }

    //结束通信
    closesocket(sockClient);//关闭服务器套接字
    WSACleanup();//结束套接字库的调用
    system("pause");
}
