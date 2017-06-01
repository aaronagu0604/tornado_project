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
                    recharge(ps['out_trade_no'], ps['trade_no'], ps['receipt_amount'], u'支付宝')
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
    parms = 'service=alipay.wap.trade.create.direct&sign=7c5abaf1402c2107b1c9a03b89427698&sec_id=MD5&v=1.0&notify_data=%3Cnotify%3E%3Cpayment_type%3E1%3C%2Fpayment_type%3E%3Csubject%3E%E8%BD%A6%E8%A3%85%E7%94%B2%E5%85%85%E5%80%BC%3C%2Fsubject%3E%3Ctrade_no%3E2017060121001004990279309698%3C%2Ftrade_no%3E%3Cbuyer_email%3E17629260130%3C%2Fbuyer_email%3E%3Cgmt_create%3E2017-06-01+11%3A51%3A19%3C%2Fgmt_create%3E%3Cnotify_type%3Etrade_status_sync%3C%2Fnotify_type%3E%3Cquantity%3E1%3C%2Fquantity%3E%3Cout_trade_no%3EU1284R496289064%3C%2Fout_trade_no%3E%3Cnotify_time%3E2017-06-01+13%3A21%3A40%3C%2Fnotify_time%3E%3Cseller_id%3E2088221897731280%3C%2Fseller_id%3E%3Ctrade_status%3ETRADE_SUCCESS%3C%2Ftrade_status%3E%3Cis_total_fee_adjust%3EN%3C%2Fis_total_fee_adjust%3E%3Ctotal_fee%3E0.01%3C%2Ftotal_fee%3E%3Cgmt_payment%3E2017-06-01+11%3A51%3A19%3C%2Fgmt_payment%3E%3Cseller_email%3Epay.chezhuangjia%40520czj.com%3C%2Fseller_email%3E%3Cprice%3E0.01%3C%2Fprice%3E%3Cbuyer_id%3E2088402583702995%3C%2Fbuyer_id%3E%3Cnotify_id%3Ef189c3cb570498b78af217a60224ab1nn2%3C%2Fnotify_id%3E%3Cuse_coupon%3EN%3C%2Fuse_coupon%3E%3C%2Fnotify%3E'
    from urllib import unquote
    data = {}
    for p in unquote(parms.encode('utf-8')).split('&'):
        k, v = p.split('=')
        data[k] = v
    print data
    ps = notify_verify(data)
    print ps



