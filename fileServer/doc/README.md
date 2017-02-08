运行： python ./src/startServer.py

系统要求：
nginx
centos 6.x
mysql 5.1x
memcached

一 安装基本环境
1 安装系统环境
rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-6

yum -y install gcc nginx mysql-libs mysql-server mysql-devel memcached


#把源文件放进来

#升级python http://nerd-is.in/2013-03/upgrade-python/

pip install -r requirement.txt

vi config/supervisord.conf


supervisord -c /var/lib/jenkins/jobs/czj/workspace/supervisord.conf #运行supervisord
supervisorctl status #查看运行环境

vi /config/nginx.conf


二 项目配置
cd src
vi setting.py
#设置数据库和缓存服务器信息


三 开始运行
supervisorctl status    #查看状态
supervisorctl restart all   #重启所有
supervisorctl stop eofan8889    #停止eofan8889
supervisorctl start eofan8889   #启动eofan8889

改变配置文件时执行：
supervisorctl reread
supervisorctl update

nginx -c /home/www/workspace/eofan/src/nginx.conf
nginx 需要给/etc/mime.types 中增加 image/svg+xml      svg

nginx -s reload 重新加个nginx配置，不用重启nginx

查看nginx缓存是否起作用：curl get -I http://www.eofan.com/upload/02020101/1.jpg
连续访问两次，出现hit标示命中缓存

四 开防火墙端口：11211

iptables -I INPUT -p tcp --dport 11211 -j ACCEPT
/etc/rc.d/init.d/iptables save
/etc/rc.d/init.d/iptables restart

#禁止此IP1.2.3.4访问服务器，不用重启防火墙
iptables -I INPUT -s 1.2.3.4 -j DROP

查看进程
ps -lx
test
杀进程
kill -9 PID

memcached -d -m 20 -u root -l 123.56.94.179 -p 11211

# /usr/local/bin/memcached -d -m 10 -u root -l 192.168.141.64 -p 12000 -c 256 -P /tmp/memcached.pid
-d选项是启动一个守护进程，
-m是分配给Memcache使用的内存数量，单位是MB，我这里是10MB，
-u是运行Memcache的用户，我这里是root，
-l是监听的服务器IP地址，如果有多个地址的话，我这里指定了服务器的IP地址192.168.0.200，
-p是设置Memcache监听的端口，我这里设置了12000，最好是1024以上的端口，
-c选项是最大运行的并发连接数，默认是1024，我这里设置了256，按照你服务器的负载量来设定，
-P是设置保存Memcache的pid文件，我这里是保存在 /tmp/memcached.pid，

#  yum install freetype-devel.x86_64
#  yum install python-devel.x86_64

#  pip install reportlab

需开始15672的外部端口，若是单独服务器，需开始5672的端口
service rabbitmq-server on #以服务形式启动rabbitmq-server
chkconfig rabbitmq-server on #开机自动启动rabbitmq-server的服务

CentOS 设置定时任务
vim /etc/crontab
15 0 * * * root python /home/www/workspace/eofan/src/handler/timer.py #代表每日0点15分执行一次
* */3 * * * root python /home/www/workspace/eofan/src/handler/timerwl.py #代表每3小时执行一次
设置完成后重新启动 crond 的服务：service crond restart

tail -f filename 实时刷新看日志

tornado异步非阻塞解决方案：
说明：某一个耗时的操作会影响网站的整个性能，导致其他正常访问的url，需等待耗时操作完成后才能返回结果。
非阻塞解决方案可以让其它正常的url访问立刻返回，提高整体网站的性能；但是不能让耗时的操作立刻返回
http://blog.csdn.net/jazywoo123/article/details/17566401
http://www.cnblogs.com/xusion/articles/3492417.html

数据抓取程序运行方法：
scrapy crawl dmoz #dmoz为蜘蛛名称


#升级PIL到支持jpeg的缩略图：
http://stackoverflow.com/questions/18504835/pil-decoder-jpeg-not-available-on-ubuntu-x64
You can try this:

1. clear PIL packages

rm -rf /usr/lib/python2.7/site-packages/PIL
rm -rf /usr/lib/python2.7/site-packages/PIL.pth
2. install required packages

ubuntu:
apt-get install libjpeg-dev libfreetype6-dev zlib1g-dev libpng12-dev

centos:
yum install zlib zlib-devel
yum install libjpeg libjpeg-devel
yum install freetype freetype-devel
3.download Image and install

wget http://effbot.org/downloads/Imaging-1.1.7.tar.gz
tar xzvf Imaging-1.1.7.tar.gz
cd Imaging-1.1.7
# if the sys is x64, you must also do this: edit the setup.py file and set:
# centOS:
TCL_ROOT = '/usr/lib64'
JPEG_ROOT = '/usr/lib64'
ZLIB_ROOT = '/usr/lib64'
TIFF_ROOT = '/usr/lib64'
FREETYPE_ROOT = '/usr/lib64'
LCMS_ROOT = '/usr/lib64'
# Ubuntu:
TCL_ROOT = '/usr/lib/x86_64-linux-gnu'
JPEG_ROOT = '/usr/lib/x86_64-linux-gnu'
ZLIB_ROOT = '/usr/lib/x86_64-linux-gnu'
TIFF_ROOT = '/usr/lib/x86_64-linux-gnu'
FREETYPE_ROOT = '/usr/lib/x86_64-linux-gnu'
LCMS_ROOT = '/usr/lib/x86_64-linux-gnu'
#then install it use:
python2.7 setup.py install


https 证书生成：
http://www.linuxidc.com/Linux/2013-08/88271.htm

# 清除memcache
telnet localhost 11211
flush_all
quit

禅道启动：
 /opt/php-5.6.28/sapi/fpm/php-fpm # 监听9000端口
 nginx启动 etc/nginx/conf.d # 动态加载该文件夹下所有的*.conf文件