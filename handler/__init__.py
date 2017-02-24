#!/usr/bin/env python
# coding=utf8


from tornado.web import RequestHandler
from model import User, Store
from lib.session import Session
from lib.mixin import FlashMessagesMixin
import logging


class MobilePageNotFoundHandler(RequestHandler):
    def get(self):
        self.set_status(404)
        return self.write('not found')


class MobileBaseHandler(RequestHandler):
    def get_user(self):
        user = None
        token = self.request.headers.get('token', None)
        if token:
            data = self.application.memcachedb.get(token)
            if data is not None:
                try:
                    user = User.get(id=data)
                except:
                    user = None
        return user

    def get_store_area_code(self):
        user = self.get_user()
        if user is None:
            area_code = self.get_default_area_code()  # 默认使用西安市的code
        else:
            area_code = user.store.area_code
        return area_code

    def get_default_area_code(self):
        return '00270001'  # 默认使用西安市的code


class MobileAuthHandler(MobileBaseHandler):
    def prepare(self):
        token = self.request.headers.get('token', None)
        if token:
            data = self.application.memcachedb.get(token)
            if data is None:
                self.set_status(401)
                logging.info('----------Unauthorized----------------')
                self.write('Unauthorized')
                self.finish()
            else:
                logging.info('----token-----')
        else:
            self.set_status(401)
            self.write('Unauthorized')
            self.finish()


class AdminPageNotFoundHandler(RequestHandler):
    def get(self):
        self.set_status(404)
        return self.write("您访问的资源不存在")


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

