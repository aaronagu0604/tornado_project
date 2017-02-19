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
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/filter 01. 发现页面的筛选界面
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
        id = self.get_argument("id", None)
        flag = self.get_argument("flag", None)
        sort = self.get_argument("sort", None)
        index = self.get_argument("index", None)

        if not (flag and id):
            result['msg'] = '分类或品牌不能为空'
            self.write(simplejson.dumps(result))
            return
        else:
            flag = int(flag)
            id = int(id)
        index = int(index) if index else 1
        area_code = self.get_store_area_code()

        result['data']['categoryList'] = []
        result['data']['brandList'] = []
        # result['data']['productList'] = []
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
        # result['data']['productList'] = self.getProductList(flag, id, sort, index, area_code)

        result['flag'] = 1
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/discover', name='mobile_discover')  # 发现 商品列表
class MobileDiscoverHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/discover 02. 发现页面列表
    @apiDescription 发现页面列表，未登陆使用西安code

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} keyword 搜索关键字
    @apiParam {String} sort 价格排序 1正序， 2逆序； 默认为1  销量排序 1正序， 2逆序； 默认2
    @apiParam {String} category 分类ID， 单选
    @apiParam {String} brand 品牌ID组合， 多选, 例：[1,2,3]
    @apiParam {String} attribute 属性ID组合, 多选, 例： [1,2,3]

    @apiSampleRequest /mobile/discover
    """
    def getProductList(self, keyword, sort, category, brand, attribute, index, area_code):
        productList = []
        pids = []
        ft = (Product.active==1)
        if category and attribute:
            fts = []
            c = Category.get(id=category)
            logging.info('-----Category------%s, %s---'%( c.id, c.name))
            for i, a in enumerate(c.attributes):
                logging.info('-----CategoryAttribute------%s, %s---'%( a.id, a.name))
                cais = CategoryAttributeItems.select().where((CategoryAttributeItems.category_attribute==a) & (CategoryAttributeItems.id<<attribute))
                for j, cai in enumerate(cais):
                    logging.info('-----CategoryAttributeItems------%s, %s, %s---'%(j, cai.id, cai.name))
                    if j == 0:
                        fts.append((ProductAttributeValue.value == cai.name))
                    else:
                        fts[i] |= (ProductAttributeValue.value == cai.name)
            for i, f in enumerate(fts):
                if i == 0:
                    products = Product.select().join(ProductAttributeValue).where(f)
                else:
                    products = Product.select().join(ProductAttributeValue).where(f & (Product.id << pids))
                pids = [product.id for product in products]
            ft = (Product.id << pids)
        elif category:
            ft &= (Product.category == category)
        ft &= ((StoreProductPrice.price>0) & (StoreProductPrice.active==1) & (StoreProductPrice.active==1))
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
            Product.resume.alias('resume'), Store.name.alias('sName')). \
            join(Product, on=(Product.id == ProductRelease.product)). \
            join(StoreProductPrice, on=(StoreProductPrice.product_release == ProductRelease.id)). \
            join(Store, on=(Store.id == ProductRelease.store)).where(ft).dicts()

        if sort == '1':
            products.order_by(StoreProductPrice.price.desc())
        elif sort == '2':
            products.order_by(StoreProductPrice.price.asc())
        elif sort == '3':
            products.order_by(ProductRelease.buy_count.desc())
        elif sort == '4':
            products.order_by(ProductRelease.buy_count.asc())
        else:
            products.order_by(ProductRelease.sort.desc())
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
                'storeName': p['sName']
            })
        return productList

    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        keyword = self.get_argument("keyword", None)
        sort = self.get_argument("sort", None)
        category = self.get_argument("category", None)
        brand = self.get_argument("brand", None)
        attribute = self.get_argument("attribute", None)
        index = self.get_argument("index", None)

        index = int(index) if index else 1
        brand = brand.split(',') if brand else None
        attribute = attribute.split(',') if attribute else None
        area_code = self.get_store_area_code()

        result['data'] = self.getProductList(keyword, sort, category, brand, attribute, index, area_code)
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/home', name='mobile_home')  # app首页数据
class MobileHomeHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/home 03. app首页数据
    @apiDescription app首页数据，
    banner 首页轮播;
    insurance  首页保险;
    hot_category 热门分类;
    hot_brand  热销产品;
    recommend  为你推荐;

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/home
    """
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        area_code = self.get_store_area_code()

        tmp_code = area_code
        banners = self.get_banner(tmp_code)
        while len(banners) == 0 and len(tmp_code) > 4:
            tmp_code = tmp_code[0: -4]
            banners = self.get_banner(tmp_code)
        if len(banners) == 0:
            banners = self.get_banner(self.get_default_area_code())
        result['data']['banner'] = banners

        tmp_code = area_code
        insurances = self.get_insurance(tmp_code)
        while len(insurances) == 0 and len(tmp_code) > 4:
            tmp_code = tmp_code[0: -4]
            insurances = self.get_insurance(tmp_code)
        if len(insurances) == 0:
            insurances = self.get_insurance(self.get_default_area_code())
        result['data']['insurance'] = insurances

        tmp_code = area_code
        categories = self.get_category(tmp_code)
        while len(categories) == 0 and len(tmp_code) > 4:
            tmp_code = tmp_code[0: -4]
            categories = self.get_category(tmp_code)
        if len(categories) == 0:
            categories = self.get_category(self.get_default_area_code())
        result['data']['hot_category'] = categories

        tmp_code = area_code
        brands = self.get_brand(tmp_code)
        while len(brands) == 0 and len(tmp_code) > 4:
            tmp_code = tmp_code[0: -4]
            brands = self.get_brand(tmp_code)
        if len(brands) == 0:
            brands = self.get_brand(self.get_default_area_code())
        result['data']['hot_brand'] = brands

        tmp_code = area_code
        recommends = self.get_recommend(tmp_code)
        while len(recommends) == 0 and len(tmp_code) > 4:
            tmp_code = tmp_code[0: -4]
            recommends = self.get_recommend(tmp_code)
        if len(recommends) == 0:
            recommends = self.get_recommend(self.get_default_area_code())
        result['data']['recommend'] = recommends
        result['flag'] = 1
        self.write(simplejson.dumps(result))
        self.finish()

    def get_banner(self, area_code):
        items = []
        banners = BlockItem.select(BlockItem).join(Block)\
            .where((Block.tag == 'banner') & (Block.active == 1) & (BlockItem.active == 1)
                   & (BlockItem.area_code == area_code)).order_by(BlockItem.sort).asc()
        for p in banners:
            items.append({
                'img': p.img,
                'name': p.name,
                'price': 0,
                'link': p.link
            })
        return items

    def get_insurance(self, area_code):
        items = []
        insurances = BlockItem.select(BlockItem.link, Insurance.logo, Insurance.name).join(Block).\
            join(Insurance, on=BlockItem.ext_id == Insurance.id).where((Block.tag == 'insurance') & (Block.active == 1)
            & (BlockItem.active == 1) & (BlockItem.area_code == area_code)).order_by(BlockItem.sort).asc().tuples()
        for link, logo, name in insurances:
            items.append({
                'img': logo,
                'name': name,
                'price': 0,
                'link': link
            })
        return items

    def get_category(self, area_code):
        items = []
        categories = BlockItem.select(BlockItem.link, Category.img_m, Category.name).join(Block).\
            join(Category, on=BlockItem.ext_id == Category.id).where((Block.tag == 'hot_category') & (Block.active == 1)
            & (BlockItem.active == 1) & (BlockItem.area_code == area_code)).order_by(BlockItem.sort).asc().tuples()
        for link, logo, name in categories:
            items.append({
                'img': logo,
                'name': name,
                'price': 0,
                'link': link
            })
        return items

    def get_brand(self, area_code):
        items = []
        brands = BlockItem.select(BlockItem.link, Brand.logo, Brand.name).join(Block).\
            join(Brand, on=BlockItem.ext_id == Brand.id).where((Block.tag == 'hot_brand') & (Block.active == 1)
            & (BlockItem.active == 1) & (BlockItem.area_code == area_code)).order_by(BlockItem.sort).asc().tuples()
        for link, logo, name in brands:
            items.append({
                'img': logo,
                'name': name,
                'price': 0,
                'link': link
            })
        return items

    def get_recommend(self, area_code):
        items = []
        recommends = BlockItem.select(BlockItem.link, Product.cover, Product.name, StoreProductPrice.price).join(Block).\
            join(StoreProductPrice, on=BlockItem.ext_id == StoreProductPrice.id).\
            join(ProductRelease, on=ProductRelease.id == StoreProductPrice.product_release). \
            join(Product, on=Product.id == ProductRelease.product). \
            where((Block.tag == 'recommend') & (Block.active == 1) & (BlockItem.active == 1)
                  & (BlockItem.area_code == area_code)).order_by(BlockItem.sort).asc().tuples()
        for link, logo, name, price in recommends:
            items.append({
                'img': logo,
                'name': name,
                'price': price,
                'link': link
            })
        return items


@route(r'/mobile/product', name='mobile_product')  # app产品详情页
class MobileProductHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/product 04. 产品详情页
    @apiDescription app产品详情页,返回html代码

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} id 产品或门店产品价格ID
    @apiParam {Int} type 当前打开的产品的来源；1从app 2从分享

    @apiSampleRequest /mobile/product
    """
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        id = self.get_argument("id", None)
        type = self.get_argument("type", None)
        product={'name': '测试产品'}
        self.render('mobile/product.html', product=product)



