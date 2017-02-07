# -*- coding: utf-8 -*-
import urllib2
import types
from urllib import urlencode, urlopen
from hashcompat import md5_constructor as md5
import xml.etree.ElementTree as etree
from config import Settings
from model import User, Order, Score,Balance,OrderItem,AdminUser,PayBack,Product_Reserve, OrderItemService
import random
import time
import logging

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
    order_params = {}
    params = {}
    _, prestr = fix_params_filter(post)
    mysign = build_mysign(prestr, Settings.KEY, Settings.SIGN_TYPE)
    if mysign != post.get('sign'):
        return False
    tree = etree.fromstring(post.get("notify_data").encode('utf-8'))
    notify_id = tree.find("notify_id").text
    order_params["trade_no"] = tree.find("trade_no").text
    order_params["out_trade_no"] = tree.find("out_trade_no").text
    order_params["trade_status"] = tree.find("trade_status").text
    order_params["total_fee"] = tree.find("total_fee").text
    order_params['buyer_email'] = tree.find("buyer_email").text
    #二级验证---数据是否支付宝发送
    if notify_id:
        params['partner'] = Settings.PARTNER
        params['notify_id'] = notify_id
        if Settings.TRANSPORT == 'https':
            params['service'] = 'notify_verify'
            gateway = 'https://mapi.alipay.com/gateway.do'
        else:
            gateway = 'http://notify.alipay.com/trade/notify_query.do'
        verify_url = "%s?%s" % (gateway, urlencode(params))
        verify_result = urlopen(verify_url).read()

        if verify_result.lower().strip() == 'true':

            tn = tree.find("out_trade_no").text
            try:
                order = None
                tn = tn.split(',')
                for n in tn:
                    orders = Order.select().where(Order.ordernum == n)
                    if orders.count() > 0:
                        order = orders[0]
                    if order and order.status == 0:
                        order.status = 1
                        order.pay_account = tree.find("buyer_email").text
                        order.trade_no = tree.find("trade_no").text
                        order.save()

                        order_Item = ''
                        cartProducts = OrderItem.select().where(OrderItem.order == order)
                        for n in cartProducts:
                            if n.product.categoryfront.type == '2':
                                sn = 1
                                for s in range(n.quantity):
                                    sn = sn + s
                                    seed = "1234567890"
                                    sa = []
                                    for i in range(12):
                                        sa.append(random.choice(seed))
                                        salt = ''.join(sa)
                                    OrderItemService.create(order_item=n.id, sn=sn, service_code=salt, service_used=0, store=order.store, user=order.user)
                        # try:
                        #     admins = AdminUser.select().where(AdminUser.roles % '%Y%')
                        #     receivers = [n.email for n in admins if len(n.email)>0]
                        #     email = {u'receiver': receivers, u'subject':u'用户下单成功',u'body': u"支付方式：在线支付；<br/>订单编号为：" + n + u"；<br>订单金额："+ str(order.currentprice) + u"；<br>订单详情："+order_Item}
                        #     create_msg(simplejson.dumps(email), 'email')
                        # except Exception, e:
                        #     print e

            except Exception, ex:
                logging.error(ex)


            return order_params
    return False


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
