#!/usr/bin/env python
# coding=utf8

from handler import AdminBaseHandler, BaseHandler
from lib.route import route
from model import *
import simplejson
import time
import logging
import setting
import os
from payqrcode import postRequest
from tornado.gen import coroutine
from tornado.web import asynchronous
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from lib.mqhelper import create_msg

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
            totalpage = total / pagesize if (total / pagesize) > 0 else 1
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
            totalpage = total / pagesize if (total / pagesize) > 0 else 1
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
            totalpage = total / pagesize if (total / pagesize) > 0 else 1
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
        policies = SSILubePolicy.select().where(SSILubePolicy.store == store)
        self.render('admin/user/store_detail.html', s=store, active=active, areas=areas, policies=policies)

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

@route(r'/admin/delete_policy/(\d+)', name='admin_delete_policy')  # 删除政策
class DeletePolicyHandler(AdminBaseHandler):
    def get(self, store_id):
        iid = self.get_argument('iid', None)
        if iid:
            SSILubePolicy.delete().where((SSILubePolicy.store == store_id) & (SSILubePolicy.insurance == iid)).execute()

        self.redirect('/admin/store_detail/%s'%store_id)

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
            totalpage = total / pagesize if (total / pagesize) > 0 else 1
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
            totalpage = total / pagesize if (total / pagesize) > 0 else 1
        cfs = cfs.order_by(MoneyRecord.apply_time.desc()).paginate(page, pagesize)

        self.render('admin/user/money_history.html', list=cfs, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, store_id=store_id)


@route(r'/admin/saler_product/(\d+)', name='admin_saler_product')  # 经销商产品地域信息
class SalerProductHandler(AdminBaseHandler):
    def get(self, store_id):
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = int(self.get_argument("pagesize", '20') if len(self.get_argument("pagesize", '20')) > 0 else '20')
        store = Store.get(id=store_id)
        keyword = self.get_argument("keyword", '')
        ft = (ProductRelease.store == store_id)
        if len(keyword) > 0:
            try:
                pid = int(keyword)
                ft &= (ProductRelease.id == pid)
            except:
                keyword2 = '%' + keyword + '%'
                ft &= (Product.name % keyword2)

        cfs = ProductRelease.select(ProductRelease).join(Product).where(ft)
        total = cfs.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize if (total / pagesize) > 0 else 1
        cfs = cfs.order_by(ProductRelease.id.asc()).paginate(page, pagesize)

        self.render('admin/user/saler_product.html', s=store, products=cfs, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, active='saler', keyword=keyword)


@route(r'/admin/change_release_area/(\d+)', name='admin_change_release_area')  # 经销商产品地域信息
class ChangeReleaseAreaHandler(AdminBaseHandler):
    def get(self, store_id):
        sas = StoreArea.select().where(StoreArea.store == store_id)
        codes = [sa.area.code for sa in sas]
        items = Area.select().where(Area.pid >> None)

        self.render('admin/user/change_release_area.html', codes=codes, items=items, sid=store_id)

    def post(self, store_id):
        flag = self.get_body_argument('flag', '')
        area_codes = self.get_body_argument('area_codes', '').split(',')
        result = {'msg': ''}
        if flag == '1':
            for sa in StoreArea.select().join(Area).where(StoreArea.store == store_id):
                for area_code in area_codes:
                    if area_code[:len(sa.area.code)] == sa.area.code:
                        area_codes.remove(area_code)
                        break
            for area_code in area_codes:
                try:
                    aid = Area.get(code=area_code).id
                    StoreArea.create(area=aid, store=store_id)
                except Exception, e:
                    pass
            result['msg'] = u'添加成功，刷新销售商品页'
        elif flag == '0':
            sas = [sa.area.code for sa in StoreArea.select().join(Area).where(StoreArea.store == store_id)]
            need_add_area_id = []
            need_del_area_code = []
            for area_code in area_codes:
                for sa_code in sas:
                    if area_code in sa_code:  # 例：已有市要删省，把已有的市删掉。或已有市删除该市
                        need_del_area_code.append(sa_code)
                    elif sa_code in area_code:  # 例：已有省要删市或区，删除省添加本省其它市
                        store_code_son_len = len(sa_code) + 4
                        store_code_g_son_len = len(sa_code) + 8
                        sa_code += '%'
                        if store_code_son_len == len(area_code):  # 省删市或市删区
                            need_add_area_id = [area.id for area in Area.select().where((Area.code % sa_code) &
                                (db.fn.Length(Area.code) == store_code_son_len))]
                            need_add_area_id.remove(Area.get(code=area_code).id)
                        elif store_code_g_son_len == len(area_code):  # 省删区
                            need_add_area_id = [area.id for area in Area.select().where((Area.code % sa_code) &
                                (db.fn.Length(Area.code) == store_code_son_len))]
                            need_add_area_id.remove(Area.get(code=area_code[:-4]).id)
                            area_code_match = area_code[:-4] + '%'
                            need_add_area_id = [area.id for area in Area.select().where((Area.code % area_code_match) &
                                (db.fn.Length(Area.code) == store_code_g_son_len))]
                            need_add_area_id.remove(Area.get(code=area_code).id)
            print('---%s---%s---'%(need_add_area_id, need_del_area_code))
            # need_del_sa_id = [sa.id for sa in StoreArea.select().join(Area).where((StoreArea.store == store_id) & (Area.code << need_del_area_code))]
            # StoreArea.delete().where(StoreArea.id << need_del_sa_id).execute()
            # for aid in need_add_area_id:
            #     StoreArea.create(area=aid, store=store_id)
            result['msg'] = u'删除成功，刷新销售商品页'
        else:
            result['msg'] = u'传入参数异常'
        self.write(simplejson.dumps(result))

@route(r'/admin/store_area_product', name='admin_store_area_product')  # 经销商产品地域价格信息
class SalerProductAreaPriceHandler(AdminBaseHandler):
    def get(self):
        keyword = self.get_argument("keyword", '')
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = int(self.get_argument("pagesize", '20') if len(self.get_argument("pagesize", '20')) > 0 else '20')
        store_id = int(self.get_argument("sid", '-1'))
        code = self.get_argument("code", '0')
        code2 = '' + code + '%'
        ft = ((StoreProductPrice.store == store_id) & (StoreProductPrice.area_code % code2))
        if len(keyword) > 0:
            keyword2 = '%' + keyword + '%'
            ft &= (Product.name % keyword2)
        cfs = StoreProductPrice.select(StoreProductPrice.product_release).join(ProductRelease).join(Product).where(ft).\
            group_by(StoreProductPrice.product_release)
        total = cfs.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize if (total / pagesize) > 0 else 1
        cfs = cfs.paginate(page, pagesize)
        self.render('admin/user/saler_area_product.html', products=cfs, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, store_id=store_id, code=code, Area=Area, keyword=keyword)


@route(r'/admin/referee', name='admin_referee_list')  # 推广人员列表
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
                'id': referee.id,
                'number': i+1,
                'referee_name': referee.realname,
                'referee_number': referee.code,
                'store_count': ss.count(),
                'insurance_order_count': insurance_order_count
            })
        self.render("admin/user/referee_list.html",page=page, referees=referees_list, active='referee', Area=Area,
                    totalpage=totalpage)


@route(r'/admin/product_release_add/(\d+)', name='admin_product_release_add')  # 批量添加产品到经销商库
class ProductReleaseAddHandler(AdminBaseHandler):
    def get(self, store_id):
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = int(self.get_argument("pagesize", '20') if len(self.get_argument("pagesize", '20')) > 0 else '20')
        keyword = self.get_argument("keyword", '')
        ft = (Product.active == 1)
        if len(keyword) > 0:
            keyword2 = '%' + keyword + '%'
            ft &= (Product.name % keyword2)

        cfs = Product.select().where(ft)
        total = cfs.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize if (total / pagesize) > 0 else 1
        cfs = cfs.order_by(Product.created.desc()).paginate(page, pagesize)
        self.render('admin/user/saler_product_release_add.html', products=cfs, total=total, page=page,
                    pagesize=pagesize, totalpage=totalpage, keyword=keyword, store_id=store_id)


