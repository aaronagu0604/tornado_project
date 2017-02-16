#!/usr/bin/env python
# coding=utf8

import logging
import setting
import simplejson
from lib.route import route
from model import *
import uuid
from handler import MobileBaseHandler
import random
from lib.mqhelper import create_msg


@route(r'/', name='mobile_app')
class MobileAppHandler(MobileBaseHandler):
    def get(self):
        us = User.select()
        logging.info('---%s---'%us.count())
        self.write("czj api")


@route(r'/mobile/getvcode', name='mobile_getvcode')
class MobileGetVCodeAppHandler(MobileBaseHandler):
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

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

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
        user.mobile = mobile
        user.password = password
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
            result['msg'] = '注册成功'
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


@route(r'/mobile/filter', name='mobile_filter')  # 发现列表的筛选界面
class MobileFilterHandler(MobileBaseHandler):
    """
    @apiGroup discover
    @apiVersion 1.0.0
    @api {get} /mobile/filter 05. 发现页面的筛选界面
    @apiDescription 发现页面的筛选界面，未登陆使用西安code

    @apiParam {Int} id 品牌或者分类ID
    @apiParam {Int} flag 1品牌 2分类

    @apiSampleRequest /mobile/filter
    """
    def getCategoryAttribute(self, bc):
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
                'id': attribute.id,
                'name': attribute.name,
                'ename': attribute.ename,
                'values': tmpList
            })
        return attributeList

    def getProductList(self, flag, id):
        productList = []
        if flag == 1:  # 品牌
            if __name__ == '__main__':
                ft = (Product.brand == id)
                products = ProductRelease.select().join(Product, on=(Product.id == ProductRelease.product)). \
                    join()
        elif flag == 2:  # 分类
            pass
        return productList

    def get(self):
        ''''
        {
            'categoryList' = [{
                'id' = 10,
                'name' = '润滑油',
                'brand' = [{'id'= 9, 'name'='SK'}, {}]
            },{
                'id' = 9,
                'name' = '导航仪',
                'brand' = [{'id'= 6, 'name'='杰成'}, {}]
            }],

            'brandList' = [{
                'id' = 66,
                'name' = 'SK',
                'categorys' = [{'id' = 10, 'name' = '润滑油'}]
            }]

            'products' = [{
                'psid': n.id,
                'pid': n.product.id,
                'name': n.product.name+' '+n.copies,
                'price': n.price,
                'sales': n.orders,
                'originalPrice': n.orginalprice,
                'ourprice': n.pf_price, #销售价（门店）修改成批发价
                'pf_price': n.pf_price,
                'copies': n.copies,
                'unit': n.unit if n.unit else u'件',
                'categoryID': n.product.categoryfront.id,
                'sku': n.product.sku,
                'cover': PassMobileImg(n.product.cover),
                'standard': n.name,
                'resume': n.product.resume,
                'status': n.product.status,
                'storeName': n.store.name,
            }]
        }
        '''
        result = {'flag': 0, 'msg': '', "data": {}}
        flag = self.get_argument("flag", None)
        id = self.get_argument("id", None)

        if not flag and id:
            result['msg'] = '分类或品牌不能为空'
            self.write(simplejson.dumps(result))
            return
        else:
            flag = int(flag)
            id = int(id)

        result['data']['categoryList'] = []
        result['data']['brandList'] = []
        result['data']['productList'] = []
        if flag == 2:    #分类一定
            brandCategorys = BrandCategory.select().where(BrandCategory.category == id)
            if brandCategorys.count() > 0:
                result['data']['categoryList'].append({
                    'id': brandCategorys[0].category.id,
                    'name': brandCategorys[0].category.name,
                    'attribute': self.getCategoryAttribute(brandCategorys[0])
                })
                result['data']['categoryList'][0]['brand'] = []
                for bc in brandCategorys:
                    result['data']['categoryList'][0]['brand'].append({
                        'id': bc.brand.id,
                        'name': bc.brand.name
                    })
            else:
                result['msg'] = '未查到该分类'
                self.write(simplejson.dumps(result))
                return
        elif flag == 1:  #品牌一定
            brandCategorys = BrandCategory.select().where(BrandCategory.brand == id)
            if brandCategorys.count() > 0:
                result['data']['brandList'].append({
                    'id': brandCategorys[0].brand.id,
                    'name': brandCategorys[0].brand.name
                })
                result['data']['brandList'][0]['category'] = []
                for bc in brandCategorys:
                    result['data']['brandList'][0]['category'].append({
                        'id': bc.category.id,
                        'name': bc.category.name,
                        'attribute': self.getCategoryAttribute(bc)
                    })
            else:
                result['msg'] = '未查到该品牌'
                self.write(simplejson.dumps(result))
                return
        else:
            result['msg'] = '输入参数错误'
            self.write(simplejson.dumps(result))
            return
        result['data']['productList'] = self.getProductList(flag, id)

        result['flag'] = 1
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/discover', name='mobile_discover')  # 发现列表
class MobileDiscoverHandler(MobileBaseHandler):
    """
    @apiGroup discover
    @apiVersion 1.0.0
    @api {get} /mobile/discover 06. 发现页面列表
    @apiDescription 发现页面列表，未登陆使用西安code

    @apiParam {String} keyword 搜索关键字
    @apiParam {String} pricesort 价格排序 1正序， 2逆序； 默认为1
    @apiParam {String} salesort 销量排序 1正序， 2逆序； 默认2
    @apiParam {String} category 分类ID， 单选
    @apiParam {String} pinpai 品牌ID组合， 多选, 例：[1,2,3]
    @apiParam {String} attribute 属性ID组合, 多选, 例： [1,2,3]

    @apiSampleRequest /mobile/discover
    """
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        mobile = self.get_body_argument("mobile", None)
        password = self.get_body_argument("password", None)

        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/home', name='mobile_home')  # app首页数据
class MobileHomeHandler(MobileBaseHandler):
    """
    @apiGroup home
    @apiVersion 1.0.0
    @api {get} /mobile/home 07. app首页数据
    @apiDescription app首页数据，
    tag=banner 首页轮播
    tag=insurance  首页保险
    tag=hot_category 热门分类
    tag=hot_brand  热销产品
    tag=recommend  为你推荐

    @apiSampleRequest /mobile/home
    """
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        mobile = self.get_body_argument("mobile", None)
        password = self.get_body_argument("password", None)

        self.write(simplejson.dumps(result))
        self.finish()














