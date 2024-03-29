#!/usr/bin/env python
# coding=utf8

import os

import simplejson
from PIL import Image, ImageDraw, ImageFont

from setting import popularizePIC
from handler import MobileBaseHandler
from handler import require_auth
# import lib.payment.ali_app_pay as alipay
import lib.payment.alipay_web.submit as alipay_web_app
from lib.payment.upay import Trade
from lib.payment.wxPay import UnifiedOrder_pub
from lib.route import route
from model import *
import logging
import urllib2
import urllib

from bootloader import settings


@route(r'/mobile/mine', name='mobile_mine')  # app我的主界面
class MobileMineHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/mine 01. app我的主界面
    @apiDescription app我的主界面，返回订单状态下的数量信息

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/mine
    """
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        platform = self.get_argument('platform','')
        result['data']['login_flag'] = 0
        result['data']['store_name'] = ''
        result['data']['user_name'] = ''
        result['data']['user_cover'] = 'http://img.520czj.com/image/2017/05/25/server1_20170525183829INZDSzGmjVfQBTUysOJAnuPl.png'
        result['data']['active'] = u'未审核'
        result['data']['store_type'] = 2  # 默认未登陆未门店
        result['data']['store_price'] = 0
        result['data']['store_score'] = 0

        result['data']['insurance_orders'] = {}
        result['data']['insurance_orders']['wait_pay'] = 0
        result['data']['insurance_orders']['wait_quote'] = 0
        result['data']['insurance_orders']['wait_send'] = 0
        result['data']['insurance_orders']['finish'] = 0
        result['data']['insurance_orders']['pay_back'] = 0
        result['data']['product_orders'] = {}
        result['data']['product_orders']['wait_pay'] = 0
        result['data']['product_orders']['wait_send'] = 0
        result['data']['product_orders']['wait_get'] = 0
        result['data']['product_orders']['finish'] = 0
        result['data']['product_orders']['pay_back'] = 0
        user = self.get_user()
        if user is not None:  # 已登录
            result['data']['login_flag'] = 1
            result['data']['store_name'] = user.store.name
            result['data']['user_name'] = user.mobile
            result['data']['active'] = user.store.active
            result['data']['store_price'] = user.store.price
            result['data']['store_score'] = user.store.score
            result['data']['store_type'] = user.store.store_type
            result['data']['active'] = user.store.active

            if user.store.store_type == 1:
                # 查询子订单数据
                sale_orders = SubOrder.select(SubOrder.status, fn.Count(SubOrder.status).alias('count')). \
                    where(SubOrder.status > -1, SubOrder.saler_del == 0, SubOrder.saler_store == user.store).\
                    group_by(SubOrder.status).tuples()
                for status, count in sale_orders:
                    if status == 0:  # 0待付款 1待发货 2待收货 3交易完成（待评价） 4已评价 5申请退款 6已退款 -1已取消
                        result['data']['product_orders']['wait_pay'] += count
                    elif status == 1:
                        result['data']['product_orders']['wait_send'] += count
                    elif status == 2:
                        result['data']['product_orders']['wait_get'] += count
                    elif status == 3:  # 仅考虑申请退款的状态
                        result['data']['product_orders']['finish'] += count
            elif user.store.store_type == 2:
                # 查询子订单数据
                buy_orders = Order.select(Order.status, fn.Count(Order.status).alias('count')). \
                    where(Order.status > -1, Order.buyer_del == 0, Order.buyer_store == user.store).\
                    group_by(Order.status).tuples()
                for status, count in buy_orders:
                    if status == 0:
                        result['data']['product_orders']['wait_pay'] += count
                    elif status == 1:
                        result['data']['product_orders']['wait_send'] += count
                    elif status == 2:
                        result['data']['product_orders']['wait_get'] += count
                    elif status == 3:
                        result['data']['product_orders']['finish'] += count
            if platform=='wx_b':
                insurance_orders = InsuranceOrder.select().\
                    where(InsuranceOrder.status > -1, InsuranceOrder.user_del == 0,
                          InsuranceOrder.user == user,InsuranceOrder.platform == 'wx_b')
            else:
                insurance_orders = InsuranceOrder.select(). \
                    where(InsuranceOrder.status > -1, InsuranceOrder.user_del == 0, InsuranceOrder.store == user.store)

            # 0待报价 1已核价/待支付 2已支付/待出单 3完成（已送积分/油） -1已删除(取消)
            for item in insurance_orders:
                if item.status == 0:
                    result['data']['insurance_orders']['wait_quote'] += 1
                elif item.status == 1 or item.current_order_price.append_refund_status==1:
                    result['data']['insurance_orders']['wait_pay'] += 1
                elif item.status == 2 and item.current_order_price.append_refund_status==0:
                    result['data']['insurance_orders']['wait_send'] += 1
                elif item.status == 3:
                    result['data']['insurance_orders']['finish'] += 1

        result['flag'] = 1
        self.write(simplejson.dumps(result))
        self.finish()


# ----------------------------------------------------推广大使----------------------------------------------------------
@route(r'/mobile/storepopularize', name='store_popularize')  # 推广大使
class MobilStorePopularizeHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/storepopularize 00 推广大使
    @apiDescription app  推广大使

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/storepopularize
    """
    def create_store_pic(self, pa_pic, store, addr1, addr2):
        pa_pic_tmp = pa_pic.picAP.split('.')
        pic = pa_pic_tmp[0] + '_' + str(store.id)+ '.' + pa_pic_tmp[1]
        new_pic_name = pic.split('/')[-1]
        if not os.path.exists(pic):
            ttfont = ImageFont.truetype(setting.typeface, pa_pic.setting.wordSize)
            im = Image.open(pa_pic.picAP)
            draw = ImageDraw.Draw(im)
            wordColour = tuple([int(a) for a in pa_pic.wordColour.split(',')])
            draw.text((pa_pic.setting.storeWidth, pa_pic.setting.storeHeight), store.name, fill=wordColour, font=ttfont)
            draw.text((pa_pic.setting.addrWidth, pa_pic.setting.addrHeight), addr1, fill=wordColour, font=ttfont)
            if addr2:
                draw.text((pa_pic.setting.addr2Width, pa_pic.setting.addr2Height), addr2, fill=wordColour, font=ttfont)
            draw.text((pa_pic.setting.phoneWidth, pa_pic.setting.phoneHeight), store.mobile, fill=wordColour, font=ttfont)
            im.save(pic, format='jpeg')
        return setting.imgDoman + 'store_popularize/' + new_pic_name

    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        try:
            store = self.get_user().store
            addr = Area.get_detailed_address(store.area_code) + store.address
            addr2 = ''
            if len(store.area_code) == 12:    # 门店是区，能查发布到省市和该区的规则
                codes = [store.area_code, store.area_code[:8], store.area_code[:4]]
                ft = (PromotionAmbassadorArea.area_code << codes)
            elif len(store.area_code) == 8:    # 门店地区是市，只能查发布到省和该市的规则
                codes = [store.area_code, store.area_code[:4]]
                ft = (PromotionAmbassadorArea.area_code << codes)
            elif len(store.area_code) == 4:    # 门店地区是省，只能查发布到省得规则
                ft = (PromotionAmbassadorArea.area_code == store.area_code)
            else:
                ft = None
            if ft:
                for paa in PromotionAmbassadorArea.select().join(PromotionAmbassadorPic).\
                        where(ft).order_by(PromotionAmbassadorPic.sort.desc(), PromotionAmbassadorPic.created.desc()):
                    if len(addr) > paa.pa_pic.setting.addr2tab:
                        addr1 = addr[:paa.pa_pic.setting.addr2tab]
                        addr2 = addr[paa.pa_pic.setting.addr2tab:]
                    else:
                        addr1 = addr
                    picPath = self.create_store_pic(paa.pa_pic,store, addr1, addr2)
                    result['data'].append(picPath)
                    result['flag'] = 1
            else:
                result['msg'] = u'门店地区没有配置'
        except Exception, e:
            logging.error('Error: /mobile/store_popularize: %s' % str(e))
            result['msg'] = u'生成图片失败'
        self.write(simplejson.dumps(result))