@route(r'/admin/product_publish/(\d+)', name='admin_product_publish')  # 经销商发布商品到地区
class ProductPublishHandler(AdminBaseHandler):
    def get(self, store_id):
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = int(self.get_argument("pagesize", '20') if len(self.get_argument("pagesize", '20')) > 0 else '20')
        keyword = self.get_argument("keyword", '')
        codes = self.get_argument("codes", '')
        codes = codes.split(',')
        ft = ((ProductRelease.active == 1) & (Product.active == 1) & (ProductRelease.store == store_id))
        if len(keyword) > 0:
            keyword2 = '%' + keyword + '%'
            ft &= (Product.name % keyword2)

        cfs = ProductRelease.select(ProductRelease).join(Product).where(ft)
        total = cfs.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize if (total / pagesize) > 0 else 1
        cfs = cfs.order_by(ProductRelease.sort.asc()).paginate(page, pagesize)
        self.render('admin/user/saler_product_publish.html', products=cfs, total=total, page=page, codes=codes,
                    pagesize=pagesize, totalpage=totalpage, keyword=keyword, store_id=store_id, Area=Area)


@route(r'/admin/admin_user/(\d+)', name='admin_admin_user')  # 后台用户管理
class AdminUserHandler(AdminBaseHandler):
    def get(self, admin_id):
        page = int(self.get_body_argument("page", '1'))
        pagesize = setting.ADMIN_PAGESIZE
        try:
            qadminuser = AdminUser.select()
            if int(admin_id) > 0:
                adminUser = AdminUser.get(id=admin_id)
                default_province = adminUser.area_code[0:4]
                default_city = adminUser.area_code[0:8]
                default_district = adminUser.area_code
            else:
                adminUser = None
                default_province = ''
                default_city = ''
                default_district = ''

            total = qadminuser.count()
            if total % pagesize > 0:
                totalpage = total / pagesize + 1
            else:
                totalpage = total / pagesize
            ivs = qadminuser.order_by(AdminUser.id.desc()).paginate(page, pagesize)
            items = Area.select().where(Area.pid >> None)

            self.render("admin/user/admin_user.html",ivs=ivs, adminUser=adminUser, total=total, page=page,
                        pagesize=pagesize, totalpage=totalpage, active='admin_user', items=items, Area=Area,
                        default_province=default_province, default_city=default_city, default_district=default_district)
        except Exception, e:
            self.write("程序出错了，可能是参数传递错误！")

    def post(self, admin_id):
        admin_id = int(admin_id)
        username = self.get_argument('username', '')
        password = self.get_argument('password', '')
        realname = self.get_argument('realname', '')
        mobile = self.get_argument('mobile', '')
        email = self.get_argument('email', '')
        roles = self.get_argument('roles', '')
        active = self.get_argument('active', '')
        code = self.get_argument('code', '')
        province_code = self.get_argument('province_code', '')
        city_code = self.get_argument('city_code', '')
        district_code = self.get_argument('district_code', '')
        if district_code and district_code != '0':
            area_code = district_code
        elif city_code and city_code != '0':
            area_code = city_code
        elif province_code and province_code != '0':
            area_code = province_code
        else:
            area_code = ''
        user = self.get_admin_user()
        is_root = ('A' in user.roles or 'D' in user.roles)

        if is_root and admin_id == 0:
            adminUser = AdminUser()
            adminUser.signuped = int(time.time())
            adminUser.lsignined = 0
            adminUser.password = AdminUser.create_password(password)
            adminUser.username = username
            adminUser.mobile = mobile
            adminUser.email = email
            adminUser.roles = roles
            adminUser.code = code
            adminUser.area_code = area_code
            adminUser.realname = realname
            if active == 'on':
                adminUser.active = 1
            else:
                adminUser.active = 0
            adminUser.save()
        elif (admin_id > 0 and user.id == admin_id) or (is_root):
            adminUser = AdminUser.get(id=admin_id)
            if password:
                adminUser.password = AdminUser.create_password(password)
            adminUser.username = username
            adminUser.mobile = mobile
            adminUser.email = email
            adminUser.realname = realname
            adminUser.code = code
            adminUser.area_code = area_code
            if is_root:
                adminUser.roles = roles
                if active:
                    adminUser.active = 1
                else:
                    adminUser.active = 0
            adminUser.save()
        self.session['admin'] = adminUser
        self.session.save()
        self.flash("提交成功")
        self.redirect("/admin/admin_user/%s"%(adminUser.id))


# -----------------------------------------------------------商品管理---------------------------------------------------
@route(r'/admin/category', name='admin_category')  # 商品分类
class CategoryHandler(AdminBaseHandler):
    def get(self):
        categories = Category.select().order_by(Category.hot, Category.sort)
        self.render('admin/product/category.html', categories=categories, active='category')


@route(r'/admin/category/(\d+)', name='admin_category_edit')  # 编辑分类
class CategoryEditHandler(AdminBaseHandler):
    def get(self, id):
        if int(id) == 0:
            category = None
        else:
            category = Category.get(id=id)
        self.render('admin/product/category_edit.html', active='category', category=category)

    def post(self, id):
        name = self.get_body_argument("name", '')
        sort = int(self.get_body_argument("sort", 1))
        hot = self.get_body_argument("hot", '')
        active = self.get_body_argument("active", '')
        mobile_img = self.request.files.get('file_mobile')[0]['body']
        pc_img = self.request.files.get('file_pc')[0]['body']

        if int(id) > 0:
            show_msg = "修改"
            category = Category.get(id=id)
        else:
            show_msg = "添加"
            category = Category()
        category.name = name
        category.sort = sort
        category.hot = 1 if hot else 0
        category.active = 1 if active else 0
        message_path = setting.admin_file_path + 'category'
        try:
            datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前时间作为图片名称
            if mobile_img:
                if not os.path.isdir(message_path):
                    os.makedirs(message_path)
                filename = message_path + str(datetime) + "_mobile.jpg"
                with open(filename, "wb") as f:
                    f.write(mobile_img)
                imgurl = postRequest(open(filename, 'rb'))
                if not imgurl:
                    imgurl = ''
                category.img_m = imgurl
            if pc_img:
                filename = message_path + str(datetime) + "_pc.jpg"
                with open(filename, "wb") as f:
                    f.write(pc_img)
                imgurl = postRequest(open(filename, 'rb'))
                if not imgurl:
                    imgurl = ''
                category.img_m = imgurl
                category.img_pc = imgurl
            category.save()
            self.flash(show_msg + u"成功")
        except Exception, ex:
            self.flash(str(ex))
        self.redirect('/admin/category')


@route(r'/admin/category_attribute/(\d+)', name='admin_category_attribute')  # 添加/修改分类的规格参数
class CategoryAttributeHandler(AdminBaseHandler):
    def get(self, cid):
        category_attributes = Category.get(id=cid).attributes
        self.render('admin/product/category_attribute.html', active='category', category_attributes=category_attributes, cid=cid)


@route(r'/admin/category_attribute_edit/(\d+)', name='admin_category_attribute_edit')  # 添加/修改分类的规格
class CategoryAttributeAddHandler(AdminBaseHandler):
    def get(self, ca_id):
        cid = self.get_argument('cid', None)
        status = self.get_argument('status', None)
        if status == '0':
            category_attribute = CategoryAttribute.get(id=ca_id)
            category_attribute.active = 0
            category_attribute.save()
            self.redirect('/admin/category_attribute/%s' % cid)
        else:
            if ca_id != '0':
                category_attribute = CategoryAttribute.get(id=ca_id)
            else:
                category_attribute = None
            self.render('admin/product/category_attribute_edit.html', active='category',
                        category_attribute=category_attribute, cid=cid)

    def post(self, ca_id):
        category = self.get_body_argument('cid', None)
        name = self.get_body_argument('name', None)
        ename = self.get_body_argument('ename', None)
        sort = int(self.get_body_argument('sort', 1))
        active = 1 if self.get_body_argument('active', None) else 0

        if ca_id != '0':
            category_attribute = CategoryAttribute.get(id=ca_id)
        else:
            category_attribute = CategoryAttribute()
            category_attribute.category = category
        if active:
            category_attribute.name = name
            category_attribute.ename = ename
            category_attribute.sort = sort
            category_attribute.active = active
            category_attribute.save()
        else:
            category_attribute.active = active
            category_attribute.save()

        self.redirect('/admin/category_attribute/%s'%category)


