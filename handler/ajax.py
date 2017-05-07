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
import StringIO
from PIL import Image
from pytesseract import image_to_string

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
            # rates = InsuranceScoreExchange.get_score_policy(io.store.area_code, iop.insurance.id)
            rates = self.get_return_cash(io.store.id, iid)
            if rates:
                iis = InsuranceItem.select().where(InsuranceItem.style_id > 1)
                result['data']['force_tax'] = rates['ftr']
                result['data']['business_tax'] = rates['btr']
                result['data']['ali_rate'] = rates['ar']
                result['data']['profit_rate'] = rates['pr']
                result['data']['base_money'] = rates['bm']
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
            print result['data']
        except Exception, e:
            result['msg'] = u'系统错误%s'%str(e)
            print e.message

        self.write(simplejson.dumps(result))


@route(r'/ajax/caculate_gift_oil', name='ajax_get_gift_oil_rate')  # 获取返佣比率
class GetGiftOilHandler(BaseHandler):
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        iid = int(self.get_argument('insurance', 0))
        iopid = int(self.get_argument('iopid', 0))
        forcetotal = int(self.get_argument('force', 0))
        businesstotal = int(self.get_argument('business', 0))
        try:
            iop = InsuranceOrderPrice.get(id=iopid)
            insurance = InsuranceOrder.get(id=iop.insurance_order_id)
            policy = LubePolicy.get_oil_policy(insurance.store.area_code, iid)
            policylist = simplejson.loads(policy.policy)

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
                pid.cash = groups['cash']
            else:
                pid.cash = 0
            pid.total_price = groups['total_price']
            pid.force_price = groups['force_price']
            pid.business_price = groups['business_price']
            pid.vehicle_tax_price = groups['vehicle_tax_price']
            pid.sms_content = groups['psummary']
            for item in i_items:
                pid.__dict__['_data'][item+'Price'] = i_items[item]
            pid.save()
            if send_msg == '1':
                io = InsuranceOrder.get(id=pid.insurance_order_id)
                sms = {'mobile': io.store.mobile, 'signtype': '1', 'isyzm': 'changePrice',
                       'body': [io.ordernum, pid.insurance.name, groups['total_price'], groups['psummary']]}
                create_msg(simplejson.dumps(sms), 'sms')  # 变更价格
            result['flag'] = 1
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
        if not (ar_num and ar_reason and pid and ar_status):
            result['msg'] = u'参数不全'
            self.write(simplejson.dumps(result))
            return
        try:
            ar_num = float(ar_num)
            io = InsuranceOrder.get(current_order_price=pid)
            iop = InsuranceOrderPrice.get(id=pid)
            if iop.append_refund_status != int(ar_status):
                result['msg'] = u'该补退款已有别人发起，刷新页面确认后重试！'
            else:
                if ar_num > 0:    # 让客户补款
                    iop.append_refund_status = 1
                elif ar_num < 0:    # 给客户退款
                    io.store.price += ar_num
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
        except Exception, e:
            result['msg'] = u'申请补款失败：%s' % e.message
        content = u'申请补退款：客户:%s，订单:%s，金额:%s元，原因:%s，操作人:%s，' % \
                  (io.store.name, io.ordernum, ar_num, ar_reason, admin_user.username)
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
        print('-----')
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

@route(r'/ajax/ocr', name='ajax_ocr')  # 自动识别图片信息
class OCRHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass

    def get(self):
        io_id = self.get_argument('io_id', None)
        if not io_id:
            self.write('该订单不存在')
        io = InsuranceOrder.get(id=io_id)
        result = {}
        if io.id_card_front:
            print io.id_card_back
            request = urllib2.Request(io.id_card_front)
            img_data = urllib2.urlopen(request).read()
            img_buffer = StringIO.StringIO(img_data)
            img = Image.open(img_buffer)
            ocrresult = image_to_string(image=img,lang='chi_sim')
            print ocrresult
            result['id_card_front'] = ocrresult
        if io.id_card_back:
            request = urllib2.Request(io.id_card_back)
            img_data = urllib2.urlopen(request).read()
            img_buffer = StringIO.StringIO(img_data)
            img = Image.open(img_buffer)
            ocrresult = image_to_string(image=img,lang='chi_sim')
            result['id_card_back'] = ocrresult
        if io.drive_card_front:
            request = urllib2.Request(io.drive_card_front)
            img_data = urllib2.urlopen(request).read()
            img_buffer = StringIO.StringIO(img_data)
            img = Image.open(img_buffer)
            ocrresult = image_to_string(image=img,lang='chi_sim')
            result['drive_card_front'] = ocrresult
        if io.drive_card_back:
            request = urllib2.Request(io.drive_card_back)
            img_data = urllib2.urlopen(request).read()
            img_buffer = StringIO.StringIO(img_data)
            img = Image.open(img_buffer)
            ocrresult = image_to_string(image=img,lang='chi_sim')
            result['drive_card_back'] = ocrresult
        self.write(simplejson.dumps(result))

