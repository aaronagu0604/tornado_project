#!/usr/bin/env python
# coding=utf8

import simplejson
from handler import BaseHandler
from lib.route import route
from model import *
from bootloader import db
from lib.mqhelper import create_msg

from tornado.gen import coroutine
from tornado.web import asynchronous
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import logging
import os
import random
from payqrcode import postRequest
import urllib2
import base64

@route(r'/ajax/GetSubAreas', name='ajax_GetSubAreas')  # 获取下级区域
class AjaxGetSubAreas(BaseHandler):
    def get(self):
        result = {'flag': 0, 'data': [], 'msg': ''}
        try:
            parent_code = self.get_argument("pcode", '')
            keyword = '' + parent_code + '%'
            ft = ((Area.code % keyword) & (Area.is_delete == 0) & (db.fn.length(Area.code) == len(parent_code) + 4))

            items = Area.select().where(ft).order_by(Area.sort, Area.id)
            result["flag"] = 1
            result["data"] = []
            for item in items:
                result["data"].append({
                    'id': item.id,
                    'code': item.code,
                    'name': item.name
                })
            else:
                result['msg'] = u'无对应子区域'
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
                if SSILubePolicy.select().where(SSILubePolicy.store == store).count() > 0:
                    result['msg'] = u'该店铺已经有返佣政策，请到该店铺详情里查看'
                else:
                    policies = InsuranceArea.get_area_insurance(store.area_code)
                    for policy in policies:
                        SSILubePolicy.create(store=store, insurance=policy['insurance'], lube=policy['lube'],
                                             dealer_store=policy['dealer_store'], cash=policy['cash'])

                create_msg(simplejson.dumps({'store': store.id, 'state': state}), 'audit_store')
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
            items = Area.select(Area.id.alias('id'), Area.pid.alias('pid'), Area.name.alias('name'),
                                Area.code.alias('code')).where(Area.code << un_codes).dicts()
            nodes = [{
                'id': item['id'],
                'pId': item['pid'] if item['pid'] else 0,
                'name': item['name'],
                'data': item['code'],
                'target': '_top',
                'click': "pop('" + item['name'] + '-产品信息' + "', '"+'/admin/store_area_product?sid=' + str(store_id) + '&code=' + item['code']+"');",
                 'open': 'true' if len(item['code']) < 8 else 'false'
            } for item in items]
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
    executor = ThreadPoolExecutor(20)
    @asynchronous
    @coroutine
    def get(self):
        type = self.get_argument('type',None)
        bi_id = int(self.get_argument('bi_id',0))
        a = yield self.get_all_area(type,bi_id)

    @run_on_executor
    def get_all_area(self,type,bi_id):
        items = Area.select(Area.id.alias('id'), Area.pid.alias('pid'), Area.name.alias('name'), Area.code.alias('code')).dicts()
        bitems = [item.area_code for item in BlockItemArea.select().where(BlockItemArea.block_item == bi_id)]
        print bitems
        nodes = [{
                'id': item['id'],
                'pId': item['pid'] if item['pid'] else 0,
                'name': item['name'],
                'data': item['code'],
                'target': '_top',
                'click': '' if type == 'blockitem' else "pop('" + item['name'] + '-产品信息' + "', '"+'/admin/store_area_product?sid=' + str(1) + '&code=' + item['code']+"');",
                'open': 'false',
                'checked': 'true' if item['code'] in bitems else 'false'
        } for item in items]
        url = '/admin/store_area_product?sid=1'
        nodes.insert(0, {
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


@route(r'/ajax/get_score_rate', name='ajax_get_score_rate')  # 获取返现比率
class WebAppCarItemListHandler(BaseHandler):
    def get_return_cash(self, sid, iid):
        try:
            cash = SSILubePolicy.get((SSILubePolicy.store == sid) & (SSILubePolicy.insurance == iid)).cash
            cash_policy = simplejson.loads(cash)
        except Exception, e:
            cash_policy = None
        return cash_policy

    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        pid = self.get_argument('pid', None)
        iid = self.get_argument('iid', None)
        try:
            iop = InsuranceOrderPrice.get(id=pid)
            io = InsuranceOrder.get(id=iop.insurance_order_id)
            rates = self.get_return_cash(io.store.id, iid)
            if rates:
                iis = InsuranceItem.select().where(InsuranceItem.style_id > 1)
                result['data']['force_tax'] = rates['ftr']
                result['data']['business_tax'] = rates['btr']
                result['data']['ali_rate'] = rates['ar']
                result['data']['profit_rate'] = rates['pr']
                result['data']['base_money'] = rates['bm']
                business = False
                for ii in iis:
                    if iop.__dict__['_data'][ii.eName]:
                        business = True
                        break
                if iop.forceI and business:
                    result['data']['business_s'] = rates['ber2']
                    result['data']['force_s'] = rates['fer2']
                else:
                    result['data']['business_s'] = rates['ber']
                    result['data']['force_s'] = rates['fer']
            else:
                result['data']['force_tax'] = 0
                result['data']['business_tax'] = 0
                result['data']['ali_rate'] = 0
                result['data']['profit_rate'] = 0
                result['data']['base_money'] = 0
                result['data']['business_s'] = 0
                result['data']['force_s'] = 0
            result['flag'] = 1
        except Exception, e:
            result['msg'] = u'系统错误%s'%str(e)

        self.write(simplejson.dumps(result))


@route(r'/ajax/calculate_gift_oil', name='ajax_get_gift_oil_rate')  # 获取返佣比率
class GetGiftOilHandler(BaseHandler):
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        iid = int(self.get_argument('insurance'))
        iopid = int(self.get_argument('iopid'))
        forcetotal = self.get_argument('force', '')
        forcetotal = float(forcetotal) if forcetotal else 0
        businesstotal = self.get_argument('business', 0)
        businesstotal = float(businesstotal) if businesstotal else 0
        try:
            iop = InsuranceOrderPrice.get(id=iopid)
            insurance = InsuranceOrder.get(id=iop.insurance_order_id)
            policy = SSILubePolicy.get((SSILubePolicy.store==insurance.store) & (SSILubePolicy.insurance == insurance))
            policylist = simplejson.loads(policy.lube)

            if forcetotal and businesstotal:
                flag = 3
                totalprice = forcetotal + businesstotal
            elif forcetotal:
                flag = 1
                totalprice = forcetotal
            elif businesstotal:
                flag = 2
                totalprice = businesstotal
            else:
                flag = 0
                totalprice = 0
            role = None
            for item in policylist:
                for p in item['items']:
                    if (int(p['minprice']) <= totalprice) and (totalprice <= int(p['maxprice'])) and (flag == int(p['flag'])):
                        role = p
                        role['oiltype'] = item['gift']
            if role:
                result['data']['driveroiltype'] = role['oiltype']
                result['data']['driveroilnum'] = role['driver']
                result['data']['storeoiltype'] = role['oiltype']
                result['data']['storeoilnum'] = role['store']
                result['flag'] = 1
            else:
                result['msg'] = u'无可用规则'
        except Exception, e:
            result['msg'] = u'本店铺该保险公司没有配置返佣规则！'

        self.write(simplejson.dumps(result))


@route(r'/ajax/save_iop_data', name='ajax_save_iop')  # 保存报价后的方案
class SaveIOPHandler(BaseHandler):
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': ''}
        groups = self.get_body_argument('groups', None)
        i_items = self.get_body_argument('i_items', None)
        send_msg = self.get_body_argument('send_msg', None)
        print groups,i_items,send_msg
        if not (groups and i_items):
            result['msg'] = u'参数不全，保存失败'
            self.write(simplejson.dumps(result))
            return
        groups = simplejson.loads(groups)
        i_items = simplejson.loads(i_items)
        pid = InsuranceOrderPrice.get(id=int(groups['pid']))
        io = InsuranceOrder.get(id=pid.insurance_order_id)
        now = int(time.time())
        if pid.response in [0,1] and io.status in [0,1]:
            pid.created = now
            pid.admin_user = self.get_admin_user()
            pid.gift_policy = groups['gift_policy']
            pid.response = 1
            pid.status = 1
            if groups['gift_policy'] == '2':
                pid.cash = groups['cash']
            else:
                pid.cash = 0
            pid.total_price = groups['total_price']
            pid.force_price = groups['force_price']
            pid.business_price = groups['business_price']
            pid.vehicle_tax_price = groups['vehicle_tax_price']

            pid.force_rate = groups['force_rate'] if groups['force_rate'] else None
            pid.business_rate = groups['business_rate'] if groups['business_rate'] else None
            pid.sms_content = groups['psummary']
            for item in i_items:
                pid.__dict__['_data'][item] = i_items[item]
            pid.save()

            io.current_order_price = pid
            io.status = 1
            io.save()
            # 创建首页消息
            msg = Message.select().where(Message.store == io.store.id, Message.type == 'new_insurance_order_price',
                                         Message.status == 0,Message.other_id == pid.id)
            if msg.count()==0:
                msg = Message()
                msg.store = io.store
                msg.type = 'new_insurance_order_price'
                msg.link = 'czj://insurance_order_detail/%d' % io.id
                msg.other_id = pid.id
                msg.content = '您有新的报价单'
                msg.save()
                # 进行极光推送
                sms = {'apptype': 1, 'body': '您有新的报价单！', 'jpushtype': 'alias', 'alias': io.user.mobile,
                       'extras':{'link':'czj://insurance_order_detail/%s' % io.id}}
                create_msg(simplejson.dumps(sms), 'jpush')
            admin_user = self.get_admin_user()
            content = '%s进行报价：io.id:%d'%(admin_user.name,io.id)
            if send_msg == '1':
                io = InsuranceOrder.get(id=pid.insurance_order_id)
                sms = {'mobile': io.store.mobile, 'signtype': '1', 'isyzm': 'changePrice',
                       'body': [io.ordernum, pid.insurance.name, groups['total_price'], groups['psummary']]}
                create_msg(simplejson.dumps(sms), 'sms')  # 变更价格
                '%s进行报价并发送短信：io.id:%d' % (admin_user.username, io.id)
            result['flag'] = 1

            AdminUserLog.create(admin_user=admin_user, created=now, content=content)
        else:
            result['msg'] = u'该方案已不可再更改'

        self.write(simplejson.dumps(result))


@route(r'/ajax/append_refund_money', name='ajax_append_refund_money')  # 补退款
class AppendRefundMoneyHandler(BaseHandler):
    def post(self):
        result = {'flag': 0, 'msg': '', 'data': ''}
        ar_num = self.get_body_argument('ar_num', None)
        ar_reason = self.get_body_argument('ar_reason', None)
        pid = self.get_body_argument('pid', None)
        ar_status = self.get_body_argument('ar_status', None)

        admin_user = self.get_admin_user()
        now = int(time.time())
        content = ''
        print self.request.body,(ar_num , ar_reason , pid , ar_status)
        if not (ar_num and ar_reason and pid and ar_status):
            result['msg'] = u'参数不全'
            self.write(simplejson.dumps(result))
            return
        try:
            ar_num = float(ar_num)
            print ar_num
            io = InsuranceOrder.get(current_order_price=pid)
            iop = InsuranceOrderPrice.get(id=pid)
            if iop.append_refund_status != int(ar_status):
                result['msg'] = u'该补退款已有别人发起，刷新页面确认后重试！'
            else:
                if ar_num > 0.001:    # 让客户补款
                    iop.append_refund_status = 1
                elif ar_num < 0.001:    # 给客户退款
                    io.store.price -= ar_num
                    io.store.save()
                    iop.append_refund_status = 2
                    iop.total_price += ar_num
                    process_log = u'订单：%s退款' % (io.ordernum)
                    MoneyRecord.create(user=io.user, store=io.store,process_type=1, process_message=u'退款',
                                       process_log=process_log, money=ar_num, status=1, apply_time=now,
                                       processing_time=now, processing_by=admin_user)
                io.save()
                iop.append_refund_time = now
                iop.append_refund_reason = ar_reason
                iop.append_refund_num = ar_num
                iop.admin_user = admin_user
                iop.save()
                result['flag'] = 1
                content = u'申请补退款：客户:%s，订单:%s，金额:%s元，原因:%s，操作人:%s，' % \
                          (io.store.name, io.ordernum, ar_num, ar_reason, admin_user.username)
                create_msg(simplejson.dumps({'order_id': io.id, 'operation': iop.append_refund_status}), 'append_refund_money')
        except Exception, e:
            result['msg'] = u'申请补款失败：%s' % e.message
            content = u'申请补退款失败：订单:%s，操作人:%s，原因:%s' % (pid, admin_user.username, str(e))
        AdminUserLog.create(admin_user=admin_user, created=now, content=content)
        self.write(simplejson.dumps(result))


@route(r'/ajax/cancel_insurance_order', name='ajax_cancel_insurance_order')  # 保险订单完成（保单返佣）
class CancelInsuranceOrderHandler(BaseHandler):
    def post(self):
        result = {'flag': 0, 'msg': ''}
        oid = self.get_body_argument('oid', '')
        cause = self.get_body_argument('cause', '')
        try:
            io = InsuranceOrder.get(id=oid)
            now = int(time.time())
            if io.status < 2:
                io.status = -1
                io.cancel_reason = cause
                io.save()
                AdminUserLog.create(admin_user=self.get_admin_user(), created=now, content=u'删除保险订单：%s' % io.id)
                result['flag'] = 1
            else:
                result['msg'] = u'取消失败：该订单不可取消！'
        except Exception, e:
            result['msg'] = u'取消失败：%s' % e.message
        self.write(simplejson.dumps(result))


@route(r'/ajax/new_program/(\d+)', name='ajax_new_program')  # 新建保险方案
class NewProgram(BaseHandler):
    def post(self, oid):
        result = {'flag': 0, 'msg': ''}
        try:
            iop = InsuranceOrderPrice()
            iop.insurance_order_id = oid
            iop.insurance = 1
            iop.gift_policy = 1
            iop.admin_user = self.get_admin_user()
            iop.created = time.time()
            iop.save()
            AdminUserLog.create(admin_user=self.get_admin_user(), created=int(time.time()), content='新增报价单: iop_id:%d'%iop.id)
            result['flag'] = 1
        except Exception, e:
            result['msg'] = u'新增保险方案失败：%s' % e.message
        self.write(simplejson.dumps(result))


@route(r'/ajax/withdraw_change_status', name='ajax_withdraw_change_status')  # 更新提现状态
class WithdrawChangeStatusHandler(BaseHandler):
    def post(self):
        result = 0
        fid = int(self.get_argument("fid", 0))
        try:
            if fid != 0:
                p = Withdraw.get(Withdraw.id == fid)
                status_old = p.status
                p.status = p.status + 1
                if p.status == 1:
                    p.processing_result = u'汇款完成'
                if p.status > 1:
                    p.status = 1
                p.processing_time = int(time.time())
                p.processing_by = self.get_admin_user()
                p.save()
                result = p.status
                if status_old == 0 and p.status == 1:
                    #已经给您的${bankName}尾号为${bankNum}的银行卡汇款，将于两小时内到账，请注意查收。
                    sms = {'mobile': p.user.mobile, 'body': [p.account_name, p.account_account[-4:]], 'signtype': '1',
                           'isyzm': 'accountNotice'}
                    create_msg(simplejson.dumps(sms), 'sms')

        except Exception, e:
            result = -1
        self.write(simplejson.dumps(result))


@route(r'/ajax/export_trade_list', name='ajax_trade_export')  # 生成网站交易明细的csv
class TradeExportHandler(BaseHandler):
    # 导出出单明细
    def export_insunrance_list(data, fname, title):
        f = open('upload/' + fname, 'w')
        try:
            f.write((title + u'出单明细[' + time.strftime("%Y-%m-%d", time.localtime(int(time.time()))) + u']\n').encode(
                'gb18030'))
            f.write(
                u'序号,日期,订单号,资金来源,资金项目,客户地址,金额,保险公司,车主/承保人,入账手续费,转出金额,转出手续费,备注\n'.encode('gb18030'))

            for s in data:
                line = s['id'] + u',' + \
                       s['ordered'] + u',' + \
                       s['ordernum'] + u',' + \
                       s['payment'] + u',' + \
                       s['moneyitem'] + u',' + \
                       s['useraddress'] + u',' + \
                       s['totalprice'] + u',' + \
                       s['insurance'] + u',' + \
                       s['user'] + u',' + \
                       s['incommission'] + u',' + \
                       s['outprice'] + u',' + \
                       s['outcommission'] + u',' + \
                       s['summary']
                f.write(line.encode('gb18030'))

        except Exception, e:
            pass
        finally:
            f.close()

    def post(self):
        begin_date = self.get_argument("begin_date", '')
        end_date = self.get_argument("end_date", '')

        ft = (Order.status << [1, 2, 3, 4])

        if begin_date and end_date:
            begin = time.strptime(begin_date, "%Y-%m-%d")
            end = time.strptime((end_date + " 23:59:59"), "%Y-%m-%d %H:%M:%S")
            ft &= (Order.ordered > time.mktime(begin)) & (Order.ordered < time.mktime(end))

        result = {'flag': 0, 'msg': ''}
        try:
            payment = {1: u'支付宝', 2: u'微信', 3: u'银联', 4: u'余额'}
            file_name = 'tradelist_export.csv'
            orders = Order.select().join(Store).where(ft).order_by(Order.ordered.asc())
            insuranceorders  = InsuranceOrder.select().join(Store).where(ft).order_by(InsuranceOrder.ordered.asc())
            data = []
            for item in orders:
                s = {}
                s['id'] = str(item.id)
                s['ordered'] = u'%s' % time.strftime('%Y-%m-%d', time.localtime(item.ordered))
                s['ordernum'] = item.ordernum
                s['payment'] = payment[item.payment]
                s['moneyitem'] = u'润滑油'
                s['useraddress'] = item.address.address
                s['totalprice'] = str(item.total_price)
                s['insurance'] = item.buyer_store.name
                s['user'] = item.user.name
                s['incommission'] = None
                s['outprice'] = None
                s['outcommission'] = None
                s['summary'] = item.message
                data.append(s)

            for item in insuranceorders:
                s = {}
                s['id'] = str(item.id)
                s['ordered'] = u'%s' % time.strftime('%Y-%m-%d', time.localtime(item.ordered))
                s['ordernum'] = item.ordernum
                s['payment'] = payment[item.payment]
                s['moneyitem'] = u'保险'
                s['useraddress'] = item.delivery_address
                s['totalprice'] = str(item.current_order_price.total_price)
                s['insurance'] = item.current_order_price.insurance.name
                s['user'] = item.user.name
                s['incommission'] = None
                s['outprice'] = None
                s['outcommission'] = None
                s['summary'] = item.local_summary
                data.append(s)
            self.export_stores(data, file_name)
            result['msg'] = file_name
            result['flag'] = 1
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))


