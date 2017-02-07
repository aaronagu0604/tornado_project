#!/usr/bin/env python
# coding=utf8

import re
#from suds.client import Client
import time
import urllib
import urllib2
import httplib
import sys
reload(sys)
from sys import path
import setting
import logging

sys.setdefaultencoding('utf-8')

def setting_from_object(obj):
    setting = dict()
    for key in dir(obj):
        if key.isupper():
            setting[key.lower()] = getattr(obj, key)
    return setting


def find_subclasses(klass, include_self=False):
    accum = []
    for child in klass.__subclasses__():
        accum.extend(find_subclasses(child, True))
    if include_self:
        accum.append(klass)
    return accum


def vmobile(mobile):
    return re.match(r"1[0-9]{10}", mobile)


def vemail(email):
    return re.match(r"^(\w)+(\.\w+)*@(\w)+((\.\w{2,3}){1,3})$", email)


def sendmsg( mobile, content, isyzm):
    # client = Client(sms_url)
    if isyzm:
        sms_param = setting.SMS_PARAM_YZM.split(',')
        sms_url = sms_param[0]
        username = sms_param[1]
        pwd = sms_param[2]
        signname=sms_param[3]
        # result = client.service.SendSMSYZM(mobile, content, signtype, isyzm)
    else:
        sms_param = setting.SMS_PARAM_YX.split(',')
        sms_url = sms_param[0]
        username = sms_param[1]
        pwd = sms_param[2]
        signname=sms_param[3]
        # result = client.service.SendSMSYX(mobile, content)
    # print result
    # http://api.bjszrk.com/sdk/BatchSend.aspx?CorpID=test&Pwd=test&Mobile=13999999999&Content=ABC&Cell=&SendTime=&encode=utf-8
    content = content + '【' + signname + '】'
    values={'CorpID':username,'Pwd':pwd,'Mobile':mobile,'Content':content,'encode':'utf-8'}
    data = urllib.urlencode(values)
    req = urllib2.Request(sms_url, data)
    response = urllib2.urlopen(req)
    result = response.read()

def mkdir(path):
    import os

    try:
        path = path.strip()
        path = path.rstrip("\\")
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
        return True
    except:
        return False


def calprice(cost, function):
    if cost and function:
        if len(function) > 0:
            s = function.replace('A', (cost.comment if cost.comment and not cost.comment == '' else '0')). \
                replace('B', str(cost.wlprice)).replace('C', str(cost.bzprice)). \
                replace('D', str(cost.rgprice)).replace('E', str(cost.shprice)).replace('F', str(cost.ccprice)). \
                replace('G', str(cost.glprice))
            result = eval(s)
            return round(result, 1)
    return None


def calpriceajax(cost, function):
    if cost and function:
        if len(function) > 0:
            s = function.replace('A', (cost['comment'] if cost['comment'] and not cost['comment'] == '' else '0')). \
                replace('B', str(cost['wlprice'])).replace('C', str(cost['bzprice'])). \
                replace('D', str(cost['rgprice'])).replace('E', str(cost['shprice'])).replace('F',
                                                                                              str(cost['ccprice'])). \
                replace('G', str(cost['glprice']))
            return eval(s)
    return None