# ----------------------------------------------------订单--------------------------------------------------------------
@route(r'/mobile/purchaseorder', name='mobile_purchase_order')  # 普通商品订单列表（采购）
class MobilPurchaseOrderHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/purchaseorder 02 手机端普通商品采购订单
    @apiDescription app  手机端普通商品采购订单

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} type 订单状态类型 all全部，unpay待支付，undispatch待发货，unreceipt待收货，success交易完成/待评价， delete删除
    @apiParam {Int} index 每页起始个数

    @apiSampleRequest /mobile/purchaseorder
    """
    def delete_timeOut_order(self, user):
        timeOut = int(time.localtime()) - setting.PRODUCT_ORDER_TIME_OUT
        ft = (Order.user == user) & (SubOrder.status > -1) & (Order.ordered < timeOut)
        sos = SubOrder.select().join(Order).where(ft)
        for so in sos:
            so.status = -1
            so.fail_reason = u'超时未支付'
            so.save()

    def product_orders(self, type, index):
        ft = (Order.user == self.get_user()) & (Order.buyer_del == 0)
        if type == 'all':  # 全部
            ft &= (Order.status > -1)
        elif type == 'unpay':  # 待付款订单
            ft &= (Order.status == 0)
        elif type == 'undispatch':  # 待发货
            ft &= (Order.status == 1)
        elif type == 'unreceipt':  # 待收货
            ft &= (Order.status == 2)
        elif type == 'success':  # 交易完成/待评价
            ft &= (Order.status == 3)
        elif type == 'delete':  # 删除
            ft &= (Order.status == -1)

        result = []
        orders = Order.select().where(ft).order_by(Order.ordered.desc()).paginate(index, setting.MOBILE_PAGESIZE)
        for o in orders:
            result.append({
                'id': o.id,
                'ordernum': o.ordernum,
                'order_type': o.order_type,
                'price': o.total_price,
                'score': o.total_score,
                'status': o.status,
                'ordered': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(o.ordered)),
                'deadline': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(o.ordered + setting.PRODUCT_ORDER_TIME_OUT))
            })
        return result

    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        type = self.get_argument("type", 'all')
        index = int(self.get_argument('index', 1))
        user = self.get_user()
        try:
            result['data'] = self.product_orders(type, index)
            result['flag'] = 1
        except Exception, e:
            result['msg'] = u'系统错误'
        self.write(simplejson.dumps(result))


@route(r'/mobile/orderdetail', name='mobile_order_detail')  # 普通商品订单详情（采购）
class MobileOrderDetailHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/orderdetail 03. 普通商品订单详情（采购）
    @apiDescription 普通商品订单详情（采购）

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} type 订单状态类型 all全部，unpay待支付，undispatch待发货，unreceipt待收货，success交易完成/待评价， delete删除
    @apiParam {Int} index 每页起始个数

    @apiSampleRequest /mobile/orderdetail
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        oid = int(self.get_argument("id"))
        order = Order.get(id=oid)
        result['data']['address'] = {
            'name':order.delivery_to,
            'mobile': order.delivery_tel,
            'province': order.delivery_province,
            'city': order.delivery_city,
            'district': order.delivery_region,
            'address': order.delivery_address
        }
        result['data']['id'] = order.id
        result['data']['ordernum'] = order.ordernum
        result['data']['payment'] = order.payment
        result['data']['ordered'] = time.strftime('%Y-%m-%d', time.localtime(order.ordered))
        result['data']['totalprice'] = order.total_price
        result['data']['totalscore'] = order.total_score
        result['data']['status'] = order.status
        result['data']['order_type'] = order.order_type

        suborders = []
        for suborder in order.sub_orders:
            products = []
            for product in suborder.items:
                pics = [item.pic for item in product.product.pics]
                pic = None
                if pics:
                    pic = pics[0]
                try:
                    productattibute = ProductAttributeValue.get(ProductAttributeValue.product == product.product)
                    attribute = "%s %s" % (productattibute.attribute.name, productattibute.value)
                except Exception, e:
                    attribute = ''
                products.append({
                    'img': pic,
                    'name': product.product.name,
                    'price': product.price,
                    'quantity': product.quantity,
                    'attribute': attribute,
                    'score': int(product.store_product_price.score),
                    'is_score': product.store_product_price.product_release.is_score
                })
            suborders.append({
                'name': suborder.saler_store.name,
                'consultmobile': suborder.saler_store.mobile,
                'complainmobile': suborder.saler_store.mobile,
                'products': products,
                'soid': suborder.id,
                'price': suborder.price,
                'score': int(suborder.score),
                'status': suborder.status,
                'order_type': order.order_type
            })
        if suborders:
            result['flag'] = 1
        result['data']['suborder'] = suborders
        self.write(simplejson.dumps(result))


@route(r'/mobile/receiveorder', name='mobile_receive_order')  # 手机端处理订单（收货）
class MobileReceiveOrderHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/receiveorder 14. 收货
    @apiDescription 收货按钮
    @apiHeader {String} token 用户登录凭证
    @apiParam {Int} soid 子订单ID
    @apiSampleRequest /mobile/receiveorder
    """

    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', 'data': ''}
        soid = self.get_argument('soid', None)
        user = self.get_user()

        if not soid:
            result['msg'] = u'传入参数异常'
            self.write(simplejson.dumps(result))
            return
        sub_orders = SubOrder.select().join(Order).where((SubOrder.buyer_store == user.store) & (SubOrder.id == soid) & (SubOrder.status == 2))
        if sub_orders.count() > 0:
            sub_orders[0].status = 3
            sub_orders[0].save()
            # 收完货，把该订单的钱同步给销售方
            # salestore = sub_orders[0].saler_store
            # salestore.price += sub_orders[0].price
            # salestore.save()
            # process_log = u'订单号：%s' % sub_orders[0].order.ordernum
            # MoneyRecord.create(user=salestore.users[0], store=salestore, process_type=1, type=3, process_message='售出',
            #                    process_log=process_log, money=sub_orders[0].price, status=1, apply_time=now)
            if len(set([sub_order.status for sub_order in sub_orders])) == 1:
                sub_orders[0].order.status = 3
                sub_orders[0].order.save()
            result['flag'] = 1
        else:
            result['msg'] = u'该订单不可收货'
        self.write(simplejson.dumps(result))
        return


@route(r'/mobile/sellorder', name='mobile_sell_order')  # 普通商品订单（售出）
class MobileSellOrderHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/sellorder 03. 普通商品售出订单
    @apiDescription 普通商品售出订单

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} type 订单状态类型 all全部，unpay待支付，undispatch待发货，unreceipt待收货，success交易完成/待评价， delete删除
    @apiParam {Int} index 每页起始个数

    @apiSampleRequest /mobile/sellorder
    """

    def productOrderSearch(self, type, index):
        store = self.get_user().store
        ft = (SubOrder.saler_store == store)
        # 0待付款 1待发货 2待收货 3交易完成（待评价） 4已评价 5申请退款 6已退款 -1已取消
        if type == 'all':  # 全部
            ft &= (SubOrder.status > -1)
        elif type == 'unpay':  # 待付款订单
            ft &= (SubOrder.status == 0)
        elif type == 'undispatch':  # 待发货
            ft &= (SubOrder.status == 1)
        elif type == 'unreceipt':  # 待收货
            ft &= (SubOrder.status == 2)
        elif type == 'success':  # 交易完成/待评价
            ft &= (SubOrder.status == 3)
        elif type == 'delete':  # 删除
            ft &= (SubOrder.status == -1)

        result = []
        sos = SubOrder.select().where(ft).order_by(SubOrder.id.desc()).paginate(index, setting.MOBILE_PAGESIZE)
        for so in sos:
            items = []
            # totalprice = 0.0
            for soi in so.items:
                # totalprice += soi.price*soi.quantity
                items.append(
                    {
                        'product': soi.product.name,
                        'cover': soi.product.cover,
                        'id': soi.store_product_price.id,
                        'price': soi.price,
                        'quantity': soi.quantity,
                        'attributes': [attribute.value for attribute in soi.product.attributes],
                        'order_type': so.order.order_type
                    }
                )
            result.append({
                'id': so.order.id,
                'soid': so.id,
                'ordernum': so.order.ordernum,
                'saler_store': so.saler_store.name,
                'buyer_store': so.buyer_store.name,
                'order_type': so.order.order_type,
                'price': so.price,
                'score': so.score,
                'status': so.status,
                'items': items,
                'ordered': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(so.order.ordered)),
                'deadline': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(so.order.ordered + setting.PRODUCT_ORDER_TIME_OUT))
            })

        return result

    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        type = self.get_argument("type", 'all')
        index = int(self.get_argument('index', 1))
        try:
            result['data'] = self.productOrderSearch(type, index)
            result['flag'] = 1
        except Exception, e:
            logging.error('Error: /mobile/sellorder %s' % str(e))
            result['msg'] = '系统错误'
        self.write(simplejson.dumps(result))


@route(r'/mobile/suborderdetail', name='mobile_suborder_detail')  # 普通商品订单详情（售出）
class MobileSubOrderDetailHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/suborderdetail 03. 售出商品订单详情
    @apiDescription 售出商品订单详情

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} soid 子订单id

    @apiSampleRequest /mobile/suborderdetail
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        soid = int(self.get_argument("soid"))
        suborder = SubOrder.get(id=soid)
        order = suborder.order
        result['data']['address'] = {
            'name': order.delivery_to,
            'mobile': order.delivery_tel,
            'province': order.delivery_province,
            'city': order.delivery_city,
            'district': order.delivery_region,
            'address': order.delivery_address
        }

        result['data']['totalprice'] = suborder.price
        result['data']['status'] = suborder.status
        result['data']['ordernum'] = order.ordernum
        result['data']['score'] = suborder.score
        result['data']['order_type'] = order.order_type
        result['data']['ordered'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(suborder.order.ordered))

        items = []
        # total_price = 0.0
        for product in suborder.items:
            pics = [item.pic for item in product.product.pics]
            pic = None
            if pics:
                pic = pics[0]
            # productattibute = ProductAttributeValue.get(ProductAttributeValue.product == product.product)
            # attribute = "%s %s" % (productattibute.attribute.name, productattibute.value)
            # total_price += product.price*product.quantity
            items.append({
                'img': pic,
                'name': product.product.name,
                'price': product.price,
                'quantity': product.quantity,
                'attribute': ''
            })
        if items:
            result['flag'] = 1
        result['data']['items'] = items
        # result['data']['totalprice'] = total_price
        self.write(simplejson.dumps(result))


@route(r'/mobile/deleteorder', name='mobile_delete_order')  # 删除商品订单
class MobileDeleteOrderHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/deleteorder 03. 删除商品订单
    @apiDescription 删除商品订单

    @apiHeader {String} token 用户登录凭证
    @apiParam {Int} id 订单id

    @apiSampleRequest /mobile/deleteorder
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        oid = int(self.get_argument("id"))
        user = self.get_user()
        try:
            order = Order.get((Order.user == user) & (Order.id == oid))
            if order.status in [0, 3, 4]:
                order.buyer_del = 1
                order.save()
                result['flag'] = 1
            else:
                result['msg'] = u'当前状态不允许删除'
        except Exception:
            result['msg'] = u'该订单不存在'
            result['flag'] = 0
        self.write(simplejson.dumps(result))


@route(r'/mobile/insuranceorder', name='mobile_insurance_order')  # 保险订单列表
class MobileInsuranceOrderHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/insuranceorder 04. 保险订单
    @apiDescription 保险订单

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} type 订单状态类型 all全部，unverify待确认，unpay待支付，paid付款完成，success已办理，post已邮寄， delete删除
    @apiParam {Int} index 每页起始个数

    @apiSampleRequest /mobile/insuranceorder
    """
    def dead_insurance_order_price(self,store):
        now = int(time.time())
        iopselect = InsuranceOrderPrice.select().join(InsuranceOrder, on=(InsuranceOrderPrice.insurance_order_id==InsuranceOrder.id)). \
            where(InsuranceOrder.store == store.id,InsuranceOrder.status << [0,1],InsuranceOrderPrice.created+setting.deadlineTime<now)

        for iop in iopselect:
            iop.status = 0
            iop.save()
            # io = InsuranceOrder.get(id=iop.insurance_order_id)
            # io.status = -1
            # io.cancel_reason = u'过期取消'
            # io.cancel_time = int(time.time())

    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        type = self.get_argument("type", 'all')
        index = int(self.get_argument('index', 1))
        platform = self.get_argument('platform','')
        user = self.get_user()
        self.dead_insurance_order_price(user.store)
        if platform=='wx_b':
            ft = ((InsuranceOrder.user == user) & (InsuranceOrder.user_del == 0)) & (InsuranceOrder.platform == 'wx_b')
        else:
            ft = ((InsuranceOrder.store == user.store) & (InsuranceOrder.user_del == 0))
        # 0待报价 1已核价/待支付 2已支付/待出单 3完成（已送积分/油） -1已删除(取消)
        iop = False
        if type == 'all':  # 全部
            ft &= (InsuranceOrder.status > -1) & (InsuranceOrder.user_del == 0)
        elif type == 'unverify':  # 待确认
            ft &= (InsuranceOrder.status == 0) & (InsuranceOrder.user_del == 0)
        elif type == 'unpay':  # 待付款
            ft &= ((InsuranceOrder.status == 1) | (InsuranceOrderPrice.append_refund_status == 1)) & (InsuranceOrder.user_del == 0)
            iop = True
        elif type == 'paid':  # 付款完成
            ft &= (InsuranceOrder.status == 2) & (InsuranceOrderPrice.append_refund_status == 0) & (InsuranceOrder.user_del == 0)
            iop = True
        elif type == 'success':  # 已办理
            ft &= (InsuranceOrder.status == 3) & (InsuranceOrderPrice.append_refund_status == 0) & (InsuranceOrder.user_del == 0)
            iop = True
        elif type == 'delete':  # 删除
            ft &= ((InsuranceOrder.status == -1) | (InsuranceOrder.user_del == 1))
        elif type == 'post':  # 已邮寄
            ft &= (InsuranceOrder.status == 4) & (InsuranceOrder.user_del == 0)
        else:
            result['msg'] = u'输入参数有误'
            return
        if iop:
            ios = InsuranceOrder.select().\
                join(InsuranceOrderPrice, on=(InsuranceOrderPrice.id == InsuranceOrder.current_order_price)).\
                where(ft).order_by(InsuranceOrder.ordered.desc()).paginate(index, setting.MOBILE_PAGESIZE)
        else:
            ios = InsuranceOrder.select().where(ft).order_by(InsuranceOrder.ordered.desc()).paginate(index, setting.MOBILE_PAGESIZE)

        for io in ios:
            result['data'].append({
                'id': io.id,
                'ordernum': io.ordernum,
                'iName': io.current_order_price.insurance.name,
                'status': io.status,
                'platform': io.platform,
                'platform_tips':'代理人下单'  if io.platform == 'wx_b' else '',
                'is_append': 1 if io.current_order_price.append_refund_status == 1 and io.current_order_price.append_refund_num > 0 else 0,
                'append_num':  io.current_order_price.append_refund_num,
                'append_reason': io.current_order_price.append_refund_reason,
                'sName': io.store.name,
                'recipients': io.delivery_to,
                'recipientsTel': io.delivery_tel,
                'recipientsAddr': io.delivery_province+io.delivery_city+io.delivery_region+io.delivery_address,
                'price': io.current_order_price.total_price,
                'commission': u'返油' if io.current_order_price.gift_policy == 1 else u'返佣金',
                'ordered': time.strftime('%Y-%m-%d %H:%M', time.localtime(io.ordered)),
                'deadline': time.strftime('%Y-%m-%d %H:%M', time.localtime(io.ordered + setting.INSURANCE_ORDER_TIME_OUT)),
                'store_name': io.store.name,
                'store_addr': Area.get_detailed_address(io.store.area_code) + io.store.address,
                'mobile': io.store.mobile
            })
        result['flag'] = 1
        logging.info('ios count:%d'%ios.count())
        self.write(simplejson.dumps(result))


