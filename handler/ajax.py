#!/usr/bin/env python
# coding=utf8

import simplejson
from handler import BaseHandler
from lib.route import route
from model import *
from bootloader import db
from lib.mqhelper import create_msg


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
                    'data': item.code,
                    'target': '_top',
                    'click': "pop('" + title + "', '"+url+"');",
                    'open': 'true' if len(item.code) < 8 else 'false'
                })

        url = '/admin/store_area_product?sid=' + str(store_id)
        nodes.append({
            'id': 0,
            'pId': -1,
            'name': '全部',
            'data': '',
            'target': '_top',
            'click': "pop('全部地域-产品信息', '" + url + "');",
            'open': 'true'
        })
        print nodes
        self.write(simplejson.dumps(nodes))


@route(r'/ajax/area_tree', name='ajax_GetAreaTree')  # 获取所有地区
class AjaxGetAllAreas(BaseHandler):
    def get(self):
        nodes = []
        # items = Area.select().where((Area.pid >> None) | (Area.code == 00270001))
        items = Area.select()
        for item in items:
            title = item.name + '-产品信息'
            url = '/admin/store_area_product?sid=' + str(1) + '&code=' + item.code
            nodes.append({
                'id': item.id,
                'pId': item.pid.id if item.pid else 0,
                'name': item.name,
                'data': item.code,
                'target': '_top',
                'click': "pop('" + title + "', '"+url+"');",
                'open': 'true' if len(item.code) < 8 else 'false'
            })
        url = '/admin/store_area_product?sid=1'
        nodes.append({
            'id': 0,
            'pId': -1,
            'name': '全部',
            'data': '',
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


@route(r'/ajax/product_release_publish/(\d+)', name='ajax_product_release_publish')  # 添加商品库
class AjaxProductReleasePublishAreas(BaseHandler):
    def post(self, sid):
        result = {'flag': 0, 'msg': '', 'data': 0}
        json = self.get_body_argument("json", '[]')
        data = simplejson.loads(json)
        if data and len(data) > 0:
            for item in data:
                query = StoreProductPrice.select().where((StoreProductPrice.product_release == item['id']) &
                                                         (StoreProductPrice.store == sid) &
                                                         (StoreProductPrice.area_code == item['code']))
                if query.count() > 0:
                    for q in query:
                        q.delete_instance()

                p = StoreProductPrice()
                p.product_release = item['id']
                p.store = sid
                p.price = item['price']
                p.sort = item['sort']
                p.created = int(time.time())
                p.area_code = item['code']
                p.save()
        result['flag'] = 1
        result['msg'] = '添加成功'
        self.write(simplejson.dumps(result))


@route(r'/ajax/get_category/(\d+)', name='ajax_get_category')  # 添加商品库
class AjaxGetCategory(BaseHandler):
    def get(self, cid):
        result = {'flag': 0, 'msg': '', 'data': []}
        category = Category.get(id=cid)
        for attribute in category.attributes:
            result['data'].append({
                'id': attribute.id,
                'name': attribute.name,
                'values': [{'id': item.id, 'name': item.name} for item in attribute.items]
            })
        result['flag'] = 1
        self.write(simplejson.dumps(result))


@route(r'/ajax/cancel_order', name='ajax_cancel_order')  # 根据订单ID取消订单
class CancelOrderHandler(BaseHandler):
    def post(self):
        result = {'err': 0, 'msg': ''}
        id = self.get_argument("id", '-1')
        status = int(self.get_argument("status", '-1'))
        cause = self.get_argument("cause", '')
        content = {}
        try:
            o = Order.get(Order.id == id)
            o.message = cause + u'；操作人：' +self.get_admin_user().username  # 订单取消原因
            o.save()
            content['cancel_cause'] = cause
            content['order_id'] = id
            AdminUserLog.create(user=self.get_admin_user(), created=int(time.time()), content=content)
        except Exception, e:
            result['err'] = 1
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/ajax/brand_list', name='ajax_brand_list')  # 品牌车型列表
class WebAppCarItemListHandler(BaseHandler):
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = 10
        #
        self.write(simplejson.dumps(result))


@route(r'/ajax/get_score_rate', name='ajax_get_score_rate')  # 获取返佣比率
class WebAppCarItemListHandler(BaseHandler):
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        pid = self.get_argument('pid', None)
        try:
            iop = InsuranceOrderPrice.get(id=pid)
            io = InsuranceOrder.get(id=iop.insurance_order_id)
            print io.store.area_code, iop.insurance.id
            rates = InsuranceScoreExchange.get_score_policy(io.store.area_code, iop.insurance.id)
            if rates:
                iis = InsuranceItem.select().where(InsuranceItem.style_id > 1)
                result['data']['force_tax'] = rates.force_tax_rate
                result['data']['business_tax'] = rates.business_tax_rate
                result['data']['ali_rate'] = rates.ali_rate
                result['data']['profit_rate'] = rates.profit_rate
                result['data']['base_money'] = rates.base_money
                for ii in iis:
                    if iop.__dict__['_data'][ii.eName]:
                        business = True
                        break
                if iop.forceI and business:
                    result['data']['business_s'] = rates.business_exchange_rate2
                    result['data']['force_s'] = rates.force_exchange_rate2
                else:
                    result['data']['business_s'] = rates.business_exchange_rate
                    result['data']['force_s'] = rates.force_exchange_rate
            else:
                result['data']['force_tax'] = 0
                result['data']['business_tax'] = 0
                result['data']['ali_rate'] = 0
                result['data']['profit_rate'] = 0
                result['data']['base_money'] = 0
                result['data']['business_s'] = 0
                result['data']['force_s'] = 0
            result['flag'] = 1
            print result['data']
        except Exception, e:
            result['msg'] = u'系统错误%s'%str(e)
            print e.message

        self.write(simplejson.dumps(result))


@route(r'/ajax/save_iop_data', name='ajax_save_iop')  # 保存报价后的方案
class SaveIOPHandler(BaseHandler):
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': ''}
        groups = self.get_body_argument('groups', None)
        i_items = self.get_body_argument('i_items', None)
        send_msg = self.get_body_argument('send_msg', None)
        if not (groups and i_items):
            result['msg'] = u'参数不全'
            self.write(simplejson.dumps(result))
            return
        groups = simplejson.loads(groups)
        i_items = simplejson.loads(i_items)
        pid = InsuranceOrderPrice.get(id=groups['pid'])
        now = int(time.time())
        if pid.response == 0 or pid.response == 1:
            pid.created = now
            pid.admin_user = self.get_admin_user()
            pid.gift_policy = groups['gift_policy']
            pid.response = 1
            pid.status = 1
            if groups['gift_policy'] == '2':
                pid.score = groups['score']
            else:
                pid.score = 0
            pid.total_price = groups['total_price']
            pid.force_price = groups['force_price']
            pid.business_price = groups['business_price']
            pid.vehicle_tax_price = groups['vehicle_tax_price']
            pid.sms_content = groups['psummary']
            for item in i_items:
                pid.__dict__['_data'][item+'Price'] = i_items[item]
            pid.save()
            if send_msg == '1':
                create_msg()
            result['flag'] = 1
        else:
            result['msg'] = u'该方案已不可再更改'

        self.write(simplejson.dumps(result))




