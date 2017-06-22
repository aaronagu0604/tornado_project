#!/usr/bin/env python
# coding=utf8

from handler import BaseHandler,WXBaseHandler
from lib.route import route
from model import *
import logging
import simplejson
import uuid
import urllib
import urllib2
import time
import string
import random as rand
import traceback
from lib.payment.wxPay import Qrcode_pub
import hashlib

appid = 'wxf23313db028ab4bc'
secret = '8d75a7fa77dc0e5b2dc3c6dd551d87d6'

@route(r'/', name='wx root') # 根域名重定向
class RootHandler(WXBaseHandler):
    def get(self):
        self.redirect('/index')

@route(r'/signature', name='wx signature') # 公众号服务器验证
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

    def post(self):
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

        return

@route(r'/index', name='wx_index')  # 首页
class IndexHandler(WXBaseHandler):
    def get(self):
        # insurance = Insurance.select().where(Insurance.active == 1,Insurance.hot == 1)[:3]
        # self.render('weixin/index.html',insurance=insurance)
        self.render('weixin/index.html')

@route(r'/insurance/(\d+)', name='wx_insurance')  # 保险公司详情页面
class InsuranceHandler(WXBaseHandler):
    def get(self,id):
        i_id = int(id)
        insurance = Insurance.get(id = i_id)
        self.render('weixin/insurance.html',insurance=insurance)

@route(r'/activer/(\d+)', name='wx_activer')  # 活动详情页面
class InsuranceHandler(WXBaseHandler):
    def get(self,id):
        self.render('weixin/activer.html')

@route(r'/category', name='wx_category')  # 分类页面
class CategoryHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/category.html')

@route(r'/insurance_order_base', name='wx_insurance_order_base')  # 保险订单上传个人信息页面
class InsuranceOrderBaseHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/insurance_order_base.html')

@route(r'/insurance_order_items', name='wx_insurance_order_items')  # html 保险下单选择保险条目页面
class InsuranceOrderItemsHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/insurance_order_items.html')

@route(r'/insurance_order_new', name='wx_insurance_order_new')  # 保险下单选择地址优惠方式页面
class InsuranceOrderNewHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/insurance_order_new.html')

@route(r'/insurance_order_success', name='wx_insurance_order_success')  # html 保险下单成功提示页面
class InsuranceOrderSuccessHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/insurance_order_success.html')

@route(r'/insurance_orders', name='wx_insurance_orders')  # html 保险订单列表
class InsuranceOrdersHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/insurance_orders.html')

@route(r'/insurance_order_detail', name='wx_insurance_order_detail')  # html 保险订单详情
class InsuranceOrderDetailHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/insurance_order_detail.html')


@route(r'/insurance_order_price', name='wx_insurance_order_price')  # html 保险订单历史报价方案
class InsuranceOrderPriceHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/insurance_order_Price.html')

@route(r'/pay_detail', name='wx_pay_detail')  # html 微信公众号支付详情页面
class PayDetailHandler(WXBaseHandler):

    def get_access_token(self):
        self.weixin_app_id = appid
        self.weixin_secret = secret
        self.url_access_token = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (
        self.weixin_app_id, self.weixin_secret)
        return simplejson.loads(urllib2.urlopen(self.url_access_token).read())["access_token"]

    def get_jsapi_ticket(self):
        # https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=ACCESS_TOKEN&type=jsapi
        self.url_access_token = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi" % (
        self.get_access_token())
        return simplejson.loads(urllib2.urlopen(self.url_access_token).read())["ticket"]

    def __create_nonce_str(self):
        return ''.join(rand.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self,ret={}):
        string1 = '&'.join(['%s=%s' % (key.lower(), ret[key]) for key in sorted(ret)])
        ret['signature'] = hashlib.sha1(string1).hexdigest()
        return ret


    def get(self):
        ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': self.get_jsapi_ticket(),
            'timeStamp': self.__create_timestamp(),
            'url': 'http://wx.dev.520czj.com/pay_detail'
        }
        ret = self.sign(ret)
        ret['appid'] = appid

        payinfo = Qrcode_pub().getPayQrcode(self.__create_nonce_str(), '车装甲微信测试付款', int(1 * 100))
        self.render('weixin/pay_detail.html',ret=ret,payinfo=payinfo)