@route(r'/mobile/insuranceorderdetail', name='mobile_insurance_order_detail')  # 保险订单详情
class MobileInsuranceOrderDetailHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/insuranceorderdetail 10. 保险订单详情
    @apiDescription 保险订单详情

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} id 订单id

    @apiSampleRequest /mobile/insuranceorderdetail
    """

    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        iList = {'subjoin': [], 'main': [], 'force': 'false'}
        ioid = int(self.get_argument('id', 1))
        insuranceorder = InsuranceOrder.get(id=ioid)
        insuranceitem = InsuranceItem.select().order_by(InsuranceItem.sort)
        iList['mainprice'] = 0
        iList['subjoinprice'] = 0
        for i in insuranceitem:
            iValue = getattr(insuranceorder.current_order_price, i.eName)
            iPrice = getattr(insuranceorder.current_order_price, i.eName+'Price')
            if not iPrice:
                iPrice = 0
            if i.style == u'交强险':
                iValue = getattr(insuranceorder.current_order_price, i.eName)
                iList['force'] = '1' if insuranceorder.current_order_price.forceI=='1' else '0'
                iList['forceprice'] = str(insuranceorder.current_order_price.forceIPrice if insuranceorder.current_order_price.forceIPrice else 0.0)
                iList['vehicle_tax'] = iList['force']
                iList['vehicle_tax_price'] = str(
                    insuranceorder.current_order_price.vehicle_tax_price if insuranceorder.current_order_price.vehicle_tax_price else 0.0)
            elif i.style == u'商业险-主险' and iValue != 'false' and iValue:
                iList['main'].append({'eName': i.eName,
                                      'name': '%s(%s)'%(i.name,iValue) if len(iValue)>1 else i.name,
                                      'style': i.style,
                                      'value': iValue,
                                      'price':str(iPrice)})
                iList['mainprice'] += iPrice
            elif i.style == u'商业险-附加险' and iValue != 'false' and iValue:
                iList['subjoin'].append({'eName': i.eName,
                                         'name': '%s(%s)'%(i.name,iValue) if len(iValue)>1 else i.name,
                                         'style': i.style,
                                         'value': iValue,
                                         'price':str(iPrice)})
                iList['subjoinprice'] += iPrice
        if 'mainprice' in iList.keys():
            iList['mainprice'] = str(iList['mainprice'])
        if 'subjoinprice' in iList.keys():
            iList['subjoinprice'] = str(iList['subjoinprice'])
        gift_summary = ''
        if insuranceorder.current_order_price.gift_policy == 1:
            gift_policy = '油品'
            commission = str(insuranceorder.current_order_price.driver_lube_num+insuranceorder.current_order_price.store_lube_num) + u'桶'
        elif insuranceorder.current_order_price.gift_policy == 2:
            gift_policy = '现金'
            commission = str(insuranceorder.current_order_price.cash) + u'元'
        elif insuranceorder.current_order_price.gift_policy == 3:
            lubenum = insuranceorder.current_order_price.driver_lube_num+insuranceorder.current_order_price.store_lube_num
            scorenum = insuranceorder.current_order_price.score
            if lubenum and scorenum:
                gift_policy = '积分&油品'
                gift_summary = insuranceorder.current_order_price.store_lube_type
            elif lubenum:
                gift_policy = '油品'
                gift_summary = insuranceorder.current_order_price.store_lube_type
            else:
                gift_summary = ''
                gift_policy = '积分'
            commission = str(insuranceorder.current_order_price.driver_lube_num+insuranceorder.current_order_price.store_lube_num) + u'桶' +str(insuranceorder.current_order_price.score) + '分'
        else:
            gift_policy = u'其它'
            commission = u'无'
        result["flag"] = 1
        deadlineWarning = ''

        messagelist = Message.select().where(Message.store == insuranceorder.store.id,Message.other_id==insuranceorder.id)
        for m in messagelist:
            m.status = 1
            m.save()
        result['data'] = {
            'id': insuranceorder.id,
            'ordernum': insuranceorder.ordernum,
            'platform': insuranceorder.platform,
            'platform_tips': '代理人下单' if insuranceorder.platform == 'wx_b' else '',
            'ordereddate': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(insuranceorder.ordered)),
            'hotline': '13912345678',
            'paytype': insuranceorder.payment,
            'deadlinewarning': deadlineWarning,
            'commission': '待核算' if insuranceorder.status == 0 else commission,
            'gift_summary': gift_summary,
            'is_append': 1 if insuranceorder.current_order_price.append_refund_status == 1 and insuranceorder.current_order_price.append_refund_num > 0 else 0,
            'append_num':  insuranceorder.current_order_price.append_refund_num,
            'append_reason': insuranceorder.current_order_price.append_refund_reason,
            'gift_policy': gift_policy,
            'store_name': insuranceorder.store.name,
            'store_addr': Area.get_detailed_address(insuranceorder.store.area_code) + insuranceorder.store.address,
            'mobile': insuranceorder.store.mobile,
            'total_price': str(insuranceorder.current_order_price.total_price),
            'is_same_person': insuranceorder.is_same_person,
            'insuranceorderprice': {
                'status': insuranceorder.status,
                'insurance': insuranceorder.current_order_price.insurance.name,
                'created': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(insuranceorder.current_order_price.created)),
                'iList': iList,
                'price': insuranceorder.current_order_price.total_price,
                'score': insuranceorder.current_order_price.score
            },
            'imgs': {
                'id_card_front': insuranceorder.id_card_front,
                'id_card_front_status':insuranceorder.icfstatus,
                'id_card_back': insuranceorder.id_card_back,
                'id_card_back_status': insuranceorder.icbstatus,
                'drive_card_front': insuranceorder.drive_card_front,
                'drive_card_front_status': insuranceorder.dcfstatus,
                'drive_card_back': insuranceorder.drive_card_back,
                'drive_card_back_status': insuranceorder.dcbstatus,
                'id_card_front_owner': insuranceorder.id_card_front_owner if insuranceorder.id_card_front_owner else '',
                'icfo_status': insuranceorder.icfostatus if insuranceorder.icfostatus else 0,
                'id_card_back_owner': insuranceorder.id_card_back_owner if insuranceorder.id_card_back_owner else '',
                'icbo_status': insuranceorder.icbostatus if insuranceorder.icbostatus else 0,
            },
            'delivery': {
                'name': insuranceorder.delivery_to,
                'mobile': insuranceorder.delivery_tel,
                'province': insuranceorder.delivery_province,
                'city': insuranceorder.delivery_city,
                'district': insuranceorder.delivery_region,
                'address': insuranceorder.delivery_address
            }
        }
        print simplejson.dumps(result)
        self.write(simplejson.dumps(result))

    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        io_id  = int(self.get_body_argument('io_id', 0))
        # id_card_front = self.get_body_argument('id_card_front', None)
        # id_card_back = self.get_body_argument('id_card_back', None)
        # drive_card_front = self.get_body_argument('drive_card_front', None)
        # drive_card_back = self.get_body_argument('drive_card_back', None)
        insurance = self.get_body_argument('insurance', None)
        # delivery_to = self.get_body_argument('delivery_to', None)
        # delivery_tel = self.get_body_argument('delivery_tel', None)
        # delivery_province = self.get_body_argument('delivery_province', None)
        # delivery_city = self.get_body_argument('delivery_city', None)
        # delivery_district = self.get_body_argument('delivery_district', None)
        # delivery_address = self.get_body_argument('delivery_address', None)
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
        if user and gift_policy and insurance and io_id:
            order = InsuranceOrder.get(id = io_id)
            order.user = user
            order.store = user.store
            # order.id_card_front = id_card_front
            # order.id_card_back = id_card_back
            # order.drive_card_front = drive_card_front
            # order.drive_card_back = drive_card_back
            # order.ordered = int(time.time())
            # order.delivery_to = delivery_to
            # order.delivery_tel = delivery_tel
            # order.delivery_province = delivery_province
            # order.delivery_city = delivery_city
            # order.delivery_region = delivery_district
            # order.delivery_address = delivery_address
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
            # order.ordernum = 'U' + str(user.id) + 'I' + str(order.id)
            order.current_order_price = order_price.id
            order.save()
            result['flag'] = 1
            result['msg'] = '修改成功'
            result['data']['order_id'] = order.id
            result['data']['order_price_id'] = order_price.id
        else:
            result['msg'] = '输入参数异常'
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/update_insuranceorderd_address', name='mobile_update_insuranceorderd_address')  #
class MobileInsuranceOrderDetailHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/update_insuranceorderd_address 10. 保险订单详情
    @apiDescription 保险订单详情

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} io_id 保险订单id
    @apiParam {Int} address_id 收货地址id

    @apiSampleRequest /mobile/update_insuranceorderd_address
    """

    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        io_id = int(self.get_body_argument('io_id', 0))
        addres_id = int(self.get_body_argument('address_id',0))

        user = self.get_user()
        if user and addres_id and io_id:
            address = StoreAddress.get(id = addres_id)
            order = InsuranceOrder.get(id = io_id)
            order.delivery_to = address.name
            order.delivery_tel = address.mobile
            order.delivery_province = address.province
            order.delivery_city = address.city
            order.delivery_region = address.region
            order.delivery_address = address.address
            order.save()

            result['flag'] = 1
            result['msg'] = '修改成功'
        else:
            result['msg'] = '输入参数异常'
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/insurance_method', name='mobile_insurance_method')  # 保险订单历史方案 列表
class MobileInsuranceMethodHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/insurance_method 11. 保险订单历史方案
    @apiDescription 保险订单历史方案

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} id 订单id

    @apiSampleRequest /mobile/insurance_method
    """

    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        io_id = self.get_argument('id', '')
        if io_id:
            result['flag'] = 1
            result['msg'] = u'订单号存在'
            io_id = int(io_id)
        else:
            result['msg'] = u'订单号不能为空'
            self.write(simplejson.dumps(result))
            return

        ops = InsuranceOrderPrice.select().where(InsuranceOrderPrice.insurance_order_id == io_id)
        for iop in ops:
            force = '0'
            forceprice = 0
            vehicle_tax = '0'
            vehicle_tax_price = 0.0
            mainprice = 0
            subjoinprice = 0
            main = []
            subjoin = []
            insuranceitem = InsuranceItem.select().order_by(InsuranceItem.sort)
            for i in insuranceitem:
                iValue = getattr(iop, i.eName)
                iPrice = getattr(iop, i.eName+'Price')
                if not iPrice:
                    iPrice = 0
                if i.style == u'交强险':
                    # force = iValue if iValue else ''
                    # forceprice = iPrice
                    force = '1' if iop.forceI=='1' else '0'
                    forceprice = str(iop.forceIPrice if iop.forceIPrice else 0.0)
                    vehicle_tax = force
                    vehicle_tax_price = str(
                        iop.vehicle_tax_price if iop.vehicle_tax_price else 0.0)
                elif i.style == u'商业险-主险' and iValue != 'false' and iValue:
                    main.append({'eName': i.eName,
                                 'name': '%s(%s)'%(i.name,iValue) if len(iValue)>1 else i.name,
                                 'style': i.style,
                                 'value': iValue,
                                 'price':str(iPrice)})
                    mainprice += iPrice
                elif i.style == u'商业险-附加险' and iValue != 'false' and iValue:
                    subjoin.append({'eName': i.eName,
                                    'name': '%s(%s)'%(i.name,iValue) if len(iValue)>1 else i.name,
                                    'style': i.style,
                                    'value': iValue,
                                    'price':str(iPrice)})
                    subjoinprice += iPrice
            if mainprice:
                mainprice =str(mainprice)

            if subjoinprice:
                subjoinprice = str(subjoinprice)
            gift_summary = ''
            if iop.gift_policy == 1:
                gift_policy = '油品'
                gift_summary = iop.store_lube_type
                commission = u'%s桶'%str(iop.driver_lube_num+iop.store_lube_num)
            elif iop.gift_policy == 2:
                gift_policy = '现金'
                commission = u'¥%s'%str(iop.cash)
            elif iop.gift_policy == 3:
                gift_policy = '积分'
                gift_summary = iop.store_lube_type
                commission = u'%s桶%s分'%(str(iop.store_lube_num),str(iop.score))
            else:
                commission = u'待计算'

            result['data'].append({
                'iop_id': iop.id,
                'insurancename':iop.insurance.name,
                'created':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(iop.created)),
                'force': force,
                'forceprice':forceprice,
                'vehicle_tax':vehicle_tax,
                'vehicle_tax_price':vehicle_tax_price,
                'main': main,
                'mainprice': mainprice,
                'subjoin': subjoin,
                'subjoinprice': subjoinprice,
                'gift_policy': gift_policy,
                'gift_summary': gift_summary,
                'score': iop.score,
                'commission': '待核算' if iop.status == 0 else commission,
                'total_price': iop.total_price,
                'default': 1 if iop == InsuranceOrder.get(id=io_id).current_order_price else 0,
                'status': iop.status,
                'response': iop.response
            })
        print simplejson.dumps(result)
        self.write(simplejson.dumps(result))


@route(r'/mobile/change_insurance_method', name='mobile_change_insurance_method')  # 切换历史方案（保险订单）
class MobileChangeInsuranceMethodHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/change_insurance_method 12. 切换历史方案（保险订单）
    @apiDescription 切换历史方案（保险订单）

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} id 保险订单id
    @apiParam {Int} iop_id 保险方案id

    @apiSampleRequest /mobile/change_insurance_method
    """

    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        io_id = int(self.get_argument('id', 0))
        iop_id = int(self.get_argument('iop_id', 0))

        if not (io_id and iop_id):
            result['msg'] = u'传入参数异常'
            self.write(simplejson.dumps(result))
            return
        try:
            iop = InsuranceOrderPrice.get(id=iop_id)
            io = InsuranceOrder.get(id=io_id)
            if io.status in  [2,3,-1]:
                result['flag'] = 0
                result['msg'] = '该订单不允许切换报价方案'
                self.write(simplejson.dumps(result))
                return
            if iop.status == 0:
                result['flag'] = 0
                result['msg'] = '不允许切换到过期报价方案'
                self.write(simplejson.dumps(result))
                return
            if iop.insurance_order_id == int(io_id):
                io.current_order_price = int(iop_id)
                # 0待报价 1已核价/待支付 2已支付/待出单 3完成（已送积分/油） -1已删除(取消)
                if iop.response == 0:
                    io.status = 0
                elif iop.response==1:
                    io.status = 1

                io.save()
                result['flag'] = 1
                result['msg'] = u'修改成功！'
            else:
                result['msg'] = u'方案与订单不匹配'
        except Exception, e:
            logging.error(e)
            result['msg'] = u'方案或订单不存在'

        self.write(simplejson.dumps(result))


