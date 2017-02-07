#!/usr/bin/env python
# coding=utf8
import simplejson
import logging
from lib.route import route
from model import *
from tornado.web import RequestHandler
from bootloader import db
from handler import MobileHandler, require_basic_authentication
import time
import datetime
import urllib2
import random
from lib.mqhelper import create_msg
import re
from lib.wap_alipay.submit import get_pay_url
from lib.wap_alipay.core import return_verify, notify_verify
from activity import user_top_up_balance
from activity import old_new_user_raffle
from activity import new_user_balance, return_reserve_balance, check_buy_quantity
import os
from activity import check_activity
import tornado.gen
from tornado.concurrent import run_on_executor
# 这个并发库在python3自带在python2需要安装sudo pip install futures
from concurrent.futures import ThreadPoolExecutor
import tornado.web
import qrcode
from io import BytesIO
import base64
import setting
from ajax2 import OrderChangeStatus
from map import getDistance
from base64 import decodestring
import random
from huanxin import create_user
from lib.wap_alipay.upay import Trade
from lib.wap_alipay.wxPay import UnifiedOrder_pub, Common_util_pub
import json
from PIL import Image, ImageDraw, ImageFont

def PassMobileImg(fileName):
    # imgArrr = os.path.splitext(imgPath)
    # outfile = imgArrr[0] + ".mobile"+imgArrr[1]
    imgArrr = os.path.splitext(fileName)
    outfile = imgArrr[0] + ".mobile" + imgArrr[1]
    return outfile


@route(r'/mobile/login', name='mobile_login')  # 手机端登录
class MobileLoginHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = self.get_mobile_user()
        self.write(simplejson.dumps(result))


@route(r'/mobile/cglogin', name='mobile_cglogin')  # 采购手机端登录
class MobileLoginHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = self.get_cg_mobile_user()
        self.write(simplejson.dumps(result))


@route(r'/mobile/home', name='mobile_home')  # 手机端首页
class MobileHomeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'products': [], 'stores': [], 'k': [], 'time': int(time.time())}
        # products 首页产品列表 stores 首页门店列表
        list2 = simplejson.loads(MobileBlock.select().where(MobileBlock.key == 'm_products')[0].content)
        vlist = ProductStandard.select(ProductStandard).join(Product).\
            where((ProductStandard.id << list2) & (ProductStandard.sale_status == 1))

        for n in vlist:
            result['products'].append({
                'id': n.id,
                'standard': n.name,
                'name': n.product.name,
                'price': n.price,
                'originalPrice': n.orginalprice,
                'unit': n.unit if n.unit else u'件',
                'sku': n.product.sku,
                'cover': PassMobileImg(n.product.cover),
                'resume': n.product.resume
            })
        list3 = simplejson.loads(MobileBlock.select().where(MobileBlock.key == 'm_stores')[0].content)
        tlist = Store.select().where((Store.id << list3) & (Store.check_state == 1))

        for n in tlist:
            result['stores'].append({
                'id': n.id,
                'name': n.name,
                'credit_score': n.credit_score,
                'star_score': n.star_score,
                'comment_count': n.comment_count,
                'image': PassMobileImg(n.image),
                'intro': n.intro
            })

        keys = Hot_Search.select().where(Hot_Search.status == 1).order_by(Hot_Search.quantity.desc(),
                                                                          Hot_Search.last_time.desc()).limit(10)
        for k in keys:
            result['k'].append({
                'keywords': k.keywords,
                'quantity': k.quantity
            })
        self.write(simplejson.dumps(result))


@route(r'/mobile/city_list', name='mobile_city_list')  # 全国所有城市列表
class MobileProductHandler(RequestHandler):
    def get(self):
        result = []
        version = self.get_argument('version', None)
        if version:
            provinces = Area.select().where((Area.has_sub == 1) & (Area.pid == None))
            for province in provinces:
                citys = Area.select().where(Area.pid==province.id)
                result.append({'name': province.name, 'citys': [{'city_code':city.code, 'city_name':city.name} for city in citys]})
        else:
            citys = Area.select().where((Area.has_sub==1) & (Area.pid!=None))
            for city in citys:
                result.append({'city_code':city.code,'city_name':city.name})
        self.write(simplejson.dumps(result))

@route(r'/mobile/product/(\d+)', name='mobile_product_detail')  # 手机端产品详情
class MobileProductHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, psid):
        uid = self.get_argument("user_id", None)
        result = {}
        try:
            ps = ProductStandard.get(id=psid)
            p = ps.product
            pics2 = p.pics
            result['time'] = int(time.time())
            result['name'] = p.name+' '+ps.copies
            result['sku'] = p.sku
            result['pid'] = p.id
            result['psid'] = ps.id
            result['standard'] = ps.name
            result['price'] = ps.price
            result['ourprice'] = ps.pf_price
            result['pf_price'] = ps.pf_price
            result['copies'] = ps.copies
            result['orginalprice'] = ps.orginalprice
            result['resume'] = p.resume
            result['status'] = p.status
            result['xgtotalnum'] = ps.xgtotalnum
            result['xgperusernum'] = ps.xgperusernum
            result['quantity'] = ps.quantity
            result['orders'] = ps.orders
            result['pics'] = []
            result['score'] = 0
            result['storeID'] = ps.store.id
            result['uid'] = ps.user.id
            result['storeName'] = ps.store.name
            result['store_credit_score'] = ps.store.credit_score
            result['store_star_score'] = ps.store.star_score
            result['prompt'] = p.prompt
            result['storeMobile'] = ps.store.mobile
            result['storeTel'] = ps.store.tel
            result['product_comment_count'] = p.product_comments.count()
            result['isScore'] = ps.is_score
            result['scoreNum'] = ps.scoreNum
            result['unit'] = ps.unit if ps.unit else u'件'

            list = simplejson.loads(ps.relations)
            pslist = ProductStandard.select().where(ProductStandard.id << list)
            standards = []
            for val in list:
                for n in pslist:
                    if n.id == val and (n.sale_status == 1):
                        standards.append({
                            'psid': n.id,
                            'pid': n.product.id,
                            'name': n.product.name,
                            'price': n.price,
                            'originalPrice': n.orginalprice,
                            'unit': n.unit if n.unit else u'件',
                            'sku': n.product.sku,
                            'cover': PassMobileImg(n.product.cover),
                            'standard': n.product.prompt,
                            'resume': n.product.resume
                        })
                        break
            result['standards'] = standards
            pics = [ProductPic(path=p.cover)] + [n for n in pics2 if not n.path == p.cover]
            for n in pics:
                result['pics'].append({
                    'img': PassMobileImg(n.path)
                })
            result['flag'] = 1

            if uid:
                create_browse(uid, ps.id, p.id, p.categoryfront.id)
        except Exception, e:
            result['flag'] = 0
            result['msg'] = '数据异常：' + e.message
            logging.info('Error: /mobile/product/%s, %s'%(psid, result['msg']))

        self.write(simplejson.dumps(result))


def create_browse(uid, psid, pid, cfid):
    # 判断用户浏览记录表中是否存在该商品
    ub_exist = User_Browse().select().where((User_Browse.user == uid) & (User_Browse.product_standard == pid))
    if ub_exist.count() > 0:
        pass
    else:
        # 创建用户浏览记录
        ub = User_Browse()
        ub.user = uid
        ub.product = pid
        ub.product_standard = psid
        ub.category_front = cfid
        ub.created = int(time.time())
        ub.save()
        # 如何该用户浏览记录大于5条，按队列顺序删除超出的数据
        ub_count = User_Browse.select().where(User_Browse.user == uid)
        if ub_count.count() > 5:
            del_count = ub_count.count() - 5
            del_ub = User_Browse.select().where(User_Browse.user == uid).order_by(User_Browse.created).limit(del_count)
            del_id = [n.id for n in del_ub]
            User_Browse.delete().where(User_Browse.id << del_id).execute()


@route(r'/mobile/pdetail/(\d+)', name='mobile_pdetail_detail')  # 手机端产品详情图片
class MobilePDetailHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, psid):
        result = []
        ps = Product.get(id=psid)
        intro = ps.intro
        #p = re.compile(r'upload/([\w]*/[\w]*/[\w]*.[\w]+)', flags=re.I)
        p = re.compile(r'upload/\w+/\w+/\w+/\w+\.\w+', flags=re.I)


        for com in p.finditer(intro):
            mm = com.group()
            result.append({
                # 'img': PassMobileImg(mm)[7:]
                'img': mm
            })

        self.write(simplejson.dumps(result))


@route(r'/mobile/search', name='mobile_product_search')  # 手机端查询
class MobileHomeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        x = self.get_argument("x", None)  # '109.005021'
        y = self.get_argument("y", None)  # '34.255995'
        index = self.get_argument("index", 1)
        keyword = self.get_argument("keywords", None)
        keyword2 = self.get_argument("keyword2", None)
        category = self.get_argument("category", None)
        city = self.get_argument("city", None)
        order = self.get_argument("order", None)
        city_code = self.get_argument("city_code", None)
        version = self.get_argument("version", None)
        level = self.get_argument("level", None)
        classes = self.get_argument("classes", None)
        capacity = self.get_argument("capacity", None)
        viscosity = self.get_argument("viscosity", None)
        configuration = self.get_argument("configuration", None)
        CAN = self.get_argument("CAN", None)
        psize = self.get_argument("psize", None)
        jsize = self.get_argument("jsize", None)
        lens = self.get_argument("lens", None)

        if city_code:
            result = get_store_new(keyword, category, int(index), city_code, order, version, level, classes, capacity,
                                   viscosity, configuration, CAN, psize, jsize, lens, keyword2)
        else:
            result = get_store(x, y, keyword, category, int(index), city, order)
        self.write(simplejson.dumps(result))

@route(r'/mobile/select_city', name='mobile_select_city')  # 手机端选择城市
class MobileSelectCityHandler(RequestHandler):
    def get(self):
        result = []
        items = Area.select().where((Area.pid >> None) & (Area.is_delete == 0) & (Area.is_site == 1))
        for i in items:
            obj = {"prov": i.name, "cities": []}
            cities = Area.select().where((Area.pid == i.id) & (Area.is_delete == 0) & (Area.is_site == 1))
            for j in cities:
                obj["cities"].append(j.name)
            result.append(obj)
        self.write(simplejson.dumps(result))

@route(r'/mobile/product_pid/(\d+)', name='mobile_product_pid_detail')  # 手机端通过pid获取产品详情
class MobileProductHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, pid):
        uid = self.get_argument("user_id", None)
        result = {}
        try:
            p = Product.get(id=pid)
            pics2 = p.pics
            result['pid'] = p.id
            result['time'] = int(time.time())
            result['name'] = p.name
            result['sku'] = p.sku
            result['resume'] = p.resume
            result['status'] = p.status
            result['quantity'] = 0
            result['pics'] = []
            result['score'] = 0
            result['prompt'] = p.prompt

            pics = [ProductPic(path=p.cover)] + [n for n in pics2 if not n.path == p.cover]
            for n in pics:
                result['pics'].append({
                    'img': PassMobileImg(n.path)
                })
            result['flag'] = 1

        except Exception, e:
            result['flag'] = 0
            result['msg'] = '数据异常：' + e

        self.write(simplejson.dumps(result))


@route(r'/mobile/product_cid/(\d+)', name='mobile_product_cid_detail')  # 手机端通过分类cid获取产品详情
class MobileProductCIDHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, cid):
        result = {}
        try:
            ft = (Product.categoryfront == cid) & (Product.status == 1)

            products = Product.select().where(ft)
            if products.count()>0:
                p = products[0]
                pics2 = p.pics
                result['pid'] = p.id
                result['time'] = int(time.time())
                result['name'] = p.name
                result['sku'] = p.sku
                result['cover'] = PassMobileImg(p.cover)
                result['resume'] = p.resume
                result['status'] = p.status
                result['quantity'] = 0
                result['pics'] = []
                result['score'] = 0 # p.score_num
                result['prompt'] = p.prompt

                pics = [ProductPic(path=p.cover)] + [n for n in pics2 if not n.path == p.cover]
                for n in pics:
                    result['pics'].append({
                        'img': PassMobileImg(n.path)
                    })
                result['flag'] = 1
            else:
                result['flag'] = 0
                result['msg'] = '没有可用的产品详情'
        except Exception, e:
            result['flag'] = 0
            result['msg'] = '数据异常：' + e

        self.write(simplejson.dumps(result))


@route(r'/mobile/category', name='mobile_category')  # 手机端分类列表
class MobileHomeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = []
        sid = self.get_argument('sid', None)  # 店铺ID
        if sid:
            list = CategoryFront.select().join(Product, on=(CategoryFront.id == Product.categoryfront)) \
                .where((Product.store == sid)).distinct()
        else:
            list = CategoryFront.select().where(CategoryFront.isactive == 1).order_by(
                CategoryFront.code)  # & (db.fn.Length(CategoryFront.code) == 12)
        for n in list:
            result.append({
                'name': n.name,
                'code': "'" + n.code + "'"
            })
        self.write(simplejson.dumps(result))


