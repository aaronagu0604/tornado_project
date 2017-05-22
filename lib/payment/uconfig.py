# -*- coding: utf-8 -*-
from setting import domanName
setting = {
    # 银联相关
    # 签名证书路径
    'SDK_SIGN_CERT_PATH': '/var/lib/jenkins/jobs/czj/workspace/lib/payment/upayfile/czj.pfx',
    # 签名证书密码
    'SDK_SIGN_CERT_PWD': '890604',
    # 验签证书路径
    'SDK_VERIFY_CERT_DIR': '/home/www/workspace/eofan/src/lib/payment/upayfile/',
    # 前台请求地址
    'SDK_FRONT_TRANS_URL': 'https://gateway.95516.com/gateway/api/frontTransReq.do',
    # 后台请求地址
    'SDK_BACK_TRANS_URL': 'https://gateway.95516.com/gateway/api/backTransReq.do',
    # 批量交易
    'SDK_BATCH_TRANS_URL': 'https://gateway.95516.com/gateway/api/batchTrans.do',
    # 单笔查询请求地址
    'SDK_SINGLE_QUERY_URL': 'https://gateway.95516.com/gateway/api/queryTrans.do',
    # 文件传输请求地址
    'SDK_FILE_QUERY_URL': 'https://filedownload.95516.com/',
    # 有卡交易地址
    'SDK_Card_Request_Url': 'https://gateway.95516.com/gateway/api/cardTransReq.do',
    # App交易地址
    'SDK_App_Request_Url': 'https://gateway.95516.com/gateway/api/appTransReq.do',
    # 前台通知地址 (商户自行配置通知地址)
    'SDK_FRONT_NOTIFY_URL': domanName+'/respone/return',
    # 后台通知地址 (商户自行配置通知地址，需配置外网能访问的地址)
    'SDK_BACK_NOTIFY_URL': domanName+'/mobile/upay_notify',
    # 后台通知地址 for 充值
    'CZ_SDK_BACK_NOTIFY_URL': domanName+'/mobile/upay_cz_notify',
}
