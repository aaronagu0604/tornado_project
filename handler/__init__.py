#!/usr/bin/env python
# coding=utf8

import urllib
from tornado.web import RequestHandler
from lib.session import Session
from lib.mixin import FlashMessagesMixin
from model import User, AdminUser, Topic, Oauth, User_Login_Log
import base64
import logging
import functools
import time


class BaseHandler(RequestHandler, FlashMessagesMixin):
    def set_default_headers(self):
        self.clear_header('Server')

    def render_string(self, template_name, **context):
        context.update({
            'xsrf': self.xsrf_form_html,
            'module': self.ui.modules,
            'request': self.request,
            'user': self.current_user,
            'admin': self.get_admin_user(),
            'handler': self,
            'store': self.get_store_user()}
        )

        return self._jinja_render(path=self.get_template_path(), filename=template_name,
                                  auto_reload=self.settings['debug'], **context)

    def _jinja_render(self, path, filename, **context):
        template = self.application.jinja_env.get_template(filename, parent=path)
        return template.render(**context)

    @property
    def is_xhr(self):
        return self.request.headers.get('X-Requested-With', '').lower() == 'xmlhttprequest'

    @property
    def memcachedb(self):
        return self.application.memcachedb

    @property
    def session(self):
        if hasattr(self, '_session'):
            return self._session
        else:
            sessionid = self.get_secure_cookie('sid')
            self._session = Session(self.application.session_store, sessionid, expires_days=1)
            if not sessionid:
                self.set_secure_cookie('sid', self._session.id, expires_days=1)
            return self._session

    def get_current_user(self):
        return self.session['user'] if 'user' in self.session else None

    def get_admin_user(self):
        return self.session['admin'] if 'admin' in self.session else None

    def get_store_user(self):
        return self.session['store'] if 'store' in self.session else None

    def get_user_role(self):
        user = self.get_admin_user()
        if not user:
            return []
        else:
            return list(user.roles)

    @property
    def next_url(self):
        return self.get_argument("next", "/login")

    def write_error(self, status_code, **kwargs):
        import traceback

        msg = '<h2>未显示错误！</h2>'
        if "exc_info" in kwargs:
            exc_info = kwargs["exc_info"]
            trace_info = ''.join(["%s<br>" % line for line in traceback.format_exception(*exc_info)])
            request_info = ''.join(
                ["%s: %s <br>" % (k, self.request.__dict__[k]) for k in self.request.__dict__.keys()])
            error = exc_info[1]
            msg = u"""Error:<br>
                %s<br>
                Traceback:<br>
                %s<br>
                Request Info<br>
                %s""" % (error, trace_info, request_info)
        self.set_status(status_code)
        if status_code == 404:
            return self.render('site/404.html')
        else:
            msg = msg if self.settings['debug'] else None
            return self.render('site/error.html', msg=msg)


class BaseWithCityHandler(BaseHandler):
    def prepare(self):
        '''
        if (self.get_secure_cookie('city_id') and self.get_secure_cookie('city_name') and self.get_secure_cookie('city_code'))or self.request.uri.find("/a")>=0 or  self.request.uri.find("/select_city")>=0 or self.get_argument("city_id",None):
            pass
        else:
            #self.redirect("/select_city")
            pass
            默认城市西安
            这里的city_id是表tb_area里的pid
            self.set_secure_cookie("city_id",'27',expires_days=1000)
            self.set_secure_cookie("city_code",'00270001', expires_days=1000)
            self.set_secure_cookie("city_name",u"西安市", expires_days=1000)
            self.redirect("/")
         '''
        super(BaseWithCityHandler, self).prepare()


class AdminBaseHandler(BaseHandler):
    def prepare(self):
        if self.get_admin_user():
            pass
        else:
            self.redirect("/admin/login")

        super(AdminBaseHandler, self).prepare()

    def vrole(self, rolelist):
        userrole = self.get_user_role()
        for n in userrole:
            if rolelist.count(n) > 0:
                return True
        return False

    def get_active_topic_count(self):
        t = Topic.select().where(Topic.status == 0)
        return t.count()