@route(r'/ajax/export_insurance_list', name='ajax_insurance_export')  # 生成出单明细的csv
class InsuranceExportHandler(BaseHandler):
    # 导出网站交易明细
    def export_trade_list(data, fname, title):
        f = open('upload/' + fname, 'w')
        try:
            f.write((title + u'网站交易明细[' + time.strftime("%Y-%m-%d", time.localtime(int(time.time()))) + u']\n').encode(
                'gb18030'))
            f.write(u'序号,出保单日期,联系电话,地区,门店,保险名称，车牌，车主，险种，经办人，登记人，金额，较强，车船，商业，快递，型号，返佣，数量（桶）,订单号,备注1,备注2,领油日期，领取人 \n'.encode(
                    'gb18030'))

            for s in data:
                jiaoqiang = None
                if s.current_order_price.force_price > 0:
                    jiaoqiang = '交强'
                if s.current_order_price.force_price > 0:
                    jiaoqiang += ',车船'
                if s.current_order_price.force_price > 0:
                    jiaoqiang += ',商业'
                gift  = None
                if s.current_order_price.gift_policy == 2:
                    gift = '佣金返积分'
                elif s.current_order_price.gift_policy == 1:
                    gift = '佣金返油'
                else:
                    gift = '无'

                line = str(s.id) + u',' + \
                    u'%s' % time.strftime('%Y-%m-%d', time.localtime(s.deal_time)) + u',' + \
                    s.delivery_tel + u',' + \
                    s.delivery_region + u',' + \
                    s.store.name + u',' + \
                    s.current_order_price.insurance.name + u',' + \
                    u'车主' + u',' + \
                    u'车牌' + u',' + \
                    jiaoqiang + u',' + \
                    s.current_order_price.admin_user.name + u',' + \
                    u'登记人' + u',' + \
                    str(s.total_price) + u',' + \
                    str(s.current_order_price.force_price) + u',' + \
                    str(s.current_order_price.vehicle_tax_price) + u',' + \
                    str(s.current_order_price.business_price) + u',' + \
                    s.deliver_company + u'(' + s.deliver_num + u')' + u',' + \
                    gift + u',' + \
                    str(s.current_order_price.score) + u',' + \
                    s.ordernum + u',' + \
                    s.local_summary + u',' + \
                    u'备注2' + u',' + \
                    u'领油日期' + u',' + \
                    u'另有人'

                f.write(line.encode('gb18030'))

        except Exception, e:
            print e
            pass
        finally:
            f.close()
    def post(self):
        begin_date = self.get_argument("begin_date", '')
        end_date = self.get_argument("end_date", '')

        ft = (Order.status << [1, 2, 3, 4])

        if begin_date and end_date:
            begin = time.strptime(begin_date, "%Y-%m-%d")
            end = time.strptime((end_date + " 23:59:59"), "%Y-%m-%d %H:%M:%S")
            ft &= (Order.ordered > time.mktime(begin)) & (Order.ordered < time.mktime(end))

        result = {'flag': 0, 'msg': ''}
        try:
            file_name = 'insurancelist_export.csv'
            q = InsuranceOrder.select().join(Store).where(ft).order_by(InsuranceOrder.ordered.asc())
            self.export_stores(q, file_name)
            result['msg'] = file_name
            result['flag'] = 1
        except Exception, e:
            result['msg'] = e.message
        self.write(simplejson.dumps(result))

