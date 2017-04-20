#!/usr/bin/env python
# coding=utf8

import jpush
import logging
import setting
import traceback


'''
# 设置设备信息（标签与别名）
@ apiParam {String} regist_id jpush标识符
@ apiParam {list} tags 推送标签列表
@ apiParam {String} alias 推送别名
'''
def set_device_info(regist_id, tags=[], alias=None):
    _jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
    device = _jpush.create_device()
    reg_id = regist_id
    entity = jpush.device_tag(jpush.add("shanxi", "xian"))

    if alias:
        entity['alias'] = alias[0]
    print entity
    result = device.set_deviceinfo(reg_id, entity)


'''
# 根据标标签推送
@ apiParam {list} tags 推送标记列表
@ apiParam {String} body 消息文本
'''
def send_users_base_tags(tags, body):
    _jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
    push = _jpush.create_push()
    push.audience = jpush.audience()
    push.audience['tag'] = tags
    push.platform = jpush.all_

    ios_msg = jpush.ios(alert=body, badge="+1", sound="a.caf", extras={'k1': 'v1'})
    android_msg = jpush.android(alert=body)
    push.notification = jpush.notification(alert=body, android=android_msg, ios=ios_msg)
    print push.payload
    push.send()
'''
# 根据别名推送
@ apiParam {String} alias 用户别名
@ apiParam {String} body 消息文本
'''
def send_users_base_alias(alias, body):
    _jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
    push = _jpush.create_push()
    alias1 = {"alias": alias}
    push.audience = jpush.audience(
        alias1
    )

    ios_msg = jpush.ios(alert=body, badge="+1", sound="a.caf", extras={'k1': 'v1'})
    android_msg = jpush.android(alert=body)
    push.notification = jpush.notification(alert=body, android=android_msg, ios=ios_msg)

    push.platform = jpush.all_
    print push.payload
    push.send()

def send_users_base_regid(reg_id, body):
    _jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
    push = _jpush.create_push()
    alias1 = {"registration_id": [reg_id]}
    push.audience = jpush.audience(
        alias1
    )
    # push.audience = jpush.all_
    ios_msg = jpush.ios(alert=body, badge="+1", sound="a.caf", extras={'k1': 'v1'})
    android_msg = jpush.android(alert=body)
    push.notification = jpush.notification(alert=body, android=android_msg, ios=ios_msg)

    push.platform = jpush.all_
    push.payload['options'] ={
        "apns_production": False
    }
    print push.payload
    result = push.send()
    # result = push.send_validate()
    print result.payload

def aliasuser():
    _jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
    device = _jpush.create_device()
    alias = "guoxiaohong"
    platform = "android,ios"
    print device.get_aliasuser(alias, platform)

def taglist():
    _jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
    device = _jpush.create_device()
    print device.get_taglist()

def getdeviceinfo(reg_id):
    _jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
    device = _jpush.create_device()
    result = device.get_deviceinfo(reg_id)
    print result.payload

if __name__ == '__main__':
    regist='101d85590977d2a2e49'
    tags = ['shanxi', 'xian']
    alias = ['guoxiaohong']
    # aliasuser()
    # taglist()
    getdeviceinfo(regist)
    # set_device_info(regist,tags,alias)
    # send_users_base_regid(regist,'ceshi for jpush base alias')
    # send_users_base_alias(alias, 'ceshi for jpush base alias')
    # send_users_base_tags(tags,'ceshi for jpush base tags')
