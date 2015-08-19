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

import re
import copy

import ctypes


# Server Side Configuration
#HOST = "192.168.1.163"
HOST = "127.0.0.1"
PORT = 10244

FILE_NAME = "./data/jd2.dat"

#分词处理
# Switch with ICTCLAS / JIEBA / ...
USE_SEGMENT = "JIEBA"

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

JIEBA_HZ = {}
if not os.path.exists(FILE_NAME_JIEBA_PK):
    print("请计算产生词频数据!")
    os.exit()
else:
    print("加载JIEBA词频信息")
    with open(FILE_NAME_JIEBA_PK, 'rb') as fin:
        JIEBA_HZ = pickle.load(fin)

JIEBA_PINYIN = {}
if not os.path.exists(FILE_NAME_JIEBA_PINYIN):
    print("请计算产生拼音信息!")
    os.exit()
else:
    print("加载JIEBA拼音信息")
    with open(FILE_NAME_JIEBA_PINYIN, 'rb') as fin:
        JIEBA_PINYIN = pickle.load(fin)

def correct_result(to_do, list_cors, verbose = False):

    max_pro = 0
    ret_item = None

    if not list_cors or not to_do or len(to_do) != 3:
        return None
    
    if verbose:
        for item in list_cors:
            if item and item['data']:
                if item['type'] == 1:
                    print("TYPE1 纠错结果：%s %s %s，概率%f"%(to_do[0],item['item'],to_do[2],item['pro']))
                elif item['type'] == 2:
                    print("TYPE2 纠错结果：%s %s，概率%f"%(item['item'],to_do[2],item['pro']))
                elif item['type'] == 3:
                    print("TYPE3 纠错结果：%s %s，概率%f"%(to_do[0],item['item'],item['pro']))
            else:
                print("TYPE%d 纠错失败" %(item['type']))
    
    for item in list_cors:
        if item and item['data']:
            if item['pro'] > max_pro:
                max_pro = item['pro']
                ret_item = item

    return ret_item

# z - zh
# c - ch
# s - sh
# l - n
# en - eng
# in - ing

def sub_hash_pinyin(py):
    ret_list = [py]

    if len(py) < 2:
        return None


    if re.match(r'^ch|sh|zh',py):
        ret_list.append(py[0]+py[2:])

    if py[0] == 'l':
        ret_list.append('n'+py[1:])
    if py[0] == 'n':
        ret_list.append('l'+py[1:])

    #deep copy
    ret_list_2 = ret_list[:]

    for item in ret_list:
        if re.search(r'(eng|ing)$',item):
            ret_list_2.append(item[0:-1])

        if re.search(r'(en|in)$',item):
            ret_list_2.append(item+'g')

    return ret_list_2

#将输入的拼音,hash成多个模糊音的结果
def hash_pinyin(pinyin_t):
    pinyin_segs = []
    pinyin_test = []
    pinyin_l = pinyin_t.split('-')
    for item in pinyin_l:
        word_1 = sub_hash_pinyin(item)
        pinyin_segs.append(word_1)

        #生成拼音序列
        if not len(pinyin_test):
            pinyin_test = [ [x] for x in word_1 ]
        else:
            pinyin_tmp = []
            for item_t in word_1:
                tmp = copy.deepcopy(pinyin_test)
                for item_j in tmp:
                    item_j.append(item_t) 
                pinyin_tmp.extend(tmp)
            pinyin_test = copy.deepcopy(pinyin_tmp)

    pinyin_l = []
    for item in pinyin_test:
        pinyin_l.append('-'.join(item))

    return pinyin_l

    
    
