#!/usr/bin/python3
#-*- coding: utf-8 -*-
#encoding=utf-8

import os
import time
import sqlite3

SQLITE_PATH_NAME = "ngram-data.db"

db_path_name = SQLITE_PATH_NAME


def db_init(db_path):
    try:
        conn = sqlite3.connect(db_path, timeout = 300)
        sql_creat_table = '''
                    create table if not exists jieba_pk (
                    id integer primary key autoincrement,
                    word varchar(20) DEFAULT NULL,
                    ); '''
        conn.execute(sql_creat_table)
        sql_creat_table = '''
                    create table if not exists jieba_pinyin (
                    id integer primary key autoincrement,
                    pinyin varchar(50) DEFAULT NULL,
                    words  varchar(50) DEFAULT NULL,
                    ); '''
        conn.execute(sql_creat_table)
    except Exception as e:
        print ('-1--'+str(e)+'--')
    finally:
        conn.commit()
        conn.close()


def db_insert(self, key, count = 1): sql_query_data = ''' select count(*) from jieba_info where char_key = '%s' ''' % key
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