@route(r'/admin/attribute_item_edit/(\d+)', name='admin_attribute_item_edit')  # 添加/修改分类规格的参数
class CategoryAttributeAddHandler(AdminBaseHandler):
    def get(self, cai_id):
        cid = self.get_argument('cid', None)
        ca_id = self.get_argument('ca_id', None)
        status = self.get_argument('status', None)
        if status == '0' and cai_id != '0':
            CategoryAttributeItems.delete().where(CategoryAttributeItems.id == cai_id).execute()
            self.redirect('/admin/category_attribute/%s'%cid)
            return
        elif cai_id == '0':
            attribute_item = None
        else:
            attribute_item = CategoryAttributeItems.get(id=cai_id)

        self.render('admin/product/category_attribute_item_edit.html', active='category', cid=cid, ca_id=ca_id,
                    attribute_item=attribute_item)

    def post(self, cai_id):
        category = self.get_body_argument('cid', None)
        category_attribute = self.get_body_argument('ca_id', None)
        name = self.get_body_argument('name', None)
        intro = self.get_body_argument('intro', None)
        sort = int(self.get_body_argument('sort', 1))

        if cai_id != '0':
            attribute_items = CategoryAttributeItems.get(id=cai_id)
        else:
            attribute_items = CategoryAttributeItems()
            attribute_items.category_attribute = int(category_attribute)
        attribute_items.name = name
        attribute_items.intro = intro
        attribute_items.sort = sort
        attribute_items.save()

        self.redirect('/admin/category_attribute/%s'%category)


@route(r'/admin/brand', name='admin_brand')  # 品牌管理
class BrandHandler(AdminBaseHandler):
    def get(self):
        page = int(self.get_argument("page", '1'))
        pagesize = setting.ADMIN_PAGESIZE

        brands = Brand.select()
        total = brands.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        bs = brands.paginate(page, pagesize)

        self.render('admin/product/brand.html', bs=bs, total=total, page=page, pagesize=pagesize,totalpage=totalpage, active='brand')


@route(r'/admin/edit_brand/(\d+)', name='admin_edit_brand')  # 编辑品牌
class EditBrandHandler(AdminBaseHandler):
    def get(self, id):
        id = int(id)
        brand_category = None
        if id != 0:
            try:
                brand_category = BrandCategory.get(brand = id)
            except:
                self.redirect("/admin/brand")
                return
        self.render('admin/product/brand_edit.html', brand_category=brand_category, active='brand')

    def post(self, brand_id):
        id = int(brand_id)
        name = self.get_argument("name", None)
        engname = self.get_argument("engname", None)
        pinyin = self.get_argument("pinyin", None)
        intro = self.get_argument("intro", None)
        sort = int(self.get_argument("sort", 1))
        hot = self.get_argument("hot", None)
        active = self.get_argument("active", None)

        try:
            if id == 0:
                ad = Brand()
            else:
                ad = Brand.get(id=id)
            if self.request.files:
                datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前时间作为图片名称
                filename = str(datetime) + ".jpg"
                file_path = setting.admin_file_path + 'brand'
                with open(file_path + filename, "wb") as f:
                    f.write(self.request.files["file"][0]["body"])
                ad.logo = file_path + filename
            ad.name = name
            ad.engname = engname
            ad.pinyin = pinyin
            ad.intro = intro
            ad.sort = sort
            ad.active = 1 if active else 0
            ad.hot = 1 if hot else 0
            ad.save()
        except Exception, e:
            logging.info('Error: %s'%e.message)
        self.redirect("/admin/brand")


@route(r'/admin/delete_brand/(\d+)', name='admin_delete_brand')  # 删除品牌
class DeleteBrandHandler(AdminBaseHandler):
    def get(self, id):
        p = Brand.get(id=id)
        p.active = 0
        p.save()
        self.redirect("/admin/brand")


@route(r'/admin/category_brand', name='admin_category_brand')  # 分类&品牌关联
class CategoryBrandHandler(AdminBaseHandler):
    def get(self):
        brand_categories = BrandCategory.select().order_by(BrandCategory.category.asc())
        categories = Category.select()
        brands = Brand.select()
        self.render('admin/product/category_brand.html',active='c_b', brand_categories=brand_categories,
                    categories=categories, brands=brands)

    def post(self):
        category = self.get_body_argument('category', None)
        brand = self.get_body_argument('brand', None)
        if category and brand:
            category = int(category)
            brand = int(brand)
            bc = BrandCategory.select().where((BrandCategory.category == category) & (BrandCategory.brand == brand))
            if bc.count() > 0:
                self.flash('已经存在')
            else:
                BrandCategory.create(category=category, brand=brand)
                self.flash('添加成功')
        self.redirect('/admin/category_brand')


@route(r'/admin/category_brand_del', name='admin_category_brand_delete')  # 删除分类&品牌关联
class CategoryBrandDelHandler(AdminBaseHandler):
    def get(self):
        bc_id = self.get_argument('bc', None)
        try:
            BrandCategory.delete().where(BrandCategory.id == bc_id).execute()
            self.flash('删除成功')
        except Exception, e:
            self.flash('删除失败：%s'% e.message)
        self.redirect('/admin/category_brand')


@route(r'/admin/product/(\d+)', name='admin_product')  # 商品
class ProductHandler(AdminBaseHandler):
    def get(self, is_score):
        page = int(self.get_argument("page", '1'))
        category = self.get_argument('category', None)
        keyword = self.get_argument("keyword", None)
        active = int(self.get_argument("status", 1))
        pagesize = setting.ADMIN_PAGESIZE
        is_score = int(is_score)
        ft = (Product.active == active) & (Product.is_score == is_score)
        if keyword:
            keyw = '%' + keyword + '%'
            ft = ft & (Product.name % keyw)
        if category:
            ft = ft & (Product.category == category)
        products = Product.select().where(ft)
        total = products.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        products = products.order_by(Product.created.desc()).paginate(page, pagesize).aggregate_rows()
        categories = Category.select()
        product_type = 'product_s' if is_score else 'product_n'

        self.render('admin/product/product.html', active=product_type, products=products, total=total, page=page,
                    c_id=category, pagesize=pagesize, totalpage=totalpage, keyword=keyword, status=active,
                    categories=categories, is_score=is_score)


@route(r'/admin/edit_product/(\d+)', name='admin_edit_product')  # 修改商品
class EditProductHandler(AdminBaseHandler):
    def get(self, pid):
        pid = int(pid)
        product_attribute_values = {}
        if pid > 0:
            p = Product.get(id=pid)
            for pa in p.attributes:
                product_attribute_values[pa.attribute.id] = pa.attribute_item.id
        else:
            p = None

        category_attributes = []
        for category in Category.select():
            attributes = []
            for attribute in category.attributes:
                attributes.append({
                    'id': attribute.id,
                    'name': attribute.name,
                    'values': [item.name for item in attribute.items]
                })
            category_attributes.append({
                'id': category.id,
                'name': category.name,
                'attributes': attributes
            })
        brands = Brand.select()
        logging.info(product_attribute_values)
        product_type = 'product_s' if p and p.is_score else 'product_n'
        self.render('admin/product/product_edit.html', active=product_type, p=p, brands=brands, category_attributes=category_attributes,
                    pa_values=product_attribute_values)

    def post(self, pid):
        name = self.get_body_argument('name', None)
        resume = self.get_body_argument('resume', None)
        brand = self.get_body_argument('brand', None)
        category = self.get_body_argument('category', None)
        unit = self.get_body_argument('unit', None)
        is_score = self.get_body_argument('is_score', 0)
        category_attributes = simplejson.loads(self.get_body_argument('category_attributes', None))
        hd_pic = self.get_body_argument('hd_pic', None)

        if pid == '0':
            product = Product()
            product.created = int(time.time())
            product.active = 1
        else:
            product = Product.get(id=pid)
        product.name = name
        product.brand = brand
        product.category = category
        product.resume = resume
        product.unit = unit
        product.intro = 'intro'
        product.is_score = is_score
        product.save()
        for category in category_attributes:
            if pid == '0':
                product_attr = ProductAttributeValue()
                product_attr.product = product.id
                product_attr.attribute = category['attribute_id']
            else:
                product_attrs = ProductAttributeValue.select().where((ProductAttributeValue.product == pid) &
                                (ProductAttributeValue.attribute == category['attribute_id']))
                if product_attrs.count() > 0:
                    product_attr = product_attrs[0]
                else:
                    product_attr = ProductAttributeValue()
                    product_attr.product = product.id
                    product_attr.attribute = category['attribute_id']
            product_attr.attribute_item = category['attribute_value_id']
            product_attr.value = CategoryAttributeItems.get(id=category['attribute_value_id']).name
            product_attr.save()
        self.redirect('/admin/edit_product/%s'%pid)


# --------------------------------------------------------App管理-------------------------------------------------------
@route(r'/admin/block', name='admin_block')
class BlockHandler(AdminBaseHandler):
    def get(self):
        blocks = Block.select()
        self.render('admin/App/block.html', blocks=blocks, active='block')


