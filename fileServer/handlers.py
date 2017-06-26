#!/usr/bin/env python
# coding=utf8

from tornado.web import RequestHandler
import logging
import setting
import time
import string
import os
import simplejson
import random
import urllib2


class BaseHandler(RequestHandler):
    def random_str(self, length=24):
        a = list(string.ascii_letters)
        random.shuffle(a)
        return ''.join(a[:length])

    def get_file_path(self, type='image'):
        now = time.localtime()
        year = time.strftime("%Y", now)
        month = time.strftime("%m", now)
        day = time.strftime("%d", now)
        return (type, year, month, day)

    def get_full_file_name(self, type='image', suffix=''):
        filename = setting.serverName + '_'+time.strftime('%Y%m%d%H%M%S') + self.random_str() + '.' + suffix
        arr = self.get_file_path(type)
        subPath = setting.imgDir
        os.chdir(subPath)
        filepath = os.path.join(subPath, *list(arr))
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        fullname = os.path.join(filepath, filename)
        return fullname, arr, filename


class DefaultHandler(RequestHandler):
    def get(self):
        self.write("车装甲——文件服务器")


class PageNotFoundHandler(RequestHandler):
    def get(self):
        self.set_status(404)
        return self.write("service not found")


class UploadImageHandler(BaseHandler):
    def set_default_headers(self):
        print "setting headers!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self):
        self.set_status(204)
        self.finish()

    def get(self):
        self.write('please upload a image file')

    def post(self):
        result = {}
        result['flag'] = 0
        result['data'] = ''
        result['msg'] = ''
        try:
            is_admin = self.get_body_argument('is_admin', None)
            meta = self.request.files['file'][0]
            suffix = meta['filename'].split('.')[-1]
            fullname, arr, filename = self.get_full_file_name('image', suffix)
            while os.path.exists(fullname):
                logging.info('已经存在文件：' + fullname)
                fullname, arr, filename = self.get_full_file_name('image', suffix)
            f = open(fullname, 'wb')
            f.write(meta['body'])
            f.close()
            result['data'] = setting.openHost+'/'+arr[0]+'/'+arr[1]+'/'+arr[2]+'/'+arr[3]+'/' + filename
            result['flag'] = 1
        except Exception, e:
            logging.info('Error: upload image failing,%s' % str(e))
            result['flag'] = 0
            result['msg'] = 'fail in upload image'
        if is_admin:
            self.redirect('%s/admin/upload_pic?data=%s' % (setting.domanName, result['data']))
        else:
            self.set_header("Access-Control-Allow-Origin", "*")
            self.write(simplejson.dumps(result))


class UploadImageFromUrlHandler(BaseHandler):
    def options(self):
        pass

    def get(self):
        self.write('please upload a image file')

    def get_access_token(self):
        self.weixin_app_id = 'wxf23313db028ab4bc'
        self.weixin_secret = '8d75a7fa77dc0e5b2dc3c6dd551d87d6'
        self.url_access_token = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (
            self.weixin_app_id, self.weixin_secret)
        return simplejson.loads(urllib2.urlopen(self.url_access_token).read())["access_token"]

    def get_img_base_media_id(self):
        media_id = self.get_argument('media_id', None)
        url = 'https://api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s' % (
        self.get_access_token(), media_id)

        return simplejson.loads(urllib2.urlopen(url).read())

    def post(self):
        result = {}
        result['flag'] = 0
        result['data'] = ''
        result['msg'] = ''
        imgdata = self.get_img_base_media_id()

        try:
            is_admin = self.get_body_argument('is_admin', None)
            fullname, arr, filename = self.get_full_file_name('image', 'jpg')
            while os.path.exists(fullname):
                logging.info('已经存在文件：' + fullname)
                fullname, arr, filename = self.get_full_file_name('image', 'jpg')
            f = open(fullname, 'wb')
            f.write(imgdata)
            f.close()
            result['data'] = setting.openHost+'/'+arr[0]+'/'+arr[1]+'/'+arr[2]+'/'+arr[3]+'/' + filename
            result['flag'] = 1
        except Exception, e:
            logging.info('Error: upload image failing,%s' % str(e))
            result['flag'] = 0
            result['msg'] = 'fail in upload image'
        if is_admin:
            self.redirect('%s/admin/upload_pic?data=%s' % (setting.domanName, result['data']))
        else:
            self.set_header("Access-Control-Allow-Origin", "*")
            self.write(simplejson.dumps(result))


class ViewHandler(BaseHandler):
    def options(self):
        pass

    def get(self):
        path = self.get_argument("path", u'image')
        result = []
        rootDir = os.path.join(setting.imgDir, path)
        items = os.listdir(rootDir)
        items.sort()
        for f in items:
            fullPath = os.path.join(rootDir, f)
            item = {}
            if os.path.isdir(fullPath):
                item['type'] = 0
                item['name'] = f
                item['path'] = path + u'/' + f
                item['size'] = 0
            elif os.path.isfile(fullPath):
                item['type'] = 1
                item['name'] = f
                item['path'] = setting.openHost + u'/' + path + u'/' + f
                item['size'] = os.path.getsize(fullPath)
            result.append(item)
        self.write(simplejson.dumps(result))