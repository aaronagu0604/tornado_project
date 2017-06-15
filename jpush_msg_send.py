#!/usr/bin/env python
# coding=utf8

from model import JPushPlan, User, Store, InsuranceOrder, InsuranceOrderPrice
from bootloader import memcachedb
from lib.mqhelper import create_msg
import time


class JPushSend():
    def check_time(self, send_time, rate):
        localtime = time.localtime()
        week = time.strftime('%w', localtime)
        date = time.strftime('%Y-%m-%d', localtime)
        now_time = time.strftime('%H:%M', localtime)
        if '0' == rate:
            check_rate = True
        elif week in rate.split(','):
            check_rate = True
        elif date == rate:
            check_rate = True
        else:
            check_rate = False
        if send_time == now_time:
            return check_rate
        else:
            return False

    def get_checked_msg(self):
        plan_keys = memcachedb.get('plan_keys')
        plans_dict = memcachedb.get_multi(plan_keys)
        for key, plan in plans_dict.items():
            if plan.admin_check == 1 and self.check_time(plan.time, plan.rate):
                # create_msg('', 'jpush')
                memcachedb.delete(key)
                plan_keys.remove(key)
                memcachedb.replace('plan_keys', plan_keys)