@route(r'/mobile/products', name='mobile_products')  # 手机端分类产品列表
class MobileHomeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def getProducts(self, ft):
        q = ProductStandard.select(ProductStandard, Product). \
            join(Product, on=(Product.id == ProductStandard.product)). \
            join(CategoryFront, on=(Product.categoryfront == CategoryFront.id)). \
            join(Store, on=(Store.id == ProductStandard.store)).where(ft)
        return q

    def get(self):
        order = self.get_argument("order", None)  # 排序
        sid = self.get_argument('sid', None)  # 店铺ID
        keyword = self.get_argument('keyword', None)  # 关键词
        code = self.get_argument("code", None)
        index = int(self.get_argument("index", 1))
        city_code = self.get_argument("city_code", None)

        version = self.get_argument("version", None)
        level = self.get_argument("level", None) #级别
        classes = self.get_argument("classes", None) #类别
        capacity = self.get_argument("capacity", None) #容量
        viscosity = self.get_argument("viscosity", None) #粘度
        configuration = self.get_argument("configuration", None) #配置
        CAN = self.get_argument("CAN", None) #CAN
        psize = self.get_argument("psize", None) #导航仪size
        jsize = self.get_argument("jsize", None) #记录仪
        lens = self.get_argument("lens", None) #镜头

        result = {'product': [], 'attribute': []}
        if city_code and code:
            key = code + '%'
            pinpai_id = Product.select().join(CategoryFront).where(CategoryFront.code == code)[0].pinpai
            pinpai_type = PinPai.get(id=pinpai_id).ptype
            #所有产品属性
            pptas = PPTAttribute.select()
            for ppta in pptas:
                tmpdict = {}
                if ppta.PinPaiType == pinpai_type:
                    pptaqs = PPTAQuantity.select().where(PPTAQuantity.PPTA_id==ppta.id)
                    tmpdict['name'] = ppta.name
                    tmpdict['ename'] = ppta.ename
                    tmpdict['value'] = [pptaq.name for pptaq in pptaqs]
                    tmpdict['arguments'] = []
                    for arg in tmpdict['value']:
                        tmpargdic = {}
                        tmpargdic['arg'] = arg
                        tmpargdic['value'] = 0
                        tmpdict['arguments'].append(tmpargdic)
                    result['attribute'].append(tmpdict)
            #对应产品
            ft = (ProductStandard.sale_status == 1) & (ProductStandard.is_sale == 1) & (CategoryFront.code % key)
            if sid:
                ft = ft & (ProductStandard.store == sid)
            if keyword:
                keyword = '%' + keyword + '%'
                ft = ft & ((Product.name % keyword) | (Store.name % keyword))
            if city_code.startswith('0004'):
                c_like = city_code[:4] + '%'
            else:
                c_like = city_code + '%'
            ft = ft & (ProductStandard.area_code % c_like)

            lubeEnable = 0
            navigatorEnable = 0
            recorderEnable = 0
            if pinpai_type.id == 1:    #润滑油 LubeAttribute
                if level:
                    quantitys = level.split(',')
                    qft = (LubeAttribute.level == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (LubeAttribute.level == quantity)
                    ft = qft & ft
                    lubeEnable = 1
                if classes:
                    quantitys = classes.split(',')
                    qft = (LubeAttribute.classes == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (LubeAttribute.classes == quantity)
                    ft = qft & ft
                    lubeEnable = 1
                if capacity:
                    quantitys = capacity.split(',')
                    qft = (LubeAttribute.capacity == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (LubeAttribute.capacity == quantity)
                    ft = qft & ft
                    lubeEnable = 1
                if viscosity:
                    quantitys = viscosity.split(',')
                    qft = (LubeAttribute.viscosity == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (LubeAttribute.viscosity == quantity)
                    ft = qft & ft
                    lubeEnable = 1
                if lubeEnable == 1:
                    q = ProductStandard.select(ProductStandard).\
                        join(Product, on=(Product.id == ProductStandard.product)).\
                        join(Store, on=(Store.id == ProductStandard.store)).\
                        join(CategoryFront, on=(Product.categoryfront == CategoryFront.id)).\
                        join(LubeAttribute, on=(Product.id == LubeAttribute.product)).where(ft);
                else:
                    q = self.getProducts(ft)
            elif pinpai_type.id == 3:    #大屏导航仪 NavigatorAttribute
                if configuration:
                    quantitys = configuration.split(',')
                    qft = (NavigatorAttribute.configuration == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (NavigatorAttribute.configuration == quantity)
                    ft = qft & ft
                    navigatorEnable = 1
                if CAN:
                    quantitys = CAN.split(',')
                    qft = (NavigatorAttribute.CAN == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (NavigatorAttribute.CAN == quantity)
                    ft = qft & ft
                    navigatorEnable = 1
                if psize:
                    quantitys = psize.split(',')
                    qft = (NavigatorAttribute.size == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (NavigatorAttribute.size == quantity)
                    ft = qft & ft
                    navigatorEnable = 1
                if navigatorEnable ==1:
                    q = ProductStandard.select(ProductStandard).\
                        join(Product, on=(Product.id == ProductStandard.product)).\
                        join(NavigatorAttribute, on=(Product.id == NavigatorAttribute.product)).\
                        join(CategoryFront, on=(Product.categoryfront == CategoryFront.id)).\
                        join(Store, on=(Store.id == ProductStandard.store)).where(ft)
                else:
                    q = self.getProducts(ft)
            elif pinpai_type.id == 4:    #记录仪 RecorderAttribute
                if jsize:
                    quantitys = jsize.split(',')
                    qft = (RecorderAttribute.size == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (RecorderAttribute.size == quantity)
                    ft = qft & ft
                    recorderEnable = 1
                if lens:
                    quantitys = lens.split(',')
                    qft = (RecorderAttribute.lens == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (RecorderAttribute.lens == quantity)
                    ft = qft & ft
                    recorderEnable = 1
                if recorderEnable == 1:
                    q = ProductStandard.select(ProductStandard).\
                        join(Product, on=(Product.id == ProductStandard.product)).\
                        join(RecorderAttribute, on=(Product.id == RecorderAttribute.product)).\
                        join(CategoryFront, on=(Product.categoryfront == CategoryFront.id)).\
                        join(Store, on=(Store.id == ProductStandard.store)).where(ft);
                else:
                    q = self.getProducts(ft)
            else:
                q = self.getProducts(ft)
            ps = q

            # order 排序0默认按权重 1价格从高到低 2价格从低到高 3销量从高到低 4销量从低到高
            if order == "1":
                ps = ps.order_by(ProductStandard.pf_price.desc())
            elif order == "2":
                ps = ps.order_by(ProductStandard.pf_price.asc())
            elif order == "3":
                ps = ps.order_by(ProductStandard.orders.desc())
            elif order == "4":
                ps = ps.order_by(ProductStandard.orders.asc())
            else:
                ps = ps.order_by(ProductStandard.weight.asc())
            paging_q = ps.paginate(index, 20)
            tmpList = []
            for n in paging_q:
                if n.id not in tmpList:
                    tmpList.append(n.id)
                    result['product'].append({
                        'psid': n.id,
                        'pid': n.product.id,
                        'name': n.product.name+' '+ n.copies,
                        'price': n.price,
                        'originalPrice': n.orginalprice,
                        'ourprice': n.pf_price, #门店价修改成批发价
                        'pf_price': n.pf_price,
                        'copies':  n.copies,
                        'unit': n.unit if n.unit else u'件',
                        'sku': n.product.sku,
                        'cover': PassMobileImg(n.product.cover),
                        'standard': n.name,
                        'resume': n.product.resume,
                        'storeName': n.store.name,
                        'sales': n.orders
                    })
        self.write(simplejson.dumps(result))


@route(r'/mobile/ads', name='mobile_ads')  # 手机端首页广告
class MobileADSHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        cid = self.get_argument("cityID", None)
        result = []
        fn = ((Ad.atype == 3) | (Ad.atype == 4) | (Ad.atype == 5)) & (Ad.flag == 1)
        if cid:
            fn = fn & ((Ad.city == cid) | (Ad.city >> None))
        else:
            fn = fn & (Ad.city >> None)
        ads = Ad.select().where(fn).order_by(Ad.sort.desc())
        for n in ads:
            result.append({
                'id': n.id,
                'img': n.picurl,
                'href': n.url,
                'title': n.imgalt,
                'atype': n.atype.id
            })

        self.write(simplejson.dumps(result))

@route(r'/mobile/ads_common', name='mobile_ads_common')  # 手机端通用广告接口
class MobileADSHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        cid = self.get_argument("cityID", None)
        category = self.get_argument("category", None)
        atypes = simplejson.loads(self.get_argument("atypes", '[]'))
        result = []
        fn = (Ad.atype << atypes)  & (Ad.flag == 1)
        if cid:
            fn = fn & ((Ad.city == cid) | (Ad.city >> None))
        else:
            fn = fn & (Ad.city >> None)
        if category:
            fn = fn & (Ad.remark == category)
        ads = Ad.select().where(fn).order_by(Ad.sort.desc())
        for n in ads:
            result.append({
                'id': n.id,
                'img': n.picurl,
                'href': n.url,
                'title': n.imgalt,
                'atype': n.atype.id
            })

        self.write(simplejson.dumps(result))

@route(r'/mobile/ads_store_buy', name='mobile_ads_store_buy')  # 门店端采购小分类
class MobileAdsStoreBuyHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        cid = self.get_argument("cityID", None)
        category = self.get_argument("category", None)
        result = []
        fn = ((Ad.atype == 6) | (Ad.atype == 7) | (Ad.atype == 8) & Ad.flag == 1)
        if cid:
            fn = fn & (Ad.city == cid)
        if category:
            fn = fn & (Ad.remark == category)
        ads = Ad.select().where(fn).order_by(Ad.sort.desc())
        for n in ads:
            result.append({
                'id': n.id,
                'img': n.picurl,
                'href': n.url,
                'title': n.imgalt,
                'atype': n.atype.id
            })

        self.write(simplejson.dumps(result))


@route(r'/mobile/shopcar', name='mobile_shopcar')  # 手机端购物车内容获取
class MobileShopCarHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = []
        psidlist = simplejson.loads(self.get_argument("psid", '[]'))
        if len(psidlist) > 0:
            q = ProductStandard.select(ProductStandard.id.alias('psid'), Product.id.alias('pid'), ProductStandard.sale_status,ProductStandard.quantity.alias('quantity'),
                                       ProductStandard.price,ProductStandard.orginalprice,ProductStandard.ourprice,ProductStandard.copies,ProductStandard.pf_price, Product.name, Product.cover, Product.sku, ProductStandard.store
                                       ).join(Product, on=(Product.id == ProductStandard.product)). \
                where((ProductStandard.id << psidlist)).dicts()  #
            for n in q:
                data = {
                    'psid': n['psid'],
                    'pid': n['pid'],
                    'name': n['name']+' '+n['copies'],
                    #'price': n['price'],  #价格修改为批发价
                    'price': n['pf_price'],
                    'originalPrice': n['orginalprice'],
                    #'ourprice': n['ourprice'],
                    'ourprice': n['pf_price'], #将门店价修改成批发价
                    'pf_price': n['pf_price'],
                    'cover': PassMobileImg(n['cover']),
                    'sku': n['sku'],
                    'status': n['sale_status'],
                    'flag': -1,
                    'msprice': 0,
                    'quantity': n['quantity'],
                    'storeid': n['store'],
                    'unit': u'件',
                    'copies': n['copies']
                }
                result.append(data)
        self.write(simplejson.dumps(result))

# 手机端注册验证码
@route(r'/mobile/vcode', name='mobile_vcode')
class MobileVCodeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': ''}
        mobile = self.get_argument("mobile")
        try:
            user = User.select().where((User.username == mobile) | (User.mobile == mobile))
            if user.count() > 0:
                result['msg'] = '您已经是车装甲会员'
            else:
                UserVcode.delete().where(UserVcode.created < (int(time.time()) - 30 * 60)).execute()
                uservcode = UserVcode()
                uservcode.mobile = mobile
                uservcode.vcode = random.randint(1000, 9999)
                uservcode.created = int(time.time())
                uservcode.flag = 0
                try:
                    uservcode.validate()
                    if UserVcode.select().where(UserVcode.mobile == mobile).count() > 3:
                        result['msg'] = '您发送验证码过于频繁，请稍后再试'
                    else:
                        try:
                            uservcode.save()
                            result['flag'] = 1
                            result['msg'] = '验证码发送成功，请查看短信'
                            sms = {'mobile': mobile, 'body': str(uservcode.vcode), 'signtype': '1', 'isyzm': 'vcode'}
                            create_msg(simplejson.dumps(sms), 'sms') #验证码
                        except Exception, ex:
                            result['msg'] = '验证码发送失败，请稍后再试'

                except Exception, ex:
                    result['msg'] = '手机号码无效'

        except Exception, e:
            result['msg'] = '系统异常'
        self.write(simplejson.dumps(result))

# 手机端注册
@route(r'/mobile/register', name='mobile_register')
class MobileRegisterHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def createRefereeUsers(self, refereeNum, mobile):
        try:
            ru = RefereeUsers()
            ru.refereeId = Referee.get(number=refereeNum).id
            ru.refereeNum = refereeNum
            ru.userMobile = mobile
            ru.save()
        except:
            logging.info('Error: Referee error, %s %s'%(refereeNum, mobile))

    def post(self):
        result = {'flag': 0}
        args = simplejson.loads(self.request.body)

        mobile = str(args["mobile"])
        password = str(args["password"])
        apassword = str(args["apassword"])
        vcode = str(args["vcode"])
        referee = ''
        if "referee" in args:
            referee = str(args["referee"])

        user = User()
        user.username = mobile
        user.password = password
        try:
            user.validate()
            if password and apassword:
                if password != apassword:
                    result['msg'] = "两次密码不一致，请重新输入"
                else:
                    if UserVcode.select().where((UserVcode.mobile == mobile) & (UserVcode.vcode == vcode) & (
                                UserVcode.flag == 0)).count() > 0:
                        now = int(time.time())
                        signupeddate = time.strftime('%Y-%m-%d', time.localtime(now))
                        signupedtime = time.strftime('%H:%M:%S', time.localtime(now))
                        user = User.create(username=user.username, password=user.password, mobile=user.mobile,
                                           signuped=now, lsignined=now, phoneactived=1,
                                           signupeddate=signupeddate, signupedtime=signupedtime)
                        create_user(user.id, user.id)
                        result['flag'] = 1
                        result['msg'] = {
                                         'birthday':'',
                                         'username': user.username,
                                         'nickname': user.nickname,
                                         'mobile': user.mobile,
                                         'score': user.score,
                                         'level': user.level,
                                         'cashed_money': user.cashed_money,
                                         'balance': user.balance,
                                         'id': user.id,
                                         'portraiturl': user.portraiturl,
                                         'bindmobile': user.bindmobile(),
                                         'hascheckedin': user.hascheckedin(),
                                         'store': None}
                        admins = AdminUser.select()
                        receivers = [n.email for n in admins if len(n.email) > 0]
                        email = {u'receiver': receivers, u'subject': u'新用户注册提醒',
                                 u'body': u"手机端有新用户注册车装甲；注册名为：" + user.username}
                        # 推广人员
                        self.createRefereeUsers(referee, mobile)
                    else:
                        result['msg'] = "请输入正确的验证码"
            else:
                result['msg'] = "请输入密码和确认密码"
        except Exception, ex:
            result['msg'] = ex.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/favorite', name='mobile_favorite')  # 手机客户端我的收藏
class MobileFavoriteHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'fav': [], 'fav_store': []}
        userid = self.get_argument("userid")
        products = ProductStandard.select(ProductStandard, Fav).join(Fav, on=(Fav.product_standard == ProductStandard.id)).where(
            Fav.user == userid)
        for n in products:
            result['fav'].append({
                'id': n.id,
                'name': n.product.name,
                'price': n.price,
                'originalPrice': n.orginalprice,
                'unit': n.unit if n.unit else u'件',
                'sku': n.product.sku,
                'cover': PassMobileImg(n.product.cover),
                'standard': n.name,
                'resume': n.product.resume,
                'status': n.product.status
            })
        stores = FavStore.select().join(Store, on=(Store.id == FavStore.store)).where(FavStore.user == userid)
        for n in stores:
            d = {'id': n.id,
                 'store_id': n.store.id,
                 'name': n.store.name,
                 'tags': n.store.tags,
                 'x': n.store.x,
                 'y': n.store.y,
                 'area_code': n.store.area_code,
                 'address': n.store.address,
                 'link_man': n.store.link_man,
                 'tel': n.store.tel,
                 'mobile': n.store.mobile,
                 'image': n.store.image,
                 'image_legal': n.store.image_legal,
                 'image_license': n.store.image_license,
                 'intro': n.store.intro,
                 'clicks': n.store.clicks,
                 'credit_score': n.store.credit_score,
                 'star_score': n.store.star_score,
                 'is_certified': n.store.is_certified,
                 'distance': n.store.image_legal,
                 'items': [],
                 'trait': n.store.trait}

            ps = ProductStandard.select() \
                .where((ProductStandard.store == n.id) & (ProductStandard.sale_status == 1)).order_by(ProductStandard.orders.desc()).limit(3)
            for n in ps:
                d['items'].append({
                    'psid': n.id,
                    'pid': n.product.id,
                    'name': n.product.name,
                    'sales': n.orders,
                    'resume': n.product.resume,
                    'price': n.price,
                    'orginal_price': n.orginalprice
                })
            result['fav_store'].append(d)
        self.write(simplejson.dumps(result))


@route(r'/mobile/order', name='mobile_order')  # 手机端我的订单
class MobilOrderHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'totalpage': 0, 'total': 0, 'items': []}
        userid = self.get_argument("userid")
        size = int(self.get_argument('size', 20))
        index = int(self.get_argument('index', 1))
        type = self.get_argument("type", 'all')
        q = True
        ft = (Order.user == userid) & (Order.status > -1) & (Order.userDel == 0)
        if type == 'unpay':  # 待付款订单
            ft = ft & ((Order.status == 0) & (Order.payment != 0))
        elif type == 'unway':  # 待收货订单
            ft = ft & (Order.status == 3)
        elif type == 'success':  # 已完成订单
            ft = ft & (Order.status == 4)
        elif type == 'unrecive':  # 已完成订单
            ft = ft & (Order.status == 3)
        elif type == 'unuse':  # 未使用
            q = OrderItemService.select(). \
                join(OrderItem, on=(OrderItem.id == OrderItemService.order_item)). \
                join(Order, on=(Order.id == OrderItem.order)). \
                group_by(Order).where(
                (OrderItemService.user == userid) & (OrderItemService.service_used == 0)).aggregate_rows()

        if type != 'unuse':
            q = Order.select().where(ft).order_by(Order.ordered.desc())
            result['total'] = q.count()
            if result['total'] % size > 0:
                result['totalpage'] = result['total'] / size + 1
            else:
                result['totalpage'] = result['total'] / size
            paging_q = q.paginate(index, size)
            for n in paging_q:
                s = ''
                itemcolor = 'item-stable'
                scolor = ''
                if n.status == -1:
                    continue
                elif n.status == 0 and n.payment > 0:
                    s = '待付款'
                    itemcolor = 'item-assertive'
                    scolor = 'assertive'
                elif n.status == 1 or n.status == 2 or (n.status == 0 and n.payment == 0):
                    s = '已付款'
                    itemcolor = 'item-balanced'
                    scolor = 'balanced'
                elif n.status == 3:
                    s = '待收货'
                    scolor = 'balanced'
                elif n.status == 4:
                    s = '交易完成'
                elif n.status == 5:
                    s = '已取消'

                result['items'].append({
                    'id': n.id,
                    'ordernum': n.ordernum,
                    'currentprice': n.currentprice,
                    'status': s,
                    'ordered': time.strftime('%Y-%m-%d', time.localtime(n.ordered)),
                    'scolor': scolor,
                    'itemcolor': itemcolor
                })
        elif type == 'unuse':
            result['total'] = q.count()
            if result['total'] % size > 0:
                result['totalpage'] = result['total'] / size + 1
            else:
                result['totalpage'] = result['total'] / size
            paging_q = q.paginate(index, size)

            for n in paging_q:
                result['items'].append({
                    'id': n.order_item.order.id,
                    'ordernum': n.order_item.order.ordernum,
                    'currentprice': n.order_item.order.currentprice,
                    'status': '未使用',
                    'ordered': time.strftime('%Y-%m-%d', time.localtime(n.order_item.order.ordered))
                })
        self.write(simplejson.dumps(result))


@route(r'/mobile/orderdetail', name='mobile_ordorderdetail')  # 手机端我的订单详情
class MobilOrderDetailHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {}
        oid = int(self.get_argument("id"))
        n = Order.get(id=oid)

        scolor = ''
        if n.status == -1:
            s = '已删除'
        elif n.status == 0 and n.payment:
            s = '待付款'
            scolor = 'assertive'
        elif (n.status == 0 and n.payment == 0) or n.status == 1:
            s = '待处理'
            scolor = 'assertive'
        elif n.status == 2:
            s = '正在处理'
            scolor = 'balanced'
        elif n.status == 3:
            s = '待收货'
            scolor = 'balanced'
        elif n.status == 4:
            s = '交易完成'
        elif n.status == 5:
            s = '已取消'
        else:
            s = str(n.status) + '-' + str(n.payment)

        p = ''
        if n.payment == 0:
            p = '货到付款'
        elif n.payment == 1:
            p = '支付宝'
        elif n.payment == 2:
            p = '账户余额'
        elif n.payment == 3:
            p = '网银支付'
        elif n.payment == 4:
            p = '合并支付'
        elif n.payment == 8:
            p = '积分换购'
        elif n.payment == 6:
            p = '微信支付'
        elif n.payment == 7:
            p = '银联支付'
        elif n.payment == 9:
            p = '系统补发'
        result['id'] = n.id
        result['ordernum'] = n.ordernum
        result['currentprice'] = n.currentprice
        result['status'] = s
        result['statusValue'] = n.status
        result['scolor'] = scolor
        result['ordered'] = time.strftime('%Y-%m-%d', time.localtime(n.ordered))
        result['paymentValue'] = n.payment
        result['payment'] = p
        result['take_name'] = n.take_name
        result['take_tel'] = n.take_tel
        result['take_address'] = n.take_address
        result['price'] = round(n.price, 2)
        result['shippingprice'] = n.shippingprice
        result['deliverynum'] = n.deliverynum
        result['balance'] = n.pay_balance
        result['order_type'] = n.order_type
        result['is_score'] = n.is_score
        result['scoreNum'] = n.scoreNum
        result['items'] = []
        for item in n.items:
            service = []
            for n in item.order_item_service:
                service.append(n.service_code)
            result['items'].append({
                'id': item.id,
                'psid': item.product.id,
                'hascomment': item.hascomment,
                'name': item.product.name+' '+item.product_standard.copies,
                'cover': item.product.cover,
                'quantity': item.quantity,
                'price': round(item.quantity * item.price, 2),
                'service_code':service,
                'scoreNum':item.product_standard.scoreNum,
                'copies':item.product_standard.copies
            })
        self.write(simplejson.dumps(result))


@route(r'/mobile/balance', name='mobile_balance')  # 手机客户端账户余额
class MobileBalanceHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {}
        userid = int(self.get_argument("userid", 0))
        minid = int(self.get_argument("minid", 99999999))
        user = User.get(id=userid)
        result['balance'] = str(user.balance)

        q = Balance.select().where((Balance.user == userid) & (Balance.isactive == 1)
                                   & (Balance.id < minid)).order_by(Balance.id.desc())
        balances = q.paginate(1, 20)
        result["items"] = []
        for b in balances:
            if b.stype == 0:
                type = '收入'
            else:
                type = '支出'
            log = b.log.split('-')[0]
            result["items"].append({
                'id': b.id,
                'stype': type,
                'amount': b.balance,
                'log': log,
                'created': time.strftime('%Y-%m-%d', time.localtime(b.created))
            })
        self.write(simplejson.dumps(result))


@route(r'/mobile/address', name='mobile_address')  # 手机端获取用户地址
class MobileAddressSHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = []
        userid = self.get_argument("userid")
        ads = UserAddr.select().where((UserAddr.user == userid) & (UserAddr.isactive == 1))
        for n in ads:
            result.append({
                'id': n.id,
                'province': n.province,
                'city': n.city,
                'region': n.region,
                'street': n.street,
                'address': n.address,
                'name': n.name,
                'tel': n.tel,
                'mobile': n.mobile,
                'isdefault': n.isdefault,
                'userid': userid
            })

        self.write(simplejson.dumps(result))


@route(r'/mobile/add_circle_topic', name='add_circle_topic')  # 手机端注册
class MobilAddCircleTopicHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        user_id = None
        content = None
        imgs = []

        if args.has_key("uid"):
            user_id = args["uid"]
        if args.has_key("content"):
            content = args["content"]
        if args.has_key("imgs"):
            imgs = args["imgs"]

        new_topic = CircleTopic.create(content=content, user=user_id, is_deleted=0, publish_from='APP', check_status=0,
                                       is_show_address=0, is_show_contact=1, created=int(time.time()))

        for img in imgs:
            path_dir = 'upload/' + str(user_id / 10000) + '/' + str(user_id)
            filename = '%d%d.%s' % (int(time.time()), random.randint(1000, 9999), 'png')
            if not os.path.exists('upload/' + str(user_id / 10000)):
                os.mkdir('upload/' + str(user_id / 10000))
            if not os.path.exists(path_dir):
                os.mkdir(path_dir)
            with open(path_dir + '/' + filename, "wb") as f:
                f.write(decodestring(img))
                CircleTopicPic.create(user=user_id, topic=new_topic.id, path='/' + path_dir + '/' + filename,
                                      created=int(time.time()))
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/addaddress', name='mobile_add_address')  # 手机端增加用户地址
class MobileAddAddressHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        try:
            province = args["province"]
            city = args["city"]
            region = args["region"]
            address = args["address"]
            street = args["street"]
            name = args["name"]
            tel = args["tel"]
            mobile = args["mobile"]
            userid = args["userid"]

            useraddr = UserAddr.create(user=userid, province=province, city=city, region=region, address=address,
                                       name=name, street=street, mobile=mobile, tel=tel, isdefault=0)

            result['msg'] = {
                'id': useraddr.id,
                'province': useraddr.province,
                'city': useraddr.city,
                'region': useraddr.region,
                'street': useraddr.street,
                'address': useraddr.address,
                'name': useraddr.name,
                'tel': useraddr.tel,
                'mobile': useraddr.mobile,
                'isdefault': useraddr.isdefault,
                'userid': userid
            }
            result['flag'] = 1
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/deladdress', name='mobile_deladdress')  # 手机端删除用户地址
class MobileDelAddressHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0}
        id = self.get_argument("id")
        addr = UserAddr.get(id=id)
        addr.isactive = 0
        addr.save()
        result["flag"] = 1
        self.write(simplejson.dumps(result))

    @require_basic_authentication
    def post(self):
        result = {'flag': 0}
        args = simplejson.loads(self.request.body)
        id = args["id"]
        addr = UserAddr.get(id=id)
        addr.isactive = 0
        addr.save()
        result["flag"] = 1
        self.write(simplejson.dumps(result))


# 手机端更新用户地址
@route(r'/mobile/updateaddress', name='mobile_updateaddress')
class MobileUpdateAddressHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        args = simplejson.loads(self.request.body)
        result = {'flag': 0, 'msg': ''}
        id = args["id"]
        province = args["province"]
        city = args["city"]
        region = args["region"]
        street = args["street"]
        address = args["address"]
        name = args["name"]
        tel = args["tel"]
        mobile = args["mobile"]
        try:
            addr = UserAddr.get(id=id)
            addr.province = province
            addr.city = city
            addr.region = region
            addr.address = address
            addr.name = name
            addr.tel = tel
            addr.street = street
            addr.mobile = mobile
            addr.save()
            result['flag'] = 1
        except:
            result['msg'] = '更新失败，请稍后再试'
            pass
        self.write(result)


@route(r'/mobile/defaultaddress', name='mobile_defaultaddress')  # 手机端设置默认用户地址
class MobileDefaultAddressHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        id = self.get_argument("id")
        addr = UserAddr.get(id=id)
        result = {'flag': 0, 'msg': ''}
        try:
            listUserAddrs = UserAddr.select().where((UserAddr.user == addr.user) & (UserAddr.isdefault == 1))
            for listUserAddr in listUserAddrs:
                listUserAddr.isdefault = 0
                listUserAddr.save()
            addr.isdefault = 1
            addr.save()
            result['flag'] = 1
        except:
            result['msg'] = '设置失败，请稍后再试'
        self.write(result)

    @require_basic_authentication
    def post(self):
        args = simplejson.loads(self.request.body)
        id = args["id"]
        addr = UserAddr.get(id=id)
        result = {'flag': 0, 'msg': ''}
        try:
            listUserAddrs = UserAddr.select().where((UserAddr.user == addr.user) & (UserAddr.isdefault == 1))
            for listUserAddr in listUserAddrs:
                listUserAddr.isdefault = 0
                listUserAddr.save()
            addr.isdefault = 1
            addr.save()
            result['flag'] = 1
        except:
            result['msg'] = '设置失败，请稍后再试'
        self.write(result)


@route(r'/mobile/profile', name='mobile_profile')  # 手机端获取用户个人信息
class MobileProfileAddressHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'cars': [], 'favorites': [], 'flag': 0, 'gifts': [], 'fav_stores': []}
        userid = self.get_argument("userid")
        favs = Fav.select().where(Fav.user == userid)
        for n in favs:
            result['favorites'].append(n.product_standard.id)
        fav_stores = FavStore.select().where(FavStore.user == userid)
        for n in fav_stores:
            result["fav_stores"].append(n.store.id)
        cars = Cart.select().where(Cart.user == userid)  # 2表示预订商品，不在购物车中显示  & (Cart.type != 2)
        for n in cars:
            if n.product_offline:
                poid = n.product_offline.id
            else:
                poid = 0
            result['cars'].append({
                'pid': n.product.id,
                'psid': n.product_standard.id,
                'quantity': n.quantity,
                'type': n.type,
                'poid': poid
            })
        current_time = time.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                                     '%Y-%m-%d %H:%M:%S')
        giftitem = Gift.select().where(
            (Gift.user == userid) & (Gift.status == 0) & (Gift.end_time > time.mktime(current_time)))
        for i in giftitem:
            reason = ''
            if i.type == 1:
                reason = u'秒杀'
            elif i.type == 2:
                reason = u'换购'
            elif i.type == 4:
                reason = u'转盘抽奖'
            elif i.type == 5:
                reason = u'预售'
            elif i.type == 3:
                reason = u'赠品'
            elif i.type == 9:
                reason = u'赠品'
            result['gifts'].append({
                'id': i.id,
                'psid': i.product_standard.id,
                'pid': i.product.id,
                'name': i.product.name,
                'cover': i.product.cover,
                'reason': reason,
                'price': 0,
                'quantity': i.quantity,
                'status': i.status,
                'expirs': i.end_time,
                'sku': i.product.sku,
                'type': i.type
            })
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/mergefav', name='mobile_mergefav')  # 手机端合并收藏
class MobileFavHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        args = simplejson.loads(self.request.body)
        userid = args["userid"]
        items = args["items"]
        stores = args["stores"]
        if args.has_key("f"):
            f = args["f"]  # 是否返回json格式结果
        Fav.delete().where(Fav.user == userid).execute()
        for n in items:
            ps = ProductStandard.get(id=n)
            Fav.create(favtime=int(time.time()), user=userid, product_standard=ps)
        FavStore.delete().where(FavStore.user == userid).execute()
        for n in stores:
            FavStore.create(user=userid, store=n, favtime=int(time.time()))
        result = 1
        if f and f == "json":
            result = {'flag': 1, 'msg': '','data':[]}
        self.write(simplejson.dumps(result))


@route(r'/mobile/mergecar', name='mobile_mergecar')  # 手机端合并购物车
class MobileMergeCarHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        args = simplejson.loads(self.request.body)
        userid = args["userid"]
        items = args["items"]
        if args.has_key("f"):
            f = args["f"]  # 是否返回json格式结果
        else:
            f = ''
        Cart.delete().where(Cart.user == userid).execute()  # & ((Cart.type == 0) | (Cart.type == 3))

        for n in items:
            type = 0
            try:
                type = n['type']
                if n['poid']:
                    Cart.create(product_standard=n['psid'], user=userid, product=n['pid'], quantity=n['quantity'],
                                type=3, product_offline=n['poid'], created=int(time.time()))
                else:
                    Cart.create(product_standard=n['psid'], user=userid, product=n['pid'], quantity=n['quantity'],
                                type=type)
            except:
                Cart.create(product_standard=n['psid'], user=userid, product=n['pid'], quantity=n['quantity'],
                            type=type)
        result = 1
        if f and f == "json":
            result = {'flag': 1, 'msg': '','data':[]}
        self.write(simplejson.dumps(result))


@route(r'/mobile/pay', name='mobile_pay')  # 手机端支付
class MobilePayHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    executor = ThreadPoolExecutor(80)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @require_basic_authentication
    def post(self):
        yield self.execPay(self)

    @run_on_executor
    def execPay(self, handler):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(handler.request.body)
        if 'id' in args:
            order = Order.get(id=args['id'])
            has_xiajia = OrderItem.select().join(ProductStandard).where((OrderItem.order == order) & (ProductStandard.sale_status != 1))
            if has_xiajia.count() > 0:
                result['msg'] = '您的订单中包含下架商品，请重新下单'
            else:
                result['orderid'] = order.id
                mscheck = True  # 检查用户今天是否秒杀过
                today_start_time = time.mktime(
                    time.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d"))
                msItems = OrderItem.select().where((OrderItem.order == order) & (OrderItem.item_type == 1))
                if msItems.count() > 0:
                    today_ms = OrderItem.select().join(Order).where((Order.status < 5) & (Order.status > 0) &
                                                                    (Order.user == order.user) & (
                                                                        OrderItem.item_type == 1) & (
                                                                        Order.ordered >= today_start_time))
                    if today_ms.count() > 0:
                        mscheck = False
                        result['msg'] = u'您今天已经秒杀过产品了，每位会员每天仅能秒杀一个商品'
                if mscheck:
                    items = OrderItem.select().where((OrderItem.order == order) & (OrderItem.item_type == 0))
                    if items.count() > 0:
                        # 检查商品是否限购商品
                        # 查出该商品今天该用户购买过几次
                        # 查出该商品库存多少
                        # 当次购买需《每日限购 《库存；否则：mscheck=False
                        jrmsg = u''
                        for n in items:
                            if n.product_standard.xgperusernum > 0:
                                today_ms = OrderItem.select().join(Order). \
                                    where((Order.status < 5) & (Order.status > 0) &
                                          (0 == OrderItem.item_type) & (Order.ordered >= today_start_time) & (
                                              Order.user == order.user)
                                          & (OrderItem.product_standard == n.product_standard))
                                jrgmcs = today_ms.count()
                                if jrgmcs + n.quantity > n.product_standard.xgperusernum:
                                    mscheck = False
                                    jrmsg += n.product.name + u' 超出了今日限购次数;'
                        if not mscheck:
                            result['msg'] = u'您购买的商品' + jrmsg

                if mscheck:  # 检查是否存在秒杀活动结束的商品
                    now = time.time()
                    activityMsg = u''
                    for item in order.items:
                        if item.item_type == 1:
                            activityProducts = Product_Activity.select().where(
                                (Product_Activity.product_standard == item.product_standard) &
                                (Product_Activity.status == 1) &
                                (now >= Product_Activity.begin_time) & (now <= Product_Activity.end_time))
                            if activityProducts.count() == 0:
                                mscheck = False
                                activityMsg += item.product.name + u'、'
                    if not mscheck:
                        result['msg'] = activityMsg[0:-1] + u'秒杀活动已经结束，感谢您的关注'
                    else:
                        if args['paymentValue'] == "1":  # 支付宝手机版
                            response_url = get_pay_url(order.ordernum.encode('utf-8'), u'车装甲商品',
                                                        str(order.currentprice))
                            if len(response_url) > 0:
                                result['url'] = response_url
                            else:
                                result['url'] = ''
                            result['flag'] = 2
                        elif args['paymentValue'] == "0":  # 货到付款
                            order.payment = 0
                            order.status = 1
                            order.save()
                            result['flag'] = 1
                        elif args['paymentValue'] == "2":  # 账户余额
                            balance = Balance()
                            balance.user = order.user
                            balance.balance = round(order.currentprice - order.pay_balance, 2)
                            balance.stype = 1
                            balance.log = u'余额支付-订单编号：' + order.ordernum
                            balance.created = int(time.time())
                            balance.save()
                            order.payment = 2
                            order.pay_balance = order.currentprice
                            order.status = 1
                            order.save()
                            result['flag'] = 1
                        elif args['paymentValue'] == "6":
                            result = UnifiedOrder_pub().getPrepayId(order.ordernum.encode('utf-8'), u'商品价格', int(order.currentprice*100))
                            result['flag'] = 3
                            result['orderid'] = order.ordernum.encode('utf-8')
                        elif args['paymentValue'] == '7':  # 银联支付
                            tn = Trade().trade(order.ordernum.replace('-', ''), order.currentprice)
                            result = {}
                            if tn:
                                result['tn'] = tn
                                result['flag'] = 4
                            else:
                                result['flag'] = 0
        else:
            addrid = args["addrid"]
            userid = args["userid"]
            payment = args['payment']
            price = args['price']  # 订单价格
            currentprice = args['currentprice']  # 实际价格
            shippingprice = args['shippingprice']  # 物流价格
            delivery_day = args["delivery_day"]  # 送货时间
            items = args.get('items', [])  # 订单内容
            msg = args['msg']  # 订单留言
            giftitems = args.get('giftitems', [])  # 赠送商品/礼品集合
            yitems = args.get('yitems', [])  # 预定商品集合
            storeid = args.get('storeid', None)  # 预定商品集合
            mscheck = True  # 检查用户今天是否秒杀过
            order_type = 0
            today_start_time = time.mktime(
                time.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d"))

            if len(items) > 0:
                # 检查商品是否限购商品
                # 查出该商品今天该用户购买过几次
                # 查出该商品库存多少
                # 当次购买需《每日限购 《库存；否则：mscheck=False
                jrmsg = u''
                for n in items:
                    ps = ProductStandard.get(id=n['psid'])
                    if ps.xgperusernum > 0:
                        today_ms = OrderItem.select().join(Order). \
                            where((Order.status < 5) & (Order.status > 0) &
                                  (0 == OrderItem.item_type) & (Order.ordered >= today_start_time) & (
                                      Order.user == userid)
                                  & (OrderItem.product_standard == n['psid']))
                        jrgmcs = today_ms.count()
                        if jrgmcs + n['quantity'] > ps.xgperusernum:
                            mscheck = False
                            jrmsg += ps.product.name + u' 超出了今日限购次数;'
                        elif n['quantity'] > ps.xgtotalnum:
                            mscheck = False
                            jrmsg += ps.product.name + u' 已经售完;'
                if not mscheck:
                    result['msg'] = u'您购买的商品' + jrmsg

            if mscheck:  # 检查是否存在秒杀活动结束的商品
                now = time.time()
                coupon = None  # 优惠券
                is_store = None
                if storeid:
                    is_store = storeid
                try:
                    coupon_code = args["coupon_code"]  # 优惠券编码
                    if coupon_code:
                        coupon = Coupon.get(Coupon.code == coupon_code)
                    balance = args["balance"]  # 账户余额支付金额
                except:
                    balance = 0
                address = UserAddr.get(id=addrid)
                psids = [n['psid'] for n in items]

                has_xiajia = ProductStandard.select().where((ProductStandard.id << psids) & (ProductStandard.sale_status != 1))
                if len(psids) > 0 and has_xiajia.count() > 0:
                    result['msg'] = '您的订单中包含下架商品，请重新下单'
                else:
                    order_weight = 0.0
                    itemList = []
                    storeList = []
                    for n in items:
                        ps = ProductStandard.get(id=n['psid'])
                        orderItem = OrderItem()
                        orderItem.product = ps.product.id
                        orderItem.product_standard = ps
                        orderItem.price = ps.pf_price
                        orderItem.weight = ps.weight
                        orderItem.quantity = n['quantity']
                        orderItem.product_standard_name = ps.name
                        orderItem.item_type = 0
                        orderItem.hascomment = ps.weights  # 存储权重，用于排序
                        itemList.append(orderItem)
                        order_weight += round((ps.weight / 500 * n['quantity']), 2)
                        is_store = orderItem.product_standard.store
                        if is_store in storeList:
                            pass
                        else:
                            storeList.append(is_store)

                    if len(itemList) == 0:
                        result['msg'] = '订单中至少需要选择一件商品'
                    else:
                        with db.handle.transaction():
                            orderList = []
                            for o in storeList:
                                order = Order()
                                if delivery_day == '':
                                    order.distributiontime = '工作日/周末/假日均可'
                                elif delivery_day == 'weekend':
                                    order.distributiontime = '仅周末送货'
                                elif delivery_day == 'weekday':
                                    order.distributiontime = '仅工作日送货'
                                elif delivery_day == 'morning':
                                    order.distributiontime = '早上8点到11点'
                                elif delivery_day == 'noon':
                                    order.distributiontime = '早上11点到下午4点'
                                elif delivery_day == 'afternoon':
                                    order.distributiontime = '下午4点到7点'
                                order.user = userid
                                order.message = msg
                                order.address = addrid
                                order.take_name = address.name
                                order.take_tel = address.mobile + ' ' + address.tel
                                order.take_address = address.province + ' ' + address.city + ' ' + address.region + ' ' + address.address

                                order.ordered = int(time.time())
                                order.ordereddate = time.strftime('%Y-%m-%d', time.localtime(order.ordered))
                                order.orderedtime = time.strftime('%H:%M:%S', time.localtime(order.ordered))
                                order.payment = payment

                                store_price = 0
                                store_weight = 0
                                order_count = len(itemList)
                                for orderItem in itemList:
                                    if orderItem.product_standard.store == o:
                                        store_price += orderItem.price * orderItem.quantity
                                        store_weight += orderItem.weight * orderItem.quantity

                                if order_count > 1:
                                    order.price = store_price
                                    order.currentprice = store_price
                                    order.weight = store_weight
                                    order.pay_balance = balance / order_count
                                else:
                                    order.price = price
                                    order.currentprice = currentprice
                                    order.weight = order_weight
                                    order.pay_balance = balance
                                order.shippingprice = shippingprice
                                order.status = 0
                                order.ip = self.request.remote_ip
                                order.order_from = 2  # 手机下单
                                order.order_type = order_type
                                order.store = o
                                order.save()
                                order.ordernum = 'U' + str(order.user.id) + 'S' + str(order.id)
                                itemList = sorted(itemList, key=lambda orderItem: orderItem.hascomment, reverse=True)
                                storeProductNum = order.ordernum #卖家订单号
                                storeProductNames = ''           #卖家卖的所有商品
                                for orderItem in itemList:
                                    if orderItem.product_standard.store == o:
                                        orderItem.hascomment = 0  # 存储权重，完成，初始化回去
                                        orderItem.order = order.id
                                        storeProductNames += orderItem.product.name
                                        orderItem.save()
                                        orderItem.product_standard.orders += 1
                                        orderItem.product_standard.save()  # 产品购买次数累计

                                        delCar = Cart.delete().where(
                                            (Cart.user == userid) & (
                                                Cart.product_standard == orderItem.product_standard))
                                        delCar.execute()  # 情况该item的购物车
                                #给卖家发短信
                                sms = {'mobile': o.mobile, 'body': u'订单号：%s 所购商品：%s'%(storeProductNum ,storeProductNames),
                                       'signtype': '1', 'isyzm': 'placeOrderToServer'}  # 有客户下单请查看
                                create_msg(simplejson.dumps(sms), 'sms')  # 下单

                                if (order_weight > int(order_weight)):
                                    order.freight = 5 + int(
                                        order_weight - 1.0) * 0.5  # 5是首重运费，order_weight单位是斤，超过一公斤每斤加五毛，不足一斤算一斤
                                else:
                                    order.freight = 5 + (order_weight - 2) * 0.5
                                # 修改优惠券状态
                                if coupon:
                                    coupon.status = 2
                                    coupon.save()
                                    # 更新订单中的优惠券信息
                                    order.coupon = coupon.id
                                order.save()
                                orderList.append(order)
                            oNum = ''
                            oId = ''
                            for oItem in orderList:
                                oNum += oItem.ordernum + '-'
                                oId += str(oItem.id) + '-'
                            if str(payment) == '0':  # 货到付款
                                for oItem in orderList:
                                    oItem.status = 1
                                    result['flag'] = 1
                                    oItem.save()
                            elif str(payment) == '1':  # 支付宝手机端
                                response_url = get_pay_url(oNum[:-1], u'车装甲商品', currentprice)
                                if len(response_url) > 0:
                                    result['url'] = response_url
                                else:
                                    result['url'] = ''
                                result['flag'] = 2
                            elif str(payment) == '2':  # 账户余额
                                user = User.get(id=userid)
                                if user.balance >= float(balance):
                                    b = Balance()
                                    b.user = userid
                                    b.balance = balance
                                    b.stype = 1
                                    b.log = u'余额支付，订单编号：' + oNum[:-1]
                                    b.created = int(time.time())
                                    b.save()

                                    for oItem in orderList:
                                        oItem.status = 1
                                        oItem.save()

                                    for n in itemList:
                                        if n.product.categoryfront.type == '2':
                                            sn = 1
                                            for s in range(n.quantity):
                                                sn = sn + s
                                                seed = "1234567890"
                                                sa = []
                                                for i in range(12):
                                                    sa.append(random.choice(seed))
                                                    salt = ''.join(sa)
                                                OrderItemService.create(order_item=n.id, sn=sn, service_code=salt, service_used=0, store=order.store, user=order.user)

                                    result['flag'] = 1
                                else:
                                    result['msg'] = '账户余额不足'
                            elif str(payment) == '3':  # 网银支付
                                result['flag'] = 2
                                pass
                            elif str(payment) == '4':  # 合并支付，剩余使用支付宝
                                b = Balance()
                                b.user = userid
                                b.balance = balance
                                b.stype = 1
                                b.log = '合并支付-订单编号：' + oNum[:-1] + ' 余额支付部分金额：' + str(b.balance)
                                b.created = int(time.time())
                                b.save()
                                for oItem in orderList:
                                    oItem.payment = 1
                                    oItem.save()
                                response_url = get_pay_url(oNum[:-1], u'车装甲商品',
                                                           round(currentprice - balance, 2))
                                if len(response_url) > 0:
                                    result['url'] = response_url
                                else:
                                    result['url'] = ''
                                result['flag'] = 2
                            elif str(payment) == '5':  # 合并支付，手机合并余额与货到付款
                                b = Balance()
                                b.user = userid
                                b.balance = balance
                                b.stype = 1
                                b.log = '合并支付-订单编号：' + oNum[:-1] + ' 余额支付部分金额：' + str(b.balance)
                                b.created = int(time.time())
                                b.save()
                                for oItem in orderList:
                                    oItem.status = 1
                                    oItem.payment = 0
                                    oItem.save()
                                result['flag'] = 1
                            elif str(payment) == '6':  # 微信手机端支付
                                result = UnifiedOrder_pub().getPrepayId(oNum[:-1], u'商品价格', int(currentprice*100))
                                result['flag'] = 3
                            elif str(payment) == '7':  # 银联支付
                                tn = Trade().trade(oNum[:-1].replace('-', ''), currentprice)
                                result = {}
                                if tn:
                                    result['tn'] = tn
                                    result['flag'] = 4
                                else:
                                    result['flag'] = 0
                            result['orderid'] = oId[:-1]
        handler.write(simplejson.dumps(result))
        return result

#保单支付成功短信
def sendMsgInsuranceOrder(mobile, storeName, area_code, ordernum, iName, payment, LubeOrScore, summary, price):
        mobiles = setting.financeMobiles
        if payment == 1:
            paymentV = '支付宝'
        elif payment == 6:
            paymentV = '微信支付'
        elif payment == 7:
            paymentV = '银联支付'
        else:
            paymentV = '其它方式支付'
        if LubeOrScore == 2:
            gift = u'返佣返积分'
        else:
            gift = u'返佣返油'
        addrs = Area().get_detailed_address(area_code)
        # to 客户
        sms = {'mobile': mobile, 'body': [storeName, addrs, ordernum, iName, paymentV, gift, summary],
               'signtype': '1', 'isyzm': 'paySuccess'}
        create_msg(simplejson.dumps(sms), 'sms')
        # to 财务
        summary = u'订单总额 %s, 客户 %s'%(price, mobile)
        sms = {'mobile': mobiles, 'body': [storeName, addrs, ordernum, iName, paymentV, gift, summary],
               'signtype': '1', 'isyzm': 'paySuccess'}
        create_msg(simplejson.dumps(sms), 'sms')
        if area_code.startswith('0004'):
            sms = {'mobile': setting.ShanXiIphone, 'body': [storeName, addrs, ordernum, iName, paymentV, gift, summary],
                   'signtype': '1', 'isyzm': 'paySuccess'}
            create_msg(simplejson.dumps(sms), 'sms')


def changeOrdersStatus(ordernum, payment):
    msgFlag = 0
    try:
        if ('I' in ordernum) or ('B' in ordernum):
            order = InsuranceOrder.get(ordernum = ordernum)
            if order.status == 1:
                order.status = 2
                msgFlag = 1
        else:
            order = Order.get(ordernum = ordernum)
            if (order.status == 0) and ('S' in ordernum):
                order.status = 1
        order.pay_from = 2
        order.payment = payment
        order.pay_account = ordernum  #
        order.trade_no = ordernum
        order.paytime = int(time.time())  # 支付时间
        order.save()
        logging.info('orderid=%s ordernum=%s payment=%s\n' % (order.id, order.ordernum, payment))
        return (order, msgFlag)
    except Exception, e:
        file_object = open('/home/pay.log', 'a')
        file_object.writelines('Error: change order status error; ordernum %s,payment %s,log: %s'%(ordernum, payment, e.message))
        file_object.close()
        logging.info('Error: change order status error; ordernum %s,payment %s,log: %s'%(ordernum, payment, e.message))
        return (0, 0)


# 银联支付完成后异步通知 银联回调
@route(r'/mobile/upay_notify', name='mobile_upay_notify')
class MobileUPayCallbackHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass
    def options(self):
        pass
    def post(self):
        result = {}
        result['return_code'] = 'FAIL'
        try:
            params = Trade().smart_str_decode(self.request.body)
            if params['respMsg'] == 'Success!':
                order, msgFlag = changeOrdersStatus(params['orderId'], 7)
                if msgFlag and order:
                    sendMsgInsuranceOrder(order.mobile, order.store.name, order.store.area_code, order.ordernum,
                                          order.insurance.name ,order.payment, order.LubeOrScore, order.summary, order.price)
                    result['return_code'] = 'SUCCESS'
            else:
                result['return_msg'] = 'get FAIL notify'
        except Exception, e:
            logging.info('Error: upay error %s'%e.message)

        self.write(simplejson.dumps(result))

# 微信支付完成后异步通知 微信回调
@route(r'/mobile/weixin_notify', name='mobile_weixinpay_notify')
class MobileWeiXinPayCallbackHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass
    def options(self):
        pass
    def post(self):
        result={}
        params = Common_util_pub().xmlToArray(self.request.body)
        result['return_code'] = 'FAIL'
        if params['return_code'] != 'SUCCESS':
            result['return_msg'] = 'get FAIL notify'
        else:
            order, msgFlag = changeOrdersStatus(params['out_trade_no'], 6)
            if msgFlag and order:
                sendMsgInsuranceOrder(order.mobile, order.store.name, order.store.area_code, order.ordernum,
                                          order.insurance.name ,order.payment, order.LubeOrScore, order.summary, order.price)
                result['return_code'] = 'SUCCESS'
        self.write(simplejson.dumps(result))

# 手机端支付完成回调
@route(r'/mobile/alipay_callback', name='mobile_alipay_callback')
class MobileAlipayCallbackHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        self.write('')

# 支付宝支付完成后异步通知 支付宝回调
@route('/mobile/alipay_notify', name='mobile_alipay_notify')
class MobileAlipayNotifyHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass
    def options(self):
        pass
    def post(self):
        msg = "fail"
        params = {}
        ks = self.request.arguments.keys()
        for k in ks:
            params[k] = self.get_argument(k)
        ps = notify_verify(params)
        if ps:
            if ps['trade_status'].upper().strip() == 'TRADE_FINISHED' or ps['trade_status'].upper().strip() == 'TRADE_SUCCESS':
                order, msgFlag = changeOrdersStatus(ps['out_trade_no'], 1)
                if msgFlag and order:
                    sendMsgInsuranceOrder(order.mobile, order.store.name, order.store.area_code, order.ordernum,
                                          order.insurance.name ,order.payment, order.LubeOrScore, order.summary, order.price)
                    msg = "success"
        self.write(msg)


@route(r'/mobile/cancelorder', name='mobile_cancel_order')  # 手机端取消订单
class MobileCancelOrderHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': '取消失败，请稍后再试'}
        args = simplejson.loads(self.request.body)
        oid = args["id"]
        refund = args["refund"]
        n = Order.get(id=oid)
        n.canceltime = int(time.time())
        try:
            OrderChangeStatus(oid, 5, refund, self)
            # n.change_status(5)
            # n.save()
            result['flag'] = 1
            result['msg'] = '取消订单成功'
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/dealorder', name='mobile_deal_order')  # 手机端处理订单
class MobileDealOrderHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': '处理失败，请稍后再试'}
        args = simplejson.loads(self.request.body)
        oid = args["id"]
        n = Order.get(id=oid)
        n.canceltime = int(time.time())
        try:
            OrderChangeStatus(oid, 2, 1, self)
            # n.change_status(5)
            # n.save()
            result['flag'] = 1
            result['msg'] = '处理订单成功'
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))

@route(r'/mobile/shouorder', name='mobile_show_order')  # 手机端确定收货
class MobileShouOrderHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': '处理失败，请稍后再试'}
        args = simplejson.loads(self.request.body)
        oid = args["id"]
        n = Order.get(id=oid)
        n.canceltime = int(time.time())
        try:
            OrderChangeStatus(oid, 4, 1, self)
            # n.change_status(5)
            # n.save()
            result['flag'] = 1
            result['msg'] = '确定收货成功'
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))

@route(r'/mobile/alipay_cz_callback', name='mobile_alipay_callback_cz')  # 手机端充值完成回调
class MobileAlipayCallbackCZHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        self.write('')


@route('/mobile/alipay_cz_notify', name='mobile_alipay_notify_cz')  # 支付宝充值完成后异步通知
class MobileAlipayNotifyCZHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        msg = "fail"
        params = {}
        ks = self.request.arguments.keys()

        for k in ks:
            params[k] = self.get_argument(k)
        ps = notify_verify(params)
        if ps:
            file_object = open('/home/alipay.txt', 'w+')
            file_object.writelines('ps = ' + simplejson.dumps(ps))
            file_object.close()
            if ps['trade_status'].upper().strip() == 'TRADE_FINISHED' or \
                            ps['trade_status'].upper().strip() == 'TRADE_SUCCESS':
                tn = ps["out_trade_no"]
                try:
                    orders = InsuranceOrder.select().where(InsuranceOrder.ordernum==tn).limit(1)
                    orders[0].status=2
                    orders[0].save()
                    msg = "success"
                except Exception, e:
                    file_object = open('/home/alipay.txt', 'w+')
                    file_object.writelines('cz-err = ' + e.message)
                    file_object.close()
                    pass
        self.write(msg)


@route(r'/mobile/alipay_cz', name='mobile_alipay_cz')  # 手机端充值
class MobileAlipayCallbackCZHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': '由于车装甲仓库搬迁，自今日起暂停服务一个月。'}
        self.write(simplejson.dumps(result))
        # args = simplejson.loads(self.request.body)
        # price = args['price']  # 充值金额
        # result = {'flag': 0, 'msg': '充值失败，请稍后再试'}
        # userid = args['userid']
        #
        # tn = 'S' + str(userid) + '-CZ' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        # response_url = get_pay_url(tn, u'车装甲充值', price, True)
        # if len(response_url) > 0:
        #     result['url'] = response_url
        #     result['flag'] = 1
        # else:
        #     result['url'] = ''
        # self.write(simplejson.dumps(result))


@route(r'/mobile/cost/status', name='mobile_alipay_cz_check')  # 手机端充值检查
class MobileAlipayCallbackCZCheckHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        userid = self.get_argument("userid")
        price = float(self.get_argument("price", 0))
        maxid = int(self.get_argument("maxid", 99999999))
        result = {'flag': 0}

        q = Balance.select().where((Balance.stype == 0) & (Balance.isactive == 1) & (Balance.id > maxid)
                                   & (Balance.user == userid)).order_by(Balance.id).limit(1)
        if q.count() > 0:
            balance = q[0]
            if round(balance.balance, 2) == round(price, 2):
                result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/order/status', name='mobile_alipay_order_check')  # 手机端订单检查
class MobileAlipayCallbackCheckHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        orderid = self.get_argument("orderid")
        result = {'flag': 0}

        q = Order.select().where((Order.status > 0) & (Order.status < 5) & (Order.id == orderid))
        if q.count() > 0:
            result['flag'] = 1

        self.write(simplejson.dumps(result))


@route(r'/mobile/payinfo', name='mobile_payinfo')  # 手机端获取用户地址与余额信息
class MobilePayInfoHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'address': [], 'balance': 0, 'coupons': []}
        userid = self.get_argument("userid")
        price = float(self.get_argument('price', '0'))
        user = User.get(id=userid)
        result['balance'] = user.balance
        result['score'] = user.score
        ads = UserAddr.select().where((UserAddr.user == userid) & (UserAddr.isactive == 1))
        for n in ads:
            result['address'].append({
                'id': n.id,
                'province': n.province,
                'city': n.city,
                'region': n.region,
                'address': n.address,
                'street': n.street,
                'name': n.name,
                'tel': n.tel,
                'mobile': n.mobile,
                'isdefault': n.isdefault,
                'userid': userid
            })
        now = int(time.time())
        coupons = Coupon.select(Coupon.id, CouponTotal.name, CouponTotal.price). \
            join(CouponTotal). \
            where((Coupon.user == user) & (Coupon.status == 1) & (CouponTotal.minprice <= price) &
                  (Coupon.starttime <= now) & (Coupon.endtime >= now)).dicts()
        for n in coupons:
            result['coupons'].append({'id': n['id'], 'name': n['name'], 'price': n['price']})
        result['freeshippingfee'] = setting.FreeshippingFee
        result['shippingfee'] = setting.ShippingFee
        result['hascheckedin'] = user.hascheckedin()
        result['discountthreshold'] = setting.Full_Price
        result['discount'] = setting.Reduce_Price
        self.write(simplejson.dumps(result))

# 手机端程序更新
@route(r'/mobile/update/(\S+)', name='mobile_verison')
class MobileVersionHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def loadVersion(self):
        result = json.load(urllib2.urlopen(setting.iosCheckVersionURL, timeout=10))
        return (result['results'][-1]['version'], result['results'][-1]['releaseNotes'])

    def get(self, client):
        order_str = MobileUpdate.updatedtime.desc()
        ft = (MobileUpdate.state == 1) & (MobileUpdate.client == client)
        q = MobileUpdate.select().where(ft)
        lists = q.order_by(order_str).limit(1)
        result = {'version': '', 'baseUrl': '', 'isForce': 'false', 'flag':0, 'releaseNotes':''}
        try:
            if lists.count()>0:
                update = lists[0]
                result['version'] = update.version
                result['isForce'] = update.isForce
                result['releaseNotes'] = update.instructions
                if update.client == 'android_b' or update.client == 'android_c':
                    result['baseUrl'] = "http://www.520czj.com" + update.path +'?r=' + str(time.time())
                result['flag'] = 1
        except Exception, e:
            logging.info('Error: mobile/update/%s %s'%(client, e.message))
        self.write(simplejson.dumps(result))


@route(r'/mobile/comment/add', name='mobile_comment_add')  # 手机端增加评论
class MobileCommentAddHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        args = simplejson.loads(self.request.body)
        result = {'flag': 0, 'msg': ''}
        try:
            if args.has_key("f"):
                f = args["f"]  # 是否返回json格式结果
            userId = args["userId"]
            # orderId = self.get_argument("orderId")
            oiid = args["oiid"]
            psid = args["psid"]
            content = args["content"]
            productRate = args["productRate"]  # 商品质量
            speedRate = args["speedRate"]  # 发货速度
            priceRate = args["priceRate"]  # 商品价格
            serviceRate = args["serviceRate"]  # 服务质量
            c = Comment.create(product=psid, user=userId, qualityscore=productRate, speedscore=speedRate,
                               pricescore=priceRate,
                               servicescore=serviceRate, comment=content, created=int(time.time()), approvedby=22,
                               status=1)
            item = OrderItem.get(id=oiid)
            item.hascomment = 1
            item.save()
            if f and f == "json":
                result['flag'] = 1
            result['msg'] = {
                'id': c.id,
                'psid': c.product.id,
                'userId': c.user.id,
                'productRate': c.qualityscore,
                'speedRate': c.speedscore,
                'priceRate': c.pricescore,
                'serviceRate': c.servicescore,
                'content': c.comment,
                'created': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(c.created)),
                'status': c.status
            }
            try:
                pass
                # user = User.get(id=userId)

                # 如果评价超过30字，并且全五星好评，赠送抽奖机会一次
                # if len(content) > 30:  # and productRate == 5 and speedRate == 5 and priceRate == 5 and serviceRate == 5
                #     user.raffle_count += 1
                #     user.save()

                # ul = UserLevel.get(levelid=user.userlevel)
                # if ul:
                #     stype = 0
                #     jftype = 1
                #     scorenum = ul.commentscore
                #     log = u'会员评价商品获得%s奖励积分'
                #     log = log % (scorenum)
                #     user.updatescore(stype, jftype, scorenum, log)
            except Exception, ex:
                if f and f == "json":
                    result['flag'] = 0
                result['msg'] = ex.message
        except Exception, e:
            if f and f == "json":
                result['flag'] = 0
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/comment/list', name='mobile_comment_list')  # 手机端获取产品评价列表
class MobileCommentListHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'items': [], 'total': 0, 'totalpage': 0}
        psid = self.get_argument("psid")
        page = int(self.get_argument("index"))
        pagesize = int(self.get_argument("size"))
        ps = ProductStandard.get(id=psid)
        comments = Comment.select().where(
            (Comment.product == ps.product) & ((Comment.status == 1) | (Comment.status == 2)))
        total = comments.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        cs = comments.order_by(Comment.created.desc()).paginate(page, pagesize)

        for n in cs:
            result['items'].append({
                'id': n.id,
                'pid': n.product.id,
                'userid': n.user.id,
                'nickname': n.user.nickname,
                'username': n.user.username,
                'productRate': n.qualityscore,
                'speedRate': n.speedscore,
                'priceRate': n.pricescore,
                'serviceRate': n.servicescore,
                'content': n.comment,
                'created': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(n.created))
            })
        result['total'] = total
        result['totalpage'] = totalpage
        self.write(simplejson.dumps(result))


