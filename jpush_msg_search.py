#!/usr/bin/env python
# coding=utf8

import time
from model import JPushPlan, JPushRecord


class JPushSearch():
    def get_time(self, start_time, end_time, rate):
        localtime = time.localtime()
        week = time.strftime('%w', localtime)
        date = time.strftime('%Y-%m-%d', localtime)
        print week,date
        if '0' == rate:
            check_rate = True
        elif week in rate.split(','):
            check_rate = True
        elif date == rate:
            check_rate = True
        else:
            check_rate = False
        now_time = time.strftime('%Y-%m-%d', time.localtime())
        start_time = time.mktime(time.strptime(now_time + ' ' + start_time,'%Y-%m-%d %H:%M'))
        end_time = time.mktime(time.strptime(now_time + ' ' + end_time,'%Y-%m-%d %H:%M'))
        print start_time,end_time
        if check_rate:
            return start_time, end_time
        else:
            return 0, 0

    # 计划
    def search_plan(self):
        # 开始本次计划
        created = int(time.time())
        for plan in JPushPlan.select().where(JPushPlan.active == 1):
            start_time, end_time = self.get_time(plan.start_time, plan.end_time, plan.rate)
            jrs = JPushRecord.select().where(JPushRecord.start_time == start_time,
                                             JPushRecord.title == plan.title,
                                             JPushRecord.end_time==end_time,
                                             JPushRecord.intro == plan.intro.id,
                                             JPushRecord.type == plan.type).count()
            if jrs >= 1:
                continue
            if start_time:
                print plan.start_time,plan.end_time
                JPushRecord.create(title=plan.title, type=plan.type,start_time=start_time, end_time=end_time, created=created,
                                   intro=plan.intro.id, check=0, send=0, istest = plan.istest)


if __name__ == '__main__':
    jpush = JPushSearch()
    jpush.search_plan()
