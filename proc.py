#!/usr/bin/python3

import os
import sys


import pickle

import pinyin


from hanzi_util import is_zh_number,is_terminator,is_punct,is_zh,is_zhs
import hanzi_prep

# Switch with ICTCLAS / JIEBA / ...
# USE_SEGMENT = "JIEBA"
USE_SEGMENT = "ICTCLAS"

FILE_NAME = "./data/all.dat"
#预处理,每句一行
FILE_NAME_PREP = FILE_NAME + "_PREP"
#结巴分词处理
if USE_SEGMENT == "JIEBA":
    FILE_NAME_JIEBA = FILE_NAME + "_JIEBA"
    FILE_NAME_JIEBA_CNT = FILE_NAME_JIEBA + "_CNT"
    FILE_NAME_JIEBA_LM = FILE_NAME_JIEBA + "_LM"
    FILE_NAME_JIEBA_PK = FILE_NAME_JIEBA + "_PK"
    FILE_NAME_JIEBA_PINYIN = FILE_NAME_JIEBA + "_PINYIN"
elif USE_SEGMENT == "ICTCLAS":
    FILE_NAME_JIEBA = FILE_NAME + "_ICTCLAS"
    FILE_NAME_JIEBA_CNT = FILE_NAME_JIEBA + "_CNT"
    FILE_NAME_JIEBA_LM = FILE_NAME_JIEBA + "_LM"
    FILE_NAME_JIEBA_PK = FILE_NAME_JIEBA + "_PK"
    FILE_NAME_JIEBA_PINYIN = FILE_NAME_JIEBA + "_PINYIN"


i = 0
if not os.path.exists(FILE_NAME_PREP):
    with open(FILE_NAME) as fin:
        with open(FILE_NAME_PREP,"w") as fout:
            for line in fin:
                i = i + 1
                if not i % 1000:
                    print("C:%d" %(i))
                line_p = hanzi_prep.split_into_sentences(line)
                for line_i in line_p:
                    str_i = ''.join(line_i)
                    fout.write(str_i+"\n")

#i = 0
#if not os.path.exists(FILE_NAME_UNIC):
#    with open(FILE_NAME_PREP) as fin:
#        with open(FILE_NAME_UNIC,"w") as fout:
#                for line in fin:
#                    i = i + 1
#                    if not i % 1000:
#                        print("C:%d" %(i))
#                    line_p = hanzi_prep.split_into_sentences_e(line)
#                    for line_i in line_p:
#                        #用空格分割每个汉字
#                        str_i = ' '.join(line_i)
#                        fout.write(str_i+"\n")
#

i = 0
if USE_SEGMENT == "ICTCLAS":
    print("ICTCLAS分词系统")

    #中科院分词系统
    import pynlpir
    from pynlpir import nlpir

    pynlpir.open()

    dict_file = b'./data/MY_DICT.dat'
    nlpir.ImportUserDict(dict_file)
    dict_file = b'./data/TYCCL.dat_DICT'
    nlpir.ImportUserDict(dict_file)

elif USE_SEGMENT == "JIEBA":
    print("JIEBA分词系统")

    #结巴分词
    import jieba

    dict_file = './data/MY_DICT.dat'
    jieba.load_userdict(dict_file)
    dict_file = './data/TYCCL.dat_DICT'
    jieba.load_userdict(dict_file)


else:
    print("未知分词系统")

#导入用户自定义词典
if not os.path.exists(FILE_NAME_JIEBA):
    with open(FILE_NAME_PREP) as fin:
        with open(FILE_NAME_JIEBA,"w") as fout:
                for line in fin:
                    i = i + 1
                    if not i % 1000:
                        print("C:%d" %(i))
                    line_p = hanzi_prep.split_into_sentences_e(line)
                    for line_i in line_p:
                        #用空格分割每个汉字
                        str_i = ''.join(line_i)
                        str_j = ''
                        if USE_SEGMENT == "JIEBA":
                            str_j = ' '.join(jieba.cut(str_i, cut_all=False))
                        elif USE_SEGMENT == "ICTCLAS":
                            str_j = ' '.join(pynlpir.segment(str_i, pos_tagging=False))
                        else:
                            print("ERROR:未知分词系统!")
                        fout.write(str_j+"\n")

if USE_SEGMENT == "ICTCLAS":
    print("END:ICTCLAS分词系统")
    pynlpir.close()

elif USE_SEGMENT == "JIEBA":
    print("END:JIEBA分词系统")

else:
    print("END:未知分词系统")

# 计算N-Gram词频信息
#if not os.path.exists(FILE_NAME_UNIC_LM):
#    str_cmd = "ngram-count -text %s -order 2 -write %s" %(FILE_NAME_UNIC, FILE_NAME_UNIC_CNT)
#    print("正在执行:%s" %(str_cmd))
#    os.system(str_cmd)
#    str_cmd = "ngram-count -read %s -order 2 -lm %s -gt1min 2 -gt1max 5 -gt2min 2 -gt2max 5 " %(FILE_NAME_UNIC_CNT, FILE_NAME_UNIC_LM)
#    print("正在执行:%s" %(str_cmd))
#    os.system(str_cmd)