@route(r'/ajax/upload', name='ajax_upload')  # 上传文件，用于产品内容
class UploadHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass

    def post(self):
        if self.request.files:
            ext = self.request.files["filedata"][0]["filename"].rsplit('.')[-1].lower()

            if ext in ['jpg', 'gif', 'png']:
                # p = Product.get(id=pid)
                filename = '%d%d.%s' % (int(time.time()), random.randint(1000, 9999), ext)
                size = len(self.request.files["filedata"][0]["body"])
                if size<=2*1024*1024:
                    try:
                        user = self.get_current_user()
                        user_id = 0
                        if user:
                            user_id = user.id
                            path_dir = 'upload/'  + str(user_id/10000) + '/' + str(user_id)
                            if not os.path.exists('upload/' + str(user_id/10000)):
                                os.mkdir('upload/' + str(user_id/10000))
                            if not os.path.exists(path_dir):
                                os.mkdir(path_dir)
                        else:
                            year = time.strftime("%Y",time.localtime())
                            mon = time.strftime("%m",time.localtime())
                            day = time.strftime("%d",time.localtime())
                            path_dir = 'upload/' + str(user_id/10000) + '/' + year + mon + '/' + day
                            if not os.path.exists('upload/' + str(user_id/10000)):
                                os.mkdir('upload/' + str(user_id/10000))
                            if not os.path.exists('upload/' + str(user_id/10000)+ '/' + year + mon ):
                                os.mkdir('upload/' + str(user_id/10000)+ '/' + year + mon )
                            if not os.path.exists(path_dir):
                                os.mkdir(path_dir)
                        imgurl = ''
                        with open(path_dir + '/' + filename, "wb") as f:
                            f.write(self.request.files["filedata"][0]["body"])
                        imgurl = postRequest(open(path_dir + '/' + filename,'rb'))
                        print imgurl
                        msg = '{"err":"","msg":"' + imgurl + '"}'


                    except Exception, e:
                        import traceback
                        traceback.print_exc()
                        msg = '{"err":0,"msg":"上传失败"}'
                else:
                    msg = '{"err":0,"msg":"上传图片大小不能超过2M！"}'
            else:
                msg = '{"err":0,"msg":"请上传.jpg,.gif,.png格式图片！"}'
            self.write(msg)

