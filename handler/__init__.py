#!/usr/bin/env python
# coding=utf8


from tornado.web import RequestHandler
import functools


class MobilePageNotFoundHandler(RequestHandler):
    def get(self):
        self.set_status(404)
        return self.write('not found')


class MobileHandler(RequestHandler):
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
