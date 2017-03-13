#!/usr/bin/env python
# coding=utf8

import logging
import setting
import simplejson
from lib.route import route
from model import *
from handler import BaseHandler
from tornado.web import RequestHandler


@route(r'/webapp', name='webapp_index')
class WebAppIndexHandler(BaseHandler):
    def get(self):
        brands = []
        chars = '<li>#</li>'
        q = CarBrand.select(CarBrand.brand_pinyin_first).where(CarBrand.active == 1).group_by(CarBrand.brand_pinyin_first).\
            order_by(CarBrand.brand_pinyin_first.asc(), CarBrand.sort.asc()).tuples()
        for py, in q:
            chars += '<li>' + py + '</li>'
            item = {}
            item['char'] = py
            item['items'] = CarBrand.select().where((CarBrand.active == 1) & (CarBrand.brand_pinyin_first == py))
            brands.append(item)

        self.render("webapp/index.html", brands=brands, chars=chars)


@route(r'/webapp/car/(\d+)', name='webapp_car')
class WebAppCarHandler(BaseHandler):
    def get(self, id):
        brand = CarBrand.get(id=id)
        cars = []
        for factory in brand.factories:
            fac = {}
            fac['name'] = factory.factory_name
            fac['car'] = 0
            cars.append(fac)
            for car in factory.cars:
                c = {}
                c['name'] = car.car_name
                c['car'] = 1
                c['id'] = car.id
                c['logo'] = car.logo
                c['saleoff'] = car.stop_sale
                cars.append(c)
        else:
            for car in brand.cars:
                c = {}
                c['name'] = car.car_name
                c['car'] = 1
                c['id'] = car.id
                c['logo'] = car.logo
                c['saleoff'] = car.stop_sale
                cars.append(c)
        self.render("webapp/car.html", brand=brand, cars=cars)


@route(r'/webapp/car_item_list/(\d+)', name='webapp_car_item_list')  # 车型详情列表
class WebAppCarItemListHandler(RequestHandler):
    def get(self, id):
        result = {'flag': 0, 'msg': '', "data": {}}

        car = Car.get(id=id)
        if car:
            result['flag'] = 1
            result['data']['saleoff'] = car.stop_sale
            result['data']['name'] = car.car_name
            result['data']['logo'] = car.logo
            result['data']['detail_list'] = []
            for item in car.groups:
                group = {}
                group['name'] = item.group_name
                group['items'] = []
                result['data']['detail_list'].append(group)
                for carItem in item.items:
                    ci = {}
                    ci['name'] = carItem.car_item_name
                    ci['gearbox'] = carItem.gearbox
                    ci['saleoff'] = carItem.stop_sale
                    group['items'].append(ci)

        else:
            result['msg'] = "系统异常"
        self.write(simplejson.dumps(result))


@route(r'/webapp/detail/(\d+)', name='webapp_detail')
class WebAppDetailHandler(BaseHandler):
    def get(self, id):
        car = Car.get(id=id)
        self.render("webapp/detail.html", car=car)