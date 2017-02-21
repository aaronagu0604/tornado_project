#!/usr/bin/env python
# coding=utf8

import logging
import setting
import simplejson
from lib.route import route
from model import *
from handler import MobileBaseHandler, MobileAuthHandler


def productOrderSearch(ft, type, index):
    if type == 'all':  # 全部
        ft &= (SubOrder.status > -1) & (SubOrder.buyer_del == 0)
    elif type == 'unpay':  # 待付款订单
        ft &= (SubOrder.status == 0) & (SubOrder.buyer_del == 0)
    elif type == 'undispatch':  # 待发货
        ft &= (SubOrder.status == 1) & (SubOrder.buyer_del == 0)
    elif type == 'unreceipt':  # 待收货
        ft &= (Order.status == 2) & (SubOrder.buyer_del == 0)
    elif type == 'success':  # 交易完成/待评价
        ft &= (Order.status == 3) & (SubOrder.buyer_del == 0)
    elif type == 'delete':  # 删除
        ft &= ((Order.status == -1) | (SubOrder.buyer_del == 1))

    result = []
    sos = SubOrder.select().join(Order).where(ft).order_by(Order.ordered.desc()).paginate(index, setting.MOBILE_PAGESIZE)
    for so in sos:
        items = []
        for soi in so.items:
            items.append({
                'product': soi.product.name,
                'price': soi.store_product_price.price,
                'quantity': soi.quantity
            })
        result.append({
            'id': so.id,
            'status': so.status,
            'items': items,
            'ordered': time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(so.order.ordered)),
            'deadline': time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(so.order.ordered + setting.PRODUCT_ORDER_TIME_OUT))
        })
    return result


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
        user = self.get_user()
        if user is None:  # 未登录
            result['data']['store_name'] = ''
            result['data']['user_name'] = ''
            result['data']['store_type'] = ''
            result['data']['store_price'] = 0
            result['data']['store_score'] = 0
            result['data']['show_sale_orders'] = 1
            result['data']['show_buy_orders'] = 1
            result['data']['show_product_manager'] = 1
            result['data']['sale_orders'] = {}
            result['data']['sale_orders']['wait_pay'] = 0
            result['data']['sale_orders']['wait_send'] = 0
            result['data']['sale_orders']['wait_get'] = 0
            result['data']['sale_orders']['wait_comment'] = 0
            result['data']['sale_orders']['wait_pay_back'] = 0
            result['data']['buy_orders'] = {}
            result['data']['buy_orders']['wait_pay'] = 0
            result['data']['buy_orders']['wait_send'] = 0
            result['data']['buy_orders']['wait_get'] = 0
            result['data']['buy_orders']['wait_comment'] = 0
            result['data']['buy_orders']['wait_pay_back'] = 0
        else:  # 已登录
            result['data']['store_name'] = user.store.name
            result['data']['user_name'] = user.mobile

            result['data']['store_price'] = user.store.price
            result['data']['store_score'] = user.store.score
            if user.store.store_type == 1:
                result['data']['store_type'] = '服务商'
                result['data']['show_sale_orders'] = 1
                result['data']['show_buy_orders'] = 0
                result['data']['show_product_manager'] = 1
                result['data']['buy_orders'] = {}
                result['data']['buy_orders']['wait_pay'] = 0
                result['data']['buy_orders']['wait_send'] = 0
                result['data']['buy_orders']['wait_get'] = 0
                result['data']['buy_orders']['wait_comment'] = 0
                result['data']['buy_orders']['wait_pay_back'] = 0
                result['data']['sale_orders'] = {}
                result['data']['sale_orders']['wait_pay'] = 0
                result['data']['sale_orders']['wait_send'] = 0
                result['data']['sale_orders']['wait_get'] = 0
                result['data']['sale_orders']['wait_comment'] = 0
                result['data']['sale_orders']['wait_pay_back'] = 0
                # 查询子订单数据
                sale_orders = SubOrder.select(SubOrder.status, fn.Count(SubOrder.id).alias('count')). \
                    where(SubOrder.status > -1, SubOrder.saler_del == 0, SubOrder.saler_store == user.store).\
                    group_by(SubOrder.status).tuples()
                for status, count in sale_orders:
                    if status == 0:
                        result['data']['sale_orders']['wait_pay'] += count
                    elif status == 1:
                        result['data']['sale_orders']['wait_send'] += count
                    elif status == 2:
                        result['data']['sale_orders']['wait_get'] += count
                    elif status == 3:
                        result['data']['sale_orders']['wait_comment'] += count
                    elif status == 5 or status == 6:
                        result['data']['sale_orders']['wait_pay_back'] += count
            elif user.store.store_type == 2:
                result['data']['store_type'] = '门店'
                result['data']['show_sale_orders'] = 0
                result['data']['show_buy_orders'] = 1
                result['data']['show_product_manager'] = 0
                result['data']['sale_orders'] = {}
                result['data']['sale_orders']['wait_pay'] = 0
                result['data']['sale_orders']['wait_send'] = 0
                result['data']['sale_orders']['wait_get'] = 0
                result['data']['sale_orders']['wait_comment'] = 0
                result['data']['sale_orders']['wait_pay_back'] = 0
                result['data']['buy_orders'] = {}
                result['data']['buy_orders']['wait_pay'] = 0
                result['data']['buy_orders']['wait_send'] = 0
                result['data']['buy_orders']['wait_get'] = 0
                result['data']['buy_orders']['wait_comment'] = 0
                result['data']['buy_orders']['wait_pay_back'] = 0
                # 查询子订单数据
                buy_orders = SubOrder.select(SubOrder.status, fn.Count(SubOrder.id).alias('count')). \
                    where(SubOrder.status > -1, SubOrder.buyer_del == 0, SubOrder.buyer_store == user.store).\
                    group_by(SubOrder.status).tuples()
                for status, count in buy_orders:
                    if status == 0:
                        result['data']['buy_orders']['wait_pay'] += count
                    elif status == 1:
                        result['data']['buy_orders']['wait_send'] += count
                    elif status == 2:
                        result['data']['buy_orders']['wait_get'] += count
                    elif status == 3:
                        result['data']['buy_orders']['wait_comment'] += count
                    elif status == 5 or status == 6:
                        result['data']['buy_orders']['wait_pay_back'] += count
        self.write(simplejson.dumps(result))
        self.finish()


