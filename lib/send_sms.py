#!/usr/bin/env python
# coding=utf8

import simplejson
from model import User
from mqhelper import create_msg


def send_sms_for_all_users(content):
    users = User.select(User.mobile).where(User.isactive == 1).dicts()

    mobiles = ''
    for u in users:
        #获取所有用户手机号码并于英文逗号隔开
        if len(u['mobile']) == 11:
            mobiles += u['mobile'] + ','
    j = 0
    #每次发送号码不能大于600个 7200字符
    while j < (users.count() + 599) / 600:
        if len(mobiles) > 7200:
            cells = mobiles[0:7200]
        else:
            cells = mobiles
        sms = {'mobile': cells, 'body': content, 'signtype': '1', 'isyzm': ''}
        create_msg(simplejson.dumps(sms), 'sms')
        #删除已发送的手机号码
        mobiles = mobiles[(j+1)*7200:]
        j += 1

    # for u in users:
    #     if len(u['mobile']) == 11:
    #         sms = {'mobile': u['mobile'], 'body': content, 'signtype': '1', 'isyzm': ''}
    #         create_msg(simplejson.dumps(sms), 'sms')
def send_sms_for_group_users(content, grade):
    if int(grade) > -1:
        users = User.select(User.mobile).where((User.grade == grade) & (User.isactive == 1)).dicts()

        mobiles = ''
        for u in users:
            #获取所有用户手机号码并于英文逗号隔开
            if len(u['mobile']) == 11:
                mobiles += u['mobile'] + ','
        j = 0
        #每次发送号码不能大于600个 7200字符
        while j < (users.count() + 599) / 600:
            if len(mobiles) > 7200:
                cells = mobiles[0:7200]
            else:
                cells = mobiles
            sms = {'mobile': cells, 'body': content, 'signtype': '1', 'isyzm': ''}
            create_msg(simplejson.dumps(sms), 'sms')
            #删除已发送的手机号码
            mobiles = mobiles[(j+1)*7200:]
            j += 1

        # for u in users:
        #     if len(u['mobile']) == 11:
        #         sms = {'mobile': u['mobile'], 'body': content, 'signtype': '1', 'isyzm': ''}
        #         create_msg(simplejson.dumps(sms), 'sms')

def send_jpush_for_all_users(content):
    users = User.select(User.mobile).where(User.isactive == 1).dicts()
    for u in users:
        if len(u['mobile']) == 11:
            sms = {'apptype': 1, 'body': content, 'receiver': [u['mobile']]}
            create_msg(simplejson.dumps(sms), 'jpush')

def send_jpush_for_group_users(content, grade):
    if int(grade) > -1:
        users = User.select(User.mobile).where((User.grade == grade) & (User.isactive == 1)).dicts()
        for u in users:
            if len(u['mobile']) == 11:
                sms = {'apptype': 1, 'body': content, 'receiver': [u['mobile']]}
                create_msg(simplejson.dumps(sms), 'jpush')

if __name__ == '__main__':
    try:

        print 'ok'
    except Exception, e:
        print e
