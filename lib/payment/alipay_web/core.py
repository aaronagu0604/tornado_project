# -*- coding: utf-8 -*-
import types
import urllib2
import xml.etree.ElementTree as etree

from lib.payment.alipay_web.aliconfig import Settings
from lib.payment.alipay_web.hashcompat import md5_constructor as md5


def build_request_params(params):
    """生成要请求给支付宝的参数数组

    <param name="sParaTemp">请求前的参数字典</param>
    <returns>要请求的参数数组</returns>
    """
    new_params, prestr = params_filter(params)
    my_sign = build_mysign(prestr, Settings.KEY)

    new_params.update({"sign": my_sign})
    if params["service"] not in ["alipay.wap.trade.create.direct",
                                 "alipay.wap.auth.authAndExecute"]:
        new_params.update({"sign_type", Settings.KEY_SIGN_TYPE})
    return new_params


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """ Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s


def params_filter(params):
    """ 对字典排序并除去数组中的空值和签名参数

    返回数组和链接串
    """
    ks = params.keys()
    ks.sort()
    new_params = {}
    prestr = ''
    for k in ks:
        v = params[k]
        k = smart_str(k, Settings.INPUT_CHARSET)
        if k not in ('sign', 'sign_type') and v != '':
            new_params[k] = smart_str(v, Settings.INPUT_CHARSET)
            prestr += '%s=%s&' % (k, new_params[k])
    prestr = prestr[:-1]
    return new_params, prestr


def fix_params_filter(params):
    """ 对字典排序并除去数组中的空值和签名参数

    返回数组和链接串
    """
    ks = params.keys()
    new_params = {}
    prestr = ''
    for k in ks:
        v = params[k]
        k = smart_str(k, Settings.INPUT_CHARSET)
        if k not in ('sign', 'sign_type') and v != '':
            new_params[k] = smart_str(v, Settings.INPUT_CHARSET)
    prestr = "service=%s&v=%s&sec_id=%s&notify_data=%s" % (new_params["service"], new_params["v"],
                                                           new_params["sec_id"], new_params["notify_data"])
    return new_params, prestr


def build_mysign(prestr, key, sign_type='MD5'):
    """生成请求时的签名

    <param name="sPara">请求给支付宝的参数数组</param>
    <returns>签名结果</returns>
    """
    if sign_type == 'MD5':
        return md5(prestr + key).hexdigest()
    return ''


def notify_verify(post):
    """验证---签名&&数据是否支付宝发送

    """
    #初级验证---签名
    _, prestr = fix_params_filter(post)
    mysign = build_mysign(prestr, Settings.KEY, Settings.SIGN_TYPE)
    if mysign != post.get('sign'):
        return False
    return True


def return_verify(query_params):
    """同步通知验证

    """
    _, prestr = params_filter(query_params)
    mysign = build_mysign(prestr, Settings.KEY, Settings.SIGN_TYPE)
    if mysign != query_params.get('sign'):
        return False
    return True


def query_timestamp():
    """用于防钓鱼，调用接口query_timestamp来获取时间戳的处理函数

    <returns>时间戳字符串</returns>
    """
    url = "%s?service=query_timestamp&partner=%s&_input_charset=%s" % \
          (Settings.GATEWAY, Settings.PARTNER, Settings.INPUT_CHARSET)
    xml_tree = urllib2.urlopen(url)
    tree = etree.parse(xml_tree)
    encrypt_key = tree.find("response/timestamp").text
    return encrypt_key


def build_request_html(params, method="GET"):
    """建立请求，以表单HTML形式构造

    <param name="sParaTemp">请求参数数组</pa
    <returns>提交表单HTML文本</returns>
    """
    new_params = build_request_params(params)
    sb_html = """<form id='alipaysubmit' name='alipaysubmit'
     action='%s?_input_charset=%s'
     method='%s'>""" % (Settings.GATEWAY, Settings.INPUT_CHARSET, method.lower())
    for p in new_params:
        sb_html += "<input type='hidden' name='%s' value='%s'/>" % (p, new_params[p])
    sb_html += """<input type='submit' value='submit' style='display:none;'></form>
    <script>document.forms['alipaysubmit'].submit();</script>
    """
    return sb_html
