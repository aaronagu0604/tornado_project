#!/usr/bin/env python
# coding=utf8

import qrcode
import urllib2
import simplejson
import time
import os
import random
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers


FILE_SERVER = 'http://img.520czj.com/upload/image'
PILIMAGE_FILE = os.getcwd()+"upload/"

def postRequest(data):
    try:
        register_openers()
        # 图片素材
        datagen, headers = multipart_encode(
            {"file": data})
        url = FILE_SERVER
        req = urllib2.Request(url, datagen, headers)
        result = urllib2.urlopen(req).read()
        result = simplejson.loads(result)
        if result['flag'] == 1:
            return result['data']
        else:
            return None
    except Exception:
        return None

def createqrcode(content='default content'):
    qr = qrcode.make(content)
    filename = PILIMAGE_FILE+str(time.time())[1:10]+str(random.randrange(1,10000))+'.jpeg'
    qr.save(filename, format='jpeg')
    st = postRequest(open(filename, 'rb'))
    return st

if __name__ == '__main__':
    print createqrcode('https://qr.alipay.com/bax05783myafczpvylrq604b')
