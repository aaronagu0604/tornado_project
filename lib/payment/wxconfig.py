# -*- coding: utf-8 -*-
from setting import domanName

class WxPayConf_pub(object):
    """配置账号信息"""
    #=======【基本信息设置】=====================================
    #微信公众号身份的唯一标识。审核通过后，在微信发送的邮件中查看
    #APPID = "wxf23313db028ab4bc"
    APPID = "wxe95fa6f70d164037"
    #JSAPI接口中获取openid，审核后在公众平台开启开发模式后可查看 app secret
    #APPSECRET = "06da33df9bb7533e8473485c2f03727c"
    APPSECRET = "e8e606893df50d285a3f8c8a79d55752"
    #受理商ID，身份标识
    #MCHID = "1339093201"
    MCHID = "1376028002"
    #商户支付密钥Key。审核通过后，在微信发送的邮件中查看
    #KEY = "520chezhuangjiawangluokeji520czj"
    KEY = "520chezhuangjiawangluokejiczj520"

    #=======【异步通知url设置】===================================
    #异步通知url，商户根据实际开发过程设定
    NOTIFY_URL = domanName+"/mobile/weixin_notify"
    CZ_NOTIFY_URL = domanName+"/mobile/weixin_cz_notify"

    #=======【JSAPI路径设置】===================================
    #获取access_token过程中的跳转uri，通过跳转将code传入jsapi支付页面
    JS_API_CALL_URL = domanName+"/pay/?showwxpaytitle=1"

    #=======【证书路径设置】=====================================
    #证书路径,注意应该填写绝对路径
    SSLCERT_PATH = "/home/www/workspace/eofan/src/cacert/apiclient_cert.pem"
    SSLKEY_PATH = "/home/www/workspace/eofan/src/cacert/apiclient_key.pem"

    #=======【curl超时设置】===================================
    CURL_TIMEOUT = 30

    #=======【HTTP客户端设置】===================================
    HTTP_CLIENT = "CURL"  # ("URLLIB", "CURL")
