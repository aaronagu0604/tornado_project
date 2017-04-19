#!/usr/bin/env python
# coding=utf8

import jpush as jpush
import logging
import setting

_jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
device = _jpush.create_device()

'''
# 设置设备信息（标签与别名）
@ apiParam {String} regist_id jpush标识符
@ apiParam {list} tags 推送标签列表
@ apiParam {String} alias 推送别名
'''
def set_device_info(regist_id, tags=[], alias=None):
    reg_id = regist_id
    entity = {}

    if tags:
        entity['tag'] = _jpush.divece(tags)
    if alias:
        entity['alias'] = alias

    result = device.set_deviceinfo(reg_id, entity)

'''
# 根据标标签推送
@ apiParam {list} tags 推送标记列表
@ apiParam {String} body 消息文本
'''
def send_users_base_tags(tags, body):
    push = _jpush.create_push()
    push.audience = jpush.audience()
    push.audience['tag'] = tags
    push.platform = jpush.all_

    ios_msg = jpush.ios(alert=body, badge="+1", sound="a.caf", extras={'k1': 'v1'})
    android_msg = jpush.android(alert=body)
    push.notification = jpush.notification(alert=body, android=android_msg, ios=ios_msg)

    push.send()
'''
# 根据别名推送
@ apiParam {String} alias 用户别名
@ apiParam {String} body 消息文本
'''
def send_users_base_alias(alias, body):
    push = _jpush.create_push()
    alias = {"alias": [alias]}
    push.audience = jpush.audience(alias)

    ios_msg = jpush.ios(alert=body, badge="+1", sound="a.caf", extras={'k1': 'v1'})
    android_msg = jpush.android(alert=body)
    push.notification = jpush.notification(alert=body, android=android_msg, ios=ios_msg)

    push.platform = jpush.all_
    push.send()

if __name__ == '__main__':
    regist=None
    tags = []
    alias = None
    set_device_info(regist,tags,alias)
    send_users_base_alias(alias, 'ceshi for jpush base alias')
    send_users_base_tags(tags,'ceshi for jpush base tags')
