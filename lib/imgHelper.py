#!/usr/bin/env python
# coding=utf8
import os, sys
from PIL import Image
import cookielib;
import urllib2;
import os

def GenerateMobileImg(imgPath):
    #size = 300, 300
    imgArrr = os.path.splitext(imgPath)
    outfile = imgArrr[0] + ".mobile"+imgArrr[1]
    try:
        im = Image.open(imgPath)
        im.thumbnail((im.size[0]/2, im.size[1]/2), Image.ANTIALIAS)
        im.save(outfile) #, "JPEG", quality=80
        print 'save success'
    except Exception, e:
        print "cannot create thumbnail for '%s'" % imgPath
        print e.message

def SaveAdminImage2Local(imgPath):

    attrArr=imgPath.replace('http://','').split('/')
    if not os.path.exists('/home/www/workspace/eofan/src/upload/' + attrArr[2]):
        os.mkdir('/home/www/workspace/eofan/src/upload/' + attrArr[2])
    with open('/home/www/workspace/eofan/src/upload/' + attrArr[2] + '/' + attrArr[3], "wb") as f:
        f.write(get_file(imgPath))


def get_file(url):
    # try:
    cj=cookielib.LWPCookieJar()
    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    req=urllib2.Request(url)
    operate=opener.open(req)
    data=operate.read()
    return data
    # except BaseException, e:
    #     print e
    #     return None

if __name__ == '__main__':
    # uploadPath = '/home/www/workspace/eofan/src/upload'
    # #uploadPath = 'D://ads'
    # for root, dirs, list in os.walk(uploadPath):
    #     for i in list:
    #         dir = os.path.join(root, i)    #将分离的部分组成一个路径名
    #         filename, ext = os.path.splitext(dir)
    #         if ext.upper() == '.JPEG' or ext.upper() == '.JPG' or ext.upper() == '.PNG' or ext.upper() == '.GIF':
    #             if not ".mobile." in dir:
    #                 print dir
    #                 GenerateMobileImg(dir)

    url='http://admin.eofan.com/upload/01010207/14290910234146.jpg'
    SaveAdminImage2Local(url)