@route(r'/admin/edit_block/(\d+)', name='admin_edit_block')
class EditBlockHandler(AdminBaseHandler):
    def get(self, aid):
        if aid == '0':
            block = Block()
        else:
            try:
                block = Block.get(id=int(aid))
            except:
                self.flash("此广告不存在")
                self.redirect("/admin/block")
                return

        self.render('admin/App/block_edit.html', block=block, active='block')

    def post(self, aid):
        aid = int(aid)
        name = self.get_argument('name', None)
        tag = self.get_body_argument('tag', None)
        file = self.get_body_argument('file', None)
        remark = self.get_argument("remark", None)
        category = self.get_argument("ad_location_category", None)
        try:
            if aid == 0:
                block = Block()
                msg = u"广告位添加成功"
            else:
                block = Block.get(id=aid)
                msg = u"广告位修改成功"
            if self.request.files:
                datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前时间作为图片名称
                filename = str(datetime) + ".jpg"
                file_path = setting.admin_file_path+'/App'
                if not os.path.isdir(file_path):
                    os.makedirs(file_path)
                with open(file_path + filename, "wb") as f:
                    f.write(self.request.files["file"][0]["body"])
                block.imagename = '/upload/block/'+filename
            block.name = name
            block.remark = remark
            block.category = category
            block.save()
            self.flash(msg)
            self.redirect("/admin/block")
            return
        except Exception, ex:
            self.flash(str(ex))
            self.redirect("/admin/block")


@route(r'/admin/advertisement', name='admin_ad')
class AdvertisementHandler(AdminBaseHandler):
    def get(self):
        ads = BlockItem.select().order_by(BlockItem.block)
        items = Area.select().where(Area.pid >> None).order_by(Area.spell, Area.sort)
        self.render('admin/App/ads.html', ads=ads, active='ads', items=items)


@route(r'/admin/edit_ad/(\d+)', name='admin_ad_edit')
class EditAdHandler(AdminBaseHandler):
    executor = ThreadPoolExecutor(20)
    @asynchronous
    @coroutine
    def get(self, aid):
        a = yield self.show_ad(aid)

    @run_on_executor
    def show_ad(self, aid):
        items = Area.select().where(Area.pid >> None)
        aid = int(aid)
        try:
            ad = BlockItem.get(id=aid)
        except:
            self.flash("此广告不存在")
            self.redirect("/admin/advertisement")
            return
        blocks = Block.select()
        self.render('admin/App/ad_e.html', items=items, ad=ad, active='ads', blocks=blocks)

    def post(self, aid):
        aid = int(aid)
        url = self.get_argument("url", None)
        imgalt = self.get_argument("imgalt", None)
        sort = int(self.get_argument("sort", 1))
        type = int(self.get_argument("sel_type", 0))
        province_code = self.get_argument("province_code", None)
        city_code = self.get_argument("city_code", None)
        remark = self.get_argument("remark", None)
        adsize = self.get_argument("adsize", None)
        status = int(self.get_argument("status", 0))
        try:
            ad = Ad.get(id=aid)
        except:
            self.flash("此广告不存在")
            self.redirect("/admin/ads")
            return

        ad.url = url
        ad.imgalt = imgalt
        ad.sort = sort
        ad.atype = type
        ad.remark = remark
        ad.flag = status
        ad.adsize = adsize
        try:
            if province_code != '' and city_code != '':
                ad.city = city_code
                ad.city_code = ad.city.code
            if self.request.files:
                datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前时间作为图片名称
                filename = str(datetime) + ".jpg"
                with open('upload/ad/' + filename, "wb") as f:
                    f.write(self.request.files["file"][0]["body"])
                imgurl = postRequest(open(filename, 'rb'))
                ad.picurl = imgurl if not imgurl else ''
            ad.validate()
            ad.save()
            self.flash(u"广告修改成功")
            self.redirect("/admin/ads")
            return
        except Exception, ex:
            self.flash(str(ex))
            self.redirect("/admin/editad/" + str(aid))

        self.render('admin/ad/editad.html', ad=ad, active='ads')


@route(r'/admin/hot_search', name='admin_hot_search')
class HotSearchHandler(AdminBaseHandler):
    def get(self):
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = self.settings['admin_pagesize']
        status = int(self.get_argument('status', -1))
        if status != -1:
            search = HotSearch.select().where(HotSearch.status == status)
        else:
            search = HotSearch.select().where(HotSearch.status != -1)
        total = search.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        s = search.order_by(HotSearch.quantity.desc()).paginate(page, pagesize)
        self.render('/admin/App/hot_search.html', search=s, active='hot_search', total=total, page=page,
                    pagesize=pagesize, totalpage=totalpage, status=status)


@route(r'/admin/search_change_status/(\d+)', name='admin_search_change_status')  # 更改搜索关键词状态
class SearchChangeStatusHandler(AdminBaseHandler):
    def get(self, tid):
        page = int(self.get_argument("page", '1'))
        status = int(self.get_argument('status', 0))
        s = int(self.get_argument('s', 0))
        hot = HotSearch.get(id=tid)
        hot.status = status
        hot.save()
        self.redirect('/admin/hot_search?status=' + str(s) + '&page=' + str(page))


# -------------------------------------------------------财务对账-------------------------------------------------------
@route(r'/admin/withdraw', name='admin_withdraw')  # 提现管理列表
class WithdrawHandler(AdminBaseHandler):
    def get(self):
        page = int(self.get_argument("page", '1'))
        pagesize = self.settings['admin_pagesize']
        key = self.get_argument("keyword", None)
        begindate = self.get_argument("begindate", '')
        enddate = self.get_argument("enddate", '')
        status = self.get_argument("status", '')

        ft = (Withdraw.id > 0)
        if begindate and enddate:
            begin = time.strptime(begindate, "%Y-%m-%d")
            end = time.strptime((enddate + " 23:59:59"), "%Y-%m-%d %H:%M:%S")
            ft = ft & (Withdraw.apply_time > time.mktime(begin)) & (Withdraw.apply_time < time.mktime(end))

        if status:
            ft = ft & (Withdraw.status == status)
        if key:
            keyword = '%' + key + '%'
            ft = ft & ((User.username % keyword) | ((User.mobile % keyword)))
            uq = Withdraw.select().join(User, on=(Withdraw.user == User.id)).where(ft)
        else:
            uq = Withdraw.select().where(ft)
        total = uq.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        lists = uq.order_by(Withdraw.apply_time.desc()).paginate(page, pagesize)
        self.render('/admin/finance/withdraw.html', lists=lists, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, active='withdraw', keyword=key, begindate=begindate, enddate=enddate,
                    status=status)

@route(r'/admin/export_insurance_success', name='admin_export_insurance_success')  # 导出出单明细
class ExportInsuranceSuccessHandler(AdminBaseHandler):
    def get(self):
        archive = self.get_argument("archive", '')
        page = int(self.get_argument("page", 1))
        status = int(self.get_argument("status", 0))
        keyword = self.get_argument("keyword", '')
        begin_date = self.get_argument("begin_date", '')
        end_date = self.get_argument("end_date", '')
        order_type = int(self.get_argument("order_type", 1))
        pagesize = setting.ADMIN_PAGESIZE

        ft = (InsuranceOrder.status >0)

        if begin_date and end_date:
            begin = time.strptime(begin_date, "%Y-%m-%d")
            end = time.strptime((end_date + " 23:59:59"), "%Y-%m-%d %H:%M:%S")
            ft &= (InsuranceOrder.ordered > time.mktime(begin)) & (InsuranceOrder.ordered < time.mktime(end))

        q = InsuranceOrder.select().join(Store).where(ft).order_by(InsuranceOrder.ordered.asc())
        total = q.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        orders = q.paginate(page, pagesize)
        if archive:
            active = 'insurancesuccess'
        else:
            active = 'insurancesuccess'
        self.render('admin/order/export_insurance_success.html', orders=orders, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, active=active, begin_date=begin_date, end_date=end_date,
                    archive=archive)

