#!/usr/bin/env python
#coding:utf-8

import base64
import time
import rsa
import urllib
import urllib2
import simplejson
import alipay_config as Settings
from payqrcode import createqrcode

ALI_GATEWAY_URL = "https://openapi.alipay.com/gateway.do?"

SIGN_TYPE = 'SHA-256'

# 拼接要签名的字符串
def join_string(total_amount, subject, body, ordernum, isCZ):
    if isCZ:
        notify_url = Settings.NOTIFY_URL_CZ
    else:
        notify_url = Settings.NOTIFY_URL
    timestamp = time.strftime('%Y-%m-%d!%H:%M:%S', time.localtime())
    before_sign = '''app_id=%s&
        biz_content={
            "timeout_express": "30m",
            "seller_id": "",
            "product_code": "QUICK_MSECURITY_PAY",
            "total_amount": "%s",
            "subject": "%s",
            "body": "%s",
            "out_trade_no": "%s"
        }&
        charset=utf-8&
        format=json&
        method=alipay.trade.app.pay&
        notify_url=%s&
        sign_type=RSA2&
        timestamp=%s&
        version=1.0''' % ('2016052701450725', total_amount, subject, body, ordernum, notify_url, timestamp)
    join_str = before_sign.replace(' ', '').replace('\n', '').replace('!', ' ')
    return join_str

def join_string_qrcode(total_amount, subject, body, ordernum):
    notify_url = Settings.NOTIFY_URL
    timestamp = time.strftime('%Y-%m-%d!%H:%M:%S', time.localtime())
    before_sign = '''app_id=%s&
        biz_content={
            "timeout_express": "30m",
            "total_amount": "%s",
            "subject": "%s",
            "body": "%s",
            "out_trade_no": "%s"
        }&
        charset=utf-8&
        format=json&
        method=alipay.trade.precreate&
        notify_url=%s&
        sign_type=RSA2&
        timestamp=%s&
        version=1.0''' % ('2016052701450725', total_amount, subject, body, ordernum, notify_url, timestamp)
    join_str = before_sign.replace(' ', '').replace('\n', '').replace('!', ' ')
    return join_str

# 拼接后的字符串转为urlencode
def switch_to_urlencode(utf_8_string):
    if not isinstance(utf_8_string, unicode):
        utf_8_string = unicode(utf_8_string, encoding='utf-8')
    doct = {}
    for key_value in utf_8_string.split('&'):
        (key, value) = key_value.split('=', 1)
        doct[key] = value.encode('UTF-8')
    return urllib.urlencode(doct)

# 字符串排序
def sort_string(string):
    str_result = ''
    for str_tmp in sorted(string.split('&')):
        str_result = str_result + '&' + str_tmp
    return str_result.strip('&')

# 签名原字符串
def alipay_sign(strings):
    private_key = rsa.PrivateKey._load_pkcs1_pem(Settings.RSA_PRIVATE)
    sign = rsa.sign(strings, private_key, SIGN_TYPE)
    return base64.b64encode(sign)

# 验证自签名
def check_sign(message, sign):
    sign = base64.b64decode(sign)
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(Settings.RSA_PUBLIC)
    return rsa.verify(message, sign, pubkey)

# 获取最终签名后的字符串
def get_alipay_string(total_price, subject, body, ordernum, isCZ=False):
    try:
        after_join_string = join_string(total_price, subject, body, ordernum, isCZ)
        sign_string = alipay_sign(after_join_string)
        url_string = switch_to_urlencode(after_join_string)
        sorted_string = sort_string(url_string)
        result_string = (sorted_string + '&' + switch_to_urlencode('sign='+sign_string)).replace('+', '%20')
    except Exception, e:
        result_string = ''
    return result_string

# 获取最终签名后的字符串
def get_alipay_string_qrcode(total_price, subject, body, ordernum):
    after_join_string = join_string_qrcode(total_price, subject, body, ordernum)
    sign_string = alipay_sign(after_join_string)
    url_string = switch_to_urlencode(after_join_string)
    sorted_string = sort_string(url_string)
    result_string = (sorted_string + '&' + switch_to_urlencode('sign='+sign_string)).replace('+', '%20')
    return result_string

# 获取支付宝二维码支付二维码图片链接地址
def get_alipay_qrcode(total_price=0.01, subject='czjqrcodetest', body='testproduct', ordernum='u4i19001235'):
    parameters = get_alipay_string_qrcode(total_price, subject, body, ordernum)
    req = urllib2.Request(ALI_GATEWAY_URL+parameters)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    resdic = simplejson.loads(res)
    print resdic
    if resdic['alipay_trade_precreate_response']['msg'] == 'Success':
        return createqrcode(resdic['alipay_trade_precreate_response']['qr_code'])
    else:
        return None