@route(r'/mobile/coupons', name='mobile_coupons')  # 手机端获取优惠券
class MobileCommentListHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = []
        userid = self.get_argument("userid")
        type = self.get_argument("type")
        current_time = time.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                                     '%Y-%m-%d %H:%M:%S')
        ft = (Coupon.user == int(userid))
        if type == 'unuse':
            ft = ft & (Coupon.status == 1)
            coupons = Coupon.select(Coupon, CouponTotal).join(CouponTotal, on=(
                (Coupon.coupontotal == CouponTotal.id) & (Coupon.endtime > time.mktime(current_time)) & (
                    Coupon.starttime < time.mktime(current_time)))).where(ft)
        elif type == 'used':
            ft = ft & (Coupon.status == 2)
            coupons = Coupon.select(Coupon, CouponTotal).join(CouponTotal,
                                                              on=(Coupon.coupontotal == CouponTotal.id)).where(ft)
        elif type == 'expired':
            ft = ft & (Coupon.status == 1)
            coupons = Coupon.select(Coupon, CouponTotal).join(CouponTotal, on=(
                (Coupon.coupontotal == CouponTotal.id) & (Coupon.endtime < time.mktime(current_time)))).where(ft)
        for n in coupons:
            result.append({
                'id': n.id,
                'code': n.code,
                'userid': n.user.id,
                'status': n.status,
                'name': n.coupontotal.name,
                'price': n.coupontotal.price,
                'minprice': n.coupontotal.minprice,
                'starttime': time.strftime('%Y-%m-%d', time.localtime(n.starttime)),
                'endtime': time.strftime('%Y-%m-%d', time.localtime(n.endtime))
            })

        self.write(simplejson.dumps(result))


@route(r'/mobile/prepurchase', name='mobile_prepurchase')  # 手机端预采购计划
class MobilePrePurchaseHandler(RequestHandler):
    def get(self):
        result = {"flag": 0, "msg": "", "data": ""}
        data = []
        try:
            category = self.get_argument("category", '01')
            key = category + '%'
            ft = (Product.status == 1) & (Product.bz_days > 0) & (Product.avg_quantity > 0) & (Product.sku % key)

            products = ProductStandard.select().join(Product, on=(
                ProductStandard.product == Product.id)).where(ft)
            for n in products:
                avg_quantity = n.product.avg_quantity / 500  # 日销量单位转换成斤
                need = n.product.bz_days * avg_quantity - n.product.quantity
                if need > 0:
                    obj = {
                        'id': n.product.id,
                        'name': n.product.name,
                        'quantity': n.product.quantity,
                        'bz_days': n.product.bz_days,
                        'avg_quantity': avg_quantity,
                        'need_quantity': 0
                    }
                    if n.product.bz_days <= 2:
                        obj["need_quantity"] = need
                        data.append(obj)
                    else:
                        if n.product.quantity <= avg_quantity * 2:
                            obj["need_quantity"] = need
                            data.append(obj)
            result["flag"] = 1
            result["data"] = data
        except Exception, e:
            result["flag"] = 0
            result["msg"] = e
        self.write(simplejson.dumps(result))


@route(r'/mobile/cg/history/(\d+)', name='mobile_cg_history')  # 手机端商品采购历史
class MobileSKUSHandler(RequestHandler):
    def get(self, pid):
        result = {'items': [], 'total': 0, 'totalpage': 0}
        page = int(self.get_argument("index", 1))
        pagesize = int(self.get_argument("size", 10))
        q = Invoicing.select().where(
            (Invoicing.status > -2) & (Invoicing.status < 1) & (Invoicing.type == 0) & (Invoicing.product == pid))
        total = q.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        cs = q.order_by(Invoicing.id.desc()).paginate(page, pagesize)

        for n in cs:
            result['items'].append({
                'id': n.id,
                'quantity': n.quantity,
                'weight': n.gross_weight,
                'price': n.price,
                'buyer': n.buyer,
                'addtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(n.addtime)),
                'status': ('已入库' if n.status == 0 else '待入库')
            })
        result['total'] = total
        result['totalpage'] = totalpage
        self.write(simplejson.dumps(result))


@route(r'/mobile/library/add', name='mobile_library_add')  # 添加/修改入库信息
class AddLibraryHandler(RequestHandler):
    def get(self):
        result = 0
        try:
            product = int(self.get_argument("product", '0'))
            quantity = float(self.get_argument("quantity", '0.0'))
            price = float(self.get_argument("price", '0.0'))
            unitprice = float(self.get_argument("unitprice", '0.0'))
            buyer = self.get_argument("buyer", '')
            weight = self.get_argument('weight', '0.0')
            i = Invoicing()
            i.status = -1
            i.type = 0  # 0入库，1出库
            i.product = product
            i.quantity = quantity
            i.price = price
            i.unitprice = unitprice
            i.args = 'A'
            i.addtime = int(time.time())
            i.buyer = buyer
            i.gross_weight = weight
            i.save()
            result = 1
        except:
            pass
        self.write(str(result))


@route(r'/mobile/xz/missions/list', name='mobile_missions_list')  # 手机端获取话题列表
class MobileMissionsListHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'items': [], 'total': 0, 'totalpage': 0}
        status = self.get_argument("status")
        page = int(self.get_argument("index", '1'))
        pagesize = int(self.get_argument("size", '10'))
        ft = (Topic.status != -1)
        if status == 'closed':
            ft = ft & ((Topic.status == 1) | (Topic.status == 2))
        elif status == 'open':
            ft = ft & (Topic.status == 0)
        topic = Topic.select().where(ft)
        total = topic.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        cs = topic.order_by(Topic.created.desc()).paginate(page, pagesize)

        for n in cs:
            result['items'].append({
                'id': n.id,
                'user': n.created_by.username,
                'userid': n.created_by.id,
                'title': n.title,
                'content': n.content,
                'executor': n.executor.username,
                'status': n.status,
                'created': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(n.created))
            })
        result['total'] = total
        result['totalpage'] = totalpage
        self.write(simplejson.dumps(result))


@route(r'/mobile/xz/missions/news', name='mobile_missions_news')  # 手机端获取话题新的列表
class MobileMissionsNewsHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = []
        max_id = int(self.get_argument("id", '1'))
        ft = (Topic.id > max_id) & (Topic.status > -1)
        topic = Topic.select().where(ft).order_by(Topic.created.desc())

        for n in topic:
            result.append({
                'id': n.id,
                'user': n.created_by.username,
                'userid': n.created_by.id,
                'title': n.title,
                'content': n.content,
                'executor': n.executor.username,
                'status': n.status,
                'created': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(n.created))
            })
        self.write(simplejson.dumps(result))


@route(r'/mobile/xz/comments/list', name='mobile_xz_comments_list')  # 手机端获取话题讨论列表
class MobileXzCommentsListHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'items': [], 'total': 0, 'totalpage': 0}
        missionid = int(self.get_argument("missionid", '0'))
        page = int(self.get_argument("index", '1'))
        pagesize = int(self.get_argument("size", '10'))
        if missionid != 0:
            discuss = Topic_Discuss.select().where(Topic_Discuss.topic == missionid)
            total = discuss.count()
            if total % pagesize > 0:
                totalpage = total / pagesize + 1
            else:
                totalpage = total / pagesize
            cs = discuss.order_by(Topic_Discuss.created.desc()).paginate(page, pagesize)

            for n in cs:
                result['items'].append({
                    'id': n.id,
                    'user': n.created_by.username,
                    'userid': n.created_by.id,
                    'content': n.content,
                    'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(n.created))
                })
            result['total'] = total
            result['totalpage'] = totalpage
        self.write(simplejson.dumps(result))


@route(r'/mobile/xz/comments/add', name='mobile_xz_comments_add')  # 添加问题评论POST
class AddXzCommentsHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        args = simplejson.loads(self.request.body)
        result = {'flag': 0, 'msg': ''}
        try:
            # orderId = self.get_argument("orderId")
            userid = args["userid"]
            missionid = args["missionid"]
            content = args["content"]
            admin_user = AdminUser.get(id=userid)
            n = Topic_Discuss.create(topic=missionid, content=content, created_by=userid, created=int(time.time()))
            body = admin_user.username + u'：' + content
            ausers = AdminUser.select().where((AdminUser.mobile != '') & (AdminUser.isactive == 1))

            sms = {'apptype': 4, 'body': body, 'receiver': []}
            for au in ausers:
                sms['receiver'].append(au.mobile)
            create_msg(simplejson.dumps(sms), 'jpush')
            result['msg'] = {
                'id': n.id,
                'user': n.created_by.username,
                'userid': n.created_by.id,
                'content': n.content,
                'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(n.created))
            }
            result['flag'] = 1
        except Exception, e:
            result['flag'] = 0
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/xz/comments/add_get', name='mobile_xz_comments_add_get')  # 添加问题评论GET
class AddXzCommentsGetHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        # args = simplejson.loads(self.request.body)
        result = {'flag': 0, 'msg': ''}
        try:
            # orderId = self.get_argument("orderId")
            userid = self.get_argument("userid")
            missionid = self.get_argument("missionid")
            content = self.get_argument("content")
            n = Topic_Discuss.create(topic=missionid, content=content, created_by=userid, created=int(time.time()))

            result['msg'] = {
                'id': n.id,
                'user': n.created_by.username,
                'userid': n.created_by.id,
                'content': n.content,
                'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(n.created))
            }
            result['flag'] = 1
        except Exception, e:
            result['flag'] = 0
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/xz/missions/change', name='mobile_xz_missions_change')  # 修改话题状态
class MissionsChangeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        args = simplejson.loads(self.request.body)
        result = 0
        try:
            # missionid = self.get_argument("missionid")
            # status = self.get_argument("status")
            missionid = args["missionid"]
            status = args["status"]
            userid = args["userid"]
            if missionid:
                t = Topic.get(id=missionid)
                if status == 'closed':
                    t.status = 1
                    t.complete_by = userid
                    t.complete = int(time.time())
                if status == 'open':
                    t.status = 0
                    t.created = int(time.time())
                t.save()
            result = 1
        except Exception, e:
            result = 0
        self.write(simplejson.dumps(result))

# 忘记密码手机验证码
@route(r'/mobile/forget/vcode', name='mobile_forget_vcode')
class MobileVcodeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        mobile = args["mobile"]
        user = User.select().where(User.username == mobile)
        if user.count() == 0:
            result['msg'] = '您输入的手机号还没有注册'
            self.write(simplejson.dumps(result))
            return

        UserVcode.delete().where(UserVcode.created < (int(time.time()) - 30 * 60)).execute()

        uservcode = UserVcode()
        uservcode.mobile = mobile
        uservcode.vcode = random.randint(1000, 9999)
        uservcode.created = int(time.time())
        uservcode.flag = 1
        try:
            uservcode.validate()
            if UserVcode.select().where((UserVcode.mobile == mobile) & (UserVcode.flag == 1)).count() > 3:
                result['msg'] = '您的操作过于频繁，请稍后再试'
            else:
                try:
                    uservcode.save()
                    result['flag'] = 1
                    result['msg'] = '验证码已发送'
                    sms = {'mobile': mobile, 'body':str(uservcode.vcode), 'signtype': '1', 'isyzm': 'vcode'}
                    create_msg(simplejson.dumps(sms), 'sms')  #验证码
                except Exception, ex:
                    result['msg'] = '验证码发送失败，请联系400客服处理'

        except Exception, ex:
            result['msg'] = '验证码发送失败，请联系400客服处理'

        self.write(simplejson.dumps(result))


@route(r'/mobile/forgotpassword', name='mobile_forgotpassword')  # 找回密码
class MobileForgotpasswordHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        args = simplejson.loads(self.request.body)
        result = {'flag': 0}
        mobile = args["mobile"]
        vcode = args["vcode"]
        if (not mobile == '') and vcode:
            if UserVcode.select().where((UserVcode.mobile == mobile) & (UserVcode.vcode == vcode) & (
                        UserVcode.flag == 1)).count() > 0:
                result['flag'] = 1
            else:
                result['msg'] = "请输入正确的验证码"
        else:
            result['msg'] = "请输入电话号码和验证码"
        self.write(simplejson.dumps(result))


@route(r'/mobile/resetpassword', name='mobile_resetpassword')  # 重置密码
class MobileResetpasswordHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        args = simplejson.loads(self.request.body)
        result = {'flag': 0}
        password = args["password"]
        apassword = args["apassword"]
        mobile = args['mobile']
        vcode = args['vcode']
        if UserVcode.select().where((UserVcode.mobile == mobile) & (UserVcode.vcode == vcode) & (
                                UserVcode.flag == 1)).count() > 0:
            if mobile and password and apassword and (password == apassword):
                user = User.select().where(User.username == mobile)[0]
                if user.isactive > 0:
                    user.password = User.create_password(password)
                    user.save()
                    user.updatesignin()
                    result['flag'] = 1
                    result['msg'] = {'username': user.username,
                                     'nickname': user.nickname,
                                     'mobile': user.mobile,
                                     'score': user.score,
                                     'balance': user.balance,
                                     'id': user.id}
                else:
                    result['msg'] = "此账户被禁止登录，请联系管理员。"
            else:
                result['msg'] = "两次密码输入不一致"
        else:
            result['msg'] = "请输入正确的验证码"
        self.write(simplejson.dumps(result))


@route(r'/mobile/oauth/login', name='mobile_oauth_login')  # oauth认证登陆
class MobileOAuthLoginHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        args = simplejson.loads(self.request.body)
        result = {'flag': 0}
        openid = args["openid"]
        token = args["token"]
        profile = None
        isValid = False
        try:
            s = urllib2.urlopen(
                "https://graph.qq.com/user/get_user_info?access_token=" + token + '&oauth_consumer_key=101204964&openid=' + openid).read()
            profile = simplejson.loads(s)
            isValid = True
        except Exception, e:
            print e.message
            result['msg'] = '认证失败'
        if isValid:
            oauths = Oauth.select().where((Oauth.openid == openid))
            if oauths.count() > 0:
                user = oauths[0].user
            else:
                now = int(time.time())
                signupeddate = time.strftime('%Y-%m-%d', time.localtime(now))
                signupedtime = time.strftime('%H:%M:%S', time.localtime(now))
                user = User()
                user.username = openid
                user.nickname = profile['nickname']
                user.password = User.create_password(str(random.randint(100000, 999999)))
                user.phoneactived = 1
                user.signuped = now
                user.lsignined = now
                user.signupeddate = signupeddate
                user.signupedtime = signupedtime
                user.save()
                Oauth.create(user=user, src='qq', openid=openid)
            if user.isactive > 0:
                user.updatesignin()
                result['flag'] = 1
                result['msg'] = {'username': user.username,
                                 'nickname': user.nickname,
                                 'mobile': user.mobile,
                                 'score': user.score,
                                 'balance': user.balance,
                                 'password': user.password,
                                 'id': user.id,
                                 'bindmobile': user.bindmobile()}
            else:
                result['msg'] = u"此账户被禁止登录，请联系管理员"
            self.application.session_store.set_session(str(user.username) + ':' + str(user.password), {}, None,
                                                       expiry=24 * 60 * 60)
        self.write(simplejson.dumps(result))

