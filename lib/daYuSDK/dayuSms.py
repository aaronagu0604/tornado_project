# -*- coding: utf-8 -*-
'''
Created on 2016-11-13
@author: aaron
'''
import logging
import top.api

alipayUrl = "gw.api.taobao.com"
alipayPort = 80
alipayAppkey = "23514523"
alipaySecret = "c3f339be7d1d0f3bf526c0a0280fa9d2"

def sendmsg(mobile, content, isyzm):
    req = top.api.AlibabaAliqinFcSmsNumSendRequest(alipayUrl, alipayPort)
    req.set_app_info(top.appinfo(alipayAppkey, alipaySecret))
    req.extend = "123456"
    req.sms_type = "normal"
    req.sms_free_sign_name = "车装甲"
    fp = open('/tmp/aaa.txt', 'a')
    fp.write('mobile=%s, content=%s, isyzm=%s\n'%(mobile, content, isyzm))
    try:#vcodeNew
        if isyzm == 'vcode': #验证码
            req.sms_param = "{\"sms_code\":\"" +content+ "\"}"
            req.sms_template_code = "SMS_35940131"
        elif isyzm == 'vcodeNew': #验证码
            req.sms_param = "{\"sms_code\":\"" +content+ "\"}"
            req.sms_template_code = "SMS_35895219"
            req.sms_free_sign_name = "车装甲网络科技"
        elif isyzm == 'changePrice': #修改价格
            req.sms_param = "{\"InsuranceOrderId\":\"%s\", \"Insurer\":\"%s\", \"Price\":\"%s\", \"Remarks\":\"%s\"}"%(content[0], content[1], content[2], content[3])
            req.sms_template_code = "SMS_25095450"
        elif isyzm == 'paySuccess': #支付成功
            req.sms_param = "{\"ShopName\":\"%s\", \"LocalArea\":\"%s\", \"OrderId\":\"%s\", \"Insurance\":\"%s\", \"payment\":\"%s\", \"gift\":\"%s\", \"Remarks\":\"%s\"}"%(
                content[0], content[1], content[2], content[3], content[4], content[5], content[6])
            req.sms_template_code = "SMS_38970039"
        elif isyzm == 'shipments': # 商品已发货，注意查收
            req.sms_param = "{\"Ordernum\":\"%s\"}"%content
            req.sms_template_code = "SMS_25465034"
        elif isyzm == 'cashMoney':  #提现（客户端）
            req.sms_param = "{\"Money\":\"%s\", \"CashMoney\":\"%s\"}"%(content[0], content[1])
            req.sms_template_code = "SMS_25340017"
        elif isyzm == 'cashMoneySys':  #提现（管理员）
            req.sms_param = "{\"addr\":\"%s\", \"company\":\"%s\", \"people\":\"%s\", \"money\":\"%s\"," \
                            " \"payment\":\"%s\"}"%(content[0], content[1], content[2], content[3], content[4])
            req.sms_template_code = "SMS_36105271"
        elif isyzm == 'placeOrderSys':  #下单通知（管理员）
            req.sms_param = "{\"OrderId\":\"%s\", \"OrderInfo\":\"%s\"}"%(content[0], content[1])
            req.sms_template_code = "SMS_25050449"
        elif isyzm == 'placeOrderToStore':  #保险订单下单通知（客户）
            req.sms_param = ""
            req.sms_template_code = "SMS_35535019"
        elif isyzm == 'checkStorePass': #申请入驻审核通过
            req.sms_param = ""
            req.sms_template_code = "SMS_25075401"
        elif isyzm == 'checkStoreDecline': #申请入驻审核 不通过
            req.sms_param = ""
            req.sms_template_code = "SMS_25225457"
        elif isyzm == 'placeOrderToServer': #普通商品下单通知卖家
            req.sms_param = "{\"product\":\"%s\"}"%content
            req.sms_template_code = "SMS_25985258"
        elif isyzm == 'accountNotice':  #已经给您的${bankName}尾号为${bankNum}的银行卡汇款，将于两小时内到账，请注意查收。
            req.sms_param = "{\"bankName\":\"%s\", \"bankNum\":\"%s\"}"%(content[0], content[1])
            req.sms_template_code = "SMS_34930382"

        req.rec_num = mobile
        resp = req.getResponse()
        fp.write('----result-----=%s\n' % str(resp))
    except Exception, e:
        fp.write('send msg error %s\n'%e)
    fp.close
















