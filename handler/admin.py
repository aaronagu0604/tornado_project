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
        report['store'] = Store.select().where(Store.active >= 0, Store.store_type == 2).count()
        report['saler'] = Store.select().where(Store.active >= 0, Store.store_type == 1).count()
        report['user'] = User.select().count()
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
        ft = (Store.store_type == 1)
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
        uid = int(self.get_argument("id", '-1'))

        ft = (User.active > -1)
        if status >= 0:
            ft &= (User.active == status)
        if keyword:
            keyword2 = '%' + keyword + '%'
            ft &= ((Store.name % keyword2) | (User.truename % keyword2) | (User.mobile % keyword2))
        if uid > 0:
            ft &= (User.id == uid)
        cfs = User.select(User).join(Store).where(ft)
        total = cfs.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = 1
        cfs = cfs.order_by(User.store, User.truename).paginate(page, pagesize)
        self.render('/admin/user/user.html', users=cfs, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, active='user', status=status, keyword=keyword)


@route(r'/admin/store_detail/(\d+)', name='admin_store_detail')  # 修改经销商或门店
class StoreDetailHandler(AdminBaseHandler):
    def get(self, store_id):
        areas = Area.select().where((Area.is_delete == 0) & (Area.pid >> None)).order_by(Area.spell_abb, Area.sort)
        store = Store.get(id=store_id)
        active = 'saler'
        if store.store_type == 1:
            active = 'saler'
        elif store.store_type == 2:
            active = 'store'
        self.render('admin/user/store_detail.html', s=store, active=active, areas=areas)

    def post(self, store_id):
        name = self.get_argument('name', '')
        province = self.get_argument('province', '')
        city = self.get_argument('city', '')
        district = self.get_argument('district', '')
        address = self.get_argument('address', '')
        active = int(self.get_argument('active', 0))
        process_insurance = int(self.get_argument('process_insurance', 0))

        legal_person = self.get_argument('legal_person', '')
        license_code = self.get_argument('license_code', '')
        linkman = self.get_argument('linkman', '')
        mobile = self.get_argument('mobile', '')

        area_code = province
        if district and not district == '':
            area_code = district
        elif city and not city == '':
            area_code = city

        store = Store.get(id=store_id)
        store.name = name
        store.area_code = area_code
        store.address = address
        store.active = active
        store.process_insurance = process_insurance
        store.legal_person = legal_person
        store.license_code = license_code
        store.linkman = linkman
        store.mobile = mobile
        store.save()

        self.flash(u"保存成功")
        self.redirect("/admin/store_detail/" + str(store_id))


@route(r'/admin/score_history', name='admin_score_history')  # 积分消费历史
class ScoreHistoryHandler(AdminBaseHandler):
    def get(self):
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = self.settings['admin_pagesize']
        store_id = int(self.get_argument("store_id", '-1'))

        cfs = ScoreRecord.select().where((ScoreRecord.store == store_id) & (ScoreRecord.status == 1))
        total = cfs.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = 1
        cfs = cfs.order_by(ScoreRecord.created.desc()).paginate(page, pagesize)

        self.render('admin/user/score_history.html', list=cfs, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, store_id=store_id)


@route(r'/admin/money_history', name='admin_money_history')  # 余额消费历史
class MoneyHistoryHandler(AdminBaseHandler):
    def get(self):
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = self.settings['admin_pagesize']
        store_id = int(self.get_argument("store_id", '-1'))

        cfs = MoneyRecord.select().where((MoneyRecord.store == store_id) & (MoneyRecord.status == 1))
        total = cfs.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = 1
        cfs = cfs.order_by(MoneyRecord.apply_time.desc()).paginate(page, pagesize)

        self.render('admin/user/money_history.html', list=cfs, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, store_id=store_id)


@route(r'/admin/saler_product/(\d+)', name='admin_saler_product')  # 经销商产品地域信息
class SalerProductHandler(AdminBaseHandler):
    def get(self, store_id):
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = self.settings['admin_pagesize']
        store = Store.get(id=store_id)
        cfs = ProductRelease.select().where(ProductRelease.store == store_id)
        total = cfs.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = 1
        cfs = cfs.order_by(ProductRelease.id.asc()).paginate(page, pagesize)
        self.render('admin/user/saler_product.html', s=store, products=cfs, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, active='saler')


@route(r'/admin/store_area_product', name='admin_store_area_product')  # 经销商产品地域价格信息
class SalerProductAreaPriceHandler(AdminBaseHandler):
    def get(self):
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = self.settings['admin_pagesize']
        store_id = int(self.get_argument("sid", '-1'))
        code = self.get_argument("code", '0')
        keyword = '' + code + '%'
        cfs = StoreProductPrice.select(StoreProductPrice.product_release).where((StoreProductPrice.store == store_id) &
                    (StoreProductPrice.area_code % keyword)).group_by(StoreProductPrice.product_release)
        total = cfs.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = 1
        cfs = cfs.paginate(page, pagesize)
        self.render('admin/user/saler_area_product.html', products=cfs, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, store_id=store_id, code=code, Area=Area)


@route(r'/admin/referee', name='admin_referee_list')  # 服务商管理列表
class RefereeList(AdminBaseHandler):
    def get(self):
        keyword = self.get_argument("keyword", '')
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = self.settings['admin_pagesize']
        ft = (AdminUser.roles == 'S')
        if keyword:
            keyword = '%'+keyword+'%'
            ft = (AdminUser.realname % keyword) | (AdminUser.code % keyword)

        s = AdminUser.select().where(ft)
        total = s.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        referees = s.paginate(page, pagesize)
        referees_list = []
        for i, referee in enumerate(referees):
            ss = Store.select().where((Store.admin_user==referee.id) & (Store.active==1))
            insurance_order_count = 0
            for s in ss:
                insurance_order_count += InsuranceOrder.select().where(InsuranceOrder.store==s & InsuranceOrder.status>2).count()
            referees_list.append({
                'number': i+1,
                'referee_name': referee.realname,
                'referee_number': referee.code,
                'store_count': ss.count(),
                'insurance_order_count': insurance_order_count
            })
        self.render("admin/user/referee_list.html",page=page, referees=referees_list, active='referee', Area=Area,
                    totalpage=totalpage)









