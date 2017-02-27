#!/usr/bin/env python
# coding=utf8

import logging
import setting
import simplejson
from lib.route import route
from model import *
from handler import MobileBaseHandler
import os
from PIL import Image, ImageDraw, ImageFont
from lib.payment.alipay import get_pay_url
from lib.payment.wxPay import UnifiedOrder_pub
from lib.payment.upay import Trade
from handler import require_auth


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
            result['data']['active'] = user.store.active
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

    def get(self):
        user = self.get_user()
        result = {'flag': 0, 'msg': '', "data": []}
        try:
            storeName = u'店铺：' + user.store.name
            addr = u'地址：' + Area.get_detailed_address(user.store.area_code) + user.store.address
            addr2 = ''
            mobile = u'电话：'+user.mobile
            now = str(time.time())[:10]
            for pop in setting.popularizePIC:
                area_limits = 0
                for area_code in pop['area_code'].split(','):
                    if user.store.area_code.startswith(area_code):
                        area_limits = 1
                if len(addr) > pop['addr2tab']:
                    addr1 = addr[:pop['addr2tab']]
                    addr2 = addr[pop['addr2tab']:]
                else:
                    addr1 = addr
                if area_limits == 1:
                    picPath = self.act_insurance(pop, user.id, storeName, addr1, addr2, mobile, now)
                    result['data'].append(picPath)
                    result['flag'] = 1

        except Exception, e:
            result['msg'] = u'生成图片错误'
        self.write(simplejson.dumps(result))


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
class MobileScoreHandler(MobileBaseHandler):
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
class MobileScoreCashHandler(MobileBaseHandler):
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
class MobileFundHandler(MobileBaseHandler):
    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {get} /mobile/fund 01. 资金入口
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
class MobileFundRechargeHandler(MobileBaseHandler):
    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {get} /mobile/fundrecharge 02. 资金充值
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
        user = self.get_user()
        payment = int(self.get_argument('payment', 0))
        price = int(self.get_argument('price', 0))
        order_num = 'U%sR%s'%(user.id, str(time.time())[1:10]).encode('utf-8')

        result['data']['payment'] = payment
        if payment == 1:  # 1支付宝  2微信 3银联
            response_url = get_pay_url(order_num, u'车装甲商品', price, True)
            if len(response_url) > 0:
                result['data']['pay_info'] = response_url
                result['flag'] = 1
                result['msg'] = '充值完成'
            else:
                result['data']['pay_info'] = ''
        elif payment == 2:
            pay_info = UnifiedOrder_pub(isCZ=True).getPrepayId(order_num, u'车装甲商品', int(price * 100))
            result['data']['pay_info'] = pay_info
            result['flag'] = 1
            result['msg'] = '充值完成'
        elif payment == 3:
            pay_info = Trade(isCZ=True).trade(order_num, price)
            result['data']['pay_info'] = pay_info
            result['flag'] = 1
            result['msg'] = '充值完成'
        else:
            result['data']['pay_info'] = ''
            result['msg'] = '传入参数错误'

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

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        store = self.get_user().store
        store_bank_accounts = StoreBankAccount.select().where(StoreBankAccount.store==store,
                                  StoreBankAccount.account_type==0).order_by(StoreBankAccount.is_default.desc())
        for bank_account in store_bank_accounts:
            result['data'].append({
                'bank_id': bank_account.id,
                'account_type': bank_account.account_type,
                'bank_account': bank_account.bank_account,
                'bank_name': bank_account.bank_name
            })

        self.write(simplejson.dumps(result))

    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/withdrawcash 04. 提现
    @apiDescription 提现
    @apiHeader {String} token 用户登录凭证
    @apiParam {Int} money 金额
    @apiParam {Int} bank_id 银行卡ID
    @apiSampleRequest /mobile/withdrawcash
    """
    def post(self):
        result = {'flag': 0, 'msg': '', "data": []}
        user = self.get_user()
        store = user.store
        money = self.get_body_argument('money', None)
        bank_id = self.get_body_argument('bank_id', None)
        account_type = int(self.get_body_argument('account_type', 0))
        if money and bank_id:
            if money <= store.price:
                now = int(time.time())
                store.price -= money
                s = StoreBankAccount.get(id=bank_id)
                if account_type == 0:
                    account_truename = s.bank_truename
                    account_account = s.bank_account
                    account_name = s.bank_name
                    MoneyRecord.create(user=user, store=user.store, process_type=1, process_log='提现',
                                       out_account_type=account_type, out_account_truename=account_truename,
                                       out_account_account=account_account, out_account_name=account_name,
                                       money=money, status=0, apply_time=now)
                elif account_type == 1:
                    account_truename = s.alipay_truename
                    account_account = s.alipay_account
                    MoneyRecord.create(user=user, store=user.store, process_type=1, process_log='提现',
                                       out_account_type=account_type, out_account_truename=account_truename,
                                       ut_account_account=account_account, money=money, status=0, apply_time=now)
                else:
                    result['msg'] = '目前仅支持银联与支付宝'
            else:
                result['msg'] = '提现金额不足'
        else:
            result['msg'] = '参数有误'

        self.write(simplejson.dumps(result))


@route(r'/mobile/get_bank_message')  # 绑定支付宝/银行卡
class MobileBindBankCardHandler(MobileAuthHandler):
    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {get} /mobile/bind_bank_card 04. 绑定支付宝/银行卡
    @apiDescription 绑定支付宝/银行卡
    @apiHeader {String} token 用户登录凭证
    @apiSampleRequest /mobile/bind_bank_card
    """
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self, *args, **kwargs):
        self.write()