# 修改密码手机验证码
@route(r'/mobile/changepassword/vcode', name='mobile_changepassword_vcode')
class MobileChangePasswordVcodeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        mobile = args["mobile"]
        user = User.select().where(User.username == mobile)
        if user.count() == 0:  # 手机还没有被绑定过
            UserVcode.delete().where(UserVcode.created < (int(time.time()) - 30 * 60)).execute()

            uservcode = UserVcode()
            uservcode.mobile = mobile
            uservcode.vcode = random.randint(1000, 9999)
            uservcode.created = int(time.time())
            uservcode.flag = 2
            try:
                uservcode.validate()

                if UserVcode.select().where(UserVcode.mobile == mobile & UserVcode.flag == 2).count() > 3:
                    result['msg'] = '您的操作过于频繁，请稍后再试'
                else:
                    try:
                        uservcode.save()
                        result['flag'] = 1
                        result['msg'] = '验证码已发送'
                        sms = {'mobile': mobile, 'body': str(uservcode.vcode), 'signtype': '1', 'isyzm': 'vcode'}
                        create_msg(simplejson.dumps(sms), 'sms') #验证码
                    except Exception, ex:
                        result['msg'] = '验证码发送失败，请联系400客服处理'

            except Exception, ex:
                result['msg'] = '验证码发送失败'
        else:
            result['msg'] = '您输入的手机号已经是车装甲会员，不能再次绑定'
        self.write(simplejson.dumps(result))


@route(r'/mobile/bindmobile', name='mobile_bindmobile')  # 绑定手机号
class MobileResetpasswordHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        args = simplejson.loads(self.request.body)
        result = {'flag': 0}
        userid = args["userid"]
        vcode = args["vcode"]
        mobile = args['mobile']
        if mobile and userid and vcode:
            user = User.select().where(User.id == userid)[0]
            if user.isactive > 0:
                if UserVcode.select().where((UserVcode.mobile == mobile) & (UserVcode.vcode == vcode) & (
                            UserVcode.flag == 2)).count() > 0:
                    user.username = mobile
                    user.mobile = mobile
                    user.save()
                    result['flag'] = 1
                    result['msg'] = '绑定手机号码成功'
                else:
                    result['msg'] = "请输入正确的验证码"
            else:
                result['msg'] = "您的账户被禁止使用，请联系车装甲客服人员"
        else:
            result['msg'] = '请输入完整信息'
        self.write(simplejson.dumps(result))


@route(r'/mobile/checkin', name='mobile_checkin')  # 签到
class MobileCheckInHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': '', 'seriesnum': 0, 'scorenum': 0, 'totalscore': 0, 'totallevel': 0}
        args = simplejson.loads(self.request.body)
        userid = args["userid"]
        users = User.select().where(User.id == userid)
        if users.count() > 0:
            result = users[0].checkin()
            if result['flag'] == 1:
                u = User.get(id=users[0].id)
                # 签到成功，增加一次抽奖机会
                u.raffle_count += 1
                u.save()
        self.write(simplejson.dumps(result))


@route(r'/mobile/gifts', name='mobile_gifts')  # 手机端获取赠品/礼品信息
class MobileProfileAddressHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'gifts': []}
        userid = self.get_argument("userid")

        giftitem = Gift.select().where(Gift.user == userid)
        for i in giftitem:
            reason = ''
            if i.type == 1:
                reason = u'秒杀'
            elif i.type == 2:
                reason = u'换购'
            elif i.type == 4:
                reason = u'转盘抽奖'
            elif i.type == 5:
                reason = u'预售'
            elif i.type == 3:
                reason = u'赠品'
            elif i.type == 9:
                reason = u'赠品'
            result['gifts'].append({
                'id': i.id,
                'psid': i.product_standard.id,
                'pid': i.product.id,
                'name': i.product.name,
                'cover': i.product.cover,
                'reason': reason,
                'price': 0,
                'quantity': i.quantity,
                'status': i.status,
                'expirs': i.end_time,
                'sku': i.product.sku,
                'type': i.type
            })
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/score_buy', name='mobile_score_buy')  # 手机端积分换购商品
class MobileScoreBuyHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 1, 'msg': ''}
        args = simplejson.loads(self.request.body)
        psid = args["psid"]
        quantity = args["quantity"]
        uid = args["userid"]
        try:
            user = User.get(User.id == uid)
        except:
            user = None
        try:
            ps = ProductStandard.get(ProductStandard.id == psid)
            if user:
                score_num = ps.product.score_num * quantity
                if user.score > score_num:
                    if quantity:
                        s = Score()
                        s.user = user
                        s.stype = 1
                        s.score = ps.product.score_num * quantity
                        s.log = u'积分换购商品 ' + ps.product.name
                        s.created = int(time.time())
                        s.save()

                        gift = Gift()
                        gift.user = user.id
                        gift.product = ps.product.id
                        gift.product_standard = psid
                        gift.quantity = 1
                        gift.created = int(time.time())
                        gift.created_by = 12  # 数据库中是 temp
                        gift.status = 0
                        gift.type = 2  # 2积分兑换
                        gift.end_time = int(time.mktime(
                            time.strptime(time.strftime("%Y-%m-%d 0:0:0", time.localtime(time.time() + 86400 * 30)),
                                          "%Y-%m-%d 0:0:0")))
                        gift.save()
                    else:
                        result['flag'] = 2
                        result['msg'] = '兑换失败，请刷新后重试！'
                else:
                    result['flag'] = 3
                    result['msg'] = '兑换失败，可用积分不足！'
            else:
                result['flag'] = 4
                result['msg'] = '获取用户信息错误，请先登录！'
        except:
            result['flag'] = 5
            result['msg'] = '兑换失败，请稍后重试！'

        self.write(simplejson.dumps(result))


@route(r'/mobile/check_cart', name='mobile_check_cart')  # 检查手机端购物车操作是否超出数量限额
class CheckCartHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', 'count': 0}
        pid = int(self.get_argument("pid", 0))
        uid = int(self.get_argument("uid", 0))
        quantity = int(self.get_argument("quantity", 1))
        poid = int(self.get_argument("poid", 0))
        if (pid > 0 and quantity > 0):
            if poid:
                po = ProductOffline.select().where((ProductOffline.status == 2) & (ProductOffline.id == poid))
                if po.count() > 0:
                    result['flag'] = 1
                    po[0].status = 6
                    po[0].save()
                else:
                    result['flag'] = 0
                    result['msg'] = '该商品已售出，请重新选择！'
                    result['count'] = 1
            else:
                c = check_buy_quantity(pid, uid, quantity, 1)
                if c['flag'] == 0:
                    result['flag'] = 1
                else:
                    result['flag'] = 0
                    result['msg'] = '该商品已超出当日最大可购买数量！'
                    result['count'] = c['quantity']
        else:
            result['flag'] = 0
            result['msg'] = '参数获取异常'
        self.write(simplejson.dumps(result))


@route(r'/mobile/stores', name='mobile_stores')  # 手机端实体店列表
class MobileStoresHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        category_id = self.get_argument('category', None)
        order = self.get_argument('order', None)
        area_code = self.get_argument('area', None)
        x = self.get_argument('x', None)
        y = self.get_argument('y', None)
        uid = self.get_argument('uid', None)

        result = {'flag': 0, 'msg': '', 'data': []}
        fn = Store.check_state == 1

        if category_id:
            p = Product.select().where(Product.categoryfront == category_id).distinct()
            id_list = [n.store.id for n in p]
            fn = fn & (Store.id << id_list)
            # stores = Store.select().where(Store.id << id_list).execute()

        if area_code:
            fn = fn & (Store.area_code == area_code)
        stores = Store.select(Store).join(User, on=(User.store == Store.id)).where(fn & (User.grade == 1))

        if order == "star":
            stores = stores.order_by(Store.star_score.desc())
        elif order == "distance":
            dics = {}
            keys = []
            if x and y:
                if stores.count() > 0:
                    for n in stores:
                        if n.x and n.y:
                            # n.image_legal = str(getDistance(float(x), float(y), float(n.x), float(n.y)))
                            xy = str(getDistance(float(x), float(y), float(n.x), float(n.y)))
                            dics[xy] = n
                            keys.append(xy)

                    keys = sorted(keys,
                                  key=lambda keys: float(keys),
                                  reverse=False)

                    stores = []
                    for key in keys:
                        stores.append(dics[key])

        elif order == "hot":
            stores = stores.order_by(Store.credit_score.desc())

        if stores:
            for store in stores:
                # s_count = Product.select(db.fn.Count(OrderItem.quantity).alias('quantity')).\
                #     join(OrderItem, on=(Product.id == OrderItem.product)).\
                #     join(Store, on=(Product.store == Store.id)).where(Store.id == store.id)
                d = {'id': store.id,
                     'name': store.name,
                     'tags': store.tags,
                     'x': store.x,
                     'y': store.y,
                     'area_code': store.area_code,
                     'address': store.address,
                     'link_man': store.link_man,
                     'tel': store.tel,
                     'mobile': store.mobile,
                     'image': store.image,
                     'image_legal': store.image_legal,
                     'image_license': store.image_license,
                     'intro': store.intro,
                     'clicks': store.clicks,
                     'credit_score': store.credit_score,
                     'star_score': store.star_score,
                     'is_certified': store.is_certified,
                     'distance': store.image_legal,
                     'items': [],
                     'trait': store.trait}

                ps = ProductStandard.select().join(Product, on=(ProductStandard.id == Product.defaultstandard))\
                    .where((Product.store == store.id) & (Product.status == 1)).order_by(Product.orders.desc()).limit(3)
                for n in ps:
                    s_count = Product.select(db.fn.SUM(Product.orders).alias('quantity'))\
                        .where(Product.id == n.product.id)
                    d['items'].append({
                        'psid': n.id,
                        'pid': n.product.id,
                        'name': n.product.name,
                        'sales': n.product.orders,
                        'resume': n.product.resume,
                        'price': n.price,
                        'orginal_price': n.orginalprice,
                        'quantity': s_count.aggregate_rows()[0].quantity,
                        'service_time': n.product.service_time
                    })
                result['data'].append(d)
            result['flag'] = 1
        else:
            result['msg'] = '没有找到相关门店'

        self.write(simplejson.dumps(result))


@route(r'/mobile/store_tel', name='mobile_store_tel')  # 手机端获取附近商家电话
class MobileStoreTelHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        category_id = self.get_argument('category', None)
        order = self.get_argument('order', None)
        area_code = self.get_argument('area', None)
        x = self.get_argument('x', None)
        y = self.get_argument('y', None)
        uid = self.get_argument('uid', None)

        result = {'flag': 0, 'msg': '', 'data': ''}
        if uid:
            brand = UserAuto.select().where(UserAuto.user == uid).limit(1)
            brand_filter = True
            if brand.count() > 0:
                brand_code = brand[0].brand_code
                brand_filter = StoreAuto.brand_code == brand_code

            fn = Store.check_state == 1
            if category_id:
                p = Product.select().where(Product.categoryfront == category_id).distinct()
                id_list = [n.store.id for n in p]
                fn = fn & (Store.id << id_list)

            if area_code:
                fn = fn & (Store.area_code == area_code)
            stores = Store.select(Store).join(User, on=(User.store == Store.id)). \
                join(StoreAuto, on=(StoreAuto.store == Store.id)). \
                where(fn & (User.grade == 1) & (brand_filter))

            if order == "star":
                stores = stores.order_by(Store.star_score.desc()).limit(1)
            elif order == "distance":
                if x and y:
                    if stores.count() > 0:
                        for n in stores:
                            if n.x and n.y:
                                n.image_legal = str(getDistance(float(x), float(y), float(n.x), float(n.y)))
                    stores = sorted(stores, key=lambda stores: float(stores.image_legal), reverse=False)
            elif order == "hot":
                stores = stores.order_by(Store.credit_score.desc())

            if stores:
                for store in stores:
                    result['data'] = {'id': store.id,
                                      'name': store.name,
                                      'tags': store.tags,
                                      'x': store.x,
                                      'y': store.y,
                                      'area_code': store.area_code,
                                      'address': store.address,
                                      'link_man': store.link_man,
                                      'tel': store.mobile}
                result['flag'] = 1
            else:
                result['data'] = {'tel': self.settings['com_tel']}
                result['flag'] = 1
        else:
            result['data'] = {'tel': self.settings['com_tel']}
            result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/store/category/(\d+)', name='mobile_store_category')  # 手机端实体店分类列表
class MobileStoreCategoryHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, sid):
        result = {'flag': 0, 'msg': '', 'data': []}
        child = Category_Store.select().where((Category_Store.status == 1) &
                                              (Category_Store.store == sid))
        if child.count() > 0:
            for n in child:
                result['data'].append({'code': n.id, 'name': n.name})
            result['flag'] = 1
        else:
            result['msg'] = '没有找到该店商品分类'
        self.write(simplejson.dumps(result))


@route(r'/mobile/store/product/(\d+)', name='mobile_store_product')  # 手机端实体店商品列表
class MobileStoreCategoryHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, sid):
        code = self.get_argument("code", None)
        min = self.get_argument("min", 9999999)
        sale_status = self.get_argument("sale_status", 0)
        city_code = self.get_argument("city_code", None)
        version = self.get_argument("version", None)
        citys = []
        ft = (ProductStandard.store == sid)
        if code and len(code) > 0:
            ft = ft & (Product.categoryfront == code)
        if sale_status and sale_status > 0 :
            ft = ft & (ProductStandard.sale_status == sale_status)
        q = ProductStandard.select(ProductStandard, Product).join(Product,
                on=(ProductStandard.product == Product.id)).where(
                ft & (ProductStandard.id < min)).order_by(ProductStandard.id.desc()).limit(20)
        if version == '1.1.2':
            result = {'product': [], 'citys': []}
        else:
            result = []
        for n in q:
            if n.area_code:
                area_name = Area.get(Area.code==n.area_code[:8]).name
                tmpdic = {
                    'status': n.sale_status,
                    'psid': n.id,
                    'pid': n.product.id,
                    'name': n.product.name,
                    'price': n.pf_price,  #销售价（车主 修改成批发价
                    'originalPrice': n.orginalprice,
                    'unit': n.unit if n.unit else u'件',
                    'sku': n.product.sku,
                    'cover': PassMobileImg(n.product.cover),
                    'standard': n.product.prompt,
                    'resume': n.product.resume,
                    'poid': 0,
                    'city_code':area_name
                }
                citys.append(n.area_code[:8])
                citys = list(set(citys))
                if (n.area_code[:8] == city_code) or (city_code is None):
                    if version == '1.1.2':
                        result['product'].append(tmpdic)
                    else:
                        result.append(tmpdic)
        if version == '1.1.2':
            for city in citys:
                c_code = Area.get(code=city)
                result['citys'].append({'city_code':city, 'city_name':c_code.name})
        self.write(simplejson.dumps(result))

@route(r'/mobile/product_updown', name='mobile_product_updown')  # 手机端实体店商品列表
class MobileProductUpdownHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        psid = args['psid']
        status = int(args['status'])
        standards = ProductStandard.select().where(ProductStandard.id == psid)
        try:
            if standards.count() > 0:
                standard = standards[0]
                standard.sale_status = status
                standard.save()
                result['flag'] = 1
        except Exception, e:
            result['msg'] = e.message

        self.write(simplejson.dumps(result))

# 手机端线下产品详情
@route(r'/mobile/store_product/(\d+)', name='mobile_store_product_detail')
class MobileProductHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, psid):
        store_id = self.get_argument("sid", None)
        result = {}
        price = StorePrice.select().where(StorePrice.product_standard == psid)
        ps = ProductStandard.get(id=psid)
        p = ps.product
        pics2 = p.pics
        result['time'] = int(time.time())
        result['name'] = p.name
        result['sku'] = p.sku
        result['pid'] = p.id
        result['psid'] = ps.id
        result['standard'] = ps.name
        result['price'] = round((price[0].price / 2), 2)  # ps.price
        result['ourprice'] = ps.pf_price
        result['pf_price'] = ps.pf_price
        result['orginalprice'] = ps.orginalprice
        result['resume'] = p.resume
        result['status'] = 1  # p.status
        result['xgtotalnum'] = p.xgtotalnum
        result['xgperusernum'] = p.xgperusernum
        result['quantity'] = 0
        result['pics'] = []
        result['score'] = p.score_num

        # ps = ProductStandard.get(id=psid)
        # po = ProductOffline.select(ProductOffline, Product, ProductStandard).join(Product, on=(Product.id == ProductOffline.product)).\
        #     join(ProductStandard, on=(Product.defaultstandard == ProductStandard.id)).where((ProductOffline.store == store_id) &
        #                                                                                     (Product.defaultstandard == psid))

        list = ProductOffline.select().where((ProductOffline.product == p.id) & (ProductOffline.store == int(store_id))
                                             & (ProductOffline.status == 2)).limit(10)
        standards = []
        for n in list:
            standards.append({
                'psid': n.product.defaultstandard,
                'pid': n.product.id,
                'name': n.product.name,
                'price': n.price,
                'originalPrice': 0,
                'unit': n.unit if n.unit else u'件',
                'sku': n.product.sku,
                'cover': PassMobileImg(n.product.cover),
                'standard': n.product.prompt,
                'resume': n.product.resume,
                'poid': n.id
            })

        result['standards'] = standards
        pics = [ProductPic(path=p.cover)] + [n for n in pics2 if not n.path == p.cover]
        for n in pics:
            result['pics'].append({
                'img': PassMobileImg(n.path)
            })
        else:
            flag = -1
        result['flag'] = flag
        self.write(simplejson.dumps(result))


@route(r'/mobile/remove_offline_car', name='mobile_remove_offline_car')  # 手机端移除线下商品
class MobileRemoveOfflineHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        args = simplejson.loads(self.request.body)
        userid = args["userid"]
        items = args["items"]
        Cart.delete().where((Cart.user == userid) & (Cart.type == 0)).execute()
        for n in items:
            if n['poid'] > 0:
                Cart.delete().where((Cart.product_offline == n['poid']) & (Cart.user == userid)).execute()
                po = ProductOffline.get(ProductOffline.id == n['poid'])
                po.status = 2
                po.save()
        result = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/cgreport', name='mobile_cgreport')  # 手机端用户采购记录
class MobileCgreportHandler(RequestHandler):
    def get(self):
        result = {'flag': 0, 'msg': '', 'records': []}
        date = self.get_argument("time", None)
        uid = self.get_argument("uid", None)
        if date:
            begindate = time.mktime(time.strptime(date, "%Y-%m-%d"))
            enddate = time.mktime(time.strptime((date + " 23:59:59"), "%Y-%m-%d %H:%M:%S"))
        else:
            begindate = time.mktime(time.strptime(time.strftime("%Y-%m-%d", time.localtime(time.time())), "%Y-%m-%d"))
            enddate = time.mktime(
                time.strptime(time.strftime("%Y-%m-%d 23:59:59", time.localtime(time.time())), "%Y-%m-%d %H:%M:%S"))

        ft = (Invoicing.addtime >= begindate) & (Invoicing.addtime < enddate) & (
            (Invoicing.status == 0) | (Invoicing.status == -1))
        if uid:
            u = AdminUser.select().where(AdminUser.id == uid)
            if u.count() > 0:
                username = '%' + u[0].username + '%'
                ft = ft & (Invoicing.buyer % username)
        i = Invoicing.select().where(ft)
        for n in i:
            result['records'].append({
                'id': n.id,
                'quantity': n.quantity,
                'price': n.price,
                'time': n.addtime,
                'weight': n.gross_weight,
                'buyer': n.buyer,
                'product': n.product.id,
                'product_name': n.product.name,
                'status': n.status
            })
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/cgrecords', name='mobile_cgrecords')  # 手机端获取未入库的采购记录
class MobileCgrecordsHandler(RequestHandler):
    def get(self):
        result = {'flag': 0, 'msg': '', 'records': []}
        ft = Invoicing.status == -1
        try:
            i = Invoicing.select().where(ft)
            for n in i:
                result['records'].append({
                    'id': n.id,
                    'quantity': n.quantity,
                    'price': n.price,
                    'time': n.addtime,
                    'weight': n.gross_weight,
                    'buyer': n.buyer,
                    'product': n.product.id,
                    'product_name': n.product.name
                })
            result['flag'] = 1
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/cgtakein', name='mobile_cgtakein')  # 手机端采购执行一个入库操作
class MobileCgtakeinHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        pid = args["pid"]
        quantity = args["quantity"]
        gross_weight = args["gross_weight"]
        try:
            ft = Invoicing.status == -1
            if pid:
                ft = ft & (Invoicing.id == pid)
            i = Invoicing.select().where(ft)
            if i.count() > 0:
                if quantity:
                    i[0].quantity = quantity
                if gross_weight:
                    i[0].gross_weight = gross_weight
                i[0].status = 0
                i[0].save()
            result['flag'] = 1
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/cgretreat', name='mobile_cgretreat')  # 手机端采购执行一个入库操作
class MobileCgretreatHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        args = simplejson.loads(self.request.body)
        pid = args["pid"]
        result = cg_change_status(pid, -2)
        self.write(simplejson.dumps(result))


@route(r'/mobile/cgcancel', name='mobile_cgcancel')  # 手机端采购取消
class MobileCgCancelHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        args = simplejson.loads(self.request.body)
        id = args["id"]
        result = cg_change_status(id, 1)
        self.write(simplejson.dumps(result))


# 更改采购记录状态
def cg_change_status(id, status):
    result = {'flag': 0, 'msg': ''}
    try:
        ft = Invoicing.status == -1
        if id:
            ft = ft & (Invoicing.id == id)
        i = Invoicing.select().where(ft)
        if i.count() > 0:
            i[0].status = status
            i[0].save()
        result['flag'] = 1
    except Exception, e:
        result['msg'] = e.message
    return result


@route(r'/mobile/get_browse/(\d+)', name='mobile_get_browse')  # 手机端获取用户浏览记录
class MobileGetBrowseHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, uid):
        result = []
        q = User_Browse.select().where(User_Browse.user == uid)
        for n in q:
            result.append({
                'id': n.id,
                'pid': n.product.id,
                'psid': n.product_standard.id,
                'name': n.product.name,
                'price': n.product_standard.price,
                'originalPrice': n.product_standard.orginalprice,
                'categoryID': n.category_front.id,
                'sku': n.product.sku,
                'cover': PassMobileImg(n.product.cover),
                'standard': n.product_standard.name,
                'resume': n.product.resume,
                'status': n.product.status
            })
        self.write(simplejson.dumps(result))


@route(r'/mobile/set_browse', name='mobile_set_browse')  # 手机端设置用户浏览记录
class MobileSetBrowseHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        args = simplejson.loads(self.request.body)
        result = {'flag': 0, 'msg': ''}
        psid = args["psid"]
        uid = args["uid"]
        try:
            ps = ProductStandard.get(id=psid)
            # 判断用户浏览记录表中是否存在该商品
            ub_exist = User_Browse().select().where(
                (User_Browse.user == self.current_user.id) & (User_Browse.product_standard == psid))
            if ub_exist.count() > 0:
                pass
            else:
                # 创建用户浏览记录
                ub = User_Browse()
                ub.user = uid
                ub.product = ps.product.id
                ub.product_standard = psid
                ub.category_front = ps.product.categoryfront
                ub.created = int(time.time())
                ub.save()
                # 如何该用户浏览记录大于5条，按队列顺序删除超出的数据
                ub_count = User_Browse.select().where(User_Browse.user == self.current_user.id)
                if ub_count.count() > 5:
                    del_count = ub_count.count() - 5
                    del_ub = User_Browse.select().where(User_Browse.user == self.current_user.id).order_by(
                        User_Browse.created).limit(del_count)
                    del_id = [n.id for n in del_ub]
                    User_Browse.delete().where(User_Browse.id << del_id).execute()
            result["flag"] = 1
        except Exception, ex:
            result["msg"] = str(ex)

        self.write(simplejson.dumps(result))


@route(r'/mobile/product_recommend', name='mobile_product_recommend')  # 手机端商品今日推荐
class MobileProductRecommendHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        cid = self.get_argument("cityID", None)
        result = []
        fn = Product.status == 1
        if cid:
            fn = fn & Product.city_id == cid
        recommend = ProductStandard.select(ProductStandard, Product).join(Product,
                                                                          on=(ProductStandard.product == Product.id)). \
            join(CategoryFront, on=(Product.categoryfront == CategoryFront.id)).where(fn & (CategoryFront.type == '1') &
                                                                                      (
                                                                                          Product.is_recommend == 1)).order_by(
            Product.orders).limit(10)
        for n in recommend:
            result.append({
                'psid': n.id,
                'pid': n.product.id,
                'name': n.product.name,
                'price': n.price,
                'originalPrice': n.orginalprice,
                'categoryID': n.product.categoryfront.id,
                'sku': n.product.sku,
                'cover': PassMobileImg(n.product.cover),
                'standard': n.name,
                'resume': n.product.resume,
                'status': n.product.status
            })
        self.write(simplejson.dumps(result))

'''
@route(r'/mobile/select_city', name='mobile_select_city')  # 手机端获取城市
class MobileSelectCityHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = []
        items = Area.select().where(~(Area.pid >> None) & (Area.is_delete == 0) & (Area.is_site == 1)).order_by(Area.spell)
        for n in items:
            result.append({
                'id': n.id,
                'pid': n.pid,
                'code': n.code,
                'name': n.name,
                'spell': n.spell,
                'spell_abb': n.spell_abb
            })
        self.write(simplejson.dumps(result))
'''


@route(r'/mobile/select_area', name='mobile_select_area')  # 手机端 根据城市ID获取所有行政区
class MobileSelectCityHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        cid = self.get_argument('cid', None)
        result = []
        if cid:
            items = Area.select().where((Area.pid == cid) & (Area.is_delete == 0)).order_by(Area.code)
            for n in items:
                result.append({
                    'id': n.id,
                    'pid': n.pid,
                    'code': n.code,
                    'name': n.name,
                    'spell': n.spell,
                    'spell_abb': n.spell_abb
                })
        self.write(simplejson.dumps(result))