@route(r'/ajax/product/pic/(\d+)', name='ajax_product_pic')  # 上传产品图片文件
class UploadPicHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass

    def post(self, pid):
        if self.request.files:
            ext = self.request.files["filedata"][0]["filename"].rsplit('.')[-1].lower()

            if ext in ['jpg', 'gif', 'png']:
                p = Product.get(id=pid)
                filename = '%d%d.%s' % (int(time.time()), random.randint(1000, 9999), ext)
                try:
                    user = self.current_user
                    user_id = 0
                    if user:
                        user_id = user.id
                        path_dir = 'upload/'  + str(user_id/10000) + '/' + str(user_id)
                        if not os.path.exists('upload/' + str(user_id/10000)):
                            os.mkdir('upload/' + str(user_id/10000))
                        if not os.path.exists(path_dir):
                            os.mkdir(path_dir)
                    else:
                        year = time.strftime("%Y",time.localtime())
                        mon = time.strftime("%m",time.localtime())
                        day = time.strftime("%d",time.localtime())
                        path_dir = 'upload/' + str(user_id/10000) + '/' + year + mon + '/' + day
                        if not os.path.exists('upload/' + str(user_id/10000)):
                            os.mkdir('upload/' + str(user_id/10000))
                        if not os.path.exists('upload/' + str(user_id/10000)+ '/' + year + mon ):
                            os.mkdir('upload/' + str(user_id/10000)+ '/' + year + mon )
                        if not os.path.exists(path_dir):
                            os.mkdir(path_dir)
                    with open(path_dir + '/' + filename, "wb") as f:
                        f.write(self.request.files["filedata"][0]["body"])
                    imgurl = postRequest(open(path_dir + '/' + filename, 'rb'))
                    print imgurl
                    pic = ProductPic.create(product=p, pic=imgurl, isactive=1)
                    msg = '{"id":' + str(pic.id) + ',"path":"'+ imgurl +'"}'
                except Exception, e:
                    logging.error(e)
                    msg = '{"id":0,"path":"上传失败"}'
            self.write(msg)

@route(r'/ajax/update_io_card_status', name='ajax_update_io_card_status')  # 保单图片重新上传
class UpdateIOCardStatusHandler(BaseHandler):

    def check_xsrf_cookie(self):
        pass

    def post(self):
        result = {'flag': 1, 'msg': '保存成功', 'data': ''}
        io_id = int(self.get_body_argument('io_id',0))
        img_type = self.get_body_argument('img_type', None)
        img_status = int(self.get_body_argument('img_status', 1)) # 0不需要 1需要

        if not (io_id and img_type):
            result['flag'] = 0
            result['msg'] = u'参数不全'
            self.write(simplejson.dumps(result))
            return
        try:
            io = InsuranceOrder.get(id=int(io_id))

            setattr(io, img_type, img_status)
            io.save()
            # 创建首页消息
            msg = Message.select().where(Message.store == io.store.id,Message.type == 'new_insurance_order_img',
                                         Message.status == 0, Message.other_id == io_id)
            if img_status and msg.count() == 0:
                msg = Message()
                msg.store = io.store
                msg.type = 'new_insurance_order_img'
                msg.link = 'czj://insurance_order_detail/%s' % io_id
                msg.other_id = io_id
                msg.content = '您的保险订单需要重新上传图片'
                msg.save()
                # 进行极光推送
                io.user.mobile
                sms = {'apptype': 1, 'body': '您有保险订单图片审核未通过，需要重新上传！', 'jpushtype': 'alias', 'alias': io.user.mobile,
                       'extras':{'link':'czj://insurance_order_detail/%s' % io_id}}
                create_msg(simplejson.dumps(sms), 'jpush')
        except Exception,e:
            result['flag'] = 0
            result['msg'] = '更新状态失败：%s'%e
        self.write(simplejson.dumps(result))