# ---------------------------------------------------------验签-----------------------------

def check_ali_sign(message, sign):
    """
    验证ali签名
    :param message:
    :param sign:
    :return:
    """
    sign = base64.b64decode(sign)
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(Settings.RSA_ALIPAY_PUBLIC)
    res = False
    try:
        res = rsa.verify(message, sign, pubkey)
    except Exception as e:
        print e
        res = False
    return res


def params_to_query(params, quotes=False, reverse=False):
    """
        生成需要签名的字符串
    :param params:
    :return:
    """
    """
    :param params:
    :return:
    """
    query = ""
    for key in sorted(params.keys(), reverse=reverse):
        value = params[key]
        if quotes == True:
            query += str(key) + "=\"" + str(value) + "\"&"
        else:
            query += str(key) + "=" + str(value) + "&"
    query = query[0:-1]
    return query


def params_filter(params):
    """
    去掉不需要验证的参数
    :param params:
    :return:
    """
    """
    :param params:
    :return:
    """
    ret = {}
    for key, value in params.items():
        if key == "sign" or key == "sign_type" or value == "":
            continue
        ret[key] = value
    return ret


def verify_alipay_request_sign(params_dict):
    """
    验证阿里支付回调接口签名
    :param params_dict: 阿里回调的参数列表
    :return:True or False
    """
    sign = params_dict['sign']
    params = params_filter(params_dict)
    message = params_to_query(params, quotes=False, reverse=False)
    check_res = check_ali_sign(message, sign)
    if check_res:
        return params
    else:
        return {}


def test():
    string_demo = '''app_id=2015052600090779&biz_content={"timeout_express":"30m","seller_id":"","product_code":"QUICK_MSECURITY_PAY","total_amount":"0.01","subject":"1","body":"我是测试数据","out_trade_no":"IQJZSRC1YMQB5HU"}&charset=utf-8&format=json&method=alipay.trade.app.pay&notify_url=http://domain.merchant.com/payment_notify&sign_type=RSA2&timestamp=2016-08-25 20:26:31&version=1.0'''
    sign_string = alipay_sign(string_demo)
    url_string = switch_to_urlencode(string_demo)
    sorted_string = sort_string(url_string)
    result_string = (sorted_string + '&' + switch_to_urlencode('sign='+sign_string)).replace('+', '%20')
    return result_string


if __name__ == '__main__':
    pass

# print test()
# string_demo = '''app_id=2015052600090779&biz_content={"timeout_express":"30m","seller_id":"","product_code":"QUICK_MSECURITY_PAY","total_amount":"0.01","subject":"1","body":"我是测试数据","out_trade_no":"IQJZSRC1YMQB5HU"}&charset=utf-8&format=json&method=alipay.trade.app.pay&notify_url=http://domain.merchant.com/payment_notify&sign_type=RSA2&timestamp=2016-08-25 20:26:31&version=1.0&sign=cYmuUnKi5QdBsoZEAbMXVMmRWjsuUj+y48A2DvWAVVBuYkiBj13CFDHu2vZQvmOfkjE0YqCUQE04kqm9Xg3tIX8tPeIGIFtsIyp/M45w1ZsDOiduBbduGfRo1XRsvAyVAv2hCrBLLrDI5Vi7uZZ77Lo5J0PpUUWwyQGt0M4cj8g='''

# private_key = rsa.PrivateKey._load_pkcs1_pem(Settings.RSA_PRIVATE)
# sign = rsa.sign(unicode('我', encoding='utf-8'), private_key, SIGN_TYPE)
# print base64.b64encode(sign)
# switch_to_urlencode(unicode(string_demo, encoding='utf-8'))

# print isinstance(unicode('a', encoding='utf-8'), unicode)
# print unicode('a', encoding='utf-8').decode('ascii')
# # from curses import ascii
# # print ascii.isascii('a')
# print '我'.encode('ascii')
# print unicode('我', encoding='utf-8').decode('utf-8').encode('ascii')

# print isinstance(unicode('我', encoding='utf-8').decode('ascii'), unicode)
# print a
# print isinstance(a, unicode)
# import chardet
# print chardet.detect(sign)
#
# b64sing = base64.b64encode(sign)
# print chardet.detect(b64sing)
# a = (strings + '&sign=' + b64sing).decode("ascii").encode('utf-8')
# print isinstance(a, unicode)
# print chardet.detect(a)
# b = unicode(a, encoding='utf-8')

# sign_string()
# reload(sys)
# print sys.getdefaultencoding()





