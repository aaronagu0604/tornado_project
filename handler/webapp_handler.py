#!/usr/bin/env python
# coding=utf8

import logging
import setting
import simplejson
from lib.route import route
import math
from model import *
from handler import BaseHandler, require_auth


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
                cars.append(c)
        else:
            for car in brand.cars:
                c = {}
                c['name'] = car.car_name
                c['car'] = 1
                c['id'] = car.id
                c['logo'] = car.logo
                cars.append(c)
        self.render("webapp/car.html", brand=brand, cars=cars)


@route(r'/webapp/detail/(\d+)', name='webapp_detail')
class WebAppDetailHandler(BaseHandler):
    def get(self, id):
        self.render("webapp/detail.html")