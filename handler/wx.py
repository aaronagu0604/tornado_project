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
import lib.payment.ali_app_pay as alipay
import hashlib
import setting
from lib.mqhelper import create_msg

appid = 'wxf23313db028ab4bc'
secret = '8d75a7fa77dc0e5b2dc3c6dd551d87d6'

'''                   
https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxf23313db028ab4bc&redirect_uri=http%3A%2F%2Fwx.dev.520czj.com%2Fwxapi%2Flogin&response_type=code&scope=snsapi_base&state=1#wechat_redirect
'''
# -----------------------------------------------微信配置----------------------------------------------------------------
@route(r'/', name='wx root') # 根域名重定向
class RootHandler(WXBaseHandler):
    def get(self):
        self.redirect('/index')

# --------------------------------------------------首页----------------------------------------------------------------
@route(r'/signature', name='wx signature') # 公众号服务器验证
class Signature(BaseHandler):
    def get(self):
        token = 'wxczjplateform'
        signature = self.get_argument('signature','')
        timestamp = self.get_argument('timestamp','')
        nonce = self.get_argument('nonce','')
        echostr = self.get_argument('echostr','')

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
        url = "http://api.520czj.com/mobile/home"
        req = urllib2.Request(url)
        req.add_header('token',token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())['data']

    def get(self):
        user = self.get_current_user()
        data = self.get_mobile_home_data(user.token)
        logging.info(data)
        banner = data['banner']
        for i in banner:
            i['link'] = i['link'].replace('czj://', '/')
        insurance = []
        for item in data['category']:
            if item['title'] == '保险业务':
                insurance = item['data']
        for i in insurance:
            index = i['link'].rfind('/')
            i['link'] = i['link'][:index].replace('czj://','/')
        msg = data['last_unread_price']
        msg['link'] = msg['link'][5:]
        self.render('weixin/index.html',banner=banner, insurance=insurance,msg=msg,tab_on='index')

# -----------------------------------------------创建保险流程------------------------------------------------------------
@route(r'/insurance/(\d+)', name='wx_insurance')  # 保险公司详情页面
class InsuranceHandler(WXBaseHandler):
    def get(self,id):
        i_id = int(id)
        insurance = Insurance.get(id = i_id)
        self.render('weixin/insurance.html',insurance=insurance)

@route(r'/insurance_order_base/(\d+)', name='wx_insurance_order_base')  # 保险订单上传个人信息页面
class InsuranceOrderBaseHandler(WXBaseHandler):
    def get(self,insurance):
        if insurance=='0':
            i=Insurance.get(id=13)
        else:
            i = Insurance.get(id=insurance)
        self.render('weixin/insurance_order_base.html',insurance=i, ret = self.get_js_sdk_sign(setting.wxdomanName+'/insurance_order_base/'+insurance))

@route(r'/insurance_order_items', name='wx_insurance_order_items')  # html 保险下单选择保险条目页面
class InsuranceOrderItemsHandler(WXBaseHandler):
    def get_mobile_order_base(self,token):
        url = "http://api.520czj.com/mobile/insuranceorderbase"
        req = urllib2.Request(url)
        req.add_header('token', token)
        print token
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())['data']

    def get(self):
        selectinsurance = self.get_argument('selectinsurance','')
        i = Insurance.get(name=selectinsurance)
        createprice = self.get_argument('createprice',0)

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
                    scratchI=scratchI, thirdDutyI=thirdDutyI,selectinsurance=i.name,
                    createprice=createprice)

@route(r'/insurance_order_new', name='wx_insurance_order_new')  # 保险下单选择地址优惠方式页面
class InsuranceOrderNewHandler(WXBaseHandler):
    def get_mobile_order_base(self,token):
        url = "http://api.520czj.com/mobile/insuranceorderbase"
        req = urllib2.Request(url)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())['data']

    def get(self):
        i_name = self.get_argument('i_name','')
        user = self.get_current_user()
        data = self.get_mobile_order_base(user.token)
        logging.info(simplejson.dumps(data))
        hasservicecard=False
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

        self.render('weixin/insurance_order_new.html', address=address, rake_back=insurance_policy,token=user.token,hasservicecard=hasservicecard)

