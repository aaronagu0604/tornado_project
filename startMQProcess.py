#!/usr/bin/env python
# coding=utf-8

import logging
import time

import rabbitpy
import simplejson

import mqProcess.setting
from dayuSms import sendmsg
from mqProcess.emailhelper import sendemail
from mqProcess.jpushhelper import pushmsg

logger = logging.getLogger('startMQProcess')
logger.addHandler(logging.StreamHandler())

url = 'amqp://' + mqProcess.setting.MQUSER + ':' + mqProcess.setting.MQPASSWORD + '@' + mqProcess.setting.MQSERVER + ':' + mqProcess.setting.MQPORT + '/%2f'

with rabbitpy.Connection(url) as conn:
    with conn.channel() as channel:
        queue = rabbitpy.Queue(channel, mqProcess.setting.MQQUEUENAME)
        try:
            for message in queue.consume_messages():
                try:
                    if message.properties['message_type'] == 'sms':
                        sms = simplejson.loads(message.body)
                        try:
                            sendmsg(sms['mobile'], sms['body'], sms['isyzm'])
                        except Exception, e:
                            logging.error(e.message)
                    elif message.properties['message_type'] == 'email':
                        email = simplejson.loads(message.body)
                        sendemail(email['receiver'], email['subject'], email['body'])
                    elif message.properties['message_type'] == 'jpush':
                        pushcontent = simplejson.loads(message.body)
                        try:
                            logging.error(pushcontent['apptype'])
                            logging.error(pushcontent['body'])
                            logging.error(pushcontent['receiver'])

                            pushmsg(1, pushcontent['body'], pushcontent['receiver'])
                        except Exception, e:
                            logging.error(e.message)
                    else:
                        logging.error('unknown msg type: ' + message.properties['message_type'] + ' body:' + message.body)
                    message.ack()
                    time.sleep(1)
                except Exception, ex:
                    logging.error(ex)
        except KeyboardInterrupt:
            logging.error('Exited consumer')