@route(r'/mobile/purchaseorder ', name='mobile_purchase_order')  # 普通商品采购订单
class MobilPurchaseOrderHandler(MobileAuthHandler):
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
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def delete_timeOut_order(self, user):
        timeOut = int(time.localtime()) - setting.PRODUCT_ORDER_TIME_OUT
        ft = (Order.user == user) & (SubOrder.status > -1) & (Order.ordered < timeOut)
        sos = SubOrder.select().join(Order).where(ft)
        for so in sos:
            so.status = -1
            so.fail_reason = '超时未支付'
            so.save()

    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        type = self.get_argument("type", 'all')
        index = int(self.get_argument('index', 1))
        user = self.get_user()
        # 先删除超时订单
        # self.delete_timeOut_order(user)
        ft = (Order.user == user)
        try:
            result['data'] = productOrderSearch(ft, type, index)
            result['flag'] = 1
        except Exception:
            result['msg'] = '系统错误'
        self.write(simplejson.dumps(result))


@route(r'/mobile/sellorder', name='mobile_sell_order')  # 普通商品售出订单
class MobileSellOrderHandler(MobileAuthHandler):
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
    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        type = self.get_argument("type", 'all')
        index = int(self.get_argument('index', 1))
        store = self.get_user().store
        ft = (SubOrder.saler_store == store)
        try:
            result['data'] = productOrderSearch(ft, type, index)
            result['flag'] = 1
        except Exception:
            result['msg'] = '系统错误'
        self.write(simplejson.dumps(result))


@route(r'/mobile/insuranceorder', name='mobile_insurance_order')  # 普通商品售出订单
class MobileInsuranceOrderHandler(MobileAuthHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/sellorder 03. 普通商品售出订单
    @apiDescription 普通商品售出订单

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} type 订单状态类型 all全部，unverify待确认，unpay待支付，paid付款完成，success已办理，post已邮寄， delete删除
    @apiParam {Int} index 每页起始个数

    @apiSampleRequest /mobile/sellorder
    """

    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        type = self.get_argument("type", 'all')
        index = int(self.get_argument('index', 1))
        store = self.get_user().store
        ft = (InsuranceOrder.saler_store == store)
        # 0待确认 1待付款 2付款完成 3已办理 4已邮寄 -1已删除(取消)
        if type == 'all':  # 全部
            ft &= (InsuranceOrder.status > -1) & (InsuranceOrder.user_del == 0)
        elif type == 'unverify':  # 待确认
            ft &= (InsuranceOrder.status == 0) & (InsuranceOrder.user_del == 0)
        elif type == 'unpay':  # 待付款
            ft &= (InsuranceOrder.status == 1) & (InsuranceOrder.user_del == 0)
        elif type == 'paid':  # 付款完成
            ft &= (InsuranceOrder.status == 2) & (InsuranceOrder.user_del == 0)
        elif type == 'success':  # 已办理
            ft &= (Order.status == 3) & (InsuranceOrder.user_del == 0)
        elif type == 'post':  # 已邮寄
            ft &= (Order.status == 4) & (InsuranceOrder.user_del == 0)
        elif type == 'delete':  # 删除
            ft &= ((Order.status == -1) | (InsuranceOrder.user_del == 1))

        ios = InsuranceOrder.select().where(ft).order_by(InsuranceOrder.ordered)
        for io in ios:
            result['data'].append({
                'id': io.id,
                'ordernum': io.ordernum,
                'iName': io.current_order_price.insurance.name,
                'status': io.status,
                'sName': io.store.name,
                'recipients': io.delivery_to,
                'recipientsTel': io.delivery_tel,
                'recipientsAddr': io.delivery_province+io.delivery_city+io.delivery_region+io.delivery_address,
                'price': io.current_order_price.total_price,
                'commission': io.gift_policy,
                'ordered': time.strftime('%Y-%m-%d %H:%M%S', time.localtime(io.ordered)),
                'deadline': time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(io.ordered + setting.INSURANCE_ORDER_TIME_OUT))
            })
        self.write(simplejson.dumps(result))