class UserBaseHandler(BaseWithCityHandler):
    def prepare(self):
        if not self.current_user:
            url = self.get_login_url()
            if "?" not in url:
                url += "?" + urllib.urlencode(dict(next=self.request.full_url()))
            self.redirect(url)

        super(UserBaseHandler, self).prepare()


class PageNotFoundHandler(BaseHandler):
    def get(self):
        self.set_status(404)
        return self.render("site/404.html")


class AdminPageNotFoundHandler(RequestHandler):
    def get(self):
        self.set_status(404)
        return self.write("您访问的资源不存在")


class MobileHandler(RequestHandler):
    def get_mobile_user(self):
        result = {'flag': 0}
        login_type = 0
        try:
            args = eval(self.request.body)
        except:
            result['msg'] = '参数错误'
            return result

        mobile = args["mobile"]
        password = args["password"]
        if args.has_key("login_type"):
            login_type = args["login_type"] # 登录类型 1门店登录
        result = {'flag': 0}
        if mobile and password:
            try:
                user = User.get(User.username == mobile)
                if user.check_mobile_password(password):
                    if user.isactive > 0:
                        user.updatesignin()
                        result['flag'] = 1
                        result['msg'] = {
                                         'birthday':'',
                                         'username': user.username,
                                         'nickname': user.nickname,
                                         'mobile': user.mobile,
                                         'score': user.score,
                                         'level': user.level,
                                         'cashed_money': user.cashed_money,
                                         'balance': user.balance,
                                         'id': user.id,
                                         'portraiturl': user.portraiturl,
                                         'bindmobile': user.bindmobile(),
                                         'hascheckedin': user.hascheckedin(),
                                         'grade': user.grade,
                                         'store': None}
                        if user.birthday is not None:
                            try:
                                 result['msg']['birthday'] = user.birthday.strftime('%Y-%m-%d')
                            except Exception, e:
                                logging.info(e)

                        result['msg']['grade'] = user.grade
                        if login_type == 0:
                            if user.grade == 1:
                                result['flag'] = 0
                                result['msg'] = "您是商家用户，请登录商家版！"
                        elif login_type == 1:
                            if user.store:
                                result['msg']['store'] ={
                                    'birthday':'',
                                    'id':user.store.id,
                                    'name':user.store.name,
                                    'province_code':user.store.area_code[0:4],
                                    'city_code':user.store.area_code[0:8],
                                    'area_code':user.store.area_code,
                                    'address':user.store.address,
                                    'link_man':user.store.link_man,
                                    'tel':user.store.tel,
                                    'image':user.store.image,
                                    'image_legal':user.store.image_legal,
                                    'image_license':user.store.image_license,
                                    'check_state':user.store.check_state,
                                }

                                if user.birthday is not None:
                                    try:
                                         result['msg']['birthday'] = user.birthday.strftime('%Y-%m-%d')
                                    except Exception, e:
                                        logging.info(e)
                        else:
                            result['flag'] = 0
                            result['msg'] = "错误的登录请求！"
                        self.application.session_store.set_session(str(mobile)+':'+str(password), {}, None, expiry=24*60*60)

                        x = args["x"]
                        y = args["y"]
                        province = args["province"]
                        city = args["city"]
                        region = args["region"]
                        address = args["address"]
                        if x and y:
                            User_Login_Log.create(user=user.id, x=x, y=y, province=province, city=city, region=region, address=address, created=int(time.time()))
                    else:
                        result['msg'] ="此账户被禁止登录，请联系管理员。"
                else:
                    result['msg'] ="密码错误"
            except Exception, ex:
                oauths = Oauth.select().where(Oauth.openid == mobile)
                if oauths.count() > 0:
                    user = oauths[0].user
                    if user.check_mobile_password(password):
                        if user.isactive > 0:
                            user.updatesignin()
                            result['flag'] = 1
                            result['msg'] = {'username': user.username,
                                             'nickname': user.nickname,
                                             'mobile': user.mobile,
                                             'score': user.score,
                                             'balance': user.balance,
                                             'id': user.id,
                                             'bindmobile': user.bindmobile(),
                                             'hascheckedin': user.hascheckedin()}
                            self.application.session_store.set_session(str(mobile)+':'+str(password), {}, None, expiry=24*60*60)
                        else:
                            result['flag'] = 0
                            result['msg'] ="此账户被禁止登录，请联系管理员。"
                else:
                    result['flag'] = 0
                    result['msg'] = "此用户不存在"
        else:
            result['msg'] = "请输入用户名或者密码"
        return result

    def get_cg_mobile_user(self):
        result = {'flag': 0}
        try:
            args = eval(self.request.body)
        except:
            result['msg'] = '参数错误'
            return result
        username = args["username"]
        password = args["password"]
        result = {'flag': 0}
        if username and password:
            try:
                user = AdminUser.get(AdminUser.username == username)
                if user.check_password(password):
                    if user.isactive > 0 and (list(user.roles).count('D') > 0 or list(user.roles).count('B') > 0
                    or list(user.roles).count('A') > 0 or list(user.roles).count('C') > 0):
                        user.updatesignin()
                        result['flag'] = 1
                        if list(user.roles).count('R') > 0 or list(user.roles).count('D') > 0:
                            role_intake = 1
                        else:
                            role_intake = 0
                        result['msg'] = {'username': user.username,
                                     'mobile': user.mobile,
                                     'id': user.id,
                                     'role_intake':role_intake}
                    else:
                        result['msg'] ="此账户被禁止登录采购系统，请联系管理员。"
                else:
                    result['msg'] ="密码错误"
            except Exception, ex:
                result['msg'] = "此用户不存在"
        else:
            result['msg'] = "请输入用户名或者密码"
        return result

