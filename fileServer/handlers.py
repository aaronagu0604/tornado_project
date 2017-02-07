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


class BaseHandler(RequestHandler):
    def valid_user(self):
        token = self.request.headers.get('token', None)
        try:
            data = self.application.session.get(token)
            flag = not (data == None)
        except Exception, e:
            flag = False
            logging.info(e.message)
        if not flag:
            logging.info('匿名用户访问, 来自:%s', self.request.remote_ip)
        return flag

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
        subPath = setting.voiceDir
        if type == 'image':
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
    def options(self):
        pass

    def get(self):
        self.write('please upload a image file')

    def post(self):
        if not self.valid_user():
            self.set_status(500)
            self.write("您无权使用该服务")
            self.finish()
        else:
            result = {}
            result['Flag'] = 0
            result['Data'] = ''
            result['Msg'] = ''
            try:
                meta = self.request.files['file'][0]
                suffix = meta['filename'].split('.')[-1]
                fullname, arr, filename = self.get_full_file_name('image', suffix)
                while os.path.exists(fullname):
                    logging.info('已经存在文件：' + fullname)
                    fullname, arr, filename = self.get_full_file_name('image', suffix)

                f = open(fullname, 'wb')
                f.write(meta['body'])
                f.close()
                result['Data'] = setting.openHost+'/'+arr[0]+'/'+arr[1]+'/'+arr[2]+'/'+arr[3]+'/' + filename
                result['Flag'] = 1
            except Exception, e:
                logging.info('upload image failing: ' + e.message)
                result['Flag'] = 0
                result['Msg'] = 'fail in upload image'
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