@route(r'/ajax/ocr', name='ajax_ocr')  # 自动识别图片信息
class OCRHandler(BaseHandler):
    executor = ThreadPoolExecutor(20)

    def check_xsrf_cookie(self):
        pass

    def ali_idcard_ocr(self,imgdata,isfront=True):
        content = base64.b64encode(buffer(imgdata))
        host = 'https://dm-51.data.aliyun.com'
        path = '/rest/160601/ocr/ocr_idcard.json'
        appcode = '09e511b3e4bd4aaca8a704ad91c582f4'

        url = host + path
        post_data = {
            'inputs': [
                {
                    'image': {
                        'dataType': 50,
                        'dataValue': content
                    },
                    'configure': {
                        'dataType': 50,
                        'dataValue': simplejson.dumps({
                            'side': 'face' if isfront else 'back'
                        })
                    }
                }
            ]
        }
        #print 'parameters',post_data
        request = urllib2.Request(url, simplejson.dumps(post_data))
        request.add_header('Authorization', 'APPCODE ' + appcode)
        # 根据API的要求，定义相对应的Content - Type
        request.add_header('Content-Type', 'application/json; charset=UTF-8')
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        response = urllib2.urlopen(request, context=ctx)
        ocrresult = response.read()
        print 'idcard:',ocrresult
        return simplejson.loads(ocrresult)['outputs'][0]['outputValue']['dataValue']

    def ali_drive_ocr(self,imgdata):
        content = base64.b64encode(buffer(imgdata))
        host = 'https://dm-53.data.aliyun.com'
        path = '/rest/160601/ocr/ocr_vehicle.json'
        appcode = '09e511b3e4bd4aaca8a704ad91c582f4'

        url = host + path
        post_data = {
            'inputs': [
                {
                    'image': {
                        'dataType': 50,
                        'dataValue': content
                    }
                }
            ]
        }

        request = urllib2.Request(url, simplejson.dumps(post_data))
        request.add_header('Authorization', 'APPCODE ' + appcode)
        # 根据API的要求，定义相对应的Content - Type
        request.add_header('Content-Type', 'application/json; charset=UTF-8')
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        response = urllib2.urlopen(request, context=ctx)
        ocrresult = response.read()
        print 'drivecard:',ocrresult
        try:
            return simplejson.loads(ocrresult)['outputs'][0]['outputValue']['dataValue']
        except:
            return simplejson.loads([])
    @run_on_executor
    def insuranceorderocr(self,io_id,isone):
        if not io_id:
            self.write('该订单不存在')
        try:
            io = InsuranceOrder.get(id=io_id)
            result = {'flag': 1}
            if io.id_card_front:
                request = urllib2.Request(io.id_card_front)
                img_data = urllib2.urlopen(request).read()
                ocrresult = self.ali_idcard_ocr(img_data)

                result['id_card_front'] = simplejson.loads(ocrresult)
            if isone==0 and io.id_card_front_owner:
                request = urllib2.Request(io.id_card_front_owner)
                img_data = urllib2.urlopen(request).read()
                ocrresult = self.ali_idcard_ocr(img_data)

                result['id_card_front_owner'] = simplejson.loads(ocrresult)
            # if io.id_card_back:
            #     request = urllib2.Request(io.id_card_back)
            #     img_data = urllib2.urlopen(request).read()
            #     ocrresult = self.ali_idcard_ocr(img_data, False)
            #     result['id_card_back'] = simplejson.loads(ocrresult)
            if io.drive_card_front:
                request = urllib2.Request(io.drive_card_front)
                img_data = urllib2.urlopen(request).read()
                ocrresult = self.ali_drive_ocr(img_data)

                result['drive_card_front'] = simplejson.loads(ocrresult)
        except Exception,e:
            result['flag'] = 0
            result['msg'] = 'ocr 识别失败'
        self.write(simplejson.dumps(result))


    @asynchronous
    @coroutine
    def get(self):

        io_id = self.get_argument('io_id', None)
        owner_buyer_isone = int(self.get_argument('owner_buyer_isone',1))
        a = yield self.insuranceorderocr(io_id,owner_buyer_isone)

@route(r'/ajax/ocr_save', name='ajax_ocr_save')  # 保存图片识别信息
class OCRSaveHandler(BaseHandler):
    executor = ThreadPoolExecutor(20)

    def check_xsrf_cookie(self):
        pass

    def post(self):
        result = {'flag': 1, 'msg': '保存成功', 'data': ''}
        io_id = self.get_body_argument('io_id', None)
        ioci_id = int(self.get_body_argument('ioci_id',0))
        print io_id,ioci_id
        try:
            ioci = UserCarInfo.get(id=ioci_id)
        except Exception,e:
            ioci = None
        # 车主信息
        car_owner_name = self.get_body_argument('car_owner_name', None)
        car_owner_idcard = self.get_body_argument('car_owner_idcard', None)
        car_owner_date = self.get_body_argument('car_owner_date', None)
        car_owner_address = self.get_body_argument('car_owner_address', None)
        car_owner_type = self.get_body_argument('car_owner_type', None)
        car_use_type = self.get_body_argument('car_use_type', None)
        car_nengyuan_type = self.get_body_argument('car_nengyuan_type', None)
        # 机构信息
        car_owner_num = self.get_body_argument('car_owner_num', None)
        # 被保险人信息
        owner_buyer_isone = self.get_body_argument('owner_buyer_isone', None)
        buy_name = self.get_body_argument('buy_name', None)
        buy_idcard = self.get_body_argument('buy_idcard', None)
        buy_date = self.get_body_argument('buy_date', None)
        buy_address = self.get_body_argument('buy_address', None)
        # 车辆信息
        car_num = self.get_body_argument('car_num', None)
        car_glass_type = self.get_body_argument('car_glass_type', None)
        car_frame_num = self.get_body_argument('car_frame_num', None)
        car_engine_num = self.get_body_argument('car_engine_num', None)
        car_type = self.get_body_argument('car_type', None)
        car_model_type = self.get_body_argument('car_model_type', None)
        car_passenger_number = self.get_body_argument('car_passenger_number', None)
        car_quality = self.get_body_argument('car_quality', None)
        car_price = self.get_body_argument('car_price', None)
        car_displacement = self.get_body_argument('car_displacement', None)
        car_model_code = self.get_body_argument('car_model_code', None)
        first_register_date = self.get_body_argument('first_register_date', None)
        assigned = self.get_body_argument('assigned', None)
        assigned_date = self.get_body_argument('assigned_date', None)
        # 保险信息
        start_date_enforce = self.get_body_argument('start_date_enforce', None)
        start_date_trade = self.get_body_argument('start_date_trade', None)
        # 中华联合额外字段
        rta_type = self.get_body_argument('rta_type', None)
        car_detail_type = self.get_body_argument('car_detail_type', None)
        car_num_type = self.get_body_argument('car_num_type', None)
        license_type = self.get_body_argument('license_type', None)

        if not io_id:
            result['msg'] = u'参数不全'
            self.write(simplejson.dumps(result))
            return

        io = InsuranceOrder.get(id=int(io_id))
        if ioci:
            ucinfo = ioci
        else:
            ucis = io.insurance_orders_car_infos
            if ucis.count():
                ucinfo = ucis[0]
            else:
                ucinfo = UserCarInfo()
                ucinfo.insuranceorder = io
        # 车主信息
        ucinfo.car_owner_name = car_owner_name  # 车主姓名
        ucinfo.car_owner_idcard = car_owner_idcard  # 车主身份证号
        ucinfo.car_owner_date = car_owner_date  # 车主身份证有效期
        ucinfo.car_owner_address = car_owner_address  # 车主身份证地址
        ucinfo.car_owner_type = car_owner_type  # 车主类型:小客车car
        ucinfo.car_use_type = car_use_type  # 车辆使用类型：非运营non_operation,运营operation
        ucinfo.car_nengyuan_type = car_nengyuan_type  # 车主能源情况：燃油ranyou，混合hunhe
        # 机构信息
        ucinfo.car_owner_num = car_owner_num  # 车辆所属组织机构代码
        # 被保险人信息
        ucinfo.owner_buyer_isone = owner_buyer_isone  # 0不是 1是
        ucinfo.buy_name = buy_name  # 姓名
        ucinfo.buy_idcard = buy_idcard  # 身份证号
        ucinfo.buy_date = buy_date  # 身份证有效期
        ucinfo.buy_address = buy_address  # 身份证地址
        # 车辆信息
        ucinfo.car_num = car_num  # 车牌号
        ucinfo.car_glass_type = car_glass_type
        ucinfo.car_frame_num = car_frame_num  # 车架号
        ucinfo.car_engine_num = car_engine_num  # 发动机号
        ucinfo.car_type = car_type  # 车型
        ucinfo.car_model_type = car_model_type  # 品牌厂型
        ucinfo.car_model_code = car_model_code
        ucinfo.car_price =car_price
        ucinfo.car_displacement = car_displacement
        ucinfo.car_passenger_number = car_passenger_number  # 车座位数
        ucinfo.car_quality = car_quality  # 整车质量
        ucinfo.first_register_date = first_register_date  # 初次等级日期
        ucinfo.assigned = assigned  # 是否过户：0没有1有
        ucinfo.assigned_date = assigned_date  # 过户日期
        # 保险信息
        ucinfo.start_date_enforce = start_date_enforce  # 交强险起保日期
        ucinfo.start_date_trade = start_date_trade  # 商业险起保日期
        # 中华联合额外字段
        ucinfo.rta_type = rta_type  # 交管所车辆类型
        ucinfo.car_detail_type = car_detail_type  # 细化车型
        ucinfo.car_num_type = car_num_type  # 车牌类型
        ucinfo.license_type = license_type  # 行驶证车辆类型

        ucinfo.save()
        self.write(simplejson.dumps(result))