@route(r'/wxapi/insurance_order_new', name='wxapi_insurance_order_new')  # wxapi 创建保险订单
class WXApiInsuranceOrderNewHandler(WXBaseHandler):
    def post_mobile_insurnace_order_new(self,token):
        url = "http://api.520czj.com/mobile/newinsuranceorder"
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
    def get_mobile_mine(self,token,index,type,platform):
        url = "http://api.520czj.com/mobile/insuranceorder?index=%s&type=%s&platform=%s"%(index,type,platform)
        req = urllib2.Request(url)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())

    def get(self):
        index = self.get_argument('index',1)
        type = self.get_argument('type','all')
        platform = self.get_argument('platform','')
        user = self.get_current_user()
        data = self.get_mobile_mine(user.token,index,type,platform)
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
        url = "http://api.520czj.com/mobile/insuranceorderdetail?id=%s"%(id)
        req = urllib2.Request(url)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())

    def get(self,id):
        user = self.get_current_user()
        data = self.get_mobile_insurance_order_detail(user.token,id)
        logging.info(data)
        self.render('weixin/insurance_order_detail.html',data=data['data'],ret = self.get_js_sdk_sign(setting.wxdomanName+'/insurance_order_detail/'+id))

@route(r'/wxapi/insurance_order_create_price', name='wx_insurance_order_create_price')  # html 保险订单重新报价
class InsuranceOrderDetailHandler(WXBaseHandler):
    def post_mobile_insurance_order_create_price(self,token):
        url = "http://api.520czj.com/mobile/insuranceorderdetail"
        logging.info(self.request.body)
        req = urllib2.Request(url, self.request.body)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return response.read()

    def post(self):
        user = self.get_current_user()
        data = self.post_mobile_insurance_order_create_price(user.token)
        logging.info(data)
        self.write(data)

