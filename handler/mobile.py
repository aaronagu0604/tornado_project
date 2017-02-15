#!/usr/bin/env python
# coding=utf8

import logging
import setting
import simplejson
from tornado.web import RequestHandler
from lib.route import route
from model import *
import uuid
from handler import MobileHandler
import random
from lib.mqhelper import create_msg


@route(r'/', name='mobile_app')
class MobileAppHandler(RequestHandler):
    def get(self):
        us = User.select()
        logging.info('---%s---'%us.count())
        self.write("czj api")


@route(r'/mobile/getvcode', name='mobile_getvcode')
class MobileGetVCodeAppHandler(RequestHandler):
    """
    @apiGroup auth
    @apiVersion 1.0.0
    @api {post} /mobile/getvcode 01. 获取验证码
    @apiDescription 获取验证码

    @apiParam {String} mobile 电话号码
    @apiParam {Int} flag 验证码类型： 0注册 1忘记密码 2绑定手机号 3提现

    @apiSampleRequest /mobile/getvcode
    """
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        mobile = self.get_body_argument("mobile", None)
        flag = self.get_body_argument("flag", None)

        user = User.select().where(User.mobile == mobile)
        if flag == 0:
            if user.count() > 0:
                result['msg'] = '您已经是车装甲会员'
                self.write(simplejson.dumps(result))
                return
        elif flag == 1:
            if user.count() == 0:
                result['msg'] = '您还不是车装甲会员'
                self.write(simplejson.dumps(result))
                return

        VCode.delete().where(VCode.created < (int(time.time()) - 30 * 60)).execute()

        uservcode = VCode()
        uservcode.mobile = mobile
        uservcode.vcode = random.randint(1000, 9999)
        uservcode.created = int(time.time())
        uservcode.flag = flag
        if uservcode.validate():
            if VCode.select().where((VCode.mobile == mobile) & (VCode.flag == flag)).count() > 3:
                result['msg'] = '您的操作过于频繁，请稍后再试'
            else:
                try:
                    uservcode.save()
                    result['flag'] = 1
                    result['msg'] = '验证码已发送'
                    logging.info('getvcode: ' + str(uservcode.vcode) + '; flag=' + str(flag))
                    sms = {'mobile': mobile, 'body': str(uservcode.vcode), 'signtype': '1', 'isyzm': 'vcode'}
                    create_msg(simplejson.dumps(sms), 'sms')  # 验证码
                except Exception, ex:
                    result['msg'] = '验证码发送失败，请联系400客服处理'

        else:
            result['msg'] = '验证码发送失败，请联系400客服处理'

        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/checkvcode', name='mobile_checkvcode')
class MobileCheckVCodeAppHandler(RequestHandler):
    """
    @apiGroup auth
    @apiVersion 1.0.0
    @api {post} /mobile/checkvcode 02. 检查验证码
    @apiDescription 检查验证码

    @apiParam {String} mobile 电话号码
    @apiParam {String} vcode 验证码
    @apiParam {Int} flag 验证码类型： 0注册 1忘记密码 2绑定手机号 3提现

    @apiSampleRequest /mobile/checkvcode
    """

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        mobile = self.get_body_argument('mobile', None)
        vcode = self.get_body_argument('vcode', None)
        flag = self.get_body_argument("flag", None)
        if mobile and vcode and flag:
            VCode.delete().where(VCode.created < (int(time.time()) - 30 * 60)).execute()
            if VCode.select().where((VCode.mobile == mobile) & (VCode.vcode == vcode) & (VCode.flag == flag)).count() > 0:
                result['flag'] = 1
            else:
                result['msg'] = "请输入正确的验证码"
            pass
        else:
            result['flag'] = 0
            result['msg'] = '请传入正确的手机号码与验证码'
        self.write(simplejson.dumps(result))