@route(r'/admin/export_trade_list', name='admin_export_trade_list')  # 导出出单明细
class ExportTradeListHandler(AdminBaseHandler):
    def get(self):
        archive = self.get_argument("archive", '')
        page = int(self.get_argument("page", 1))
        status = int(self.get_argument("status", 0))
        begin_date = self.get_argument("begin_date", '')
        end_date = self.get_argument("end_date", '')
        pagesize = setting.ADMIN_PAGESIZE
        payment = {1: u'支付宝', 2: u'微信', 3: u'银联', 4: u'余额',5: u'other'}
        orderft = (Order.status << [1, 2, 3, 4])
        insuranceft = (InsuranceOrder.status << [1, 2, 3, 4])
        if begin_date and end_date:
            begin = time.strptime(begin_date, "%Y-%m-%d")
            end = time.strptime((end_date + " 23:59:59"), "%Y-%m-%d %H:%M:%S")
            orderft &= (Order.ordered > time.mktime(begin)) & (Order.ordered < time.mktime(end))
            insuranceft &= (InsuranceOrder.ordered > time.mktime(begin)) & (InsuranceOrder.ordered < time.mktime(end))

        orders = Order.select().join(Store).where(orderft).order_by(Order.ordered.asc())
        insuranceorders = InsuranceOrder.select().join(Store).where(insuranceft).order_by(InsuranceOrder.ordered.asc())
        total = orders.count() + insuranceorders.count()
        data = []
        for item in orders:
            s = {}
            s['id'] = str(item.id)
            s['ordered'] = u'%s' % time.strftime('%Y-%m-%d', time.localtime(item.ordered))
            s['ordernum'] = item.ordernum
            s['payment'] = payment[item.payment] if item.payment in payment.keys() else 'other'
            s['moneyitem'] = u'润滑油'
            s['useraddress'] = item.address.address
            s['totalprice'] = str(item.total_price)
            s['insurance'] = item.buyer_store.name
            s['user'] = item.user.truename
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
            s['user'] = item.user.truename
            s['incommission'] = None
            s['outprice'] = None
            s['outcommission'] = None
            s['summary'] = item.local_summary
            data.append(s)

        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        orders = data[10*(page-1):10*page-1]
        if archive:
            active = 'tradelist'
        else:
            active = 'tradelist'
        self.render('admin/order/export_trade_list.html', orders=orders, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, status=status, active=active, begin_date=begin_date, end_date=end_date,
                    archive=archive)

    @route(r'/admin/store_liquidity/(\d+)', name='admin_store_liquidit')  #
    class StoreLiquiditHandler(AdminBaseHandler):
        def get(self, sid):
            page = int(self.get_argument("page", '1'))
            pagesize = self.settings['admin_pagesize']
            keyword = self.get_argument("keyword", '')
            begindate = self.get_argument("begindate", '')
            enddate = self.get_argument("enddate", '')
            type = self.get_argument("type", '1')
            if type == '1':
                ft = (ScoreRecord.status == 1) & (ScoreRecord.store == sid)
                if begindate and enddate:
                    begin = time.strptime(begindate, "%Y-%m-%d")
                    end = time.strptime((enddate + " 23:59:59"), "%Y-%m-%d %H:%M:%S")
                    ft = ft & (ScoreRecord.created > time.mktime(begin)) & (ScoreRecord.created < time.mktime(end))
                if keyword:
                    key = '%' + keyword + '%'
                    ft = ft & (ScoreRecord.ordernum % key)
                srs = ScoreRecord.select().where(ft)
            else:
                ft = (MoneyRecord.status == 1) & (MoneyRecord.store == sid)
                if begindate and enddate:
                    begin = time.strptime(begindate, "%Y-%m-%d")
                    end = time.strptime((enddate + " 23:59:59"), "%Y-%m-%d %H:%M:%S")
                    ft = ft & (MoneyRecord.apply_time > time.mktime(begin)) & (
                    MoneyRecord.apply_time < time.mktime(end))
                if keyword:
                    key = '%' + keyword + '%'
                    ft = ft & (MoneyRecord.in_num % key)
                srs = MoneyRecord.select().where(ft)
            total = srs.count()
            if total % pagesize > 0:
                totalpage = total / pagesize + 1
            else:
                totalpage = total / pagesize
            if type == '1':
                lists = srs.order_by(ScoreRecord.created.desc()).paginate(page, pagesize)
            else:
                lists = srs.order_by(MoneyRecord.apply_time.desc()).paginate(page, pagesize)
            self.render('/admin/finance/liquidity.html', lists=lists, total=total, page=page, pagesize=pagesize,
                        totalpage=totalpage, active='withdraw', keyword=keyword, begindate=begindate, enddate=enddate,
                        sid=sid, type=type)


# --------------------------------------------------------订单管理------------------------------------------------------
@route(r'/admin/product_orders', name='admin_product_orders')  # 普通商品订单
class ProductOrdersHandler(AdminBaseHandler):
    def get(self):
        archive = self.get_argument("archive", '')
        page = int(self.get_argument("page", 1))
        status = int(self.get_argument("status", 0))
        keyword = self.get_argument("keyword", '')
        begin_date = self.get_argument("begin_date", '')
        end_date = self.get_argument("end_date", '')
        order_type = int(self.get_argument("order_type", 1))
        pagesize = setting.ADMIN_PAGESIZE
        if status == -2:
            ft = (Order.status > -2)
        else:
            ft = (Order.status == status)
        if order_type:
            ft &= (Order.order_type == order_type)
        if keyword:
            keyword_ = '%' + keyword + '%'
            ft &= ((Order.ordernum % keyword_) | (Store.name % keyword_) | (Store.mobile % keyword_))
        if begin_date and end_date:
            begin = time.strptime(begin_date, "%Y-%m-%d")
            end = time.strptime((end_date + " 23:59:59"), "%Y-%m-%d %H:%M:%S")
            ft &= (Order.ordered > time.mktime(begin)) & (Order.ordered < time.mktime(end))

        q = Order.select().join(Store).where(ft).order_by(Order.ordered.desc())
        total = q.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        orders = q.paginate(page, pagesize)
        if archive:
            active = 'p_order_a'
        else:
            active = 'p_order'
        self.render('admin/order/product_orders.html', orders=orders, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, status=status, active=active, begin_date=begin_date, end_date=end_date,
                    keyword=keyword, order_type=order_type, archive=archive)


@route(r'/admin/product_order/(\d+)', name='admin_product_order_detail')  # 订单详情
class ProductOrderDetailHandler(AdminBaseHandler):
    def get(self, oid):
        o = Order.get(id=oid)
        archive = self.get_argument("archive", '')
        num = '%' + o.ordernum + '%'
        stores=Store.select().where(Store.store_type==0)
        if archive:
            active = 'p_order_a'
        else:
            active = 'p_order'

        self.render('admin/order/product_order_detail.html', o=o, active=active)


@route(r'/admin/insurance_orders', name='admin_insurance_orders')  # 保险订单管理
class InsuranceOrderHandler(AdminBaseHandler):
    def get(self):
        archive = self.get_argument("archive", '')
        page = self.get_argument("page", 1)
        page = 1 if page else int(page)
        status = self.get_argument("status", '')
        status = int(status) if status else -2
        keyword = self.get_argument("keyword", '')
        begin_date = self.get_argument("begin_date", '')
        end_date = self.get_argument("end_date", '')
        province = self.get_argument('province_code', '')
        city = self.get_argument('city_code', '')
        district = self.get_argument("district_code", '')
        pagesize = self.settings['admin_pagesize']
        default_city = city
        default_province = province
        # 0待确认 1待付款 2付款完成 3已办理 4已邮寄 -1已删除(取消)

        if status != -2:
            ft = (InsuranceOrder.status == status)
        else:
            ft = (InsuranceOrder.status > -2)
        if keyword:
            keyw = '%' + keyword + '%'
            ft &= ((InsuranceOrder.ordernum % keyw)|(InsuranceOrder.mobile % keyw))
        if begin_date and end_date:
            begin = time.strptime(begin_date, "%Y-%m-%d")
            end = time.strptime((end_date + " 23:59:59"), "%Y-%m-%d %H:%M:%S")
            ft = ft & (InsuranceOrder.paytime > time.mktime(begin)) & (InsuranceOrder.paytime < time.mktime(end))

        if district and district != '0':
            ft &= (Store.area_code == district)
        elif city and city != '0':
            search_area = city + '%'
            ft &= (Store.area_code % search_area)
        elif province and province != '0':
            search_area = province + '%'
            ft &= (Store.area_code % search_area)
        admin_user = self.get_admin_user()
        if admin_user.area_code:
            area_code = admin_user.area_code + '%'
            ft &= (Store.area_code % area_code)

        q = InsuranceOrder.select().join(Store).where(ft).order_by(InsuranceOrder.ordered.desc())
        total = q.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        orders = q.paginate(page, pagesize)
        items = Area.select().where(Area.pid >> None)
        if archive:
            active = 'i_order_a'
        else:
            active = 'i_order'

        self.render('admin/order/insurance_orders.html', orders=orders, total=total, page=page, pagesize=pagesize,
                    totalpage=totalpage, status=status, active=active,begin_date=begin_date,end_date=end_date,
                    keyword=keyword, items=items, default_province=default_province, default_city=default_city,
                    default_status=status, Area=Area)


