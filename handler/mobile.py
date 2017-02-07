#!/usr/bin/env python
# coding=utf8
import simplejson
from lib.route import route
from handler import MobileHandler


@route(r'/mobile/login', name='mobile_login')  # 手机端登录
class MobileLoginHandler(MobileHandler):
    """
    @apiGroup auth
    @apiVersion 1.0.0
    @api {post} /mobile/login 01. 登录
    @apiDescription 通过手机号密码登录系统

    @apiParam {String} mobile 电话号码
    @apiParam {String} password 密码
    @apiParam {String} login_type 登录类型 1门店登录

    @apiSampleRequest /mobile/login
    """
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = self.get_mobile_user()
        self.write(simplejson.dumps(result))

