# 根据city_code获取商品
def get_store_new(keyword, category, index, city_code, order, version, level, classes, capacity, viscosity,
                  configuration, CAN, psize, jsize, lens, keyword2):
    tmpResult = {'items': [], 'flag': 0, 'msg': ''}
    result = {'items': [], 'flag': 0, 'msg': ''}
    try:
        if not index and index<1:
            index = 1
        ft = (ProductStandard.sale_status == 1)
        c_like = city_code + '%'
        ft = ft & (ProductStandard.area_code % c_like)
        pinpaiTypes = []
        flag = 0
        if keyword:
            keyword = '%' + keyword + '%'
            ft = ft & (Product.name % keyword)
        if level or classes or capacity or viscosity:
            pinpaiTypes.append(1)
            flag = 1
        elif configuration or CAN or psize:
            pinpaiTypes.append(3)
            flag = 1
        elif jsize or lens:
            pinpaiTypes.append(4)
            flag = 1
        elif keyword2:
            keyword2s = keyword2.strip(',').split(',')
            keyword2 = '%'+keyword2s[0]+'%'
            tmpft = (Product.name % keyword2)
            for keyword2 in keyword2s[1:]:
                keyword2 = '%' + keyword2 + '%'
                tmpft |= (Product.name % keyword2)
            ft = ft & tmpft
        if flag:
            ptypeLen = 1
        else:
            products = Product.select().join(ProductStandard, on=(Product.id == ProductStandard.product)).where(ft)
            for p in products:
                pinpaiTypes.append(p.pinpai.ptype.id)
            pinpaiTypes = list(set(pinpaiTypes))
            ptypeLen = len(pinpaiTypes)

        if version>'1.1.1' and ptypeLen == 1:
            if pinpaiTypes[0] == 1:  # 润滑油 LubeAttribute
                if level:
                    quantitys = level.split(',')
                    qft = (LubeAttribute.level == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (LubeAttribute.level == quantity)
                    ft = qft & ft
                if classes:
                    quantitys = classes.split(',')
                    qft = (LubeAttribute.classes == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (LubeAttribute.classes == quantity)
                    ft = qft & ft
                if capacity:
                    quantitys = capacity.split(',')
                    qft = (LubeAttribute.capacity == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (LubeAttribute.capacity == quantity)
                    ft = qft & ft
                if viscosity:
                    quantitys = viscosity.split(',')
                    qft = (LubeAttribute.viscosity == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (LubeAttribute.viscosity == quantity)
                    ft = qft & ft
                q = ProductStandard.select(ProductStandard, Product). \
                    join(Product, on=(Product.id == ProductStandard.product)). \
                    join(LubeAttribute, on=(Product.id == LubeAttribute.product)). \
                    join(CategoryFront, on=(Product.categoryfront == CategoryFront.id)). \
                    join(Store, on=(Store.id == ProductStandard.store)).where(ft);
            elif pinpaiTypes[0] == 3:  # 大屏导航仪 NavigatorAttribute
                if configuration:
                    quantitys = configuration.split(',')
                    qft = (NavigatorAttribute.configuration == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (NavigatorAttribute.configuration == quantity)
                    ft = qft & ft
                if CAN:
                    quantitys = CAN.split(',')
                    qft = (NavigatorAttribute.CAN == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (NavigatorAttribute.CAN == quantity)
                    ft = qft & ft
                if psize:
                    quantitys = psize.split(',')
                    qft = (NavigatorAttribute.size == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (NavigatorAttribute.size == quantity)
                    ft = qft & ft
                q = ProductStandard.select(ProductStandard, Product). \
                    join(Product, on=(Product.id == ProductStandard.product)). \
                    join(NavigatorAttribute, on=(Product.id == NavigatorAttribute.product)). \
                    join(CategoryFront, on=(Product.categoryfront == CategoryFront.id)). \
                    join(Store, on=(Store.id == ProductStandard.store)).where(ft);
            elif pinpaiTypes[0] == 4:  # 记录仪 RecorderAttribute
                if jsize:
                    quantitys = jsize.split(',')
                    qft = (RecorderAttribute.size == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (RecorderAttribute.size == quantity)
                    ft = qft & ft
                if lens:
                    quantitys = lens.split(',')
                    qft = (RecorderAttribute.lens == quantitys.pop())
                    for quantity in quantitys:
                        qft |= (RecorderAttribute.lens == quantity)
                    ft = qft & ft
                q = ProductStandard.select(ProductStandard, Product). \
                    join(Product, on=(Product.id == ProductStandard.product)). \
                    join(RecorderAttribute, on=(Product.id == RecorderAttribute.product)). \
                    join(CategoryFront, on=(Product.categoryfront == CategoryFront.id)). \
                    join(Store, on=(Store.id == ProductStandard.store)).where(ft);
        else:
            q = ProductStandard.select(ProductStandard, Product). \
                join(Product, on=(Product.id == ProductStandard.product)). \
                join(CategoryFront, on=(Product.categoryfront == CategoryFront.id)). \
                join(Store, on=(Store.id == ProductStandard.store)).where(ft);
        ps = q
        # order 排序0默认按权重 1价格从高到低 2价格从低到高 3销量从高到低 4销量从低到高
        if order == "1":
            ps = ps.order_by(ProductStandard.pf_price.desc())
        elif order == "2":
            ps = ps.order_by(ProductStandard.pf_price.asc())
        elif order == "3":
            ps = ps.order_by(ProductStandard.orders.desc())
        elif order == "4":
            ps = ps.order_by(ProductStandard.orders.asc())
        else:
            ps = ps.order_by(ProductStandard.weight.asc())
        #ps = ps.paginate(index, 10).aggregate_rows()
        paging_q = ps.paginate(index, 10)
        for n in paging_q:
            tmpResult['items'].append({
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
            })
        tmpResult['flag'] = 1
        if version > '1.1.1' and ptypeLen == 1:
            result = {'items': [], 'flag': 0, 'msg': '', 'attribute': []}
            result['items'] = tmpResult['items']
            result['flag'] = tmpResult['flag']
            pptas = PPTAttribute.select()
            for ppta in pptas:
                tmpdict = {}
                if ppta.PinPaiType.id == pinpaiTypes[0]:
                    pptaqs = PPTAQuantity.select().where(PPTAQuantity.PPTA_id==ppta.id)
                    tmpdict['name'] = ppta.name
                    tmpdict['ename'] = ppta.ename
                    tmpdict['value'] = [pptaq.name for pptaq in pptaqs]
                    tmpdict['arguments'] = []
                    for arg in tmpdict['value']:
                        tmpargdic = {}
                        tmpargdic['arg'] = arg
                        tmpargdic['value'] = 0
                        tmpdict['arguments'].append(tmpargdic)
                    result['attribute'].append(tmpdict)
        elif version > '1.1.1' and ptypeLen > 1:
            tmpdict = {}
            result = {'items': [], 'flag': 0, 'msg': '', 'attribute': []}
            result['items'] = tmpResult['items']
            result['flag'] = tmpResult['flag']
            tmpdict['arguments'] = []
            tmpdict['name'] = '种类'
            tmpdict['ename'] = 'keyword2'
            for pinpai_type_id in pinpaiTypes:
                tmpargdic = {}
                tmpargdic['arg'] = PinPaiType.get(id=pinpai_type_id).name
                tmpargdic['value'] = 0
                tmpdict['arguments'].append(tmpargdic)
            result['attribute'].append(tmpdict)
        else:
            result = tmpResult
    except Exception, e:
        result['msg'] = e
    return result

# 根据x，y坐标获取附近店铺商品
def get_store(x, y, keyword, category, index, city,order):
    result = {'items': [], 'flag': 0, 'msg': ''}
    try:
        if not index and index<1:
            index = 1
        ft = (ProductStandard.sale_status == 1)
        if x and y:
            lng_start = float(x) - 0.0350
            lng_end = float(x) + 0.0350
            lat_start = float(y) - 0.0400
            lat_end = float(y) + 0.0400
            ft = ft & ((Store.x > lng_start) & (Store.x < lng_end))
            ft = ft & ((Store.y > lat_start) & (Store.y < lat_end))
        city_code = None
        if city:
            qArea= Area.select().where(Area.name == city)
            if qArea.count() > 0:
                city_code = qArea[0].code
        if city_code:
            c_like = city_code + '%'
            #ft = ft & ((ProductStandard.area_code % c_like) | (ProductStandard.area_code % (city_code[0:4] + '%')))
            ft = ft & (ProductStandard.area_code % c_like)
            # ft = ft & (Product.city_id == city_id)
        if keyword:
            keyword = '%' + keyword + '%'
            ft = ft & (Product.name % keyword)
        if category:
            ft = ft & (Product.categoryfront == category)
        ps = ProductStandard.select(ProductStandard).join(
            Product, on=(Product.id == ProductStandard.product)).join(
            Store, on=(Store.id == ProductStandard.store)). \
            where(ft & (Store.check_state == 1))
        # order 排序0默认按权重 1价格从高到低 2价格从低到高 3销量从高到低 4销量从低到高
        if order == "1":
            ps = ps.order_by(ProductStandard.pf_price.desc())
        elif order == "2":
            ps = ps.order_by(ProductStandard.pf_price.asc())
        elif order == "3":
            ps = ps.order_by(ProductStandard.orders.desc())
        elif order == "4":
            ps = ps.order_by(ProductStandard.orders.asc())
        else:
            ps = ps.order_by(ProductStandard.weight.asc())
        ps = ps.paginate(index, 10).aggregate_rows()
        for n in ps:
            result['items'].append({
                'psid': n.id,
                'pid': n.product.id,
                'name': n.product.name,
                'price': n.price,
                'sales': n.orders,
                'originalPrice': n.orginalprice,
                # 'ourprice': n.ourprice,#商店价修改为批发价
                'ourprice': n.pf_price,
                'pf_price': n.pf_price,
                'categoryID': n.product.categoryfront.id,
                'sku': n.product.sku,
                'cover': PassMobileImg(n.product.cover),
                'standard': n.name,
                'resume': n.product.resume,
                'status': n.product.status,
                'x': n.store.x,     #.product.store.x
                'y': n.store.y      #.product.store.y
            })
        result['flag'] = 1
    except Exception, e:
        result['msg'] = e.message
    return result


@route(r'/mobile/store/(\d+)', name='mobile_store_detail')  # 手机端店铺详情
class MobileProductHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, id):
        result = {}
        try:
            p = Store.get(id=id)
            pics2 = p.store_pics
            result['id'] = p.id
            result['name'] = p.name
            result['tags'] = p.tags
            result['area_code'] = p.area_code
            result['address'] = p.address
            result['link_man'] = p.link_man
            result['tel'] = p.tel
            result['mobile'] = p.mobile
            result['image'] = PassMobileImg(p.image)
            result['image_legal'] = p.image_legal
            result['image_license'] = p.image_license
            result['x'] = p.x
            result['y'] = p.y
            result['intro'] = p.intro
            result['clicks'] = p.clicks
            result['credit_score'] = p.credit_score
            result['star_score'] = p.star_score
            result['comment_count'] = p.comment_count
            result['store_type'] = p.store_type
            result['is_certified'] = p.is_certified
            result['trait'] = p.trait
            result['pics'] = []
            result['items'] = []
            pics = [StorePic(path=p.image)] + [n for n in pics2 if not n.path == p.image]
            for n in pics:
                result['pics'].append({
                    'img': PassMobileImg(n.path)
                })

            categoryfronts = CategoryFront.select().join(Product, on=(CategoryFront.id == Product.categoryfront)) \
                .where((Product.store == id) & (Product.status == 1)).distinct()
            for n in categoryfronts:
                result['items'].append({
                    'item_id': n.id,
                    'item_name': n.name
                })
            result['flag'] = 1
        except Exception, e:
            result['flag'] = 0
            result['msg'] = '数据异常：' + e

        self.write(simplejson.dumps(result))


@route(r'/mobile/category_store', name='mobile_category_store')  # 手机端店铺分类列表
class MobileCategoryStoreHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = []

        list = CategoryFront.select().join(Product, on=(CategoryFront.id == Product.categoryfront)) \
            .where(Product.status == 1).distinct()
        for n in list:
            result.append({
                'name': n.name,
                'id': n.id,
                'code': "'" + n.code + "'"
            })
        self.write(simplejson.dumps(result))


@route(r'/mobile/feedback', name='mobile_feedback')  # 手机端店意见反馈
class MobileFeedbackHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = 0
        args = simplejson.loads(self.request.body)
        uid = args["userid"]
        content = args["content"]
        if args.has_key("f"):
            f = args["f"]  # 是否返回json格式结果
        if uid:
            type = ''
            contact = ''
            created = int(time.time())
            reply_content = ''
            reply_time = 0
            try:
                u = User.get(id=uid)
                fb = Feedback()
                fb.user = u.id
                fb.type = type
                fb.content = content
                fb.contact = contact
                fb.mobile = u.mobile
                fb.created = created
                fb.reply_content = reply_content
                fb.reply_time = reply_time
                fb.save()
                result = 1
                if f and f == "json":
                    result = {'flag': 1, 'msg': '','data':[]}
            except Exception, ex:
                result = 0
                if f and f == "json":
                    result = {'flag': 0, 'msg': '','data':[]}
        self.write(simplejson.dumps(result))


@route(r'/mobile/check_service_code', name='mobile_check_service_code')  # 校验服务码
class MobileCheckServiceCodeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        code = args["service_code"]
        sid = args["store_id"]
        # sid = int(self.get_argument("store_id", 0))
        # code = self.get_argument("service_code", None)
        try:
            item_service = OrderItemService.select().where(OrderItemService.service_code == code)
            if item_service.count() > 0:
                if item_service[0].store.id == sid:
                    if item_service[0].service_used == 0:
                        item_service[0].service_used = 1
                        item_service[0].used_time = int(time.time())
                        i = datetime.datetime.now()
                        item_service[0].used_year = i.year
                        item_service[0].used_month = i.month
                        item_service[0].used_day = i.day
                        item_service[0].save()
                        result["flag"] = 1
                        result["msg"] = "验证成功！"
                    else:
                        result["flag"] = 3
                        result["msg"] = "验证失败，服务码已使用！"
                else:
                    result["flag"] = 2
                    result["msg"] = "验证失败，您无权操作！"
            else:
                result["flag"] = 2
                result["msg"] = "验证失败，验证码不存在！"

        except Exception, ex:
            result["msg"] = "验证失败，数据异常：" + str(ex)
        self.write(simplejson.dumps(result))


@route(r'/mobile/get_item_service', name='get_item_service')  # 手机端登录
class MobileLoginHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': ''}
        user_id = self.get_argument("uid", None)
        item_service = []
        try:
            items = OrderItemService.select().where(OrderItemService.user == user_id)
            for i in items:
                item_service.append({
                    'sn': i.sn,
                    'id': i.id,
                    'product_name': i.order_item.product_standard.name,
                    'product_resume': i.order_item.product.resume,
                    'service_code': i.service_code,
                    'service_used': i.service_used,
                    'reserve_time': time.strftime('%Y-%m-%d', time.localtime(items[0].reserve_time))
                })
            result['msg'] = item_service;
            result['flag'] = 1

        except:
            result['msg'] = '服务器异常'

        self.write(simplejson.dumps(result))


@route(r'/mobile/get_item_service_detail', name='get_item_service_detail')  # 手机端登录
class MobileLoginHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': ''}
        user_id = self.get_argument("uid", None)
        id = self.get_argument("id", None)
        item_service = {}
        try:
            items = OrderItemService.select().where((OrderItemService.user == user_id) & (OrderItemService.id == id))
            if items.count() > 0:
                item_service = {
                    'sn': items[0].sn,
                    'id': items[0].id,
                    'product_name': items[0].order_item.product_standard.name,
                    'product_resume': items[0].order_item.product.resume,
                    'service_code': items[0].service_code,
                    'service_used': items[0].service_used,
                    'reserve_time': time.strftime('%Y-%m-%d', time.localtime(items[0].reserve_time))
                }

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=4,
                )
                qr.add_data(item_service['service_code'])
                qr.make(fit=True)
                img = qr.make_image()
                out = BytesIO()
                img.save(out, 'PNG')
                item_service['qrcode'] = u"data:image/png;base64," + base64.b64encode(out.getvalue()).decode('ascii')

            result['msg'] = item_service
            result['flag'] = 1

        except:
            result['msg'] = '服务器异常'

        self.write(simplejson.dumps(result))


@route(r'/mobile/getProvinces', name='mobile_getProvinces')  # 手机端分类列表
class MobileGetProvincesHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 1, 'msg': [], 'data': ''}
        pcode = self.get_argument('pcode', '')
        site = self.get_argument('site', None)
        keyword = '' + pcode + '%'
        site_filter = True
        if (len(pcode) < 4):
            pcode = ''
        if not pcode and len(pcode) < 4:
            site_filter = (Area.is_site == site)
        try:
            areas = Area.select().where(
                (Area.code % keyword) & (Area.is_delete == 0) & (db.fn.length(Area.code) == len(pcode) + 4) & (
                    site_filter)).order_by(Area.sort)
            for area in areas:
                result['msg'].append({
                    'id': area.id,
                    'name': area.name,
                    'code': area.code,
                })
            result['flag'] = 1
        except Exception, e:
            print e

        self.write(simplejson.dumps(result))


@route(r'/mobile/get_circle_topics', name='get_circle_topics')  # 手机端登录
class MobileLoginHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def get(self):
        # index = self.get_argument("index", 999999999999)
        max = self.get_argument("max", None)
        min = self.get_argument("min", None)
        size = self.get_argument("size", 10)
        user_id = self.get_argument("uid", None)
        user_id_filter = True
        index_filter = True
        if user_id != None:
            user_id_filter = (CircleTopic.user == user_id)
        if ((max == None) and (min != None)):
            index_filter = (CircleTopic.id < min)
        if ((max != None) and (min == None)):
            index_filter = (CircleTopic.id > max)

        result = {'msg': '', 'flag': 0, 'msg': ''}
        msg = {'topics': [], 'pictures': [], 'praises': [], 'replies': []}

        try:
            topics = CircleTopic \
                .select() \
                .where((index_filter) & (CircleTopic.is_delete == 0) & (user_id_filter)) \
                .order_by(CircleTopic.id.desc()) \
                .limit(size)

            for topic in topics:
                msg['topics'].append({
                    'id': topic.id,
                    'user_id':topic.user.id,
                    'user_name': topic.user.username,
                    'user_photo': topic.user.portraiturl,
                    'content': topic.content,
                    'created': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(topic.created))
                })

            idx = CircleTopic \
                .select(CircleTopic.id) \
                .where((index_filter) & (CircleTopic.is_delete == 0)) \
                .order_by(CircleTopic.id.desc()) \
                .limit(size)

            idx = topics.alias('idx')
            pictures = (CircleTopicPic \
                        .select() \
                        .join(idx, on=(CircleTopicPic.topic == idx.c.id)) \
                        .order_by(CircleTopicPic.created.desc()))

            for picture in pictures:
                msg['pictures'].append({
                    'id': picture.id,
                    'topic_id': picture.topic.id,
                    'path': picture.path
                })

            praises = (CircleTopicPraise \
                       .select() \
                       .join(idx, on=(CircleTopicPraise.topic == idx.c.id)) \
                       .order_by(CircleTopicPraise.created.desc()))

            for praise in praises:
                msg['praises'].append({
                    'id': praise.id,
                    'topic_id': praise.topic.id,
                    'user_id': praise.user.id,
                    'user_name': praise.user.username
                })

            replies = (CircleTopicReply \
                       .select() \
                       .join(idx, on=(CircleTopicReply.topic == idx.c.id)) \
                       .where(CircleTopicReply.is_delete == 0) \
                       .order_by(CircleTopicReply.created.desc()))

            for reply in replies:
                i = {
                    'id': reply.id,
                    'topic_id': reply.topic.id,
                    'user_id': reply.user.id,
                    'user_name': reply.user.username,
                    'content': reply.content,
                    'replied_user_name': None,
                    'replied_user_id': None,
                }

                if reply.replied_user is not None:
                    i['replied_user_name'] = reply.replied_user.username
                    i['replied_user_id'] = reply.replied_user.id

                msg['replies'].append(i)

            result['msg'] = msg
            result['flag'] = 1

        except Exception, e:
            result['msg'] = '服务器异常'

        self.write(simplejson.dumps(result))


@route(r'/mobile/question', name='mobile_question')  # 用户中心-我提出的问题
class MobileGetProvincesHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', 'questions': [], 'bests': []}
        user_id = self.get_argument("userid", None)
        size = self.get_argument("size", None)
        max_id = self.get_argument("max_id", None)
        if not max_id:
            max_id = 9999999999
        try:
            ft = (Question.is_delete == 0) & (Question.id < max_id)
            if (user_id is not None):
                if (int(user_id) > 0):
                    ft = ft & (Question.user == user_id)
            else:
                ft = ft & ((Question.check_status == 0) or (Question.check_status == 1))
            q = Question.select().where(ft).order_by(Question.created.desc()).limit(size)
            for i in q:
                status = ''
                if i.check_status == 0:
                    status = '未审核'
                elif i.check_status == 1:
                    status = '通过'
                elif i.check_status == 2:
                    status = '未通过'
                user_name = i.user.nickname
                if not user_name:
                    user_name = i.user.username[:3] + "****" + i.user.username[7:]
                result['questions'].append({
                    'id': i.id,
                    'user_name': user_name,
                    'user_level': i.user.level,
                    'user_photo': i.user.portraiturl,
                    'user_id': i.user.id,
                    'title': i.title,
                    'content': i.content,
                    'scores': i.scores,
                    'clicks': i.clicks,
                    'answers': i.answers,
                    'publish_from': i.publish_from,
                    'check_status': status,
                    'created': time.strftime('%Y-%m-%d', time.localtime(i.created))
                })

            idx = q.alias('idx')
            a = (Answer \
                 .select() \
                 .join(idx, on=(Answer.question == idx.c.id)) \
                 .where((Answer.is_best == 1) & (Answer.is_delete == 0)) \
                 .order_by(Answer.created.desc()))

            for i in a:
                result['bests'].append({
                    'id': i.id,
                    'question_id': i.question.id,
                    'user_id': i.user.id,
                    'user_name': i.user.nickname,
                    'user_photo': i.user.portraiturl,
                    'user_level': i.user.level,
                    'content': i.content,
                    'created': time.strftime('%Y-%m-%d', time.localtime(i.created))

                })

            result['flag'] = 1

        except Exception, e:
            result['msg'] = '服务器异常'

        self.write(simplejson.dumps(result))


@route(r'/mobile/add_question', name='mobile_add_question')  # 手机端增加问题
class MobileAddQuestionHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': ''}
        args = simplejson.loads(self.request.body)
        try:
            title = args["title"]
            content = args["content"]
            publish_from = 'APP'
            created = int(time.time())
            user_id = args["uid"]
            imgs = []

            if args.has_key("imgs"):
                imgs = args["imgs"]

            i = Question.create(user=user_id, title=title, content=content, publish_from=publish_from,
                                created=created)

            for img in imgs:
                path_dir = 'upload/' + str(user_id / 10000) + '/' + str(user_id)
                filename = '%d%d.%s' % (int(time.time()), random.randint(1000, 9999), 'png')
                if not os.path.exists('upload/' + str(user_id / 10000)):
                    os.mkdir('upload/' + str(user_id / 10000))
                if not os.path.exists(path_dir):
                    os.mkdir(path_dir)
                with open(path_dir + '/' + filename, "wb") as f:
                    f.write(decodestring(img))
                    QuestionPic.create(user=user_id, question=i.id, path='/' + path_dir + '/' + filename,
                                       created=int(time.time()))

            result['data'] = {
                'id': i.id,
                'user_name': i.user.username,
                'user_id': i.user.id,
                'title': i.title,
                'content': i.content,
                'scores': i.scores,
                'publish_from': i.publish_from,
                'check_status': 2,
                'created': time.strftime('%Y-%m-%d', time.localtime(i.created))
            }
            result['flag'] = 1
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/question_answer', name='question_answer')  # 用户中心-我提出的问题
class MobileGetProvincesHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', 'question': None, 'myanswer': None, 'bests': [], 'answers': []}
        user_id = self.get_argument("uid", None)
        question_id = self.get_argument("question_id", None)

        try:
            qs = Question.select().where(Question.id == question_id)
            if qs.count() > 0:
                status = ''
                i = qs[0]
                if i.check_status == 0:
                    status = '未审核'
                elif i.check_status == 1:
                    status = '通过'
                elif i.check_status == 2:
                    status = '未通过'
                user_name = i.user.nickname
                if not user_name:
                    user_name = i.user.username[:3] + "****" + i.user.username[7:]
                result['question'] = {
                    'id': i.id,
                    'user_name': user_name,
                    'user_level': i.user.level,
                    'user_photo': i.user.portraiturl,
                    'user_id': i.user.id,
                    'title': i.title,
                    'content': i.content,
                    'scores': i.scores,
                    'clicks': i.clicks,
                    'answers': i.answers,
                    'publish_from': i.publish_from,
                    'check_status': status,
                    'created': time.strftime('%Y-%m-%d', time.localtime(i.created))
                }

            a = Answer.select().where((Answer.question == question_id) & (Answer.is_best == 1))
            for i in a:
                result['answers'].append({
                    'id': i.id,
                    'user_name': i.user.nickname,
                    'user_level': i.user.level,
                    'user_photo': i.user.portraiturl,
                    'user_id': i.user.id,
                    'content': i.content,
                    'supports': i.supports,
                    'created': time.strftime('%Y-%m-%d', time.localtime(i.created))
                })

            b = Answer.select().where((Answer.question == question_id) & (Answer.is_best == 1))
            for i in b:
                result['bests'].append({
                    'id': i.id,
                    'user_name': i.user.nickname,
                    'user_level': i.user.level,
                    'user_photo': i.user.portraiturl,
                    'user_id': i.user.id,
                    'content': i.content,
                    'supports': i.supports,
                    'created': time.strftime('%Y-%m-%d', time.localtime(i.created))
                })
            if user_id:
                qa = Answer.select().where(
                    (Answer.question == question_id) & (Answer.is_delete == 0) & (Answer.user == user_id))
                if qa.count() > 0:
                    # p = qa[0]
                    result['myanswer'] = {
                        'content': qa[0].content
                    }
            result['flag'] = 1

        except Exception, e:
            result['msg'] = '服务器异常'

        self.write(simplejson.dumps(result))

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': ''}
        args = simplejson.loads(self.request.body)
        user_id = args["uid"]
        question_id = args["question_id"]
        content = args["content"]
        opposes = 0
        supports = 0
        need_money = 0
        publish_from = "手机"
        is_best = 0
        is_anonymous = 0
        is_delete = 0
        created = int(time.time())
        try:
            question = Question.get(Question.id == question_id)
            qa = Answer.select().where(
                (Answer.question == question_id) & (Answer.is_delete == 0) & (Answer.user == user_id))
            if qa.count() > 0:
                p = qa[0]
            else:
                p = Answer()
                p.opposes = opposes
                p.supports = supports
                p.publish_from = publish_from
                p.is_best = is_best
                p.is_anonymous = is_anonymous
                p.is_delete = is_delete
                p.created = created
                p.question = question_id
                p.user = user_id
                question.answers = question.answers + 1
                p.need_money = need_money
                question.save()
            p.content = content
            p.save()
            result['msg'] = "解答成功！"
            result['flag'] = 1
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/support_answer', name='support_answer')  # 手机端增加问题
class MobileSupportAnswerHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': '', 'supports': 0}
        args = simplejson.loads(self.request.body)
        try:
            user_id = args["uid"]
            answer_id = args["answer_id"]

            a = Answer.select().where(Answer.id == answer_id)
            if a.count() > 0:
                answer = a[0]
                sas = SupportAnswer.select().where(
                    (SupportAnswer.answer == answer_id) & (SupportAnswer.user == user_id))
                if sas.count() > 0:
                    SupportAnswer.delete().where(SupportAnswer.id == sas[0].id).execute()
                    answer.supports = answer.supports - 1
                    result['msg'] = '已取消赞同'
                else:
                    answer.supports = answer.supports + 1
                    result['msg'] = '已赞同'
                    SupportAnswer.create(user=user_id, answer=answer_id, created=int(time.time()))

                answer.save()
                result['supports'] = answer.supports
                result['flag'] = 1
            else:
                result['flag'] = 2

        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/add_answer', name='mobile_add_answer')  # 手机端增加问题回答
class MobileAddAnswerHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': ''}
        args = simplejson.loads(self.request.body)
        try:
            content = args["content"]
            publish_from = '手机'
            created = int(time.time())
            userid = args["userid"]
            question = args["question_id"]

            i = Answer.create(user=userid, question=question, content=content, publish_from=publish_from,
                              created=created)

            result['data'] = {
                'id': i.id,
                'user_name': i.user.name,
                'user_id': i.user.id,
                'question_title': i.question.title,
                'question_content': i.question.content,
                'content': i.content,
                'publish_from': i.publish_from,
                'check_status': '未审核',
                'created': time.strftime('%Y-%m-%d', time.localtime(i.created))
            }
            result['flag'] = 1
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/service_code_history', name='mobile_service_code_history')  # 校验服务码历史
class MobileServiceCodeHistoryHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': []}
        # args = simplejson.loads(self.request.body)
        # sid = args["store_id"]
        sid = self.get_argument("store_id", None)
        try:
            if sid:
                sql = '''
                select used_year,used_month,used_day,COUNT(1) as used_count from tb_order_item_service where service_used=1 and store_id=%s
     GROUP BY used_year,used_month,used_day order by used_year desc,used_month desc,used_day
                '''
                q = db.handle.execute_sql(sql % (sid))
                old_year = ""
                old_month = ""
                month = {}
                qcount = 0
                for n in q:
                    qcount = qcount + 1
                    if old_year != n[0] or old_month != n[1]:
                        if qcount != 1:
                            result['msg'].append(month)
                        month = {
                            'year': n[0],
                            'month': n[1],
                            'items': []
                        }
                        month['items'].append({
                            'year': n[0],
                            'month': n[1],
                            'day': n[2],
                            'used_count': n[3],
                        })
                        old_year = n[0]
                        old_month = n[1]
                    else:
                        month['items'].append({
                            'year': n[0],
                            'month': n[1],
                            'day': n[2],
                            'used_count': n[3],
                        })
                if month:
                    result['msg'].append(month)
                result["flag"] = 1
            else:
                result["flag"] = 0
                result["msg"] = "参数传递错误！"
        except Exception, ex:
            result["flag"] = 0
            result["msg"] = "验证失败，数据异常：" + str(ex)
        self.write(simplejson.dumps(result))

# 手机端门店的订单
@route(r'/mobile/store_order', name='mobile_store_order')
class MobilStoreOrderHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'totalpage': 0, 'total': 0, 'items': []}
        store_id = self.get_argument("store_id")
        size = int(self.get_argument('size', 20))
        index = int(self.get_argument('index', 1))
        type = self.get_argument("type", 'all')

        ft = (Order.store == store_id)
        if type == 'unpay':  # 待付款订单
            ft = ft & ((Order.status == 0) & ((Order.payment == 1) | (Order.payment == 3)))
        elif type == 'unway':  # 待收货订单
            ft = ft & (Order.status == 3)
        elif type == 'undelivery':  # 待发货订单
            ft = ft & ((Order.status == 1) | (Order.status == 2))
        elif type == 'success':  # 已完成订单
            ft = ft & (Order.status == 4)
        elif type == 'yestoday':  # 昨日成交金额
            ft = ft & (Order.ordereddate == time.strftime("%Y-%m-%d", time.localtime(time.time()- 86400 * 1)))

        q = Order.select().where(ft).order_by(Order.ordered.desc())
        result['total'] = q.count()
        if result['total'] % size > 0:
            result['totalpage'] = result['total'] / size + 1
        else:
            result['totalpage'] = result['total'] / size
        paging_q = q.paginate(index, size)
        for n in paging_q:
            s = ''
            itemcolor = 'item-stable'
            scolor = ''
            if n.status == -1:
                s = '已删除'
            elif n.status == 0 and n.payment:
                s = '待付款'
                itemcolor = 'item-assertive'
                scolor = 'assertive'
            elif (n.status == 0 and n.payment == 0) or n.status == 1:
                s = '待处理'
                itemcolor = 'item-assertive'
                scolor = 'assertive'
            elif n.status == 2:
                s = '正在处理'
                itemcolor = 'item-balanced'
                scolor = 'balanced'
            elif n.status == 3:
                s = '待收货'
                itemcolor = 'item-balanced'
                scolor = 'balanced'
            elif n.status == 4:
                s = '交易完成'
            elif n.status == 5:
                s = '已取消'

            result['items'].append({
                'id': n.id,
                'ordernum': n.ordernum,
                'currentprice': n.currentprice,
                'status': s,
                'ordered': time.strftime('%Y-%m-%d', time.localtime(n.ordered)),
                'scolor': scolor,
                'itemcolor': itemcolor
            })
        self.write(simplejson.dumps(result))


@route(r'/mobile/getDeliverys', name='mobile_getDelivery')  # 获取物流公司
class MobileGetDeliverysHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = []
        list = Delivery.select()
        for n in list:
            result.append({
                'name': n.name,
                'id': str(n.id)
            })
        self.write(simplejson.dumps(result))


@route(r'/mobile/leave_topic_reply', name='leave_topic_reply')  # 手机端注册
class MobileLeaveTopicReplyHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        user_id = None
        content = None
        replied_user_id = None
        topic_id = None

        if args.has_key("id"):
            topic_id = args["id"]
        if args.has_key("uid"):
            user_id = args["uid"]
        if args.has_key("content"):
            content = args["content"]
        if args.has_key("replied_user_id"):
            replied_user_id = args["replied_user_id"]

        if replied_user_id == '':
            replied_user_id = None

        if (topic_id is not None) & (user_id is not None) & (content is not None):
            replay = CircleTopicReply.create(user=user_id, is_delete=0, publish_from='APP', content=content,
                                             topic=topic_id,
                                             replied_user=replied_user_id, created=int(time.time()));
            result["flag"] = 1
            result["id"] = replay.id
        else:
            result["msg"] = "信息不完整"

        self.write(simplejson.dumps(result))


@route(r'/mobile/delete_replay', name='delete_replay')  # 手机端注册
class MobileLeaveTopicReplyHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        id = None

        if args.has_key("id"):
            id = args["id"]

        if (id is not None):
            reply = None
            replies = CircleTopicReply.select().where(CircleTopicReply.id == id)
            if replies.count() > 0:
                reply = replies[0]

            if (reply != None):
                reply.is_delete = 1
                reply.save()

            result["flag"] = 1
        else:
            result["msg"] = "信息不完整"

        self.write(simplejson.dumps(result))


@route(r'/mobile/leave-topic-praise', name='leave-topic-praise')  # 手机端注册
class MobileLeaveTopicPraiseHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        user_id = None
        topic_id = None

        if args.has_key("id"):
            topic_id = args["id"]
        if args.has_key("uid"):
            user_id = args["uid"]

        if (topic_id is not None) & (user_id is not None):
            topics = CircleTopicPraise \
                .select(CircleTopicPraise.id) \
                .where((CircleTopicPraise.topic == topic_id) & (CircleTopicPraise.user == user_id))

            if topics.count() == 0:
                CircleTopicPraise.create(user=user_id, is_delete=0, publish_from='APP', topic=topic_id,
                                         created=int(time.time()));
                result["flag"] = 1
            else:
                result["msg"] = "您已赞"

        else:
            result["msg"] = "信息不完整"

        self.write(simplejson.dumps(result))


@route(r'/mobile/remove-topic', name='remove-topic')  # 手机端注册
class MobileLeaveTopicPraiseHandler(MobileHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        user_id = None
        topic_id = None

        if args.has_key("id"):
            topic_id = args["id"]
        if args.has_key("uid"):
            user_id = args["uid"]

        if (topic_id is not None) & (user_id is not None):
            topics = CircleTopic \
                .select() \
                .where((CircleTopic.id == topic_id) & (CircleTopic.user == user_id))

            if topics.count() > 0:
                topics[0].is_delete = 1
                topics[0].save()
                result["flag"] = 1

        self.write(simplejson.dumps(result))

@route(r'/mobile/deliveryOrder', name='mobile_deliveryOrder')  # 手机端处理订单
class MobileDeliveryOrderHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 1, 'msg': '操作成功！'}
        args = simplejson.loads(self.request.body)
        # oid = args["id"]
        id = args["id"]
        num = args["num"]
        did = args["did"]
        status = int(args["status"])
        try:
            OrderChangeStatus(id, status, 0, self)
            order = Order.get(id=id)
            order.change_status(3)
            order.delivery = did
            order.deliverynum = num
            order.delivery_time = int(time.time())
            # order.lasteditedby = self.get_admin_user()
            order.lasteditedtime = int(time.time())
            order.save()
            d = Delivery.get(id=did)
            if order.address:
                if order.address.mobile:
                    try:
                        sms = {'mobile': order.address.mobile,'body': order.ordernum, 'signtype': '1', 'isyzm': 'shipments'}
                            #'body': u"订单号：" + order.ordernum + u"商品已发出，登录电脑端查看详情。质量投诉请拨" + self.settings['com_tel'],
                        create_msg(simplejson.dumps(sms), 'sms')  #发货
                    except Exception, e:
                        pass
        except Exception, e:
            result['flag'] = 0
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/mobile/get_auto', name='mobile_getAuto')  # 获取物流公司
class MobileGetDeliverysHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {
            'flag': 0,
            'msg': ''
        }

        car = None
        user_id = self.get_argument("uid", None)
        cars = UserCarInfo \
            .select() \
            .where((UserCarInfo.user == user_id) & (UserCarInfo.is_delete == 0))

        if cars.count() > 0:
            car = cars[0]

        if car is not None:
            result['msg'] = {
                # 'brand_code': car.brand_code,
                'auto_id': car.id,
                'mileage': car.mileage,
                'buy_time': time.strftime('%Y-%m-%d', time.localtime(car.buy_time)),
                'chassis_num': car.chassis_num,
                'car_num': car.car_num,
                'brand_code': None if (car.brand is None) else car.brand.code,
                'brand_id': None if (car.brand is None) else car.brand.id,
                'created': time.strftime('%Y-%m-%d', time.localtime(car.created)),
                'brand': []
            }

            brand_code = result['msg']['brand_code']
            code_filter = (Brand.code == brand_code)
            i = 1

            if brand_code is not None:
                for i in range(1, len(brand_code) / 4):
                    code_filter = code_filter | (Brand.code == brand_code[0:(i * 4)])

            # if brand_code.length() >= 12:
            #     code_filter = ((Brand.code == brand_code[0:4]) & (Brand.code == brand_code[0:]))
            brands = Brand.select().where((code_filter) & (Brand.is_delete == 0)).order_by(
                Brand.code.asc())
            for brand in brands:
                result['msg']['brand'].append({
                    'id': brand.id,
                    'code': brand.code,
                    'name': brand.name
                })
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/get_brands', name='mobile_getBrands')  # 获取物流公司
class MobileGetDeliverysHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {
            'flag': 0,
            'msg': []
        }

        car = None
        id = self.get_argument("id", 0)

        brands = Brand \
            .select() \
            .where((Brand.pid == id) & (Brand.is_delete == 0))

        for brand in brands:
            result['msg'].append({
                'id': brand.id,
                'pid': brand.pid,
                'code': brand.code,
                'name': brand.name
            })
        result['flag'] = 1

        self.write(simplejson.dumps(result))


@route(r'/mobile/messages', name='mobile_mesages')
class MobileGetDeliverysHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {
            'flag': 0,
            'msg': []
        }

        user_id = self.get_argument("uid", 0)
        max = self.get_argument("max", 999999999999)
        size = self.get_argument("size", 20)
        messages = UserMessage.select().where((UserMessage.user == user_id) & (UserMessage.id < max)).limit(
            size).order_by(
            UserMessage.id.desc())

        for message in messages:
            result['msg'].append({
                'id': message.id,
                'type': message.type,
                'title': message.title,
                'content': message.content,
                'has_read': message.has_read,
                'send_time': time.strftime('%Y-%m-%d', time.localtime(message.send_time))
            })
        result['flag'] = 1

        self.write(simplejson.dumps(result))


@route(r'/mobile/messages_detail', name='mobile_mesages_detail')
class MobileGetDeliverysHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {
            'flag': 0,
            'msg': []
        }
        args = simplejson.loads(self.request.body)
        id = args["id"]
        mark = False
        if args.has_key("mark"):
            mark = args["mark"]
        messages = UserMessage.select().where(UserMessage.id == id)
        if messages.count() > 0:
            result['msg'] = {
                'id': messages[0].id,
                'type': messages[0].type,
                'title': messages[0].title,
                'content': messages[0].content,
                'has_read': 1,
                'send_time': time.strftime('%Y-%m-%d', time.localtime(messages[0].send_time))
            }

            if mark == True:
                messages[0].has_read = 1
                messages[0].save()

        result['flag'] = 1

        self.write(simplejson.dumps(result))


@route(r'/mobile/message_clear', name='mobile_message_clear')
class MobileGetDeliverysHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {
            'flag': 0,
            'msg': []
        }
        args = simplejson.loads(self.request.body)
        user_id = args["uid"]
        message_id = None
        if args.has_key("mid"):
            message_id = args["mid"]

        if message_id is None:
            command = UserMessage.delete().where(UserMessage.user == user_id)
            command.execute()
        else:
            command = UserMessage.delete().where((UserMessage.user == user_id) & (UserMessage.id == message_id))
            command.execute()

        result['flag'] = 1

        self.write(simplejson.dumps(result))


@route(r'/mobile/edit_profile', name='mobile_editProfile')  # 获取物流公司
class MobileGetDeliverysHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {
            'flag': 0,
            'msg': []
        }
        args = simplejson.loads(self.request.body)

        try:
            portrait = None
            auto_id = None
            nickname = args["nickname"]
            birthday = args["birthday"]
            buy_time = args["buy_time"]
            car_num = args["car_num"]
            chassis_num = args["chassis_num"]
            brand_id = args["brand_id"]
            if args.has_key("auto_id"):
                auto_id = args["auto_id"]
            uid = args["uid"]
            mileage = args["mileage"]
            created = args["created"]
            portrait_path = None
            if args.has_key("portrait"):
                portrait = args["portrait"]

            if portrait is not None:
                path_dir = 'upload/' + str(uid / 10000) + '/' + str(uid)
                filename = '%d%d.%s' % (int(time.time()), random.randint(1000, 9999), 'png')
                if not os.path.exists('upload/' + str(uid / 10000)):
                    os.mkdir('upload/' + str(uid / 10000))
                if not os.path.exists(path_dir):
                    os.mkdir(path_dir)
                with open(path_dir + '/' + filename, "wb") as f:
                    f.write(decodestring(portrait))
                    portrait_path = '/' + path_dir + '/' + filename

            users = User.select().where(User.id == uid)
            if users.count() > 0:
                user = users[0]
                if portrait_path is not None:
                    user.portraiturl = portrait_path

                user.birthday = birthday
                user.nickname = nickname
                user.save()

            if auto_id is not None:
                autos = UserCarInfo.select().where(UserCarInfo.id == auto_id)
                if autos.count() > 0:
                    auto = autos[0]
                    auto.car_num = car_num
                    auto.chassis_num = chassis_num
                    auto.brand = brand_id
                    auto.mileage = mileage
                    try:
                        auto.created = time.mktime(time.strptime(created, "%Y-%m-%d"))
                    except Exception, e:
                        print e
                    auto.buy_time = time.mktime(time.strptime(buy_time, "%Y-%m-%d"))
                    auto.save()
            else:
                UserCarInfo.create(user=uid,
                                   car_num=car_num,
                                   chassis_num=chassis_num,
                                   brand_id=brand_id,
                                   mileage=mileage,
                                   crated=(0 if (created is None) else time.mktime(time.strptime(created, "%Y-%m-%d"))),
                                   buy_time=(
                                       0 if (buy_time is None) else time.mktime(time.strptime(buy_time, "%Y-%m-%d"))))

            result['flag'] = 1

        except Exception, e:
            result['msg'] = e.message

        self.write(simplejson.dumps(result))  # /mobile/edit_profile


@route(r'/mobile/store_summary', name='store_summary')  # 获取物流公司
class MobileStoreSummaryHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {
            'flag': 0,
            'msg': {
                'totalOrders': 0,
                'unpayOrders': 0,
                'processOrders': 0,
                'nowayOrders': 0,
                'unsumeOrders': 0,
                'totalPriceYesterday': 0
            }
        }
        store_id = self.get_argument("sid", None)

        # 今日订单数
        sql = 'select count(1) as result from tb_orders where store_id = ' + store_id + ' and ordereddate =  date_format(now(), "%s-%s-%s")'
        q = db.handle.execute_sql(sql, ('%Y', '%d', '%m'))
        rows = q.fetchall()
        result['msg']['totalOrders'] = (0 if (rows[0][0] is None) else rows[0][0])

        # 待付款
        sql = 'select count(1) as result from tb_orders where store_id = ' + store_id + ' and status = 0'
        q = db.handle.execute_sql(sql)
        rows = q.fetchall()
        result['msg']['unpayOrders'] = (0 if (rows[0][0] is None) else rows[0][0])

        # 待处理
        sql = 'select count(1) as result from tb_orders where store_id =  ' + store_id + '  and status = 1'
        q = db.handle.execute_sql(sql)
        rows = q.fetchall()
        result['msg']['processOrders'] = (0 if (rows[0][0] is None) else rows[0][0])

        # 待发货
        sql = 'select count(1) as result from tb_orders where store_id =  ' + store_id + ' and status = 2'
        q = db.handle.execute_sql(sql)
        rows = q.fetchall()
        result['msg']['nowayOrders'] = (0 if (rows[0][0] is None) else rows[0][0])

        # 待结算金额
        sql = 'select sum(price) as result from tb_orders where store_id =  ' + store_id + ' and status = 4 and settlement_id is  null'
        q = db.handle.execute_sql(sql)
        rows = q.fetchall()
        result['msg']['unsumeOrders'] = (0 if (rows[0][0] is None) else rows[0][0])

        # 昨日成交金
        sql = 'select sum(currentprice) as result from tb_orders where store_id =  ' + store_id + ' and ordereddate =  "' + time.strftime("%Y-%m-%d", time.localtime(time.time()- 86400 * 1)) + '"'
        q = db.handle.execute_sql(sql)
        rows = q.fetchall()
        result['msg']['totalPriceYesterday'] = round((0 if (rows[0][0] is None) else rows[0][0]),2)
        result['flag'] = 1
        self.write(simplejson.dumps(result))  # /mobile/edit_profile

# 结算历史
@route(r'/mobile/settlement_history', name='settlement_history')
class MobileSettlementHistoryHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {
            'flag': 0,
            'msg': []
        }
        store_id = self.get_argument("sid", None)
        user_id = self.get_argument("uid", None)
        max = self.get_argument('max', 999999999999)

        uid = int(user_id)
        rows = Score.select().where((Score.isactive==1) & (Score.jftype==2) & (Score.user==uid) &
                                    (Score.id < max) ).order_by(Score.created.desc()).limit(20)
        for row in rows:
            result['msg'].append({
                'id': row.id,
                'orderType': 'I',    #保险商品
                'order_count': 1,
                'sum_money': 0 if not row.remark else float(row.remark),
                'created': None if row.created is None else time.strftime('%Y-%m-%d', time.localtime(row.created))
            })

        rows = Settlement.select().where((Settlement.user == user_id) & (Settlement.id < max)).order_by(
            Settlement.id.desc()).limit(20)
        for row in rows:
            result['msg'].append({
                'id': row.id,
                'orderType': 'S',   #普通商品
                'order_count': row.settlement_orders.count(),
                'sum_money': row.sum_money,
                'created': None if row.created is None else time.strftime('%Y-%m-%d', time.localtime(row.created))
            })
        sql = 'select sum(price) as result from tb_orders where store_id =  ' + store_id + ' and status = 4 and settlement_id is  null'
        q = db.handle.execute_sql(sql)
        rows = q.fetchall()
        result['unsumeOrders'] = (0 if (rows[0][0] is None) else rows[0][0])


        sql = 'select cashed_money from tb_users where id=' + user_id;
        q = db.handle.execute_sql(sql)
        rows = q.fetchall()
        result['cashed_money'] = (0 if (rows[0][0] is None) else rows[0][0])

        result['flag'] = 1
        self.write(simplejson.dumps(result))  # /mobile/edit_profile


@route(r'/mobile/settlement_detail', name='settlement_detail')  # 获取物流公司
class MobileSettlementDetailHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {
            'flag': 0,
            'msg': None
        }

        id = self.get_argument("id", None)
        rows = Settlement.select().where(Settlement.id == id)
        for row in rows:
            order = {
                'id': row.id,
                'orders': [],
                'order_count': row.settlement_orders.count(),
                'sum_money': row.sum_money,
                'created': None if row.created is None else time.strftime('%Y-%m-%d', time.localtime(row.created))
            }

            for o in row.settlement_orders:
                order['orders'].append({
                    'id': o.id,
                    'number': o.ordernum,
                    'price': o.price,
                    'created': None if not o.ordered else time.strftime('%Y-%m-%d', time.localtime(o.ordered))
                })

            result['msg'] = order

        result['flag'] = 1
        self.write(simplejson.dumps(result))  # /mobile/edit_profile


@route(r'/mobile/settlement_order', name='settlement_order')  # 获取物流公司
class MobileSettlementOrderHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {
            'flag': 0,
            'msg': []
        }

        store_id = self.get_argument("sid", None)
        max = self.get_argument("max", 9999999999999)
        rows = Order.select().where(
            (Order.store == store_id) & (Order.status == 4) & (Order.settlement == None) & (
                Order.id < max)).order_by(
            Order.id.desc()).limit(20)
        for row in rows:
            result['msg'].append({
                'id': row.id,
                'created': row.ordered,
                'order_number': row.ordernum,
                'price': row.price
            })

        result['flag'] = 1
        self.write(simplejson.dumps(result))  # /mobile/edit_profile


@route(r'/settlement/resume', name='SettlementResume')  # 用户订单结算
class OrderHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        ids = simplejson.loads(args["ids"])
        user_id = args["uid"]

        try:
            u = None
            rows = User.select().where(User.id == user_id)
            if rows.count() > 0:
                u = rows[0]

            if u and len(ids) > 0:
                s = Settlement()
                s.user = u
                s.sum_money = 0
                s.created = int(time.time())
                s.save()
                sum_money = 0
                for n in ids:
                    order = Order.get(id=n)
                    if not order.settlement:
                        order.settlement = s
                        sum_money = sum_money + order.price
                        order.save()
                s.sum_money = sum_money
                s.save()
                u.cashed_money = u.cashed_money + sum_money
                u.save()
                result['flag'] = 1
            else:
                result['flag'] = 1
                result['msg'] = "请登录后至少选择一个订单！"

        except Exception, e:
            print e
            result['flag'] = 0
            result['msg'] = e.message

        self.write(simplejson.dumps(result))

# 提现历史记录
@route(r'/mobile/withdraw_history', name='withdraw_history')
class MobileWithdrawHistoryHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': []}
        user_id = self.get_argument("uid", None)
        max = self.get_argument('max', 999999999999)

        try:
            rows = Withdraw.select().where((Withdraw.user == user_id) & (Withdraw.id < max)).order_by(
                                                                        Withdraw.id.desc()).limit(10)
            for row in rows:
                result['msg'].append({
                    'id': row.id,
                    'account_type': row.account_type,
                    'account_truename': row.account_truename,
                    'account_name': row.account_name,
                    'account_branchname': row.account_branchname,
                    'account_account': row.account_account,
                    'sum_money': row.sum_money,
                    'account_name': row.account_name,
                    'apply_time': None if row.apply_time is None else time.strftime('%Y-%m-%d',time.localtime(row.apply_time)),
                    'processing_time': time.strftime('%Y-%m-%d',time.localtime(row.apply_time)) if row.processing_time is None else time.strftime('%Y-%m-%d',
                                                        time.localtime(row.processing_time)),
                    'processing_result': row.processing_result
                })
            result['flag'] = 1

        except Exception, e:
            result['msg'] = e.message
            print e;

        self.write(simplejson.dumps(result))  # /mobile/edit_profile

# 首页银行卡
@route(r'/mobile/bank', name='Bank')
class MobileBankHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': ''}
        user_id = self.get_argument('uid', None)

        try:
            u = None
            rows = User.select().where(User.id == user_id)
            if rows.count() > 0:
                u = rows[0]
                if type(u.bank_name) == type(u'字符串'):
                    utf8BankName = u.bank_name[:4]
                elif type(u.bank_name) == type('str'):
                    utf8BankName = u.bank_name[:8]
                else:
                    utf8BankName = u.bank_name
                result['msg'] = {
                    'bank_truename': u.bank_truename,
                    'bank_name': utf8BankName,
                    'bank_branchname': u.bank_branchname,
                    'bank_account': u.bank_account
                }

            result['flag'] = 1

        except Exception, e:
            print e
            result['flag'] = 0
            result['msg'] = e.message

        self.write(simplejson.dumps(result))


# 首页支付宝
@route(r'/mobile/alipay', name='alipay')
class MobileAlipayHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'data': {'alipay_truename': '', 'alipay_account': ''}, 'msg': ''}
        user_id = self.get_argument('uid', None)

        try:
            u = User.get(id = user_id)
            result['data'] = {
                'alipay_truename': u.alipay_truename,
                'alipay_account': u.alipay_account
            }
            result['flag'] = 1
        except Exception, e:
            logging.info('Error: /mobile/alipay, %s'%e.message)
            result['msg'] = e.message

        self.write(simplejson.dumps(result))

# 用户绑定支付宝
@route(r'/mobile/bind_alipay', name='BindAlipay')
class MobileBindAlipayHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def check_alipay(self, name, account):
        if name.strip() == '':
            return False
        if not (re.match('^[A-Za-z]+$', name) or re.match(u'^[\u4e00-\u9fa5]+$', name)):
            return False
        if ('.com' in account) or ('.cn' in account) or ('.cc' in account) or ('.net' in account) or (len(account)==11 and account.isdigit()):
            return True
        else:
            return False

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        user_id = args["uid"]
        alipay_truename = args["alipay_truename"]
        alipay_account = args["alipay_account"]
        vcode = args["vcode"]

        try:
            u = User.get(id = user_id)
            uv = UserVcode.select().where((UserVcode.mobile == u.mobile) & (UserVcode.vcode == vcode) & (UserVcode.flag == 1))
            if not uv.count() > 0:
                result['msg'] = u'请输入正确的验证码'
            elif not self.check_alipay(alipay_truename, alipay_account):
                result['msg'] = u'姓名或支付宝账号不正确'
            else:
                u.alipay_truename = alipay_truename
                u.alipay_account = alipay_account
                u.save()
                result['flag'] = 1
                result['msg'] = u'绑定银行卡成功'
        except Exception, e:
            logging.info('Error: /mobile/bind_alipay, %s'%e.message)
            result['msg'] = u'用户不存在'

        self.write(simplejson.dumps(result))


# 用户获取银行名称
@route(r'/mobile/get_bank_name', name='GetBankName')
class MobileGetBankNameHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': {'id':0, 'bank_name':''}, 'log':''}
        bank_number = self.get_argument('no', None)

        try:
            rows = BankCard.select().where(BankCard.card_bin == db.fn.LEFT(bank_number, BankCard.bin_digits))
            if rows.count() > 0:
                u = rows[0]
                result['msg'] = {
                    'id': u.id,
                    'bank_name': u.bank_name
                }
                result['flag'] = 1
            else:
                result['log'] = u'未查找到该卡银行'
        except Exception, e:
            result['log'] = e.message
            logging.info('Error: /mobile/get_bank_name, %s'%e.message)

        self.write(simplejson.dumps(result))

# 用户绑定银行卡
@route(r'/mobile/bind_bank', name='BindBank')
class MobileBindBankHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def check_alipay(self, name, account):
        if name.strip() == '':
            return False
        if not (re.match('^[A-Za-z]+$', name) or re.match(u'^[\u4e00-\u9fa5]+$', name)):
            return False
        accountC = len(account)
        if (((accountC>17 and accountC<22) or accountC==16) and account.isdigit()):
            return True
        else:
            return False

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        user_id = args["uid"]
        bank_truename = args["bank_truename"]
        bank_name = args["bank_name"]
        bank_branchname = args["bank_branchname"]
        bank_account = args["bank_account"]
        vcode = args["vcode"]

        try:
            rows = User.select().where(User.id == user_id)
            if rows.count() > 0:
                u = rows[0]
                if not UserVcode.select().where((UserVcode.mobile == u.mobile) & (UserVcode.vcode == vcode) & (UserVcode.flag == 1)).count() > 0:
                    result['msg'] = "请输入正确的验证码"
                elif not self.check_alipay(bank_truename, bank_account):
                    result['msg'] = "卡号或持卡人姓名不正确"
                else:
                    u.bank_truename = bank_truename
                    u.bank_name = bank_name
                    u.bank_branchname = bank_branchname
                    u.bank_account = bank_account
                    u.save()
                    result['flag'] = 1
                    result['msg'] = '绑定银行卡成功'
            else:
                result['flag'] = 0
                result['msg'] = '用户不存在'
        except Exception, e:
            logging.info('Error: /mobile/bind_bank, %s'%e.message)
            result['msg'] = e.message

        self.write(simplejson.dumps(result))

# 提现首页
@route(r'/mobile/store/get_bank', name='mobile_store_get_bank')
class MobileStoreGetBankHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '','data':{}}
        user_id = self.get_argument('uid', None)
        users = User.select().where(User.id == user_id)
        if users.count() == 0:
            result['msg'] = '您还没有注册'
            self.write(simplejson.dumps(result))
            return
        user = users[0]
        result['flag'] = 1
        bank_icon = 'default.png'
        if "北京" in user.bank_name:
            bank_icon = "beijing.png"
        elif "工商" in user.bank_name:
            bank_icon = "gongshang.png"
        elif "光大" in user.bank_name:
            bank_icon = "guangda.png"
        elif "广发" in user.bank_name:
            bank_icon = "guangfa.png"
        elif "华夏" in user.bank_name:
            bank_icon = "huaxia.png"
        elif "建设" in user.bank_name:
            bank_icon = "jianshe.png"
        elif "交通" in user.bank_name:
            bank_icon = "jiaotong.png"
        elif "民生" in user.bank_name:
            bank_icon = "minsheng.png"
        elif "农业" in user.bank_name:
            bank_icon = "nonghang.png"
        elif "平安" in user.bank_name:
            bank_icon = "pingan.png"
        elif "浦发" in user.bank_name:
            bank_icon = "pufa.png"
        elif "兴业" in user.bank_name:
            bank_icon = "xingye.png"
        elif "邮政" in user.bank_name:
            bank_icon = "youchu.png"
        elif "招商" in user.bank_name:
            bank_icon = "zhaoshang.png"
        elif "中国银行" in user.bank_name:
            bank_icon = "zhongguo.png"
        elif "中信" in user.bank_name:
            bank_icon = "zhongxin.png"
        else:
            bank_icon = "default.png"
        bank_icon = "img/yinhang/" + bank_icon
        bank_account_abb = user.bank_account
        if len(user.bank_account)>4:
            bank_account_abb = user.bank_account[-4:]
        if type(user.bank_name) == type(u'字符串'):
            utf8BankName = user.bank_name[:4]
        elif type(user.bank_name) == type('str'):
            utf8BankName = user.bank_name[:8]
        else:
            utf8BankName = user.bank_name
        result['data'] = {
            "alipay_truename": user.alipay_truename,
            "alipay_account": user.alipay_account,
            "bank_icon": bank_icon,
            "bank_truename": user.bank_truename,
            "bank_name": utf8BankName,
            "bank_branchname": user.bank_branchname,
            "bank_account": user.bank_account,
            "bank_account_abb": bank_account_abb
        }

        self.write(simplejson.dumps(result))

# 提现验证码
@route(r'/mobile/store/cash', name='mobile_store_cash')
class MobileStoreCashHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        user_id = args["uid"]
        users = User.select().where(User.id == user_id)
        if users.count() == 0:
            result['msg'] = '您还没有注册'
            self.write(simplejson.dumps(result))
            return
        user = users[0]
        mobile = user.mobile
        if user.mobile is None:
            result['msg'] = '您的账户还没有绑定手机号，请先绑定手机号'
            self.write(simplejson.dumps(result))
            return

        user = users[0]
        UserVcode.delete().where(UserVcode.created < (int(time.time()) - 30 * 60)).execute()

        uservcode = UserVcode()
        uservcode.mobile = user.mobile
        uservcode.vcode = random.randint(1000, 9999)
        uservcode.created = int(time.time())
        uservcode.flag = 3
        try:
            uservcode.validate()
            if UserVcode.select().where((UserVcode.mobile == mobile) & (UserVcode.flag == 1)).count() > 3:
                result['msg'] = '您的操作过于频繁，请稍后再试'
            else:
                uservcode.save()
                result['flag'] = 1
                result['msg'] = '验证码已发送'
                sms = {'mobile': user.mobile, 'body': str(uservcode.vcode), 'signtype': '1', 'isyzm': 'vcodeNew'}
                create_msg(simplejson.dumps(sms), 'sms') #验证码
        except Exception, ex:
            logging.info('Error: /mobile/store/cash, %s'%ex.message)
            result['msg'] = '验证码发送失败，请联系400客服处理'

        self.write(simplejson.dumps(result))

# 提现到银行卡
@route(r'/mobile/store/cash_sume', name='mobile_store_cash_sume')
class MobileStoreCashHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        user_id = args["uid"]
        money = float(args["money"])
        code = args["code"]
        users = User.select().where(User.id == user_id)
        checkaccount = 0
        if users.count() > 0:
            user = users[0]
            if type(user.bank_account) == type('str') or type(user.bank_account) == type(u'字符串'):
                checkaccount = user.bank_account.isdigit()
            if not checkaccount:
                result['msg'] = '您的账户没有绑定银行卡信息，或者缺失，请补充银行卡信息后再试'
            else:
                if money > user.cashed_money:
                    result['msg'] = '提现金额不能超过您当前的余额，请重试'
                elif money < 100:
                    result['msg'] = '抱歉，提现金额不能小于100元'
                else:
                    try:
                        if UserVcode.select().where((UserVcode.mobile == user.mobile) & (UserVcode.vcode == code) & (
                                    UserVcode.flag == 3)).count() > 0:
                            with db.handle.transaction():
                                Withdraw.create(user=user_id, account_type=0, account_truename=user.bank_truename,
                                                account_name=user.bank_name, account_branchname=user.bank_branchname,
                                                account_account=user.bank_account,sum_money=money, processing_result='正在处理',
                                                apply_time=int(time.time()))
                                user.cashed_money = user.cashed_money - money
                                user.save()
                                mobile = user.mobile    #给客户的短信
                                sms = {'mobile': mobile, 'body': [str(money), str(user.cashed_money)],
                                       'signtype': '1','isyzm': 'cashMoney'}
                                #您提交的提现%s元的订单已经有财务美眉受理请耐心等候。提现后剩余%s元
                                create_msg(simplejson.dumps(sms), 'sms')
                                mobile = setting.financeMobiles  #财务电话
                                store = Store.get(id=user.store)
                                addr = Area().get_detailed_address(store.area_code)
                                company = store.name
                                payment = u'银行卡'
                                #地区:${addr}；公司:${company} ${people}；申请提现:${money}元；方式:${payment}；
                                sms = {'mobile': mobile, 'body': [addr, company, user.mobile ,str(money), payment],
                                       'signtype': '1','isyzm': 'cashMoneySys'}
                                create_msg(simplejson.dumps(sms), 'sms')  #提现我们
                            result['flag'] = 1
                            result['msg'] = u'提现已成功受理'
                        else:
                            result['msg'] = '验证码不正确，请检查'
                    except Exception, ex:
                        result['msg'] = '服务器异常'
        else:
            result['msg'] = '您的账户异常，请联系客服'

        self.write(simplejson.dumps(result))

# 提现到支付宝
@route(r'/mobile/store/cash_alipay', name='mobile_store_cash_alipay')
class MobileStoreCashAlipayHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        user_id = args["uid"]
        money = float(args["money"])
        code = args["code"]
        checkaccount = 0
        try:
            user = User.get(id=user_id)
            if type(user.alipay_account) == type('str') or type(user.alipay_account) == type(u'字符串'):
                if (user.alipay_account.isdigit()) or ('com' in user.alipay_account):
                    checkaccount = 1
            if checkaccount == 0:
                result['msg'] = '您的账户没有绑定支付宝信息，或者缺失，请补充银行卡信息后再试'
            else:
                if money > user.cashed_money:
                    result['msg'] = '提现金额不能超过您当前的余额，请重试'
                elif money < 100:
                    result['msg'] = '抱歉，提现金额不能小于100元'
                else:
                    if UserVcode.select().where((UserVcode.mobile == user.mobile) & (UserVcode.vcode == code) & (
                                UserVcode.flag == 3)).count() > 0:
                        with db.handle.transaction():
                            Withdraw.create(user=user_id, account_type=1, account_truename=user.bank_truename,
                                            account_name=user.alipay_truename, account_account=user.alipay_account,
                                            sum_money=money, processing_result='正在处理',apply_time=int(time.time()))
                            user.cashed_money = user.cashed_money - money
                            user.save()
                            mobile = user.mobile    #给客户的短信
                            #您提交的提现%s元的订单已经有财务美眉受理请耐心等候。提现后剩余%s元
                            sms = {'mobile': mobile, 'body': [str(money), str(user.cashed_money)], 'signtype': '1','isyzm': 'cashMoney'}
                            create_msg(simplejson.dumps(sms), 'sms')  #提现客户
                            mobile = setting.financeMobiles  #财务电话
                            store = Store.get(id=user.store)
                            addr = Area().get_detailed_address(store.area_code)
                            company = store.name
                            payment = u'支付宝'
                            #地区:${addr}；公司:${company} ${people}；申请提现:${money}元；方式:${payment}；
                            sms = {'mobile': mobile, 'body': [addr, company, user.mobile ,str(money), payment],
                                   'signtype': '1','isyzm': 'cashMoneySys'}
                            create_msg(simplejson.dumps(sms), 'sms')  #提现我们
                        result['flag'] = 1
                        result['msg'] = u'提现已成功受理'
                    else:
                        result['msg'] = '验证码不正确，请检查'
        except Exception, ex:
            result['msg'] = '您的账户异常，请联系客服'

        self.write(simplejson.dumps(result))


@route(r'/mobile/store_profile', name='store_profile')  # 获取物流公司
class MobileStoreProfileHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {
            'flag': 0,
            'msg': None
        }

        store_id = self.get_argument("sid", None)
        rows = Store.select().where(Store.id == store_id)
        if rows.count() > 0:
            result['msg'] = {
                'id': rows[0].id,
                'address': rows[0].address,
                'tel': rows[0].tel,
                'link_man': rows[0].link_man,
                'area_code': rows[0].area_code,
                'mobile': rows[0].mobile,
                'areas': []

            }

            # areas = Area.select().where((Area.code % "'"+rows[0].area_code[0:4]+"'"))

            idx = Area.select(Area.id).where(
                (Area.code == db.fn.LEFT(rows[0].area_code, 4)) | (
                    Area.code == db.fn.LEFT(rows[0].area_code, 8)) | (
                    Area.code == db.fn.LEFT(rows[0].area_code, 12)) | (
                    Area.code == db.fn.LEFT(rows[0].area_code, 16)))

            areas = Area.select().where(Area.pid << idx)

            for area in areas:
                result['msg']['areas'].append({
                    'id': area.id,
                    'code': area.code,
                    'name': area.name
                })

        result['flag'] = 1
        self.write(simplejson.dumps(result))  # /mobile/edit_profile


@route(r'/mobile/store/change_cover', name='store_change_cover')  # 获取物流公司
class MobileEditStoreProfileHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {
            'flag': 0,
            'msg': None
        }

        args = simplejson.loads(self.request.body)
        img = args["source"]
        store_id = args["sid"]
        user_id = args["uid"]

        try:
            stores = Store.select().where(Store.id == store_id)
            if stores.count() > 0:
                store = stores[0]
                path_dir = 'upload/' + str(user_id / 10000) + '/' + str(user_id)
                filename = '%d%d.%s' % (int(time.time()), random.randint(1000, 9999), 'jpg')
                if not os.path.exists('upload/' + str(user_id / 10000)):
                    os.mkdir('upload/' + str(user_id / 10000))
                if not os.path.exists(path_dir):
                    os.mkdir(path_dir)
                with open(path_dir + '/' + filename, "wb") as f:
                    f.write(decodestring(img))

                store.image = '/' +  path_dir + '/' + filename
                store.save()
                result['msg'] = store.image
            result['flag'] = 1
        except Exception, e:
            print e

        self.write(simplejson.dumps(result))


@route(r'/mobile/edit_store_profile', name='edit_store_profile')  # 获取物流公司
class MobileEditStoreProfileHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {
            'flag': 0,
            'msg': None
        }

        args = simplejson.loads(self.request.body)
        id = args["id"]
        try:
            stores = Store.select().where(Store.id == id)
            if stores.count() > 0:
                store = stores[0]
                store.address = args["address"]
                store.tel = args["tel"]
                store.link_man = args["link_man"]
                store.area_code = args["area_code"]
                store.mobile = args["mobile"]
                store.save()
            result['flag'] = 1
        except Exception, e:
            print e

        self.write(simplejson.dumps(result))

# 申请成为服务门店 申请入驻
@route(r'/mobile/apply_store', name='mobile_apply_store')
class MobileApplyStoreHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    @require_basic_authentication
    def post(self):
        result = {
            'flag': 0,
            'msg': None
        }
        args = simplejson.loads(self.request.body)
        uid = args["uid"]
        name = args["name"]
        area_code = args["area_code"]
        address = args["address"]
        link_man = args["link_man"]
        image = ''
        image_legal = ''
        image_license = ''

        try:
            user = User.get(id=uid)
            store = user.store
            if not store:
                store = Store()
            store.name = name
            store.area_code = area_code
            store.address = address
            store.link_man = link_man
            if args.has_key("image") and args["image"]:
                image = self.upload_store_image(uid, args["image"])
            if args.has_key("image_legal") and args["image_legal"]:
                image_legal = self.upload_store_image(uid, args["image_legal"])
            if args.has_key("image_license") and args["image_license"]:
                image_license = self.upload_store_image(uid, args["image_license"])
            if args.has_key('grade') and args["grade"]:
                user.grade = int(args["grade"])
            store.image = image
            store.image_legal = image_legal
            store.image_license = image_license
            store.mobile = user.mobile
            store.tel = user.mobile
            store.created = time.time()
            store.x = 0
            store.y = 0
            store.intro = ''
            store.check_state = 0
            store.save()
            user.store = store
            user.save()
            ru = RefereeUsers.select().where(RefereeUsers.userMobile==user.mobile)
            if ru.count() > 0:
                ru[0].userMobile = user.mobile
                ru[0].store = store.id
                ru[0].save()
            pics = StorePic.select().where((StorePic.store == store) & (StorePic.is_cover == 1) & (StorePic.is_active == 1))
            if image:
                if pics.count() > 0:
                    pics[0].path = image
                    pics[0].save()
                else:
                    pic = StorePic.create(store=store, path=image, check_state=0, is_cover=1, is_active=1)
            result['flag'] = 1
        except Exception, ex:
            logging.info('Error: /mobile/apply_store, %s'%ex.message)
            result['flag'] = 0
            result['msg'] = ex.message
        self.write(simplejson.dumps(result))

    def upload_store_image(self, user_id, img):
        path_dir = 'upload/' + str(user_id / 10000) + '/' + str(user_id)
        filename = '%d%d.%s' % (int(time.time()), random.randint(1000, 9999), 'jpg')
        if not os.path.exists('upload/' + str(user_id / 10000)):
            os.mkdir('upload/' + str(user_id / 10000))
        if not os.path.exists(path_dir):
            os.mkdir(path_dir)
        with open(path_dir + '/' + filename, "wb") as f:
            f.write(decodestring(img))

        return  '/' + path_dir + '/' + filename

# 手机端我的保险订单
@route(r'/mobile/insurance', name='mobile_insurance')
class MobileInsuranceHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'totalpage': 0, 'total': 0, 'items': []}
        userid = int(self.get_argument("userid", 0))
        size = int(self.get_argument('size', 20))
        index = int(self.get_argument('index', 1))
        status = int(self.get_argument("status", '-1'))
        ft = (InsuranceOrder.user == userid) & (InsuranceOrder.userDel == 0)
        ft = ft & (InsuranceOrder.ordertype == 1)
        if status > -1:
            ft = ft & (InsuranceOrder.status == status)
        else:
            ft = ft & (InsuranceOrder.status > -1)

        q = InsuranceOrder.select().where(ft).order_by(InsuranceOrder.ordered.desc())

        if result['total'] % size > 0:
            result['totalpage'] = result['total'] / size + 1
        else:
            result['totalpage'] = result['total'] / size
        now = int(time.time())
        paging_q = q.paginate(index, size)
        for n in paging_q:
            deadlineWarning = ''
            if not n.store:
                continue
            if n.status == 1:   #待确认
                if not n.deadline:
                    n.deadline = now+setting.deadlineTime
                    n.save()
                elif now >= n.deadline:
                    n.status = 5
                    n.cancelreason = u'超时未支付'
                    n.save()
            if n.status == 1 and now < n.deadline:
                deadlineWarning = u'订单将于%s失效'%time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(n.deadline))
            result['total'] += 1
            area = Area.get(code=n.store.area_code)
            if len(n.store.area_code) == 12:
                sArea = u'%s %s %s %s'%(area.pid.pid.name, area.pid.name, area.name, n.store.address)
            elif len(n.store.area_code) == 8:
                sArea = u'%s %s %s' % (area.pid.name, area.name, n.store.address)
            elif len(n.store.area_code) == 4:
                sArea = u'%s %s' % (area.name, n.store.address)
            if n.LubeOrScore == 1:
                commission = u'返佣返油（三个工作日内送达）'
            elif n.LubeOrScore == 2:
                if n.status == 2 and n.paytime > 1483538153:
                    commission = str(n.scoreNum) + u'积分（订单完成后赠送）'
                else:
                    commission = str(n.scoreNum)+u'积分'
            else:
                commission = u'无'
            result['items'].append({
                'id': n.id,
                'ordernum': n.ordernum,
                'price': n.price,
                'detail': n.insurance.name,
                'ordered': n.ordereddate,
                'status':n.status,
                'sName': n.store.name,
                'sArea': sArea,
                'mobile': n.store.mobile,
                'commission': commission,
                'deadline': deadlineWarning
            })

        self.write(simplejson.dumps(result))

