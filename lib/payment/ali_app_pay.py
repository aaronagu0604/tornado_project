#!/usr/bin/env python
#coding:utf-8


import base64
import time
import rsa
import alipay_config as Settings

SIGN_TYPE = 'SHA-256'

# 拼接要签名的字符串
def join_string(total_amount, subject, body, ordernum):
    notify_url = Settings.NOTIFY_URL
    timestamp = time.strftime('%Y-%m-%d!%H:%M:%S', time.localtime())
    before_sign = '''app_id=%s&
        biz_content={
            "timeout_express": "30m",
            "seller_id": "",
            "product_code": "QUICK_MSECURITY_PAY",
            "total_amount": %s,
            "subject": %s,
            "body": %s,
            "out_trade_no": %s
        }&
        charset=utf-8&
        format=json&
        method=alipay.trade.app.pay&
        notify_url=%s&
        sign_type=RSA2&
        timestamp=%s&
        version=1.0''' % ('2016052701450725', total_amount, subject, body, ordernum, notify_url, timestamp)
    return before_sign.replace(' ', '').replace('\n', '').replace('!', ' ')

# 签名字符串
def alipay_sign(total_price, subject, body, ordernum):
    private_key = rsa.PrivateKey._load_pkcs1_pem(Settings.RSA_PRIVATE)
    strings = join_string(total_price, subject, body, ordernum)
    sign = rsa.sign(strings, private_key, SIGN_TYPE)
    b64sing = base64.b64encode(sign)
    return strings, b64sing

# 拼接字符串与签名并转为utf-8
def switch_to_utf_8(total_price, subject, body, ordernum):
    strings, sign_string = alipay_sign(total_price, subject, body, ordernum)
    return unicode((strings + '&sign=' + sign_string), encoding='utf-8')

# 验证自签名
def check_sign(message, sign):
    sign = base64.b64decode(sign)
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(Settings.RSA_PUBLIC)
    return rsa.verify(message, sign, pubkey)

def test():
    print switch_to_utf_8('10', 'insurance', '你好', 'U220I110')
    print isinstance(switch_to_utf_8('10', 'insurance', '你好', 'U220I110'), unicode)
    message, sign = alipay_sign('10', 'insurance', '你好', 'U220I110')
    print check_sign(message, sign)




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





