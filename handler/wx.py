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
import setting

appid = 'wxf23313db028ab4bc'
secret = '8d75a7fa77dc0e5b2dc3c6dd551d87d6'

'''                   
https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxf23313db028ab4bc&redirect_uri=http%3A%2F%2Fwx.dev.520czj.com%2Fwxapi%2Flogin&response_type=code&scope=snsapi_base&state=1#wechat_redirect
'''

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
    def get_mobile_home_data(self,token):
        url = "http://api.dev.test.520czj.com/mobile/home"
        req = urllib2.Request(url)
        req.add_header('token',token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())['data']

    def get(self):
        user = self.get_current_user()
        data = self.get_mobile_home_data(user.token)
        logging.info(data)
        banner = data['banner']
        insurance = []
        for item in data['category']:
            if item['title'] == '保险业务':
                insurance = item['data']
        for i in insurance:
            index = i['link'].rfind('/')
            i['link'] = i['link'][:index].replace('czj://','/')

        self.render('weixin/index.html',banner=banner, insurance=insurance)

@route(r'/insurance/(\d+)', name='wx_insurance')  # 保险公司详情页面
class InsuranceHandler(WXBaseHandler):
    def get(self,id):
        i_id = int(id)
        insurance = Insurance.get(id = i_id)
        self.render('weixin/insurance.html',insurance=insurance)

@route(r'/insurance_order_base/(\d+)', name='wx_insurance_order_base')  # 保险订单上传个人信息页面
class InsuranceOrderBaseHandler(WXBaseHandler):
    def get(self,insurance):
        self.render('weixin/insurance_order_base.html',insurance=insurance, ret = self.get_js_sdk_sign(setting.wxdomanName+'/insurance_order_base/'+insurance))

@route(r'/insurance_order_items', name='wx_insurance_order_items')  # html 保险下单选择保险条目页面
class InsuranceOrderItemsHandler(WXBaseHandler):
    def get_mobile_order_base(self,token):
        url = "http://api.dev.test.520czj.com/mobile/insuranceorderbase"
        req = urllib2.Request(url)
        req.add_header('token', token)
        print token
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())['data']

    def get(self):
        user = self.get_current_user()
        data = self.get_mobile_order_base(user.token)
        logging.info(simplejson.dumps(data))
        insurance_message = simplejson.dumps(data['insurance_message'])
        driverDutyI = simplejson.dumps(['不投']+data['driverDutyI'])
        passengerDutyI = simplejson.dumps(['不投']+data['passengerDutyI'])
        scratchI = simplejson.dumps(['不投']+data['scratchI'])
        thirdDutyI = simplejson.dumps(['不投']+data['thirdDutyI'])
        self.render('weixin/insurance_order_items.html',insurance_message=insurance_message,
                    driverDutyI=driverDutyI, passengerDutyI=passengerDutyI,
                    scratchI=scratchI, thirdDutyI=thirdDutyI,selectinsurance='中华联合')

@route(r'/insurance_order_new', name='wx_insurance_order_new')  # 保险下单选择地址优惠方式页面
class InsuranceOrderNewHandler(WXBaseHandler):
    def get_mobile_order_base(self,token):
        url = "http://api.dev.test.520czj.com/mobile/insuranceorderbase"
        req = urllib2.Request(url)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())['data']

    def get(self):
        i_name = self.get_argument('i_name','')
        user = self.get_current_user()
        data = self.get_mobile_order_base(user.token)
        logging.info(simplejson.dumps(data))
        address = {}
        address["delivery_address"]=data["delivery_address"]
        address["delivery_city"]= data["delivery_city"]
        address["delivery_district"]=data["delivery_district"]
        address["delivery_province"]=data["delivery_province"]
        address["delivery_tel"]=data["delivery_tel"]
        address["delivery_to"]=data["delivery_to"]
        insurance_message = data['insurance_message']
        insurance_policy = None
        for item in insurance_message:
            if item['name'] == i_name:
                insurance_policy = item['rake_back']

        self.render('weixin/insurance_order_new.html', address=address, rake_back=insurance_policy,token=user.token)

