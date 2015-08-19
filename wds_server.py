#!/usr/bin/python3

import os
import sys
import time

import pickle

from hanzi_util import is_zh_number,is_terminator,is_punct,is_zh,is_zhs
import hanzi_prep

import pinyin

import threading
import socket
import queue


# Server Side Configuration
#HOST = "192.168.1.163"
HOST = "127.0.0.1"
PORT = 10244

# Switch with ICTCLAS / JIEBA / ...
USE_SEGMENT = "JIEBA"

FILE_NAME = "./data/all.dat"
#结巴分词处理
if USE_SEGMENT == "JIEBA":

    import jieba

    dict_file = './data/MY_DICT.dat'
    jieba.load_userdict(dict_file)
    dict_file = './data/TYCCL.dat_DICT'
    jieba.load_userdict(dict_file)

    FILE_NAME_JIEBA = FILE_NAME + "_JIEBA"
    FILE_NAME_JIEBA_CNT = FILE_NAME_JIEBA + "_CNT"
    FILE_NAME_JIEBA_LM = FILE_NAME_JIEBA + "_LM"
    FILE_NAME_JIEBA_PK = FILE_NAME_JIEBA + "_PK"
    FILE_NAME_JIEBA_PINYIN = FILE_NAME_JIEBA + "_PINYIN"
elif USE_SEGMENT == "ICTCLAS":

    import pynlpir
    from pynlpir import nlpir

    pynlpir.open()

    dict_file = b'./data/MY_DICT.dat'
    nlpir.ImportUserDict(dict_file)
    dict_file = b'./data/TYCCL.dat_DICT'
    nlpir.ImportUserDict(dict_file)

    FILE_NAME_JIEBA = FILE_NAME + "_ICTCLAS"
    FILE_NAME_JIEBA_CNT = FILE_NAME_JIEBA + "_CNT"
    FILE_NAME_JIEBA_LM = FILE_NAME_JIEBA + "_LM"
    FILE_NAME_JIEBA_PK = FILE_NAME_JIEBA + "_PK"
    FILE_NAME_JIEBA_PINYIN = FILE_NAME_JIEBA + "_PINYIN"

tyccl_list_name = './data/TYCCL.dat_LIST'
tyccl_mean_name = './data/TYCCL.dat_MEAN'

JIEBA_HZ = {}
if not os.path.exists(FILE_NAME_JIEBA_PK):
    print("请计算产生词频数据!")
    os.exit()
else:
    print("加载JIEBA词频信息")
    with open(FILE_NAME_JIEBA_PK, 'rb') as fin:
        JIEBA_HZ = pickle.load(fin)

TYCCL_list = {}
TYCCL_mean = {}
if not os.path.exists(tyccl_list_name):
    print("请计算同义词词林数据!")
    os.exit()
else:
    print("加载同义词词林信息")
    with open(tyccl_list_name, 'rb') as fin:
        TYCCL_list = pickle.load(fin)
    with open(tyccl_mean_name, 'rb') as fin:
        TYCCL_mean= pickle.load(fin)

# 返回的是字典类型
def calc_list_pro(word, word_head, word_tail):
    head_pro = []
    tail_pro = []
    total_ret = {}
    
    if word in TYCCL_mean.keys() :
        list_t = TYCCL_mean.get(word)
        if list_t:
            if len(list_t) == 1:
                return { list_t[0] : 1.0 }
            else:
                for item in list_t:
                    words = TYCCL_list.get(item)
                    #print("==义项==> %s"%item)
                    #print("==词列==>%s"%repr(words))
                    head_pro = {}
                    tail_pro = {}
                    # HEAD
                    if word_head:
                        for word_t in words:
                            pro_t = JIEBA_HZ.get(word_head+word_t)
                            if pro_t:
                                #print("%s%s->%f"%(word_head, word_t, pro_t))
                                head_pro[word_head+word_t] = pro_t
                                #print("%s-%s %f " %(word_head,word_t,pro_t))
                            #else:
                            #    head_pro.append(0)
                            #    head_pro[word_head+word_t] = 0


                    # TAIL
                    if word_tail:
                        for word_t in words:
                            pro_t = JIEBA_HZ.get(word_t+word_tail)
                            if pro_t:
                                #print("%s%s->%f"%(word_t, word_tail, pro_t))
                                if word_head:
                                    word_pre = word_head + word_t
                                    if word_pre in head_pro.keys():
                                        # 嘉奖首尾都匹配的
                                        tail_pro[word_t+word_tail] = pro_t * 4
                                        head_pro[word_head+word_t] = head_pro[word_head+word_t] * 4
                                    else:
                                        tail_pro[word_t+word_tail] = pro_t
                                else:
                                    tail_pro[word_t+word_tail] = pro_t
                            #else:
                            #    #tail_pro.append(0)
                            #    tail_pro[word_t+word_tail] = 0

                    if not head_pro and not tail_pro:
                        return None
                    elif not head_pro:
                        total_pro = len(tail_pro)/len(words)*sum(tail_pro.values())/len(tail_pro)
                    elif not tail_pro:
                        total_pro = len(head_pro)/len(words)*sum(head_pro.values())/len(head_pro)
                    else:
                        total_pro = len(head_pro)/len(words)*0.5*sum(head_pro.values())/len(head_pro) + len(tail_pro)/len(words)*0.5*sum(tail_pro.values())/len(tail_pro)

                    total_ret[item] = total_pro
                return total_ret

        return None

