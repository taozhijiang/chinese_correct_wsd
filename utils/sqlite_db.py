#!/usr/bin/python3
#-*- coding: utf-8 -*-
#encoding=utf-8

import os
import time
import sqlite3
import hashlib


SQLITE_PATH_NAME = "sqlite.db"

class SQlite_Db:
    def __init__(self):
        self.db_path_name = SQLITE_PATH_NAME
        if not os.path.exists(self.db_path_name):
            print("初始化-数据库文件不存在，创建数据库中")
            self.db_init()
        else:
            pass

    def db_init(self):
        try:
            conn = sqlite3.connect(self.db_path_name, timeout = 300)
            sql_creat_table = '''
                        create table if not exists jieba_info (
                        id integer primary key autoincrement,
                        char_key varchar(10) DEFAULT NULL,
                        count int DEFAULT 0
                        ); '''
            conn.execute(sql_creat_table)
        except Exception as e:
            print ('-1--'+str(e)+'--')
        finally:
            conn.commit()
            conn.close()

    def db_query_count(self, key):
        sql_query_data = ''' select count from jieba_info where char_key = '%s' ''' %(key)
        one = 0
        try:
            conn = sqlite3.connect(self.db_path_name,  timeout = 2000, check_same_thread = False)
            results = conn.execute(sql_query_data)
            one = results.fetchone()[0]
        except Exception as e:
            print ('-2--'+str(e)+'--')
        finally:
            conn.close()
        return one

    def db_insert(self, key, count = 1):
        sql_query_data = ''' select count(*) from jieba_info where char_key = '%s' ''' % key
        try:
            conn = sqlite3.connect(self.db_path_name,  timeout = 2000,  check_same_thread = False)
            total = conn.execute(sql_query_data)
            if total.fetchone()[0] > 0:
                return
            sql_insert_data = '''insert into jieba_info(char_key, count) values ('%s', '%d')''' %(key, count)
            conn.execute(sql_insert_data)
        except Exception as e:
            print ('-3--'+str(e)+'--')
        finally:
            conn.commit()
            conn.close()

    def db_update_count(self, key, count = 1):
        sql_query_data = ''' select count(*) from jieba_info where char_key = '%s' ''' % key
        try:
            conn = sqlite3.connect(self.db_path_name,  timeout = 2000,  check_same_thread = False)
            total = conn.execute(sql_query_data)
            if total.fetchone()[0] >= 0:
                sql_update_data = '''update jieba_info set count = '%d' where char_key = '%s' ''' %(count, key)
                conn.execute(sql_update_data)
        except Exception as e:
            print ('-4--'+str(e)+'--')
        finally:
            conn.commit()
            conn.close()

    def db_dump(self):
        sql_dump_data = '''select * from jieba_info'''
        try:
            conn = sqlite3.connect(self.db_path_name,  timeout = 2000,  check_same_thread = False)
            cursor = conn.execute(sql_dump_data)
            for row in cursor:
                print (row[0],row[1],row[2])
        except Exception as e:
            print ('-5--'+str(e)+'--')
        finally:
            conn.close()

if __name__ == '__main__':
   db = SQlite_Db()
   db.db_insert("aaa")
   db.db_insert("bbb", 3)
   db.db_dump()
   db.db_update_count('bbb',8)
   print(db.db_query_count('aaa'))
   print(db.db_query_count('xxx'))
   print(db.db_query_count('bbb'))
