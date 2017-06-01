# -*- coding: utf-8 -*-
from setting import domanName

class Settings:
    # 安全检验码，以数字和字母组成的32位字符
    KEY = 'd2fmn3xc7f45bxl21qfjdojhw7q0049t'

    INPUT_CHARSET = 'utf-8'

    # 合作身份者ID，以2088开头的16位纯数字
    PARTNER = '2088221897731280'

    # 签约支付宝账号或卖家支付宝帐户
    SELLER_EMAIL = 'pay.chezhuangjia@520czj.com'

    SIGN_TYPE = 'MD5'

    # 付完款后跳转的页面（同步通知） 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
    RETURN_URL = domanName+'/mobile/alipay_callback'

    # 交易过程中服务器异步通知的页面 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
    NOTIFY_URL = domanName+'/mobile/alipay_notify_web'

    SHOW_URL = ''

    # 访问模式,根据自己的服务器是否支持ssl访问，若支持请选择https；若不支持请选择http
    TRANSPORT = 'https'

    #签名方式 不需修改
    #ALIPAY_KEY_SIGN_TYPE = '0001'
    KEY_SIGN_TYPE = 'MD5'

    GATEWAY = 'https://mapi.alipay.com/gateway.do'

    #商户的私钥（后缀是.pen）文件相对路径
    #如果签名方式设置为“0001”时，请设置该参数
    #PRIVATE_KEY_PATH = 'key/rsa_private_key.pem'

    #支付宝公钥（后缀是.pen）文件相对路径
    #如果签名方式设置为“0001”时，请设置该参数
    #PUBLIC_KEY_PATH = 'key/alipay_public_key.pem'

    #ca证书路径地址，用于curl中ssl校验
    #请保证cacert.pem文件在当前文件夹目录中
    #CACERT = 'cacert.pem'

    # 充值同步回调，没做接口哈哈
    CZ_RETURN_URL = domanName+'/mobile/alipay_cz_callback'

    # 交易过程中服务器异步通知的页面 要用 http://格式的完整路径，不允许加?id=123这类自定义参数 web支付充值回调
    CZ_NOTIFY_URL = domanName+'/mobile/alipay_cz_notify_web'














