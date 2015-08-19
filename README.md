用于用户输入语句的同音自动纠错.


依赖于pynlpir
https://github.com/tsroten/pynlpir

数据是抓取的某东客服语料训练的，可以后续把自己抓取的语料共享
给大家训练用

./proc.py 训练产生数据

使用方法:
./server.py 或者 /usr/bin/python3 server.py 启动服务端

然后./client_run.py 或者 /usr/bin/python3 client_run.py XXX来进行纠错测试

➜  utf-8 ./client_run.py "我想买哥苹果手机" "对京东新人度大打折扣"
原语句:我想买哥苹果手机
纠正句:我想买个苹果手机
原语句:对京东新人度大打折扣
纠正句:对京东信任度大打折扣
➜  utf-8 

中文词义消歧也是这个思路，但是效果比较差，有时间后续研究。使用到了
同义词词林（没有加入库，utils目录中的只做参考）。