@route(r'/wxapi/update_insurance_order_img', name='wxapi_update_insurance_order_img')  # 修改保险订单证件图片（保险订单）
class WXApiUpdateInsuranceOrderIMGHandler(WXBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/update_insurance_order_img 12. 修改保险订单证件图片（保险订单）
    @apiDescription 修改保险订单证件图片（保险订单）

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} id 保险订单id
    @apiParam {String} imgurl 图片地址
    @apiParam {String} imgtype 图片类型：icf:身份证前，icb：身份证后，dcf：行驶证前，dcb:行驶证后

    @apiSampleRequest /mobile/update_insurance_order_img
    """

    def post(self):
        result = {'flag': 0, 'msg': '', "data": []}
        io_id = self.get_argument('id', '')
        imgurl = self.get_argument('imgurl', '')
        imgtype = self.get_argument('imgtype','')

        if not (io_id and imgurl and imgtype):
            result['msg'] = u'传入参数异常'
            self.write(simplejson.dumps(result))
            return
        try:
            io = InsuranceOrder.get(id=io_id)
            result['flag'] = 1
            if imgtype == 'icf':
                io.id_card_front = imgurl
                io.icfstatus = 0
            elif imgtype == 'icb':
                io.id_card_back = imgurl
                io.icbstatus = 0
            elif imgtype == 'icof':
                io.id_card_front_owner = imgurl
                io.icfostatus = 0
            elif imgtype == 'icob':
                io.id_card_back_owner = imgurl
                io.icbostatus = 0
            elif imgtype == 'dcf':
                io.drive_card_front = imgurl
                io.dcfstatus = 0
            elif imgtype == 'dcb':
                io.drive_card_back = imgurl
                io.dcbstatus = 0
            else:
                result['flag'] = 0
                result['msg'] = u'图片类型不匹配'
            io.save()
        except Exception, e:
            result['msg'] = u'订单不存在'

        self.write(simplejson.dumps(result))

@route(r'/insurance_order_price/(\d+)', name='wx_insurance_order_price')  # html 保险订单历史报价方案
class InsuranceOrderPriceHandler(WXBaseHandler):
    def get_mobile_insurance_order_price(self,token,id):
        url = "http://api.520czj.com/mobile/insurance_method?id=%s"%(id)
        req = urllib2.Request(url)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())

    def get(self,id):
        user = self.get_current_user()
        data = self.get_mobile_insurance_order_price(user.token,id)
        logging.info(data)
        self.render('weixin/insurance_order_price.html',data=data['data'])

@route(r'/pay_detail/(\d+)', name='wx_pay_detail')  # html 微信公众号支付详情页面
class PayDetailHandler(WXBaseHandler):
    def get(self,id):
        type = self.get_argument('type',0)
        if type=='wxqrcode':
            typestr = '微信'
        else:
            typestr = '支付宝'
        io = InsuranceOrder.get(id=int(id))
        log = u'车装甲保单'
        if io.status == 1:  # 保单支付
            log += u'支付'
        elif io.status in [2, 3] and io.current_order_price.append_refund_status == 1:  # 保单补款
            log += u'补款'
        if type=='wxqrcode':
            payinfo = Qrcode_pub().getPayQrcode(io.ordernum, log, int(io.current_order_price.total_price * 100))
        else:
            payinfo = pay_info = alipay.get_alipay_qrcode(io.current_order_price.total_price, log, log, io.ordernum)

        self.render('weixin/pay_detail.html', payinfo=payinfo,typestr=typestr)

# -----------------------------------------------第三方登录：微信---------------------------------------------------------
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

        user_id = parameters[0]
        tourl = parameters[1].replace('00xiegang00','/')
        openid,_ = self.get_access_token_from_code(code)
        access_token = self.get_access_token()
        userinfo = self.get_user_info(access_token,openid)
        logging.info({'url':'/wxapi/login','code':code,'openid':openid,'accesstoken':access_token,'userinfo':userinfo})
        users = User.select().where(User.openid == openid)
        if users.count() >= 1:
            user = users[0]
        else:
            if user_id=='0':
                self.render('weixin/tips.html')
                return
            nickname = '微信注册用户'
            if userinfo.has_key('nickname'):
                nickname = userinfo['nickname']
            self.render('weixin/login.html',user_id=user_id,nickname=nickname,openid=openid,subscribe=userinfo['subscribe'])
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
            self.redirect('https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzIyNDMyODk2NQ==&scene=124#wechat_redirect')

@route(r'/register', name='wx_register')  # html 登录
class RegisterHandler(BaseHandler):
    def create_user(self, openid, mobile, nickname, user_id=0):
        try:
            user = User.get(mobile=mobile)
            user.openid = openid
            if user.role.find('W') >=0:
                pass
            else:
                user.role += 'W'
            token = user.token
            if token:
                data = self.application.memcachedb.get(token)
                if data is None:
                    token = setting.user_token_prefix + str(uuid.uuid4())
            else:
                token = setting.user_token_prefix + str(uuid.uuid4())
            user.token = token
            user.save()

            return user
        except Exception:
            try:
                logging.error(traceback.format_exc())
                parent_user = User.get(id=int(user_id))
                user = User()
                user.parent_user = parent_user.id
                user.store = parent_user.store.id
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
        user_id = self.get_argument('user_id', 0)
        subscribe = self.get_argument('subscribe', 0)
        user = self.create_user(openid, mobile, nickname, user_id)
        self.session['user'] = user
        self.session.save()
        self.application.memcachedb.set(user.token, str(user.id), setting.user_expire)
        if subscribe == '1':
            # 已经关注条个人中心
            self.redirect('/mine')
        else:
            # 未关注太跳关注引导
            self.redirect('https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzIyNDMyODk2NQ==&scene=124#wechat_redirect')

# -----------------------------------------------个人中心----------------------------------------------------------------
@route(r'/mine', name='wx_mine')  # html 会员中心
class MineHandler(WXBaseHandler):
    def get_mobile_mine(self, token):
        url = "http://api.520czj.com/mobile/mine?platform=wx_b"
        req = urllib2.Request(url)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())['data']

    def get(self):
        user = self.get_current_user()
        data = self.get_mobile_mine(user.token)
        logging.info(data)
        self.render('weixin/mine.html', mine=data,tab_on='mine')

@route(r'/user_address', name='wx_user_address')  # html 收货地址
class UserAddressHandler(WXBaseHandler):
    def get_mobile_address(self,token):
        url = "http://api.520czj.com/mobile/receiveraddress"
        req = urllib2.Request(url)
        req.add_header('token', token)
        response = urllib2.urlopen(req)
        return simplejson.loads(response.read())['data']

    def get(self):
        user = self.get_current_user()
        address = self.get_mobile_address(user.token)
        logging.info(address)
        logging.info(user.id)

        self.render('weixin/user_address.html',address=address,user_id=user.id)

@route(r'/user_address_detail/(\d+)', name='wx_user_address_detail')  # html 编辑地址
class UserAddressDetailHandler(WXBaseHandler):
    def get(self,store_address_id):
        add_id = int(store_address_id) if store_address_id!='0' else 0
        if add_id:
            address = StoreAddress.get(id=add_id)
            user_id = self.get_current_user().id
        else:
            address = None
            user_id = None
        self.render('weixin/user_address_detail.html',address=address,user_id=user_id)

    def post(self,store_address_id):
        user = self.get_current_user()
        receiver = self.get_argument('receiver', None)
        mobile = self.get_argument('mobile', None)
        province = self.get_argument('province', None)
        city = self.get_argument('city', None)
        region = self.get_argument('region', None)
        address = self.get_argument('address', None)
        is_default = self.get_argument('is_default', None)
        created = int(time.time())

        if is_default == 'on':
            is_default = 1
            for store_address in user.store.addresses:
                if store_address.is_default:
                    store_address.is_default = 0
                    store_address.save()
        else:
            is_default = 0

        if store_address_id!='0':
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

@route(r'/delete_address/(\d+)', name='wx_delete_user_address_detail')  # html 删除地址
class DeleteUserAddressDetailHandler(WXBaseHandler):
    def get(self,store_address_id):
        add_id = int(store_address_id) if store_address_id!='0' else 0
        if add_id:
            StoreAddress.delete().where(StoreAddress.id == add_id).execute()

        self.redirect('/user_address')

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

@route(r'/car_service_cards', name='wx_car_service_cards') # 汽车保养券列表
class CarServiceCardsHandler(WXBaseHandler):
    def get(self):
        user = self.get_current_user()
        cards = CarServiceCard.select().where(CarServiceCard.user==user.id,CarServiceCard.status==1)
        self.render('weixin/user_car_service_cards.html', cards=cards)

@route(r'/car_service_card_detail/(\d+)', name='wx_car_service_card_detail')  # 汽车保养券详情
class CarServiceCardDetailHandler(WXBaseHandler):
    def get(self,card_id):
        try:
            card = CarServiceCard.get(id=int(card_id))
            user = self.get_current_user()
            #stores = Store.select().where(Store.area_code == user.store.area_code,Store.process_car_service==1)
            stores = Store.select().where(Store.id << [1,2,3])

        except Exception:
            card = None
        self.render('weixin/user_car_service_card_detail.html', card=card,stores = stores)

    def post(self):
        store_id = self.get_body_argument('store_id',None)
        card_id = self.get_body_argument('card_id',None)

        store_id = int(store_id) if store_id else 0
        card_id = int(card_id) if card_id else 0
        if not (store_id and card_id):
            self.render('weixin/result.html',msg='参数有无，无法使用该优惠券')
        try:
            card = CarServiceCard.get(id=card_id)
            if card.status in [-1,2]:
                self.render('weixin/result.html', msg='无效的保养券')
            store = Store.get(id=store_id)
            card.service_store = store.id
            card.status = 2
            card.save()
            sms = {'apptype': 1, 'body': '您收到微信用户：%s的%s,请其提供响应的服务！'%(card.user.mobile,card.type), 'jpushtype': 'alias', 'alias': store.mobile,
                   'images': '', 'extras': {'link': 'czj://car_service_cards'}}
            create_msg(simplejson.dumps(sms), 'jpush')
            self.self.render('weixin/result.html', msg='使用成功，请联系店铺工作人员核对，并享受对应保养服务')
        except CarServiceCard.DoesNotExist:
            self.render('weixin/result.html',msg='保养券不存在')
        except Store.DoesNotExist:
            self.render('weixin/result.html',msg='店铺不存在')

@route(r'/user_store_detail/(\d+)', name='wx_user_store_detail')  # 汽车保养券详情
class UserStoreDetailHandler(WXBaseHandler):
    def get(self, store_id):
        try:
            store = Store.get(id=int(store_id))
        except Exception:
            traceback.print_exc()

        self.render('weixin/user_store_detail.html', store_info=store)

# -----------------------------------------------分享推广----------------------------------------------------------------
@route(r'/share/(\d+)', name='wx_share')  # 分享页面
class ShareHandler(BaseHandler):
    def create_url(self,user_id):
        url = setting.wxdomanName + '/wxapi/login'
        wxlogin_url = "https://open.weixin.qq.com/connect/oauth2/authorize"
        appid = 'wxf23313db028ab4bc'
        redirect_uri = urllib.urlencode({'url': url})
        response_type = "code"
        scope = "snsapi_base"

        state = '%s00douhao00%s'%(str(user_id),'/index'.replace('/','00xiegang00'))
        end = "#wechat_redirect"
        wx_url = wxlogin_url + "?appid=" + appid + "&redirect_uri=" + redirect_uri[4:] + \
                 "&response_type=" + response_type + "&scope=" + scope + "&state=" + state + end

        return wx_url

    def get(self,user_id):
        if user_id=='0':
            user = self.get_current_user()
            if user:
                self.redirect('/share/%d'%user.id)
            else:
                self.render('weixin/tips.html')
            return
        else:
            user = User.get(id=int(user_id))
            from payqrcode import createqrcode
            link = createqrcode(self.create_url(user.id))
            logging.info(link)
            self.render('weixin/share.html',link=link)
