#!/usr/bin/env python
# coding=utf8

import time
from model import JPushPlan, User, Store, InsuranceOrder, InsuranceOrderPrice
from bootloader import memcachedb


class JPushSearch():
    # 新注册的门店
    def __init__(self):
        self.all_stores = Store.select().where(Store.active == 1)

    def new_store(self):
        now = int(time.time())
        start_time = now - 604800
        store = []
        for s in self.all_stores:
            if s.created > start_time:
                store.append({
                    'id': s.id,
                    'name': s.name,
                    'mobile': s.mobile,
                    'area_code': s.area_code
                })
        return store

    # 经常下保单的门店（条件：一个月内下过保单的门店，返佣返油多的就是经常返油）
    def often_create_io_store(self):
        io_lube_store = []
        io_cash_store = []
        for s in self.all_stores:
            io_lube_count = InsuranceOrder.select().join(InsuranceOrderPrice).\
                where((InsuranceOrder.store == s) & (InsuranceOrderPrice.gift_policy == 1)).count()
            io_cash_count = InsuranceOrder.select().join(InsuranceOrderPrice).\
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

    # 计划
    def search_plan(self):
        '''
        jpush_list = [
            {
                'store': [{'id':1, 'name': '小毛汽修', 'mobile': '110'}, {}],
                'title': u'新用户注册',
                'time': '10:30',
                'rate': '0',
                'intro': 1,
                'admin_check': 0
            },
        {}, {}]
        '''
        # 删除上一次的所有计划
        try:
            plan_keys = memcachedb.get('plan_keys')
            if plan_keys:
                for key in plan_keys:
                    memcachedb.delete(key)
                memcachedb.delete('plan_keys')
        except Exception, e:
            pass
        # 开始本次计划
        plan_keys = []
        io_lube_store, io_cash_store = self.often_create_io_store()
        for plan in JPushPlan.select().where(JPushPlan.active == 1):
            store = []
            if plan.type == 1:    # 新注册用户jpush 计划
                # store = self.new_store()
                store = [{'id':1, 'name': '小毛汽修', 'mobile': '110'}]
                this_plan_key = 'plan_1'
            elif plan.type == 2:    # 经常出单用户（返油）jpush计划
                store = io_lube_store
                this_plan_key = 'plan_2'
            elif plan.type == 3:    # 经常出单用户（返现）jpush计划
                store = io_cash_store
                this_plan_key = 'plan_3'
            elif plan.type == 4:
                pass
            elif plan.type == 5:
                pass
            elif plan.type == 6:
                pass
            elif plan.type == 7:
                pass
            if store:
                plan_keys.append(this_plan_key)
                print('this_plan_key=%s, value=%s' % (this_plan_key, str(store)))
                memcachedb.set(this_plan_key, {
                    'title': plan.title,
                    'time': plan.time,
                    'rate': plan.rate,
                    'intro': plan.intro.id,
                    'admin_check': 0,
                    'store': store
                })
        memcachedb.set('plan_keys', plan_keys)
        print('--plan_keys: %s--' % str(plan_keys))

if __name__ == '__main__':
    jpush = JPushSearch()
    jpush.search_plan()

