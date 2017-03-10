#!/usr/bin/env python
# coding=utf8

import logging
import setting
import simplejson
from lib.route import route
import math
from model import *
from tornado.web import RequestHandler


@route(r'/webapp', name='webapp_index')
class WebAppIndexHandler(RequestHandler):
    def get(self):
        self.render("webapp/index.html")


@route(r'/webapp/car/(\d+)', name='webapp_car')
class WebAppCarHandler(RequestHandler):
    def get(self, id):
        self.render("webapp/car.html")


@route(r'/webapp/detail/(\d+)', name='webapp_detail')
class WebAppDetailHandler(RequestHandler):
    def get(self, id):
        self.render("webapp/detail.html")