@route(r'/mobile/banpen', name='mobile_banpen')  # 手机端我的钣喷订单
class MobileBanPenHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'totalpage': 0, 'total': 0, 'items': []}
        userid = int(self.get_argument("userid", 0))
        size = int(self.get_argument('size', 20))
        index = int(self.get_argument('index', 1))
        status = int(self.get_argument("status", '-1'))
        q = True
        ft = (InsuranceOrder.user == userid)
        ft = ft & (InsuranceOrder.ordertype == 2)
        if status > -1:
            ft = ft & (InsuranceOrder.status == status)
        else:
            ft = ft & (InsuranceOrder.status > -1)

        q = InsuranceOrder.select().where(ft).order_by(InsuranceOrder.ordered.desc())
        result['total'] = q.count()
        if result['total'] % size > 0:
            result['totalpage'] = result['total'] / size + 1
        else:
            result['totalpage'] = result['total'] / size
        paging_q = q.paginate(index, size)
        for n in paging_q:
            result['items'].append({
                'id': n.id,
                'ordernum': n.ordernum,
                'price': n.price,
                'detail': n.insurance.name,
                'ordered': n.ordereddate,
                'status':n.status
            })
        self.write(simplejson.dumps(result))


# 手机端获取价格和保险种类
@route(r'/mobile/getprice', name='mobile_getprice')
class MobileGetPrice(RequestHandler):
    def get(self):
        result = {'company':[], 'thirdDutyIP':[], 'driverDutyIP':[],'passengerDutyIP':[],'scratchIP':[]}
        code = self.get_argument('city_code', '')
        city_name = self.get_argument("city_name", '')
        uid = self.get_argument("uid", 0)
        ugrade = 0
        try:
            ugrade = User.get(id=uid).grade
        except:
            pass
        if code:
            area = Area.get(code=code)
            products = Product.select().join(InsuranceAdmin, on=(InsuranceAdmin.insurance == Product.name)).where(
                (Product.is_index == 1) & (Product.status == 1) & (InsuranceAdmin.area==area)).order_by(InsuranceAdmin.sort)
        elif city_name:
            try:
                area = Area.get(name=city_name)
                products = Product.select().join(InsuranceAdmin, on=(InsuranceAdmin.insurance == Product.name)).where(
                    (Product.is_index == 1) & (Product.status == 1) & (InsuranceAdmin.area == area)).order_by(InsuranceAdmin.sort)
            except:
                products = Product.select().where((Product.is_index == 1) & (Product.status == 1))

        else:
            products = Product.select().where((Product.is_index == 1) & (Product.status == 1))
        tmpList = []
        for p in products:
            tmpdic = {}
            tmpdic['id'] = p.id
            tmpdic['name'] = p.name
            tmpdic['gift'] = 'none'
            if code:
                if CheckScoreArea().checkAreaInsurance(code[:8], p.id) and ugrade==1:
                    tmpdic['isScore'] = 'true'
                    tmpdic['gift'] = 'score'
                else:
                    tmpdic['isScore'] = 'false'
                if CheckScoreArea().checkLube(code[:8]):
                    if tmpdic['gift'] is not 'none':
                        tmpdic['gift'] += 'lube'
                    else:
                        tmpdic['gift'] = 'lube'
            else:
                tmpdic['isScore'] = 'false'

            if p.id not in tmpList:
                result['company'].append(tmpdic)
                tmpList.append(p.id)
        ips = InsurancePrice.select().where(InsurancePrice.pid == 3)
        for ip in ips:
            tmpdic = {}
            tmpdic['id'] = ip.id
            tmpdic['name'] = ip.name
            result['thirdDutyIP'].append(tmpdic)
        ips = InsurancePrice.select().where(InsurancePrice.pid == 5)
        for ip in ips:
            tmpdic = {}
            tmpdic['id'] = ip.id
            tmpdic['name'] = ip.name
            result['driverDutyIP'].append(tmpdic)
        ips = InsurancePrice.select().where(InsurancePrice.pid == 6)
        for ip in ips:
            tmpdic = {}
            tmpdic['id'] = ip.id
            tmpdic['name'] = ip.name
            result['passengerDutyIP'].append(tmpdic)
        ips = InsurancePrice.select().where(InsurancePrice.pid == 8)
        for ip in ips:
            tmpdic = {}
            tmpdic['id'] = ip.id
            tmpdic['name'] = ip.name
            result['scratchIP'].append(tmpdic)
        self.write(simplejson.dumps(result))

