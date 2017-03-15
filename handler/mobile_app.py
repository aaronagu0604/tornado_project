#!/usr/bin/env python
# coding=utf8

import logging
import setting
import simplejson
from lib.route import route
import math
from model import *
import uuid
from handler import MobileBaseHandler, require_auth
import random
from lib.mqhelper import create_msg
from lib.payment.alipay import get_pay_url
from lib.payment.wxPay import UnifiedOrder_pub
from lib.payment.upay import Trade


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

    @apiParam {String} mobile 电话号码
    @apiParam {Int} flag 验证码类型： 0注册 1忘记密码 2绑定手机号 3提现

    @apiSampleRequest /mobile/getvcode
    """
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
            result['msg'] = "请输入正确的手机号或验证码"
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
            province_name = Area.get(code=province).name
            city_name = Area.get(code=city).name
            district_name = Area.get(code=district).name
            StoreAddress.create(store=sid.id, province=province_name, city=city_name, region=district_name, address=address,
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
                        if self.application.memcachedb.set(token, str(user.id), setting.user_expire):
                            result['flag'] = 1
                            result['data']['type'] = user.store.store_type
                            result['data']['active'] = user.store.active
                            result['data']['token'] = token
                            result['data']['uid'] = user.id
                            user.updatesignin(token)
                        else:
                            result['msg'] = '登录失败'
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


@route(r'/mobile/home', name='mobile_home')  # 首页数据
class MobileHomeHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/home 01. 首页
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
        banners = BlockItem.select(BlockItem).join(Block) \
            .where((Block.tag == 'banner') & (Block.active == 1) & (BlockItem.active == 1)
                   & (BlockItem.area_code == area_code)).order_by(BlockItem.sort.asc())
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
        insurances = BlockItem.select(BlockItem.link, Insurance.logo, Insurance.name).join(Block). \
            join(Insurance, on=BlockItem.ext_id == Insurance.id).where(
            (Block.tag == 'insurance') & (Block.active == 1)
            & (BlockItem.active == 1) & (BlockItem.area_code == area_code)).order_by(BlockItem.sort.asc()).tuples()
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
        categories = BlockItem.select(BlockItem.link, Category.img_m, Category.name).join(Block). \
            join(Category, on=BlockItem.ext_id == Category.id).where(
            (Block.tag == 'hot_category') & (Block.active == 1)
            & (BlockItem.active == 1) & (BlockItem.area_code == area_code)).order_by(BlockItem.sort.asc()).tuples()
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
        brands = BlockItem.select(BlockItem.link, Brand.logo, Brand.name).join(Block). \
            join(Brand, on=BlockItem.ext_id == Brand.id).where((Block.tag == 'hot_brand') & (Block.active == 1)
                                                               & (BlockItem.active == 1) & (
                                                               BlockItem.area_code == area_code)).order_by(
            BlockItem.sort.asc()).tuples()
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
        recommends = BlockItem.select(BlockItem.link, Product.cover, Product.name, StoreProductPrice.price).join(
            Block). \
            join(StoreProductPrice, on=BlockItem.ext_id == StoreProductPrice.id). \
            join(ProductRelease, on=ProductRelease.id == StoreProductPrice.product_release). \
            join(Product, on=Product.id == ProductRelease.product). \
            where((Block.tag == 'recommend') & (Block.active == 1) & (BlockItem.active == 1)
                  & (BlockItem.area_code == area_code)).order_by(BlockItem.sort.asc()).tuples()
        for link, logo, name, price in recommends:
            items.append({
                'img': logo,
                'name': name,
                'price': price,
                'link': link
            })
        return items


# -----------------------------------------------------普通商品---------------------------------------------------------
@route(r'/mobile/discover', name='mobile_discover')  # 发现
class MobileDiscoverHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/discover 02. 发现
    @apiDescription 发现

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} type 入参为值category或brand category:分类更多； brand:品牌更多；不传就是发现页（两者都有）

    @apiSampleRequest /mobile/discover
    """
    def get_category(self):
        items = []
        categories = Category.select().where(Category.active == 1).order_by(Category.hot.desc(), Category.sort.desc())
        for categorie in categories:
            items.append({
                'id': categorie.id,
                'img': categorie.img_m if categorie.img_m else '',
                'name': categorie.name
            })
        return items

    def get_brand(self):
        items = []
        brands = Brand.select().where(Brand.active == 1).order_by(Brand.hot.desc(), Brand.sort.desc())
        for brand in brands:
            items.append({
                'id': brand.id,
                'img': brand.logo if brand.logo else '',
                'name': brand.name
            })
        return items

    def get(self):
        result = {'flag': 0, 'msg': '', 'data': {}}
        type = self.get_argument('type', None)

        if type == 'category':
            result['data']['category'] = self.get_category()
            result['data']['brand'] = []
        elif type == 'brand':
            result['data']['brand'] = self.get_brand()
            result['data']['category'] = []
        else:
            result['data']['category'] = self.get_category()[:6]
            result['data']['brand'] = self.get_brand()[:6]

        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/filter', name='mobile_filter')  # 普通商品筛选界面
class MobileFilterHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/filter 03. 普通商品筛选界面
    @apiDescription 普通商品筛选界面，未登陆使用西安code

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

        if not (flag and id):
            result['msg'] = '分类或品牌不能为空'
            self.write(simplejson.dumps(result))
            return
        else:
            flag = int(flag)
            id = int(id)

        result['data']['categoryList'] = []
        result['data']['brandList'] = []
        if flag == 2:    # 分类一定
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
        elif flag == 1:  # 品牌一定
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

        result['flag'] = 1
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/discoverproducts', name='mobile_discover_products')  # 商品列表
class MobileDiscoverProductsHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/discoverproducts 04. 商品列表
    @apiDescription 商品列表，未登陆使用西安code

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} keyword 搜索关键字
    @apiParam {String} sort 价格排序 1正序， 2逆序； 默认为1  销量排序 1正序， 2逆序； 默认2
    @apiParam {String} category 分类ID， 单选
    @apiParam {String} brand 品牌ID组合， 多选, 例：1,2,3
    @apiParam {String} attribute 属性ID组合, 多选, 例： 1,2,3
    @apiParam {Int} index

    @apiSampleRequest /mobile/discoverproducts
    """
    def getProductList(self, keyword, sort, category, brand, attribute, index, area_code):
        productList = []
        pids = []
        ft = (Product.active==1)
        # 根据规格参数搜索
        if category and attribute:
            fts = []
            c = Category.get(id=category)
            for i, a in enumerate(c.attributes):
                cais = CategoryAttributeItems.select().where((CategoryAttributeItems.category_attribute==a) & (CategoryAttributeItems.id<<attribute))
                for j, cai in enumerate(cais):
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
        ft &= ((StoreProductPrice.price>0) & (StoreProductPrice.active==1) & (ProductRelease.active==1))
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
        # 排序
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
        brand = brand.strip(',').split(',') if brand else None
        attribute = attribute.strip(',').split(',') if attribute else None
        area_code = self.get_store_area_code()

        result['data'] = self.getProductList(keyword, sort, category, brand, attribute, index, area_code)
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/product', name='mobile_product')  # 产品详情页
class MobileProductHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/product 05. 产品详情页
    @apiDescription 产品详情页,返回html代码

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


@route(r'/mobile/addshopcar', name='mobile_add_shop_car')  # 添加购物车
class MobileAddShopCarHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {post} /mobile/addshopcar 06. 添加购物车
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
            car = ShopCart()
            car.store = user.store
            car.store_product_price = sppid
            car.quantity = quantity
            car.created = int(time.time())
            car.save()
            result['flag'] = 1
        else:
            result['msg'] = '转入参数异常'
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/shopcar', name='mobile_shopcar')  # 手机端购物车内容获取
class MobileShopCarHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/shopcar 07. 手机端购物车内容获取
    @apiDescription app  手机端购物车内容获取

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/shopcar
    """
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        user = self.get_user()
        if user:
            for item in user.store.cart_items:
                result['data'].append({
                    'sppid': item.store_product_price.id,
                    'prid': item.store_product_price.product_release.id,
                    'pid': item.store_product_price.product_release.product.id,
                    'name': item.store_product_price.product_release.product.name,
                    'price': item.store_product_price.price,
                    'unit': item.store_product_price.product_release.product.unit,
                    'cover': item.store_product_price.product_release.product.cover,
                    'status': (item.store_product_price.active & item.store_product_price.product_release.active & item.store_product_price.product_release.product.active),
                    'quantity': item.quantity,
                    'storeid': user.store.id
                })
            result['flag'] = 1
        else:
            result['msg'] = '请先登录'
        self.write(simplejson.dumps(result))
        self.finish()