@route(r'/mobile/update_insurance_order_img', name='update_insurance_order_img')  # 修改保险订单证件图片（保险订单）
class MobileUpdateInsuranceOrderIMGHandler(MobileBaseHandler):
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

    @require_auth
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


@route(r'/mobile/delete_insurance_order', name='mobile_delete_insurance_order')  # 删除保险订单
class MobileInsuranceMethodHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/delete_insurance_order 删除保险订单
    @apiDescription 删除保险订单

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} id 保险订单id

    @apiSampleRequest /mobile/delete_insurance_order
    """

    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        io_id = self.get_argument('id', '')
        user = self.get_user()

        ios = InsuranceOrder.select().where((InsuranceOrder.user == user) & (InsuranceOrder.id == io_id))
        if ios.count() > 0:
            if ios[0].status in [-1, 0, 1, 3]:
                ios[0].user_del = 1
                ios[0].save()
                result['flag'] = 1
            else:
                result['msg'] = u'该订单不能删除'
        else:
            result['msg'] = u'该订单不存在'

        self.write(simplejson.dumps(result))


@route(r'/mobile/deliveryorder', name='mobile_delivery_order')  # 手机端处理订单（发货）
class MobileDeliveryOrderHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/deliveryorder 12. 获取快递公司信息
    @apiDescription 获取快递公司信息
    @apiHeader {String} token 用户登录凭证
    @apiSampleRequest /mobile/deliveryorder
    """
    @require_auth
    def get(self):
        result = {'flag': 1, 'msg': '', 'data': [{'id': delivery.id, 'name': delivery.name, 'img': delivery.img} for delivery in Delivery.select()]}
        self.write(simplejson.dumps(result))
        self.finish()

    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/deliveryorder 13. 经销商发货
    @apiDescription 经销商发货

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} soid 子订单id
    @apiParam {Int} did 物流公司id
    @apiParam {Int} delivery_num 物流单号

    @apiSampleRequest /mobile/deliveryorder
    """
    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': ''}
        soid = self.get_body_argument('soid', None)
        did = self.get_body_argument('did', None)
        delivery_num = self.get_body_argument('delivery_num', None)
        user = self.get_user()

        if not (soid and did and delivery_num):
            result['msg'] = u'传入参数异常'
            self.write(simplejson.dumps(result))
            return
        if not user.store.store_type == 1:
            result['msg'] = u'您不是经销商'
            self.write(simplejson.dumps(result))
            return

        sub_orders = SubOrder.select().join(Order).where((SubOrder.saler_store == user.store) & (SubOrder.id == soid) & (SubOrder.status == 1))
        if sub_orders:
            sub_orders[0].status = 2
            sub_orders[0].delivery = int(did)
            sub_orders[0].delivery_num = delivery_num
            sub_orders[0].delivery_time = int(time.time())
            sub_orders[0].save()
            if len(set([sub_order.status for sub_order in sub_orders])) == 1:
                sub_orders[0].order.status = 2
                sub_orders[0].order.save()
            # sms = {'mobile': sub_orders.address.mobile, 'body': sub_orders.ordernum, 'signtype': '1', 'isyzm': 'shipments'}
            # 'body': u"订单号：" + order.ordernum + u"商品已发货，如有质量投诉请拨" + self.settings['com_tel'],
            # create_msg(simplejson.dumps(sms), 'sms')  # 发货
            result['flag'] = 1
        else:
            result['msg'] = u'该订单不可发货'

        self.write(simplejson.dumps(result))


@route(r'/mobile/change_order_price', name='mobile_change_order_price')  # 手机端 经销商修改订单价格
class ChangeOrderPriceHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/change_order_price 15. 经销商修改订单价格
    @apiDescription 经销商修改订单价格

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} soid 子订单id
    @apiParam {Int} sub_order_price 子订单原价
    @apiParam {Int} sub_order_price_new 子订单修改后价格

    @apiSampleRequest /mobile/change_order_price
    """
    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': ''}
        soid = self.get_body_argument('soid', None)
        sub_order_price = self.get_body_argument('sub_order_price', None)
        sub_order_price_new = self.get_body_argument('sub_order_price_new', None)
        user = self.get_user()
        if soid and sub_order_price and sub_order_price_new:
            soid = int(soid)
            sub_order_price = float(sub_order_price)
            sub_order_price_new = float(sub_order_price_new)
        else:
            result['msg'] = u'传入参数有误'
            self.write(simplejson.dumps(result))
            return
        sub_order = SubOrder.get(id=soid)
        if sub_order.price == sub_order_price and sub_order.saler_store == user.store:
            sub_order.price = sub_order_price_new
            order_price = sub_order.order.total_price
            sub_order.order.total_price -= (sub_order.price-sub_order_price_new)
            sub_order.order.save()
            sub_order.save()
            now = int(time.time())
            log = u'门店:%s将订单%s价格由%s修改为%s' % (user.store.name, sub_order.order.ordernum, sub_order_price,
                                             sub_order_price_new)
            OrderRepriceRecord.create(order=sub_order.order, sub_order=sub_order, order_price=order_price,
                                      sub_order_price=sub_order_price, user=user, log=log, created=now)
            result['flag'] = 1
        else:
            result['msg'] = u'订单价格不一致，刷新后重试'

        self.write(simplejson.dumps(result))