# 手机端创建保险订单收货地址
@route(r'/mobile/newinsuranceadd', name='mobile_new_insurance_add')
class MobileNewInsuranceHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {}
        try:
            args = simplejson.loads(self.request.body)
            orderid = args['orderid']  # 订单ID
            contact = args['contact']  # 联系人
            mobile = args['mobile']  # 电话
            address = args['address']  # 省市区
            paddress = args['paddress']  # 详细地址
            InsuranceOrderReceiving.create(orderid=orderid, contact=contact, mobile=mobile, address=address,
                                           paddress=paddress)
            result['flag'] = 1
        except:
            result['flag'] = 0
        self.write(simplejson.dumps(result))

# 手机端创建保险订单
@route(r'/mobile/newinsurance', name='mobile_newinsurance')
class MobileNewInsuranceHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': '', 'data': 0}
        args = simplejson.loads(self.request.body)
        uid = args["userid"]
        pid = int(args['pid'])
        mobile = args["mobile"]
        msg = args["msg"]
        contact = args["contact"]
        idcard = args["idcard"]
        idcardback = args["idcardback"]
        drivercard = args["drivercard"]
        drivercard2 = None
        try:
            drivercard2 = args["drivercard2"]
            order = InsuranceOrder()
            order.forceI = args['forceI']
            order.damageI = args['damageI']
            order.thirdDutyI = args['thirdDutyI']
            order.robbingI = args['robbingI']
            order.driverDutyI = args['driverDutyI']
            order.passengerDutyI = args['passengerDutyI']
            order.glassI = args['glassI']
            order.scratchI = args['scratchI']
            order.normalDamageI = args['normalDamageI']
            order.wadeI = args['wadeI']
            order.specialI = args['specialI']
            order.thirdSpecialI = args['thirdSpecialI']
            order.damageSpecialI = order.specialI
            order.thirdDutySpecialI = args['thirdDutySpecialI']
            order.robbingSpecialI = args['robbingSpecialI']
            order.driverDutySpecialI = args['driverDutySpecialI']
            order.passengerDutySpecialI = args['passengerDutySpecialI']
            order.scratchSpecialI = args['scratchSpecialI']
            order.normalDamageSpecialI = args['normalDamageSpecialI']
            order.wadeSpecialI = args['wadeSpecialI']
            order.thirdSpecialSpecialI = args['thirdSpecialSpecialI']
            order.specialI = 'false'
        except:
            pass

        order.user = uid
        order.contact = contact
        order.store = order.user.store
        order.insurance = pid
        order.mobile = mobile
        order.ordertype = 1
        order.message = msg
        order.ordered = int(time.time())
        order.ordereddate = time.strftime('%Y-%m-%d', time.localtime(order.ordered))  # 下单日期，文本格式
        order.orderedtime = time.strftime('%H:%M:%S', time.localtime(order.ordered))  # 下单时间，文本格式

        if not os.path.exists('upload/insurance'):
            os.mkdir('upload/insurance')
        datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前时间作为图片名称
        if idcard:
            filename = str(datetime) + '_idcard.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(idcard))
            order.idcard = '/upload/insurance/' + filename
        if idcardback:
            filename = str(datetime) + '_idcardback.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(idcardback))
            order.idcardback = '/upload/insurance/' + filename
        if drivercard:
            filename = str(datetime) + '_drivercard.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(drivercard))
            order.drivercard = '/upload/insurance/' + filename
        if drivercard2:
            filename = str(datetime) + '_drivercard2.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(drivercard2))
            order.drivercard2 = '/upload/insurance/' + filename
        order.save()
        order.ordernum = 'U' + str(uid) + 'I' + str(order.id)
        order.save()
        result["flag"] = 1
        result['data'] = order.id
        result['contact'] = contact  # 联系人
        result['mobile'] = mobile  # 联系电话
        area_code = Store.get(id=order.store).area_code
        province = Area.get(code=area_code[:4]).name
        city = Area.get(code=area_code[:8]).name
        if len(area_code) == 12:
            region = Area.get(code=area_code).name
        else:
            region = ''
        result['address'] = province + city + region
        result['paddress'] = Store.get(id=order.store).address

        mobiles = setting.serviceMobiles
        if order.store.area_code.startswith('0004'):
            oscode = '0004%'
        else:
            oscode = order.store.area_code[:8] + '%'
        ft = (User.grade == 5) & (Store.area_code % oscode)
        us = User.select().join(Store).where(ft)
        for u in us:
            if not u.mobile in mobiles:
                mobiles = mobiles + ','  + u.mobile

        # ssas = StoreServerArea.select().join(Store).where(Store.area_code % oscode)
        # for ssa in ssas:
        #     mobiles.append(ssa.sid.mobile)
        # mobiles = set(mobiles)

        sms = {'mobile': mobile, 'body': [order.ordernum, order.insurance.name], 'signtype': '1', 'isyzm': 'placeOrderSys'}
        # 保单下单提醒 '亲，有人下单请去受理呦！订单号：%s 订单信息：%s'
        create_msg(simplejson.dumps(sms), 'sms')
        # content = u'您的订单已有客服美眉受理'
        sms = {'mobile': order.mobile, 'body': '', 'signtype': '1', 'isyzm': 'placeOrderToStore'}
        create_msg(simplejson.dumps(sms), 'sms')
        self.write(simplejson.dumps(result))

# 手机端创建保险订单 新接口
@route(r'/mobile/createnewinsurance', name='mobile_crt_new_insurance')
class MobileCrtNewInsuranceHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': u''}
        uid = self.get_argument('uid', '')
        try:
            user = User.get(id=uid)
            result['contact'] = user.store.link_man  # 联系人
            result['mobile'] = user.store.mobile  # 联系电话
            result['address'] = Area().get_detailed_address(user.store.area_code)
            result['paddress'] = user.store.address
            result["flag"] = 1
        except:
            result['msg'] = u'获取地址失败'
        self.write(simplejson.dumps(result))

    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        uid = args["userid"]
        pid = int(args['pid'])
        msg = args["msg"]
        idcard = args["idcard"]
        idcardback = args["idcardback"]
        drivercard = args["drivercard"]
        drivercard2 = args["drivercard2"]
        contact = args['contact']  # 联系人
        mobile = args['mobile']  # 电话
        address = args['address']  # 省市区
        paddress = args['paddress']  # 详细地址

        order = InsuranceOrder()
        order.user = uid
        order.contact = contact
        order.store = order.user.store
        order.insurance = pid
        order.mobile = mobile
        order.ordertype = 1
        order.message = msg
        order.ordered = int(time.time())
        order.ordereddate = time.strftime('%Y-%m-%d', time.localtime(order.ordered))    #下单日期，文本格式
        order.orderedtime = time.strftime('%H:%M:%S', time.localtime(order.ordered))    #下单时间，文本格式
        order.forceI = args['forceI']
        order.damageI = args['damageI']
        order.thirdDutyI = args['thirdDutyI']
        order.robbingI = args['robbingI']
        order.driverDutyI = args['driverDutyI']
        order.passengerDutyI = args['passengerDutyI']
        order.glassI = args['glassI']
        order.scratchI = args['scratchI']
        order.normalDamageI = args['normalDamageI']
        order.wadeI = args['wadeI']
        order.thirdSpecialI = args['thirdSpecialI']

        order.specialI = 'false'
        order.damageSpecialI = args['specialI']
        order.thirdDutySpecialI = args['thirdDutySpecialI']
        order.robbingSpecialI = args['robbingSpecialI']
        order.driverDutySpecialI = args['driverDutySpecialI']
        order.passengerDutySpecialI = args['passengerDutySpecialI']
        order.scratchSpecialI = args['scratchSpecialI']
        order.normalDamageSpecialI = args['normalDamageSpecialI']
        order.wadeSpecialI = args['wadeSpecialI']
        order.thirdSpecialSpecialI = args['thirdSpecialSpecialI']

        if not os.path.exists('upload/insurance'):
            os.mkdir('upload/insurance')
        datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前时间作为图片名称
        if idcard:
            filename = str(datetime) + '_idcard.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(idcard))
            order.idcard = '/upload/insurance/'+filename
        if idcardback:
            filename = str(datetime) + '_idcardback.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(idcardback))
            order.idcardback = '/upload/insurance/'+filename
        if drivercard:
            filename = str(datetime) + '_drivercard.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(drivercard))
            order.drivercard = '/upload/insurance/'+filename
        if drivercard2:
            filename = str(datetime) + '_drivercard2.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(drivercard2))
            order.drivercard2 = '/upload/insurance/'+filename

        if 'LubeOrScore' in args:
            LubeOrScore = args['LubeOrScore']
            if LubeOrScore and LubeOrScore != '0':
                order.LubeOrScore = LubeOrScore
        order.save()
        oid = order.id
        order.ordernum = 'U' + str(uid) + 'I' + str(oid)
        order.save()

        InsuranceOrderReceiving.create(orderid=oid, contact=contact, mobile=mobile, address=address, paddress=paddress)

        mobiles = setting.serviceMobiles
        if order.store.area_code.startswith('0004'):
            oscode = '0004%'
        else:
            oscode = order.store.area_code[:8] + '%'
        ft = (User.grade == 5) & (Store.area_code % oscode)
        us = User.select().join(Store).where(ft)
        for u in us:
            if not u.mobile in mobiles:
                mobiles = mobiles + ',' + u.mobile

        # ssas = StoreServerArea.select().join(Store, on=(Store.id==StoreServerArea.sid)).\
        #         join(User, on=(User.store==Store.id)).where(Store.area_code % oscode)
        # for ssa in ssas:
        #     mobiles.append(ssa.sid.mobile)
        # # 保险公司 未加
        # mobiles = set(mobiles)

        # 给保险订单管理人发短信 '亲，有人下单请去受理呦！订单号：%s 订单信息：%s'
        sms = {'mobile': mobiles, 'body': [order.ordernum, order.insurance.name], 'signtype': '1', 'isyzm': 'placeOrderSys'}
        create_msg(simplejson.dumps(sms), 'sms')
        # 给客户发短信 content = u'您的订单已有客服美眉受理'
        sms = {'mobile': order.mobile, 'body': '', 'signtype': '1', 'isyzm': 'placeOrderToStore'}
        create_msg(simplejson.dumps(sms), 'sms')

        result["flag"] = 1
        self.write(simplejson.dumps(result))

# 保险、钣喷订单详情
@route(r'/mobile/insurance/(\d+)', name='mobile_insurance_detail')
class MobileInsuranceOrderDetailHandler(RequestHandler):
    def get(self, oid):
        result = {'flag': 0, 'msg': '', 'data': None}
        iList={'subjoin': [], 'main': [], 'force':'false'}
        o = InsuranceOrder.get(id=oid)
        sArea = ''
        sName = ''
        if o.store:
            sName = o.store.name
            if len(o.store.area_code)==12:
                sArea = '%s %s %s'%(Area.get(code=o.store.area_code[:4]).name, Area.get(code=o.store.area_code[:8]).name ,Area.get(code=o.store.area_code).name)
            elif len(o.store.area_code)==8:
                sArea = '%s %s'%(Area.get(code=o.store.area_code[:4]).name, Area.get(code=o.store.area_code).name)
            elif len(o.store.area_code)==4:
                sArea = Area.get(code=o.store.area_code).name
        insurances = Insurances.select().order_by(Insurances.sort)
        for i in insurances:
            iValue = getattr(o, i.eName)
            if i.style == u'交强险':
                iList['force'] = iValue if iValue else ''
            elif i.style == u'商业险-主险' and iValue != 'false' and iValue:
                iList['main'].append({'eName':i.eName, 'name':i.name, 'style':i.style, 'value':iValue})
            elif i.style == u'商业险-附加险' and iValue != 'false' and iValue:
                iList['subjoin'].append({'eName':i.eName, 'name':i.name, 'style':i.style, 'value':iValue})
        if o.LubeOrScore == 1:
            commission = u'返佣返油（三个工作日内送达）'
        elif o.LubeOrScore == 2:
            commission = str(o.scoreNum)+u'积分'
        else:
            commission = u'无'
        result["flag"] = 1
        now = int(time.time())
        deadlineWarning = ''
        if o.status == 1:  # 待确认
            if not o.deadline:
                o.deadline = now + setting.deadlineTime
                o.save()
            elif now >= o.deadline:
                o.status = 5
                o.cancelreason = u'超时未支付'
                o.save()
        if o.status == 1 and now < o.deadline:
            deadlineWarning = u'订单将于%s失效'%time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(o.deadline))
        result['data'] = {
                'id': o.id,
                'status': o.status,
                'sName': sName,
                'sArea': sArea,
                'insurance': o.insurance.name,
                'mobile': o.mobile,
                'ordernum': o.ordernum,
                'ordereddate': o.ordereddate,
                'orderedtime': o.orderedtime,
                'idcard': o.idcard,
                'idcardback': o.idcardback,
                'drivercard': o.drivercard,
                'drivercard2': o.drivercard2,
                'imgs': [],
                'iList': iList,
                'commission': commission,
                'deadline': deadlineWarning
            }
        for img in o.imgs:
            result['data']['imgs'].append({'id':img.id, 'name':img.name, 'imgtype':img.imgtype})
        self.write(simplejson.dumps(result))

@route(r'/mobile/newbanpen', name='mobile_newbanpen')  # 手机端创建钣喷订单
class MobileNewBanPenHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': '','data':0}
        args = simplejson.loads(self.request.body)
        uid = args["userid"]
        pid = int(args['pid'])
        mobile = args["mobile"]
        msg = args["msg"]
        contact = args["contact"]
        idcard = args["idcard"]
        drivercard = args["drivercard"]
        imgtype = int(args['imgtype'])
        imgs = args['imgs']

        order = InsuranceOrder()
        order.user = uid
        order.contact = contact
        order.store = order.user.store
        order.insurance = pid
        order.mobile = mobile
        order.ordertype = 2
        order.message = msg
        order.ordered = int(time.time())
        order.ordereddate = time.strftime('%Y-%m-%d', time.localtime(order.ordered))    #下单日期，文本格式
        order.orderedtime = time.strftime('%H:%M:%S', time.localtime(order.ordered))    #下单时间，文本格式
        if not os.path.exists('upload/insurance'):
            os.mkdir('upload/insurance')
        if idcard:
            datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前时间作为图片名称
            filename = str(datetime) + '_idcard.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(idcard))
            order.idcard = '/upload/insurance/'+filename
        if drivercard:
            datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前时间作为图片名称
            filename = str(datetime) + '_drivercard.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(drivercard))
            order.drivercard = '/upload/insurance/'+filename

        order.save()
        order.ordernum = 'U' + str(uid) + 'B' + str(order.id)
        order.save()

        if not os.path.exists('upload/insurance'):
            os.mkdir('upload/insurance')
        for i in range(len(imgs)):
            datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前时间作为图片名称
            filename = str(datetime) + '_' + str(i)+ str(random.random()) + ".jpg"
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(imgs[i]))
            InsuranceOrderImg.create(name='/upload/insurance/'+filename,order=order.id,imgtype=imgtype)

        result["flag"] = 1
        result['data'] = order.id
        self.write(simplejson.dumps(result))

@route(r'/mobile/banpenidcard', name='mobile_banpen_idcard')  # 手机端上传钣喷订单的身份证和驾驶证
class MobileBanPenIDCardHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': '','data':0}
        args = simplejson.loads(self.request.body)
        oid = int(args['oid'])
        idcard = args["idcard"]
        idcardback = args["idcardback"]
        drivercard = args["drivercard"]
        drivercard2 = None
        try:
            drivercard2 = args["drivercard2"]
        except:
            pass
        order = InsuranceOrder.get(id=oid)

        if not os.path.exists('upload/insurance'):
            os.mkdir('upload/insurance')
        datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前时间作为图片名称
        if idcard:
            filename = str(datetime) + '_idcard.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(idcard))
            order.idcard = '/upload/insurance/'+filename
        if idcardback:
            filename = str(datetime) + '_idcardback.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(idcardback))
            order.idcardback = '/upload/insurance/'+filename
        if drivercard:
            filename = str(datetime) + '_drivercard.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(drivercard))
            order.drivercard = '/upload/insurance/'+filename
        if drivercard2:
            filename = str(datetime) + '_drivercard2.jpg'
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(drivercard2))
            order.drivercard2 = '/upload/insurance/'+filename
        order.save()

        result["flag"] = 1
        result['data'] = order.id
        self.write(simplejson.dumps(result))

@route(r'/mobile/newbanpenimg', name='mobile_newbanpenimg')  # 手机端为钣喷订单上传图片
class MobileNewBanPenImgHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(self.request.body)
        oid = int(args['oid'])
        imgtype = int(args['imgtype'])
        imgs = args['imgs']
        InsuranceOrderImg.delete().where((InsuranceOrderImg.order == oid) & (InsuranceOrderImg.imgtype == imgtype)).execute()
        if not os.path.exists('upload/insurance'):
            os.mkdir('upload/insurance')
        for i in range(len(imgs)):
            datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前时间作为图片名称
            filename = str(datetime) + '_' + str(i)+ str(random.random()) + ".jpg"
            with open('upload/insurance/' + filename, "wb") as f:
                f.write(decodestring(imgs[i]))
            InsuranceOrderImg.create(name='/upload/insurance/'+filename,order=oid,imgtype=imgtype)
            '''
            img = InsuranceOrderImg()
            img.name = '/upload/insurance/'+filename
            img.order = oid
            img.imgtype = imgtype
            img.save()
           '''
        result["flag"] = 1
        self.write(simplejson.dumps(result))