@route(r'/admin/insurance_order/(\d+)', name='admin_insurance_order_detail')  # 保险订单详情
class InsuranceOrderDetailHandler(AdminBaseHandler):
    def get(self, oid):
        archive = self.get_argument("archive", '')
        o = InsuranceOrder.get(id=oid)
        poid = (int(oid) * 73 + 997)
        poid2 = (int(oid) * 91 + 97)
        i_items = InsuranceItem.select().order_by(InsuranceItem.sort)
        insurances = Insurance.select()

        programs = []
        insurance_order_prices = InsuranceOrderPrice.select().where(InsuranceOrderPrice.insurance_order_id == oid)
        for program in insurance_order_prices:
            i_item_list = []
            for i_item in i_items:
                if program.__dict__['_data'][i_item.eName]:
                    i_item_list.append({
                        'name': i_item.name,
                        'e_name': i_item.eName,
                        'style_id': i_item.style_id,
                        'value': program.__dict__['_data'][i_item.eName],
                        'price': program.__dict__['_data'][i_item.eName+'Price'] if program.__dict__['_data'][i_item.eName+'Price'] else 0
                    })
            rates = InsuranceScoreExchange.get_score_policy(o.store.area_code, program.insurance)
            lubepolicy = LubePolicy.select().where(LubePolicy.area_code == o.store.area_code)
            programs.append({
                'pid': program.id,
                'insurance': program.insurance,
                'gift_policy': program.gift_policy,
                'score': program.score,
                'total_price': program.total_price,
                'force_price': program.force_price,
                'business_price': program.business_price,
                'vehicle_tax_price': program.vehicle_tax_price,
                'program': i_item_list,
                'msg': program.sms_content if program.sms_content else '',
                'rates': rates
            })
        if archive:
            active = 'i_order_a'
        else:
            active = 'i_order'

        self.render('admin/order/insurance_order_detail.html', active=active, o=o, insurances=insurances,
                    poid=poid, poid2=poid2, programs=programs)

    def post(self, oid):
        '''
        programs = {
            'program_id': 2,
            'i_id': 1,
            'i_items': {'forceI': 1000, 'driverI':500},
            'gift_policy': 1,
            'score': 0,
            'force_price': 5005,
            'business_price':6000,
            'vehicle_tax_price': 500,
            'total_price': 110505,
            'psummary': 短信,
            'is_send_msg': 0
        }
        '''
        programs = simplejson.loads(self.get_body_argument('programs'))
        insurance_order = InsuranceOrder.get(id=oid)

        iop = InsuranceOrderPrice.get(id=programs['program_id'])
        if iop.status == 2 or iop.status == -1:  # 不可修改的报价和已关闭的报价pass
            self.flash('此条报价不可再修改')
            self.redirect('admin/insurance_order/%s' % oid)
            return
        iop.created = int(time.time())
        iop.admin_user = self.get_admin_user()
        iop.gift_policy = programs['gift_policy']
        iop.sms_content = programs['sms_content']
        if programs['gift_policy'] == 2:
            iop.score = int(programs['score'])
        else:
            iop.score = 0
        if iop.status == 0:  # 仅未报价的可以修改以下内容
            iop.total_price = programs['total_price']
            iop.force_price = programs['force_price']
            iop.business_price = programs['business_price']
            iop.vehicle_tax_price = programs['vehicle_tax_price']
            for key in programs['i_items']:
                iop.__dict__['_data'][key+'Price'] = programs['i_items'][key]
        iop.save()
        self.flash("保存成功")

        if programs['is_send_msg'] == '1':
            sms = {'mobile': insurance_order.store.mobile, 'body': [insurance_order.ordernum, iop.insurance.name,
                    str(iop.total_price), programs['sms_content']], 'signtype': '1', 'isyzm': 'changePrice'}
            # create_msg(simplejson.dumps(sms), 'sms')  #变更价格

        self.redirect('admin/insurance_order/%s'%oid)


@route(r'/admin/new_program/(\d+)', name='admin_new_program')  # 保险订单详情
class NewProgramHandler(AdminBaseHandler):
    def get(self, oid):
        i_items = InsuranceItem.select().order_by(InsuranceItem.sort)
        insurances = Insurance.select().order_by(Insurance.sort)
        insurance_list = []
        for insurance in insurances:
            insurance_list.append({
                'id': insurance.id,
                'name': insurance.name
            })
        i_item_list = []
        for i_item in i_items:
            i_item_list.append({
                'eName': i_item.eName,
                'name': i_item.name,
                'style': i_item.style,
                'style_id': i_item.style_id,
                'insurance_prices': [i_price.coverage for i_price in i_item.insurance_prices]
            })

        self.render('admin/order/insurance_order_new_program.html', oid=oid, i_item_list=i_item_list,
                    insurance_list=insurance_list)

    def post(self, oid):
        insurance = self.get_body_argument('insurance', None)
        gift_policy = self.get_body_argument('gift_policy', None)
        datas = {}
        for data in self.request.body.split('&'):
            key, value = data.split('=', 1)
            if value:
                datas[key] = value
        iop = InsuranceOrderPrice()
        iop.insurance_order_id = oid
        iop.insurance = insurance
        iop.gift_policy = gift_policy if gift_policy else 1
        iop.admin_user = self.get_admin_user()
        iop.created = time.time()
        i_items = InsuranceItem.select().order_by(InsuranceItem.sort)
        for i_item in i_items:
            if i_item.eName in datas:
                if i_item.eName+'_p' in datas:
                    iop.__dict__['_data'][i_item.eName] = self.get_body_argument(i_item.eName+'_p', None)
                else:
                    iop.__dict__['_data'][i_item.eName] = '1'
        iop.save()
        
        self.write(u'新建成功')
        # self.redirect('/admin/insurance_order/%s'%oid)


@route(r'/admin/delinsurance/(\d+)', name='admin_delete_insurance')  # 保险订单 删除或完成
class InsuranceOrderDelHandler(AdminBaseHandler):
    def get(self, oid):
        status = self.get_argument('status', '')
        status = int(status) if status else 1
        page = self.get_argument('page', 1)
        try:
            io = InsuranceOrder.get(id=oid)
            if status < 2:
                io.status = -1
                io.save()
            elif status == 2:  # 赠送积分，创建积分记录
                if io.status == 2:
                    # ReScore().rewardScore_insurance(io.user.id, io.LubeOrScore, io.scoreNum, io.ordernum)
                    iop = io.current_order_price
                    if iop.gift_policy == 2:    # 返现
                        now = int(time.time())
                        money = iop.cash
                        admin_user = self.get_admin_user()
                        MoneyRecord.create(user=io.user, store=io.store, process_type=1, process_message=u'保险',
                                           process_log=u'卖保险返现所得', money=money, status=1, apply_time=now,
                                           processing_time=now, processing_by=admin_user)
                    else:    # 返油
                        self.flash(u'返油')
                    io.status = 3
                    io.save()
                else:
                    self.flash(u'该订单不能完成状态为:%s'%(io.status))
        except Exception, e:
            logging.info('Error: /admin/delinsurance/%s, %s'%(oid, e.message))
        self.redirect('/admin/insurances/processing?status=%s&page=%s'%(status,page))


# --------------------------------------------------------保险业务------------------------------------------------------
@route(r'/admin/insurance', name='admin_insurance_list')  # 保险公司列表
class InsuranceList(AdminBaseHandler):
    def get(self):
        iid = int(self.get_argument('iid', 0))
        insurances = Insurance.select().where(Insurance.active == 1)
        ft = InsuranceArea.active == 1
        if iid > 0:
            ft &= InsuranceArea.insurance == iid
        areas = InsuranceArea.select().where(ft)
        self.render("admin/insurance/index.html", insurances=insurances, active='insurance',
                    areas=areas, Area=Area, iid=iid)


@route(r'/admin/insurance_area', name='admin_insurance_area')  # 保险发布地域
class InsuranceAreaHandler(AdminBaseHandler):
    def get(self):
        code = self.get_argument('code', '')
        insurances = InsuranceArea.select().where((InsuranceArea.active == 1) &(InsuranceArea.area_code == code))
        self.render("admin/insurance/area.html", insurances=insurances, active='insurance_area')


