#!/usr/bin/env python
# coding=utf8

import logging
import random
import uuid
import time
import simplejson

import setting
from handler import MobileBaseHandler, require_auth
from lib.mqhelper import create_msg
import lib.payment.ali_app_pay as alipay
from lib.payment.upay import Trade
from lib.payment.wxPay import UnifiedOrder_pub, Qrcode_pub
from lib.route import route
from model import *
from mqProcess.jpushhelper import set_device_info


def get_insurance(area_code):
    items = []
    insurances = InsuranceArea.select(InsuranceArea.insurance). \
        where((InsuranceArea.area_code == area_code) & (InsuranceArea.active == 1)).order_by(InsuranceArea.sort.asc())
    for insurance in insurances:
        items.append({
            'img': insurance.insurance.logo,
            'name': insurance.insurance.name,
            'price': 0,
            'link': 'czj://insurance/%d' % insurance.insurance.id
        })
    return items


"""
    @apiGroup aaaa
    @apiVersion 1.0.0
    @api {get} /mobile 01. 车装甲协议
    @apiDescription 车装甲协议；http://或者https://开头，跳转入webview；czj://开头，进入原生界面，详情如下：

    @apiParam {String} insurance 进入购买保险详情，后跟保险ID（暂时不使用，已改为h5完成），例：czj://insurance/1
    @apiParam {String} insurance_list 进入全部保险列表，例：czj://insurance_list
    @apiParam {String} product 进入商品详情，后跟商品ID（暂时不使用，已改为h5完成），例：czj://product/1
    @apiParam {String} category 进入某分类、某品牌列表，后跟分类、品牌ID，ID为0标识所有；例：czj://category/1/brand/1
    @apiParam {String} insurance_order_list 进入保险订单列表，后跟状态，例：czj://insurance_order_list/0，表示报价列表
    @apiParam {String} insurance_order_detail 进入保险订单详情，后跟保险订单ID，例：czj://insurance_order_detail/1
    @apiParam {String} score_product 进入积分商城，例：czj://score_product
    @apiParam {String} score_product 进入返油政策，例：czj://lube_policy
    @apiParam {String} score_product_detail 进入积分商品详情，例：czj://score_product_detail/1
    @apiParam {String} buyer_product_order_detail 进入采购订单详情，后跟普通订单ID，例：czj://buyer_product_order_detail/1
    @apiParam {String} saler_product_order_detail 进入销售订单详情，后跟普通订单ID，例：czj://saler_product_order_detail/1
    """


@route(r'/mobile', name='mobile_app')
class MobileAppHandler(MobileBaseHandler):
    def get(self):
        self.write("czj api")

    def post(self):
        self.write("czj api post")


@route(r'/mobile/getvcode', name='mobile_getvcode')  # 获取验证码
class MobileGetVCodeAppHandler(MobileBaseHandler):
    """
    @apiGroup auth
    @apiVersion 1.0.0
    @api {post} /mobile/getvcode 01. 获取验证码
    @apiDescription 获取验证码

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} mobile 电话号码（1.3.4不用传）
    @apiParam {Int} flag 验证码类型： 0注册 1忘记密码 2绑定手机号 3提现 4绑定银行卡/支付宝

    @apiSampleRequest /mobile/getvcode
    """

    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        mobile = self.get_body_argument("mobile", None)
        flag = self.get_body_argument("flag", None)
        if flag:
            flag = int(flag)
        else:
            result['msg'] = u'入参错误'
            self.write(simplejson.dumps(result))
            return
        user = self.get_user()
        if flag == 0:
            if user:
                result['msg'] = u'您已经是车装甲会员'
                self.write(simplejson.dumps(result))
                return
        elif flag == 3 or flag == 4:
            if not user:
                result['msg'] = u'您还不是车装甲会员'
                self.write(simplejson.dumps(result))
                return
            mobile = user.mobile
        elif flag == 1:
            if user:
                result['msg'] = u'您已经登录，可以修改密码'
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
                result['msg'] = u'您的操作过于频繁，请稍后再试'
            else:
                try:
                    uservcode.save()
                    logging.info('getvcode: ' + str(uservcode.vcode) + '; flag=' + str(flag))
                    sms = {'mobile': mobile, 'body': str(uservcode.vcode), 'signtype': '1', 'isyzm': 'vcode'}
                    create_msg(simplejson.dumps(sms), 'sms')  # 验证码
                    result['flag'] = 1
                    result['msg'] = u'验证码已发送'
                except Exception, ex:
                    result['msg'] = u'验证码发送失败，请联系400客服处理'
        else:
            result['msg'] = u'手机号格式错误'

        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/checkvcode', name='mobile_checkvcode')  # 检查验证码
class MobileCheckVCodeAppHandler(MobileBaseHandler):
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

    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        mobile = self.get_body_argument('mobile', None)
        vcode = self.get_body_argument('vcode', None)
        flag = self.get_body_argument("flag", None)
        if VCode.check_vcode(mobile, vcode, flag):
            result['flag'] = 1
        else:
            result['msg'] = u'请输入正确的手机号或验证码'
        self.write(simplejson.dumps(result))


@route(r'/mobile/reg', name='mobile_reg')  # 手机端注册
class MobileRegHandler(MobileBaseHandler):
    """
    @apiGroup auth
    @apiVersion 1.0.0
    @api {post} /mobile/reg 03. 商家申请入驻平台
    @apiDescription 商家申请入驻平台

    @apiParam {String} mobile 电话号码
    @apiParam {String} password 密码
    @apiParam {Int}     store_type 门店类型 0其它 1经销商 2社会修理厂（门店）
    @apiParam {String}    referee 推广人编号
    @apiParam {String}    companyName 公司名称
    @apiParam {String}     province 省
    @apiParam {String}     city 市
    @apiParam {String}     district 区
    @apiParam {String}     address 详细地址
    @apiParam {String}     legalPerson 法人代表
    @apiParam {String}     licenseCode 营业执照编号
    @apiParam {String}     licensePic 营业执照图片url
    @apiParam {String}     storePic 门店图片url

    @apiSampleRequest /mobile/reg
    """

    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        mobile = self.get_body_argument("mobile", None)
        password = self.get_body_argument("password", None)
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
        user.truename = legalPerson
        user.mobile = mobile
        user.password = user.create_password(password)
        try:
            user.validate()
            if not (store_type and companyName and province and city and district and address and legalPerson
                    and licenseCode and licensePic and storePic and password):
                raise Exception('申请信息不完整')
            try:
                admin_user = AdminUser.get(code=referee)
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
            user.save()
            StoreAddress.create(store=sid.id, province=province, city=city, region=district, address=address,
                                street='', name=legalPerson, mobile=mobile, created=now, create_by=user.id)
            self.application.memcachedb.set(user.token, str(user.id), setting.user_expire)
            result['data'] = {
                'token': user.token,
                'store_type': store_type,
                'active': 0
            }
            result['flag'] = 1
            result['msg'] = u'注册成功'
        except Exception, ex:
            result['msg'] = ex.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/login', name='mobile_login')  # 手机端登录
