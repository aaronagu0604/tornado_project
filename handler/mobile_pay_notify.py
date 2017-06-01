#!/usr/bin/env python
# coding=utf8

import logging

import simplejson
from tornado.web import RequestHandler

import setting
from lib.mqhelper import create_msg
from lib.payment.ali_app_pay import verify_alipay_request_sign
from lib.payment.alipay_web.core import notify_verify
from lib.payment.upay import Trade
from lib.payment.wxPay import Notify_pub
from lib.route import route
from model import *


# ------------------------------------------------第三方回调------------------------------------------------------------
# 修改订单状态
def change_order_status(ordernum, trade_no):
    is_insurance_order = False
    try:
        ordernum_list = ordernum.split('A')
        if len(ordernum_list) == 1:    # 订单（普通商品、保单）支付回调
            if 'I' in ordernum:    # 保单
                order = InsuranceOrder.get(ordernum=ordernum)
                order.change_status(2)
                is_insurance_order = True
            else:    # 普通商品订单
                order = Order.get(ordernum=ordernum)
                order.status = 1
                for sub_order in order.sub_orders:
                    sub_order.status = 1
                    sub_order.save()
            order.trade_no = trade_no
            order.pay_time = int(time.time())  # 支付时间
            order.save()
            return order, is_insurance_order
        elif len(ordernum_list) == 2:    # 保单补款回调
            ordernum_originally = ordernum_list[0]
            order = InsuranceOrder.get(ordernum=ordernum_originally)
            order.current_order_price.append_refund_status = 0
            order.current_order_price.total_price += order.current_order_price.append_refund_num
            order.current_order_price.save()
            return order, False
    except Exception, e:
        logging.info('Error: change order status error; ordernum %s,trade_no %s,log: %s' % (ordernum, trade_no, e.message))
        return None, is_insurance_order


# 保单支付成功短信
def send_new_insurance_order_msg(mobile, storeName, area_code, ordernum, iName, payment, LubeOrScore, summary, price):
        mobiles = setting.financeMobiles
        if payment == 1:
            paymentV = '支付宝'
        elif payment == 2:
            paymentV = '微信支付'
        elif payment == 3:
            paymentV = '银联支付'
        elif payment == 4:
            paymentV = '余额支付'
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


# 阿里支付手机端支付完成同步回调
@route(r'/mobile/alipay_callback', name='mobile_alipay_callback')
class MobileAlipayCallbackHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def get(self):
        self.write('')


# 支付宝支付完成后异步通知 支付宝回调 （APP支付）
@route('/mobile/alipay_notify', name='mobile_alipay_notify')
class MobileAlipayNotifyHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        msg = "fail"
        params = {}
        notify = PaymentNotify()
        notify.content = self.request.body
        notify.notify_time = int(time.time())
        notify.notify_type = 2
        notify.payment = 1
        notify.function_type = 1
        notify.save()
        ks = self.request.arguments.keys()
        for k in ks:
            params[k] = self.get_argument(k)
        ps = verify_alipay_request_sign(params)
        if ps:
            if ps['trade_status'].upper().strip() == 'TRADE_FINISHED' or ps['trade_status'].upper().strip() == 'TRADE_SUCCESS':
                order, is_insurance_order = change_order_status(ps['out_trade_no'], ps['trade_no'])
                create_msg(simplejson.dumps({'payment': 1, 'order_id': ps['out_trade_no']}), 'pay_success')
                if is_insurance_order and order:
                    send_new_insurance_order_msg(order.delivery_tel, order.store.name, order.store.area_code,
                                                 order.ordernum, order.current_order_price.insurance.name, order.payment,
                                                 order.current_order_price.gift_policy, order.sms_content,
                                                 order.current_order_price.total_price)
                msg = "success"
        self.write(msg)


# 支付宝支付完成后异步通知 支付宝回调（web支付）
@route('/mobile/alipay_notify_web', name='mobile_alipay_notify_web')
class MobileAlipayNotifyWebHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        notify = PaymentNotify()
        notify.content = self.request.body
        notify.notify_time = int(time.time())
        notify.notify_type = 2
        notify.payment = 1
        notify.function_type = 1
        notify.save()
        msg = "fail"
        params = {}
        ks = self.request.arguments.keys()
        for k in ks:
            params[k] = self.get_argument(k)
        ps = notify_verify(params)
        if ps:
            if ps['trade_status'].upper().strip() == 'TRADE_FINISHED' or ps['trade_status'].upper().strip() == 'TRADE_SUCCESS':
                order, is_insurance_order = change_order_status(ps['out_trade_no'], ps['trade_no'])
                create_msg(simplejson.dumps({'payment': 1, 'order_id': ps['out_trade_no']}), 'pay_success')
                if is_insurance_order and order:
                    send_new_insurance_order_msg(order.delivery_tel, order.store.name, order.store.area_code,
                                                 order.ordernum, order.current_order_price.insurance.name,
                                                 order.payment, order.current_order_price.gift_policy,
                                                 order.sms_content, order.current_order_price.total_price)
                msg = "success"
        self.write(msg)