# ----------------------------------------------------积分--------------------------------------------------------------
@route(r'/mobile/score', name='mobile_score')  # 积分入口
class MobileScoreHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/score 05. 积分入口
    @apiDescription 积分入口

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/score
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        store = self.get_user().store
        result['data']['score'] = store.score
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/scoreStore', name='mobile_score_store')  # 积分商城
class MobileScoreStore(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/scoreStore 06. 积分商城
    @apiDescription 积分商城

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} index 每页起始个数

    @apiSampleRequest /mobile/scoreStore
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        index = int(self.get_argument("index", 1))
        store = self.get_user().store
        ft = (StoreProductPrice.score>0) & (StoreProductPrice.active==1) & (ProductRelease.active==1) & (Product.active==1)
        if len(store.area_code) == 12:  # 门店可以购买的范围仅仅到区县
            ft &= (((db.fn.Length(StoreProductPrice.area_code) == 4) & (StoreProductPrice.area_code == store.area_code[:4])) |
                   ((db.fn.Length(StoreProductPrice.area_code) == 8) & (StoreProductPrice.area_code == store.area_code[:8])) |
                   (StoreProductPrice.area_code == store.area_code))
        elif len(store.area_code) == 8:  # 门店可以购买的范围到市级
            ft &= (((db.fn.Length(StoreProductPrice.area_code) == 4) & (StoreProductPrice.area_code == store.area_code[:4])) |
                   (StoreProductPrice.area_code == store.area_code))
        elif len(store.area_code) == 4:  # 门店可以购买的范围到省级
            ft &= (StoreProductPrice.area_code == store.area_code)

        spps = StoreProductPrice.select().\
            join(ProductRelease, on=(ProductRelease.id==StoreProductPrice.product_release)).\
            join(Product, on=(Product.id==ProductRelease.product)).where(ft).\
            order_by(StoreProductPrice.created.desc()).paginate(index, setting.MOBILE_PAGESIZE)
        for spp in spps:
            result['data'].append({
                'sppid': spp.id,
                'prid': spp.product_release.id,
                'pid': spp.product_release.product.id,
                'name': spp.product_release.product.name,
                'score': spp.score,
                'unit': spp.product_release.product.unit,
                'buy_count': spp.product_release.buy_count,
                'cover': spp.product_release.product.cover,
                'resume': spp.product_release.product.resume,
                'storeName': spp.product_release.store.name,
                'is_score': 1
            })
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/scorecash', name='mobile_score_cash')  # 积分兑现
class MobileScoreCashHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/scorecash 07. 积分兑现
    @apiDescription 积分兑现

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/scorecash
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        store = self.get_user().store
        result['data']['score'] = store.score
        result['data']['cashRate'] = setting.CASH_RATE
        result['data']['baseMoney'] = setting.CASH_MIN_MONEY
        result['flag'] = 1
        self.write(simplejson.dumps(result))

    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/scorecash 08. 提交兑现
    @apiDescription 提交兑现

    @apiHeader {String} token 用户登录凭证
    @apiParam {Int} score 积分
    @apiParam {Int} money 金钱（人民币）

    @apiSampleRequest /mobile/scorecash
    """

    def post(self):
        result = {'flag': 0, 'msg': '', 'data': {}}
        score = self.get_body_argument('score', None)
        money = self.get_body_argument('money', None)
        user = self.get_user()
        if score and money:
            money = float(money)
            score = int(round(money/setting.CASH_RATE, 0))
        else:
            result['msg'] = '参数有误'
            self.write(simplejson.dumps(result))
            return
        store = self.get_user().store
        if store.score >= score and score >= setting.CASH_MIN_MONEY:
            sysCalculateMoney = score*setting.CASH_RATE

            if money == sysCalculateMoney:
                try:
                    old_score = store.score
                    old_money = store.price
                    store.score -= score
                    store.price += money
                    store.save()
                    sr = ScoreRecord.create_score_record(user, 2, score, '积分兑现')
                    if sr:
                        result['flag'] = 1
                        result['msg'] = '兑现成功'
                        sr.ordernum = 'U%sC%s'%(user.id, sr.id)
                        sr.save()
                    else:
                        result['msg'] = '兑现失败'
                        store.score = old_score
                        store.price = old_money
                        store.save()
                except:
                    result['msg'] = '系统错误'
            else:
                result['msg'] = '兑换错误'
        else:
            result['msg'] = '兑现积分小于最低兑现积分或积分不足'
        self.write(simplejson.dumps(result))


@route(r'/mobile/scorerecord', name='mobile_score_record')  # 积分明细
class MobileScoreRecordHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/scorerecord 09. 积分明细
    @apiDescription 积分明细

    @apiHeader {String} token 用户登录凭证
    @apiParam {String} index 分页

    @apiSampleRequest /mobile/scorerecord
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        index = int(self.get_argument('index', 1))
        store = self.get_user().store
        srs = ScoreRecord.select().where(ScoreRecord.store == store).\
            order_by(ScoreRecord.created.desc()).paginate(index, setting.MOBILE_PAGESIZE)
        for sr in srs:
            if sr.status == 1:
                result['data'].append({
                    'orderNum': sr.ordernum,
                    'type': sr.type,
                    'process_type': sr.process_type,
                    'log': sr.process_log,
                    'score': sr.score,
                    'date': time.strftime('%Y-%m-%d %H:%M%S', time.localtime(sr.created))
                })
        result['flag'] = 1

        self.write(simplejson.dumps(result))


# ----------------------------------------------------资金--------------------------------------------------------------
@route(r'/mobile/fund', name='mobile_fund')  # 资金入口
class MobileFundHandler(MobileBaseHandler):
    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {get} /mobile/fund 01. 资金入口
    @apiDescription 资金入口

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/fund
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        store = self.get_user().store
        result['data']['price'] = store.price
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/fundrecharge', name='mobile_recharge')  # 资金充值
class MobileFundRechargeHandler(MobileBaseHandler):
    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {get} /mobile/fundrecharge 02. 资金充值
    @apiDescription 资金充值

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/fundrecharge
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        user = self.get_user()
        payment = int(self.get_argument('payment', 0))
        price = float(self.get_argument('price', 0.0))
        order_num = ('U%sR%s'%(user.id, str(time.time())[1:10])).encode('utf-8')

        result['data']['payment'] = payment
        if payment == 1:  # 1支付宝  2微信 3银联
            # pay_info = alipay.get_alipay_string(price, u'车装甲充值', u'车装甲充值', order_num, True)
            pay_info = alipay_web_app.get_pay_url(order_num.encode('utf-8'), u'车装甲充值', str(price), True)
            if len(pay_info) > 0:
                result['data']['pay_info'] = pay_info
                result['flag'] = 1
                result['msg'] = u'充值完成'
            else:
                result['data']['pay_info'] = ''
        elif payment == 2:
            pay_info = UnifiedOrder_pub(isCZ=True).getPrepayId(order_num, u'车装甲充值', int(price * 100))
            result['data']['pay_info'] = pay_info
            result['flag'] = 1
            result['msg'] = u'充值完成'
        elif payment == 3:
            pay_info = Trade(isCZ=True).trade(order_num, price)
            result['data']['pay_info'] = pay_info
            result['flag'] = 1
            result['msg'] = u'充值完成'
        else:
            result['data']['pay_info'] = ''
            result['msg'] = u'传入参数错误'

        self.write(simplejson.dumps(result))


@route(r'/mobile/withdrawcash', name='mobile_withdraw_cash')  # 提现
class MobileWithdrawCashHandler(MobileBaseHandler):
    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {get} /mobile/withdrawcash 03. 提现
    @apiDescription 提现
    @apiHeader {String} token 用户登录凭证
    @apiSampleRequest /mobile/withdrawcash
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        store = self.get_user().store
        store_bank_accounts = StoreBankAccount.select().where(StoreBankAccount.store == store).order_by(StoreBankAccount.is_default.desc())
        result['data']['totalprice'] = store.price
        result['data']['withdrawline'] = 100
        result['data']['items'] = []
        for bank_account in store_bank_accounts:
            result['flag'] = 1
            if bank_account.account_type == 0:
                url = 'http://img.520czj.com/image/2017/07/04/server1_20170704150606yqeYZlaxsFBmPnkzGVIWuwgO.jpg'
                for k, v in setting.bank_en.items():
                    if v.find(bank_account.bank_name) >= 0:
                        url = 'https://apimg.alipay.com/combo.png?d=cashier&t=%s' % k
                result['data']['items'].append({
                    'bank_id': bank_account.id,
                    'account_type': bank_account.account_type,
                    'bank_account': bank_account.bank_account,
                    'bank_name': bank_account.bank_name,
                    'bank_pic': url
                })
            else:
                result['data']['items'].append({
                    'bank_id': bank_account.id,
                    'account_type': bank_account.account_type,
                    'bank_account': bank_account.alipay_account,
                    'bank_name': u'支付宝',
                    'bank_pic': 'http://img.hb.aicdn.com/f36700ea3039da9f49d23c11ebf1be1aec12996a439da-5HoGoW_fw658'
                })
        else:
            result['flag'] = 1
            result['msg'] = u'无可用提现账户'

        self.write(simplejson.dumps(result))

    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/withdrawcash 04. 提现
    @apiDescription 提现
    @apiHeader {String} token 用户登录凭证
    @apiParam {Int} money 金额
    @apiParam {Int} bank_id 银行卡ID
    @apiParam {Int} account_type 0银联 1支付宝
    @apiSampleRequest /mobile/withdrawcash
    """
    def post(self):
        result = {'flag': 0, 'msg': '', "data": []}
        user = self.get_user()
        store = user.store
        money = float(self.get_body_argument('money', None))
        bank_id = self.get_body_argument('bank_id', None)
        account_type = int(self.get_body_argument('account_type', 0))
        try:
            if money and bank_id:
                if money <= store.price:
                    now = int(time.time())
                    store.price -= money
                    s = StoreBankAccount.get(id=bank_id)
                    result['flag'] = 1
                    if account_type == 0:    # 银联
                        account_truename = s.bank_truename
                        account_account = s.bank_account
                        account_name = s.bank_name
                        MoneyRecord.create(user=user, store=user.store, process_type=2,  type=1,process_message='提现',process_log='提现',
                                           out_account_type=account_type, out_account_truename=account_truename,
                                           out_account_account=account_account, out_account_name=account_name,
                                           money=money, status=0, apply_time=now)
                        store.save()
                    elif account_type == 1:    # 支付宝
                        account_truename = s.alipay_truename
                        account_account = s.alipay_account
                        MoneyRecord.create(user=user, store=user.store, type=1,process_type=2, process_message='提现',process_log='提现',
                                           out_account_type=account_type, out_account_truename=account_truename,
                                           out_account_account=account_account, money=money, status=0, apply_time=now)
                        store.save()
                    else:
                        result['msg'] = '目前仅支持银联与支付宝'
                else:
                    result['msg'] = '提现金额不足'
            else:
                result['msg'] = '参数有误'
        except Exception,e:
            result['flag'] = 0
        self.write(simplejson.dumps(result))