@route(r'/wxapi/login', name='wx_api_login')  # html 登录
class WXApiLoginHandler(BaseHandler):
    def get_access_token_from_code(self,code):
        get_access_token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        grant_type = "authorization_code"
        try:
            _code = code
            url = get_access_token_url + "?appid=" + appid + "&secret=" + secret + "&code=" + _code + "&grant_type=" + grant_type

            result = urllib2.urlopen(url).read()
            result = simplejson.loads(result)

            return result['openid'], result['access_token']
        except Exception, e:
            logging.error(traceback.format_exc())
            return '',''
    def get_user_info(self,access_token,openid):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN" % (access_token, openid)
            result = urllib2.urlopen(url).read()
            logging.info(result)
            return simplejson.loads(result)
        except Exception, e:
            logging.error(traceback.format_exc())
            return {}

    def get_access_token(self):
        url_access_token = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (
        appid, secret)
        return simplejson.loads(urllib2.urlopen(url_access_token).read())["access_token"]

    def get(self):
        code = self.get_argument('code','')
        store_id = self.get_argument('state','0')
        openid,_ = self.get_access_token_from_code(code)
        access_token = self.get_access_token()
        userinfo = self.get_user_info(access_token,openid)
        logging.info({'url':'/wxapi/login','code':code,'openid':openid,'accesstoken':access_token,'userinfo':userinfo})
        users = User.select().where(User.openid == openid)
        if users.count() >= 1:
            user = users[0]
        else:
            self.render('weixin/login.html',storeid=store_id,nickname=userinfo['nickname'],openid=openid,subscribe=userinfo['subscribe'])
            return

        self.session['user'] = user
        self.session.save()

        if userinfo['subscribe'] == 1:
            # 已经关注条个人中心
            self.redirect('/mine')
        else:
            # 未关注太跳关注引导
            self.render('weixin/focus_guide.html')

@route(r'/register', name='wx_register')  # html 登录
class LoginHandler(BaseHandler):
    def create_user(self, openid, mobile, nickname, store_id=0):
        try:
            user = User.get(mobile=mobile)
            user.openid = openid
            user.role += 'W'
            user.save()
        except Exception:
            try:
                logging.error(traceback.format_exc())
                user = User()
                user.store = int(store_id)
                user.truename = nickname
                user.mobile = mobile
                user.openid = openid
                user.password = user.create_password('123456')  # 微信用户默认密码：123456
                user.role = 'W'

                user.signuped = int(time.time())
                user.save()
                return user
            except Exception:
                return None

    def get(self):
        openid = self.get_argument('openid','')
        mobile = self.get_argument('mobile', '')
        nickname = self.get_argument('nickname', '')
        store_id = self.get_argument('store_id', 0)
        subscribe = self.get_argument('subscribe', 0)
        user = self.create_user(openid, mobile, nickname, store_id)
        self.session['user'] = user
        self.session.save()
        if subscribe == '1':
            # 已经关注条个人中心
            self.redirect('/mine')
        else:
            # 未关注太跳关注引导
            self.render('weixin/focus_guide.html')

@route(r'/mine', name='wx_mine')  # html 会员中心
class MineHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/mine.html')

@route(r'/bound_mobile', name='wx_bound_mobile')  # html 绑定手机号
class BoundMobileHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/bound_mobile.html')

@route(r'/rake_back_setting', name='wx_rake_back_setting')  # html 返佣配置
class RakeBackSettingHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/rake_back_setting.html')

@route(r'/user_address', name='wx_user_address')  # html 收货地址
class UserAddressHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/user_address.html')

@route(r'/user_address_detail', name='wx_user_address_detail')  # html 编辑地址
class UserAddressDetailHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/user_address_detail.html')

@route(r'/user_childrens', name='wx_user_childrens')  # 我的下线
class UserChildrensHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/user_childrens.html')

@route(r'/user_income', name='wx_user_income')  # html 收入
class UserIncomeHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/user_income.html')

@route(r'/user_income_record', name='wx_user_income_record')  # html 收入明细
class UserIncomeRecordHandler(WXBaseHandler):
    def get(self):
        self.render('weixin/user_income_record.html')

@route(r'/income_record_list', name='api_income_record_list')  # api 收入明细
class IncomeRecordListHandler(WXBaseHandler):
    def get(self):
        result = {'flag':1,'msg':'','data':[]}
        data = [{
            'name': str(i),
            'price': i
        } for i in range(20)]
        result['data'] = data
        self.write(simplejson.dumps(result))

@route(r'/demo_insurance_list', name='wx_demo_insurance_list')
class UserIncomeRecord11Handler(WXBaseHandler):
    def get(self):
        demo = []
        item1 = {"values":1, "displayValues":"中华联合"}
        item2 = {"values":2, "displayValues":"平安"}
        demo.append(item1)
        demo.append(item2)
        self.write(simplejson.dumps(demo))
        self.finish()
