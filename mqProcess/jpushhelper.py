#!/usr/bin/env python
# coding=utf8

import jpush as jpush
import logging
import setting


# apptype:1车装甲app
def pushsinglemsg(apptype, body, receiver):

    _jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
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
    for n in receivers:
        try:
            pushsinglemsg(apptype, body, n)
        except Exception, e:
            logging.info('fail:'+n+' '+e.message)


if __name__ == '__main__':
    pushmsg(4, u'python 测试2', ["18189279823"])  #13239109398  18189279823 {"alias":["18189279823","13239109398"]}
