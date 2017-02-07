#!/usr/bin/env python
# coding=utf8

DEBUG = True
GZIP = True

DB_PORT = 3306
DB_HOST = '192.168.1.30'
DB_USER = 'carlife_f' #root  magento
DB_PASSWD = '123456'
DB_NAME = 'carlife'
MAX_CONNECTIONS = 300 # mysql 连接池最大数量
STALE_TIMEOUT = 86400 # mysql 连接池回收时间

#MEMCACHE_HOST = '182.92.188.59:11211'
MEMCACHE_HOST = '192.168.1.30:11211'
ADMIN_PAGESIZE = 20
USER_PAGESIZE = 10

ALIPAY_KEY = 'd2fmn3xc7f45bxl21qfjdojhw7q0049t'
ALIPAY_INPUT_CHARSET = 'utf-8'
ALIPAY_PARTNER = '2088221897731280'
ALIPAY_SELLER_EMAIL = 'pay.chezhuangjia@520czj.com'
ALIPAY_SIGN_TYPE = 'MD5'
ALIPAY_AUTH_URL = 'http://127.0.0.1:8889/oauth/alipay_return'
ALIPAY_RETURN_URL = 'http://127.0.0.1:8889/alipay/return'
ALIPAY_NOTIFY_URL = 'http://127.0.0.1:8889/alipay/notify'
ALIPAY_RETURN_CZ_URL = 'http://127.0.0.1:8889/alipay/return_cz'
ALIPAY_NOTIFY_CZ_URL = 'http://127.0.0.1:8889/alipay/notify_cz'
ALIPAY_SHOW_URL = ''
ALIPAY_TRANSPORT = 'https'
ALIPAY_RETURN_PAY_NOTIFY_URL = 'http://127.0.0.1:8889/alipay/pay_back/notify'

COM_TEL='4006904200' #客服热线

MQSERVER = '123.56.94.179'
MQPORT = '5672'
MQUSER = 'guest'
MQPASSWORD='520czj90-='
MQEXCHANGENAME='czj_exchange'
MQQUEUENAME='czj_queue'
MQROUTINGKEY = 'czj_routing_key'

presentToA = u'车主'
presentToB = u'修理厂'

financeMobiles = '17791812996,18729368422' #王琳，吴静
serviceMobiles = '13323560933,13891949153' #余飞（银川），马玉霞，
ShanXiIphone = '18503516282' #山西服务商保险支付成功短信

deadlineTime = 86400    # 一天86400秒
remark_ZhouKou=u'大地车险承保仅限15万以内家庭使用非营运客车车辆'

