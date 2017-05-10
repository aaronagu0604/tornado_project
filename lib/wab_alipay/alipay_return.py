#!/usr/bin/env python
# coding=utf-8

import types
import md5
from urllib import urlencode, urlopen
import time


class AlipayReturn:
    _GATEWAY = 'https://mapi.alipay.com/gateway.do?'

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
        self.ALIPAY_RETURN_PAY_NOTIFY_URL = settings['alipay_return_pay_notify_url']

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

            if k not in ('sign', 'sign_type') and v != '':
                newparams[k] = self.smart_str(v, self.ALIPAY_INPUT_CHARSET)
                prestr += '%s=%s&' % (k, newparams[k])

        prestr = prestr[:-1]
        return newparams, prestr

    def build_mysign(self, prestr, key, sign_type='MD5'):
        if sign_type == 'MD5':
            return md5.new(prestr + key).hexdigest()
        return ''

    def notify_verify(self, post):
        _, prestr = self.params_filter(post)
        mysign = self.build_mysign(prestr, self.ALIPAY_KEY, self.ALIPAY_SIGN_TYPE)

        if mysign != post.get('sign'):
            return False

        params = {}
        params['partner'] = self.ALIPAY_PARTNER
        params['notify_id'] = post.get('notify_id')
        params['service'] = 'notify_verify'

        veryfy_result = urlopen(self._GATEWAY, urlencode(params)).read()

        return veryfy_result.lower().strip() == 'true'

    def request_payback(self, trade_no, batch_no, price):

        params = {}
        params['notify_url'] = self.ALIPAY_RETURN_PAY_NOTIFY_URL
        params['_input_charset'] = self.ALIPAY_INPUT_CHARSET
        params['seller_email'] = self.ALIPAY_SELLER_EMAIL
        params['refund_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        params['partner'] = self.ALIPAY_PARTNER
        params['service'] = "refund_fastpay_by_platform_pwd"

        params['batch_no'] = batch_no
        params['batch_num'] = 1

        params['detail_data'] = str(trade_no)+u'^'+str(price)+u'^'+u'协商退款'

        params, prestr = self.params_filter(params)

        params['sign'] = self.build_mysign(prestr, self.ALIPAY_KEY, self.ALIPAY_SIGN_TYPE)
        params['sign_type'] = self.ALIPAY_SIGN_TYPE

        return self._GATEWAY + urlencode(params)