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
class StoreUpdateGradeHandler(BaseHandler):
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


@route(r'/ajax/store_update_state', name='ajax_store_update_state')  # 修改门店的状态
class StoreUpdateGradeHandler(BaseHandler):
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': 0}
        oid = int(self.get_argument("id", 0))
        state = int(self.get_argument("state_type", -1))
        result['data'] = state
        try:
            if oid > 0 and state > -1:
                store = Store.get(id=oid)
                store.active = state
                store.save()
                result['flag'] = 1
                result['msg'] = u'审核成功'
            else:
                result['msg'] = u'参数传入错误'
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/ajax/exportStore', name='ajax_store_export')  # 生成store的csv
class StoreExportHandler(BaseHandler):

    # 导出Store的数据
    def export_stores(self, stores, file_name):
        f = open('upload/' + file_name, 'w')
        try:
            f.write(u'客户名称,联系人,省,市,区,地址,账户状态,创建时间\n'.encode('gb18030'))
            for store in stores:
                if store.active == 0:  # 审核状态 0未审核 1审核通过 2审核未通过
                    state = u'未审核'
                elif store.active == 1:
                    state = u'已通过'
                else:
                    state = u'未通过'
                if store.created == 0:
                    ctime = u'猴年马月'
                else:
                    ctime = u'%s' % time.strftime('%Y-%m-%d', time.localtime(store.created))

                province = Area.get(code=store.area_code[:4]).name
                city = Area.get(code=store.area_code[:8]).name
                district = Area.get(code=store.area_code).name

                line = u'%s,%s,%s,%s,%s,%s,%s,%s\n' % (store.name, store.linkman,
                                                       province, city, district, store.address, state, ctime)
                f.write(line.encode('gb18030'))
        except Exception, err:
            raise err
        finally:
            f.close()

    def post(self):
        province = self.get_argument("province", '')
        city = self.get_argument("city", '')
        town = self.get_argument("district", '')
        keyword = self.get_argument("keyword", '')
        status = int(self.get_argument("status", '-1'))

        ft = (Store.store_type == 2)
        if status >= 0:
            ft &= (Store.active == status)
        if town and town != '':
            ft &= (Store.area_code == town)
        elif city and city != '':
            city += '%'
            ft &= (Store.area_code % city)
        elif province and province != '':
            province += '%'
            ft &= (Store.area_code % province)
        if keyword:
            keyword2 = '%' + keyword + '%'
            ft &= (Store.name % keyword2)

        result = {'flag': 0, 'msg': ''}
        try:
            file_name = 'stores_export.csv'
            q = Store.select().where(ft)
            self.export_stores(q, file_name)
            result['msg'] = file_name
            result['flag'] = 1
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/ajax/user_update_state', name='ajax_user_update_state')  # 修改门店的状态
class UserUpdateStateHandler(BaseHandler):
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': 0}
        oid = int(self.get_argument("id", 0))
        state = int(self.get_argument("state_type", -1))
        result['data'] = state
        try:
            if oid > 0 and state > -1:
                store = User.get(id=oid)
                store.active = state
                store.save()
                result['flag'] = 1
                result['msg'] = u'操作成功'
            else:
                result['msg'] = u'参数传入错误'
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/ajax/store_tree/(\d+)', name='ajax_GetStoreTree')  # 获取下级区域
class AjaxGetSubAreas(BaseHandler):
    def get(self, store_id):
        store = Store.get(id=store_id)
        nodes = []
        codes = []
        for item in store.service_areas:
            if len(item.area.code) == 12:
                codes.append(item.area.code)
                codes.append(item.area.code[:8])
                codes.append(item.area.code[:4])
            elif len(item.area.code) == 8:
                codes.append(item.area.code)
                codes.append(item.area.code[:4])
                keyword = '' + item.area.code + '%'
                ft = (Area.code % keyword) & (Area.is_delete == 0)
                items = Area.select().where(ft)
                for sub in items:
                    codes.append(sub.code)
            elif len(item.area.code) == 4:
                codes.append(item.area.code)
                keyword = '' + item.area.code + '%'
                ft = (Area.code % keyword) & (Area.is_delete == 0)
                items = Area.select().where(ft)
                for sub in items:
                    codes.append(sub.code)

        un_codes = list(set(codes))
        if len(un_codes) > 0:
            items = Area.select().where(Area.code << un_codes)
            for item in items:
                title = item.name + '-产品信息'
                url = '/admin/store_area_product?sid=' + str(store_id) + '&code=' + item.code
                nodes.append({
                    'id': item.id,
                    'pId': item.pid.id if item.pid else 0,
                    'name': item.name,
                    'url': '',
                    'target': '_top',
                    'click': "pop('" + title + "', '"+url+"');",
                    'open': 'true' if len(item.code) < 8 else 'false'
                })

        url = '/admin/store_area_product?sid=' + str(store_id)
        nodes.append({
            'id': 0,
            'pId': -1,
            'name': '全部',
            'url': '',
            'target': '_top',
            'click': "pop('全部地域-产品信息', '" + url + "');",
            'open': 'true'
        })
        self.write(simplejson.dumps(nodes))


