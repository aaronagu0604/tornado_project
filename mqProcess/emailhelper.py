#!/usr/bin/env python
# coding=utf8

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import setting


def sendemail(receiver, subject, body):
    msg = MIMEText(body, 'html', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')

    smtp = smtplib.SMTP()
    smtp.connect(setting.email_smtp)
    smtp.login(setting.email_user, setting.email_password)  # 邮件账户登录校验
    smtp.sendmail(setting.email_sender, receiver, msg.as_string())
    smtp.quit()
    print 'send success'


if __name__ == '__main__':
    sendemail('xiaoming.liu@520czj.com', 'python email test 测试', '你好')
