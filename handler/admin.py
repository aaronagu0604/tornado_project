#!/usr/bin/env python
# coding=utf8

from handler import AdminBaseHandler, BaseHandler
from lib.route import route
from model import *
import simplejson
import time
import logging
import setting


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
        try:
            qadminuser = AdminUser.select()
            if int(admin_id) > 0:
                adminUser = AdminUser.get(id=admin_id)
            else:
                adminUser = None
            pagesize = setting.ADMIN_PAGESIZE

            total = qadminuser.count()
            if total % pagesize > 0:
                totalpage = total / pagesize + 1
            else:
                totalpage = total / pagesize
            ivs = qadminuser.order_by(AdminUser.id.desc()).paginate(page, pagesize)
            self.render("admin/user/admin_user.html",ivs=ivs, adminUser=adminUser, total=total, page=page,
                        pagesize=pagesize, totalpage=totalpage, active='admin_user')
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
        message_path = 'C:/Users/agu/Desktop/tmp/'
        try:
            datetime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前时间作为图片名称
            if mobile_img:
                filename = message_path + str(datetime) + "_mobile.jpg"
                with open(filename, "wb") as f:
                    f.write(mobile_img)
                category.img_m = filename
            if pc_img:
                filename = message_path + str(datetime) + "_pc.jpg"
                with open(filename, "wb") as f:
                    f.write(pc_img)
                category.img_pc = filename
            category.save()
            self.flash(show_msg + u"成功")
        except Exception, ex:
            self.flash(str(ex))
        self.redirect('/admin/category')


@route(r'/admin/brand', name='admin_brand')  # 品牌管理
class BrandHandler(AdminBaseHandler):
    def get(self):
        page = int(self.get_argument("page", '1'))
        pagesize = setting.ADMIN_PAGESIZE

        brands = BrandCategory.select()
        total = brands.count()
        if total % pagesize > 0:
            totalpage = total / pagesize + 1
        else:
            totalpage = total / pagesize
        bs = brands.paginate(page, pagesize)

        self.render('admin/product/brand.html', bs=bs, total=total, page=page, pagesize=pagesize,totalpage=totalpage, active='brand')


@route(r'/admin/edit_brand/(\d+)', name='admin_edit_brand')
class EditBrandHandler(AdminBaseHandler):
    def get(self, id):
        id = int(id)
        brand_category = None
        categories = Category.select()
        if id != 0:
            try:
                brand_category = BrandCategory.get(brand = id)
            except:
                self.redirect("/admin/brand")
                return
        self.render('admin/product/brand_edit.html', brand_category=brand_category, categories=categories, active='brand')

    def post(self, brand_id):
        id = int(brand_id)
        name = self.get_argument("name", None)
        engname = self.get_argument("engname", None)
        pinyin = self.get_argument("pinyin", None)
        intro = self.get_argument("intro", None)
        sel_type = int(self.get_argument("sel_type", 1))
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
                with open('upload/ad/' + filename, "wb") as f:
                    f.write(self.request.files["file"][0]["body"])
                ad.logo = '/upload/ad/' + filename
            ad.name = name
            ad.engname = engname
            ad.pinyin = pinyin
            ad.intro = intro
            ad.ptype = sel_type
            ad.active = 1 if active else 0
            ad.hot = 1 if hot else 0
            ad.save()
        except Exception, e:
            pass
        self.redirect("/admin/brand")


@route(r'/admin/delete_brand/(\d+)', name='admin_delete_brand')
class DeleteBrandHandler(AdminBaseHandler):
    def get(self, id):
        p = Brand.get(id=id)
        p.active = 0
        p.save()
        self.redirect("/admin/brand")


@route(r'/admin/product/(\d+)', name='admin_product')
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

        self.render('admin/product/product.html', products=products, total=total, page=page, c_id=category,
                    pagesize=pagesize, totalpage=totalpage, active=product_type, keyword=keyword, status=active,
                    categories=categories, is_score=is_score)


@route(r'/admin/edit_product/(\d+)', name='admin_edit_product')  # 修改产品页
class EditProductHandler(AdminBaseHandler):
    def get(self, pid):
        pid = int(pid)
        if pid > 0:
            p = Product.get(id=pid)
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
        logging.info('---%s---'%category_attributes)
        brands = Brand.select()
        self.render('admin/product/product_edit.html', p=p, brands=brands, category_attributes=category_attributes)



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


@route(r'/admin/insurance', name='admin_insurance_list')  # 保险列表
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
        items = InsuranceScoreExchange.select().where((InsuranceScoreExchange.insurance==iid)
                                                     & (InsuranceScoreExchange.area_code == area_code))
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
        items = LubePolicy.select().where((LubePolicy.insurance==iid)
                                                     & (LubePolicy.area_code == area_code))
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



