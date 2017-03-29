#!/usr/bin/env python
# coding=utf8

import jpush as jpush
import logging
import setting

_jpush = jpush.JPush(setting.jpush_key, setting.jpush_secret)
device = _jpush.create_device()


# 设置设备信息（标签与别名）
def set_device_info(regist_id, tags=[], alias=None):
    reg_id = regist_id
    entity = {}

    if tags:
        entity['tag'] = {'add': tags}
    if alias:
        entity['alias'] = alias

    result = device.set_deviceinfo(reg_id, entity)
    print (result.status_code)
    print (result.payload)


# 根据标标签推送
def send_users_base_tags(tags,type):
    push = _jpush.create_push()

    push.audience = jpush.audience()
    push.audience['tag'] = tags
    push.platform = jpush.all_
    push.notification = jpush.notification(alert="Hello world with audience!")

    push.send()


# 根据别名推送
# type:1代表通知,2代表透传
NOTIFICATION = 1
MESSAGE = 2
def get_users_from_alias(alias, type, **kwargs):
    push = _jpush.create_push()

    push.audience = jpush.audience()
    push.audience['alias'] = alias
    push.platform = jpush.all_
    push.options = {"apns_production": False}

    if type == NOTIFICATION:
        set_notification_body(push, alert)
    elif type == MESSAGE:
        set_message_body(push, title, content_type, content, extras)
    else:
        raise TypeError('push type is undifined!')

    push.send()


# 设置通知消息体
def set_notification_body(push, alert):
    ios_msg = jpush.ios(alert=alert)
    android_msg = jpush.android(alert=alert)

    push.notification = jpush.notification(alert=alert, android=android_msg, ios=ios_msg)


# 设置透传（自定义）消息体
def set_message_body(push, title, content_type, content, extras):
    message = jpush.message(
        title=title,
        content_type=content_type,
        msg_content=content,
        extras=extras
    )

    push.message = message


if __name__ == '__main__':
    pass
