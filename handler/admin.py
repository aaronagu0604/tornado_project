#!/usr/bin/env python
# coding=utf8

from handler import AdminBaseHandler, BaseHandler
from lib.route import route
from model import *
import time
import logging


@route(r'/admin', name='admin_index')  # 后台首页
class IndexHandler(AdminBaseHandler):
    def get(self):
        report = {}
        report['insurance'] = Insurance.select().where(Insurance.active == 1).count()
        report['store'] = Store.select().where(Store.active == 1, Store.store_type == 2).count()
        report['saler'] = Store.select().where(Store.active == 1, Store.store_type == 1).count()
        report['order_i'] = InsuranceOrder.select().where(InsuranceOrder.status > 0).count()
        report['order_n'] = SubOrder.select().where(SubOrder.status > 0).count()
        report['product_n'] = Product.select().where(Product.active == 1, Product.is_score == 0).count()
        report['product_s'] = Product.select().where(Product.active == 1, Product.is_score == 1).count()
        logs = AdminUserLog.select().order_by(AdminUserLog.created.desc()).limit(20)
        self.render('admin/index.html', report=report, logs=logs)


@route(r'/admin/login', name='admin_login')  # 后台登录
class LoginHandler(BaseHandler):
    def get(self):
        self.render('admin/login.html')

    def post(self):
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        if username and password:
            try:
                user = AdminUser.get(AdminUser.username == username)
                if user.check_password(password):
                    if user.active == 1:
                        user.updatesignin()
                        self.session['admin'] = user
                        self.session.save()
                        self.redirect("/admin")
                        return
                    else:
                        self.flash("此账户被禁止登录，请联系管理员。")
                else:
                    self.flash("密码错误")
            except Exception, e:
                print e
                self.flash("此用户不存在")
        else:
            self.flash("请输入用户名或者密码")

        self.render("/admin/login.html", next=self.next_url)


@route(r'/admin/logout', name='admin_logout')  # 后台退出
class LogoutHandler(AdminBaseHandler):
    def get(self):
        if "admin" in self.session:
            del self.session["admin"]
            self.session.save()
        self.render('admin/login.html')


@route(r'/admin/saler', name='admin_saler')  # 后台经销商
class SalerHandler(AdminBaseHandler):
    def get(self):
        province = self.get_argument("province", '')
        city = self.get_argument("city", '')
        town = self.get_argument("district", '')
        keyword = self.get_argument("keyword", '')
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = self.settings['admin_pagesize']

        default_province = ''
        default_city = ''
        default_district = ''
        ft = ((Store.active == 1) & (Store.store_type == 1))
        if town and town != '':
            ft &= (Store.area_code == town)
            default_province = town[:4]
            default_city = town[:8]
            default_district = town
        elif city and city != '':
            default_province = city[:4]
            default_city = city
            city += '%'
            ft &= (Store.area_code % city)
        elif province and province != '':
            default_province = province
            province += '%'
            ft &= (Store.area_code % province)
        if keyword:
            keyword2 = '%' + keyword + '%'
            ft &= (Store.name % keyword2)

        s = Store.select().where(ft)
        total = s.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = 1
        stores = s.paginate(page, pagesize)
        items = Area.select().where((Area.pid >> None) & (Area.is_delete == 0) & (Area.is_site == 1)).order_by(
            Area.spell, Area.sort)
        self.render("admin/user/saler.html", stores=stores, total=total, totalpage=totalpage, keyword=keyword,
                    province=default_province, city=default_city, district=default_district,
                    page=page, pagesize=pagesize, items=items, Area=Area, active='saler')


@route(r'/admin/store', name='admin_store')  # 门店管理
class StoresHandler(AdminBaseHandler):
    def get(self):
        province = self.get_argument("province", '')
        city = self.get_argument("city", '')
        town = self.get_argument("district", '')
        keyword = self.get_argument("keyword", '')
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = self.settings['admin_pagesize']
        status = int(self.get_argument("status", '-1'))
        default_province = ''
        default_city = ''
        default_district = ''

        ft = (Store.store_type == 2)
        if status >= 0:
            ft &= (Store.active == status)
        if town and town != '':
            ft &= (Store.area_code == town)
            default_province = town[:4]
            default_city = town[:8]
            default_district = town
        elif city and city != '':
            default_province = city[:4]
            default_city = city
            city += '%'
            ft &= (Store.area_code % city)
        elif province and province != '':
            default_province = province
            province += '%'
            ft &= (Store.area_code % province)
        if keyword:
            keyword2 = '%' + keyword + '%'
            ft &= (Store.name % keyword2)
        cfs = Store.select().where(ft)
        total = cfs.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = 1
        cfs = cfs.paginate(page, pagesize)
        items = Area.select().where((Area.pid >> None) & (Area.is_delete == 0) & (Area.is_site == 1)).order_by(
            Area.spell, Area.sort)
        self.render('/admin/user/store.html', stores=cfs, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, active='store', status=status, keyword=keyword, Area=Area, items=items,
                    province=default_province, city=default_city, district=default_district)


@route(r'/admin/user', name='admin_user')  # 客户管理
class UsersHandler(AdminBaseHandler):
    def get(self):
        keyword = self.get_argument("keyword", '')
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = self.settings['admin_pagesize']
        status = int(self.get_argument("status", '-1'))

        ft = (User.active > -1)
        if status >= 0:
            ft &= (User.active == status)
        if keyword:
            keyword2 = '%' + keyword + '%'
            ft &= ((Store.name % keyword2) | (User.truename % keyword2) | (User.mobile % keyword2))
        cfs = User.select(User).join(Store).where(ft)
        total = cfs.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = 1
        cfs = cfs.order_by(User.store, User.truename).paginate(page, pagesize)
        self.render('/admin/user/user.html', users=cfs, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, active='user', status=status, keyword=keyword)
