#!/usr/bin/env python
# coding=utf8

import logging
import setting
import simplejson
from lib.route import route
from model import *
from handler import MobileBaseHandler


@route(r'/mobile/mine', name='mobile_mine')  # app我的主界面
class MobileMineHandler(MobileBaseHandler):
    """
    @apiGroup mine
    @apiVersion 1.0.0
    @api {get} /mobile/mine 01. app我的主界面
    @apiDescription app我的主界面

    @apiHeader {String} token 用户登录凭证

    @apiSampleRequest /mobile/mine
    """
    def get(self):
        result = {'flag': 0, 'msg': '', "data": {}}
        user = self.get_user()
        if user is None:  # 未登录
            result['data']['store_name'] = ''
            result['data']['user_name'] = ''
            result['data']['store_type'] = ''
            result['data']['store_price'] = 0
            result['data']['store_score'] = 0
            result['data']['show_sale_orders'] = 1
            result['data']['show_buy_orders'] = 1
            result['data']['show_product_manager'] = 1
            result['data']['sale_orders'] = {}
            result['data']['sale_orders']['wait_pay'] = 0
            result['data']['sale_orders']['wait_send'] = 0
            result['data']['sale_orders']['wait_get'] = 0
            result['data']['sale_orders']['wait_comment'] = 0
            result['data']['sale_orders']['wait_pay_back'] = 0
            result['data']['buy_orders'] = {}
            result['data']['buy_orders']['wait_pay'] = 0
            result['data']['buy_orders']['wait_send'] = 0
            result['data']['buy_orders']['wait_get'] = 0
            result['data']['buy_orders']['wait_comment'] = 0
            result['data']['buy_orders']['wait_pay_back'] = 0
        else:  # 已登录
            result['data']['store_name'] = user.store.name
            result['data']['user_name'] = user.mobile

            result['data']['store_price'] = user.store.price
            result['data']['store_score'] = user.store.score
            if user.store.store_type == 1:
                result['data']['store_type'] = '服务商'
                result['data']['show_sale_orders'] = 1
                result['data']['show_buy_orders'] = 0
                result['data']['show_product_manager'] = 1
                result['data']['buy_orders'] = {}
                result['data']['buy_orders']['wait_pay'] = 0
                result['data']['buy_orders']['wait_send'] = 0
                result['data']['buy_orders']['wait_get'] = 0
                result['data']['buy_orders']['wait_pay_back'] = 0
                # 查询

                result['data']['sale_orders'] = {}
                result['data']['sale_orders']['wait_pay'] = 0
                result['data']['sale_orders']['wait_send'] = 0
                result['data']['sale_orders']['wait_get'] = 0
                result['data']['sale_orders']['wait_pay_back'] = 0
            elif user.store.store_type == 2:
                result['data']['store_type'] = '门店'
                result['data']['show_sale_orders'] = 0
                result['data']['show_buy_orders'] = 1
                result['data']['show_product_manager'] = 0
                result['data']['sale_orders'] = {}
                result['data']['sale_orders']['wait_pay'] = 0
                result['data']['sale_orders']['wait_send'] = 0
                result['data']['sale_orders']['wait_get'] = 0
                result['data']['sale_orders']['wait_comment'] = 0
                result['data']['sale_orders']['wait_pay_back'] = 0
                # 查询
                result['data']['buy_orders'] = {}
                result['data']['buy_orders']['wait_pay'] = 0
                result['data']['buy_orders']['wait_send'] = 0
                result['data']['buy_orders']['wait_get'] = 0
                result['data']['buy_orders']['wait_comment'] = 0
                result['data']['buy_orders']['wait_pay_back'] = 0
        self.write(simplejson.dumps(result))
        self.finish()