@route(r'/mobile/get_bank_message')  # 银行卡信息获取
class MobileBindBankCardHandler(MobileBaseHandler):
    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {get} /mobile/get_bank_message 04. 银行卡信息获取
    @apiDescription 银行卡信息获取
    @apiHeader {String} token 用户登录凭证
    @apiParam {String} bank_number 卡号
    @apiSampleRequest /mobile/get_bank_message
    """
    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': {}}
        bank_number = self.get_body_argument('bank_number', None)
        truename = self.get_body_argument('truename', None)
        if StoreBankAccount.check_bank(truename, bank_number):
            rows = BankCard.select().where(BankCard.card_bin == db.fn.LEFT(bank_number, BankCard.bin_digits))
            if rows.count() > 0:
                result['data'] = {
                    'id': rows[0].id,
                    'bank_name': rows[0].bank_name
                }
                result['flag'] = 1
            else:
                result['msg'] = u'未查找到该卡银行'
        else:
            result['msg'] = u'卡号或持卡人姓名不合法'
        self.write(simplejson.dumps(result))


@route(r'/mobile/bank_card')  # 银行卡列表、绑定银行卡
class MobileBindBankCardHandler(MobileBaseHandler):
    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {get} /mobile/bank_card 05. 银行卡列表
    @apiDescription 银行卡列表
    @apiHeader {String} token 用户登录凭证
    @apiSampleRequest /mobile/bank_card
    """
    @require_auth
    def get(self):
        result = {'flag': 1, 'msg': '', 'data': []}
        store = self.get_user().store
        sbas = StoreBankAccount.select().where((StoreBankAccount.store == store) & (StoreBankAccount.account_type == 0))
        for sba in sbas:
            result['data'].append({
                'bank_id': sba.id,
                'bank_name': sba.bank_name if sba.bank_name else '',
                'bank_truename': sba.bank_truename if sba.bank_truename else '',
                'bank_account': '%s****%s'%(sba.bank_account[:5], sba.bank_account[-5:]) if sba.bank_account else '',
                'bank_branch_name': sba.bank_branch_name if sba.bank_branch_name else '',
                'bank_pic': 'http://img.520czj.com/image/bank_pic/yinlian.png'
            })
        self.write(simplejson.dumps(result))

    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {post} /mobile/bank_card 06. 绑定银行卡
    @apiDescription 绑定银行卡
    @apiHeader {String} token 用户登录凭证
    @apiParam {String} is_delete 是否删除 0否 1是
    @apiParam {String} bank_id 删除的银行卡ID
    @apiParam {String} bank_name 银行名
    @apiParam {String} bank_branch_name 支行名
    @apiParam {String} bank_truename 持卡人姓名
    @apiParam {String} bank_account 卡号
    @apiParam {String} vcode 验证码
    @apiSampleRequest /mobile/bank_card
    """
    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': {}}
        is_delete = self.get_body_argument('is_delete', None)
        bank_id = self.get_body_argument('bank_id', None)
        bank_name = self.get_body_argument('bank_name', None)
        truename = self.get_body_argument('bank_truename', None)
        bank_branch_name = self.get_body_argument('bank_branch_name', None)
        account = self.get_body_argument('bank_account', None)
        vcode = self.get_body_argument('vcode', None)

        store = self.get_user().store
        if is_delete == '1':
            sba = StoreBankAccount().delete().where(StoreBankAccount.id == bank_id).execute()
            if sba:
                result['flag'] = 1
                result['msg'] = u'删除成功'
            else:
                result['msg'] = u'未找到该银行卡'
        elif not VCode.check_vcode(store.mobile, vcode, 4):
            result['msg'] = u'请输入正确的验证码'
        elif bank_name and truename and account:
            if not StoreBankAccount.check_bank(truename, account):
                result['msg'] = u'银行卡号或姓名不合法'
                self.write(simplejson.dumps(result))
                return
            sba = StoreBankAccount()
            if StoreBankAccount.select().where((StoreBankAccount.is_default == 1) & (StoreBankAccount.store == store)).count() > 0:
                sba.is_default = 0
            else:
                sba.is_default = 1
            sba.store = store
            sba.bank_truename = truename
            sba.bank_account = account
            sba.bank_name = bank_name
            sba.bank_branch_name = bank_branch_name
            sba.save()
            result['flag'] = 1
            result['msg'] = u'绑定银行卡成功'
        else:
            result['msg'] = u'参数有误'
        self.write(simplejson.dumps(result))


@route(r'/mobile/bind_alipay')  # 绑定/修改支付宝
class MobileBindAlipayHandler(MobileBaseHandler):
    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {get} /mobile/bind_alipay 07. 绑定/修改支付宝
    @apiDescription 绑定/修改支付宝
    @apiHeader {String} token 用户登录凭证
    @apiSampleRequest /mobile/bind_alipay
    """
    @require_auth
    def get(self):
        result = {'flag': 1, 'msg': '', 'data': {'bank_id': '', 'alipay_truename':'', 'alipay_account': ''}}
        store = self.get_user().store
        sbas = StoreBankAccount.select().where((StoreBankAccount.store == store) & (StoreBankAccount.account_type == 1))
        if sbas.count() > 0:
            sba = sbas[0]
            result['data']['alipay_truename'] = sba.alipay_truename
            result['data']['alipay_account'] = sba.alipay_account

        self.write(simplejson.dumps(result))

    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {post} /mobile/bind_alipay 08. 绑定/修改支付宝
    @apiDescription 绑定/修改支付宝
    @apiHeader {String} token 用户登录凭证
    @apiParam {String} alipay_truename 支付宝主人姓名
    @apiParam {String} alipay_account 支付宝账号
    @apiParam {String} vcode 验证码
    @apiSampleRequest /mobile/bind_alipay
    """
    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': {}}
        alipay_truename = self.get_body_argument('alipay_truename', None)
        alipay_account = self.get_body_argument('alipay_account', None)
        vcode = self.get_body_argument('vcode', None)
        store = self.get_user().store
        if not VCode.check_vcode(store.mobile, vcode, 4):
            result['msg'] = u'请输入正确的验证码'
        elif alipay_truename and alipay_account:
            sbas = StoreBankAccount.select().where((StoreBankAccount.account_type == 1) & (StoreBankAccount.store == store))
            if sbas.count() > 0:
                sbas[0].alipay_truename = alipay_truename
                sbas[0].alipay_account = alipay_account
                sbas[0].account_type = 1
                sbas[0].save()
                result['flag'] = 1
                result['msg'] = u'修改支付宝成功'
            elif StoreBankAccount.check_alipay(alipay_truename, alipay_account):
                sba = StoreBankAccount()
                sba.alipay_truename = alipay_truename
                sba.alipay_account = alipay_account
                sba.account_type = 1
                sba.store = store
                sba.is_default = 1
                sba.save()
                result['flag'] = 1
                result['msg'] = u'绑定支付宝成功'
            else:
                result['msg'] = u'支付宝账号或支付宝主人姓名不合法'
        else:
            result['msg'] = u'参数有误'

        self.write(simplejson.dumps(result))


@route(r'/mobile/moneyrecord')  # 收支明细
class MobileMoneyRecordHandler(MobileBaseHandler):
    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {get} /mobile/moneyrecord 09. 收支明细
    @apiDescription 绑定/修改支付宝
    @apiHeader {String} token 用户登录凭证
    @apiParam {String} process_type 1入账 2出账 不传则全部
    @apiParam {String} index 分页页数
    @apiSampleRequest /mobile/moneyrecord
    """
    @require_auth
    def get(self):
        result = {'flag': 1, 'msg': '', 'data': []}
        store = self.get_user().store
        process_type = self.get_argument('process_type', None)
        index = int(self.get_argument('index', 1))

        ft = (MoneyRecord.store == store)
        if process_type:
            ft &= (MoneyRecord.process_type == int(process_type))
        money_records = MoneyRecord.select().where(ft).order_by(MoneyRecord.id.desc())
        money_records = money_records.paginate(index, setting.MOBILE_PAGESIZE)
        for record in money_records:
            result['data'].append({
                'record_id': record.id,
                'type': record.type,
                'process_type': record.process_type,
                'process_message': record.process_message,
                'in_num': record.in_num,
                'money': record.money,
                'status': record.status,
                'apply_time': time.strftime('%Y-%m-%d %H:%M', time.localtime(record.apply_time)),
                'processing_time': time.strftime('%Y-%m-%d %H:%M', time.localtime(record.processing_time))
            })
        self.write(simplejson.dumps(result))

    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {get} /mobile/moneyrecord 09. 收支明细
    @apiDescription 绑定/修改支付宝
    @apiHeader {String} token 用户登录凭证
    @apiParam {String} record_id 流水ID
    @apiSampleRequest /mobile/moneyrecord
    """
    @require_auth
    def post(self):
        result = {'flag': 1, 'msg': '', 'data': {}}
        record_id = self.get_body_argument('record_id', None)
        try:
            record = MoneyRecord.get(id=record_id)
            result['data']['process_type'] = record.process_type
            result['data']['process_message'] = record.process_message
            result['data']['in_num'] = record.in_num
            result['data']['money'] = record.money
            result['data']['apply_time'] = time.strftime('%Y-%m-%d %H:%M:S', time.localtime(record.apply_time))
            result['data']['processing_time'] = time.strftime('%Y-%m-%d %H:%M:S', time.localtime(record.processing_time))
            result['flag'] = 1
        except Exception, ex:
            result['msg'] = '系统错误'

        self.write(simplejson.dumps(result))


# ---------------------------------------------------商品管理-----------------------------------------------------------
@route(r'/mobile/myproducts', name='mobile_my_products')  # 商品管理/我的商品
class MobileMyProductsHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/myproducts 12. 商品管理/我的商品
    @apiDescription 商品管理/我的商品

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} area_code 地区code 逗号分隔，例： 00270001,00270002
    @apiParam {String} brand 品牌ID组合， 多选, 例：1,2,3
    @apiParam {Int} index 页数

    @apiSampleRequest /mobile/myproducts
    """
    @require_auth
    def get(self):
        result = {'flag': 1, 'msg': '', "data": {'products': [], 'brand': ''}}
        keyword = self.get_argument('keyword', '')
        area_code = self.get_argument('area_code', '')
        index = self.get_argument('index', '')
        index = int(index) if index else 1
        pagesize = setting.MOBILE_PAGESIZE
        brand = self.get_argument('brand', '')
        store = self.get_user().store

        ft = (ProductRelease.store == store)
        if keyword:
            keyword = '%'+keyword+'%'
            ft &= (Product.name % keyword)
        if area_code:
            area_code = area_code.strip(',').split(',')
            ft &= (StoreProductPrice.area_code << area_code)
        if brand:
            ft_brand = brand.strip(',').split(',')
            ft &= (Product.brand << ft_brand)
        product_releases = ProductRelease.select().\
            join(StoreProductPrice, on=(StoreProductPrice.product_release == ProductRelease.id)).\
            join(Product, on=(Product.id == ProductRelease.product)).where(ft)
        product_brand_list = []
        for product_release in product_releases:
            if product_release.product.brand.id not in product_brand_list:
                product_brand_list.append(product_release.product.brand.id)
                result['data']['brand'] = result['data']['brand'] + ',' + str(product_release.product.brand.id)
        result['data']['brand'] = result['data']['brand'].strip(',')
        prs = product_releases.paginate(index, pagesize)
        for product_release in prs:
            result['data']['products'].append({
                'pid': product_release.product.id,
                'prid': product_release.id,
                'name': product_release.product.name,
                'cover': product_release.product.cover,
                'attributes': [attributes.value for attributes in product_release.product.attributes],
                'area_price': [{
                                   'sppid': spp.id,
                                   'area': spp.area_code,
                                   'area_name': Area.get_detailed_address(spp.area_code),
                                   'price': spp.price,
                                   'active': spp.active
                               } for spp in product_release.area_prices]
            })
        self.write(simplejson.dumps(result))


