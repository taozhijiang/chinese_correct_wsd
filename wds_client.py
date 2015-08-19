#!/usr/bin/python
#-*- coding: utf-8 -*-
#encoding=utf-8

import os
import time
import threading

import socket

import sys

# Server Side Configuration
#HOST = "192.168.1.163"
HOST = "127.0.0.1"
PORT = 10244

def dispatch_me(str_test):

    if not str_test:
        return None

    sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sk.connect((HOST, PORT))
    
    req_url = {'CLIENT':7789,'TYPE':'REQ_WDS','DATA':str_test}

    jreq_url = repr(req_url) + ','
    sk.sendall((jreq_url).encode())
    
    # 等待服务器返回
    try:
        rep_url = sk.recv(1024).decode()
    except Exception as e:
        print("Socket Error:", str(e))
        return None
    finally:
        # 关闭，节约资源
        sk.close()
        
    if not rep_url:
        print("服务器处理失败！")
        return None
    else:
        jrep_url = eval(rep_url)[0]
        if jrep_url and jrep_url['CLIENT'] == 7789 and jrep_url['TYPE'] == 'REP_WDS':
            return (jrep_url['DATA'])

if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            print("原语句:" + sys.argv[i])
            print("分析结果:" + dispatch_me(sys.argv[i]))
    else:
        str_test = "对京东信任度大打折扣"
        print("原语句:" + str_test)
        print("分析结果:" + dispatch_me(str_test))
    
