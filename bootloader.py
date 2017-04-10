#!/usr/bin/env python
# coding=utf8

import os
from jinja2 import Environment, FileSystemLoader
from jinja2 import MemcachedBytecodeCache
import setting
from lib.util import setting_from_object
from lib.database import Db
import memcache

settings = setting_from_object(setting)

settings.update({
    'template_path': os.path.join(os.path.dirname(__file__), 'template'),
    'static_path': os.path.join(os.path.dirname(__file__), 'style'),
    'upload_path': os.path.join(os.path.dirname(__file__), 'upload'),
    'cookie_secret': "Fux+poCnRSGIb/EsikPs5gI0BTwBBkN5k8U4kPxaV1o=",
    'login_url': '/signin',
    "xsrf_cookies": True,
    'autoescape': None
})


memcachedb = memcache.Client([settings['memcache_host']])

bcc = None
if settings['debug'] == False:
    bcc = MemcachedBytecodeCache(memcachedb)

jinja_environment = Environment(
    loader=FileSystemLoader(settings['template_path']),
    bytecode_cache=bcc,#缓存模板编译的结果到memcache
    auto_reload=settings['debug'],
    autoescape=False)

db_old = Db({'db': 'carlife', 'host': '123.57.217.29', 'port': settings['db_port'], \
         'user': 'root', 'passwd': '9%qVP*vz', 'charset': 'utf8', \
         'max_connections':settings['max_connections'], 'stale_timeout':settings['stale_timeout']})
db_move = Db({'db': 'czjmove', 'host': settings['db_host'], 'port': settings['db_port'], \
         'user': settings['db_user'], 'passwd': settings['db_passwd'], 'charset': 'utf8', \
         'max_connections':settings['max_connections'], 'stale_timeout':settings['stale_timeout']})

db = Db({'db': settings['db_name'], 'host': settings['db_host'], 'port': settings['db_port'], \
         'user': settings['db_user'], 'passwd': settings['db_passwd'], 'charset': 'utf8', \
         'max_connections':settings['max_connections'], 'stale_timeout':settings['stale_timeout']})


