# -*- coding: utf-8 -*-
'''
Created on 2016-11-13
@author: aaron
'''
import top.api
import mqProcess.setting
import logging


def sendmsg(mobile, content, isyzm):
    req = top.api.AlibabaAliqinFcSmsNumSendRequest(mqProcess.setting.dayu_url, mqProcess.setting.dayu_port)
    req.set_app_info(top.appinfo(mqProcess.setting.dayu_appkey, mqProcess.setting.dayu_secret))
    req.extend = "123456"
    req.sms_type = "normal"
    req.sms_free_sign_name = "车装甲"

    fp = open('/imgData/nginx/server_log/msg_log.txt', 'a')
    fp.write('send msg: mobile=%s, content=%s, isyzm=%s\n'%(mobile, content, isyzm))

    if isinstance(mobile, unicode):
        mobile = mobile.encode('utf8')
    tmp_content = content
    if type(tmp_content) == type([]):
        content = []
        for c in tmp_content:
            if isinstance(c, unicode):
                c = c.encode('utf8')
            content.append(c)
    elif type(tmp_content) == type('') and isinstance(content, unicode):
        content = content.encode('utf8')
    if isinstance(isyzm, unicode):
        isyzm = isyzm.encode('utf8')
    try:#vcodeNew
        if isyzm == 'vcode': #验证码
            req.sms_param = "{\"sms_code\":\"" +content+ "\"}"
            req.sms_template_code = "SMS_35940131"
        elif isyzm == 'vcodeNew': #验证码
            req.sms_param = "{\"sms_code\":\"" +content+ "\"}"
            req.sms_template_code = "SMS_35895219"
            req.sms_free_sign_name = "车装甲网络科技"
        elif isyzm == 'changePrice': #修改价格
            logging.error(u'修改价格，发送短信 %s' % str(content))
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
    except Exception, e:
        print 'send msg error:' + str(e)

    fp.close()

if __name__ == '__main__':
    # sendmsg(u'18189279823'.encode("utf8"), u'2234'.encode("utf8"), u'vcode'.encode("utf8"))  #13239109398  18189279823 {"alias":["18189279823","13239109398"]}
    sendmsg('13389202687', ['U1285D0604I9764', '修改价格', '修改成1分', '6666'], 'changePrice')