@route(r'/mobile/bind_bank_card')  # 绑定支付宝/银行卡
class MobileBindBankCardHandler(MobileAuthHandler):
    """
    @apiGroup fund
    @apiVersion 1.0.0
    @api {get} /mobile/bind_bank_card 04. 绑定支付宝/银行卡
    @apiDescription 绑定支付宝/银行卡
    @apiHeader {String} token 用户登录凭证
    @apiSampleRequest /mobile/bind_bank_card
    """
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self, *args, **kwargs):

        self.write()


# ---------------------------------------------------商品管理-----------------------------------------------------------
@route(r'/mobile/myproducts', name='mobile_my_products')  # 商品管理/我的商品
class MobileMyProductsHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/myproducts 12. 商品管理/我的商品
    @apiDescription 商品管理/我的商品

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} keyword 关键字搜索
    @apiParam {String} area_code 地区code
    @apiParam {Int} category 分类ID
    @apiParam {Int} brand 品牌ID

    @apiSampleRequest /mobile/myproducts
    """

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        keyword = self.get_argument('keyword', None)
        area_code = self.get_argument('area_code', None)
        category = self.get_argument('category', None)
        brand = self.get_argument('brand', None)
        store = self.get_user().store

        ft = (ProductRelease.store==store)
        if keyword:
            keyword = '%'+keyword+'%'
            ft &= (Product.name % keyword)
        if area_code:
            ft &= (StoreProductPrice.area_code==area_code)
        if category:
            ft &= (Product.category==category)
        if brand:
            ft &= (Product.brand==brand)
        product_releases = ProductRelease.select().join(StoreProductPrice).where(ft)
        for product_release in product_releases:
            area_price = []
            for spp in product_release.area_prices:
                area_price.append({
                    'sppid': spp.id,
                    'area': spp.area_code,
                    'price': spp.price,
                    'active': spp.active
                })
            result['data'].append({
                'pid': product_release.product.id,
                'prid': product_release.id,
                'name': product_release.product.name,
                'cover': product_release.product.cover,
                'attributes': [attributes.value for attributes in product_release.product.attributes],
                'old_price': product_release.price,
                'area_price': area_price
            })
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/mobile/filtermyproducts', name='mobile_filter_my_products')  # 我的商品筛选
class MobileFilterMyProductsHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/filtermyproducts 13. 我的商品筛选
    @apiDescription 我的商品筛选

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/filtermyproducts
    """

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        store = self.get_user().store
        brand_list = []
        category_list = []
        serve_area_list = []
        for p in store.products:
            if p.brand.name not in brand_list:
                brand_list.append({
                    'name': p.brand.name,
                    'id': p.brand.id
                })
            if p.category.name not in category_list:
                category_list.append({
                    'name': p.category.name,
                    'id': p.category.id
                })
        for service_area in store.service_areas:
            serve_area_list.append({
                'name': service_area.area.name,
                'area_code': service_area.area_code
            })

        result['data'] = {
            'brand': brand_list,
            'category': category_list,
            'serve_area': serve_area_list
        }
        result['flag'] = 1
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

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': '', "data": []}
        args = simplejson.loads(self.get_body_argument('area_price'))
        try:
            for area_price in args['area_price']:
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
    # 一个地区多个保险公司返油政策相同 或 一个保险公司
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

    # 一个地区多个保险公司返油政策不同
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

    @require_auth
    def get(self):
        result = {
            'flag': 0,
            'msg': '',
            'data': {
                'iCompany': '',
                'presentToA': setting.presentToA,
                'remark': '',
                'presentToB': setting.presentToB,
                'type': []
            }
        }
        logging.info('-----1---')
        area_code = self.get_user().store.area_code
        result['data']['remark'] = setting.get_help_center_remark(area_code)
        area_code_lenth = len(area_code)
        if area_code_lenth == 12:
            rows = LubePolicy.select().where(LubePolicy.area_code==area_code).order_by(LubePolicy.sort, LubePolicy.sort2)
        if area_code_lenth == 8 or (area_code_lenth == 12 and rows.count() <= 0):
            rows = LubePolicy.select().where(LubePolicy.area_code == area_code[:8]).order_by(LubePolicy.sort, LubePolicy.sort2)
        if area_code_lenth == 4 or (area_code_lenth > 4 and rows.count() <= 0):
            rows = LubePolicy.select().where(LubePolicy.area_code == area_code[:12]).order_by(LubePolicy.sort, LubePolicy.sort2)
        logging.info('-----2---')
        if rows.count() > 0:
            logging.info('-----3---')
            iCompanyName = ''
            totalICname = []
            for row in rows:
                self.i_cname = row.iCompany not in totalICname
                if self.i_cname:
                    totalICname.append(row.iCompany)
                    iCompanyName += row.iCompany
            if len(totalICname) > 1:
                result = self.get_insurances_for_difI(rows, result, iCompanyName)
            else:
                result = self.get_insurances(rows, result)
                logging.info('-----4---')
            result['flag'] = 1
        else:
            result['msg'] = u'该地区的具体优惠政策请联系车装甲客服'
        logging.info('-----%s---'%result)
        self.write(simplejson.dumps(result))