@route(r'/mobile/filtermyproducts', name='mobile_filter_my_products')  # 我的商品筛选
class MobileFilterMyProductsHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/filtermyproducts 13.我的商品筛选
    @apiDescription 我的商品筛选

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/filtermyproducts
    """
    @require_auth
    def get(self):
        result = {'flag': 1, 'msg': '', "data": {}}
        store = self.get_user().store
        brand_list = []
        serve_area_list = []
        bids = []
        for p in store.products:
            if p.product.brand.id not in bids:
                bids.append(p.product.brand.id)
                brand_list.append({
                    'name': p.product.brand.name,
                    'id': p.product.brand.id
                })
        sas = []
        for service_area in store.service_areas:
            if service_area.id not in sas:
                sas.append(service_area.id)
                serve_area_list.append({
                    'name': service_area.area.name,
                    'area_code': service_area.area.code
                })
        result['data'] = {
            'brand': brand_list,
            'serve_area': serve_area_list
        }
        self.write(simplejson.dumps(result))


@route(r'/mobile/productrelease', name='mobile_product_release')  # 修改商品发布价格
class MobileProductReleaseHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/productrelease 14. 修改商品发布价格
    @apiDescription 修改商品发布价格

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} area_price 商品发布地区价格的json 例：[{'sppid':1, 'price':100, 'active': 1}]，active：0下架，1上架

    @apiSampleRequest /mobile/productrelease
    """
    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', "data": []}

        area_price = self.get_body_argument('area_price',None)
        if not area_price:
            result['msg'] = 'area_price 参数校验失败'
            self.write(result)
        args = simplejson.loads(area_price)
        try:
            for area_price in args:
                spp = StoreProductPrice.get(id=area_price['sppid'])
                spp.price = area_price['price']
                spp.active = area_price['active']
                spp.save()
            result['flag'] = 1
            result['msg'] = '修改成功'
        except:
            result['msg'] = '系统错误'
        self.write(simplejson.dumps(result))


# ---------------------------------------------------帮助中心-----------------------------------------------------------
@route(r'/mobile/lubepolicy', name='mobile_lube_policy')  # 返油政策
class MobileLubePolicyHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/lubepolicy 16. 返油政策
    @apiDescription 返油政策

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/lubepolicy
    """

    @require_auth
    def get(self):
        area_code = self.get_store_area_code()
        user = self.get_user()
        if user:
            store = user.store
            rows = SSILubePolicy.select().where((SSILubePolicy.store == store) &
                                            (SSILubePolicy.lube != ''))
        else:
            rows = []
        self.render('mobile/lube_protocol.html', insurances=rows, area_code=area_code)


@route(r'/mobile/lubepolicy_detail/(\d+)', name='mobile_lube_policy_detail')  # 返油政策详情
class MobileLubePolicyDetailHandler(MobileBaseHandler):
    def get(self, id):
        item = SSILubePolicy.get(id=id)
        json = '{"detail":'+item.lube+',"insurance": {"name":"'+item.insurance.name+\
               '","logo":"'+item.insurance.logo+'"}}'
        self.write(json)

# -----------------------------------------------------设置-------------------------------------------------------------
@route(r'/mobile/mysetting', name='mobile_my_setting')  # 账户信息
class MobileMySettingHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/mysetting 17. 账户信息
    @apiDescription 账户信息

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/mysetting
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        store = self.get_user().store

        result['data']['store_name'] = store.name
        result['data']['address'] = Area.get_detailed_address(store.area_code)
        result['data']['detailed_address'] = store.address
        result['data']['active'] = store.active
        result['data']['legal_person'] = store.legal_person
        result['data']['license_code'] = store.license_code
        result['data']['license_image'] = store.license_image
        result['data']['store_image'] = store.store_image
        result['flag'] = 1

        self.write(simplejson.dumps(result))


@route(r'/mobile/changepassword', name='mobile_change_password')  # 修改密码
class MobileChangePasswordHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/changepassword 18. 修改密码
    @apiDescription 修改密码

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} old_password  旧密码
    @apiParam {String} new_password  新密码

    @apiSampleRequest /mobile/changepassword
    """
    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        user = self.get_user()

        old_password = self.get_body_argument('old_password', None)
        new_password = self.get_body_argument('new_password', None)

        if user.check_password(old_password):
            if old_password == new_password:
                result['msg'] = u'新旧密码不能相同'
            else:
                user.password = user.create_password(new_password)
                user.save()
                result['flag'] = 1
                result['msg'] = u'修改成功'
        else:
            result['msg'] = u'原始密码不正确'
        self.write(simplejson.dumps(result))