# 微信支付完成后异步通知 微信回调
@route(r'/mobile/weixin_notify', name='mobile_weixinpay_notify')
class MobileWeiXinPayCallbackHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        notify = PaymentNotify()
        notify.content = self.request.body
        notify.notify_time = int(time.time())
        notify.notify_type = 2
        notify.payment = 2
        notify.function_type = 1
        notify.save()
        notify_data = Notify_pub()
        notify_data.saveData(self.request.body)
        ps = notify_data.getData()
        if notify_data.checkSign():
            if ps['return_code'] == 'SUCCESS' and ps['result_code'] == 'SUCCESS':
                order, is_insurance_order = change_order_status(ps['out_trade_no'], ps['transaction_id'])
                create_msg(simplejson.dumps({'payment': 2, 'order_id': ps['out_trade_no']}), 'pay_success')
                if is_insurance_order and order:
                    send_new_insurance_order_msg(order.delivery_tel, order.store.name, order.store.area_code,
                                                 order.ordernum, order.current_order_price.insurance.name, order.payment,
                                                 order.current_order_price.gift_policy, order.sms_content,
                                                 order.current_order_price.total_price)
                notify_data.setReturnParameter('return_code', 'SUCCESS')
            else:
                logging.info(u'微信通知支付失败')
        else:
            logging.info(u'微信通知验证失败')
        self.write(notify_data.returnXml())


# 银联支付完成后异步通知 银联回调
@route(r'/mobile/upay_notify', name='mobile_upay_notify')
class MobileUPayCallbackHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'return_code': 'FAIL'}
        try:
            ps = Trade().smart_str_decode(self.request.body)
            if Trade().union_validate(ps):
                if ps['respMsg'] == 'Success!':
                    order, is_insurance_order = change_order_status(ps['orderId'], ps['queryId'])
                    create_msg(simplejson.dumps({'payment': 3, 'order_id': ps['orderId']}), 'pay_success')
                    if is_insurance_order and order:
                        send_new_insurance_order_msg(order.delivery_tel, order.store.name, order.store.area_code,
                                                     order.ordernum, order.insurance.name, order.payment,
                                                     order.current_order_price.gift_policy, order.sms_content,
                                                     order.current_order_price.total_price)
                    result['return_code'] = 'SUCCESS'
                else:
                    result['return_msg'] = 'upay get FAIL notify'
            else:
                logging.info('upay invalid')
        except Exception, e:
            logging.info('Error: upay error %s' % e.message)

        self.write(simplejson.dumps(result))


# ------------------------------------------------充值回调--------------------------------------------------------------
def recharge(order_num, trade_no, money, payment=''):
    user_id = int(order_num.split('R')[0].strip('U'))
    user = User.get(id=user_id)
    store = user.store
    store.price += float(money)
    store.save()
    now = int(time.time())
    process_log = u'支付方式：%s，订单号：order_id=%s' % (payment, order_num)
    # 资金类别 # 1提现、2充值、3售出、4采购、5保险、6退款、7保单补款
    MoneyRecord.create(user=user, store=user.store, type=2,process_type=1, process_message=u'充值', apply_time=now,
                       process_log=process_log, in_num=trade_no, money=money, status=1, processing_time=now)


# 支付宝充值完成后异步通知 支付宝回调（APP 支付）
@route('/mobile/alipay_cz_notify', name='mobile_alipay_cz_notify')
class MobileAlipayCZNotifyHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        notify = PaymentNotify()
        notify.content = self.request.body
        notify.notify_time = int(time.time())
        notify.notify_type = 2
        notify.payment = 1
        notify.function_type = 1
        notify.save()
        msg = "fail"
        params = {}
        ks = self.request.arguments.keys()
        for k in ks:
            params[k] = self.get_argument(k)
        ps = verify_alipay_request_sign(params)
        if ps and (ps['trade_status'].upper().strip() == 'TRADE_FINISHED' or ps['trade_status'].upper().strip() == 'TRADE_SUCCESS'):
            if MoneyRecord.select().where(MoneyRecord.in_num == ps['trade_no']).count() > 0:
                logging.error(u'支付宝重复回调：order_id:%s in_num:%s' % (ps['out_trade_no'], ps['trade_no']))
            else:
                create_msg(simplejson.dumps({'payment': 1, 'order_id': ps['out_trade_no']}), 'recharge')
                recharge(ps['out_trade_no'], ps['trade_no'], ps['receipt_amount'], u'支付宝')
            msg = "success"
        self.write(msg)