# -----------------------------------------------------设置-------------------------------------------------------------
@route(r'/mobile/mysetting', name='mobile_my_setting')  # 我的设置
class MobileMySettingHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/mysetting 17. 我的设置
    @apiDescription 我的设置

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/mysetting
    """

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

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


@route(r'/mobile/changeloginpassword', name='mobile_change_login_password')  # 修改登录密码
class MobileChangeLoginPasswordHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/changeloginpassword 18. 修改登录密码
    @apiDescription 修改登录密码

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} old_password  旧密码
    @apiParam {String} new_password  新密码

    @apiSampleRequest /mobile/changeloginpassword
    """

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        user = self.get_user()

        old_password = self.get_body_argument('old_password', None)
        new_password = self.get_body_argument('new_password', None)

        if user.check_password(old_password):
            user.password = user.create_password(new_password)
            user.save()
            result['flag'] = 1
            result['msg'] = '修改成功'
        else:
            result['msg'] = '原始密码不正确'
        self.write(simplejson.dumps(result))


@route(r'/mobile/changepaypassword', name='mobile_change_pay_password')  # 修改支付密码
class MobileChangePayPasswordHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/changepaypassword 19. 修改支付密码
    @apiDescription 修改支付密码

    @apiHeader {String} token 用户登录凭证

    @apiParam {String} v_code  验证码
    @apiParam {String} new_password  新密码

    @apiSampleRequest /mobile/changepaypassword
    """

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        store = self.get_user().store
        new_password = self.get_body_argument('new_password', None)
        v_code = self.get_body_argument('v_code', None)
        flag = 1
        if v_code and new_password:
            VCode.delete().where(VCode.created < (int(time.time()) - 30 * 60)).execute()
            if VCode.select().where((VCode.mobile == store.mobile) & (VCode.v_code == v_code) & (VCode.flag == flag)).count() > 0:
                store.pay_password = User.create_password(new_password)
                store.save()
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

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        result = {'flag': 0, 'msg': '', "data": []}
        store = self.get_user().store
        for address in StoreAddress.select().where(StoreAddress.store==store).order_by(StoreAddress.is_default.desc()):
            result['data'].append({
                'address_id': address.id,
                'store_name': store.name,
                'province': address.province,
                'city': address.city,
                'district': address.region,
                'address': address.address,
                'receiver': address.name,
                'mobile': address.mobile,
                'is_default': address.is_default
            })
        result['flag'] = 1
        self.write(simplejson.dumps(result))

    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {post} /mobile/receiveraddress 20. 修改收货地址
    @apiDescription 修改收货地址

    @apiHeader {String} token 用户登录凭证
    @apiParam {Int} store_address_id 门店收货地址ID（仅创建新收货地址时不用传）
    @apiParam {Int} cancel_def_id 取消收货地址的ID（仅修改默认收货地址时传）
    @apiParam {String} receiver 收货人姓名
    @apiParam {String} mobile 收货人手机号
    @apiParam {String} province 省
    @apiParam {String} city 市
    @apiParam {String} district 区
    @apiParam {String} address 详细地址
    @apiParam {Int} is_default 是否为默认收货地址 0否，1是

    @apiSampleRequest /mobile/receiveraddress
    """
    def post(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        user = self.get_user()
        store_address_id = self.get_body_argument('store_address_id', None)
        cancel_def_id = self.get_body_argument('cancel_def_id', None)
        receiver = self.get_body_argument('receiver', None)
        mobile = self.get_body_argument('mobile', None)
        province = self.get_body_argument('province', None)
        city = self.get_body_argument('city', None)
        region = self.get_body_argument('district', None)
        address = self.get_body_argument('address', None)
        is_default = int(self.get_body_argument('is_default', 0))
        created = int(time.time())
        
        if cancel_def_id and store_address_id:
            store_address_cancel = StoreAddress.get(id=cancel_def_id)
            store_address_cancel.is_default = 0
            store_address_cancel.save()
            store_address_set = StoreAddress.get(id=store_address_id)
            store_address_set.is_default = 1
            store_address_set.save()
            result['msg'] = '修改成功'
        else:
            if is_default:
                for store_address in user.store.addresses:
                    if store_address.is_default:
                        store_address.is_default = 0
                        store_address.save()
            if store_address_id:
                sa = StoreAddress.get(id=store_address_id)
                sa.name = receiver
                sa.mobile = mobile
                sa.province = province
                sa.city = city
                sa.region = region
                sa.address = address
                sa.is_default = is_default
                sa.create_by = user
                sa.save()
                result['msg'] = '修改成功'
            else:
                StoreAddress.create(store=user.store, province=province, city=city, region=region, address=address,
                                    name=receiver, mobile=mobile, is_default=is_default, create_by=user, created=created)
                result['msg'] = '创建成功'

        result['flag'] = 1
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

    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

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







