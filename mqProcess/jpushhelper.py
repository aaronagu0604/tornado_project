#!/usr/bin/env python
# coding=utf8

import jpush
import setting

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
        entity['alias'] = alias
    print entity
    result = device.set_deviceinfo(reg_id, entity)


'''
# 根据标标签推送
@ apiParam {list} tags 推送标记列表
@ apiParam {String} body 消息文本
'''
def send_users_base_tags(tags, body, extras = None):
    _jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
    push = _jpush.create_push()
    push.audience = jpush.audience()
    push.audience['tag'] = tags
    push.platform = jpush.all_

    if extras:
        ios_msg = jpush.ios(alert=body, badge="+1", sound="a.caf", extras=extras)
        android_msg = jpush.android(alert=body, extras=extras)
    else:
        ios_msg = jpush.ios(alert=body, badge="+1", sound="a.caf")
        android_msg = jpush.android(alert=body)
    push.notification = jpush.notification(alert=body, android=android_msg, ios=ios_msg)
    push.payload['options'] = {
        "apns_production": False
    }
    print push.payload
    result = push.send()
    print result.payload


'''
# 根据别名推送
@ apiParam {String} alias 用户别名
@ apiParam {String} body 消息文本
'''
def send_users_base_alias(alias, body, extras = None):
    _jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
    push = _jpush.create_push()
    alias1 = {"alias": alias}
    push.audience = jpush.audience(
        alias1
    )

    if extras:
        ios_msg = jpush.ios(alert=body, badge="+1", sound="a.caf", extras=extras)
        android_msg = jpush.android(alert=body, extras=extras)
    else:
        ios_msg = jpush.ios(alert=body, badge="+1", sound="a.caf")
        android_msg = jpush.android(alert=body)
    push.notification = jpush.notification(alert=body, android=android_msg, ios=ios_msg)

    push.platform = jpush.all_
    push.payload['options'] = {
        "apns_production": False
    }
    result = push.send()
    print result.payload

'''
# 根据registrationID推送
@ apiParam {String} reg_id 注册ID
@ apiParam {String} body 消息文本
'''
def send_users_base_regid(reg_id, body, extras = None):
    _jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
    push = _jpush.create_push()
    alias1 = {"registration_id": [reg_id]}
    push.audience = jpush.audience(
        alias1
    )
    if extras:
        ios_msg = jpush.ios(alert=body, badge="+1", sound="a.caf", extras=extras)
        android_msg = jpush.android(alert=body, extras=extras)
    else:
        ios_msg = jpush.ios(alert=body, badge="+1", sound="a.caf")
        android_msg = jpush.android(alert=body)
    push.notification = jpush.notification(alert=body, android=android_msg, ios=ios_msg)

    push.platform = jpush.all_
    push.options = {
        "apns_production": False
    }
    print type(push.payload), push.payload
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
    # getdeviceinfo(regist)
    # set_device_info(regist, tags, alias)
    send_users_base_regid(regist,'ceshi for jpush base registid',{'jumpto':'active', 'value':1})
    # send_users_base_alias(alias, 'ceshi for jpush base alias')
    # send_users_base_tags(tags,'ceshi for jpush base tags')