class PFBaseHandler(BaseHandler):
    def prepare(self):
        adminUser = self.get_pf_user()
        if adminUser and self.vrole('P'):
            pass
        else:
            self.redirect("/pf/login")

        super(PFBaseHandler, self).prepare()

    def vrole(self, rolelist):
        userrole = list(self.get_pf_user().roles)
        for n in userrole:
            if rolelist.count(n) > 0:
                return True
        return False

    def get_pf_user(self):
        return self.session['pf'] if 'pf' in self.session else None

class StoreBaseHandler(BaseHandler):
    def prepare(self):
        adminUser = self.get_store_user()
        if adminUser and self.vrole('J'):
            pass
        else:
            self.redirect("/store/login")

        super(StoreBaseHandler, self).prepare()

    def vrole(self, rolelist):
        userrole = list(self.get_store_user().roles)
        for n in userrole:
            if rolelist.count(n) > 0:
                return True
        return False

    def get_store_user(self):
        return self.session['store'] if 'store' in self.session else None

class OfflineHandler(RequestHandler):

    def get_offline_user(self):
        username = self.get_argument("mobile")
        password = self.get_argument("password")
        result = '0'
        if username and password:
            try:
                user = AdminUser.select().where(AdminUser.username == username)
                if user.count() > 0:
                    user = user[0]
                    if user.check_password(password):
                        if user.isactive > 0 :
                            user.updatesignin()
                            result = user.id
                        else:
                            result ="此账户被禁止登录采购系统，请联系管理员。"

                    else:
                        result ="密码错误"
                else:
                    result = "用户名不存在"
            except Exception, ex:
                result = "登陆异常，异常信息：" + ex.message
        else:
            result = "请输入用户名或者密码"
        return result

def require_basic_authentication(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        auth_header = self.request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Basic '):
            logging.error(self.request.remote_ip + ' no Authorization info')
        return method(self, *args, **kwargs)
    return wrapper