@route(r'/ajax/saler_product_process', name='ajax_saler_product_process')  # 处理发布商品数据
class AjaxSalerProductProcessAreas(BaseHandler):
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': 0}
        json = self.get_body_argument("json", '[]')
        flag = int(self.get_body_argument("flag", -2))
        data = simplejson.loads(json)
        if data and len(data) > 0:
            for item in data:
                p = ProductRelease.get(id=item['id'])
                if flag == 0:
                    p.active = 0
                    p.save()
                elif flag == 2:
                    p.active = 1
                    p.save()
                elif flag == -1:
                    query = StoreProductPrice.delete().where(StoreProductPrice.product_release == p)
                    query.execute()
                    p.delete_instance()
                elif flag == 1:
                    p.price = item['price']
                    p.save()
        result['flag'] = 1
        result['msg'] = '操作成功'
        self.write(simplejson.dumps(result))


@route(r'/ajax/saler_product_price_process', name='ajax_saler_product_price_process')  # 处理已发布商品数据
class AjaxSalerProductPriceProcessAreas(BaseHandler):
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': 0}
        json = self.get_body_argument("json", '[]')
        flag = int(self.get_body_argument("flag", -2))
        data = simplejson.loads(json)
        if data and len(data) > 0:
            for item in data:
                p = StoreProductPrice.get(id=item['id'])
                if flag == 0:
                    p.active = 0
                    p.save()
                elif flag == 2:
                    p.active = 1
                    p.save()
                elif flag == -1:
                    p.delete_instance()
                elif flag == 1:
                    p.price = item['price']
                    p.sort = item['sort']
                    p.save()
        result['flag'] = 1
        result['msg'] = '操作成功'
        self.write(simplejson.dumps(result))


@route(r'/ajax/add_product_release/(\d+)', name='ajax_add_product_release')  # 添加商品库
class AjaxSalerProductPriceProcessAreas(BaseHandler):
    def post(self, sid):
        result = {'flag': 0, 'msg': '', 'data': 0}
        json = self.get_body_argument("json", '[]')
        data = simplejson.loads(json)
        if data and len(data) > 0:
            for item in data:
                query = ProductRelease.select().where((ProductRelease.product == item['id']) & (ProductRelease.store == sid))
                if query.count() > 0:
                    for q in query:
                        q.price = item['price']
                        q.active = 1
                        q.save()
                else:
                    p = ProductRelease()
                    p.product = item['id']
                    p.store = sid
                    p.price = item['price']
                    p.save()
        result['flag'] = 1
        result['msg'] = '添加成功'
        self.write(simplejson.dumps(result))