if not os.path.exists(FILE_NAME_JIEBA_LM):
    str_cmd = "ngram-count -no-sos -no-eos -text %s -order 2 -write %s" %(FILE_NAME_JIEBA, FILE_NAME_JIEBA_CNT)
    #str_cmd = "ngram-count -no-sos -no-eos -text %s -order 3 -write %s" %(FILE_NAME_JIEBA, FILE_NAME_JIEBA_CNT)
    print("正在执行:%s" %(str_cmd))
    os.system(str_cmd)
    str_cmd = "ngram-count -no-sos -no-eos -read %s -order 2 -lm %s -gt1min 2 -gt1max 5 -gt2min 2 -gt2max 5 " %(FILE_NAME_JIEBA_CNT, FILE_NAME_JIEBA_LM)
    #str_cmd = "ngram-count -no-sos -no-eos -read %s -order 3 -lm %s -gt1min 2 -gt1max 5 -gt2min 3 -gt2max 5 " %(FILE_NAME_JIEBA_CNT, FILE_NAME_JIEBA_LM)
    print("正在执行:%s" %(str_cmd))
    os.system(str_cmd)

# 保存数据结构
#UNIC_HZ = {}
#i = 0
#start_flag = 0
#if not os.path.exists(FILE_NAME_UNIC_PK):
#    with open(FILE_NAME_UNIC_LM) as fin:
#        with open(FILE_NAME_UNIC_PK,"w") as fout:
#            for line in fin:
#                i = i + 1
#                if not i % 1000:
#                    print("C:%d" %(i))
#                if not line.find('\\2-grams:'):
#                    start_flag = 1
#                    continue
#                if not line.find('\\end\\'):
#                    continue
#                if start_flag:
#                    aa = line.split()
#                    if aa:
#                        item_key = aa[1]+aa[2]
#                        item_val = 10**float(aa[0])
#                        UNIC_HZ[item_key] = item_val
#    #保存
#    print("保存UNIC词频信息")
#    with open(FILE_NAME_UNIC_PK, 'wb') as fout:
#                pickle.dump(UNIC_HZ, fout, True)
#else:
#    print("加载UNIC词频信息")
#    with open(FILE_NAME_UNIC_PK, 'rb') as fin:
#                UNIC_HZ = pickle.load(fin)
#

JIEBA_HZ = {}
i = 0
start_flag = 0
if not os.path.exists(FILE_NAME_JIEBA_PK):
    with open(FILE_NAME_JIEBA_LM) as fin:
        with open(FILE_NAME_JIEBA_PK,"w") as fout:
            for line in fin:
                i = i + 1
                if not i % 1000:
                    print("C:%d" %(i))
                if not line.find('\\2-grams:'):
                    start_flag = 1
                    continue
                if not line.find('\\end\\'):
                    continue
                if start_flag:
                    aa = line.split()
                    if aa:
                        item_key = aa[1]+aa[2]
                        item_val = 10**float(aa[0])
                        JIEBA_HZ[item_key] = item_val
    #保存
    print("保存JIEBA词频信息")
    with open(FILE_NAME_JIEBA_PK, 'wb') as fout:
                pickle.dump(JIEBA_HZ, fout, True)



JIEBA_PINYIN = {"null":["null"]}
i = 0
start_flag = 0
if not os.path.exists(FILE_NAME_JIEBA_PINYIN):
    with open(FILE_NAME_JIEBA_LM) as fin:
        with open(FILE_NAME_JIEBA_PINYIN,"w") as fout:
            for line in fin:
                i = i + 1
                if not i % 1000:
                    print("C:%d" %(i))
                if not line.find('\\2-grams:'):
                    start_flag = 1
                    continue
                if not line.find('\\end\\'):
                    continue
                if start_flag:
                    aa = line.split()
                    pinyin_t = ""
                    if aa:
                        item_key = aa[1]+aa[2]
                        if aa[1] == '<s>' or aa[1] == '</s>':
                            pinyin_t = aa[1] + '-'+pinyin.word2pinyin_split(aa[2],'-')
                        elif aa[2] == '<s>' or aa[2] == '</s>':
                            pinyin_t = pinyin.word2pinyin_split(aa[1],'-') + '-' + aa[2]
                        else:
                            pinyin_t = pinyin.word2pinyin_split(aa[1],'-') + '-' + pinyin.word2pinyin_split(aa[2],'-')
                        if pinyin_t in JIEBA_PINYIN.keys():
                            JIEBA_PINYIN[pinyin_t].append(item_key)
                        else:
                            JIEBA_PINYIN[pinyin_t] = [item_key]
    #保存
    print("保存JIEBA词频信息")
    with open(FILE_NAME_JIEBA_PINYIN, 'wb') as fout:
                pickle.dump(JIEBA_PINYIN, fout, True)



print("你好,处理完毕")
