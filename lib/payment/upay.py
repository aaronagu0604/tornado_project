#!/usr/bin/env python
# -*- coding: utf-8 -*-
import types, hashlib, time, base64, os
import urllib2
import urllib
from urllib import urlencode, urlopen
from uconfig import setting  # 见config.py
from OpenSSL.crypto import load_pkcs12, FILETYPE_PEM, sign, verify, load_certificate


class Trade(object):
    def __init__(self, isCZ=False):
        self.isCZ = isCZ
    # 读取文件
    def getDataByCerPath(self, cert_path):
        fp = open(cert_path, 'r')
        if not fp:
            raise Exception('open %s fail!!!' % cert_path)
        pkcs12certdata = fp.read()
        return pkcs12certdata


    # 获取证书信息
    def getSign(self, cert_path, cert_pwd):
        pkcs12certdata = self.getDataByCerPath(cert_path)
        # 先解析pkcs12格式
        certs = load_pkcs12(pkcs12certdata, cert_pwd)
        return certs


    # 获取证书序列号
    def getSignCertId(self, cert_path, cert_pwd):
        certs = self.getSign(cert_path, cert_pwd)
        # 返回509序列号
        return certs.get_certificate().get_serial_number()


    # 获取证书私钥匙
    def getPrivateKey(self, cert_path, cert_pwd):
        certs = self.getSign(cert_path, cert_pwd)
        # 然后解析内容
        private_key = certs.get_privatekey()
        # key_pem = dump_privatekey(FILETYPE_PEM, certs.get_privatekey())
        # private_key = load_privatekey(FILETYPE_PEM, key_pem)
        return private_key


    # 取证书ID(.cer)
    def getCertIdByCerPath(self, cert_path):
        pkcs12certdata = self.getDataByCerPath(cert_path)
        # 非密码直读文件
        certs = load_certificate(FILETYPE_PEM, pkcs12certdata)
        pub_key = certs.get_serial_number()
        return pub_key


    # 验证用
    def getCerToX509(self, cert_path):
        pkcs12certdata = self.getDataByCerPath(cert_path)
        certs = load_certificate(FILETYPE_PEM, pkcs12certdata)
        return certs


    # 获取公钥
    def getPulbicKeyByCertId(self, certId):
        cert_dir = setting['SDK_VERIFY_CERT_DIR']
        for root, dirs, files in os.walk(cert_dir):
            for file in files:
                if os.path.splitext(file)[1] == '.cer':
                    if str(self.getCertIdByCerPath(os.path.join(root, file))) == certId:
                        return self.getCerToX509(os.path.join(root, file))
        return False
        # print(os.path.join(root, file))


    # 字符串编解码处理
    def smart_str(self, s, encoding='utf-8', strings_only=False, errors='strict'):
        if strings_only and isinstance(s, (types.NoneType, int)):
            return s
        if not isinstance(s, basestring):
            try:
                return str(s)
            except UnicodeEncodeError:
                if isinstance(s, Exception):
                    return ' '.join([self.smart_str(arg, encoding, strings_only,
                                               errors) for arg in s])
                return unicode(s).encode(encoding, errors)
        elif isinstance(s, unicode):
            return s.encode(encoding, errors)
        elif s and encoding != 'utf-8':
            return s.decode('utf-8', errors).encode(encoding, errors)
        else:
            return s

    def smart_str_decode(self, s):
        params = {}
        for tmps in s.split('&'):
            key, value = tmps.split('=', 1)
            params[key] = value
        return params

    # 排序并且参数化
    def createLinkString(self, params):
        if 'signature' in params:
            del params['signature']
        # 对数组排序并除去数组中的空值和签名参数
        ks = params.keys()
        ks.sort()
        newparams = {}
        prestr = ''
        for k in ks:
            v = params[k]
            k = self.smart_str(k)
            if k not in ('sign', 'sign_type') and v != '':
                newparams[k] = self.smart_str(v)
                prestr += '%s=%s&' % (k, newparams[k])
        prestr = prestr[:-1]
        return prestr


    # 签名
    def union_pay_sign(self, params, cert_path, cert_pwd):
        prestr = self.createLinkString(params)
        # sha1编码
        params_sha1 = hashlib.sha1(prestr).hexdigest()
        # 秘钥
        private_key = self.getPrivateKey(cert_path, cert_pwd)
        # 编码验证
        sign_falg = sign(private_key, params_sha1, 'sha1')
        if sign_falg:
            signature_base64 = base64.b64encode(sign_falg)
            return signature_base64
        else:
            return 'sign error'


    # 即时到账交易接口
    def createAutoFormHtml(self, tn, total_fee):
        params = {}
        params['version'] = '5.0.0'  # 版本号
        params['encoding'] = 'utf-8'  # 编码方式
        params['txnType'] = '01'  # 交易类型
        params['txnSubType'] = '01'  # 交易子类
        params['bizType'] = '000201'  # 业务类型
        params['frontUrl'] = setting['SDK_FRONT_NOTIFY_URL']  # 前台通知地址
        params['backUrl'] = setting['CZ_SDK_BACK_NOTIFY_URL'] if self.isCZ else setting['SDK_BACK_NOTIFY_URL'] # 后台通知地址
        params['signMethod'] = '01'  # 签名方法
        params['channelType'] = '08'  # 渠道类型，07-PC，08-手机
        params['accessType'] = '0'  # 接入类型
        params['currencyCode'] = '156'  # 交易币种，境内商户固定156

        params['merId'] = '898111948160473'  # 商户代码，请改自己的测试商户号，此处默认取demo演示页面传递的参数
        params['orderId'] = tn  # 商户订单号，8-32位数字字母，不能含“-”或“_”，此处默认取demo演示页面传递的参数，可以自行定制规则
        params['txnTime'] = time.strftime("%Y%m%d%H%M%S",time.localtime())  # 订单发送时间，格式为YYYYMMDDhhmmss，取北京时间，此处默认取demo演示页面传递的参数
        params['txnAmt'] = int(total_fee * 100)  # 交易金额，单位分，此处默认取demo演示页面传递的参数
        # 获取证书序列号
        params['certId'] = self.getSignCertId(setting['SDK_SIGN_CERT_PATH'], setting['SDK_SIGN_CERT_PWD']);
        # 签名函数
        params['signature'] = self.union_pay_sign(params, setting['SDK_SIGN_CERT_PATH'], setting['SDK_SIGN_CERT_PWD'])

        return params


    # 银联返回验证
    def union_validate(self, params):
        # 公钥
        public_key = self.getPulbicKeyByCertId(params['certId'])
        # 签名串
        signature_str = params['signature']
        del params['signature']
        # 组合
        params_str = self.createLinkString(params)
        # 解密
        signature = base64.b64decode(signature_str)
        # 签名核对
        params_sha1 = hashlib.sha1(params_str).hexdigest()
        try:
            verify(public_key, signature, params_sha1, 'sha1')
            return True
        except:
            return False

    def trade(self, orderId, total_fee):
        params = self.createAutoFormHtml(orderId, total_fee)
        r = urllib2.urlopen(setting['SDK_App_Request_Url'], data=urllib.urlencode(params), timeout=10).read()
        params = self.smart_str_decode(r)
        try:
            if params['respCode'] == '00':
                return params['tn']
        except:
            return ''

if __name__ == '__main__':
    tn = Trade().trade('u110s111', 0.1)
    print('---%s---' % tn)
    result={}
    if tn:
        result['tn'] = tn
        result['flag'] = 4
    else:
        result['flag'] = 0
    print str(result)