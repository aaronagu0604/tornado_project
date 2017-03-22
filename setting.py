#!/usr/bin/env python
# coding=utf8


DEBUG = True
GZIP = True

DB_PORT = 3306
DB_HOST = '123.56.94.179'
DB_USER = 'root'
DB_PASSWD = '6V^efYdy'
DB_NAME = 'czj'
MAX_CONNECTIONS = 300  # mysql 连接池最大数量
STALE_TIMEOUT = 432000  # mysql 连接池回收时间 (5天)

MEMCACHE_HOST = '127.0.0.1:11211'

ADMIN_PAGESIZE = 20  # 管理后台页面数据条数
USER_PAGESIZE = 10  # 商家后台页面数据条数
MOBILE_PAGESIZE = 20  # 移动端数据条数

COM_TEL = '4006904200'  # 客服热线

MQSERVER = '127.0.0.1'
MQPORT = '5672'
MQUSER = 'guest'
MQPASSWORD = '1q2w3e4R'
MQEXCHANGENAME = 'czj_exchange'
MQQUEUENAME = 'czj_queue'
MQROUTINGKEY = 'czj_routing_key'

presentToA = u'车主'
presentToB = u'修理厂'

ORDERBEGIN = 145667520000

financeMobiles = '17791812996,18729368422'  # 王琳，吴静
serviceMobiles = '13323560933,13891949153'  # 余飞（银川），马玉霞，
ShanXiIphone = '18503516282'  # 山西服务商保险支付成功短信

INSURANCE_ORDER_TIME_OUT = 60 * 60 * 24 * 1  # 保险订单超时时间
PRODUCT_ORDER_TIME_OUT = 60 * 60 * 24 * 3  # 普通订单超时时间

user_expire = 60 * 60 * 24 * 10  # 用户登录token保留时间， 默认保留10天
user_token_prefix = "mt:"  # 用户登录token的前缀

CASH_MIN_MONEY = 0  # 积分兑现最小金额
CASH_RATE = 1.0  # 积分兑现比率 money = score * cashRate

def get_help_center_remark(area_code):
    if area_code[:8] == '00160016':
        return '大地车险承保仅限15万以内家庭使用非营运客车车辆'
    else:
        return ''


typeface = '/home/www/workspace/eofan/src/simsun.ttc'
popularizePIC = [{
    'activity': 'repairCar',
    'area_code': '00',
    'basePicPath': '/home/www/workspace/eofan/src/upload/popularizePIC/repairCar.png',
    'PicPath': '/home/www/workspace/eofan/src/upload/popularizePIC/repairCar',
    'wordSize':30,
    'wordColour': (255, 255, 255),
    'storeWidth': 96,
    'storeHeight': 924,
    'addrWidth': 96,
    'addrHeight': 1016,
    'addr2tab':25,
    'addr2Width': 182,
    'addr2Height': 1057,
    'phoneWidth': 96,
    'phoneHeight': 1133
},{
    'activity': 'happyNewYear',
    'area_code': '00',
    'basePicPath': '/home/www/workspace/eofan/src/upload/popularizePIC/happyNewYear.png',
    'PicPath': '/home/www/workspace/eofan/src/upload/popularizePIC/happyNewYear',
    'wordSize':30,
    'wordColour': (255, 255, 255),
    'storeWidth': 96,
    'storeHeight': 924,
    'addrWidth': 96,
    'addrHeight': 1016,
    'addr2tab':25,
    'addr2Width': 182,
    'addr2Height': 1057,
    'phoneWidth': 96,
    'phoneHeight': 1133
},{
    'activity': 'insurance',
    'area_code': '00',
    'basePicPath': '/home/www/workspace/eofan/src/upload/popularizePIC/insurance.png',
    'PicPath': '/home/www/workspace/eofan/src/upload/popularizePIC/insurance',
    'wordSize':30,
    'wordColour': (255, 255, 255),
    'storeWidth': 96,
    'storeHeight': 925,
    'addrWidth': 96,
    'addrHeight': 1016,
    'addr2tab':25,
    'addr2Width': 182,
    'addr2Height': 1057,
    'phoneWidth': 96,
    'phoneHeight': 1133
}]