@route(r'/wxapi/insurance_order_new', name='wxapi_insurance_order_new')  # wxapi 创建保险订单
class WXApiInsuranceOrderNewHandler(WXBaseHandler):
    def post_mobile_insurnace_order_new(self,token):
        url = "http://api.dev.test.520czj.com/mobile/newinsuranceorder"
        logging.info(self.request.body)
        req = urllib2.Request(url,self.request.body)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return response.read()

    def post(self):
        user = self.get_current_user()
        data = self.post_mobile_insurnace_order_new(user.token)
        logging.info(data)
        self.write(data)


@route(r'/insurance_order_success/(\d+)', name='wx_insurance_order_success')  # html 保险下单成功提示页面
class InsuranceOrderSuccessHandler(WXBaseHandler):
    def get(self,id):
        self.render('weixin/insurance_order_success.html',id=id)

@route(r'/wxapi/insurance_orders', name='wxapi_insurance_orders')  # html 保险订单列表
class InsuranceOrdersHandler(WXBaseHandler):
    def get_mobile_mine(self,token,index,type):
        url = "http://api.dev.test.520czj.com/mobile/insuranceorder?index=%s&type=%s"%(index,type)
        req = urllib2.Request(url)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())

    def get(self):
        index = self.get_argument('index',1)
        type = self.get_argument('type','all')
        user = self.get_current_user()
        data = self.get_mobile_mine(user.token,index,type)
        logging.info(data)
        self.write(simplejson.dumps(data))

@route(r'/insurance_orders', name='wx_insurance_orders')  # html 保险订单列表
class InsuranceOrdersHandler(WXBaseHandler):
    def get(self):
        active = self.get_argument('active','all')
        self.render('weixin/insurance_orders.html',active=active)

@route(r'/insurance_order_detail/(\d+)', name='wx_insurance_order_detail')  # html 保险订单详情
class InsuranceOrderDetailHandler(WXBaseHandler):
    def get_mobile_insurance_order_detail(self,token,id):
        url = "http://api.dev.test.520czj.com/mobile/insuranceorderdetail?id=%s"%(id)
        req = urllib2.Request(url)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())

    def get(self,id):
        user = self.get_current_user()
        data = self.get_mobile_insurance_order_detail(user.token,id)
        logging.info(data)
        self.render('weixin/insurance_order_detail.html',data=data['data'])



@route(r'/insurance_order_price', name='wx_insurance_order_price')  # html 保险订单历史报价方案
class InsuranceOrderPriceHandler(WXBaseHandler):
    def get_mobile_insurance_order_price(self,token,id):
        url = "http://api.dev.test.520czj.com/mobile/insurance_method?id=%s"%(id)
        req = urllib2.Request(url)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())

    def get(self,id):
        user = self.get_current_user()
        data = self.get_mobile_insurance_order_price(user.token,id)
        logging.info(data)
        self.render('weixin/insurance_order_price.html',data=data['data'])


@route(r'/pay_detail', name='wx_pay_detail')  # html 微信公众号支付详情页面
class PayDetailHandler(WXBaseHandler):
    def get(self):
        payinfo = Qrcode_pub().getPayQrcode(self.__create_nonce_str(), '车装甲微信测试付款', int(1 * 100))
        self.render('weixin/pay_detail.html', payinfo=payinfo)

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
        state = self.get_argument('state','0')
        parameters = state.replace('00douhao00',',')
        logging.info(parameters)
        parameters = parameters.split(',')

        store_id = parameters[0]
        tourl = parameters[1].replace('00xiegang00','/')
        openid,_ = self.get_access_token_from_code(code)
        access_token = self.get_access_token()
        userinfo = self.get_user_info(access_token,openid)
        logging.info({'url':'/wxapi/login','code':code,'openid':openid,'accesstoken':access_token,'userinfo':userinfo})
        users = User.select().where(User.openid == openid)
        if users.count() >= 1:
            user = users[0]
        else:
            if store_id=='0':
                self.render('weixin/tips.html')
                return
            nickname = '微信注册用户'
            if userinfo.has_key('nickname'):
                nickname = userinfo['nickname']
            self.render('weixin/login.html',storeid=store_id,nickname=nickname,openid=openid,subscribe=userinfo['subscribe'])
            return

        self.session['user'] = user
        self.session.save()
        token = user.token
        if token:
            data = self.application.memcachedb.get(token)
            if data is None:
                token = setting.user_token_prefix + str(uuid.uuid4())
        else:
            token = setting.user_token_prefix + str(uuid.uuid4())
        user.token = token
        user.save()
        self.application.memcachedb.set(token, str(user.id), setting.user_expire)
        if userinfo['subscribe'] == 1:
            # 已经关注条个人中心
            self.redirect(tourl)
        else:
            # 未关注太跳关注引导
            self.render('weixin/focus_guide.html')

