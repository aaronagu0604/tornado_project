#!/usr/bin/env python
# coding=utf8


from tornado.web import RequestHandler
from model import User, Store


class MobilePageNotFoundHandler(RequestHandler):
    def get(self):
        self.set_status(404)
        return self.write('not found')


class MobileBaseHandler(RequestHandler):
    def get_user(self):
        user = None
        token = self.request.headers.get('token', None)
        if token:
            data = self.application.memcachedb.get(token)
            if data is not None:
                try:
                    user = User.get(id=data)
                except:
                    user = None
        return user

    def get_store_area_code(self):
        user = self.get_user()
        if user is None:
            area_code = self.get_default_area_code()  # 默认使用西安市的code
        else:
            area_code = user.store.area_code
        return area_code

    def get_default_area_code(self):
        return '00270001'  # 默认使用西安市的code


class MobileAuthHandler(MobileBaseHandler):
    def prepare(self):
        token = self.request.headers.get('token', None)
        if token:
            data = self.application.memcachedb.get(token)
            if data is None:
                self.set_status(401)
                self.write('Unauthorized')
                self.finish()
        else:
            self.set_status(401)
            self.write('Unauthorized')
            self.finish()