@route(r'/mobile/reg', name='mobile_reg')  # 手机端注册
class MobileRegHandler(RequestHandler):
    """
    @apiGroup auth
    @apiVersion 1.0.0
    @api {post} /mobile/reg 03. 商家申请入驻平台
    @apiDescription 商家申请入驻平台

    @apiParam {String} mobile 电话号码
    @apiParam {String} password 密码
    @apiParam {String}     rePassword 重复密码
    @apiParam {Int}     store_type 门店类型
    @apiParam {String}    referee 推广人编号
    @apiParam {String}    companyName 公司名称
    @apiParam {String}     province 省
    @apiParam {String}     city 市
    @apiParam {String}     district 区
    @apiParam {String}     address 详细地址
    @apiParam {String}     legalPerson 法人代表
    @apiParam {String}     licenseCode 营业执照编号
    @apiParam {String}     licensePic 营业执照图片
    @apiParam {String}     storePic 门店图片

    @apiSampleRequest /mobile/reg
    """

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        mobile = self.get_body_argument("mobile", None)
        password = self.get_body_argument("password", None)
        rePassword = self.get_body_argument("rePassword", None)
        store_type = self.get_body_argument("store_type", None)
        referee = self.get_body_argument("referee", None)
        companyName = self.get_body_argument("companyName", None)
        province = self.get_body_argument("province", None)
        city = self.get_body_argument("city", None)
        district = self.get_body_argument("district", None)
        address = self.get_body_argument("address", None)
        legalPerson = self.get_body_argument("legalPerson", None)
        licenseCode = self.get_body_argument("licenseCode", None)
        licensePic = self.get_body_argument("licensePic", None)
        storePic = self.get_body_argument("storePic", None)
        user = User()
        user.mobile = mobile
        user.password = password
        try:
            user.validate()
            if password and rePassword:
                if password != rePassword:
                    result['msg'] = "两次密码不一致，请重新输入"
                else:
                    if not (store_type and companyName and province and city and district and address and legalPerson
                            and licenseCode and licensePic and storePic):
                        raise Exception('门店信息不完整')
                    try:
                        admin_user = AdminUser.get(code = referee).id
                    except:
                        admin_user = None
                    now = int(time.time())
                    sid = Store.create(store_type=int(store_type), admin_code=referee, admin_user=admin_user, name=companyName,
                                       area_code=district, address=address, legal_person=legalPerson, license_code=licenseCode,
                                       license_image=licensePic, store_image=storePic, lng='0', lat='0', pay_password='',
                                       intro='', linkman=legalPerson, mobile=mobile, created=now)
                    user.signuped = now
                    user.lsignined = now
                    user.store = sid.id
                    user.token = setting.user_token_prefix + str(uuid.uuid4())
                    self.application.memcachedb.set(user.token, str(user.id), setting.user_expire)
                    user.save()
                    StoreAddress.create(store=sid.id, province=province, city=city, region=district, address=address,
                                        street='', name=legalPerson, mobile=mobile, created=now, create_by=user.id)
                    result['data'] = {
                        'token': user.token,
                        'store_type': store_type,
                        'active': 0
                    }
                    result['flag'] = 1
                    result['msg'] = '注册成功'
            else:
                result['msg'] = "请输入密码和确认密码"
        except Exception, ex:
            result['msg'] = ex.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/login', name='mobile_login')  # 手机端登录
class MobileLoginHandler(RequestHandler):
    """
    @apiGroup auth
    @apiVersion 1.0.0
    @api {post} /mobile/login 04. 登录
    @apiDescription 通过手机号密码登录系统

    @apiParam {String} mobile 电话号码
    @apiParam {String} password 密码

    @apiSampleRequest /mobile/login
    """
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        mobile = self.get_body_argument("mobile", None)
        password = self.get_body_argument("password", None)
        if mobile and password:
            try:
                user = User.get(User.mobile == mobile)
                if user.check_password(password):
                    if user.active > 0:
                        token = user.token
                        if token:
                            data = self.application.memcachedb.get(token)
                            if data is None:
                                token = setting.user_token_prefix + str(uuid.uuid4())
                        else:
                            token = setting.user_token_prefix + str(uuid.uuid4())
                        result['flag'] = 1
                        result['data']['type'] = user.store.store_type
                        result['data']['token'] = token
                        result['data']['uid'] = user.id
                        self.application.memcachedb.set(token, str(user.id), setting.user_expire)
                        user.updatesignin(token)
                    else:
                        result['msg'] = "此账户被禁止登录，请联系管理员。"
                else:
                    result['msg'] = "用户名或密码错误"
            except Exception, e:
                result['msg'] = "此用户不存在"
        else:
            result['msg'] = "请输入用户名或者密码"
        self.write(simplejson.dumps(result))
        self.finish()

