@route(r'/register', name='wx_register')  # html 登录
class RegisterHandler(BaseHandler):
    def create_user(self, openid, mobile, nickname, store_id=0):
        try:
            user = User.get(mobile=mobile)
            user.openid = openid
            user.role += 'W'
            user.save()
            return user
        except Exception:
            try:
                logging.error(traceback.format_exc())
                user = User()
                user.store = int(store_id)
                user.truename = nickname
                user.token = setting.user_token_prefix + str(uuid.uuid4())
                user.mobile = mobile
                user.openid = openid
                user.password = user.create_password('123456')  # 微信用户默认密码：123456
                user.role = 'W'

                user.signuped = int(time.time())
                user.save()
                return user
            except Exception:
                logging.error(traceback.format_exc())
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
        self.application.memcachedb.set(user.token, str(user.id), setting.user_expire)
        if subscribe == '1':
            # 已经关注条个人中心
            self.redirect('/mine')
        else:
            # 未关注太跳关注引导
            self.redirect('https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzIyNDMyODk2NQ==&scene=124#wechat_redirect')

@route(r'/mine', name='wx_mine')  # html 会员中心
class MineHandler(WXBaseHandler):
    def get_mobile_mine(self, token):
        url = "http://api.dev.test.520czj.com/mobile/mine"
        req = urllib2.Request(url)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())['data']

    def get(self):
        user = self.get_current_user()
        data = self.get_mobile_mine(user.token)
        logging.info(data)
        self.render('weixin/mine.html', mine=data)

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
    def get_mobile_address(self,token):
        url = "http://api.dev.test.520czj.com/mobile/receiveraddress"
        req = urllib2.Request(url)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())['data']

    def get(self):
        user = self.get_current_user()
        address = self.get_mobile_address(user.token)
        logging.info(address)

        self.render('weixin/user_address.html',address=address)

@route(r'/user_address_detail/(\d+)', name='wx_user_address_detail')  # html 编辑地址
class UserAddressDetailHandler(WXBaseHandler):
    def get(self,store_address_id):
        add_id = store_address_id
        if add_id:
            address = StoreAddress.get(id=int(add_id))
        else:
            address = None
        self.render('weixin/user_address_detail.html',address=address)

    def post(self):
        user = self.get_current_user()
        store_address_id = self.get_argument('store_address_id', None)
        receiver = self.get_argument('receiver', None)
        mobile = self.get_argument('mobile', None)
        province = self.get_argument('province', None)
        city = self.get_argument('city', None)
        region = self.get_argument('district', None)
        address = self.get_argument('address', None)
        is_default = int(self.get_argument('is_default', 0))
        created = int(time.time())

        if is_default:
            for store_address in user.store.addresses:
                if store_address.is_default:
                    store_address.is_default = 0
                    store_address.save()

        if store_address_id:
            sa = StoreAddress.get(id=store_address_id)
            sa.is_default = is_default
            if receiver:
                sa.name = receiver
            if mobile:
                sa.mobile = mobile
            if province:
                sa.province = province
            if city:
                sa.city = city
            if region:
                sa.region = region
            if address:
                sa.address = address
            sa.save()
        else:
            StoreAddress.create(store=user.store, province=province, city=city, region=region, address=address,
                                name=receiver, mobile=mobile, is_default=is_default, create_by=user, created=created)
        self.redirect('/user_address')

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
