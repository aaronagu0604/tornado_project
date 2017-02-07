#!/usr/bin/env python
# coding=utf8

imgDir = "/home/www/fileservice/data/"  # 图片文件保存地址
waterMarker = "/home/www/fileservice/data/watermark.png"  # 图片水印文件路径
voiceDir = "/home/www/fileservice/data/"  # 音频文件保存地址
openHost = "http://img.icomelife.com"  # 图片服务器的访问基URL
serverName = 'server1'  # 保存在该图片服务器中文件的命名前缀，用于反向代理时快速定位图片所在服务器，如果禁用一台服务器，该字段无实际意义
memcache_host = '127.0.0.1:11211'

