#!/usr/bin/python3
import pinyin

res = {}

with open("tmp.txt", 'r') as fin:
    with open("tmp_a.txt",'w') as fout:
        for ch in fin:
            ch = ch.strip()
            if ch not in res.keys():
                res[ch] = "\'%s\':(\'%s\',),\n" %(ch,pinyin.get(ch))
                fout.write(res[ch])


print(repr(res))
