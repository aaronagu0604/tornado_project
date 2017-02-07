#!/usr/bin/env python
#coding=utf-8

import types
import md5
import logging
from urllib import urlencode, urlopen
import time
import re


class AlipayMobile:
    
    _GATEWAY = 'http://wappaygw.alipay.com/service/rest.htm?'
    
    def __init__(self, **settings):
        self.ALIPAY_KEY = settings['alipay_key']
        self.ALIPAY_PARTNER = settings['alipay_partner']
        self.ALIPAY_SELLER_EMAIL = settings['alipay_seller_email']
        self.ALIPAY_AUTH_URL = settings['alipay_auth_url']
        self.ALIPAY_RETURN_URL = settings['alipay_return_url']
        self.ALIPAY_NOTIFY_URL = settings['alipay_notify_url']
        self.ALIPAY_INPUT_CHARSET = settings['alipay_input_charset']
        self.ALIPAY_SHOW_URL = settings['alipay_show_url']
        self.ALIPAY_SIGN_TYPE = settings['alipay_sign_type']
        self.ALIPAY_TRANSPORT = settings['alipay_transport']
        self.ALIPAY_RETURN_CZ_URL = settings['alipay_return_cz_url']
        self.ALIPAY_NOTIFY_CZ_URL = settings['alipay_notify_cz_url']
    
    def smart_str(self, s, encoding='utf-8', strings_only=False, errors='strict'):
        
        if strings_only and isinstance(s, (types.NoneType, int)):
            return s
        
        if not isinstance(s, basestring):
            try:
                return str(s)
            except UnicodeEncodeError:
                if isinstance(s, Exception):
                    return ' '.join([self.smart_str(arg, encoding, strings_only, errors) for arg in s])
                return unicode(s).encode(encoding, errors)
            
        elif isinstance(s, unicode):
            return s.encode(encoding, errors)
        elif s and encoding != 'utf-8':
            return s.decode('utf-8', errors).encode(encoding, errors)
        else:
            return s
        
    def params_filter(self, params):
        ks = params.keys()
        ks.sort()
        newparams = {}
        prestr = ''
        
        for k in ks:
            v = params[k]
            k = self.smart_str(k, self.ALIPAY_INPUT_CHARSET)
            
            if v != '':
                newparams[k] = self.smart_str(v, self.ALIPAY_INPUT_CHARSET)
                prestr += '%s=%s&' % (k, newparams[k])
        
        prestr = prestr[:-1]
        return newparams, prestr
    
    def build_mysign(self, prestr, key, sign_type = 'MD5'):
        if sign_type == 'MD5':
            return md5.new(prestr + key).hexdigest()
        return ''
    
    def notify_verify(self, prestr, sign):
        mysign = self.build_mysign(prestr, self.ALIPAY_KEY, self.ALIPAY_SIGN_TYPE)
        return mysign == sign

    def get_request_token(self, ordernum, subject, totalfee, call_back_url, notify_url, merchant_url):
        GATEWAY_NEW = "http://wappaygw.alipay.com/service/rest.htm?"
        format = "xml"
        v = "1.0"
        req_id = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

        seller_email = self.ALIPAY_SELLER_EMAIL
        subject = subject
        out_trade_no = ordernum
        total_fee = totalfee
        req_dataToken = "<direct_trade_create_req><notify_url>" + notify_url + \
                        "</notify_url><call_back_url>" + call_back_url + \
                        "</call_back_url><seller_account_name>" + seller_email + \
                        "</seller_account_name><out_trade_no>" + out_trade_no + \
                        "</out_trade_no><subject>" + subject + "</subject><total_fee>" + \
                        total_fee + "</total_fee><merchant_url>" + merchant_url + \
                        "</merchant_url></direct_trade_create_req>"

        params = {}
        params['partner'] = self.ALIPAY_PARTNER
        params['sec_id'] = self.ALIPAY_SIGN_TYPE
        params['service'] = "alipay.wap.trade.create.direct"
        params['format'] = format
        params['v'] = v
        params['req_id'] = req_id
        params['req_data'] = req_dataToken

        params, prestr = self.params_filter(params)
        params['sign'] = self.build_mysign(prestr, self.ALIPAY_KEY, self.ALIPAY_SIGN_TYPE)
        params, prestr = self.params_filter(params)
        result = None
        try:
            newURL = GATEWAY_NEW + urlencode(params)
            response = urlopen(newURL).read()
            print response
            p = re.compile(r'(request_token%3E[\w]*%3C%2Frequest_token)')

            for com in p.finditer(response):
                mm = com.group()
                result = mm.replace('request_token%3E','').replace('%3C%2Frequest_token','')
                print result

        except Exception, ex:
            logging.error(ex)
        return result

    def pay_order(self, ordernum, subject, totalfee, call_back_url, notify_url, merchant_url):
        GATEWAY_NEW = "http://wappaygw.alipay.com/service/rest.htm?"
        params = {}
        token = self.get_request_token(ordernum, subject, totalfee, call_back_url, notify_url, merchant_url)
        params['service'] = 'alipay.wap.auth.authAndExecute'
        params['partner'] = self.ALIPAY_PARTNER
        params['sec_id'] = self.ALIPAY_SIGN_TYPE
        params['format'] = 'xml'
        params['v'] = '1.0'
        params['req_data'] = "<auth_and_execute_req><request_token>" + token + "</request_token></auth_and_execute_req>"

        params, prestr = self.params_filter(params)
        params['sign'] = self.build_mysign(prestr, self.ALIPAY_KEY, self.ALIPAY_SIGN_TYPE)

        result = ''
        try:
            result = urlopen(GATEWAY_NEW + urlencode(params)).read()
        except Exception, ex:
            logging.error(ex)

        return result