@route(r'/ajax/search_car_info', name='ajax_search_car_info')  # 查询车辆信息
class SearchCarInfoHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass

    def sear_chcar_info(self, insurance=0,car_model_type=None,register_date=None,frame_num=None,car_num=None):
        url = 'http://apitest.baodaibao.com.cn/index.php?g=Api&m=SearchCarInfoApi&a=SearchCarInfo'
        msg = {'flag':0 , 'msg':'查询失败', 'data':''}
        insurance = Insurance.get(id = int(insurance))
        if insurance.eName not in ['zhlh','taiping','huaan']:
            msg['msg'] = '不支持自动报价的保险公司'
            self.write(msg)
            return
        post_data = {}
        post_data['changpai_model'] = car_model_type  # "北京现代BH7203AY"
        post_data['user_id'] = "142"
        if insurance.eName == 'taiping':
            post_data['taiping_data'] = {
                "customerid": "3"
            }
        if insurance.eName == 'zhlh':
            post_data['zhlh_data'] = {
                "customerid": "17",
                "first_register_data": register_date
            }
        if insurance.eName == 'huaan':
            post_data['huaan_data'] = {
                'frame_number': frame_num,
                'car_number': car_num,
                "customerid": "14",
                "city_code":"610000"
            }
        print 'post data:',simplejson.dumps(post_data)
        request = urllib2.Request(url, 'data=%s' % simplejson.dumps(post_data))
        response = urllib2.urlopen(request)
        result = response.read()
        print 'return data:',result
        jsondata = simplejson.loads(result)
        data = []

        if jsondata['status'] == '200':
            msg['flag'] = 1
            for item in jsondata['data']:
                display = item['car_remark']
                value = simplejson.dumps(item)
                data.append({'display':display, 'value':value})
            msg['data'] = data

        self.write(simplejson.dumps(msg))


    def get(self):
        io_id = self.get_argument('io_id', None)
        insurance = self.get_argument('insurance', 1)
        car_model_type = self.get_argument('car_model_type',None)
        register_date = self.get_argument('register_date', None)
        frame_num = self.get_argument('frame_num', None)
        car_num = self.get_argument('car_num', None)
        self.sear_chcar_info(insurance,car_model_type,register_date,frame_num,car_num)

