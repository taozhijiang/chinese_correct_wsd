#!/usr/bin/python3

import os
import sys
import time

from collections import OrderedDict


from hanzi_util import is_zh_number,is_terminator,is_punct,is_zh,is_zhs
import hanzi_prep

# Switch with ICTCLAS / JIEBA / ...
USE_SEGMENT = "JIEBA"
# USE_SEGMENT = "ICTCLAS"

FILE_NAME = "./data/ge.dat"
#预处理,每句一行
FILE_NAME_PREP = FILE_NAME + "_PREP"
#结巴分词处理
if USE_SEGMENT == "JIEBA":
    FILE_NAME_JIEBA = FILE_NAME + "_JIEBA"
    FILE_NAME_JIEBA_LM = FILE_NAME_JIEBA + "_LM"
    FILE_NAME_JIEBA_1 = FILE_NAME_JIEBA + "_1"
    FILE_NAME_JIEBA_2 = FILE_NAME_JIEBA + "_2"
elif USE_SEGMENT == "ICTCLAS":
    FILE_NAME_JIEBA = FILE_NAME + "_ICTCLAS"
    FILE_NAME_JIEBA_LM = FILE_NAME_JIEBA + "_LM"
    FILE_NAME_JIEBA_1 = FILE_NAME_JIEBA + "_1"
    FILE_NAME_JIEBA_2 = FILE_NAME_JIEBA + "_2"

FILE_LIST_WORDS = "./data/list_words.dat"


JIEBA_HZ_1 = {}
JIEBA_HZ_2 = {}

JIEBA_LIST_WORDS = []
with open(FILE_LIST_WORDS) as fin:
    for item in fin.readlines():
        item = item.strip(' \r\n\t')
        item = item.split(':')
        JIEBA_LIST_WORDS.append(item[0])

i = 0
start_flag = 0
with open(FILE_NAME_JIEBA_LM) as fin:
    #with open(FILE_NAME_JIEBA_1,"w") as fout:
    for line in fin:
        i = i + 1
        if not i % 1000:
            print("C:%d" %(i))
        if not line.find('\\1-grams:'):
            start_flag = 1
            continue
        if not line.find('\\2-grams:'):
            break 
        if start_flag:
            aa = line.split()
            if aa:
                item_key = aa[1]
                item_val = 10**float(aa[0])
                item_val *= 10000
                JIEBA_HZ_1[item_key] = item_val
                    #fout.write("%s:%f\n"%(aa[1], item_val))

with open(FILE_NAME_JIEBA_1,"w") as fout:
    JIEBA_HZ_1_OR = OrderedDict(sorted(JIEBA_HZ_1.items(), key=lambda t: t[1], reverse=True))
    for key, val in JIEBA_HZ_1_OR.items():
        fout.write("%s:%f\n"%(key, val))

i = 0
start_flag = 0
with open(FILE_NAME_JIEBA_LM) as fin:
        for line in fin:
            i = i + 1
            if not i % 1000:
                print("C:%d" %(i))
            if not line.find('\\2-grams:'):
                start_flag = 1
                continue
            if not line.find('\\end\\'):
               break 
            if start_flag:
                aa = line.split()
                if aa:
                    if aa[1] in JIEBA_LIST_WORDS or aa[2] in JIEBA_LIST_WORDS: 
                        item_key = aa[1]+"-"+aa[2]
                        item_val = 10**float(aa[0])
                        JIEBA_HZ_2[item_key] = item_val

# 归类 2-grams
total_len = len(JIEBA_HZ_1)
i = 0
with open(FILE_NAME_JIEBA_2,"w") as fout:
    for key in JIEBA_HZ_1_OR:
        i += 1
#不在白名单的，剔除掉
        if key not in JIEBA_LIST_WORDS:
            continue
        tmp_dict = {}
        for key_1, val_1 in JIEBA_HZ_2.items():
            key_1_s = key_1.split('-')
            if key in key_1_s:
                tmp_dict[key_1] = val_1
        tmp_dict_or = OrderedDict(sorted(tmp_dict.items(), key=lambda t: t[1], reverse=True)) 
        fout.write('[%s]\n'%(key))
        print("%d/%d"%(i,total_len))
        for key_1, val_1 in tmp_dict_or.items():
            fout.write("%s:%f\n"%(key_1, val_1))


print("你好,处理完毕")