@route(r'/mobile/payinsurance', name='mobile_payinsurance')  # 手机端支付保险、钣喷订单
class MobilePayInsuranceHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        paymentValue = self.get_argument('paymentValue', '1')
        oid = int(self.get_argument("oid", 0))
        result = {'flag': 0, 'msg': '', 'url': ''}
        order = InsuranceOrder.get(id=oid)
        if paymentValue == "1":  #支付宝支付
            result["flag"] = 1
            result["url"] = get_pay_url(order.ordernum.encode('utf-8'), u'车装甲商品',order.price)
        elif paymentValue == "6":  #微信支付
            result = UnifiedOrder_pub().getPrepayId(order.ordernum.encode('utf-8'), u'商品价格', int(order.price*100))
            result['flag'] = 3
        elif paymentValue == '7':  # 银联支付
            tn = Trade().trade(order.ordernum.replace('-', ''), order.price)
            result = {}
            if tn:
                result['tn'] = tn
                result['flag'] = 4
            else:
                result['flag'] = 0
        self.write(simplejson.dumps(result))

@route(r'/mobileb/home', name='mobileb_home2')  # 手机b端首页
class MobileBHomeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        city_name = self.get_argument("city_name", None)
        city_code = self.get_argument("city_code", None)
        city = None
        if city_code:
            ccode = city_code[:8] + '%'
            qArea= Area.select().where((Area.code % ccode)&(Area.is_delete == 0))
            if qArea.count() > 0:
                city = qArea[0]
        elif city_name:
            qArea= Area.select().where((Area.name == city_name)&(Area.is_delete == 0))
            if qArea.count() > 0:
                city = qArea[0]
        result = {'banner': [], 'bx': [], 'bp': [], 'cate': [], 'city':{}}
        fn_ad = (Ad.flag == 1)
        if city:
            fn_for_insurance = (InsuranceAdmin.area == city)
            fn_ad = fn_ad & ((Ad.city == city.id) | (Ad.city >> None))
            result['city'] = {
                'id' : city.id,
                'name' : city.name,
                'code' : city.code,
                'image' : city.image
            }
        else:
            city = Area.get(code='00270001')
            fn_for_insurance = fn_ad & (InsuranceAdmin.area == city)
            fn_ad = fn_ad & (Ad.city >> None)
        list = Ad.select().where((Ad.atype == 11) & fn_ad).order_by(Ad.sort.desc(), Ad.city.desc())
        for n in list:
            result['banner'].append({
                'pid': n.url,
                'name': n.imgalt,
                'pic': n.picurl
            })
        #保险
        list = Ad.select().join(InsuranceAdmin).where((Ad.atype == 12) & (InsuranceAdmin.area == city)).order_by(InsuranceAdmin.sort)
        if list.count() > 0:
            for n in list:
                result['bx'].append({
                    'pid': n.url,
                    'name': n.imgalt,
                    'pic': n.picurl,
                    'category': 2
                })
        list = Ad.select().where((Ad.atype == 13) & fn_ad).order_by(Ad.city.desc(), Ad.sort.desc())
        for n in list:
             result['bp'].append({
                'pid': n.url,
                'name': n.imgalt,
                'pic': n.picurl,
                'category': 3
            })

        list = Ad.select().where((Ad.atype == 14) & fn_ad).order_by(Ad.city.desc(), Ad.sort.desc())
        item = {'name':u'润滑油', 'items':[], 'category': 0}
        for n in list:
            item['items'].append({
                'pinpaiid': n.url,
                'name': n.imgalt,
                'pic': n.picurl
            })
        result['cate'].append(item)

        list = Ad.select().where((Ad.atype == 15) & fn_ad).order_by(Ad.city.desc(), Ad.sort.desc())
        item = {'name':u'大屏幕导航仪', 'items':[], 'category': 1}
        for n in list:
            item['items'].append({
                'pinpaiid': n.url,
                'name': n.imgalt,
                'pic': n.picurl
            })
        result['cate'].append(item)

        list = Ad.select().where((Ad.atype == 16)&(Ad.flag == 1) ).order_by(Ad.city.desc(), Ad.sort.desc())
        item = {'name':u'记录仪', 'items':[], 'category': 1}

        for n in list:
            item['items'].append({
                'pinpaiid': n.url,
                'name': n.imgalt,
                'pic': n.picurl
            })
        result['cate'].append(item)

        list = Ad.select().where((Ad.atype == 17) & fn_ad).order_by(Ad.city.desc(), Ad.sort.desc())
        item = {'name':u'电动尾门', 'items':[], 'category': 4}
        for n in list:
            item['items'].append({
                'pinpaiid': n.url,
                'name': n.imgalt,
                'pic': n.picurl
            })
        result['cate'].append(item)
        self.write(simplejson.dumps(result))

@route(r'/mobileb/tj', name='mobileb_home')  # 手机b端推荐内容
class MobileBHomeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        code = self.get_argument('city_code', '')
        city_name = self.get_argument("city_name", '')
        area=None
        if code:
            area = Area.get(code=code)
        elif city_name:
            area = Area.get(name=city_name)

        result = {'tj': []}
        list = Ad.select().where((Ad.atype == 18)&(Ad.flag == 1)).order_by(Ad.sort)
        for n in list:
            if 'bx' in n.url and area:
                tmpList = []
                insurances = InsuranceAdmin.select().where(InsuranceAdmin.area==area).order_by(InsuranceAdmin.sort)
                if insurances.count()>0:
                    for iss in insurances:
                        if (iss.insurance == n.imgalt) and (n.url not in tmpList):
                            result['tj'].append({
                                'pid': n.url,
                                'name': n.imgalt,
                                'pic': n.picurl
                            })
                            tmpList.append(n.url)
            else:
                try:
                    pid = int(n.url)
                    ft = (ProductStandard.product==pid) & (ProductStandard.area_code == code) & \
                         (ProductStandard.sale_status==1) & (ProductStandard.is_sale==1)
                    ps = ProductStandard.select().where(ft)
                    if ps.count() > 0:
                        result['tj'].append({
                            'pid': 'sp%s'%ps[0].id,
                            'name': n.imgalt,
                            'pic': n.picurl
                        })
                except Exception, e:
                    logging.info('Error: /mobileb/tj, %s'%e.message)
        self.write(simplejson.dumps(result))

@route(r'/mobileb/products', name='mobileb_products')  # 手机b端分类产品列表
class MobileBPHomeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        pinpai = int(self.get_argument("pinpai", 0))  # 品牌id
        result = []
        index = int(self.get_argument("index", 1))

        ft = ((ProductStandard.sale_status == 1) & (Product.pinpai == pinpai))
        q = ProductStandard.select(ProductStandard, Product).\
            join(Product, on=(Product.id == ProductStandard.product)). \
            join(CategoryFront, on=(Product.categoryfront == CategoryFront.id)). \
            join(Store, on=(Store.id == ProductStandard.store)).where(ft)
        paging_q = q.paginate(index, 10)
        for n in paging_q:
            result.append({
                'psid': n.id,
                'pid': n.product.id,
                'name': n.product.name,
                'price': n.price,
                'originalPrice': n.orginalprice,
                'unit': n.unit if n.unit else u'件',
                'sku': n.product.sku,
                'cover': PassMobileImg(n.product.cover),
                'standard': n.name,
                'resume': n.product.resume,
                'storeName': n.store.name
            })
        self.write(simplejson.dumps(result))

@route(r'/mobileb/category', name='mobileb_category')  # 手机b端分类列表
class MobileBHomeHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = []
        categories1 = CategoryFront.select().where((CategoryFront.isactive == 1) & (db.fn.Length(CategoryFront.code) == 4))
        categories2 = CategoryFront.select().where((CategoryFront.isactive == 1) & (db.fn.Length(CategoryFront.code) == 8))
        categories3 = CategoryFront.select().where((CategoryFront.isactive == 1) & (db.fn.Length(CategoryFront.code) == 12))
        code = self.get_argument('city_code','')
        for n in categories1:
            cat1 = {'cid':n.id, 'name':n.name, 'code': n.code, 'subs':[]}
            for c in categories2:
                if (c.code[0:4] == n.code):
                    cat2 = {'cid':c.id, 'name':c.name, 'code': c.code, 'subs':[]}
                    cat1['subs'].append(cat2)
                    if cat2['code'] == '00030001' and code:
                        area = Area.get(code=code)
                        ft = (CategoryFront.isactive==1) & (db.fn.Length(CategoryFront.code)==12) & (InsuranceAdmin.area==area)
                        categories_i3 = CategoryFront.select().join(InsuranceAdmin).where(ft).order_by(InsuranceAdmin.sort)
                        for cc in categories_i3:
                            if (cc.code[0:8] == c.code):
                                cat2['subs'].append({'cid':cc.id,'name':cc.name, 'code':  cc.code,'img':cc.img_m })
                    else:
                        for cc in categories3:
                            if (cc.code[0:8] == c.code):
                                cat2['subs'].append({'cid':cc.id,'name':cc.name, 'code':  cc.code,'img':cc.img_m })
            result.append(cat1)
        self.write(simplejson.dumps(result))

@route(r'/mobile/user/(\d+)', name='mobile_user_detail')  # 用户详情
class MobileUserDetailHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, uid):
        result = {'flag': 0, 'msg': '', 'data': None}
        user = User.get(id=uid)
        result["flag"] = 1
        result['data'] = {
            'birthday':'',
            'username': user.username,
            'nickname': user.nickname,
            'mobile': user.mobile,
            'score': user.score,
            'level': user.level,
            'cashed_money': user.cashed_money,
            'balance': user.balance,
            'id': user.id,
            'portraiturl': user.portraiturl,
            'bindmobile': user.bindmobile(),
            'hascheckedin': user.hascheckedin(),
            'isactive': user.isactive,# 用户组 0被禁止的用户 1正常用户
            'grade': user.grade,# 0普通C端用户，1门店B端用户，2厂商A端用户，3代理商用户
            'store': None}
        if user.store:
            store = user.store
            result['data']['store'] = {
                'id':store.id,
                'name':store.name,
                'province_code':store.area_code[0:4],
                'city_code':store.area_code[0:8],
                'area_code':store.area_code,
                'address':store.address,
                'link_man':store.link_man,
                'tel':store.tel,
                'image':store.image,
                'image_legal':store.image_legal,
                'image_license':store.image_license,
                'check_state':store.check_state,
                'business_type': store.business_type
                }
        self.write(simplejson.dumps(result))


@route(r'/mobile/helpCenter', name='mobile_help_center')  # 手机b端分类列表
class MobileHelpCenter(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get_insurances(self, rows, result):
        tmpList = []
        for row in rows:
            result['data']['iCompany'] = row.iCompany
            if '+' in row.insurance:
                forceI, comI = row.insurance.split('+')
                insurance = '%s+(%s)%s' % (forceI, row.price, comI)
            elif u'单商业险' == row.insurance:
                insurance = '%s(%s)' % (row.insurance, row.price)
            else:
                insurance = row.insurance
            if row.driverGift not in tmpList:
                tmpList.append(row.driverGift)
                tmpDict = {'gift': '', 'insurances': []}
                if row.driverGift == row.party2Gift:
                    tmpDict['gift'] = row.driverGift
                else:
                    tmpDict['gift'] = row.driverGift+u'（修理厂:'+row.party2Gift+'）'
                tmpDict['insurances'].append([insurance, row.driverGiftNum, row.party2GiftNum])
                result['data']['type'].append(tmpDict)
            else:
                for i, tmpDict in enumerate(result['data']['type']):
                    if row.driverGift == row.party2Gift:
                        tmpGift = row.driverGift
                    else:
                        tmpGift = row.driverGift + u'（修理厂:' + row.party2Gift + '）'
                    if tmpGift == tmpDict['gift']:
                        result['data']['type'][i]['insurances'].append(
                            [insurance, row.driverGiftNum, row.party2GiftNum])
        return result

    def get_insurances_for_difI(self, rows, result, iCompanyName):
        tmpList = []
        result['data']['iCompany'] = iCompanyName
        for row in rows:
            if '+' in row.insurance:
                forceI, comI = row.insurance.split('+')
                insurance = '%s+(%s)%s' % (forceI, row.price, comI)
            elif u'单商业险' == row.insurance:
                insurance = '%s(%s)' % (row.insurance, row.price)
            else:
                insurance = row.insurance

            driverGiftName = u'%s（%s）'%(row.driverGift, row.iCompany)
            facilitatorGiftName = u'%s（%s）'%(row.party2Gift, row.iCompany)
            if driverGiftName not in tmpList:
                tmpList.append(driverGiftName)
                tmpDict = {'gift': '', 'insurances': []}
                if driverGiftName == facilitatorGiftName:
                    tmpDict['gift'] = driverGiftName
                else:
                    tmpDict['gift'] = u'%s（修理厂:%s）（%s）'%(row.driverGift, row.party2Gift, row.iCompany)
                tmpDict['insurances'].append([insurance, row.driverGiftNum, row.party2GiftNum])
                result['data']['type'].append(tmpDict)
            else:
                for i, tmpDict in enumerate(result['data']['type']):
                    if driverGiftName == facilitatorGiftName:
                        tmpGift = driverGiftName
                    else:
                        tmpGift = u'%s（修理厂:%s）（%s）'%(row.driverGift, row.party2Gift, row.iCompany)
                    if tmpGift == tmpDict['gift']:
                        result['data']['type'][i]['insurances'].append(
                            [insurance, row.driverGiftNum, row.party2GiftNum])
        return result

    def get(self):
        result = {'flag': 0, 'msg': '', 'data': {
            'iCompany': '',
            'presentToA':setting.presentToA,
            'remark': '',
            'presentToB':setting.presentToB,
            'type':[]}}
        cityCode = self.get_argument('city_code', '')
        if len(cityCode) == 8:
            if cityCode == '00160016':
                result['data']['remark'] = setting.remark_ZhouKou
            rows = HelpCenter.select().where(HelpCenter.area_code==cityCode).order_by(HelpCenter.sort, HelpCenter.sort2)
            if not rows.count()>0:
                rows = HelpCenter.select().where(HelpCenter.area_code == cityCode[:4]).order_by(HelpCenter.sort, HelpCenter.sort2)
            if rows.count()>0:
                iCompanyName = ''
                totalICname = []
                for row in rows:
                    if row.iCompany not in totalICname:
                        totalICname.append(row.iCompany)
                        iCompanyName += row.iCompany
                if len(totalICname) > 1:
                    result = self.get_insurances_for_difI(rows, result, iCompanyName)
                else:
                    result = self.get_insurances(rows, result)
                result['flag']=1
            else:
                result['msg'] = u'该地区的具体优惠政策请联系车装甲客服'
        else:
            result['msg'] =  u'未获取到城市'

        self.write(simplejson.dumps(result))

# 获取用户积分
@route(r'/mobile/score/(\d+)', name='mobile_user_score')
class MobileUserScore(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, uid):
        result = {'flag': 0, 'msg': '', 'data': None}
        try:
            user = User.get(id=uid)
            result["flag"] = 1
            result['data'] = {'score': user.score}
        except Exception, e:
            logging.info('Error: /mobile/score/%s, %s'%(uid, e.message))
            result['msg'] = u'未查询到该用户'
        self.write(simplejson.dumps(result))


# 积分商城
@route(r'/mobile/scoreStoreShow', name='mobile_score_store_show')
class MobileScoreScoreShow(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', 'userScore':0, 'data': None}
        uid = int(self.get_argument("uid", 0))
        city_code = self.get_argument('city_code', '')
        index = int(self.get_argument("index", 1))

        try:
            if not CheckScoreArea().checkArea(city_code[:8]):
                result['flag'] = -1
            elif not Area.get(code=city_code).is_scorearea:
                result['msg'] = u'该地区积分商城即将上市，敬请期待！'
            else:
                u = User.get(id=uid)
                result['userScore'] = u.score
                code = city_code[:8]+'%'
                ft = (ProductStandard.area_code % code) & (ProductStandard.is_score==1) & \
                     (ProductStandard.sale_status == 1) & (Product.status==1)
                pss = ProductStandard.select().join(Product).where(ft).order_by(ProductStandard.update_time.desc())
                tmpResult = []
                paging_q = pss.paginate(index, 10)
                for n in paging_q:
                    tmpResult.append({
                        'psid': n.id,
                        'pid': n.product.id,
                        'name': n.product.name+' '+n.copies,
                        'price': n.price,
                        'originalPrice': n.orginalprice,
                        'ourprice': n.pf_price,  # 门店价修改成批发价
                        'pf_price': n.pf_price,
                        'copies': n.copies,
                        'unit': n.unit if n.unit else u'件',
                        'sku': n.product.sku,
                        'cover': PassMobileImg(n.product.cover),
                        'standard': n.name,
                        'resume': n.product.resume,
                        'storeid':n.store.id,
                        'storeName': n.store.name,
                        'sales': n.orders,
                        'scoreNum': n.scoreNum, #商品的积分
                        'quantity': n.quantity
                    })
                result['flag'] = 1
                result['data'] = tmpResult
        except Exception, e:
            logging.info('Error: /mobile/scoreStoreShow: %s'%str(e))
            result['msg'] = u'获取地区失败'
        self.write(simplejson.dumps(result))


# 手机端用积分支付 积分兑商品
@route(r'/mobile/scoreStorePay', name='mobile_score_Store_pay')
class MobileScorePay(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    # 查出该商品今天该用户购买过几次
    # 查出该商品库存多少
    def checkLeftProductS(self, items):
        jrmsg = u''
        result = True
        if len(items) > 0:
            ps = ProductStandard.get(id=items[0]['psid'])
            if items[0]['quantity'] > ps.quantity:
                jrmsg = u'该商品已售罄'
                result = False
        else:
            result = False
            jrmsg = u'没有选中商品'
        return (result, jrmsg)

    executor = ThreadPoolExecutor(80)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    @require_basic_authentication
    def post(self):
        yield self.execPay(self)

    @run_on_executor
    def execPay(self, handler):
        result = {'flag': 0, 'msg': ''}
        args = simplejson.loads(handler.request.body)
        addrid = args["addrid"]
        userid = args["userid"]
        payment = args['payment']
        version = args['version']
        if 'id' in args:
            order = Order.get(id=args['id'])
            result['orderid'] = order.id

            items = []
            items.append({
                'psid': order.items[0].product_standard.id,
                'quantity': order.items[0].quantity
            })
            LeftProductS, result['msg'] = self.checkLeftProductS(items)
            if LeftProductS:
                # 积分支付
                if str(payment) == '8':  # 积分支付
                    user = User.get(id=order.user)
                    if user.score >= order.scoreNum:
                        user.score -= order.scoreNum
                        order.status = 1
                        result['flag'] = 4  # 积分支付
                        result['payment'] = u'积分支付'
                        result['spendScore'] = order.scoreNum
                        result['surplusScore'] = user.score
                        user.save()
                    else:
                        result['msg'] = u'积分余额不足'
            else:
                result['msg'] = u'库存不足'
        else:
            items = args.get('items', [])  # 订单内容
            LeftProductS, result['msg'] = self.checkLeftProductS(items)
            u = User.get(id=userid)
            ps = ProductStandard.get(id=items[0]['psid'])
            if LeftProductS and u.score >= items[0]['quantity']*ps.scoreNum:
                address = UserAddr.get(id=addrid)
                itemList = []
                #创建新 orderItem
                orderItem = OrderItem()
                orderItem.product = ps.product.id
                orderItem.product_standard = ps
                orderItem.price = ps.pf_price
                orderItem.weight = ps.weight
                orderItem.quantity = items[0]['quantity']
                orderItem.product_standard_name = ps.name
                orderItem.item_type = 0
                orderItem.hascomment = ps.weights  # 存储权重，用于排序
                itemList.append(orderItem)
                o = orderItem.product_standard.store
                #is_store = orderItem.product_standard.store
                #storeList.append(is_store)

                if len(itemList) == 0:
                    result['msg'] = '订单中至少需要选择一件商品'
                else:
                    with db.handle.transaction():
                        #创建订单
                        order = Order()
                        order.user = userid
                        order.address = addrid
                        order.take_name = address.name
                        order.take_tel = address.mobile + ' ' + address.tel
                        order.take_address = address.province + ' ' + address.city + ' ' + address.region + ' ' + address.address

                        order.ordered = int(time.time())
                        order.ordereddate = time.strftime('%Y-%m-%d', time.localtime(order.ordered))
                        order.orderedtime = time.strftime('%H:%M:%S', time.localtime(order.ordered))
                        order.payment = payment
                        order.is_score = 1
                        order.scoreNum = int(items[0]['scoreNum']) * int(items[0]['quantity'])
                        #订单价格与实际卖价
                        store_price = orderItem.price * orderItem.quantity
                        order.price = store_price
                        order.currentprice = store_price

                        order.status = 0 #订单状态
                        order.ip = self.request.remote_ip #订单 买家IP
                        order.order_from = 2  # 手机下单
                        order.store = o    #卖家store
                        order.save()

                        order.ordernum = 'U' + str(order.user.id) + 'S' + str(order.id)
                        storeProductNum = order.ordernum #卖家订单号
                        storeProductNames = ''           #卖家卖的所有商品
                        if orderItem.product_standard.store == o:
                            orderItem.hascomment = 0  # 存储权重，完成，初始化回去
                            orderItem.order = order.id
                            storeProductNames = orderItem.product.name
                            orderItem.save()
                            orderItem.product_standard.orders += 1
                            orderItem.product_standard.save()  # 产品购买次数累计

                        #给卖家发短信
                        sms = {'mobile': o.mobile, 'body': u'订单号：%s 所购商品：%s'%(storeProductNum ,storeProductNames),
                               'signtype': '1', 'isyzm': 'placeOrderToServer'}  # 有客户下单请查看
                        #create_msg(simplejson.dumps(sms), 'sms')  # 下单

                        #积分支付
                        if str(payment) == '8':  # 积分支付
                            if order.user.score >= order.scoreNum:
                                order.user.score = order.user.score - order.scoreNum
                                order.status = 1
                                #创建score 历史记录
                                log = u'积分兑商品'
                                createdTime = int(time.time())
                                Score.create(user=order.user.id, stype=1, score=order.scoreNum, log=log, created=createdTime,
                                     isactive=1, jftype=1, remark='', orderNum=order.ordernum)
                                #返回值
                                result['flag'] = 4#积分支付
                                result['payment'] = u'积分支付'
                                result['spendScore'] = order.scoreNum
                                result['surplusScore'] = order.user.score
                            else:
                                result['msg'] = u'积分余额不足'
                        order.save()
                        result['orderid'] = order.id
            else:
                if not result['msg']:
                    result['msg'] = u'积分余额不足'
        handler.write(simplejson.dumps(result))
        return result


# 积分消费记录接口
@route(r'/mobile/scoreStoreRecord', name='mobile_score_store_Record')
class MobileScoreScoreShow(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', 'data': []}
        uid = int(self.get_argument('uid', '0'))
        index = int(self.get_argument("index", 1))

        try:
            ss = Score.select().where((Score.user==uid) & (Score.isactive==1))
            scores = ss.paginate(index, 10)

            for uss in scores:
                result['data'].append({
                'stype': uss.stype,
                'score': uss.score,
                'created': time.strftime('%Y-%m-%d', time.localtime(uss.created)),
                'jftype': uss.jftype,
                'orderNum': uss.orderNum
                })
            result['flag'] = 1
            logging.info(str(result))
        except Exception, e:
            logging.info('Error: /mobile/scoreStoreShow: %s'%str(e))
            result['msg'] = u'用户获取失败'
        self.write(simplejson.dumps(result))


# 用户积分兑现
@route(r'/mobile/scoreConvertibility/(\d+)', name='mobile_user_score_Convertibility')
class MobileUserScoreConvertibility(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, uid):
        result = {'flag': 0, 'msg': '', 'data': {}}
        try:
            user = User.get(id=uid)
            result['data']['score'] = user.score
            city_code = user.store.area_code[:8]
            cel = ''
            cels = CurrencyExchangeList.select().where((CurrencyExchangeList.area_code == city_code) & (CurrencyExchangeList.is_cash==1) & (CurrencyExchangeList.iswork==1))
            if cels.count() > 0:
                cel = cels[0]
            else:
                city_code = city_code[:4]
                cels = CurrencyExchangeList.select().where((CurrencyExchangeList.area_code == city_code) & (CurrencyExchangeList.is_cash==1) & (CurrencyExchangeList.iswork==1))
                if cels.count() > 0:
                    cel = cels[0]
            if cel:
                result['data']['rate'] = cel.aliRate   #各地区rate不一样
                result['data']['baseMoney'] = cel.baseMoney     #起兑金额
                result["flag"] = 1
            else:
                result['msg'] = u'该地区未配置'
        except Exception, e:
            logging.info('Error: %s'%e.message)
            result['msg'] = u'系统错误'
        self.write(simplejson.dumps(result))

    def post(self, uid):
        result = {'flag': 0, 'msg': '', 'data':{}}
        args = simplejson.loads(self.request.body)
        score = int(args['score'])
        price = round(float(args['price']), 2)
        rate = float(args['rate'])
        baseMoney = float(args['baseMoney'])

        cashScore = round(price/(1-rate), 0)
        if price * rate >= 25:
            cashScore = round(price+25, 0)

        try:
            user = User.get(id=uid)
            uScore = user.score
            if (cashScore==score) and (uScore>=score) and (price>=baseMoney):
                log = u'积分兑现'
                created = int(time.time())
                s = Score.create(user=user.id, stype=1, score=score, log=log, created=created,
                                 isactive=1, jftype=2, remark=str(price))
                s.orderNum = 'U%sC%s' % (user.id, s.id)
                s.save()
                user.score -= score
                user.cashed_money += price  # 可提现金额
                user.save()
                result['data']['surplusScore'] = score
                result['data']['cashedMoney'] = price
                result['flag'] = 1
                result['msg'] = u'兑现成功'
            else:
                result['msg'] = u'注意剩余积分或最低提现金额'
        except:
            result['msg'] = u'用户不存在'
        self.write(simplejson.dumps(result))


# 获取用户积分订单
@route(r'/mobile/scoreOrders/(\d+)', name='mobile_user_score_orders')
class MobileUserScoreOrders(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self, uid):
        result = {'flag': 0, 'msg': '', 'data': []}
        try:
            index = int(self.get_argument("index", 1))
            status = self.get_argument("status", '')
            ft = ((Order.user==uid) & (Order.is_score==1))
            if status:
                status = int(status)
                ft &= (Order.status==status)
            Sorders = Order.select().where(ft).order_by(Order.ordered.desc())
            sos = Sorders.paginate(index, 10)
            for so in sos:
                result['data'].append({
                    'id': so.id,
                    'ordernum': so.ordernum,
                    'cover':so.items[0].product.cover,
                    'quantity':so.items[0].quantity,
                    'scoreNum': so.scoreNum,
                    'detail': so.items[0].product.name,
                    'ordered': so.ordereddate,
                    'status':so.status
                })
            result["flag"] = 1
        except Exception, e:
            logging.info('Error: %s'%str(e))
            result['msg'] = u'未查询到该用户'
        self.write(simplejson.dumps(result))

    def post(self, oid):
        result = {'flag': 0, 'msg': '', 'data': None}
        try:
            order = Order.get(id = oid)
            order.status = 5
            order.save()
            result["flag"] = 1
        except Exception, e:
            logging.info('Error: %s' % str(e))
            result['msg'] = u'未查询到该订单'
        self.write(simplejson.dumps(result))


@route(r'/mobile/closeorders/(\d+)', name='close_orders')
class MobileCloseOrders(RequestHandler):
    def get(self, uid):
        result = {'flag': 0, 'msg': ''}
        ordernum = self.get_argument('ordernum', '')
        try:
            if ('U'+uid+'I' in ordernum) or ('U'+uid+'B' in ordernum) or ('U'+uid+'-I' in ordernum) or ('U'+uid+'-B' in ordernum):
                io = InsuranceOrder.get(ordernum=ordernum)
                if io.status < 2:
                    io.status = -1
                    io.save()
                elif io.status > 3:
                    io.userDel = 1
                    io.save()
            if ('U'+uid+'S' in ordernum) or ('U'+uid+'C' in ordernum) or ('U'+uid+'-S' in ordernum):
                o = Order.get(ordernum=ordernum)
                if o.status == 0 or o.status == 5:
                    o.status = -1
                    o.save()
                elif o.status == 4:
                    o.userDel = 1
                    o.save()
            result['flag'] = 1
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))

@route(r'/mobile/storepopularize/(\d+)', name='store_popularize')
class StorePopularize(RequestHandler):
    def act_insurance(self, pop, uid, storeName, addr1, addr2, mobile, now):
        pic = '%s_%s_'%(pop['PicPath'], str(uid))
        oldPic = pic+'*'
        newPic = '%s%s.png'%(pic, now)
        if not os.system('ls %s > /dev/null 2>&1'%oldPic):
            os.system('rm -f '+oldPic)
        ttfont = ImageFont.truetype(setting.typeface, pop['wordSize'])
        im = Image.open(pop['basePicPath'])
        draw = ImageDraw.Draw(im)
        draw.text((pop['storeWidth'], pop['storeHeight']), storeName, fill=pop['wordColour'], font=ttfont)
        draw.text((pop['addrWidth'], pop['addrHeight']), addr1, fill=pop['wordColour'], font=ttfont)
        if addr2:
            draw.text((pop['addr2Width'], pop['addr2Height']), addr2, fill=pop['wordColour'], font=ttfont)
        draw.text((pop['phoneWidth'], pop['phoneHeight']), mobile, fill=pop['wordColour'], font=ttfont)
        im.save(newPic)
        return newPic[29:]

    def get(self, uid):
        result = {'flag': 0, 'data':[], 'msg': ''}
        try:
            user = User.get(id=uid)
            storeName = u'店铺：' + user.store.name
            addr = u'地址：' + Area().get_detailed_address(user.store.area_code) + user.store.address
            addr2 = ''
            mobile = u'电话：'+user.mobile
            now = str(time.time())[:10]
            for pop in setting.popularizePIC:
                areaLimits = 0
                for area_code in pop['area_code'].split(','):
                    if user.store.area_code.startswith(area_code):
                        areaLimits = 1
                if len(addr) > pop['addr2tab']:
                    addr1 = addr[:pop['addr2tab']]
                    addr2 = addr[pop['addr2tab']:]
                else:
                    addr1 = addr
                if areaLimits == 1:
                    picPath = self.act_insurance(pop, uid, storeName, addr1, addr2, mobile, now)
                    result['data'].append(picPath)
                    result['flag'] = 1

        except Exception, e:
            result['msg'] = u'生成图片错误'
            logging.info('Error: /mobile/storepopularize/%s, %s'%(uid, e.message))
        self.write(simplejson.dumps(result))


@route(r'/mobile/activity/(\d+)', name='mobile_activity')
class StorePopularize(RequestHandler):
    def get(self, aid):
        if aid == '1':
            pic = '/style/activity/zhoukou.jpg'
        elif aid == '2':
            pic = '/style/activity/fangjia.jpg'
        else:
            pic = '/style/activity/fangjia.jpg'
        self.render("mobile/pic.html", pic=pic)

