# -------------------------------------------------------商品/保险订单--------------------------------------------------
@route(r'/mobile/orderbase', name='mobile_order_base')  # 创建订单前的获取数据
class MobileOrderBaseHandler(MobileBaseHandler):
    """
    @apiGroup order
    @apiVersion 1.0.0
    @api {get} /mobile/orderbase 01. 创建订单前的获取数据
    @apiDescription 创建订单前的获取数据，传入产品信息，获取用户的默认地址、支付信息等

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} sppids 地区产品价格ID， 格式：1,2,3

    @apiSampleRequest /mobile/orderbase
    """
    @require_auth
    def get(self):
        user = self.get_user()
        result = {'flag': 0, 'msg': '', 'data': {'address':{}, 'store':[]}}
        sppids = self.get_argument('sppids', '').strip(',').split(',')
        if user is not None:
            if not sppids[0]:
                result['msg'] = '请选择购买的产品'
            else:
                for address in user.store.addresses:
                    if address.is_default == 1:
                        result['data']['address']['id'] = address.id
                        result['data']['address']['mobile'] = address.mobile
                        result['data']['address']['province'] = address.province
                        result['data']['address']['city'] = address.city
                        result['data']['address']['district'] = address.region
                        result['data']['address']['address'] = address.address
                        result['data']['address']['name'] = address.name
                        break
                else:
                    result['data']['address'] = None
                result['data']['last_pay_type'] = user.last_pay_type

                stores = Store.select(Store).join(StoreProductPrice).\
                    where((StoreProductPrice.active == 1) & (StoreProductPrice.id << sppids)).group_by(StoreProductPrice.store)
                for i, store in enumerate(stores):
                    products = []
                    product_list = StoreProductPrice.select().\
                        where((StoreProductPrice.active == 1) & (StoreProductPrice.id << sppids)).\
                        order_by(StoreProductPrice.store)
                    for product_price in product_list:
                        products.append({
                            'sppid': product_price.id,
                            'name': product_price.product_release.product.name,
                            'price': product_price.price,
                            'score': product_price.score,
                            'img': product_price.product_release.product.cover,
                            'attributes': [attribute.value for attribute in product_price.product_release.product.attributes]
                        })
                    result['data']['store'].append({
                        'name': store.name,
                        'store_tel': store.mobile,
                        'id': store.id,
                        'service_tel': setting.COM_TEL,
                        'products': products
                    })
                result['flag'] = 1
        else:
            result['msg'] = '请登录后再购买'
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
    @apiParam {Int} payment 付款方式  1支付宝  2微信 3银联 4余额
    @apiParam {Float} total_price 订单总价
    @apiParam {String} products 产品数据集合，如：[{sid:1, price:119, products:[{sppid:1, count:1}]}, ……]；
    sid为店铺ID；price为该店铺的金额；sppid为StoreProductPrice的ID，count为产品数量；服务端将订单按Store拆分为多个SubOrder

    @apiSampleRequest /mobile/neworder
    """
    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        address = self.get_body_argument("address", None)
        order_type = self.get_body_argument("order_type", None)
        payment = self.get_body_argument("payment", None)
        total_price = self.get_body_argument("total_price", None)
        products = self.get_body_argument("products", None)
        user = self.get_user()

        if address and payment and total_price and products and user and order_type:
            items = simplejson.loads(products)
            order = Order()
            order.user = user
            order.buyer_store = user.store
            order.address = address
            order.ordered = int(time.time())
            order.payment = payment
            order.message = ''
            order.order_type = order_type
            order.total_price = total_price
            if payment == 4:  # 余额支付
                if user.store.price < total_price:
                    result['msg'] = "您的余额不足"
                else:
                    order.user.store.price -= total_price
                    order.status = 1
                    order.pay_time = int(time.time())
                    order.save()
                    order.ordernum = 'U' + str(user.id) + 'S' + str(order.id)
                    order.save()
                    if order_type == 1:  # 1金钱订单
                        money_record = MoneyRecord()
                        money_record.user = user
                        money_record.store = user.store
                        money_record.process_type = 2
                        money_record.process_log = '购买产品使用余额支付, 订单号：' + order.ordernum
                        money_record.status = 1
                        money_record.money = total_price
                        money_record.apply_time = int(time.time())
                        money_record.save()
                    elif order_type == 2:  # 2积分订单
                        score_record = ScoreRecord()
                        score_record.user = user
                        score_record.store = user.store
                        score_record.process_type = 2
                        score_record.process_log = '积分兑换产品, 订单号：' + order.ordernum
                        score_record.score = math.ceil(total_price)  # 积分有小数进位
                        score_record.status = 1
                        score_record.save()
            else:
                order.status = 0
                order.save()
                order.ordernum = 'U' + str(user.id) + 'S' + str(order.id)
                order.save()
            for item in items:
                sub_order = SubOrder()
                sub_order.order = order
                sub_order.saler_store = item['sid']
                sub_order.buyer_store = user.store
                sub_order.price = item['price']
                sub_order.status = order.status
                sub_order.save()
                for product in item['products']:
                    spp = StoreProductPrice.get(id=product['sppid'])
                    order_item = OrderItem()
                    order_item.order = order
                    order_item.sub_order = sub_order
                    order_item.store_product_price = spp
                    order_item.quantity = product['count']
                    order_item.price = spp.price
                    order_item.product = spp.product_release.product
                    order_item.save()
            result['flag'] = 1
            result['data']['order_id'] = order.id
            result['data']['payment'] = payment
            if payment == 1:  # 1支付宝  2微信 3银联 4余额
                response_url = get_pay_url(order.ordernum.encode('utf-8'), u'车装甲商品', str(total_price))
                if len(response_url) > 0:
                    result['data']['pay_info'] = response_url
                else:
                    result['data']['pay_info'] = ''
            elif payment == 2:
                pay_info = UnifiedOrder_pub().getPrepayId(order.ordernum.encode('utf-8'), u'车装甲商品',
                                                          int(total_price * 100))
                result['data']['pay_info'] = pay_info
            elif payment == 3:
                pay_info = Trade().trade(order.ordernum, order.currentprice)
                result['data']['pay_info'] = pay_info
            else:
                result['data']['pay_info'] = ''
        else:
            result['msg'] = "传入参数异常"
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

        @apiParam {Int} insurance 保险公司ID

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
            'commerce_insurance_slave':{
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

    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        area_code = self.get_store_area_code()
        user = self.get_user()
        try:
            address = StoreAddress.get((StoreAddress.store == user.store) & (StoreAddress.is_default == 1))
            result['data']['delivery_to'] = address.name
            result['data']['delivery_tel'] = address.mobile
            result['data']['delivery_province'] = address.province
            result['data']['delivery_city'] = address.city
            result['data']['delivery_region'] = address.region
            result['data']['delivery_address'] = address.address
            result['data']['insurance_message'] = InsuranceScoreExchange.get_insurances(area_code)
            for i_item in InsuranceItem.select():
                if i_item.insurance_prices:
                    result['data'][i_item.eName] = [i_price.coverage for i_price in i_item.insurance_prices]
        except Exception, ex:
            result['data']['delivery_to'] = ''
            result['data']['delivery_tel'] = ''
            result['data']['delivery_province'] = ''
            result['data']['delivery_city'] = ''
            result['data']['delivery_region'] = ''
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
    @apiParam {String} delivery_region 保单邮寄接收区域
    @apiParam {String} delivery_address 保单邮寄地址
    @apiParam {Int} gift_policy 礼品策略 1反油， 2反积分, 0无礼品
/mobile/receiveraddress
    @apiSampleRequest /mobile/newinsuranceorder
    """

    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        id_card_front = self.get_body_argument('id_card_front', None)
        id_card_back = self.get_body_argument('id_card_back', None)
        drive_card_front = self.get_body_argument('drive_card_front', None)
        drive_card_back = self.get_body_argument('drive_card_back', None)
        insurance = self.get_body_argument('insurance', None)
        delivery_to = self.get_body_argument('delivery_to', None)
        delivery_tel = self.get_body_argument('delivery_tel', None)
        delivery_province = self.get_body_argument('delivery_province', None)
        delivery_city = self.get_body_argument('delivery_city', None)
        delivery_region = self.get_body_argument('delivery_region', None)
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
        if user and gift_policy and delivery_address and delivery_city and delivery_province and delivery_region and \
            delivery_tel and delivery_to and insurance and drive_card_back and drive_card_front and id_card_back and \
            id_card_front:
            order = InsuranceOrder()
            order.user = user
            order.store = user.store
            order.id_card_front = id_card_front
            order.id_card_back = id_card_back
            order.drive_card_front = drive_card_front
            order.drive_card_back = drive_card_back
            order.ordered = int(time.time())
            order.delivery_to = delivery_to
            order.delivery_tel = delivery_tel
            order.delivery_province = delivery_province
            order.delivery_city = delivery_city
            order.delivery_region = delivery_region
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
            result['msg'] = '输入参数异常'
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
    @apiParam {Int} payment 支付方式

    @apiSampleRequest /mobile/payorder
    """
    def after_pay_operation(self, order, total_price, user, order_type):
        order.user.store.price -= total_price
        order.status += 1
        order.pay_time = int(time.time())
        order.save()
        if order_type == 1:  # 1金钱订单
            money_record = MoneyRecord()
            money_record.user = user
            money_record.store = user.store
            money_record.process_type = 2
            money_record.process_log = '购买产品使用余额支付, 订单号：' + order.ordernum
            money_record.status = 1
            money_record.money = total_price
            money_record.apply_time = int(time.time())
            money_record.save()
        elif order_type == 2:  # 2积分订单
            score_record = ScoreRecord()
            score_record.user = user
            score_record.store = user.store
            score_record.process_type = 2
            score_record.process_log = '积分兑换产品, 订单号：' + order.ordernum
            score_record.score = math.ceil(total_price)  # 积分有小数进位
            score_record.status = 1
            score_record.save()

    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        order_number = self.get_body_argument("order_number", None)
        payment = self.get_body_argument("payment", None)
        payment = int(payment) if payment else None
        user = self.get_user()
        if order_number and payment:
            if 'S' in order_number:  # 普通商品订单
                order = Order.get(ordernum=order_number)
                if order.status != 0:
                    result['msg'] = '该订单不可支付'
                    return self.write(simplejson.dumps(result))
                else:
                    total_price = order.total_price
                    order_type = order.order_type
            elif 'I' in order_number:  # 保险订单
                order = InsuranceOrder.get(ordernum=order_number)
                if order.status != 1:
                    result['msg'] = '该订单不可支付'
                    return self.write(simplejson.dumps(result))
                else:
                    total_price = order.current_order_price.total_price
                    order_type = 1
            else:
                result['msg'] = '订单类型不可知'
                return self.write(simplejson.dumps(result))
            if payment == 4:  # 余额支付
                if user.store.price < total_price:
                    result['msg'] = "您的余额不足"
                else:
                    self.after_pay_operation(order, total_price, user, order_type)
            elif payment == 1:  # 1支付宝  2微信 3银联 4余额
                response_url = get_pay_url(order.ordernum.encode('utf-8'), u'车装甲商品', str(total_price))
                result['data']['pay_info'] = response_url
            elif payment == 2:
                pay_info = UnifiedOrder_pub().getPrepayId(order.ordernum.encode('utf-8'), u'车装甲商品',
                                                          int(total_price * 100))
                result['data']['pay_info'] = pay_info
            elif payment == 3:
                pay_info = Trade().trade(order.ordernum, total_price)
                result['data']['pay_info'] = pay_info
            else:
                result['data']['pay_info'] = ''
            result['flag'] = 1
        else:
            result['msg'] = "传入参数异常"
        self.write(simplejson.dumps(result))
        self.finish()