class MobileLoginHandler(MobileBaseHandler):
    """
    @apiGroup auth
    @apiVersion 1.0.0
    @api {post} /mobile/login 04. 登录
    @apiDescription 通过手机号密码登录系统

    @apiParam {String} mobile 电话号码
    @apiParam {String} password 密码
    @apiParam {String} jpush 极光推送标识符
    @apiParam {Sting} apptype 应用标识符 1 安卓 2 苹果

    @apiSampleRequest /mobile/login
    """

    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        mobile = self.get_body_argument("mobile", None)
        password = self.get_body_argument("password", None)
        jpushtag = self.get_body_argument('jpush', None)
        apptype = self.get_body_argument('apptype', None)
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
                        if self.application.memcachedb.set(token, str(user.id), setting.user_expire):
                            result['flag'] = 1
                            result['data']['type'] = user.store.store_type
                            result['data']['active'] = user.store.active
                            result['data']['token'] = token
                            result['data']['uid'] = user.id
                            user.updatesignin(token)
                            if jpushtag:
                                code = []
                                area = user.store.area_code
                                while len(area) >= 4:
                                    code.append(area)
                                    area = area[:-4]
                                set_device_info(jpushtag, code, user.mobile)
                        else:
                            result['msg'] = u'登录失败'
                    else:
                        result['msg'] = u"此账户被禁止登录，请联系管理员。"
                else:
                    result['msg'] = u"用户名或密码错误"
            except Exception, e:
                result['msg'] = u"此用户不存在"
        else:
            result['msg'] = u"请输入用户名密码"
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/home', name='mobile_home')  # 首页数据
class MobileHomeHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/home 01. 首页
    @apiDescription app首页数据，
    banner 首页轮播
    insurance  首页保险;
    hot_category 热门分类;
    hot_brand  热销产品;
    recommend  为你推荐;
    last_unread_price 新报价

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/home
    """

    def get(self):
        logging.error('----mobile_home')
        result = {'flag': 0, 'msg': '', "data": {}}
        area_code = self.get_store_area_code()
        user = self.get_user()

        result['data']['login_flag'] = 0
        result['data']['last_unread_price'] = {}
        result['data']['last_unread_price']['show'] = 0
        result['data']['last_unread_price']['msg'] = ''
        result['data']['last_unread_price']['insurance'] = ''
        result['data']['last_unread_price']['time'] = ''
        result['data']['last_unread_price']['link'] = ''
        if user:
            result['data']['login_flag'] = 1
            # 消息通知
            message_list = Message.select().where(Message.store == user.store & Message.status == 0)
            if message_list.count() > 0:
                result['data']['last_unread_price']['show'] = 1
                result['data']['last_unread_price']['msg'] = message_list[0].content
                result['data']['last_unread_price']['type'] = message_list[0].type
                result['data']['last_unread_price']['link'] = message_list[0].link

        # 获取首页banner列表，没有数据时使用西安的数据
        tmp_code = area_code
        banners = self.get_banner(tmp_code)
        while len(banners) == 0 and len(tmp_code) > 4:
            tmp_code = tmp_code[0: -4]
            banners = self.get_banner(tmp_code)
        if len(banners) == 0:
            banners = self.get_banner(self.get_default_area_code())
        result['data']['banner'] = banners

        # 保险
        if user:
            insurances = [{
                'img': store_insurance.insurance.logo,
                'name': store_insurance.insurance.name,
                'price': 0,
                'link': 'czj://insurance/%d' % store_insurance.insurance.id
            } for store_insurance in user.store.store_policy]
        else:
            insurances = self.application.memcachedb.get('insurances_no_login')
            if not insurances:
                insurances = InsuranceArea.get_insurances_link('0027')
                self.application.memcachedb.set('insurances_no_login', insurances)
        result['data']['category'] = [{'title': u'保险业务', 'data': insurances}]

        # 热门分类
        tmp_code = area_code
        categories = self.get_category(tmp_code)
        while len(categories) == 0 and len(tmp_code) > 4:
            tmp_code = tmp_code[0: -4]
            categories = self.get_category(tmp_code)
        if len(categories) == 0:
            categories = self.get_category(self.get_default_area_code())
        result['data']['category'].append({'title': u'热门分类', 'data': categories[:4]})

        # 热销品牌
        tmp_code = area_code
        brands = self.get_brand(tmp_code)
        while len(brands) == 0 and len(tmp_code) > 4:
            tmp_code = tmp_code[0: -4]
            brands = self.get_brand(tmp_code)
        if len(brands) == 0:
            brands = self.get_brand(self.get_default_area_code())
        result['data']['category'].append({'title': u'热销品牌', 'data': brands[:4]})

        # 推荐商品
        tmp_code = area_code
        recommends = self.get_recommend(tmp_code)
        while len(recommends) == 0 and len(tmp_code) > 4:
            tmp_code = tmp_code[0: -4]
            recommends = self.get_recommend(tmp_code)
        if len(recommends) == 0:
            recommends = self.get_recommend(self.get_default_area_code())
        result['data']['category'].append({'title': u'为您推荐', 'data': []})

        # 积分商品
        tmp_code = area_code
        score_product = self.get_score_product(tmp_code)
        while len(score_product) == 0 and len(tmp_code) > 4:
            tmp_code = tmp_code[0: -4]
            score_product = self.get_score_product(tmp_code)
        if len(score_product) == 0:
            score_product = self.get_score_product(self.get_default_area_code())
        result['data']['category'].append({'title': u'积分兑换', 'data': score_product})

        result['flag'] = 1

        self.write(simplejson.dumps(result))
        self.finish()

    def get_banner(self, area_code):
        items = []
        banners = BlockItem.select(BlockItem).join(Block, on=(Block.id == BlockItem.block)). \
            where((Block.tag == 'banner') & (Block.active == 1) & (BlockItem.active == 1) & (
        BlockItem.area_code << [area_code, '', None])). \
            order_by(BlockItem.sort.asc())
        for p in banners:
            items.append({
                'img': p.img,
                'name': p.name,
                'price': 0,
                'link': p.link
            })
        return items

    def get_category(self, area_code):
        items = []
        if isinstance(area_code, list):
            ft = StoreProductPrice.area_code << area_code
        else:
            ft = StoreProductPrice.area_code == area_code
        spps = Category.select(). \
            join(Product, on=Product.category == Category.id). \
            join(ProductRelease, on=ProductRelease.product == Product.id). \
            join(StoreProductPrice, on=StoreProductPrice.product_release == ProductRelease.id). \
            where(ft)
        clist = []
        for item in spps:
            if item.id not in clist:
                clist.append(item.id)
                items.append({
                    'img': item.img_m,
                    'name': item.name,
                    'price': 0,
                    'link': 'czj://category/%s' % item.id
                })
        return items

    def get_brand(self, area_code):
        items = []
        if isinstance(area_code, list):
            ft = StoreProductPrice.area_code << area_code
        else:
            ft = StoreProductPrice.area_code == area_code
        spps = Brand.select(Brand.id.alias('id'),Brand.logo.alias('logo'),Brand.name.alias('name'),Product.category.alias('cid')). \
            join(Product, on=Product.brand == Brand.id). \
            join(ProductRelease, on=ProductRelease.product == Product.id). \
            join(StoreProductPrice, on=StoreProductPrice.product_release == ProductRelease.id). \
            where(ft).tuples()
        blist = []
        for id,logo,name,cid in spps:
            if id not in blist:
                blist.append(id)
                items.append({
                    'img': logo,
                    'name': name,
                    'price': 0,
                    'link': 'czj://category/%d/brand/%d' %(cid, id)
                })

        return items

    def get_recommend(self, area_code):
        items = []
        if isinstance(area_code, list):
            ft = StoreProductPrice.area_code << area_code
        else:
            ft = StoreProductPrice.area_code == area_code
        spps = Product.select(Product.id.alias('id'),
                              Product.name.alias('name'),
                              Product.cover.alias('cover'),
                              StoreProductPrice.price.alias('price'),
                              StoreProductPrice.score.alias('score'),
                              Store.name.alias('sname')). \
            join(ProductRelease, on=(ProductRelease.product == Product.id)). \
            join(Store, on=(Store.id == ProductRelease.store)). \
            join(StoreProductPrice, on=(StoreProductPrice.product_release == ProductRelease.id)). \
            where(ft).tuples()
        for id, name, cover, price, score, sname in spps:
            items.append({
                'img': cover,
                'name': name,
                'price': price,
                'score': score,
                'link': 'czj://product/%d' % id,
                'is_score': 0,
                'storeName': sname
            })
        return items[:6]

    def get_score_product(self, area_code):
        items = []
        if isinstance(area_code, list):
            ft = StoreProductPrice.area_code << area_code
        else:
            ft = StoreProductPrice.area_code == area_code
        spps = Product.select(Product.id.alias('id'),
                              Product.name.alias('name'),
                              Product.cover.alias('cover'),
                              StoreProductPrice.price.alias('price'),
                              StoreProductPrice.score.alias('score'),
                              Store.name.alias('sname')). \
            join(ProductRelease, on=(ProductRelease.product == Product.id)). \
            join(Store, on=(Store.id == ProductRelease.store)). \
            join(StoreProductPrice, on=(StoreProductPrice.product_release == ProductRelease.id)). \
            where(ft, ProductRelease.is_score == 1).tuples()
        for id, name, cover, price, score, sname in spps:
            items.append({
                'img': cover,
                'name': name,
                'price': price,
                'score': score,
                'link': 'czj://score_product_detail/%d' % id,
                'is_score': 1,
                'storeName': sname
            })
        return items[:6]


@route(r'/mobile/get_bank_name', name='GetBankName')  # 用户获取银行卡名称
class MobileGetBankNameHandler(MobileBaseHandler):
    """
    @apiGroup auth
    @apiVersion 1.0.0
    @api {get} /mobile/get_bank_name 05. 获取银行卡名称
    @apiDescription 获取银行卡名称

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} bank_number 银行卡号

    @apiSampleRequest /mobile/get_bank_name
    """

    def get(self):
        result = {'flag': 0, 'data': {'id': 0, 'bank_name': ''}, 'msg': ''}
        bank_number = self.get_argument('bank_number', None)

        rows = BankCard.select().where(BankCard.card_bin == db.fn.LEFT(bank_number, BankCard.bin_digits))
        if rows.count() > 0:
            u = rows[0]
            result['data'] = {
                'id': u.id,
                'bank_name': u.bank_name
            }
            result['flag'] = 1

        self.write(simplejson.dumps(result))


@route(r'/mobile/hot_search', name='mobile_hot_search')  # 热搜
class MobileHotSearchHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/hot_search 02. 热搜
    @apiDescription 热搜关键字获取

    @apiSampleRequest /mobile/hot_search
    """

    def get(self):
        result = {'flag': 0, 'data': [], 'msg': ''}

        rows = HotSearch.select().where(HotSearch.status == 1).order_by(HotSearch.quantity.desc()).limit(4)
        if rows.count() > 0:
            result['data'] = [hot_search.keywords for hot_search in rows]
            result['flag'] = 1
        else:
            result['msg'] = u'暂无'

        self.write(simplejson.dumps(result))