@route(r'/admin/insurance/score', name='admin_insurance_score')  # 保险返积分策略
class InsuranceScore(AdminBaseHandler):
    def get(self):
        iid = int(self.get_argument('iid', 0))
        area_code = self.get_argument('area_code', '0')
        sid = self.get_argument('sid', '')
        if sid:
            items = SSILubePolicy.select().where((SSILubePolicy.store == sid) & (SSILubePolicy.insurance == iid))
        else:
            '''
    business_exchange_rate = FloatField(default=0.0)  # 兑换率（商业险），仅商业险
    business_exchange_rate2 = FloatField(default=0.0)  # 兑换率（商业险），商业险+交强险
    business_tax_rate = FloatField(default=0.0)  # 商业险税率

    force_exchange_rate = FloatField(default=0.0)  # 交强险兑换率, 仅交强险
    force_exchange_rate2 = FloatField(default=0.0)  # 交强险兑换率, 商业险+交强险
    force_tax_rate = FloatField(default=0.0)  # 交强险税率

    ali_rate = FloatField(default=0.0)  # 银联支付宝微信转账 手续费率
    profit_rate = FloatField(default=0.0)  # 利润率（车装甲）
    base_money = FloatField(default=0.0)  # 多少元起兑

            '''
            items = InsuranceScoreExchange.select(InsuranceScoreExchange.business_exchange_rate.alias('ber'),
                                                  InsuranceScoreExchange.business_exchange_rate2.alias('ber2'),
                                                  InsuranceScoreExchange.business_tax_rate.alias()).\
                where((InsuranceScoreExchange.insurance == iid) & (InsuranceScoreExchange.area_code == area_code)).dicts()
        if items.count() > 0:
            item = items[0]
        else:
            item = None
        self.render("admin/insurance/score.html", item=item, active='insurance', iid=iid, area_code = area_code)

    def post(self):
        exid = int(self.get_body_argument('exid', '0'))
        base_money = float(self.get_body_argument('base_money', '0'))
        business_exchange_rate = float(self.get_body_argument('business_exchange_rate', '0'))
        business_exchange_rate2 = float(self.get_body_argument('business_exchange_rate2', '0'))
        business_tax_rate = float(self.get_body_argument('business_tax_rate', '0'))

        force_exchange_rate = float(self.get_body_argument('force_exchange_rate', '0'))
        force_exchange_rate2 = float(self.get_body_argument('force_exchange_rate2', '0'))
        force_tax_rate = float(self.get_body_argument('force_tax_rate', '0'))

        ali_rate = float(self.get_body_argument('ali_rate', '0'))
        profit_rate = float(self.get_body_argument('profit_rate', '0'))
        area_code = self.get_body_argument('area_code', '0')
        iid = int(self.get_argument('iid', 0))

        if exid > 0:
            item = InsuranceScoreExchange.get(id=exid)
        else:
            item = InsuranceScoreExchange()
            item.area_code = area_code
            item.insurance = iid
            item.created = int(time.time())
        item.base_money = base_money
        item.business_exchange_rate = business_exchange_rate
        item.business_exchange_rate2 = business_exchange_rate2
        item.business_tax_rate = business_tax_rate
        item.force_exchange_rate = force_exchange_rate
        item.force_exchange_rate2 = force_exchange_rate2
        item.force_tax_rate = force_tax_rate
        item.ali_rate = ali_rate
        item.profit_rate = profit_rate
        item.save()
        self.flash('保存成功')
        items = InsuranceScoreExchange.select().where((InsuranceScoreExchange.insurance == iid)
                                                      & (InsuranceScoreExchange.area_code == area_code))
        if items.count() > 0:
            item = items[0]
        else:
            item = None
        self.render("admin/insurance/score.html", item=item, active='insurance')


@route(r'/admin/insurance/lube', name='admin_insurance_lube')  # 保险返油策略
class InsuranceLube(AdminBaseHandler):
    def get(self):
        iid = int(self.get_argument('iid', 0))
        area_code = self.get_argument('area_code', '0')
        items = LubePolicy.select().where((LubePolicy.insurance == iid) & (LubePolicy.area_code == area_code))
        if items.count() > 0:
            item = items[0]
        else:
            item = None
        self.render("admin/insurance/lube.html", item=item, iid=iid, area_code = area_code)

    def post(self):
        exid = int(self.get_body_argument('exid', '0'))
        json = self.get_body_argument('json', '[]')
        area_code = self.get_body_argument('area_code', '0')
        iid = int(self.get_argument('iid', 0))

        if exid > 0:
            item = LubePolicy.get(id=exid)
        else:
            item = LubePolicy()
            item.area_code = area_code
            item.insurance = iid
        item.policy = json
        item.save()
        self.flash('保存成功')
        items = LubePolicy.select().where((LubePolicy.insurance == iid)
                                          & (LubePolicy.area_code == area_code))
        if items.count() > 0:
            item = items[0]
        else:
            item = None
        self.render("admin/insurance/lube.html", item=item, iid=iid, area_code=area_code)


# --------------------------------------------------------SK润滑油------------------------------------------------------
@route(r'/admin/sk', name='admin_sk')  # 后台SK产品维护
class SKHandler(AdminBaseHandler):
    def get(self):
        category = int(self.get_argument("category", '0') if len(self.get_argument("category", '0')) > 0 else '0')
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = self.settings['admin_pagesize']
        ft = (CarSK.active == 1)
        if category > 0:
            ft &= (CarSK.category == category)

        s = CarSK.select().where(ft)
        total = s.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize if (total / pagesize) > 0 else 1
        products = s.paginate(page, pagesize)
        self.render("admin/sk/product.html", products=products, total=total, totalpage=totalpage,
                    page=page, pagesize=pagesize, category=category, active='sk_product')


@route(r'/admin/sk_car', name='admin_sk_car')  # 后台SK产品与车型映射
class SKCarHandler(AdminBaseHandler):
    def get(self):
        type = int(self.get_argument("type", '1') if len(self.get_argument("type", '1')) > 0 else '1')
        page = int(self.get_argument("page", '1') if len(self.get_argument("page", '1')) > 0 else '1')
        pagesize = 10
        engine_1 = CarItem.select().where((CarItem.active == 1) & (CarItem.car_sk_engine_1 >> None)).count()
        engine_2 = CarItem.select().where((CarItem.active == 1) & (CarItem.car_sk_engine_2 >> None)).count()
        gearbox_1 = CarItem.select().where((CarItem.active == 1) & (CarItem.car_sk_gearbox_1 >> None)).count()
        gearbox_2 = CarItem.select().where((CarItem.active == 1) & (CarItem.car_sk_gearbox_2 >> None)).count()

        ft = ((CarBrand.active == 1) & (CarItem.active == 1) & (Car.active == 1))
        ft2 = ((CarItem.active == 1) & (Car.active == 1))
        if type == 1:
            ft &= (CarItem.car_sk_engine_1 >> None)
            ft2 &= (CarItem.car_sk_engine_1 >> None)
        elif type == 2:
            ft &= (CarItem.car_sk_engine_2 >> None)
            ft2 &= (CarItem.car_sk_engine_2 >> None)
        elif type == 3:
            ft &= (CarItem.car_sk_gearbox_1 >> None)
            ft2 &= (CarItem.car_sk_gearbox_1 >> None)
        elif type == 4:
            ft &= (CarItem.car_sk_gearbox_2 >> None)
            ft2 &= (CarItem.car_sk_gearbox_2 >> None)

        s = CarBrand.select().join(Car).join(CarItem).where(ft).group_by(CarBrand)
        total = s.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize if (total / pagesize) > 0 else 1
        brands = s.paginate(page, pagesize)
        bs = []
        for brand in brands:
            b = {}
            b['brand_name'] = brand.brand_name
            b['id'] = brand.id
            b['logo'] = brand.logo
            ft3 = ft2 & (Car.brand == brand)
            b['items'] = Car.select().join(CarItem).where(ft3).group_by(Car)
            bs.append(b)

        self.render("admin/sk/car_map.html", brands=bs, type=type, active='sk_car', engine_1=engine_1,
                    engine_2=engine_2, gearbox_1=gearbox_1, gearbox_2=gearbox_2, total=total,
                    totalpage=totalpage, page=page, pagesize=pagesize)


# -----------------------------------------------------------系统设置---------------------------------------------------
@route(r'/admin/upload_pic', name='admin_upload_pic')    # 图片上传
class UploadPicHandler(AdminBaseHandler):
    def get(self):
        data = self.get_argument('data', '')
        self.render('admin/sysSetting/picture_edit.html', active='pic', data=data)