# type can be 1,2,3        
# 采用拼音模糊音进行匹配纠错
def sub_correct_me_ext(head_t, check_t, tail_t, type_t):
    if not check_t:
        return None

    if not head_t and not tail_t:
        return None

    p_res_1 = {}
    p_res_2 = {}
    max_pro = 0
    max_item = None
    
    if head_t:    
        pinyin_t = pinyin.word2pinyin_split(head_t,'-') + '-' + pinyin.word2pinyin_split(check_t,'-')
        pinyin_ts = hash_pinyin(pinyin_t)
        for pinyin_t in pinyin_ts:
            if pinyin_t in JIEBA_PINYIN.keys():
                list_t = JIEBA_PINYIN.get(pinyin_t)
                for item in list_t:
                    if head_t != item[0:len(head_t)]:
                        continue
                    else:
                        p_res_1[item[len(head_t):]] = JIEBA_HZ.get(item)
    
    if tail_t:
        pinyin_t = pinyin.word2pinyin_split(check_t,'-') + '-' + pinyin.word2pinyin_split(tail_t,'-')
        pinyin_ts = hash_pinyin(pinyin_t)
        for pinyin_t in pinyin_ts:
            if pinyin_t in JIEBA_PINYIN.keys():
                list_t = JIEBA_PINYIN.get(pinyin_t)
                for item in list_t:
                    if tail_t != item[len(check_t):]:
                        continue
                    else:
                        p_res_2[item[0:len(check_t)]] = JIEBA_HZ.get(item)
    
    if not p_res_1:
        p_res_1 = p_res_2
    elif not p_res_2:
        p_res_2 = p_res_1

    p_res_intr = dict.fromkeys(x for x in p_res_1 if x in p_res_2)
    if p_res_intr:
        for item in p_res_intr:
            p_res_intr[item] = p_res_1[item]*p_res_2[item] / (p_res_1[item] + p_res_2[item])
            if p_res_intr[item] > max_pro:
                max_pro = p_res_intr[item]
                max_item = item
    
    return ({'item':max_item, 'pro':max_pro, 'data':p_res_intr, 'type': type_t})

# type can be 1,2,3        
def sub_correct_me(head_t, check_t, tail_t, type_t):
    if not check_t:
        return None

    if not head_t and not tail_t:
        return None

    p_res_1 = {}
    p_res_2 = {}
    max_pro = 0
    max_item = None
    
    if head_t:    
        pinyin_t = pinyin.word2pinyin_split(head_t,'-') + '-' + pinyin.word2pinyin_split(check_t,'-')
        if pinyin_t in JIEBA_PINYIN.keys():
            list_t = JIEBA_PINYIN.get(pinyin_t)
            for item in list_t:
                if head_t != item[0:len(head_t)]:
                    continue
                else:
                    p_res_1[item[len(head_t):]] = JIEBA_HZ.get(item)
    
    if tail_t:
        pinyin_t = pinyin.word2pinyin_split(check_t,'-') + '-' + pinyin.word2pinyin_split(tail_t,'-')
        if pinyin_t in JIEBA_PINYIN.keys():
            list_t = JIEBA_PINYIN.get(pinyin_t)
            for item in list_t:
                if tail_t != item[len(check_t):]:
                    continue
                else:
                    p_res_2[item[0:len(check_t)]] = JIEBA_HZ.get(item)
    
    if not p_res_1:
        p_res_1 = p_res_2
    elif not p_res_2:
        p_res_2 = p_res_1

    p_res_intr = dict.fromkeys(x for x in p_res_1 if x in p_res_2)
    if p_res_intr:
        for item in p_res_intr:
            p_res_intr[item] = p_res_1[item]*p_res_2[item] / (p_res_1[item] + p_res_2[item])
            if p_res_intr[item] > max_pro:
                max_pro = p_res_intr[item]
                max_item = item
    
    return ({'item':max_item, 'pro':max_pro, 'data':p_res_intr, 'type': type_t})


