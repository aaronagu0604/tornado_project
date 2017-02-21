#!/usr/bin/env python
# coding=utf8

import logging
import setting
import simplejson
from lib.route import route
from model import *
from handler import MobileBaseHandler, MobileAuthHandler


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
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

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


# ----------------------------------------------------订单--------------------------------------------------------------
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
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

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


@route(r'/mobile/insuranceorder', name='mobile_insurance_order')  # 保险订单
class MobileInsuranceOrderHandler(MobileAuthHandler):
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

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        type = self.get_argument("type", 'all')
        index = int(self.get_argument('index', 1))
        store = self.get_user().store
        ft = (InsuranceOrder.store == store)
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
        else:
            result['msg'] = '输入参数有误'
            return
        ios = InsuranceOrder.select().where(ft).order_by(InsuranceOrder.ordered).paginate(index, setting.MOBILE_PAGESIZE)
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
        result['flag'] = 1
        self.write(simplejson.dumps(result))


# ----------------------------------------------------积分--------------------------------------------------------------
@route(r'/mobile/score', name='mobile_score')  # 积分入口
class MobileScoreHandler(MobileAuthHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/score 05. 普通商品售出订单
    @apiDescription 普通商品售出订单

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/score
    """

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        store = self.get_user().store
        result['data']['score'] = store.score
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/scoreStore', name='mobile_score_store')  # 积分商城
class MobileScoreStore(MobileAuthHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/scoreStore 06. 积分商城
    @apiDescription 积分商城

    @apiHeader {String} token 用户登录凭证

    @apiParam {Int} index 每页起始个数

    @apiSampleRequest /mobile/scoreStore
    """
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

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
                'storeName': spp.product_release.store.name
            })
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/scorecash', name='mobile_score_cash')  # 积分兑现
class MobileScoreCashHandler(MobileAuthHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/scorecash 07. 积分兑现
    @apiDescription 积分兑现

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/scorecash
    """

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

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

    def post(self, uid):
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
            sysCalculateMoney = score * setting.CASH_MIN_MONEY
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
            result['msg'] = '提现积分小于最低提现积分或积分不足'
        self.write(simplejson.dumps(result))


@route(r'/mobile/scorerecord', name='mobile_score_record')  # 积分明细
class MobileScoreRecordHandler(MobileAuthHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/scorerecord 09. 积分明细
    @apiDescription 积分明细

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/scorerecord
    """

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        store = self.get_user().store
        for sr in store.score_records:
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
class MobileFundHandler(MobileAuthHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/fund 10. 资金入口
    @apiDescription 资金入口

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/fund
    """

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        store = self.get_user().store
        result['data']['price'] = store.price
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/fundrecharge', name='mobile_recharge')  # 资金充值
class MobileFundRechargeHandler(MobileAuthHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/fundrecharge 11. 资金充值
    @apiDescription 资金充值

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/fundrecharge
    """

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        store = self.get_user().store
        result['data']['price'] = store.price
        result['flag'] = 1
        self.write(simplejson.dumps(result))









