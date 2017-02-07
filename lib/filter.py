#!/usr/bin/env python
#coding=utf8

import time
import re

def datetimeformat(value, fmt='%Y-%m-%d %H:%M:%S'):
    return time.strftime(fmt, time.localtime(value))

def timeformat(value, fmt='%H:%M:%S'):
    return time.strftime(fmt, time.localtime(value))

def dateformat(value, fmt='%Y-%m-%d'):
    return time.strftime(fmt, time.localtime(value))

def rightformat(value):
    return value[-5:]

def truncate_words(s, num=50, end_text='...'):
    s = unicode(s,'utf8')
    length = int(num)
    if len(s) > length:
        s = s[:length]
        if not s[-1].endswith(end_text):
            s= s+end_text
    return s

def null(value):
    return value if value else ""


def register_filters():
    filters ={}
    filters['truncate_words'] = truncate_words
    filters['datetimeformat'] = datetimeformat
    filters['dateformat'] = dateformat
    filters['null'] = null
    filters['rightformat'] = rightformat
    return filters

##过滤HTML中的标签
#将HTML中标签等信息去掉
#@param htmlstr HTML字符串.
def filter_tags(htmlstr):
    #先过滤CDATA
    re_cdata=re.compile('//<!CDATA\[[>]∗//\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>')#HTML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s=replaceCharEntity(s)#替换实体
    return s

##替换常用HTML字符实体.
#使用正常的字符替换HTML中特殊的字符实体.
#你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
#@param htmlstr HTML字符串.
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES={'nbsp':' ','160':' ',
                'lt':'<','60':'<',
                'gt':'>','62':'>',
                'amp':'&','38':'&',
                'quot':'"''"','34':'"',}

    re_charEntity=re.compile(r'&#?(?P<name>\w+);')
    sz=re_charEntity.search(htmlstr)
    while sz:
        entity=sz.group()#entity全称，如>
        key=sz.group('name')#去除&;后entity,如>为gt
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
            sz=re_charEntity.search(htmlstr)
        except KeyError:
            #以空串代替
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr

# def repalce(s,re_exp,repl_string):
#     return re_exp.sub(repl_string,s)
