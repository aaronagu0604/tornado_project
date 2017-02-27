#!/usr/bin/env python
# coding=utf8

import simplejson
from handler import BaseHandler
from lib.route import route
from model import *
from bootloader import db


@route(r'/ajax/GetSubAreas', name='ajax_GetSubAreas')  # 获取下级区域
class AjaxGetSubAreas(BaseHandler):
    def get(self):
        result = {'flag': 0, 'data': [], 'msg': ''}
        try:
            parent_code = self.get_argument("parent_code", '')
            keyword = '' + parent_code + '%'
            ft = (Area.code % keyword) & (Area.is_delete == 0) & (db.fn.length(Area.code) == len(parent_code) + 4)

            items = Area.select().where(ft).order_by(Area.sort, Area.id, Area.spell)
            result["flag"] = 1
            result["data"] = []
            for item in items:
                result["data"].append({
                    'id': item.id,
                    'code': item.code,
                    'name': item.name
                })
        except Exception, ex:
            result["flag"] = 0
            result["msg"] = ex.message
        self.write(simplejson.dumps(result))


@route(r'/ajax/store_insurance_change', name='ajax_store_insurance_change')  # 更新代理商保险服务设置
class UserUpdateGradeHandler(BaseHandler):
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': 0}
        oid = int(self.get_argument("id", 0))
        state = int(self.get_argument("state_type", -1))
        result['data'] = state
        try:
            if oid > 0 and state > -1:
                store = Store.get(id=oid)
                store.process_insurance = state
                store.save()
                result['flag'] = 1
                result['msg'] = u'设置成功'
            else:
                result['msg'] = u'参数传入错误'
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))