@route(r'/admin/send_msg', name='admin_sms_send')  # 短信群发
class SendMsgHandler(AdminBaseHandler):
    def get(self):
        items = Area.select().where(Area.pid >> None)
        self.render('admin/sysSetting/send_msg.html', active='msg', items=items)

    def post(self):
        content_log = {}
        number = self.get_body_argument('number', '')
        content = self.get_body_argument('content', '')
        title = self.get_body_argument('title', '')
        is_users = self.get_body_argument('is_users', '')
        user_type = int(self.get_body_argument('user_type',-1))
        sms_type = int(self.get_body_argument('sms_type',-1))
        province = self.get_body_argument('province_code', '')
        city = self.get_body_argument('city_code', '')
        district = self.get_body_argument('district_code', '')
        get_mobile = self.get_body_argument('get_mobile', '')

        if district:
            area_code = district + '%'
        elif city:
            area_code = city + '%'
        elif province:
            area_code = province + '%'
        else:
            area_code = None
        if get_mobile and area_code:
            mobiles = ''
            stores = Store.select(Store.mobile).where(Store.area_code % area_code)
            for store in stores:
                mobiles += store.mobile + ','
            with open('mobiles.txt', 'w') as f:
                f.write(mobiles.strip(','))
            self.redirect('/admin/send_msg')
            return
        # 极光推送
        if sms_type == 0:
            if is_users == 'all_user':
                content_log['content'] = u'为用户 所有用户 推送极光消息，消息内容：' + content
                create_msg(simplejson.dumps({'body': content, 'jpushtype':'tags', 'tags':['all']}), 'jpush')
                self.flash("推送成功")
            elif is_users == 'user':
                if number:
                    content_log['content'] = u'为用户 ' + number + u' 推送极光消息，消息内容：' + content
                    num = number.split(',')
                    for n in num:
                        sms = {'apptype': 1, 'body': content, 'jpushtype':'alias', 'alias': n}
                        create_msg(simplejson.dumps(sms), 'jpush')
                    self.flash("推送成功")
                else:
                    self.flash("请输入电话号码！")
            elif is_users == 'group_user':
                content_log['content'] = u'为用户组 ' + str(user_type) + u' 推送极光消息，消息内容：' + content
                tags = []
                if province != '0':
                    tags.append(province)
                if city != '0':
                    tags.append(city)
                if district != '0':
                    tags.append(district)
                print user_type, tags
                create_msg(simplejson.dumps({'body': content, 'jpushtype': 'tags', 'tags': tags}),
                           'jpush')
                self.flash("推送成功")
        # 短信
        elif sms_type == 1:
            if is_users and content:
                if is_users == 'all_user':
                    stores = Store.select()
                    mobiles = ''
                    for s in stores:
                        #获取所有用户手机号码并于英文逗号隔开
                        if len(s.mobile) == 11:
                            mobiles += s.mobile + ','
                            logging.info('---%s-%s--%s' % (s.id, s.name, s.mobile))
                    j = 0
                    #每次发送号码不能大于600个 7200字符
                    while j < (stores.count() + 599) / 600:
                        if len(mobiles) > 7200:
                            cells = mobiles[0:7200]
                        else:
                            cells = mobiles
                        sms = {'mobile': cells, 'body': content, 'signtype': '1', 'isyzm': ''}
                        # create_msg(simplejson.dumps(sms), 'sms')
                        #删除已发送的手机号码
                        mobiles = mobiles[(j+1)*7200:]
                        j += 1
                    self.flash("发送成功")
                elif is_users == 'user':
                    if number:
                        sms = {'mobile': number, 'body': content, 'signtype': '1', 'isyzm': ''}
                        # create_msg(simplejson.dumps(sms), 'sms')
                        self.flash("发送成功")
                    else:
                        self.flash("请输入电话号码！")
                elif is_users == 'group_user':
                    area_code = 0
                    if district and district != '0':
                        area_code = district+'%'
                    elif city and city != '0':
                        area_code = city+'%'
                    elif province and province != 0:
                        area_code = province+'%'
                    if area_code:
                        stores = Store.select().where(Store.area_code % area_code)
                        mobiles = ''
                        for s in stores:
                            #获取所有用户手机号码并于英文逗号隔开
                            if len(s.mobile) == 11:
                                mobiles += s.mobile + ','
                                logging.info('---%s-%s-%s-%s'%(s.id, s.name, s.area_code, s.mobile))
                        j = 0
                        logging.info('-----%s---%s---'%(content, mobiles))
                        #每次发送号码不能大于600个 7200字符
                        while j < (stores.count() + 599) / 600:
                            if len(mobiles) > 7200:
                                cells = mobiles[0:7200]
                            else:
                                cells = mobiles
                            sms = {'mobile': cells, 'body': content, 'signtype': '1', 'isyzm': ''}
                            #create_msg(simplejson.dumps(sms), 'sms')
                            #删除已发送的手机号码
                            mobiles = mobiles[(j+1)*7200:]
                            j += 1
                        self.flash("发送成功")
                    else:
                        self.flash("请选择地区")
            else:
                self.flash("尚未填写短信内容")
        # 站内
        elif sms_type == 2:
            pass
        items = Area.select().where((Area.pid >> None) & (Area.is_delete == 0) & (Area.is_site == 1))
        self.redirect('/admin/send_msg')


@route(r'/admin/log', name='admin_log')  # 系统日志
class LogHandler(AdminBaseHandler):
    def get(self):
        page = int(self.get_argument('page', 1))
        pagesize = setting.ADMIN_PAGESIZE

        logs = AdminUserLog.select().order_by(AdminUserLog.created.desc())
        total = logs.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize if (total / pagesize) > 0 else 1
        logs = logs.paginate(page, pagesize)

        self.render('admin/sysSetting/logs.html', active='log', logs=logs, page=page, totalpage=totalpage, total=total)


@route(r'/admin/pw', name='password')  # 密码管理
class PasswordHandler(AdminBaseHandler):
    def get(self):
        self.render('admin/sysSetting/password.html', active='pw')

    def post(self):
        opassword = self.get_argument("Password", None)
        password = self.get_argument("NPassword", None)
        apassword = self.get_argument("RNPassword", None)
        if opassword and password and apassword:
            if len(password) < 6:
                self.flash("请确认输入6位以上新密码")
            elif password != apassword:
                self.flash("请确认新密码和重复密码一致")
            else:
                user = self.get_admin_user()
                if user.check_password(opassword):
                    user.password = AdminUser.create_password(password)
                    user.save()
                    self.session['admin'] = user
                    self.session.save()
                    self.flash("修改密码成功。")
                else:
                    self.flash("请输入正确的原始密码")
        else:
            self.flash("请输入原始密码和新密码")
        self.redirect('/admin/pw')


# ----------------------------------------------------------其它--------------------------------------------------------
@route(r'/admin/gift_area', name='admin_area')  # 积分区域管理
class AreaHandler(AdminBaseHandler):
    def get(self):
        defultCode = self.get_argument('defultCode', '0')
        defultSub = int(self.get_argument('defultSub', 0))
        items = Area.select().where((Area.pid >> None ) & (Area.is_delete == 0)).order_by(Area.sort,Area.id,Area.spell)

        self.render('admin/insurance/score_list.html', items=items, active='gift_area',
                    defultCode=defultCode, defultSub=defultSub)


@route(r'/admin/changeareascorestatu/(\d+)', name='admin_score_area_del')  # 修改积分区域状态
class AdminScoreAreaDelHandler(AdminBaseHandler):
    def get(self,id):
        status = int(self.get_argument('status', 0))
        try:
            area = Area.get(id = id)
            if len(area.code) == 8:   # 市
                area.is_scorearea = status
                area.save()
                codelike = area.code[:4] + '%'
                areas = Area.select().where(Area.code % codelike)
                pStatus = 0
                for a in areas:
                    if len(a.code)==8 and a.is_scorearea == 1:
                        pStatus = 1
                        break
                p = Area.get(code=area.code[:4])
                p.is_scorearea = pStatus
                p.save()
            else:   # 省
                area.is_scorearea = status
                area.save()
                areas = Area.select().where(Area.pid==id)
                for a in areas:
                    a.is_scorearea = status
                    a.save()
            self.flash(u"修改成功！")
        except Exception, e:
            logging.info('Error: %s'%e.message)
            self.flash(u"修改失败！")
        self.redirect('/admin/gift_area?defultCode=%s&defultSub=%s'%(area.code, 1))


@route(r'/admin/loop', name='admin_loop')  # 死循环
class LoopTestHandler(AdminBaseHandler):
    executor = ThreadPoolExecutor(2)
    @asynchronous
    @coroutine
    def get(self):
        a = yield self._sleep()
        self.write("when i sleep s")
        self.finish()

    @run_on_executor
    def _sleep(self):
        for i in xrange(20):
            time.sleep(1)
            print '--%(num)s--' % {'num': i}
        # self.write('end test')
        return 1