# 支付宝支付完成后异步通知 支付宝回调 （手机网站支付）
@route('/mobile/alipay_cz_notify_web', name='mobile_alipay_cz_notify_web')
class MobileAlipayCZNotifyWebHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        notify = PaymentNotify()
        notify.content = self.request.body
        notify.notify_time = int(time.time())
        notify.notify_type = 2
        notify.payment = 1
        notify.function_type = 1
        notify.save()
        msg = "fail"
        params = {}
        ks = self.request.arguments.keys()
        for k in ks:
            params[k] = self.get_argument(k)
        logging.error('----parms=%s---' % params)
        ps = notify_verify(params)
        logging.error('----ps=%s---' % ps)
        if ps:
            if ps['trade_status'].upper().strip() == 'TRADE_FINISHED' or ps['trade_status'].upper().strip() == 'TRADE_SUCCESS':
                if MoneyRecord.select().where(MoneyRecord.in_num == ps['trade_no']).count() > 0:
                    logging.error(u'支付宝重复回调：order_id:%s in_num:%s' % (ps['out_trade_no'], ps['trade_no']))
                else:
                    create_msg(simplejson.dumps({'payment': 1, 'order_id': ps['out_trade_no']}), 'recharge')
                    recharge(ps['out_trade_no'], ps['trade_no'], ps['total_fee'], u'支付宝')
                msg = "success"
        self.write(msg)


# 微信充值完成后异步通知 微信回调
@route(r'/mobile/weixin_cz_notify', name='mobile_weixinpay_cz_notify')
class MobileWeiXinPayCZNotifyHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        notify = PaymentNotify()
        notify.content = self.request.body
        notify.notify_time = int(time.time())
        notify.notify_type = 2
        notify.payment = 2
        notify.function_type = 1
        notify.save()
        notify_data = Notify_pub()
        notify_data.saveData(self.request.body)
        ps = notify_data.getData()
        if notify_data.checkSign():
            if ps['return_code'] == 'SUCCESS' and ps['result_code'] == 'SUCCESS':
                create_msg(simplejson.dumps({'payment': 2, 'order_id': ps['out_trade_no']}), 'recharge')
                if MoneyRecord.select().where(MoneyRecord.in_num == ps['transaction_id']).count() > 0:
                    logging.error(u'微信重复回调：order_id:%s in_num:%s' % (ps['out_trade_no'], ps['transaction_id']))
                else:
                    recharge(ps['out_trade_no'], ps['transaction_id'], float(ps['total_fee'])/100, u'微信')
                notify_data.setReturnParameter('return_code', 'SUCCESS')
            else:
                logging.info(u'微信通知支付失败')
        else:
            logging.info(u'微信通知验证失败')
        self.write(notify_data.returnXml())


# 银联充值完成后异步通知 银联回调
@route(r'/mobile/upay_cz_notify', name='mobile_upay_cz_notify')
class MobileUPayCZNotifyHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def options(self):
        pass

    def post(self):
        result = {'return_code': 'FAIL'}
        try:
            ps = Trade(isCZ=True).smart_str_decode(self.request.body)
            if Trade(isCZ=True).union_validate(ps):
                if ps['respMsg'] == 'Success!':
                    create_msg(simplejson.dumps({'payment': 3, 'order_id': ps['orderId']}), 'recharge')
                    if MoneyRecord.select().where(MoneyRecord.in_num == ps['queryId']).count() > 0:
                        logging.error(u'银联重复回调：order_id:%s in_num:%s' % (ps['orderId'], ps['queryId']))
                    else:
                        recharge(ps['orderId'], ps['queryId'], float(ps['settleAmt'])/100, u'银联')
                    result['return_code'] = 'SUCCESS'
                else:
                    result['return_msg'] = 'upay get FAIL notify'
            else:
                logging.info('upay invalid')
        except Exception, e:
            logging.info('Error: upay error %s' % e)

        self.write(simplejson.dumps(result))





if __name__ == '__main__':
    parms = {'sec_id': u'MD5', 'v': u'1.0', 'notify_data': u'<notify><payment_type>1</payment_type><subject>\u8f66\u88c5\u7532\u5145\u503c</subject><trade_no>2017060121001004990279718514</trade_no><buyer_email>17629260130</buyer_email><gmt_create>2017-06-01 15:11:40</gmt_create><notify_type>trade_status_sync</notify_type><quantity>1</quantity><out_trade_no>U1284R496301090</out_trade_no><notify_time>2017-06-01 15:11:41</notify_time><seller_id>2088221897731280</seller_id><trade_status>TRADE_SUCCESS</trade_status><is_total_fee_adjust>N</is_total_fee_adjust><total_fee>0.01</total_fee><gmt_payment>2017-06-01 15:11:41</gmt_payment><seller_email>pay.chezhuangjia@520czj.com</seller_email><price>0.01</price><buyer_id>2088402583702995</buyer_id><notify_id>cd8b4964f7dd5b0ef1445bd72c516c6nn2</notify_id><use_coupon>N</use_coupon></notify>', 'service': u'alipay.wap.trade.create.direct', 'sign': u'eb9170996068512528a03acbc1f27417'}
    ps = notify_verify(parms)
    print ps
    if ps['trade_status'].upper().strip() == 'TRADE_FINISHED' or ps['trade_status'].upper().strip() == 'TRADE_SUCCESS':
        print ps['out_trade_no'], ps['total_fee'], ps['trade_no']