# -----------------------------------------------------普通商品---------------------------------------------------------
@route(r'/mobile/discover', name='mobile_discover')  # 发现
class MobileDiscoverHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/discover 03. 发现
    @apiDescription 发现

    @apiHeader {String} token 用户登录凭证
    @apiSampleRequest /mobile/discover
    """

    def get(self):
        result = {'flag': 1, 'msg': '', 'data': []}
        area_code = self.get_store_area_code()

        if isinstance(area_code, list):
            ft = StoreProductPrice.area_code << area_code
        else:
            ft = StoreProductPrice.area_code == area_code
        productlist = Product.select(Product.category.alias('cid'), Product.brand.alias('bid')). \
            join(ProductRelease, on=(ProductRelease.product == Product.id)). \
            join(Store, on=(Store.id == ProductRelease.store)). \
            join(StoreProductPrice, on=(StoreProductPrice.product_release == ProductRelease.id)). \
            where(ft).tuples()
        cbs = {}

        cbs = {}
        for cid, bid in productlist:
            if cid not in cbs.keys():
                cbs[cid] = []
            else:
                if bid not in cbs[cid]:
                    cbs[cid].append(bid)
                else:
                    pass
        tmp_num = 0
        for cid in cbs.keys():
            if tmp_num == 0:
                tmp_ad = {'img': 'http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png', 'link': ''}
            elif tmp_num == 1:
                tmp_ad = {'img': 'http://img.520czj.com/image/2017/02/22/server1_20170222162422ShymVuXKNglbcJCrIvLFAoEO.png', 'link': ''}
            tmp_num += 1
            category = Category.get(id=cid)
            result['data'].append({
                'name': category.name,
                'cid': category.id,
                'ads': tmp_ad,
                'subs': [{
                    'name': u'热销品牌',
                    'subs': [{'img': brand.logo,
                              'name': brand.name,
                              'price': 0,
                              'link': 'czj://category/%d/brand/%d' % (cid, brand.id)} for brand in
                             Brand.select().where(Brand.id << cbs[cid]) if brand.hot == 1]
                },
                    {
                        'name': u'不太热销的',
                        'subs': [{'img': brand.logo,
                                  'name': brand.name,
                                  'price': 0,
                                  'link': 'czj://category/%d/brand/%d' % (cid, brand.id)} for brand in
                                 Brand.select().where(Brand.id << cbs[cid]) if brand.hot != 1]
                    }
                ]
            })

        # 保险商城
        area_code = self.get_store_area_code()
        result['data'].append({
            'name': u'保险商城',
            'cid': 0,
            'subs': [{
                'name': u'热门保险',
                'subs': InsuranceArea.get_insurances_link(area_code)[:3]
            }, {
                'name': u'不太热门保险',
                'subs': InsuranceArea.get_insurances_link(area_code)[3:]
            }],
            'ads': {'img': 'http://img.520czj.com/image/category/20170104184002.jpg', 'link': ''}
        })

        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/filter', name='mobile_filter')  # 普通商品筛选界面
class MobileFilterHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/filter 04. 普通商品筛选界面
    @apiDescription 普通商品筛选界面，未登陆使用西安code
    @apiHeader {String} token 用户登录凭证
    @apiParam {Int} flag 1品牌 2分类
    @apiParam {Int} id 品牌或者分类ID
    @apiSampleRequest /mobile/filter
    """

    def getCategoryAttribute(self, bc, cid):
        '''
        attributeList = [{
            'id': id,
            'name': '容量',
            'values': [{
                'id': 1,
                'name': 1L
            },{
                'id': 1,
                'name': 3L
            }]
        },{}]
        '''
        attributeList = []
        for attribute in bc.category.attributes:
            tmpList = []
            for item in attribute.items:
                tmpList.append({
                    'id': item.id,
                    'name': item.name
                })
            attributeList.append({
                'cid': cid,
                'aid': attribute.id,
                'name': attribute.name,
                'ename': attribute.ename,
                'values': tmpList
            })
        return attributeList

    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        id = self.get_argument("id", None)
        flag = self.get_argument("flag", None)

        if not (flag and id):
            result['msg'] = u'分类或品牌不能为空'
            self.write(simplejson.dumps(result))
            return
        else:
            flag = int(flag)
            id = int(id)

        result['data']['filter_items'] = []
        if flag == 2:  # 分类一定
            brandCategorys = BrandCategory.select().where(BrandCategory.category == id)
            if brandCategorys.count() > 0:
                result['data']['filter_items'].append({
                    'cid': id,
                    'ename': 'pp',
                    'aid': 0,
                    'name': u'品牌',
                    'values': [{'id': bc.brand.id, 'name': bc.brand.name} for bc in brandCategorys]
                })
                result['data']['filter_items'] += self.getCategoryAttribute(brandCategorys[0],
                                                                            brandCategorys[0].category.id)
            else:
                result['msg'] = u'未查到该分类'
                self.write(simplejson.dumps(result))
                return
        elif flag == 1:  # 品牌一定
            brandCategorys = BrandCategory.select().where(BrandCategory.brand == id)
            if brandCategorys.count() > 0:
                result['data']['filter_items'].append({
                    'cid': id,
                    'ename': 'pp',
                    'aid': 0,
                    'name': u'品牌',
                    'values': [{'id': brandCategorys[0].brand.id, 'name': brandCategorys[0].brand.name}]
                })
                for bc in brandCategorys:
                    result['data']['filter_items'] += self.getCategoryAttribute(bc, bc.category.id)
            else:
                result['msg'] = u'未查到该品牌'
                self.write(simplejson.dumps(result))
                return
        else:
            result['msg'] = u'输入参数错误'
            self.write(simplejson.dumps(result))
            return

        result['flag'] = 1
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/discoverproducts', name='mobile_discover_products')  # 商品列表
class MobileDiscoverProductsHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/discoverproducts 05. 商品列表
    @apiDescription 商品列表，未登陆使用西安code

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} keyword 搜索关键字
    @apiParam {String} sort 价格排序 1正序， 2逆序； 默认为1  销量排序 3正序， 4逆序； 默认2
    @apiParam {String} category 分类ID， 多选, 例：1,2,3
    @apiParam {String} brand 品牌ID组合， 多选, 例：1,2,3
    @apiParam {String} attribute 属性ID组合, 多选, 例： 1,2,3
    @apiParam {Int} index 页数

    @apiSampleRequest /mobile/discoverproducts
    """

    def getProductList(self, keyword, sort, category, brand, attribute, index, area_code):
        productList = []
        ft = (Product.active == 1)
        # 根据规格参数搜索
        if category and attribute:
            ft1 = ft2 = None
            c = Category.get(id=category)
            for i, a in enumerate(c.attributes):
                cais = CategoryAttributeItems.select().where(
                    (CategoryAttributeItems.category_attribute == a.id) & (CategoryAttributeItems.id << attribute))
                for cai in cais:
                    ft2 = (ProductAttributeValue.value == cai.name) if not ft2 else ft2 | (
                    ProductAttributeValue.value == cai.name)
                if ft2:
                    ft1 = ft2 if not ft1 else ft1 & ft2
            if ft1:
                products = Product.select().join(ProductAttributeValue).where(ft1)
                pids = [product.id for product in products]
                ft = (Product.id << pids)
                # for i, f in enumerate(fts):
                #     if i == 0:
                #         products = Product.select().join(ProductAttributeValue).where(f)
                #     else:
                #         products = Product.select().join(ProductAttributeValue).where(f & (Product.id << pids))
                #     pids = [product.id for product in products]
        elif category:
            ft &= (Product.category == category)
        ft &= ((StoreProductPrice.price > 0) & (StoreProductPrice.active == 1) & (ProductRelease.active == 1))
        if keyword:
            keyword = '%' + '%'
            ft &= (Product.name % keyword)
        if brand:
            ft &= (Product.brand << brand)
        if len(area_code) == 12:  # 门店可以购买的范围仅仅到区县
            ft &= (((db.fn.Length(StoreProductPrice.area_code) == 4) & (StoreProductPrice.area_code == area_code[:4])) |
                   ((db.fn.Length(StoreProductPrice.area_code) == 8) & (StoreProductPrice.area_code == area_code[:8])) |
                   (StoreProductPrice.area_code == area_code))
        elif len(area_code) == 8:  # 门店可以购买的范围到市级
            ft &= (((db.fn.Length(StoreProductPrice.area_code) == 4) & (StoreProductPrice.area_code == area_code[:4])) |
                   (StoreProductPrice.area_code == area_code))
        elif len(area_code) == 4:  # 门店可以购买的范围到省级
            ft &= (StoreProductPrice.area_code == area_code)
        products = ProductRelease.select(
            ProductRelease.id.alias('prid'), Product.id.alias('pid'), StoreProductPrice.id.alias('sppid'),
            Product.name.alias('name'), StoreProductPrice.price.alias('price'), Product.unit.alias('unit'),
            ProductRelease.buy_count.alias('buy_count'), Product.cover.alias('cover'),
            Product.resume.alias('resume'), Store.name.alias('sName'), ProductRelease.is_score.alias('is_score')). \
            join(Product, on=(Product.id == ProductRelease.product)). \
            join(StoreProductPrice, on=(StoreProductPrice.product_release == ProductRelease.id)). \
            join(Store, on=(Store.id == ProductRelease.store)).where(ft).dicts()
        # 排序
        if sort == '1':
            products = products.order_by(StoreProductPrice.price.desc())
        elif sort == '2':
            products = products.order_by(StoreProductPrice.price.asc())
        elif sort == '3':
            products = products.order_by(ProductRelease.buy_count.desc())
        elif sort == '4':
            products = products.order_by(ProductRelease.buy_count.asc())
        else:
            products = products.order_by(ProductRelease.sort.desc())
        ps = products.paginate(index, setting.MOBILE_PAGESIZE)
        for p in ps:
            productList.append({
                'prid': p['prid'],
                'pid': p['pid'],
                'sppid': p['sppid'],
                'name': p['name'],
                'price': p['price'],
                'unit': p['unit'] if p['unit'] else '件',
                'buy_count': p['buy_count'],
                'cover': p['cover'],
                'resume': p['resume'],
                'storeName': p['sName'],
                'is_score': p['is_score']
            })

        return productList

    def hot_search_add_keyword(self, keyword):
        if keyword:
            now = int(time.time())
            hss = HotSearch.select().where(HotSearch.keywords == keyword)
            if hss.count() > 0:
                hss[0].quantity += 1
                hss[0].last_time = now
                hss[0].save()
            else:
                HotSearch.create(keywords=keyword, quantity=1, status=0, last_time=now)

    def get(self):
        result = {'flag': 1, 'msg': '', "data": {}}
        keyword = self.get_argument("keyword", None)
        sort = self.get_argument("sort", None)
        category = self.get_argument("category", '')
        brand = self.get_argument("brand", '')
        attribute = self.get_argument("attribute", '')
        index = self.get_argument("index", None)
        index = int(index) if index else 1
        categories = list(set(category.strip(',').split(',')))
        brands = brand.strip(',').split(',') if brand else []
        attributes = attribute.strip(',').split(',') if attribute else []
        area_code = self.get_store_area_code()

        self.hot_search_add_keyword(keyword)
        if len(categories) > 1:
            result['data']['products'] = []
        else:
            result['data']['products'] = self.getProductList(keyword, sort, categories[0], brands, attributes, index,
                                                             area_code)

        result['data']['category'] = ''
        result['data']['brand'] = ''
        if category or brand:
            result['data']['category'] = category
            result['data']['brand'] = brand
        else:
            try:
                if u'油' in keyword or u'仪' in keyword:
                    result['data']['category'] = Product.get(id=result['data']['products'][0]['pid']).category.id
                else:
                    result['data']['brand'] = Product.get(id=result['data']['products'][0]['pid']).brand.id
            except Exception, e:
                pass
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/insurance_list', name='mobile_insurance_list')  # 保险列表
class MobileInsuranceListHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/insurance_list 06. 保险列表
    @apiDescription 保险列表

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/insurance_list
    """

    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        user = self.get_user()
        if user is not None:
            tmp_code = user.store.area_code
            insurances = get_insurance(tmp_code)
            while len(insurances) == 0 and len(tmp_code) > 4:
                tmp_code = tmp_code[0: -4]
                insurances = get_insurance(tmp_code)
            result['data']['insurance'] = insurances
            result['flag'] = 1
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/product', name='mobile_product')  # 产品详情页
class MobileProductHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/product 07. 产品详情页
    @apiDescription 产品详情页,返回html代码; showDetail(): 详情；showMain()：商品；getBusinessTel()：返回商品咨询电话；callPhone()：拨打电话

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} id 产品或门店产品价格ID
    @apiParam {Int} from 当前打开的产品的来源；1从app 2从分享
    @apiParam {Int} price 销售商品；1普通销售商品 2积分商品
    @apiParam {String} platform 平台来源：ios或者android

    @apiSampleRequest /mobile/product
    """

    def get(self):
        id = self.get_argument("id", None)
        spp = StoreProductPrice.get(id=id)
        f = self.get_argument("from", 2)
        type = self.get_argument("price", 2)
        platform = self.get_argument('platform', 'android')
        pics = sorted(spp.product_release.product.pics, key=lambda pic: pic.sort)
        items = [i for i in spp.product_release.product.attributes if i.attribute.active == 1]
        attributes = sorted(items, key=lambda item: item.attribute.sort)
        login = self.get_user() is not None
        product = {'name': spp.product_release.product.name, 'type': type, 'from': f, 'id': id,
                   'price': spp.price, 'pics': pics, 'buy_count': spp.product_release.buy_count,
                   'store': spp.store.name, 'mobile': spp.store.mobile, 'attributes': attributes,
                   'login': login, 'platform': platform,'intro':spp.product_release.product.intro}
        if str(type) == '2':
            product['price'] = spp.score

        self.render('mobile/product.html', product=product)


@route(r'/mobile/insurance', name='mobile_insurance')  # 保险详情页
class MobileInsuranceHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/insurance 08. 保险详情页
    @apiDescription 保险详情页,返回html代码

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} id 保险ID
    @apiParam {Int} type 当前打开的产品的来源；1从app 2从分享

    @apiSampleRequest /mobile/insurance
    """

    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        id = self.get_argument("id", None)
        type = self.get_argument("type", None)
        insurance = Insurance.get(id=id)
        self.render('mobile/insurance.html', insurance=insurance)


