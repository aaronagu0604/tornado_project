#!/usr/bin/env python
# coding=utf-8

import re
import time
from peewee import *
import hashlib
from bootloader import db
from playhouse.signals import post_save
from lib.util import vmobile
import logging
import setting


# logger = logging.getLogger('peewee')
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())


# 用户表
class User(db.Model):
    id = PrimaryKeyField()  # 主键
    username = CharField(unique=True, max_length=64, null=False)  # 注册用户名
    mobile = CharField(max_length=12)  # 注册手机号
    email = CharField(max_length=128, default='')  # email
    password = CharField(max_length=32)  # 密码
    nickname = CharField(max_length=32, default='')  # 昵称
    gender = IntegerField(default=2)  # 性别 0男 1女 2未知
    qq = CharField(max_length=15, default='')  # qq
    birthday = DateField(null=True)  # 生日
    tel = CharField(max_length=30, null=True, default='')  # 固定电话
    balance = FloatField(default=0)  # 用户账户余额
    cashed_money = FloatField(default=0)  # 用户账户可提现余额
    isactive = IntegerField(default=1)  # 用户组 0被禁止的用户 1正常用户
    signuped = IntegerField(default=0)  # 注册时间
    signupeddate = CharField(max_length=16)  # 注册日期，文本格式
    signupedtime = CharField(max_length=16)  # 注册时间，文本格式
    lsignined = IntegerField(default=0)  # 最后登录时间
    phoneactived = IntegerField(default=0)  # 0代表网站注册 1代表手机端注册 2代表后台经销商注册
    emailactived = IntegerField(default=0)  # 激活邮箱 0未 1已激活
    portraiturl = CharField(max_length=128, null=True, default='')  # 用户头像

    score = IntegerField(default=0)  # 用户积分
    gift = CharField(max_length=20, default='00')  # 礼品赠送 00未获取 10获取注册礼品 01获取首单礼品 11获取注册和首单礼品
    level = IntegerField(default=0) # 累计积分 会员等级 2000以内优先会员 2001-4000铜卡会员 4001-6000金卡会员 6001-8000白金会员 8000+钻石会员
    raffle_count = IntegerField(default=0)  # 抽奖次数

    grade = IntegerField(default=0) # 用户分级，0普通C 端用户，1门店B端用户，2厂商A端用户，3代理商用户， 4银行服务商， 5代理商可以处理保险订单
    # levelid = IntegerField(default=1) # 会员等级
    # userlevel = ForeignKeyField(UserLevel, related_name='userlevel',
    #                        db_column='levelid',default=1)  # 外键到tb_user_level表，字段名为levelid，从tb_user_level引用为userlevel
    levelstart = IntegerField(default=0) # 用户等级开始时间
    levelend = IntegerField(default=0) # 用户结束开始时间
    # store = ForeignKeyField(Store, related_name='user_store', db_column='store_id', null=True)  #所属店铺
    alipay_truename = CharField(max_length=32, default='')  # 支付宝姓名
    alipay_account = CharField(max_length=128, default='')  # 支付宝账号
    bank_truename = CharField(max_length=32, default='')  # 银行卡姓名
    bank_account = CharField(max_length=32, default='')  # 银行卡号
    bank_name = CharField(max_length=64, default='')  # 银行名称
    bank_branchname = CharField(max_length=64, default='')  # 支行名称

    @staticmethod
    def create_password(raw):
        return hashlib.new("md5", raw).hexdigest()

    def check_password(self, raw):
        return hashlib.new("md5", raw).hexdigest() == self.password

    def check_mobile_password(self, raw):
        return raw == self.password

    def validate(self):
        if vmobile(self.username):
            self.mobile = self.username
            if User.select().where(User.username == self.username).count() > 0:
                raise Exception('此账号已经注册')
        else:
            raise Exception('请输入正确的手机号码或邮寄地址')

    class Meta:
        db_table = 'tb_users'


def initDB():
    from lib.util import find_subclasses

    models = find_subclasses(db.Model)
    for model in models:
        if model.table_exists():
            print model
            model.drop_table()
        model.create_table()

if __name__ == '__main__':
    pass

