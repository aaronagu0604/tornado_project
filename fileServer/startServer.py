#!/usr/bin/env python
#
# Copyright 2009 Facebook
#

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import logging
import sys
from handlers import UploadImageHandler,  PageNotFoundHandler, DefaultHandler, ViewHandler
import memcache
import setting


class Application(tornado.web.Application):
    def __init__(self):
        self.session = memcache.Client([setting.memcache_host])

        handlers = [
                        (r"/", DefaultHandler),
                        (r"/upload/image", UploadImageHandler),
                        (r"/upload/view", ViewHandler),
                        tornado.web.url(r".*", tornado.web.StaticFileHandler,
                                        dict(path=setting.imgDir), name='static_path')
                    ]
        tornado.web.Application.__init__(self, handlers)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    application = Application()
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    port = 8889
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    http_server.listen(port)
    loop = tornado.ioloop.IOLoop.instance()
    logging.info('File Server running on http://127.0.0.1:%d' % port)
    loop.start()
