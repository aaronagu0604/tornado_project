#!/usr/bin/env python
# coding=utf-8

import logging
import time

import rabbitpy
import simplejson

import setting
from dayuSms import sendmsg
from mqProcess.emailhelper import sendemail
from mqProcess.jpushhelper import send_users_base_alias,send_users_base_tags

logger = logging.getLogger('startMQProcess')
logger.addHandler(logging.StreamHandler())

url = 'amqp://' + setting.MQUSER + ':' + setting.MQPASSWORD + '@' + setting.MQSERVER + ':' + setting.MQPORT + '/%2f'

with rabbitpy.Connection(url) as conn:
    with conn.channel() as channel:
        queue = rabbitpy.Queue(channel, setting.MQQUEUENAME)
        try:
            for message in queue.consume_messages():
                try:
                    if message.properties['message_type'] == 'sms':    # 发短信
                        sms = simplejson.loads(message.body)
                        try:
                            sendmsg(sms['mobile'], sms['body'], sms['isyzm'])
                        except Exception, e:
                            logging.error(e.message)
                    elif message.properties['message_type'] == 'email':    # 发邮件
                        email = simplejson.loads(message.body)
                        sendemail(email['receiver'], email['subject'], email['body'])
                    elif message.properties['message_type'] == 'jpush':    # 极光推送
                        pushcontent = simplejson.loads(message.body)
                        try:
                            if pushcontent['jpushtype'] == 'alias':
                                send_users_base_alias(pushcontent['alias'],pushcontent['body'],pushcontent['extras'])
                            else:
                                send_users_base_tags(pushcontent['tags'],pushcontent['body'],pushcontent['extras'])
                        except Exception, e:
                            logging.error(e.message)
                    elif message.properties['message_type'] == 'pay_success':    # 支付成功
                        logging.info('get pay_success')
                    elif message.properties['message_type'] == 'recharge':    # 充值
                        logging.info('get recharge')
                    elif message.properties['message_type'] == 'append_refund_money':    # 补退款
                        logging.info('get append_refund_money')
                    elif message.properties['message_type'] == 'audit_store':    # 审核门店、经销商，需要配返佣方案
                        logging.info('get audit_store')
                    else:
                        logging.error('unknown msg type: ' + message.properties['message_type'] + ' body:' + message.body)
                    message.ack()
                    time.sleep(1)
                except Exception, ex:
                    logging.error(ex)
        except KeyboardInterrupt:
            logging.error('Exited consumer')
