import rabbitpy
from sys import path

path.append(r"../")
import setting
import logging


def create_msg(body, type):
    try:
        url = 'amqp://' + setting.MQUSER + ':' + setting.MQPASSWORD + '@' + setting.MQSERVER + ':' + setting.MQPORT + '/%2f'
        with rabbitpy.Connection(url) as conn:
            with conn.channel() as channel:
                exchange = rabbitpy.Exchange(channel=channel, name=setting.MQEXCHANGENAME, durable=True)
                exchange.declare()
                queue = rabbitpy.Queue(channel=channel, name=setting.MQQUEUENAME, durable=True)
                queue.declare()
                queue.bind(exchange, setting.MQROUTINGKEY)  # Bind the queue
                message = rabbitpy.Message(channel, body, {'content_type': 'text/plain', 'delivery_mode': 2, 'message_type': type})
                message.publish(exchange, setting.MQROUTINGKEY)
    except Exception, err:
        logging.info('Error: send message error:%s' % err)