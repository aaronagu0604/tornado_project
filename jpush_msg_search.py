#!/usr/bin/env python
# coding=utf8

import time
from model import JPushPlan, JPushRecord


class JPushSearch():
    def get_time(self, start_time, end_time, rate):
        localtime = time.localtime()
        week = time.strftime('%w', localtime)
        date = time.strftime('%Y-%m-%d', localtime)
        if '0' == rate:
            check_rate = True
        elif week in rate.split(','):
            check_rate = True
        elif date == rate:
            check_rate = True
        else:
            check_rate = False
        now_time = time.strftime('%Y-%m-%d', time.localtime())
        start_time = time.mktime(time.strptime('%Y-%m-%d %H:%M', now_time + ' ' + start_time))
        end_time = time.mktime(time.strptime('%Y-%m-%d %H:%M', now_time + ' ' + end_time))

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
            if start_time:
                JPushRecord.create(title=plan.title, start_time=start_time, end_time=end_time, created=created,
                                   intro=plan.intro, check=0, send=0)


if __name__ == '__main__':
    jpush = JPushSearch()
    jpush.search_plan()