@route(r'/ajax/auto_caculate_price', name='ajax_auto_caculate_price')  # 自动报价
class AutoCaculateInsuranceOrderPriceHandler(BaseHandler):
    executor = ThreadPoolExecutor(20)

    def check_xsrf_cookie(self):
        pass

    def quote_iop(self,insurance,io,items={},insurance_id='0',price=0,quality=0,displacement=0,
                                          model_code=0):
        result = {'flag': 0, 'msg': '', 'data': ''}
        insurance = insurance.eName
        if insurance not in ['zhlh','taiping','huaan']:
            result['msg'] = '不支持自动报价的保险公司'
            self.write(result)
            return
        notify_url = 'http:///api.dev.test.520czj.com/mobile/baodaibao_notify'
        url = 'http://apitest.baodaibao.com.cn/index.php?g=Api&m=QuoteApi&a=Quote'
        post_id = io.ordernum + str(time.time())[:10]
        insurance_items = {
            'damageI':'车辆损失险(主)',
            'thirdDutyI': '第三者责任险(主)',
            'robbingI': '全车盗抢险(主)',
            'driverDutyI': '车上人员险(主)(司机)',
            'passengerDutyI': '车上人员险(主)(乘客)',
            'glassI': '玻璃单独破碎险(附)', #玻璃险value传进口或者国产,
            'scratchI': '车身划痕险(附)',
            'fireDamageI': '自燃损失险(附)',
            'wadeI': '发动机涉水险(附)',
            'thirdSpecialI': '无法找到第三方险(附)',
            '11': '指定修理厂险(附)',
        }
        insurance_name = {
            '1': '商业',
            '2':'交强',
            '3':'商业+交强'
        }
        insuranceinfo = []
        for k,v in items.items():
            if k in ['forceI','vehicleTax']:
                continue
            deductible,value = v.decode('utf8').split(',')
            insuranceinfo.append({
                "deductible": deductible,
                "ip_name": insurance_items[k],
                "value": value
            })
        post_data = {}
        car_infos = io.insurance_orders_car_infos[0]
        post_data['car'] = {
            "car_price": price,
            "model_code": model_code,
            "displacement": displacement
        }
        post_data['orderArr'] = {
            # BaseInfo
            "order_id": post_id,  # 订单号
            "created": time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),  # 当前时间
            "city_code": "610100",  # 城市代码
            # 车辆信息
            "province": car_infos.car_num.decode('utf8')[0],  # 车牌汉字
            "car_number": car_infos.car_num.decode('utf8')[1:],  # 车牌数字
            "car_category": car_infos.car_type,  # 车辆类型:小客车car
            "car_nengyuan_type": car_infos.car_nengyuan_type,  # 能源类型:燃油ranyou，混合hunhe(中华必填)
            "use_cat": car_infos.car_use_type,  # 使用类型:非运营non_operation(中华必填)
            "assigned": car_infos.assigned,  # 是否过户: 0否1是
            "guohudate": car_infos.assigned_date,  # 过户日期
            "passenger_number": car_infos.car_passenger_number,  # 座位数(中华必填)
            "changpai_model": car_infos.car_model_type,  # 厂牌型号
            "frame_number": car_infos.car_frame_num,  # 车架号
            "engine_number": car_infos.car_engine_num,  # 发动机号
            "standard_quality": quality,  # 整备质量(中华必填)
            "first_register_date": car_infos.first_register_date,  # 初登日期(中华必填)
            "car_owner_type": car_infos.car_owner_type,  # 车主类型: 个人private(中华必填)
            # 车主信息
            "car_owner_uname": car_infos.car_owner_name,  # 车主姓名
            "car_owner_idcard":car_infos.car_owner_idcard,  # 车主身份证号
            "car_owner_idcard_address": car_infos.car_owner_address,  # 车主地址
            # 被保险人信息(购买人)
            "uname": car_infos.buy_name if not car_infos.owner_buyer_isone else car_infos.car_owner_name,  # 被保险人姓名(华安，中华必填)
            "idcard": car_infos.buy_idcard if not car_infos.owner_buyer_isone else car_infos.car_owner_idcard,  # 被保险人身份证号(华安，中华必填)
            # 机构信息
            "seller_id": "142",  # 机构ID
            "belong": "142",  # 所属机构ID
            "branch_id": "0",  # 分支机构ID:没有则为0
            "buyer_id": "682",  # 代理人ID
            # 保险信息
            "start_date_enforce": car_infos.start_date_enforce,  # 交强险起保日期
            "start_date_trade": car_infos.start_date_trade,  # 商业险起保日期
            "insurance_id": insurance_id,  # 保险类型:1 交强 2商业3商加交
            "insurance_name": insurance_name[insurance_id],  # 保险类型名称:险种名称 交强+商业或者交强、商业
            # others
            "remark": "",
            "come_from": "wx",
            "rta_type": car_infos.rta_type,
            "car_detail_type": car_infos.car_detail_type,  # 细化车型：怎么获取
            "car_number_type": car_infos.car_num_type,  # 车牌类型：怎么获取
            "license_type": car_infos.license_type,
        }

        if insurance == 'taiping':
            post_data['taiping_data'] = {
                "customerid": "3",
                "return_url": notify_url,
                "insuranceinfo": insuranceinfo,
                "taiping_config": {
                    "GROUP_NO": "snzhongyue001",
                    "SOLUTION_CODE": "0370010601002000250008"
                },
                "cityinfo": [
                    {
                        "city_code": "220000",
                        "city_id": "2302",
                        "city_name": "陕西",
                        "uname": "管理员123"
                    }
                ],
            }
        if insurance == 'huaan':
            post_data['huaan_data'] = {
                "order_id": post_id,
                "return_url": notify_url,
                "city_name": "陕西",
                "customerid": 14,
                "insuranceinfo": insuranceinfo,
                "huaan_config": {
                    "EXTENTERPCODE": "CMBC0601037064",
                    "PASSWORD": "baodaibao",
                    "SLS_CDE": "2701065374",
                    "USER": "baodaibao"
                }
            }
        if insurance == 'zhlh':
            post_data['zhlh_data'] = {
                "order_id": post_id,
                "customerid": "17",
                "return_url": notify_url,
                "insuranceinfo": insuranceinfo,
                "zhlh_config": {
                    "Salesman_number": "61000184",
                    "agency_code": "61970400",
                    "agent": "u4e0au6d77u4e1cu5927u4fddu9669u7ecfu7eaau6709u9650u8d23u4efbu516cu53f8u9655u897fu5206u516cu53f8",
                    "agent_name": "u4e0au6d77u4e1cu5927u4fddu9669u7ecfu7eaau6709u9650u8d23u4efbu516cu53f8u9655u897fu5206u516cu53f8",
                    "intermediary_agency_code": "2015000045",
                    "operator": "maxiaoping001",
                    "proxy_protocol_number": "B201761000040",
                    "salesman_name": "u5eb7u8000u6587",
                    "service_code": "6197J2004003"
                }
            }
        print 'post_data:',simplejson.dumps(post_data)
        try:
            request = urllib2.Request(url, 'data=%s' % simplejson.dumps(post_data))
            response = urllib2.urlopen(request)
            s = response.read()
            print 'baodaibao result:',s
            id_insuranceitem_nomarl_map = {
                1: 'damageI',  # '车辆损失险',
                2: 'thirdDutyI',  # ''第三者责任险',
                3: 'robbingI',  # '全车盗抢险',
                4: 'driverDutyI',  # '驾驶人员责任险',
                5: 'passengerDutyI',  # '乘客责任险',
                6: 'glassI',  # '玻璃单独破碎险',
                7: 'scratchI',  # '车身划痕险',
                8: 'fireDamageI',  # '自燃损失险',
                9: 'wadeI',  # '车辆涉水险',
                10: '倒车镜、车灯单独损失险',
                11: '',
                12: 'thirdSpecialI',  # '无法找到第三方特约险',
                13: '指定修理厂险'
            }
            id_insuranceitem_plus_map = {
                1: 'damageIPlus',  # '车辆损失险',
                2: 'thirdDutyIPlus',  # ''第三者责任险',
                3: 'robbingIPlus',  # '全车盗抢险',
                4: 'driverDutyIPlus',  # '驾驶人员责任险',
                5: 'passengerDutyIPlus',  # '乘客责任险',
                6: '玻璃单独破碎险',
                7: 'scratchIPlus',  # '车身划痕险',
                8: 'fireDamageIPlus',  # '自燃损失险',
                9: 'wadeIPlus',  # '车辆涉水险',
                10: '倒车镜、车灯单独损失险',
                11: '',
                12: '无法找到第三方特约险',
                13: '指定修理厂险'
            }

            bdb_json = simplejson.loads(s)
            if int(bdb_json['status']) == 200:
                result['flag'] = 1
                nomarl = [{id_insuranceitem_nomarl_map[int(k)]:v} for k,v in bdb_json['data']['quotation_price']['trade_price_detail'].items()]
                plus = [{id_insuranceitem_plus_map[int(k)]:v} for k,v in bdb_json['data']['quotation_price']['trade_deductible_price_detail'].items()]
                data = nomarl + plus
                dic = {
                    'businessI': 0,  # 商业险总额
                    'businessZK': 0,  # 商业险折扣
                    'forceI': 0,  # 交强
                    'forceZK': 0,  # 交强险折扣
                    'damageI': 0,  # 车辆损失
                    'damageIPlus': 0,  # 车损不计免赔
                    'thirdDutyI': 0,  # 三责
                    'thirdDutyIPlus': 0,  # 三责不计免赔
                    'robbingI': 0,  # 盗抢
                    'robbingIPlus': 0,  # 盗抢免责
                    'driverDutyI': 0,  # 车上司机
                    'driverDutyIPlus': 0,  # 车上司机免责
                    'passengerDutyI': 0,  # 车上乘客
                    'passengerDutyIPlus': 0,  # 车上乘客免责
                    'glassI': 0,  # 玻璃
                    'scratchI': 0,  # 划痕
                    'scratchIPlus': 0,  # 划痕免责
                    'fireDamageI': 0,  # 自燃
                    'fireDamageIPlus': 0,  # 自燃免责
                    'wadeI': 0,  # 涉水
                    'wadeIPlus': 0,  # 涉水免责
                    'thirdSpecialI': 0,  # 跑路
                    'vehicle_tax_price': 0,  # 车船税价格
                    'totalI': 0  # 保险总额
                }
                for item in data:
                    for k, v in item.items():
                        dic[k] = v
                total_price = 0.0
                if bdb_json['data']['quotation_price'].has_key('trade_price') and float(bdb_json['data']['quotation_price']['trade_price']):
                    price = float(bdb_json['data']['quotation_price']['trade_price'])
                    dic['businessI'] = price
                    total_price += price
                if bdb_json['data']['quotation_price'].has_key('enforce_price') and int(bdb_json['data']['quotation_price']['enforce_price']):
                    price = float(bdb_json['data']['quotation_price']['enforce_price'])
                    dic['forceI'] = price
                    total_price += price
                if bdb_json['data']['quotation_price'].has_key('vehicle_price') and int(bdb_json['data']['quotation_price']['vehicle_price']):
                    price = float(bdb_json['data']['quotation_price']['vehicle_price'])
                    dic['vehicle_tax_price'] = price
                    total_price += price
                if bdb_json['data']['quotation_price'].has_key('trade_price_discount') and float(bdb_json['data']['quotation_price']['trade_price_discount']):
                    dic['businessZK'] = float(bdb_json['data']['quotation_price']['trade_price_discount'])

                dic['totalI'] = total_price
                result['data'] = dic
            else:
                msglist = [item['MsgDesc'] for item in bdb_json['data']['body']['message']]
                result['msg'] = '\n'.join(msglist)
        except Exception,e:
            import traceback
            traceback.print_exc()
            result['flag']=0
            result['msg']='报价失败'
        #print 'return result:',simplejson.dumps(result)
        self.write(simplejson.dumps(result))

        # step = 15
        # id_insuranceitem_nomarl_map = {
        #     1: 'damageI',  # '车辆损失险',
        #     2: 'thirdDutyI',  # ''第三者责任险',
        #     3: 'robbingI',  # '全车盗抢险',
        #     4: 'driveDutyI',  # '驾驶人员责任险',
        #     5: 'passengerDutyI',  # '乘客责任险',
        #     6: 'glassI',  # '玻璃单独破碎险',
        #     7: 'scatchI',  # '车身划痕险',
        #     8: 'fireDamageI',  # '自燃损失险',
        #     9: 'wadeI',  # '车辆涉水险',
        #     10: '倒车镜、车灯单独损失险',
        #     11: '',
        #     12: 'thirdSpecialI',  # '无法找到第三方特约险',
        #     13: '指定修理厂险'
        # }
        # id_insuranceitem_plus_map = {
        #     1: 'damageIPlus',  # '车辆损失险',
        #     2: 'thirdDutyIPlus',  # ''第三者责任险',
        #     3: 'robbingIPlus',  # '全车盗抢险',
        #     4: 'driveDutyIPlus',  # '驾驶人员责任险',
        #     5: 'passengerDutyIPlus',  # '乘客责任险',
        #     6: '玻璃单独破碎险',
        #     7: 'scatchIPlus',  # '车身划痕险',
        #     8: 'fireDamageIPlus',  # '自燃损失险',
        #     9: 'wadeIPlus',  # '车辆涉水险',
        #     10: '倒车镜、车灯单独损失险',
        #     11: '',
        #     12: '无法找到第三方特约险',
        #     13: '指定修理厂险'
        # }
        # while(step < 0):
        #     bdbquotes = BaoDaiBaoQuote.select().where(BaoDaiBaoQuote.quotenum == post_id &
        #                                   BaoDaiBaoQuote.status == 0 )
        #     if bdbquotes.count():
        #         bdb = bdbquotes[0]
        #         bdb.status = 1
        #         bdb.save()
        #         bdb_json = simplejson.loads(bdb.content)
        #         nomarl = [{id_insuranceitem_nomarl_map[k]:v} for k,v in bdb_json['trade_price_detail'].items()]
        #         plus = [{id_insuranceitem_plus_map[k]:v} for k,v in bdb_json['trade_deductible_price_detail'].items()]
        #         result = nomarl + plus
        #         if bdb_json.has_key('enforce_price') and int(bdb_json['enforce_price']):
        #             result['forceI'] = int(bdb_json['enforce_price'])
        #         if bdb_json.has_key('vehicle_price') and int(bdb_json['vehicle_price']):
        #             result['vehicle_tax_price'] = int(bdb_json['vehicle_price'])
        #         self.write(simplejson.dumps(result))
        #     else:
        #         time.sleep(1)
        #     step -= 1

    @run_on_executor
    def caculate_iop_price(self,io_id,i_id,items,insurance_id,price,quality,displacement,
                                          model_code):
        if not (io_id and i_id and items):
            self.write('该订单不存在')

        i = Insurance.get(id=i_id)
        io = InsuranceOrder.get(id=io_id)
        items = simplejson.loads(items)

        self.quote_iop(i,io,items,insurance_id,price,quality,displacement,
                                          model_code)


    @asynchronous
    @coroutine
    def post(self):
        io_id = self.get_body_argument('io_id', 0)
        i_id = self.get_body_argument('i_id', 0)
        items = self.get_body_argument('i_items', '')
        insurance_id =self.get_body_argument('insurance_type','0')
        price = self.get_body_argument('price',0)
        quality = self.get_body_argument('quality',0)
        model_code = self.get_body_argument('model_code','')
        displacement = self.get_body_argument('displacement',0)
        print io_id,i_id,items,insurance_id,price,quality,displacement,model_code
        a = yield self.caculate_iop_price(io_id,i_id,items,insurance_id,
                                          price,quality,displacement,
                                          model_code)

@route(r'/ajax/baodaibao_notify', name='ajax_baodaibao_notify')  # 报价回调函数
class BaoDaiBaoNotifyHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass

    def post(self):
        result = {'flag': 0, 'msg': ''}
        data = self.get_argument('data',None)
        print data
        if data:
            # dosomething for baodaibao notify
            data = simplejson.loads(data)
            if data['status'] == '200':
                # 报价成功
                order_id = data['data']['order_id']
                items = data['data']['quotation_price']

                bdb = BaoDaiBaoQuote()
                bdb.insuranceorder = order_id
                bdb.content = simplejson.dumps(items)
                bdb.save()
                result['flag'] = 1
                result['msg'] = u'解析报价成功'
            else:
                bdb = BaoDaiBaoQuote()
                bdb.insuranceorder = 27
                bdb.content = simplejson.dumps(items)
                bdb.save()

        return simplejson.dumps(result)