@route(r'/mobile/addshopcar', name='mobile_add_shop_car')  # 添加购物车
class MobileAddShopCarHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {post} /mobile/addshopcar 09. 添加购物车
    @apiDescription 添加购物车

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} sppid 地区产品价格ID
    @apiParam {Int} quantity 产品数量

    @apiSampleRequest /mobile/addshopcar
    """

    @require_auth
    def post(self):
        user = self.get_user()
        result = {'flag': 0, 'msg': '', "data": {}}
        sppid = self.get_body_argument("sppid", None)
        quantity = self.get_body_argument("quantity", 1)
        if user and sppid:
            has_product = ShopCart.select().where(
                (ShopCart.store_product_price == sppid) & (ShopCart.store == user.store)).count()
            if has_product > 0:
                result['msg'] = u'该商品已存在'
            else:
                car = ShopCart()
                car.store = user.store
                car.store_product_price = sppid
                car.quantity = quantity
                car.created = int(time.time())
                car.save()
                result['msg'] = u'添加成功'
                result['flag'] = 1
        else:
            result['msg'] = u'传入参数异常'
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/deleteshopcar', name='mobile_delete_shop_car')  # 移出购物车
class MobileDeleteShopCarHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {post} /mobile/deleteshopcar 10. 移出购物车
    @apiDescription 移出购物车

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} sppids 地区产品价格ID集合，如：[1,3,6]

    @apiSampleRequest /mobile/deleteshopcar
    """

    @require_auth
    def post(self):
        user = self.get_user()
        result = {'flag': 0, 'msg': '', "data": {}}
        sppids = simplejson.loads(self.get_body_argument("sppids", '[]'))
        if user and len(sppids) > 0:
            query = ShopCart.delete().where(ShopCart.store == user.store, ShopCart.store_product_price << sppids)
            query.execute()
            result['flag'] = 1
        else:
            result['msg'] = u'传入参数异常'
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/shopcar', name='mobile_shopcar')  # 手机端购物车内容获取
class MobileShopCarHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/shopcar 11. 手机端购物车内容获取
    @apiDescription app  手机端购物车内容获取

    @apiHeader {String} token 用户登录凭证
    @apiParam {Int} index 页数

    @apiSampleRequest /mobile/shopcar
    """

    @require_auth
    def get(self):
        result = {'flag': 1, 'msg': '', "data": [], 'products_count': ''}
        user = self.get_user()
        index = self.get_argument('index', '')
        index = int(index) if index else 1
        saler_store_list = []
        items = user.store.cart_items.order_by(ShopCart.created.desc())
        result['products_count'] = items.count()
        for item in items.paginate(index, setting.MOBILE_PAGESIZE):
            is_sale = (item.store_product_price.active & item.store_product_price.product_release.active &
                       item.store_product_price.product_release.product.active)
            saler_store_id = item.store_product_price.store.id
            if saler_store_id not in saler_store_list:
                saler_store_list.append(saler_store_id)
                result['data'].append({
                    'saler_store_name': item.store_product_price.store.name,
                    'products': [{
                        'sppid': item.store_product_price.id,
                        'prid': item.store_product_price.product_release.id,
                        'pid': item.store_product_price.product_release.product.id,
                        'name': item.store_product_price.product_release.product.name,
                        'price': item.store_product_price.price,
                        'unit': item.store_product_price.product_release.product.unit,
                        'cover': item.store_product_price.product_release.product.cover,
                        'quantity': item.quantity,
                        'is_sale': is_sale
                    }]
                })
            else:
                result['data'][saler_store_list.index(saler_store_id)]['products'].append({
                    'sppid': item.store_product_price.id,
                    'prid': item.store_product_price.product_release.id,
                    'pid': item.store_product_price.product_release.product.id,
                    'name': item.store_product_price.product_release.product.name,
                    'price': item.store_product_price.price,
                    'unit': item.store_product_price.product_release.product.unit,
                    'cover': item.store_product_price.product_release.product.cover,
                    'quantity': item.quantity,
                    'is_sale': is_sale
                })

        self.write(simplejson.dumps(result))
        self.finish()


# -------------------------------------------------------商品/保险订单--------------------------------------------------
def pay_order(payment, total_price, ordernum, log):
    pay_info = ''
    if payment == 1:  # 1支付宝  2微信 3银联 4余额 5积分 6立即支付宝 7立即微信
        pay_info = alipay.get_alipay_string(total_price, log, log, ordernum)
    elif payment == 2:
        pay_info = UnifiedOrder_pub().getPrepayId(ordernum, log, int(total_price * 100))
    elif payment == 3:
        pay_info = Trade().trade(ordernum, total_price)
    elif payment == 6:
        pay_info = alipay.get_alipay_qrcode(total_price, log, log, ordernum)
    elif payment == 7:
        pay_info = Qrcode_pub().getPayQrcode(ordernum, log, int(total_price * 100))
    return pay_info


@route(r'/mobile/orderbase', name='mobile_order_base')  # 创建订单前的获取数据
class MobileOrderBaseHandler(MobileBaseHandler):
    """
    @apiGroup order
    @apiVersion 1.0.0
    @api {get} /mobile/orderbase 01. 创建订单前的获取数据
    @apiDescription 创建订单前的获取数据，传入产品信息，获取用户的默认地址、支付信息等

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} spp_dicts 地区产品价格ID， 格式：[{"quantity":1,"sppid":3},{"quantity":1,"sppid":5}]

    @apiSampleRequest /mobile/orderbase
    """

    @require_auth
    def get(self):
        user = self.get_user()
        result = {'flag': 0, 'msg': '', 'data': {'address': {}, 'store': []}}
        try:
            spp_dicts = simplejson.loads(self.get_argument('spp_dicts'))
            spp_dicts = {int(spp_dict['sppid']): int(spp_dict['quantity']) for spp_dict in spp_dicts}
        except Exception, e:
            result['msg'] = u'入参错误'
            self.write(simplejson.dumps(result))
            return
        if spp_dicts:
            sppids = [key for key in spp_dicts]
            if user is not None:
                for address in user.store.addresses:
                    if address.is_default == 1:
                        result['data']['address']['address_id'] = address.id
                        result['data']['address']['mobile'] = address.mobile
                        result['data']['address']['province'] = address.province
                        result['data']['address']['city'] = address.city
                        result['data']['address']['district'] = address.region
                        result['data']['address']['address'] = address.address
                        result['data']['address']['receiver'] = address.name
                        result['data']['address']['is_default'] = address.is_default
                        break
                else:
                    result['data']['address'] = {}
                result['data']['last_pay_type'] = user.last_pay_type

                stores = []
                product_list = StoreProductPrice.select(). \
                    where((StoreProductPrice.active == 1) & (StoreProductPrice.id << sppids)).order_by(
                    StoreProductPrice.store)
                for product_price in product_list:
                    products = {
                        'sppid': product_price.id,
                        'quantity': spp_dicts[product_price.id],
                        'name': product_price.product_release.product.name,
                        'price': product_price.price,
                        'score': product_price.score,
                        'img': product_price.product_release.product.cover,
                        'attributes': [attribute.value for attribute in
                                       product_price.product_release.product.attributes]
                    }
                    if product_price.store.id not in stores:
                        result['data']['store'].append({
                            'name': product_price.store.name,
                            'store_tel': product_price.store.mobile,
                            'sid': product_price.store.id,
                            'service_tel': setting.COM_TEL,
                            'products': [products]
                        })
                        stores.append(product_price.store.id)
                    else:
                        result['data']['store'][stores.index(product_price.store.id)]['products'].append(products)
                result['flag'] = 1
            else:
                result['msg'] = u'请登录后再购买'
        else:
            result['msg'] = u'请选择购买的产品'
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/neworder', name='mobile_new_order')  # 创建产品订单
class MobileNewOrderHandler(MobileBaseHandler):
    """
    @apiGroup order
    @apiVersion 1.0.0
    @api {post} /mobile/neworder 02. 创建产品订单
    @apiDescription 创建产品订单

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} address 地址ID
    @apiParam {Int} order_type 订单类型  1金钱订单  2积分订单
    @apiParam {Int} is_shop_cart  是否是从购物车购买
    @apiParam {Int} payment 付款方式  1支付宝  2微信 3银联 4余额 5积分
    @apiParam {Float} total_price 订单总价（金钱/积分）
    @apiParam {String} products 产品数据集合，如：[{sid:1, price:119, products:[{sppid:1, quantity:1}]}, ……]；
    sid为店铺ID；price为该店铺的金额；sppid为StoreProductPrice的ID，count为产品数量；服务端将订单按Store拆分为多个SubOrder

    @apiSampleRequest /mobile/neworder
    """

    # 检查商品是否存在and 支付方式and价格传输是否正确
    def check_products_price(self, order_type, total_price, items):
        try:
            db_total_price = 0
            for item in items:
                db_store_price = 0
                for p in item['products']:
                    spp = StoreProductPrice.get(id=p['sppid'])
                    if order_type == 1:
                        db_store_price += (spp.price * int(p['quantity']))
                    elif order_type == 2:
                        db_store_price += (spp.score * int(p['quantity']))
                    else:
                        return False, u'入参错误 order_type'
                if db_store_price != float(item['price']):
                    return False, u'store价格有误'
                db_total_price += db_store_price
            if total_price != db_total_price:
                return False, u'总价有误'
        except Exception, e:
            return False, u'该商品未获取到%s'%e
        return True, '1'

    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        address = self.get_body_argument("address", None)
        order_type = self.get_body_argument("order_type", None)
        payment = self.get_body_argument("payment", None)
        total_price = self.get_body_argument("total_price", None)
        products = self.get_body_argument("products", None)
        is_shop_cart = self.get_body_argument("is_shop_cart", '')
        user = self.get_user()

        if address and payment and total_price and products and user and order_type:
            order_type = int(order_type)
            payment = int(payment)
            items = simplejson.loads(products)
            if order_type == 1:
                total_price = float(total_price)
            elif order_type == 2:
                total_price = int(total_price)
            else:
                result['msg'] = u'支付方式不正确'
                self.write(simplejson.dumps(result))
                return
            check_result, log = self.check_products_price(order_type, total_price, items)
            if not check_result:
                result['msg'] = log
                self.write(simplejson.dumps(result))
                return
            now = int(time.time())
            order_now = int(time.time() * 100)
            order = Order()
            order.user = user
            order.buyer_store = user.store

            address = StoreAddress.get(id=address)
            order.delivery_to = address.name
            order.delivery_tel = address.mobile
            order.delivery_province = address.province
            order.delivery_city = address.city
            order.delivery_region = address.region
            order.delivery_address = address.address

            order.ordered = now
            order.payment = payment
            order.message = ''
            order.order_type = order_type
            order.total_price = total_price if order_type == 1 else 0
            order.total_score = total_price if order_type == 2 else 0
            order.ordernum = 'U' + str(user.id) + 'S' + str(order_now - setting.ORDERBEGIN)
            if order_type == 2 and payment == 5:    # 积分支付
                if user.store.score < total_price:
                    result['msg'] = u"您的积分不足"
                    self.write(simplejson.dumps(result))
                    return
                else:
                    user.store.score -= total_price
                    user.store.save()
                    order.status = 1
                    order.pay_time = now
                    order.save()
                    # 积分消费记录
                    score_record = ScoreRecord()
                    score_record.user = user
                    score_record.store = user.store
                    score_record.type = 1
                    score_record.process_type = 2
                    score_record.process_log = u'积分兑换产品，订单号：' + order.ordernum
                    score_record.created = now
                    score_record.score = total_price
                    score_record.status = 1
                    score_record.save()
            elif payment == 4:  # 余额支付
                if user.store.price < total_price:
                    result['msg'] = u"您的余额不足"
                    self.write(simplejson.dumps(result))
                    return
                else:
                    user.store.price -= total_price
                    user.store.save()
                    order.status = 1
                    order.pay_time = now
                    order.save()
                    money_record = MoneyRecord()
                    money_record.user = user
                    money_record.store = user.store
                    money_record.process_type = 2
                    money_record.process_log = u'购买产品使用余额支付, 订单号：' + order.ordernum
                    money_record.status = 1
                    money_record.money = total_price
                    money_record.apply_time = now
                    money_record.save()
            else:
                order.status = 0
                order.save()
            sppids = []
            for item in items:
                sub_order = SubOrder()
                sub_order.order = order
                sub_order.saler_store = item['sid']
                sub_order.buyer_store = user.store
                sub_order.price = item['price'] if order_type == 1 else 0
                sub_order.score = item['price'] if order_type == 2 else 0
                sub_order.status = order.status
                sub_order.save()
                for product in item['products']:
                    sppids.append(product['sppid'])
                    spp = StoreProductPrice.get(id=product['sppid'])
                    order_item = OrderItem()
                    order_item.order = order
                    order_item.sub_order = sub_order
                    order_item.product = spp.product_release.product
                    order_item.store_product_price = spp
                    order_item.quantity = product['quantity']
                    order_item.price = spp.price if order_type == 1 else spp.score
                    order_item.save()
            result['flag'] = 1
            result['data']['order_id'] = order.id
            result['data']['payment'] = payment
            result['data']['pay_info'] = pay_order(payment, total_price, order.ordernum, u'车装甲普通商品')
            if is_shop_cart == '1':
                ShopCart.delete().where(ShopCart.store == user.store, ShopCart.store_product_price << sppids).execute()
        else:
            result['msg'] = u"传入参数异常"
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/insuranceorderbase', name='mobile_insurance_order_base')  # 创建保险订单前的获取数据
class MobilInsuranceOrderBaseHandler(MobileBaseHandler):
    """
        @apiGroup order
        @apiVersion 1.0.0
        @api {get} /mobile/insuranceorderbase 03. 创建保险订单前的获取数据
        @apiDescription 创建保险订单前的获取数据，获取用户门店的默认地址、返油积分设置等

        @apiHeader {String} token 用户登录凭证

        @apiSampleRequest /mobile/insuranceorderbase
        """

    def get_insurance_message(self, area_code):
        result = {
            'force_insurance': {
                'title': '交强险',
                'item': []
            },
            'commerce_insurance_master': {
                'title': '商业险-主险',
                'item': []
            },
            'commerce_insurance_slave': {
                'title': '商业险-附加险',
                'item': []
            }
        }
        i_items = InsuranceItem.select()
        for i_item in i_items:
            if i_item.style_id == 1:
                result['force_insurance']['item'].append({
                    'name': i_item.name,
                    'eName': i_item.eName
                })
            elif i_item.style_id == 2:
                result['commerce_insurance_master']['item'].append({
                    'name': i_item.name,
                    'eName': i_item.eName,
                    'iPrice': [i_price.coverage for i_price in i_item.insurance_prices]

                })
            elif i_item.style_id == 3:
                result['commerce_insurance_slave']['item'].append({
                    'name': i_item.name,
                    'eName': i_item.eName,
                    'iPrice': [i_price.coverage for i_price in i_item.insurance_prices]
                })
        return result

    # 获取该门店所有保险的返佣政策
    def get_store_policies(self, store):
        insurance_list = []
        store_policies = SSILubePolicy.select().where(SSILubePolicy.store == store)
        for sp in store_policies:
            rake_back = []
            if sp.lube:
                rake_back.append({
                    'name': "返油",
                    'type': 1,
                    'link': "czj://lube_policy",
                    'link_str': "查看返油政策>>"
                })
            if sp.cash:
                rake_back.append({
                    'name': "返现",
                    'type': 2,
                    'link': "",
                    'link_str': "奖励现金将存入个人余额"
                })
            insurance_list.append({
                'id': sp.insurance.id,
                'name': sp.insurance.name,
                'rake_back': rake_back
            })
        return insurance_list

    def get_store_delivery_address(self, store):
        address = StoreAddress.select().where(StoreAddress.store == store).order_by(StoreAddress.is_default.desc())
        if address.count() > 0:
            store_delivery_address = {
                'delivery_to': address[0].name,
                'delivery_tel': address[0].mobile,
                'delivery_province': address[0].province,
                'delivery_city': address[0].city,
                'delivery_district': address[0].region,
                'delivery_address': address[0].address,
            }
        else:
            store_delivery_address = {
                'delivery_to': store.linkman,
                'delivery_tel': store.mobile,
                'delivery_province': Area.get(code=store.area_code[:4]).name if len(store.area_code) >= 4 else '',
                'delivery_city': Area.get(code=store.area_code[:8]).name if len(store.area_code) >= 8 else '',
                'delivery_district': Area.get(code=store.area_code).name if len(store.area_code) == 12 else '',
                'delivery_address': store.address,
            }
        return store_delivery_address

    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        user = self.get_user()
        try:
            sda = self.get_store_delivery_address(user.store)
            result['data']['delivery_to'] = sda['delivery_to']
            result['data']['delivery_tel'] = sda['delivery_tel']
            result['data']['delivery_province'] = sda['delivery_province']
            result['data']['delivery_city'] = sda['delivery_city']
            result['data']['delivery_district'] = sda['delivery_district']
            result['data']['delivery_address'] = sda['delivery_address']
            result['data']['insurance_message'] = self.get_store_policies(user.store)
            for i_item in InsuranceItem.select():
                if i_item.insurance_prices:
                    result['data'][i_item.eName] = [i_price.coverage for i_price in i_item.insurance_prices]
                else:
                    result['data'][i_item.eName] = []
        except Exception, ex:
            result['data']['delivery_to'] = ''
            result['data']['delivery_tel'] = ''
            result['data']['delivery_province'] = ''
            result['data']['delivery_city'] = ''
            result['data']['delivery_district'] = ''
            result['data']['delivery_address'] = ''
            result['data']['insurance_message'] = {}
        result['flag'] = 1

        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/newinsuranceorder', name='mobile_new_insurance_order')  # 创建保险订单
class MobilNewInsuranceOrderHandler(MobileBaseHandler):
    """
    @apiGroup order
    @apiVersion 1.0.0
    @api {post} /mobile/newinsuranceorder 04. 创建保险订单
    @apiDescription app  创建保险订单

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} id_card_front 身份证正面
    @apiParam {String} id_card_back 身份证反面
    @apiParam {String} drive_card_front 行驶证正面
    @apiParam {String} drive_card_back 行驶证反面
    @apiParam {Int} is_same_person 被保人与车主是否是同一人 是1 否0
    @apiParam {String} id_card_front_owner 车主身份证正面
    @apiParam {String} id_card_back_owner 车主身份证反面
    @apiParam {Int} insurance 保险公司ID
    @apiParam {String} forceI 交强险，字符串格式：1购买 ''未购买
    @apiParam {String} damageI 商业险-主险-车辆损失险，字符串格式：1购买 ‘’未购买
    @apiParam {String} damageIPlus 商业险-主险-车辆损失险-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} thirdDutyI 商业险-主险-第三者责任险，含保额，字符串格式：5万 ‘’未购买
    @apiParam {String} thirdDutyIPlus 商业险-主险-第三者责任险，含保额-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} robbingI 商业险-主险-机动车全车盗抢险，字符串格式：1购买 ‘’未购买
    @apiParam {String} robbingIPlus 商业险-主险-机动车全车盗抢险-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} driverDutyI 商业险-主险-机动车车上人员责任险（司机），含保额，字符串格式：5万 ‘’未购买
    @apiParam {String} driverDutyIPlus 商业险-主险-机动车车上人员责任险（司机），含保额-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} passengerDutyI 商业险-主险-机动车车上人员责任险（乘客），含保额，字符串格式：5万 ‘’未购买
    @apiParam {String} passengerDutyIPlus 商业险-主险-机动车车上人员责任险（乘客），含保额-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} glassI 商业险-附加险-玻璃单独破碎险，字符串格式：1购买 ''未购买
    @apiParam {String} scratchI 商业险-附加险-车身划痕损失险，含保额，字符串格式：5万 ‘’未购买
    @apiParam {String} scratchIPlus 商业险-附加险-车身划痕损失险，含保额-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} fireDamageI 商业险-主险-自燃损失险，字符串格式：1购买 ‘’未购买
    @apiParam {String} fireDamageIPlus 商业险-主险-自燃损失险-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} wadeI 商业险-主险-发动机涉水损失险，字符串格式：1购买 ‘’未购买
    @apiParam {String} wadeIPlus 商业险-主险-发动机涉水损失险-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} thirdSpecialI 商业险-附加险-机动车损失保险无法找到第三方特约金，字符串格式：1购买 ''未购买
    @apiParam {String} delivery_to 保单邮寄接收人名称
    @apiParam {String} delivery_tel 保单邮寄接收人电话
    @apiParam {String} delivery_province 保单邮寄接收省份
    @apiParam {String} delivery_city 保单邮寄接收城市
    @apiParam {String} delivery_district 保单邮寄接收区域
    @apiParam {String} delivery_address 保单邮寄地址
    @apiParam {Int} gift_policy 礼品策略 1反油， 2反积分, 0无礼品
    @apiSampleRequest /mobile/newinsuranceorder
    """

    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        id_card_front = self.get_body_argument('id_card_front', None)
        id_card_back = self.get_body_argument('id_card_back', None)
        drive_card_front = self.get_body_argument('drive_card_front', None)
        drive_card_back = self.get_body_argument('drive_card_back', None)
        is_same_person = int(self.get_body_argument('is_same_person', 1))
        id_card_front_owner = self.get_body_argument('id_card_front_owner', '')
        id_card_back_owner = self.get_body_argument('id_card_back_owner', '')

        insurance = self.get_body_argument('insurance', None)
        delivery_to = self.get_body_argument('delivery_to', None)
        delivery_tel = self.get_body_argument('delivery_tel', None)
        delivery_province = self.get_body_argument('delivery_province', None)
        delivery_city = self.get_body_argument('delivery_city', None)
        delivery_district = self.get_body_argument('delivery_district', None)
        delivery_address = self.get_body_argument('delivery_address', None)
        gift_policy = self.get_body_argument('gift_policy', None)

        forceI = self.get_body_argument('forceI', '')
        damageI = self.get_body_argument('damageI', '')
        damageIPlus = self.get_body_argument('damageIPlus', '')
        thirdDutyI = self.get_body_argument('thirdDutyI', '')
        thirdDutyIPlus = self.get_body_argument('thirdDutyIPlus', '')
        robbingI = self.get_body_argument('robbingI', '')
        robbingIPlus = self.get_body_argument('robbingIPlus', '')
        driverDutyI = self.get_body_argument('driverDutyI', '')
        driverDutyIPlus = self.get_body_argument('driverDutyIPlus', '')
        passengerDutyI = self.get_body_argument('passengerDutyI', '')
        passengerDutyIPlus = self.get_body_argument('passengerDutyIPlus', '')
        glassI = self.get_body_argument('glassI', '')
        scratchI = self.get_body_argument('scratchI', '')
        scratchIPlus = self.get_body_argument('scratchIPlus', '')
        fireDamageI = self.get_body_argument('fireDamageI', '')
        fireDamageIPlus = self.get_body_argument('fireDamageIPlus', '')
        wadeI = self.get_body_argument('wadeI', '')
        wadeIPlus = self.get_body_argument('wadeIPlus', '')
        thirdSpecialI = self.get_body_argument('thirdSpecialI', '')

        user = self.get_user()
        if user and gift_policy and delivery_address and delivery_city and delivery_district and delivery_tel \
                and delivery_to and insurance and drive_card_back and drive_card_front and id_card_back and \
                id_card_front:
            order = InsuranceOrder()
            order.user = user
            order.store = user.store
            order.id_card_front = id_card_front
            order.id_card_back = id_card_back
            order.is_same_person = is_same_person
            order.id_card_front_owner = id_card_front_owner
            order.id_card_back_owner = id_card_back_owner
            order.drive_card_front = drive_card_front
            order.drive_card_back = drive_card_back
            order.ordered = int(time.time())
            order.delivery_to = delivery_to
            order.delivery_tel = delivery_tel
            order.delivery_province = delivery_province
            order.delivery_city = delivery_city
            order.delivery_region = delivery_district
            order.delivery_address = delivery_address
            order.status = 0
            order.save()
            order_price = InsuranceOrderPrice()
            order_price.insurance_order_id = order.id
            order_price.insurance = insurance
            order_price.created = int(time.time())
            order_price.gift_policy = gift_policy
            order_price.forceI = forceI
            order_price.damageI = damageI
            order_price.damageIPlus = damageIPlus
            order_price.thirdDutyI = thirdDutyI
            order_price.thirdDutyIPlus = thirdDutyIPlus
            order_price.robbingI = robbingI
            order_price.robbingIPlus = robbingIPlus
            order_price.driverDutyI = driverDutyI
            order_price.driverDutyIPlus = driverDutyIPlus
            order_price.passengerDutyI = passengerDutyI
            order_price.passengerDutyIPlus = passengerDutyIPlus
            order_price.glassI = glassI
            order_price.scratchI = scratchI
            order_price.scratchIPlus = scratchIPlus
            order_price.fireDamageI = fireDamageI
            order_price.fireDamageIPlus = fireDamageIPlus
            order_price.wadeI = wadeI
            order_price.wadeIPlus = wadeIPlus
            order_price.thirdSpecialI = thirdSpecialI
            order_price.save()
            order.ordernum = 'U' + str(user.id) + 'I' + str(order.id)
            order.current_order_price = order_price.id
            order.save()
            result['flag'] = 1
            result['data']['order_id'] = order.id
            result['data']['order_price_id'] = order_price.id
        else:
            result['msg'] = u'输入参数异常'
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/payorder', name='mobile_pay_order')  # 订单支付
class MobilePayOrderHandler(MobileBaseHandler):
    """
    @apiGroup order
    @apiVersion 1.0.0
    @api {post} /mobile/payorder 05. 订单支付
    @apiDescription 订单支付

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} order_number 订单号
    @apiParam {Int} payment 支付方式 1支付宝  2微信 3银联 4余额 5积分 6立即支付宝 7立即微信

    @apiSampleRequest /mobile/payorder
    """

    def after_pay_operation(self, order, total_price, user, order_type):
        now = int(time.time())
        user.store.price -= total_price
        user.store.save()
        order.status += 1
        order.pay_time = now
        order.save()
        for so in order.sub_orders:
            so.status = 1
            so.save()

        if order_type == 1:  # 1金钱订单
            money_record = MoneyRecord()
            money_record.user = user
            money_record.store = user.store
            money_record.process_type = 2
            money_record.process_log = u'购买产品使用余额支付, 订单号：' + order.ordernum
            money_record.status = 1
            money_record.money = total_price
            money_record.apply_time = now
            money_record.save()

    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        order_number = self.get_body_argument("order_number", None)
        payment = self.get_body_argument("payment", None)
        payment = int(payment) if payment else None
        user = self.get_user()
        now = int(time.time())
        if order_number and payment:
            if 'S' in order_number:  # 普通商品订单
                order = Order.get(ordernum=order_number)
                ordernum = order.ordernum
                if order.status != 0:
                    result['msg'] = u'该订单不可支付'
                    return self.write(simplejson.dumps(result))
                else:
                    total_price = order.total_price
                    order_type = order.order_type
                    log = u'车装甲普通订单'
            elif 'I' in order_number:  # 保险订单
                order = InsuranceOrder.get(ordernum=order_number)
                ordernum = order.ordernum
                log = u'车装甲保单'
                if order.status == 1:
                    total_price = order.current_order_price.total_price
                    order_type = 1
                    log += u'支付'
                elif order.status in [2, 3] and order.current_order_price.append_refund_status == 1:
                    total_price = order.current_order_price.append_refund_num
                    order_type = 1
                    ordernum = ordernum + 'A' + str(now)[5:10]
                    log += u'补款'
                else:
                    result['msg'] = u'该订单不可支付'
                    return self.write(simplejson.dumps(result))
            else:
                result['msg'] = u'订单类型不可知'
                return self.write(simplejson.dumps(result))
            if payment == 4:  # 余额支付
                if 'I' in order_number and order.status in [2, 3] and order.current_order_price.append_refund_status == 1:
                    if user.store.price < order.current_order_price.append_refund_num:
                        result['msg'] = u"您的余额不足"
                    else:
                        order.current_order_price.append_refund_status = 2
                        order.current_order_price.save()
                        user.store.price -= order.current_order_price.append_refund_num
                        user.store.save()
                        money_record = MoneyRecord()
                        money_record.user = user
                        money_record.store = user.store
                        money_record.process_type = 2
                        money_record.process_log = u'余额补款保单, 订单号：%s, 补单号：%s' % (order.ordernum, ordernum)
                        money_record.status = 1
                        money_record.money = order.current_order_price.append_refund_num
                        money_record.apply_time = now
                        money_record.save()
                else:
                    if user.store.price < total_price:
                        result['msg'] = u"您的余额不足"
                        self.write(simplejson(result))
                        return
                    else:
                        self.after_pay_operation(order, total_price, user, order_type)
                        result['flag'] = 1

            result['data']['pay_info'] = pay_order(payment, total_price, ordernum, log)
            result['data']['payment'] = payment

            if result['data']['pay_info']:
                result['flag'] = 1
            if payment in [6, 7] and not result['data']['pay_info']:
                result['msg'] = u'获取二维码失败'

        else:
            result['msg'] = u"传入参数异常"
        self.write(simplejson.dumps(result))
        self.finish()


# -----------------------------------------------------工具箱-------------------------------------------------------------
@route(r'/mobile/tools', name='mobile_tools')  # 工具箱页
class MobileToolsHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/tools 12. 工具箱
    @apiDescription 工具箱页,返回html代码

    @apiSampleRequest /mobile/tools
    """

    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        self.render('mobile/tools.html')