@route(r'/mobile/forgotpassword', name='mobile_forgot_password')  # 忘记密码
class MobileForgotPasswordHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/forgotpassword 19. 忘记密码
    @apiDescription 忘记密码

    @apiParam {String} v_code  验证码
    @apiParam {String} new_password  新密码
     @apiParam {String} mobile  用户手机号

    @apiSampleRequest /mobile/fogotpassword
    """
    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        new_password = self.get_body_argument('new_password', None)
        v_code = self.get_body_argument('v_code', None)
        mobile = self.get_argument('mobile','')
        if not (new_password and v_code and mobile):
            self.write(simplejson.dumps(result))
            return

        user = User.get(User.mobile == mobile)
        flag = 1
        if v_code and new_password:
            VCode.delete().where(VCode.created < (int(time.time()) - 30 * 60)).execute()
            if VCode.select().where((VCode.mobile == user.mobile) & (VCode.vcode == v_code) & (VCode.flag == flag)).count() > 0:
                user.password = User.create_password(new_password)
                user.save()
                result['flag'] = 1
                result['msg'] = "修改成功"
            else:
                result['msg'] = "请输入正确的验证码"
        else:
            result['flag'] = 0
            result['msg'] = '请传入正确的验证码或密码'

        self.write(simplejson.dumps(result))


@route(r'/mobile/receiveraddress', name='mobile_receiver_address')  # 收货地址
class MobileReceiverAddressHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/receiveraddress 20. 收货地址
    @apiDescription 收货地址

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/receiveraddress
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        store = self.get_user().store
        for address in StoreAddress.select().where(StoreAddress.store == store).order_by(StoreAddress.is_default.desc()):
            result['data'].append({
                'address_id': address.id,
                'province': address.province,
                'city': address.city,
                'district': address.region,
                'address': address.address,
                'receiver': address.name,
                'mobile': address.mobile,
                'is_default': address.is_default,
                'create_by': address.create_by.id
            })
        result['flag'] = 1
        self.write(simplejson.dumps(result))

    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/receiveraddress 20. 修改收货地址
    @apiDescription 修改收货地址

    @apiHeader {String} token 用户登录凭证
    @apiParam {Int} store_address_id 门店收货地址ID（创建新收货地址时不用传）
    @apiParam {String} receiver 收货人姓名
    @apiParam {String} mobile 收货人手机号
    @apiParam {String} province 省
    @apiParam {String} city 市
    @apiParam {String} district 区
    @apiParam {String} address 详细地址
    @apiParam {Int} is_default 是否为默认收货地址 0否，1是

    @apiSampleRequest /mobile/receiveraddress
    """
    @require_auth
    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        user = self.get_user()
        store_address_id = self.get_body_argument('store_address_id', None)
        receiver = self.get_body_argument('receiver', None)
        mobile = self.get_body_argument('mobile', None)
        province = self.get_body_argument('province', None)
        city = self.get_body_argument('city', None)
        region = self.get_body_argument('district', None)
        address = self.get_body_argument('address', None)
        is_default = int(self.get_body_argument('is_default', 0))
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
            result['msg'] = u'修改成功'
        else:
            StoreAddress.create(store=user.store, province=province, city=city, region=region, address=address,
                                name=receiver, mobile=mobile, is_default=is_default, create_by=user, created=created)
            result['msg'] = u'创建成功'

        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/deleteaddress',name='mobile_delete_receiver_address')  # 删除收货地址
class MobileDeleteAddressHandler(MobileBaseHandler):
    @require_auth
    def post(self):
        user = self.get_user()
        store_address_id = self.get_body_argument('store_address_id', None)
        result = {'flag': 0, 'msg': '', "data": {}}
        if user and store_address_id:
            query = StoreAddress.delete().where(StoreAddress.id == store_address_id)
            query.execute()
            result['flag'] = 1
        else:
            result['msg'] = u'传入参数异常'
        self.write(simplejson.dumps(result))


@route(r'/mobile/feedback', name='mobile_my_feedback')  # 意见反馈
class MobileFeedbackHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/feedback 22. 意见反馈
    @apiDescription 意见反馈

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} suggest 用户建议
    @apiParam {String} img 图片URL

    @apiSampleRequest /mobile/feedback
    """
    @require_auth
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        user = self.get_user()
        suggest = self.get_argument('suggest', None)
        img = self.get_argument('img', None)
        if suggest or img:
            Feedback.create(user=user, suggest=suggest, img=img)
            result['flag'] = 1
        else:
            result['msg'] = '请输入您的意见或图片'

        self.write(simplejson.dumps(result))


@route(r'/mobile/update/(\S+)', name='mobile_verison')    # 手机端程序更新
class MobileVersionHandler(MobileBaseHandler):
    """
        @apiGroup mine
        @apiVersion 1.0.0
        @api {get} /mobile/update 22. 手机端程序更新
        @apiDescription 手机端程序更新:需要客户端类型

        @apiSampleRequest /mobile/update/
        """
    def get(self, client):
        order_str = MobileUpdate.updatedtime.desc()
        ft = (MobileUpdate.client == client)
        q = MobileUpdate.select().where(ft)
        lists = q.order_by(order_str).limit(1)
        result = {'version': '', 'baseUrl': '', 'isForce': 'false', 'flag':0, 'releaseNotes':''}
        try:
            logging.info(lists.count())
            if lists.count()>0:
                update = lists[0]
                result['version'] = update.version
                result['isForce'] = update.isForce
                result['releaseNotes'] = update.instruction
                if update.client == 'android_b' or update.client == 'android_c':
                    result['baseUrl'] = 'http://img.520czj.com' + update.path
                result['flag'] = 1
        except Exception, e:
            logging.info('Error: mobile/update/%s %s'%(client, e.message))
        self.write(simplejson.dumps(result))


# ----------------------------------------代理入口---------------------------------------------------
@route(r'/mobile/sales_agent', name='mobile_sales_agent')  # 下线页
class MobileToolsHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/sales_agent 12. 下线页面
    @apiDescription 下线页面,返回html代码

    @apiSampleRequest /mobile/sales_agent
    """
    def get_access_token(self):
        self.weixin_app_id = 'wxf23313db028ab4bc'
        self.weixin_secret = '8d75a7fa77dc0e5b2dc3c6dd551d87d6'
        self.url_access_token = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (
        self.weixin_app_id, self.weixin_secret)
        return simplejson.loads(urllib2.urlopen(self.url_access_token).read())["access_token"]

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

    def get(self):
        platform = self.get_argument('platform', 'android')
        user = self.get_user()
        if user:
            linkurl = self.create_url(user.id)
            imgurl = 'http://img.520czj.com/image/2017/06/29/server1_20170629170424FMnqzTtESLpuvbZQUjVdYkRA.png'
            title = '车装甲，人人卖车险'
            desc='正文描述......'
            token = user.token
        else:
            linkurl = ''
            imgurl = ''
            title = ''
            desc = ''
            token = ''
        self.render('mobile/sales_agent.html',token=token,
                    linkurl=linkurl,imgurl=imgurl,title=title,
                    desc=desc, platform=platform)

@route(r'/mobile/get_sales_agent', name='mobile_get_sales_agent')  # 下线api
class MobileToolsHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/get_sales_agent 12. 下线api
    @apiDescription 下线api

    @apiSampleRequest /mobile/get_sales_agent
    """

    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        begin_date  = self.get_argument('begin_date',None)
        end_date = self.get_argument('end_date',None)
        index = self.get_argument('index',None)
        token = self.get_argument('token',None)
        sort_type = self.get_argument('sort_type','orders')
        sort_value = self.get_argument('sort_value','desc')
        if not (index and token):
            result['flag'] = 1
            self.write(simplejson.dumps(result))
            return
        reverse = True
        if sort_value=='asc':
            reverse = False

        store = User.get(token=token).store
        index  = int(index) if index else 1
        ft = User.role.contains('W') & (InsuranceOrder.status << [2,3]) & (User.store == store.id)
        fts = None
        fte = None
        if begin_date and end_date:
            begin_date = time.strptime(begin_date+" 00:00:00", "%Y-%m-%d %H:%M:%S")
            fts = (InsuranceOrder.ordered >= time.mktime(begin_date))
            end_date = time.strptime((end_date + " 23:59:59"), "%Y-%m-%d %H:%M:%S")
            fte = (InsuranceOrder.ordered < time.mktime(end_date))
            ft &= fts
            ft &= fte
        agent = {}
        userlist = User.select().where(User.role.contains('W'),User.store == store.id,~User.role.contains('1'),~User.role.contains('A'))
        for u in userlist:
            agent[u.id] = {
                'id':u.id,
                'mobile':u.mobile,
                'orders':0,
                'total_price':0.0
            }
        users = User.select(User.id.alias('uid'),
                            User.mobile.alias('umobile'),
                            fn.count(InsuranceOrder.id).alias('orders'),
                            fn.sum(InsuranceOrderPrice.total_price).alias('total_price')). \
            join(InsuranceOrder,on=(InsuranceOrder.user == User.id)). \
            join(InsuranceOrderPrice,on=(InsuranceOrder.current_order_price == InsuranceOrderPrice.id)). \
            where(ft).group_by(User.mobile). \
            tuples()

        for uid,umobile,orders,total_price in users:
            if uid in agent.keys():
                agent[uid]['orders'] = orders
                agent[uid]['total_price'] = round(total_price,2)
        data = agent.values()

        if sort_type=='orders':
            data.sort(key=lambda x:x['orders'],reverse=reverse)
        elif sort_type=='total_price':
            data.sort(key=lambda x:x['total_price'], reverse=reverse)
        result['flag'] = 1
        result['data'] = data[(index-1)*setting.MOBILE_PAGESIZE:index*setting.MOBILE_PAGESIZE]

        self.write(simplejson.dumps(result))


# ----------------------------------------优惠券---------------------------------------------------
@route(r'/mobile/saver_tickets', name='mobile_saver_tickets')  # 门店端 优惠券列表
class SaverTicketHandler(MobileBaseHandler):
    """
    @apiGroup app
    @apiVersion 1.0.0
    @api {get} /mobile/saver_tickets 12. 门店端 优惠券列表
    @apiDescription 门店端 优惠券列表

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/saver_tickets
    """
    # @require_auth
    def get(self):
        store = self.get_user().store
        tickets = []
        for ticket in store.store_service_cards:
            if ticket.status == 2:
                tickets.append({
                    'type': ticket.type,
                    'name': ticket.name,
                    'desc': ticket.desc,
                    'deal_time': ticket.deal_time,
                    'user': ticket.user.truename
                })

        self.render('mobile/store_saver_tickets.html', tickets=tickets)


