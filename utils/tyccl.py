#!/usr/bin/python3

import pickle


file_name = 'TYCCL.dat'

#词典,用于增强分词功能
dict_name = 'TYCCL.dat_DICT'

#义项
list_name = 'TYCCL.dat_LIST'
mean_name = 'TYCCL.dat_MEAN'

tyccl_dict = {}
tyccl_list = {}
tyccl_mean = {}

with open(file_name, 'r') as fin:
    for ch in fin:
        ch = ch.strip()
        ch_l = ch.split()
        tyccl_list[ch_l[1]] = ch_l[2:]
        ch_sub = ch_l[2:]
        for item in ch_sub:
            if item not in tyccl_dict.keys():
                # 词,以及词性
                tyccl_dict[item] = ch_l[0]
            if item not in tyccl_mean.keys():
                tyccl_mean[item] = [ch_l[1]]
            else:
                tyccl_mean[item].append(ch_l[1])

with open(dict_name, 'w') as fout:
    for (key,val) in tyccl_dict.items():
        fout.write(key+' '+val+'\n')


with open(mean_name, 'wb') as fout:
    pickle.dump(tyccl_mean, fout, True)

with open(list_name, 'wb') as fout:
    pickle.dump(tyccl_list, fout, True)
