#!/usr/bin/env python
# coding=utf8

import logging
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.options import  parse_command_line
import sys
from bootloader import settings, jinja_environment, memcachedb
from lib.filter import register_filters
from lib.route import Route
from handler import MobilePageNotFoundHandler, mobile_app, mobile_mine, mobile_pay_notify


class Application(tornado.web.Application):
    def __init__(self):
        self.jinja_env = jinja_environment
        self.jinja_env.filters.update(register_filters())
        self.jinja_env.tests.update({})
        self.jinja_env.globals['settings'] = settings
        self.memcachedb = memcachedb

        handlers = [
                       tornado.web.url(r"/style/(.+)", tornado.web.StaticFileHandler,
                                       dict(path=settings['static_path']), name='static_path')
                   ] + Route.routes() +[(r".*", MobilePageNotFoundHandler)]
        tornado.web.Application.__init__(self, handlers, **settings)


def runserver():
    parse_command_line()
    http_server = HTTPServer(Application(), xheaders=True)
    port = 8889
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    http_server.listen(port)
    loop = tornado.ioloop.IOLoop.instance()

    logging.info('Mobile Service running on http://127.0.0.1:%d' % port)
    loop.start()


if __name__ == '__main__':
    runserver()