def find_max_dict(dict_t):
    if not dict_t:
        return None

    if len(dict_t) == 1:
        return dict_t.popitem()

    max_item = None
    max_pro = 0
    for key,val in dict_t.items():
        if val > max_pro:
            max_pro = val
            max_item = key

    return (max_item, max_pro)


def dispatch_me(str_test):

    print("测试语句：%s" %(str_test))
    line_p = hanzi_prep.split_into_sentences(str_test)
    lines = []
    for line_i in line_p:
        lines.extend(line_i)
    str_i = ''.join(lines)
    if USE_SEGMENT == "JIEBA":
        print("==JIEBA分词==")
        jieba_i = ' '.join(jieba.cut(str_i, cut_all=False))
    elif USE_SEGMENT == "ICTCLAS":
        print("==NLPIR分词==")
        jieba_i = ' '.join(pynlpir.segment(str_i, pos_tagging=False))
    else:
        print("ERROR:未知分词系统!")
        return None

    print("分词结果:%s"%(repr(jieba_i)))
    jieba_i = jieba_i.split()
    jieba_len = len(jieba_i)
    result_collect = []
    for i in range(0,jieba_len):
        if i > 0:
            head = jieba_i[i-1]
        else:
            head = None
        if i < jieba_len -1:
            tail = jieba_i[i+1]
        else:
            tail = None
        ret = calc_list_pro(jieba_i[i], head, tail)
        if ret:
            ret_pro = find_max_dict(ret)
            if ret_pro:
                print("词汇:[[%s]], 最大概率义项:%s, 概率:%f" %(jieba_i[i], ret_pro[0], ret_pro[1]))
                print("DEBUG:::"+repr(ret))
                result_collect.append((jieba_i[i], ret_pro[0], ret_pro[1]))
        else:
            print("无计算结果")

    return result_collect

# Max buffer size
global_q = queue.Queue(maxsize=10)


# 由DistributeThread分发，用于处理客户端请求
class ProcessPoolThread(threading.Thread):
    def __init__(self, tid):
        self.cur_thread = threading.Thread.__init__(self)
        self.threadID = tid
    
    def run(self):
        while True:
            # The Queue get是阻塞的
            conn, addr = global_q.get()
            self.handle_process(conn, addr)

    def handle_process(self, conn, addr):
        # 多个返回可能会被合并到一个数据包中
        print("PROCESS T[%d]正在处理%s" %(self.threadID, repr(addr)))
        req_datas = conn.recv(2048).decode()
        jreq_datas = eval(req_datas)
        for req_item in jreq_datas:
            if req_item['CLIENT'] != 0 and req_item['TYPE'] == 'REQ_WDS':
                rep_data = repr(dispatch_me(req_item['DATA']))
                rep_url = {'CLIENT':req_item['CLIENT'],'TYPE':'REP_WDS','DATA':rep_data}
                jrep_url = repr(rep_url) + ','
                conn.sendall(jrep_url.encode())        
            else:
                print("UKNOWN CLIENT REQUEST!")
                
        return


class DistributeThread(threading.Thread):
    def __init__(self, host, port, tid):
        threading.Thread.__init__(self)   
        self.host = host
        self.port = port
        self.threadID = tid
        self.sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)         

    def run(self):
        print ("启动服务器分发线程 %d ...\n" % self.threadID)
        self.sk.bind((self.host,self.port))
        self.sk.listen(1)
    
        while True:
            conn, addr = self.sk.accept()
            print("SERVER[%d], Recv request from %s" % (self.threadID, addr))
            global_q.put((conn, addr))
            
        print ("我怎么可能退出。。。。")
        return        
        
if __name__ == '__main__':

    #str_test = "这款电脑是正品行货吗"
    #dispatch_me(str_test)

    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            dispatch_me(sys.argv[i])
    else:
        thread_distr = DistributeThread(HOST, PORT, 99)
        thread_distr.start()   
        threads_process = []
        for i in range(20, 22):
            t = ProcessPoolThread(i)
            t.start()
            time.sleep(2)
            threads_process.append(t)
            print("启动处理线程...")

        print("你好,服务器线程启动完毕,等待客户端请求...")

        while True:
            print("服务器还活着 ;-)...")
            time.sleep(60)