def correct_me(str_test, enhance = True):

    print("")
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
        print("未知分词类型!")
        jieba_i = []
    print("分词结果:%s"%(repr(jieba_i)))
    jieba_i = jieba_i.split()
    jieba_len = len(jieba_i)
    if jieba_len < 3:
        print("词数太小，放弃纠错!")
        return
    jieba_key = []
    jieba_pro = []
    for i in range(1,jieba_len):

        #不考虑开头结尾模式
        tmp_str = jieba_i[i-1] + jieba_i[i]
        pro = JIEBA_HZ.get(tmp_str)

        jieba_key.append(tmp_str)
        if pro:
            jieba_pro.append(pro)
        else:
            jieba_pro.append(0)

    print("分词表:"+repr(jieba_key))
    print("概率表:"+repr(jieba_pro))

    jieba_pro_t = []
    for i in range(0,jieba_len-2):
        jieba_pro_t.append( jieba_pro[i] + jieba_pro[i+1])

    min_index = jieba_pro_t.index(min(jieba_pro_t)) + 1
    print("可疑位置:[%d]->%s"%(min_index,jieba_i[min_index]))
    to_do = []
    g_check_a = None
    g_check_e = None
    #纠错位置不可能在开头或者结尾
    to_do.append(jieba_i[min_index-1])
    to_do.append(jieba_i[min_index])
    to_do.append(jieba_i[min_index+1])
    if min_index - 2 >= 0:
        g_check_a = jieba_i[min_index-2]
    if min_index + 2 < jieba_len:
        g_check_e = jieba_i[min_index+2]

    print("需要处理:"+repr(to_do))
    print("辅助检测:%s,%s" %(g_check_a, g_check_e))

    #保存最终的结果
    p_res_stage1 = {}
    p_res_stage2 = {}
    p_res_stage3 = {}

    if enhance:
        #STAGE1 假设分词没有错误
        p_res_st1 = sub_correct_me_ext(to_do[0], to_do[1], to_do[2], 1)
        #STAGE2 假设第一和第二个合并
        p_res_st2 = sub_correct_me_ext(g_check_a, to_do[0]+to_do[1], to_do[2], 2)
        #STAGE3 假设第二和第三个合并
        p_res_st3 = sub_correct_me_ext(to_do[0], to_do[1]+to_do[2], g_check_e, 3)
    else:
        #STAGE1 假设分词没有错误
        p_res_st1 = sub_correct_me(to_do[0], to_do[1], to_do[2], 1)
        #STAGE2 假设第一和第二个合并
        p_res_st2 = sub_correct_me(g_check_a, to_do[0]+to_do[1], to_do[2], 2)
        #STAGE3 假设第二和第三个合并
        p_res_st3 = sub_correct_me(to_do[0], to_do[1]+to_do[2], g_check_e, 3)

    #打印纠正结果   
    cor_ret = correct_result(to_do, [p_res_st1, p_res_st2, p_res_st3], True)
    if not cor_ret:
        final_words = ['NONE']
    else:
        if cor_ret['type'] == 1:
            final_words = jieba_i[0:min_index-1] + [ to_do[0], cor_ret['item'], to_do[2] ] + jieba_i[min_index+2:jieba_len]
        elif cor_ret['type'] == 2:
            final_words = jieba_i[0:min_index-1] + [ cor_ret['item'], to_do[2] ] + jieba_i[min_index+2:jieba_len]
        elif cor_ret['type'] == 3:
            final_words = jieba_i[0:min_index-1] + [ to_do[0], cor_ret['item'] ] + jieba_i[min_index+2:jieba_len]
        else:
            final_words = ['NONE']

    return ''.join(final_words)
    

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
        raw_recv = conn.recv(2048)
        # 只考虑GBK UTF-8编码
        try:
            req_datas = raw_recv.decode()
        except Exception as e:
            req_datas = raw_recv.decode('gbk')
            pass
        #req_datas = req_datas[:-1]
        jreq_datas = eval(req_datas)
        for req_item in jreq_datas:
            if req_item['CLIENT'] != 0 and req_item['TYPE'] == 'REQ_COR':
                rep_data = correct_me(req_item['DATA'])
                rep_url = {'CLIENT':req_item['CLIENT'],'TYPE':'REP_COR','DATA':rep_data}
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

    #s = bytes("我想要一个双卡双待的手机", encoding='utf-8')
    #size = ctypes.c_int()
    #result = nlpir.ParagraphProcessA(s, ctypes.byref(size), True)

    #result_t_vector = ctypes.cast(result, ctypes.POINTER(nlpir.ResultT))
    #words = []
    #for i in range(0, size.value):
    #    r = result_t_vector[i]
    #    word = s[r.start:r.start+r.length]
    #    words.append(word) 
    #for word in words:
    #    print(word.decode('utf-8'))


    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            correct_me(sys.argv[i])
    else:
            thread_distr = DistributeThread(HOST, PORT, 99)
            thread_distr.start()   
            threads_process = []
            for i in range(20, 25):
                t = ProcessPoolThread(i)
                t.start()
                time.sleep(2)
                threads_process.append(t)
                print("启动处理线程...")

            print("你好,服务器线程启动完毕,等待客户端请求...")

            while True:
                print("服务器还活着 ;-)...")
                time.sleep(60)


    if USE_SEGMENT == "ICTCLAS":
        pynlpir.close()
