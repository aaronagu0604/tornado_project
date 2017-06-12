#!/usr/bin/env python
# coding=utf8

from handler import AdminBaseHandler, BaseHandler
from lib.route import route
from model import *
import simplejson
import time
import logging
import setting
import os
from payqrcode import postRequest
from tornado.gen import coroutine
from tornado.web import asynchronous
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from lib.mqhelper import create_msg
import hashlib
@route(r'/', name='wx root')
class RootHandler(BaseHandler):
    def get(self):
        self.redirect('/index')

@route(r'/signature', name='wx signature')
class Signature(BaseHandler):
    def get(self):
        token = 'wxczjplateform'
        signature = self.get_argument('signature')
        timestamp = self.get_argument('timestamp')
        nonce = self.get_argument('nonce')
        echostr = self.get_argument('echostr')

        keylist = [token, timestamp, nonce]
        keylist.sort()
        sha1 = hashlib.sha1()
        map(sha1.update, keylist)
        hashcode = sha1.hexdigest()

        if hashcode == signature:
            self.write(echostr)
            return

        self.write('signature error')

@route(r'/index', name='wx_index')  # 后台首页
class IndexHandler(BaseHandler):
    def get(self):
        self.render('weixin/index.html')

@route(r'/insurance/(\d+)', name='wx_insurance')  # 后台首页
class InsuranceHandler(BaseHandler):
    def get(self,id):
        i_id = int(id)
        insurance = Insurance.get(id = i_id)
        self.render('weixin/insurance.html',insurance=insurance)

@route(r'/insurance_order_base', name='wx_insurance_order_base')  # 后台首页
class InsuranceOrderBaseHandler(BaseHandler):
    def get(self):
        self.render('weixin/insurance_order_base.html')

@route(r'/insurance_order_items', name='wx_insurance_order_items')  # 后台首页
class InsuranceOrderItemsHandler(BaseHandler):
    def get(self):
        self.render('weixin/insurance_order_base.html')

@route(r'/insurance_order_new', name='wx_insurance_order_new')  # 后台首页
class InsuranceOrderNewHandler(BaseHandler):
    def get(self):
        self.render('weixin/insurance_order_New.html')

@route(r'/insurance_orders', name='wx_insurance_orders')  # 后台首页
class InsuranceOrdersHandler(BaseHandler):
    def get(self):
        self.render('weixin/insurance_orders.html')

@route(r'/insurance_order_detail', name='wx_insurance_order_detail')  # 后台首页
class InsuranceOrderDetailHandler(BaseHandler):
    def get(self):
        self.render('weixin/insurance_order_detail.html')


@route(r'/insurance_order_price', name='wx_insurance_order_price')  # 后台首页
class InsuranceOrderPriceHandler(BaseHandler):
    def get(self):
        self.render('weixin/insurance_order_Price.html')

@route(r'/pay_detail', name='wx_pay_detail')  # 后台首页
class PayDetailHandler(BaseHandler):
    def get(self):
        self.render('weixin/pay_detail.html')

@route(r'/login', name='wx_login')  # 后台首页
class LoginHandler(BaseHandler):
    def get(self):
        self.render('weixin/Login.html')

@route(r'/mine', name='wx_mine')  # 后台首页
class MineHandler(BaseHandler):
    def get(self):
        self.render('weixin/mine.html')

@route(r'/rake_back_setting', name='wx_rake_back_setting')  # 后台首页
class RakeBackSettingHandler(BaseHandler):
    def get(self):
        self.render('weixin/rake_back_setting.html')

@route(r'/user_address', name='wx_user_address')  # 后台首页
class UserAddressHandler(BaseHandler):
    def get(self):
        self.render('weixin/user_address.html')

@route(r'/user_address_detail', name='wx_user_address_detail')  # 后台首页
class UserAddressDetailHandler(BaseHandler):
    def get(self):
        self.render('weixin/user_address_detail.html')

@route(r'/user_childrens', name='wx_user_childrens')  # 后台首页
class UserChildrensHandler(BaseHandler):
    def get(self):
        self.render('weixin/user_childrens.html')

@route(r'/user_income', name='wx_user_income')  # 后台首页
class UserIncomeHandler(BaseHandler):
    def get(self):
        self.render('weixin/user_income.html')

@route(r'/user_income_record', name='wx_user_income_record')  # 后台首页
class UserIncomeRecordHandler(BaseHandler):
    def get(self):
        self.render('weixin/user_income_recod.html')