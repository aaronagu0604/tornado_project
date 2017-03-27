#!/usr/bin/env python
# coding=utf8

from handler import AdminBaseHandler, BaseHandler
from lib.route import route
from model import *
import time


@route(r'/user/show_insurance/(\d+)')  # 保单展示
class showInsurance(BaseHandler):
    def getInsuranceOrderReceiving(self, oid):
        iors = InsuranceOrderReceiving.select().where(InsuranceOrderReceiving.orderid==oid)
        if iors.count()>0:
            return iors[0]
        else:
            return None
    def get(self, oid):
        addr = self.get_argument('addr', '')
        if addr:
            if (int(oid)-97)%91:
                return self.render('site/404.html')
            oid = (int(oid)-97)/91
        else:
            if (int(oid)-997)%73:
                return self.render('site/404.html')
            oid = (int(oid)-997)/73
        o = InsuranceOrder.get(id=oid)
        if o.ordertype == 1:
            sql = 'select a.id, a.name from tb_store a where a.business_type=%s '
            q = db.handle.execute_sql(sql % o.ordertype)
        stores = []
        dictI = {}
        lists = Insurances.select()
        for list in lists:
            dictI[list.eName] = [list.name, list.style]
        for row in q.fetchall():
            stores.append({'id': row[0], 'name': row[1]})
        insurances = Product.select().where((Product.is_index == o.ordertype) & (Product.status == 1))
        ior = self.getInsuranceOrderReceiving(oid)
        paytime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(o.paytime))
        self.render('user/insuranceDetails/showInsurance.html', o=o, products=insurances, stores=stores,
                    active='insurance', dictI=dictI, ior=ior, paytime=paytime, addr=addr)





















