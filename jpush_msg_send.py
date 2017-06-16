#!/usr/bin/env python
# coding=utf8

import time
import simplejson
from model import JPushMsg, JPushPlan, User, Store, InsuranceOrder, InsuranceOrderPrice, JPushRecord
from lib.mqhelper import create_msg


class JPushSend():
    # 新注册的门店
    def __init__(self):
        self.all_stores = Store.select().where(Store.active == 1)

    def new_store(self):
        now = int(time.time())
        start_time = now - 604800
        store = []
        for s in self.all_stores:
            if s.created > start_time:
                store.append(s.mobile)
        return store

    # 经常下保单的门店（条件：一个月内下过保单的门店，返佣返油多的就是经常返油）
    def often_create_io_store(self):
        io_lube_store = []
        io_cash_store = []
        for s in self.all_stores:
            io_lube_count = InsuranceOrder.select().join(InsuranceOrderPrice). \
                where((InsuranceOrder.store == s) & (InsuranceOrderPrice.gift_policy == 1)).count()
            io_cash_count = InsuranceOrder.select().join(InsuranceOrderPrice). \
                where((InsuranceOrder.store == s) & (InsuranceOrderPrice.gift_policy == 2)).count()
            if io_lube_count >= io_cash_count:
                io_lube_store.append({
                    'id': s.id,
                    'name': s.name,
                    'mobile': s.mobile,
                    'area_code': s.area_code
                })
            else:
                io_cash_store.append({
                    'id': s.id,
                    'name': s.name,
                    'mobile': s.mobile,
                    'area_code': s.area_code
                })
        return io_lube_store, io_cash_store

    # 活动推送
    def active(self):
        pass

    def get_checked_msg(self):
        now = time.time()
        need_send_msgs = JPushRecord.select().where((JPushRecord.start_time <= now) & (now <= JPushRecord.end_time) &
                                                    (JPushRecord.check == 1) & (JPushRecord.send == 1))
        for msg in need_send_msgs:
            mobile = []
            if msg.type == 1:  # 新注册用户jpush 计划
                # mobile = self.new_store()
                mobile = [1, 2, 555]
            elif msg.type == 2:  # 经常出单用户（返油）jpush计划
                mobile = self.often_create_io_store('lube')
            elif msg.type == 3:  # 经常出单用户（返现）jpush计划
                mobile = self.often_create_io_store('cash')
            elif msg.type == 4:
                pass
            elif msg.type == 5:
                pass
            elif msg.type == 6:
                pass
            elif msg.type == 7:
                pass
            if msg.intro.static:
                link = 'http://admin.520czj.com/user/showarticle/%d' % msg.intro.id
                j = 0
                jpush_msg = JPushMsg.get(id=msg.intro.id)
                while j*1000 < len(mobile):
                    sms = {'apptype': 1, 'body': jpush_msg.content, 'jpushtype': 'alias', 'extras': {'link': link},
                           'alias': mobile[j*1000:(j+1)*1000], 'images': jpush_msg.img_url}
                    create_msg(simplejson.dumps(sms), 'jpush')
                    j += 1
            else:    # 动态url
                pass