# -----------------------------------------------------额外API----------------------------------------------------------
@route(r'/mobile/insurance_order_quote_info', name='insurance_order_quote_info')  # 查询保险报价信息
class MobilInsuranceOrderQuoteInfoHandler(MobileBaseHandler):
    """
    @apiGroup order
    @apiVersion 1.0.0
    @api {post} /mobile/newinsuranceorder 04. 创建保险订单
    @apiDescription app  创建保险订单

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} id_card_front 身份证正面
    @apiParam {String} id_card_back 身份证反面
    @apiParam {String} drive_card_front 行驶证正面
    @apiParam {String} drive_card_back 行驶证反面
    @apiParam {Int} is_same_person 被保人与车主是否是同一人 是1 否0
    @apiParam {String} id_card_front_owner 车主身份证正面
    @apiParam {String} id_card_back_owner 车主身份证反面
    @apiParam {Int} insurance 保险公司ID
    @apiParam {String} forceI 交强险，字符串格式：1购买 ''未购买
    @apiParam {String} damageI 商业险-主险-车辆损失险，字符串格式：1购买 ‘’未购买
    @apiParam {String} damageIPlus 商业险-主险-车辆损失险-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} thirdDutyI 商业险-主险-第三者责任险，含保额，字符串格式：5万 ‘’未购买
    @apiParam {String} thirdDutyIPlus 商业险-主险-第三者责任险，含保额-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} robbingI 商业险-主险-机动车全车盗抢险，字符串格式：1购买 ‘’未购买
    @apiParam {String} robbingIPlus 商业险-主险-机动车全车盗抢险-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} driverDutyI 商业险-主险-机动车车上人员责任险（司机），含保额，字符串格式：5万 ‘’未购买
    @apiParam {String} driverDutyIPlus 商业险-主险-机动车车上人员责任险（司机），含保额-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} passengerDutyI 商业险-主险-机动车车上人员责任险（乘客），含保额，字符串格式：5万 ‘’未购买
    @apiParam {String} passengerDutyIPlus 商业险-主险-机动车车上人员责任险（乘客），含保额-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} glassI 商业险-附加险-玻璃单独破碎险，字符串格式：1购买 ''未购买
    @apiParam {String} scratchI 商业险-附加险-车身划痕损失险，含保额，字符串格式：5万 ‘’未购买
    @apiParam {String} scratchIPlus 商业险-附加险-车身划痕损失险，含保额-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} fireDamageI 商业险-主险-自燃损失险，字符串格式：1购买 ‘’未购买
    @apiParam {String} fireDamageIPlus 商业险-主险-自燃损失险-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} wadeI 商业险-主险-发动机涉水损失险，字符串格式：1购买 ‘’未购买
    @apiParam {String} wadeIPlus 商业险-主险-发动机涉水损失险-不计免赔特约险，字符串格式：1购买 ‘’未购买
    @apiParam {String} thirdSpecialI 商业险-附加险-机动车损失保险无法找到第三方特约金，字符串格式：1购买 ''未购买
    @apiParam {String} delivery_to 保单邮寄接收人名称
    @apiParam {String} delivery_tel 保单邮寄接收人电话
    @apiParam {String} delivery_province 保单邮寄接收省份
    @apiParam {String} delivery_city 保单邮寄接收城市
    @apiParam {String} delivery_district 保单邮寄接收区域
    @apiParam {String} delivery_address 保单邮寄地址
    @apiParam {Int} gift_policy 礼品策略 1反油， 2反积分, 0无礼品
    @apiSampleRequest /mobile/newinsuranceorder
    """

    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        iop_id = self.get_argument('iop_id',0)

        try:
            iop = InsuranceOrderPrice.get(id = int(iop_id))
            io = InsuranceOrder.get(id=iop.insurance_order_id)
            uci = io.insurance_orders_car_infos
            if uci.count():
                uci = uci[0]
                data = {}

                data['ChePai'] =uci.car_num
                data['CheZhuName'] =uci.car_owner_name
                data['CheZhuID'] =uci.car_owner_idcard
                data['NewCar'] =False
                data['CarChuDengDate'] =uci.first_register_date
                data['CarShiBieCode'] =uci.car_frame_num
                data['CarEngineCode'] =uci.car_engine_num
                data['CarPinPaiXingHao'] =uci.car_model_type
                data['GuoHu'] =True if uci.assigned else False
                data['GuoHuDate'] =uci.assigned_date
                data['forceI'] =True if getattr(iop,'forceI') == '1' else False
                data['damageI'] =True if getattr(iop,'damageI') == '1' else False
                data['damageIPlus'] =True if getattr(iop,'damageIPlus') == '1' else False
                data['thirdDutyI'] =getattr(iop,'thirdDutyI')
                data['thirdDutyIPlus'] =True if getattr(iop,'thirdDutyIPlus') == '1' else False
                data['driverDutyI'] =getattr(iop,'thirdDutyI')
                data['driverDutyIPlus'] =True if getattr(iop,'driverDutyIPlus') == '1' else False
                data['passengerDutyI'] =getattr(iop,'passengerDutyI')
                data['passengerDutyIPlus'] = True if getattr(iop,'passengerDutyIPlus') == '1' else False
                data['robbingI'] = True if getattr(iop,'robbingI') == '1' else False
                data['robbingIPlus'] = True if getattr(iop,'robbingIPlus') == '1' else False
                data['glassI'] = True if getattr(iop,'glassI') == '1' else False
                data['fireDamageI'] = True if getattr(iop,'fireDamageI') == '1' else False
                data['fireDamageIPlus'] = True if getattr(iop,'fireDamageIPlus') == '1' else False
                data['scratchI'] = getattr(iop,'fireDamageIPlus')
                data['scratchIPlus'] = True if getattr(iop,'fireDamageIPlus') == '1' else False
                data['wadeI'] = True if getattr(iop,'fireDamageIPlus') == '1' else False
                data['wadeIPlus'] = True if getattr(iop,'fireDamageIPlus') == '1' else False
                data['thirdSpecialI'] = True if getattr(iop,'fireDamageIPlus') == '1' else False
                data['PTBName'] = uci.car_owner_name if uci.owner_buyer_isone else uci.buy_name
                data['PTBID'] = uci.car_owner_idcard if uci.owner_buyer_isone else uci.buy_idcard
                data['PTBSameCheZhu'] = True if uci.owner_buyer_isone == 1 else False
            result['flag'] = 1
            result['data'] = data
            result['msg'] = '查询成功'
        except Exception,e:
            result['msg'] = '查询失败:%s'%e

        self.write(simplejson.dumps(result))