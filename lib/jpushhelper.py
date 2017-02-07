#!/usr/bin/env python
# coding=utf8

import jpush as jpush


# apptype:1车装甲 2车装甲采购 3车装甲采价，4内部系统
def pushsinglemsg(apptype, body, receiver):
    key = 'bb9fc37f914d94589c6d7c4d'
    secret = '0b058bd331eae435fa38f20e'
    if apptype == 2:
        key = '382c5d880cae31ec81df46ff'
        secret = 'ac37c4c44a0b83539d469464'
    elif apptype == 3:
        key = '28e20ce5dcfd49511309806a'
        secret = 'b05bdc47c2cb686850a6c766'
    elif apptype == 4:
        key = '3c7971b2e03ef0f0df5c70b2'
        secret = 'ff57774954b9ed1f0771cef4'
    _jpush = jpush.JPush(key, secret)
    push = _jpush.create_push()
    push.audience = jpush.audience(
        jpush.alias(receiver))

    ios_msg = jpush.ios(alert=body, badge="+1", sound="a.caf", extras={'k1': 'v1'})
    android_msg = jpush.android(alert=body)
    push.notification = jpush.notification(alert=body, android=android_msg, ios=ios_msg)

    push.platform = jpush.all_
    push.options = {"apns_production": False}
    re = push.send()
    print re


def pushmsg(apptype, body, receivers):
    f=open('/home/www/workspace/eofan/log/out.txt','w')
    for n in receivers:
        try:
            pushsinglemsg(apptype, body, n)
            print >> f, 'success:'+n
        except Exception, e:
            print >> f, 'fail:'+n+' '+e.message
    f.close()

if __name__ == '__main__':
    pushmsg(4, u'python 测试2', ["18189279823"])  #13239109398  18189279823 {"alias":["18189279823","13239109398"]}
