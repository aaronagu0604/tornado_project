#!/usr/bin/env python
# coding=utf-8

import re
import time
from peewee import *
import hashlib
from bootloader import db_old
from playhouse.signals import post_save
import logging


# 快递公司
class Delivery(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=50)  # 快递公司名称

    class Meta:
        db_table = 'tb_delivery'

#快递公司单号库
class DeliveryNumbers(db_old.Model):
    id = PrimaryKeyField()
    delivery = ForeignKeyField(Delivery, related_name='numbers', db_column='delivery_id', null=True)  #物流公司
    num = CharField(max_length=32, unique=True)  #快递单号
    status = IntegerField(default=0)  # 状态 0未使用 1已使用 -1删除

    class Meta:
        db_table = 'tb_delivery_numbers'

# 地区表
class Area(db_old.Model):
    id = PrimaryKeyField()
    pid = ForeignKeyField('self', db_column='pid', null=True)  #  IntegerField(default=0)           # 父级ID
    code = CharField(max_length=40)         # 编码
    has_sub = IntegerField(default=0)       # 是否拥有下级
    name = CharField(max_length=30)         # 名称
    spell = CharField(max_length=50)        # 拼音
    spell_abb = CharField(max_length=30)    # 拼音缩写
    show_color = CharField(max_length=30)   # 显示颜色
    show_itf = IntegerField(default=0)      # 是否斜体
    show_btf = IntegerField(default=0)      # 是否粗体
    image = IntegerField(default=0)         # 图片地址
    sort = IntegerField(default=00)         # 排序，数字越小排在越前
    is_delete = IntegerField(default=0)     # 是否删除
    is_site = IntegerField(default=0)       # 是否站点
    is_scorearea = IntegerField(default=0)       # 是否开通积分地区
    is_lubearea = IntegerField(default=0)       # 是否开通返油地区

    def validate(self):
        if self.name:
            ft = (Area.name == self.name)
            if self.id:
                ft = ft & (Area.id != self.id)
            if Area.select().where(ft).count() > 0:
                raise Exception('地区名已存在')
        else:
            raise Exception('请输入地区名')
    def get_detailed_address(self, area_code):
        lenAreaCode = len(area_code)
        if lenAreaCode == 12 or lenAreaCode==8 or lenAreaCode==4 :
            try:
                a = Area.get(code = area_code)
                if lenAreaCode == 12:
                    addr = a.pid.pid.name+a.pid.name+a.name
                elif lenAreaCode == 8:
                    addr = a.pid.name+a.name
                else:
                    addr = a.name
                return addr
            except:
                return ''
        else:
            return ''

    class Meta:
        db_table = 'tb_area'


# 广告类型
class AdType(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=50)     # 类型名称
    remark = CharField(max_length=50, null=True)   # 备注
    imagename = CharField(max_length=100, null=True)   # 图片名
    category = CharField(max_length=50, null=True)   # 分类

    class Meta:
        db_table = 'tb_ads_type'

# 广告
class Ad(db_old.Model):
    id = PrimaryKeyField()
    url = CharField(max_length=250)  # 商品连接地址
    picurl = CharField(max_length=50)  # 广告图片地址
    imgalt = CharField(max_length=50)  # 广告图片描述
    atype = ForeignKeyField(AdType, db_column='atype')  # 广告类型 1首页大滚动 2首页小滚动，3为手机顶部首页广告 4手机腰部广告 5手机浏览推荐 6门店端采购小分类
    sort = IntegerField(default=1)  #排序顺序，数字越大排列越靠前
    city = ForeignKeyField(Area, related_name='ads_city', db_column='city_id', null=True)  # 城市ID
    city_code = CharField(max_length=50)  # 城市code
    remark = CharField(max_length=50)   # 备注
    adsize = CharField(max_length=50)   # 备注
    flag = IntegerField(default=1)  # 1启用，0停用

    def validate(self):
        if self.picurl:
            pass
        else:
            raise Exception('请上传广告图片')

    class Meta:
        db_table = 'tb_ads'

# 品牌表
class Brand(db_old.Model):
    id = PrimaryKeyField()
    pid = IntegerField(default=0)  # 父级ID
    code = CharField(max_length=40)  # 编码
    has_sub = IntegerField(default=0)   # 是否拥有下级
    name = CharField(max_length=30)  # 名称
    is_luxurious = IntegerField(default=0)  # 是否豪华车型
    spell = CharField(max_length=50)  # 拼音
    spell_abb = CharField(max_length=30)  # 拼音缩写
    show_color = CharField(max_length=30)  # 显示颜色
    show_itf = IntegerField(default=0)  # 是否斜体
    show_btf = IntegerField(default=0)  # 是否粗体
    image = IntegerField(default=0)  # 图片地址
    sort = IntegerField(default=99)  # 排序，数字越小排在越前
    is_delete = IntegerField(default=0)  # 是否删除

    class Meta:
        db_table = 'tb_brand'

# 门店
class Store(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=100)     # 门店名称
    tags = CharField(max_length=128, null=True)  # 标签
    area_code = CharField(max_length=40)    # 区域编码
    address = CharField(max_length=128, null=True)  # 详细地址
    link_man = CharField(max_length=32)    # 联系人
    tel = CharField(max_length=16)    # 联系电话
    mobile = CharField(max_length=16)    # 联系手机号
    image = CharField(max_length=128)    # 门店图片
    image_legal = CharField(max_length=128)    # 法人身份证照片
    image_license = CharField(max_length=128)    # 营业执照
    x = CharField(max_length=12)        # 经度坐标
    y = CharField(max_length=12)        # 纬度坐标
    intro = TextField()        # 介绍
    clicks = IntegerField(default=0)    # 查看次数
    credit_score = FloatField(default=0)    # 信誉分数 代表企业信誉，100分制
    star_score = FloatField(default=0)    # 星级分数 根据用户购买评价的评分来定 5分制
    comment_count = IntegerField(default=0)     # 评价数量
    store_type = IntegerField(default=0)    # 门店类型 0其它 1品牌4S店 2社会修理厂
    business_type = IntegerField(default=0)    # 业务类型 0普通业务 1保险业务 2板喷业务
    business_scope = CharField(max_length=200, null=True)    # 业务范围
    is_certified = IntegerField(default=0)    # 是否已经认证
    check_state = IntegerField(default=0)    # 审核状态 0未审核 1审核通过 2审核未通过
    is_recommend = IntegerField(default=0)    # 是否推荐 0否 1是
    last_update = IntegerField(default=0)   # 最后修改时间
    created = IntegerField(default=0)   # 创建时间
    trait = CharField(max_length=128, null=True)    # 门店特征

    class Meta:
        db_table = "tb_store"


#门店的服务区域
class StoreServerArea(db_old.Model):
    id = PrimaryKeyField()
    sid = ForeignKeyField(Store, related_name='store_server', db_column='store_id')  #所属门店
    aid = ForeignKeyField(Area, related_name='area_id', db_column='area_id')  #地区ID

    class Meta:
        db_table = "tb_store_server_area"


# 门店图片表
class StorePic(db_old.Model):
    id = PrimaryKeyField()
    store = ForeignKeyField(Store, related_name='store_pics', db_column='store_id')  #所属商品
    path = CharField(max_length=256)
    check_state = IntegerField(default=0)    # 审核状态 0未审核 1审核通过 2审核未通过
    is_cover = IntegerField(default=0)  # 状态 0是否是封面
    is_active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_store_pics'


# 店铺信息分类
class StoreNewsCategory(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=20)  # 分类名
    status = IntegerField(default=1)  # 状态 0删除 1有效
    class Meta:
        db_table = 'tb_store_news_cagetory'

# 店铺信息表
class StoreNews(db_old.Model):
    id = PrimaryKeyField()
    store = ForeignKeyField(Store, related_name='news', db_column='store_id')  # 所属店铺
    category = ForeignKeyField(StoreNewsCategory, related_name='news_category',
                                    db_column='category_id')  # 信息分类 1公司资质 2公司团队 3公司案例
    title = CharField(max_length=100)  # 标题
    image = CharField(max_length=30)    # 图片
    clicks = IntegerField(default=0)    # 查看次数
    content = TextField()        # 介绍
    check_state = IntegerField(default=0)    # 审核状态 0未审核 1审核通过 2审核未通过
    is_recommend = IntegerField(default=0)    # 是否推荐 0否 1是
    status = IntegerField(default=1)  # 状态 0删除 1有效
    last_update = IntegerField(default=0)   # 最后修改时间
    created = IntegerField(default=0)   # 创建时间

    class Meta:
        db_table = 'tb_store_news'


# 店铺商品分类
class Category_Store(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=20)  #分类名
    code = CharField(max_length=20, default='')  #分类编码,访问url
    status = IntegerField(default=1)  #状态 0删除 1有效
    store = ForeignKeyField(Store, db_column='store_id')  #所属店铺

    def validate(self):
        if self.name and self.code:
            if not re.match('^[0-9a-z]+$', self.code):
                raise Exception('访问目录只能是字母和数字组合')
            ft = ((Category_Store.name == self.name) | (Category_Store.code == self.code))
            if self.id:
                ft = ft & (Category_Store.id != self.id)
            if Category_Store.select().where(ft).count() > 0:
                raise Exception('分类同名或者目录同名')
        else:
            raise Exception('请输入分类名或者访问目录')
    class Meta:
        db_table = 'tb_category_store'

# 管理员用户表
class AdminUser(db_old.Model):
    id = PrimaryKeyField()  # 主键
    username = CharField(unique=True, max_length=32, null=False)  # 注册用户名
    password = CharField(max_length=32)  # 密码
    mobile = CharField(max_length=12)  # 手机号
    email = CharField(max_length=128)  # email
    realname = CharField(max_length=32)  # 真实姓名
    roles = CharField(max_length=8)  # D开发人员；A管理员；Y运营；S市场；K客服；C仓库；Z直踩点；B编辑；G采购；P批发商；J经销商；R采购APP入库；+经销商价格修改权限（可组合，如：DA）
    signuped = IntegerField(default=0)  # 注册时间
    lsignined = IntegerField(default=0)  # 最后登录时间
    isactive = IntegerField(default=1)  # 状态 0删除 1有效
    # store = ForeignKeyField(Store, related_name='users', db_column='store_id', null=True)  #所属店铺
    # front_user = IntegerField(null=True)    # 对应前端用户ID 每个经销商有一个默认前端用户用户后台下单。
    @staticmethod
    def create_password(raw):
        return hashlib.new("md5", raw).hexdigest()

    def check_password(self, raw):
        return hashlib.new("md5", raw).hexdigest() == self.password

    def updatesignin(self):
        self.lsignined = int(time.time())
        self.save()

    class Meta:
        db_table = 'tb_admin_users'

# 用户级别表
class UserLevel(db_old.Model):
    levelid = PrimaryKeyField()
    levelname = CharField(max_length=30, default='')  #级别名字
    startscore = IntegerField(default=0)  #级别起始积分
    endscore = IntegerField(default=0)  #级别结束积分
    xfonescore = IntegerField(default=100)  #每消费一元人民币获得消费积分数百分比,整数表示
    jlperscore = IntegerField(default=0)  #额外获得相当于消费积分百分比的奖励积分,整数表示
    commentscore = IntegerField(default=0)  #评价（晒单）商品应该获得奖励积分
    isactive = IntegerField(default=1)  #状态 0删除 1有效

    class Meta:
        db_table = 'tb_user_level'

# 用户签到表
class UserCheckIn(db_old.Model):
    id = PrimaryKeyField()
    user_id =IntegerField(default=0)# ForeignKeyField(User, related_name='checkin',db_column='user_id')  #外键到user表，字段名为user_id，从user引用为checkin
    checkintime = IntegerField(default=0)  #签到时间
    seriesnum = IntegerField(default=0)  #连续签到次数，包括本次
    isactive = IntegerField(default=1)  #状态 0删除 1有效

    class Meta:
        db_table = 'tb_user_checkin'

# 银行卡数据库
class BankCard(db_old.Model):
    id = PrimaryKeyField()
    card_bin = CharField(max_length=50, null=True) #卡号范围
    bank_name = CharField(max_length=100, null=True)  #银行名称
    bank_id = IntegerField(null=True)  #银行标示
    card_name = CharField(max_length=100,null=True)  #卡名称
    card_type = CharField(max_length=50,null=True)  #卡类型
    bin_digits = IntegerField(null=True)
    card_digits = IntegerField(null=True)
    demo = CharField(max_length=50,null=True)

    class Meta:
        db_table = 'bank_card_bin'

# # 银行表
# class Banks(db_old.Model):
#     id = PrimaryKeyField()
#     bank_name = CharField(max_length=100, null=True)  #银行名称
#     image = IntegerField(null=True)
#
#     class Meta:
#         db_table = 'tb_banks'


# 用户表
class User(db_old.Model):
    id = PrimaryKeyField()  # 主键
    username = CharField(unique=True, max_length=64, null=False)  # 注册用户名
    mobile = CharField(max_length=12)  # 注册手机号
    email = CharField(max_length=128, default='')  # email
    password = CharField(max_length=32)  # 密码
    nickname = CharField(max_length=32, default='')  # 昵称
    gender = IntegerField(default=2)  # 性别 0男 1女 2未知
    qq = CharField(max_length=15, default='')  # qq
    birthday = DateField(null=True)  # 生日
    tel = CharField(max_length=30, null=True, default='')  # 固定电话
    balance = FloatField(default=0)  # 用户账户余额
    cashed_money = FloatField(default=0)  # 用户账户可提现余额
    isactive = IntegerField(default=1)  # 用户组 0被禁止的用户 1正常用户
    signuped = IntegerField(default=0)  # 注册时间
    signupeddate = CharField(max_length=16)  # 注册日期，文本格式
    signupedtime = CharField(max_length=16)  # 注册时间，文本格式
    lsignined = IntegerField(default=0)  # 最后登录时间
    phoneactived = IntegerField(default=0)  # 0代表网站注册 1代表手机端注册 2代表后台经销商注册
    emailactived = IntegerField(default=0)  # 激活邮箱 0未 1已激活
    portraiturl = CharField(max_length=128, null=True, default='')  # 用户头像

    score = IntegerField(default=0)  # 用户积分
    gift = CharField(max_length=20, default='00')  # 礼品赠送 00未获取 10获取注册礼品 01获取首单礼品 11获取注册和首单礼品
    level = IntegerField(default=0) # 累计积分 会员等级 2000以内优先会员 2001-4000铜卡会员 4001-6000金卡会员 6001-8000白金会员 8000+钻石会员
    raffle_count = IntegerField(default=0)  # 抽奖次数

    grade = IntegerField(default=0) # 用户分级，0普通C 端用户，1门店B端用户，2厂商A端用户，3代理商用户， 4银行服务商， 5代理商可以处理保险订单
    # levelid = IntegerField(default=1) # 会员等级
    userlevel = ForeignKeyField(UserLevel, related_name='userlevel',
                           db_column='levelid',default=1)  # 外键到tb_user_level表，字段名为levelid，从tb_user_level引用为userlevel
    levelstart = IntegerField(default=0) # 用户等级开始时间
    levelend = IntegerField(default=0) # 用户结束开始时间
    store = ForeignKeyField(Store, related_name='user_store', db_column='store_id', null=True)  #所属店铺
    alipay_truename = CharField(max_length=32, default='')  # 支付宝姓名
    alipay_account = CharField(max_length=128, default='')  # 支付宝账号
    bank_truename = CharField(max_length=32, default='')  # 银行卡姓名
    bank_account = CharField(max_length=32, default='')  # 银行卡号
    bank_name = CharField(max_length=64, default='')  # 银行名称
    bank_branchname = CharField(max_length=64, default='')  # 支行名称

    @staticmethod
    def create_password(raw):
        return hashlib.new("md5", raw).hexdigest()

    def check_password(self, raw):
        return hashlib.new("md5", raw).hexdigest() == self.password

    def check_mobile_password(self, raw):
        return raw == self.password

    def bindmobile(self):
        if self.mobile == None or self.mobile == '':
            flag = 0
        else:
            flag = 1
        return flag

    def updatesignin(self):
        self.lsignined = int(time.time())
        self.save()

    def updatescore(self,stype,jftype,scorenum,log):
        #stype积分类型 jftype积分类别 scorenum积分数 log积分说明
        if(scorenum<=0):
            return self.userlevel
        score = Score()
        # log.user = user.id
        score.user=self
        score.stype = stype
        score.jftype=jftype
        score.score = scorenum
        score.log = log
        score.created = int(time.time())
        score.save()
        if stype == 0:#增加
            q=UserLevel.select().where(UserLevel.startscore<=self.level,UserLevel.endscore>=self.level).limit(1)
            if(q.count()>0 and  q[0].levelid<>self.userlevel.levelid):# and ( q[0].levelid>self.userlevel or self.userlevel>2)
                #修改会员级别
                if q[0].levelid>self.userlevel.levelid:
                    self.userlevel=q[0].levelid
                else:
                    #铜卡会员 永久有效
                    self.userlevel=2
                #time.strftime('%Y-%m-%d', time.localtime(time.time())) 2015-1-3
                # time.mktime(time.strptime(begindate, "%Y-%m-%d"))
                self.levelstart= time.mktime(time.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d"))
                self.levelend=self.levelstart+365*24*60*60
                self.save()
            else:
                self.levelstart= time.mktime(time.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d"))
                self.levelend=self.levelstart+365*24*60*60
                self.save()
        return self.userlevel

    def recountlevel(self):#重新计算会员级别，包括会员期限
        scores = Score.select().where(Score.user == self.id)
        self.level=scores.sum(Score.score)
        q=UserLevel.select().where(UserLevel.startscore<=self.level,UserLevel.endscore>=self.level).limit(1)
        if(q.count()>0):
            #修改会员级别
            self.levelid=q[0].levelid
            self.levelstart= time.mktime(time.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d"))
            self.levelend=self.levelstart+365*24*60*60
        else:
            self.levelstart= time.mktime(time.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d"))
            self.levelend=self.levelstart+365*24*60*60
        self.save()
        return self.levelid

    def hascheckedin(self):#是否已经签到
        q = UserCheckIn.select().where(UserCheckIn.user_id == self.id).order_by(UserCheckIn.checkintime.desc()).limit(1)
        flag=0
        if(q.count()>0):
            #已经有签到
            todaystart=time.mktime(time.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d"))
            # yestoday=todaystart-24*60*60
            todayend=todaystart+24*60*60
            if(q[0].checkintime>=todaystart and q[0].checkintime<todayend):#已经签到
                flag=q[0].seriesnum
            else:
                flag=0
        return flag
    class Meta:
        db_table = 'tb_users'

#用户车辆信息
class UserCarInfo(db_old.Model):
    user = ForeignKeyField(User, related_name='carinfo',
                           db_column='user_id')           # 外键到user表，字段名为user_id
    car_num = CharField(max_length=16, null=True)                      # 车牌号
    brand = ForeignKeyField(Brand, db_column='brand_id', null=True)  # 车辆品牌
    car_models = CharField(max_length=32, null=True)                   # 车辆类型
    buy_time = IntegerField(null=True)                      # 购买时间
    mileage = IntegerField(null=True)                       # 行驶里程
    owner = CharField(max_length=16, null=True)                        # 车主姓名/所有人
    color = CharField(max_length=16, null=True)                        # 颜色
    chassis_num = CharField(max_length=32, null=True)                  # 车架号
    phone = CharField(max_length=32, null=True)                        # 车主联系电话
    address = CharField(max_length=128, null=True)                     # 车主联系地址
    pailiang = FloatField(null=True)                      # 发动机排量
    check_time = IntegerField(null=True)                    # 年检时间
    created = IntegerField(null=True)           # 登记时间
    is_delete = IntegerField(default=0)                     # 是否删除


    class Meta:
        db_table = 'tb_user_car'

# 第三方登录
class Oauth(db_old.Model):
    user = ForeignKeyField(User, related_name='auths',
                           db_column='user_id')
    src = CharField(max_length=20, default='qq')  # 来源
    openid = CharField(max_length=50)  # 第三方平台用户Id

    class Meta:
        db_table = 'tb_oauths'

# 用户联系地址
class UserAddr(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='addresses',
                           db_column='user_id')  #外键到user表，字段名为user_id，从user引用为addresses
    province = CharField(max_length=16, default='陕西')  #省份
    city = CharField(max_length=16, default='西安')  #城市
    region = CharField(max_length=32, null=True)  #区域
    street = CharField(max_length=64, null=True)  #街道
    address = CharField(max_length=128, null=True)  #详细地址
    name = CharField(max_length=16, null=True)  #姓名
    tel = CharField(max_length=32, default='')  #固定电话
    mobile = CharField(max_length=11, null=True)  #手机号码
    isdefault = IntegerField(default=1)  #是否默认 0否 1是
    isactive = IntegerField(default=1)  #状态 0删除 1有效

    class Meta:
        db_table = 'tb_user_address'

# 用户汽车
class UserAuto(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='autos',
                           db_column='user_id')  #外键到user表，字段名为user_id，从user引用为autos
    brand_code = CharField(max_length=40)  # 品牌code
    mileage = IntegerField(default=0)  # 里程数（单位：km）
    buy_time = IntegerField(default=0) # 购车时间
    class Meta:
        db_table = 'tb_user_auto'

# 店铺汽车
class StoreAuto(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='store_auto_user',
                           db_column='user_id')  #外键到user表，字段名为user_id，从user引用为autos
    store = ForeignKeyField(Store, related_name='brand_auto_store', db_column='store_id')  #所属店铺
    brand_code = CharField(max_length=40)  # 品牌code
    brand_full_name =  CharField(max_length=64)  # 品牌名称

    class Meta:
        db_table = 'tb_store_auto'

# 用户消息表
class UserMessage(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='messages',
                           db_column='user_id', null=True)  # 外键到user表，字段名为user_id，从user引用为messages
    username = TextField()  # 品牌code
    type = IntegerField(default=0)  # 消息分类 0 系统消息
    is_send = IntegerField(default=0)  # 是否是发送记录 0否 1是
    title = CharField(max_length=200)  # 消息标题
    content = TextField()  # 消息内容
    has_read = IntegerField(default=0)  # 是否已读 0否 1是
    send_time = IntegerField(default=0)  # 消息发送时间
    class Meta:
        db_table = 'tb_user_message'

#用户活动记录
class UserActivity(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='activities',
                           db_column='user_id')  #外键到user表，字段名为user_id，从user引用为activities
    catchtime = IntegerField(default=0)  #领取时间
    status = IntegerField(default=1)  #状态 0删除 1有效

    class Meta:
        db_table = 'tb_user_activity'

#会员与客服访谈记录
class UserInterview(db_old.Model):
    id = PrimaryKeyField()
    admin = ForeignKeyField(AdminUser, related_name='viewadminuser',
                           db_column='admin_id')  #外键到adminuser表，字段名为user_id，从adminuser引用为viewadminuser
    user = ForeignKeyField(User, related_name='viewuser',
                           db_column='user_id')  #外键到user表，字段名为user_id，从user引用为viewuser
    title = CharField(max_length=1024, null=True)  #标题说明
    content = TextField(null=True)  # 访谈内容
    viewtime = IntegerField(default=0)  #领取时间
    status = IntegerField(default=1)  #状态 0删除 1有效

    class Meta:
        db_table = 'tb_user_interview'

#手机验证码
class UserVcode(db_old.Model):
    id = PrimaryKeyField()
    mobile = CharField(max_length=32, null=False)  #注册手机号
    vcode = CharField(max_length=16, null=False)
    created = IntegerField(index=True, default=0)
    flag = IntegerField(default=0)  #0注册 1忘记密码 2绑定手机号 3提现

    class Meta:
        db_table = 'tb_user_vcodes'

#积分历史表 user, stype, score, log, created, isactive, jftype, orderNum, remark
class Score(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='scores', db_column='user_id')
    stype = IntegerField()  #积分类型 0增加 1扣除
    score = IntegerField()  #积分数
    log = CharField(max_length=100)  #说明
    created = IntegerField(default=0)  #时间
    isactive = IntegerField(default=1)  #状态 0删除 1有效
    jftype = IntegerField()  #积分类别 0暂无 1兑换商品 2兑现 3卖保险获取
    orderNum = CharField() #订单号
    remark = CharField(max_length=256)  # 管理员备注

    class Meta:
        db_table = 'tb_score'
        order_by = ('-id',)

#余额历史表
class Balance(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='balances', db_column='user_id')
    stype = IntegerField()  #余额类型 0增加 1扣除
    balance = FloatField()  #钱数
    log = CharField(max_length=100)  #说明
    created = IntegerField(default=0)  #时间
    isactive = IntegerField(default=1)  #状态 0删除 1有效
    remark = CharField(max_length=256)  # 管理员备注

    class Meta:
        db_table = 'tb_balance'
        order_by = ('-id',)

#前端商品分类
class CategoryFront(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=20)     # 分类名
    code = CharField(max_length=20)     # 分类编码,访问url
    slug = CharField(max_length=20)     # 显示顺序
    metakeywords = CharField(max_length=128, default='')  # seo
    metadescription = CharField(max_length=128, default='')  # seo
    metatitle = CharField(max_length=128, default='')  # seo
    isactive = IntegerField(default=1)  # 状态 0删除 1有效
    has_sub = IntegerField(default=0)   # 是否拥有下级
    pid = IntegerField(default=0)   # 父级ID
    type = CharField(max_length=20)  # 分类类型 1汽车配件，2汽车服务
    img_m = CharField(max_length=256, null=True)  #分类图片手机端
    img_pc = CharField(max_length=256, null=True)  #分类图片PC端

    def validate(self):
        if self.name and self.slug:
            self.slug = self.slug.lower()
            if not re.match('^[0-9a-z]+$', self.code):
                raise Exception('访问目录只能是字母和数字组合')

            ft = ((CategoryFront.name == self.name) | (CategoryFront.code == self.code))
            if self.id:
                ft = ft & (CategoryFront.id != self.id)

            if CategoryFront.select().where(ft).count() > 0:
                raise Exception('分类同名或者目录同名')

        else:
            raise Exception('请输入分类名或者访问目录')

    class Meta:
        db_table = 'tb_category_front'


#后端商品分类
class CategoryBack(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=20)  #分类名
    slug = CharField(max_length=20)  #访问url
    isactive = IntegerField(default=1)  #状态 0删除 1有效

    def validate(self):
        if self.name and self.slug:
            self.slug = self.slug.lower()
            if not re.match('^[0-9a-z]+$', self.slug):
                raise Exception('访问目录只能是字母和数字组合')

            ft = ((CategoryBack.name == self.name) | (CategoryBack.slug == self.slug))
            if self.id:
                ft = ft & (CategoryBack.id != self.id)

            if CategoryBack.select().where(ft).count() > 0:
                raise Exception('分类同名或者目录同名')

        else:
            raise Exception('请输入分类名或者访问目录')

    class Meta:
        db_table = 'tb_category_back'

#商品属性
class Attribute(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=20)  #属性名称
    type = IntegerField(default=1)  #属性分类 1首页属性 2菜单属性
    isactive = IntegerField(default=1)  #状态 0删除 1有效

    class Meta:
        db_table = 'tb_attribute'

#品牌分类
class PinPaiType(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=20)  #属性名称
    flag = IntegerField(default=1)  #状态 0删除 1有效

    class Meta:
        db_table = 'tb_pinpai_type'

# 品牌分类的属性（所有商品属性）
class PPTAttribute(db_old.Model):
    id = PrimaryKeyField()
    PinPaiType = ForeignKeyField(PinPaiType, related_name='ppt_attribute', db_column='PinPaiType_id')
    name = CharField(max_length=20)  # 属性名称
    ename = CharField(max_length=16)  # 英语名

    class Meta:
        db_table = 'tb_ppt_attribute'

# 商品属性的量
class PPTAQuantity(db_old.Model):
    id = PrimaryKeyField()
    PPTA_id = ForeignKeyField(PPTAttribute, related_name='ppta_quantity', db_column='PPTA_id')
    name = CharField(max_length=20)  # 属性名称

    class Meta:
        db_table = 'tb_ppta_quantity'

# 商品品牌
class PinPai(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=50)     # 品牌名称
    engname = CharField(max_length=50)     # 品牌英文名称
    pinyin = CharField(max_length=50, null=True)   # 中文拼音
    logo = CharField(max_length=100, null=True)   # 品牌logo
    description = CharField(max_length=300, null=True)   # 说明
    ptype = ForeignKeyField(PinPaiType,  db_column='pinpai_type_id')  # 品牌分类
    intro = CharField(max_length=300, null=True)   # 品牌简介
    flag = IntegerField(default=1)

    class Meta:
        db_table = 'tb_pinpai'

#商品
class Product(db_old.Model):
    id = PrimaryKeyField()
    sku = CharField(max_length=64, unique=True, null=False)  # 商品sku
    name = CharField(max_length=64)  #商品名称
    brand_code = CharField(max_length=40)  # 年款code
    pinpai = ForeignKeyField(PinPai, related_name='pinpai_products',
                                    db_column='pinpai_id',null=True)  # 配件品牌分类
    categoryfront = ForeignKeyField(CategoryFront, related_name='products_front',
                                    db_column='category_front_id')  # 前端商品分类
    # categoryback = ForeignKeyField(CategoryBack, related_name='products_back', db_column='category_back_id')  # 后端商品分类
    resume = CharField()  # 简单介绍
    intro = TextField()  # 详细介绍
    prompt = TextField()  # 提示      空余字段 现用于购买须知
    args = TextField()  # A批发市场,B直采
    marketprice = FloatField()  # 市场价
    cover = CharField(max_length=128)  # 头图
    # quantity = FloatField(default=0.0)  # 数量 库存
    # producer = CharField(max_length=128)  # 产地
    # views = IntegerField(default=0)  # 点击率
    # orders = IntegerField(default=0)  # 购买次
    status = IntegerField(default=1)  # 0删除 1正常 2下架 在这下架表示用户再发布产品时候看不到这个产品了
    # defaultstandard = IntegerField(null=True)  # 默认规格id
    created = IntegerField(default=0)  # 添加时间
    metakeywords = CharField(max_length=128, default='')  # seo
    metadescription = CharField(max_length=128, default='')  # seo
    metatitle = CharField(max_length=128, default='')  # seo
    updatedtime = IntegerField(default=0)  # 更新时间
    updatedby = ForeignKeyField(AdminUser, related_name='lastupdatedproducts', db_column='updatedby', null=True)  #最后更新人
    attribute = ForeignKeyField(Attribute, related_name='product_attribute', db_column='attribute_id', null=True)  #商品属性
    is_index = IntegerField(default=0)  # 是否特殊商品 0普通 1保险 2板喷
    tags = CharField(max_length=128, null=True)  # 标签，使用‘,’分割多个
    is_score = IntegerField(default=0)

    # xgtotalnum = IntegerField(default=99999)  # 限购库存总数
    # xgperusernum = IntegerField(default=50)  # 限购每个用户,0为不限购
    # is_reserve = IntegerField(default=0)    # 是否预订商品 1预订商品  0非预订商品
    # reserve_time = IntegerField(default=0)  # 预订商品统一发货时间
    # is_score = IntegerField(default=0)      # 是否积分换购商品 1换购商品 0非换购商品
    # score_num = IntegerField(default=0)     # 积分换购所需积分
    # is_store = IntegerField(default=0)      # 是否为店铺特有商品 0平台 1店铺
    # store = ForeignKeyField(Store, related_name='belong_store', db_column='store_id')  #所属店铺
    # category_store = ForeignKeyField(Category_Store, related_name='products_store', db_column='category_store_id', null=True)  #店铺分类
    # avg_quantity = IntegerField(default=0)  # 日平均销售量，单位 件
    # weights = IntegerField(default=0)   # 权重 排序用，数值越大排在越前
    #
    # is_pass = IntegerField(default=0)   # 是否审核通过 0未审核 1通过 2不通过
    # user = ForeignKeyField(User, related_name='user_product', db_column='user_id')
    # comment_count = IntegerField(default=0)     # 评价数量
    # source_id = IntegerField(default=0)         # 来源产品ID，用于标识从哪个产品发布
    # is_recommend = IntegerField(default=0)      # 是否推荐商品 0否 1是  用于首页精品
    # is_bargain = IntegerField(default=0)        # 是否特价商品 0正常 1免费 2特价
    # service_time = IntegerField(default=0)      # 服务时间（分钟）

    class Meta:
        db_table = 'tb_product'
        order_by = ('-created',)


# 商品属性关联表
class ProductAttribute(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='product_attr', db_column='product_id')  #商品
    attribute = ForeignKeyField(Attribute, related_name='attribute_products', db_column='attribute_id')  #商品属性
    created = IntegerField(default=0)  # 创建时间
    sort = IntegerField(default=10000)  # 排序

    class Meta:
        db_table = 'tb_product_attribute'

# 商品附图
class ProductPic(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='pics', db_column='product_id')  #所属商品
    path = CharField(max_length=100)
    isactive = IntegerField(default=1)  #状态 0删除 1有效
    user = ForeignKeyField(User, db_column='user_id')

    class Meta:
        db_table = 'tb_product_pics'

# 商品评价
class Comment(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='product_comments', db_column='product_id')  # 所属商品
    user = ForeignKeyField(User, related_name='user_comments', db_column='user_id')
    store = ForeignKeyField(Store, related_name='store_comments', db_column='store_id')
    qualityscore = IntegerField(default=0)  # 质量得分
    speedscore = IntegerField(default=0)  # 发货速度得分
    pricescore = IntegerField(default=0)  # 价格得分
    servicescore = IntegerField(default=0)  # 服务得分
    comment = CharField(default='', max_length=1024)  # 评价内容
    created = IntegerField(default=0)  # 用户提交时间
    approvedby = ForeignKeyField(AdminUser, related_name='admin_approved_comments', db_column='admin_user_id')  # 审核通过管理员
    approvedtime = IntegerField(default=0)  # 审核时间
    status = IntegerField(default=1)  # 状态 0删除 1用户已提交，2 审核通过-前台显示，3拒绝-前台不显示
    reply_content = CharField(max_length=1024, default='')  # 门店回复
    reply_time = IntegerField(default=0)    # 回复时间

    class Meta:
        db_table = 'tb_comment'

#润滑油属性
class LubeAttribute(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='LA', db_column='product_id')  #所属商品
    level = CharField(max_length=16)  #级别
    classes = CharField(max_length=16)  #类别
    capacity = CharField(max_length=16) #容量
    viscosity = CharField(max_length=16)  #粘度
    class Meta:
        db_table = 'tb_lube_attribute'

#大屏导航仪属性
class NavigatorAttribute(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='NA', db_column='product_id')  #所属商品
    configuration = CharField(max_length=16)  #配置
    CAN = CharField(max_length=16)  #CAN
    size = CharField(max_length=16) #屏幕尺寸
    class Meta:
        db_table = 'tb_navigator_attribute'

#记录仪属性
class RecorderAttribute(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='RA', db_column='product_id')  #所属商品
    size = CharField(max_length=16) #屏幕尺寸
    lens = CharField(max_length=16)  #镜头
    class Meta:
        db_table = 'tb_recorder_attribute'


# 发布商品
class ProductStandard(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='standards', db_column='product_id')  #所属商品
    name = CharField(max_length=50)  #商品规格
    weight = FloatField()  #统计用每份重量
    price = FloatField()  #销售价（车主）
    orginalprice = FloatField()  #市场价格
    ourprice = FloatField()  #销售价（门店）
    relations = CharField(default='', max_length=255)  #关联规格列表
    # isactive = IntegerField(default=1)  #状态 0删除 1有效
    pf_price = FloatField(default=0)    # 批发价
    unit = CharField()    # 单位
    copies = CharField()    # 一份几桶
    # is_show = IntegerField(default=1)   # 是否在列表中显示，1显示 0不显示

    # 新增20160603 未更新到服务器*****************************
    city_id = IntegerField(default=0)  # 城市id
    area_code = CharField(max_length=40)  # 区域code
    quantity = IntegerField(default=0)  # 数量 库存
    views = IntegerField(default=0)  # 点击率
    orders = IntegerField(default=0)  # 购买次
    sale_status = IntegerField(default=1)  # 0删除 1正常 2下架
    xgtotalnum = IntegerField(default=99999)  # 限购库存总数
    xgperusernum = IntegerField(default=50)  # 限购每个用户,0为不限购
    store = ForeignKeyField(Store, related_name='belong_store', db_column='store_id')  #所属店铺
    avg_quantity = IntegerField(default=0)  # 日平均销售量，单位 件
    weights = IntegerField(default=0)   # 权重 排序用，数值越大排在越前
    is_pass = IntegerField(default=0)   # 平台是否审核通过 0未审核 1通过 2不通过
    user = ForeignKeyField(User, related_name='user_product', db_column='user_id')
    comment_count = IntegerField(default=0)     # 评价数量
    is_recommend = IntegerField(default=0)      # 是否推荐商品 0否 1是  用于首页精品
    is_bargain = IntegerField(default=0)        # 是否特价商品 0正常 1免费 2特价
    service_time = IntegerField(default=0)      # 服务时间（分钟）
    update_time = IntegerField(default=0)  # 更新时间
    update_user = CharField(max_length=40)  # 更新用户名
    add_time = IntegerField(default=0)  # 更新时间
    is_score = IntegerField(default=0)    #是否可以用积分兑换 0不可积分兑换 1可以兑换
    is_sale = IntegerField(default=1)  #是否在普通商品中展示  0不能用钱买， 1可以用钱买
    scoreNum = IntegerField(default=0)    #兑换该商品需要消耗多少积分

    def validate(self):
        if self.product and self.name and self.store:

            ft = ((ProductStandard.product == self.product) & (ProductStandard.name == self.name)& (ProductStandard.store == self.store))

            if self.id:
                ft = ft & (ProductStandard.id != self.id)

            if ProductStandard.select().where(ft).count() > 0:
                raise Exception('此规格已存在')
        else:
            raise Exception('请输入规格，价格或设置分类id')

    @classmethod
    def maxorder(cls, sid):
        return ProductStandard.select().where(ProductStandard.product.id == sid).count() + 1

    class Meta:
        db_table = 'tb_product_standard'

# 发布的商品在哪几个地区卖
class ReleaseArea(db_old.Model):
    id = PrimaryKeyField()
    pid = ForeignKeyField(Product)  # product id
    psid = ForeignKeyField(ProductStandard)  # product standard id
    area_code = CharField(max_length=40)  # 区域code
    price = FloatField(default=0)  # 销售价
    quantity = IntegerField(default=0)  # 库存
    class Meta:
        db_table = 'tb_product_release_area'

# 店铺入库表
class In_Store(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='product_in', db_column='product_id')  # 所属商品
    quantity = FloatField(default=0)  # 入库量（斤） 净重
    price = FloatField(default=0)   # 费用（元）
    unitprice = FloatField(default=0)  # 折合每斤花费/单价（元）
    addtime = IntegerField(default=0)  # 采购时间
    created = IntegerField(default=0)  # 入库时间
    store = ForeignKeyField(Store, db_column='store_id', null=True)  #所属店铺

    class Meta:
        db_table = 'tb_in_store'

# 店铺价格表
class StorePrice(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, db_column='product_id')  # 所属商品
    product_standard = ForeignKeyField(ProductStandard, related_name='store_price', db_column='product_standard_id')  # 所属商品规格
    store = ForeignKeyField(Store, db_column='store_id')  # 所属店铺
    price = FloatField(default=0)   # 价格(元/千克)
    last_update_time = IntegerField(default=0)  # 采购时间
    last_user_id = IntegerField(default=0) # 最后修改用户

    class Meta:
        db_table = 'tb_store_price'

# 店铺库存表
class Inventory_Store(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='is_products', db_column='product_id')  #所属商品
    product_standard = ForeignKeyField(ProductStandard, related_name='is_product_standard', db_column='product_standard_id')  #商品规格
    quantity = FloatField(default=0)    # 库存数量
    price = FloatField()  #每份价格
    perprice = FloatField()  #每斤价格
    store = ForeignKeyField(Store, db_column='store_id', null=True)  #所属店铺
    last_time = IntegerField(default=0)  # 最后修改时间

    class Meta:
        db_table = 'tb_inventory_store'

# 进销存表
class Invoicing(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='product', db_column='product_id')  # 所属商品
    type = IntegerField(default=0)  # 0入库，1出库
    quantity = FloatField(default=0)  # 入库/出库量（斤） 净重
    price = FloatField(default=0)  # 采购价格（元）
    unitprice = FloatField(default=0)  # 折合每斤花费/单价（元）
    addtime = IntegerField(default=0)  # 采购时间
    created = IntegerField(default=0)  # 入库/出库时间
    buyer = CharField(max_length=10)  # 采购员
    args = CharField(max_length=20)  # A批发市场,B直采
    status = IntegerField(default=0)  # 0正常,1删除,-1待入库，-2退货
    gross_weight = FloatField(default=0)  # 入库量（斤） 毛重

    class Meta:
        db_table = 'tb_invoicing'

# 进销存表
class InvoicingChanged(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='invocing_changed', db_column='product_id')  #所属商品
    last_invoicing = ForeignKeyField(Invoicing, related_name='invocing_changed1', db_column='last_invoicing_id')  #上次入库记录
    current_invoicing = ForeignKeyField(Invoicing, related_name='invocing_changed2', db_column='current_invoicing_id')  #本次入库记录
    last_unitprice = FloatField(default=0)  #上次入库每斤花费/单价（元）
    current_unitprice = FloatField(default=0)  #本次入库每斤花费/单价（元）

    class Meta:
        db_table = 'tb_invoicing_changed'

# 线下商品
class ProductOffline(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, db_column='product_id')  # 所属商品
    store = ForeignKeyField(Store, db_column='store_id', null=True)  # 所属店铺
    barcode = CharField(unique=True, max_length=64, default='')  # 条码
    status = IntegerField(default=0)        # 状态 0标准化完成; 1出仓库; 2入门店; 3售出; 4退回; 5耗损; 6购物车;
    weight = FloatField(default=0)          # 商品重量
    price = FloatField(default=0)           # 商品价格（份）
    out_time = IntegerField(default=0)      # 出仓库时间
    in_time = IntegerField(default=0)       # 入门店时间
    sale_time = IntegerField(default=0)     # 售出时间
    cancel_reason = CharField(default='', max_length=1024)  # 取消原因
    cancel_time = IntegerField(default=0)   # 取消时间
    class Meta:
        db_table = 'tb_product_offline'

# 购物车
class Cart(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='cartitems', db_column='user_id')
    product = ForeignKeyField(Product, db_column='product_id')  # 所属商品
    product_standard = ForeignKeyField(ProductStandard, db_column='product_standard_id')  # 商品规格
    quantity = IntegerField(default=0)  # 数量
    type = IntegerField(default=0)      # 商品类型 0默认 1实物卷商品,礼品，赠品，积分换购   2订购商品 3线下商品
    product_offline = ForeignKeyField(ProductOffline, related_name='cart_offline',db_column='offline_id', null=True)   # 线下订单ID
    created = IntegerField(default=0)   # 创建时间 即加入购物车时间
    class Meta:
        db_table = 'tb_cart'

#优惠券总表
class CouponTotal(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=20)  #优惠劵名称
    price = FloatField(default=0.0)  #价格
    minprice = FloatField(default=0.0)  #满多少可以使用的条件
    starttime = IntegerField(default=0)  # 有效期开始
    endtime = IntegerField(default=0)  # 有效期结束
    total = IntegerField(default=0)  #总量
    quantity = IntegerField(default=0)  #已发送数量
    used = IntegerField(default=0)  #已使用
    createby = CharField(max_length=20)  #发行者
    createtime = IntegerField(default=0)  # 发行时间
    status = IntegerField(default=0)  #0启用 1禁用

    class Meta:
        db_table = 'tb_coupontotal'

#优惠劵
class Coupon(db_old.Model):
    id = PrimaryKeyField()
    code = CharField(max_length=32)  #优惠劵编码
    user = ForeignKeyField(User, related_name='coupons', db_column='user_id', null=True)  #用户
    coupontotal = ForeignKeyField(CouponTotal, related_name='coupons_c', db_column='coupontotal_id')  #优惠劵类别
    status = IntegerField(default=0)  # 0有效，1已指派,2已使用
    starttime = IntegerField(default=0)  # 有效期开始
    endtime = IntegerField(default=0)  # 有效期结束
    log = CharField(max_length=64)   # 获取方式及其他信息
    class Meta:
        db_table = 'tb_coupon'

#实物优惠券类别
class CouponRealTotal(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=32)         # 优惠券名称
    product = ForeignKeyField(Product, db_column='product_id')  # 对应商品
    product_standard = ForeignKeyField(ProductStandard, db_column='product_standard_id')  # 商品规格
    quantity = IntegerField(default=0)      # 已发数量
    used = IntegerField(default=0)          # 已使用数量
    createby = CharField(max_length=32)     # 创建人
    createtime = IntegerField(default=0)    # 创建时间
    status = IntegerField(default=0)        # 0启用 1禁用

    class Meta:
        db_table = 'tb_coupon_real_total'

#实物优惠券
class CouponReal(db_old.Model):
    id = PrimaryKeyField()
    code = CharField(max_length=32)     #优惠券码
    user = ForeignKeyField(User, related_name='coupon_real', db_column='user_id', null=True)  #用户
    coupon_real_total = ForeignKeyField(CouponRealTotal, related_name='coupon_real_c', db_column='coupon_real_total_id')  #优惠劵类别
    status = IntegerField(default=0)  # 0有效，1已指派,2已使用
    starttime = IntegerField(default=0)  # 有效期开始
    endtime = IntegerField(default=0)  # 有效期结束
    createby = CharField(max_length=32)     # 创建人
    createtime = IntegerField(default=0)    # 创建时间

    class Meta:
        db_table = 'tb_coupon_real'

#结算表
class Settlement(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='settlements', db_column='user_id')  # 用户
    sum_money = FloatField(default=0.0)  # 订单总金额
    created = IntegerField(default=0)  # 结算时间

    class Meta:
        db_table = 'tb_settlement'

#提现表
class Withdraw(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='withdraws', db_column='user_id')  # 用户
    account_type = IntegerField(default=0)  # 提现账户类型 0银行卡 1支付宝
    account_truename = CharField(max_length=32, default='')  # 银行卡姓名
    account_name = CharField(max_length=64, default='')  # 银行名称
    account_branchname = CharField(max_length=64, default='')  # 支行名称
    account_account = CharField(max_length=32, default='')  # 银行卡号
    sum_money = FloatField(default=0.0)  # 提现金额
    status = IntegerField(default=0)  # 处理状态
    apply_time = IntegerField(default=0)  # 申请时间
    processing_time = IntegerField(default=0)  # 处理时间
    processing_by = ForeignKeyField(AdminUser, db_column='updated_by', null=True)  # 处理人
    processing_result = CharField(max_length=64, default='')  # 处理结果

    class Meta:
        db_table = 'tb_withdraw'
    # def checkBank(self):
    #     banks = [u'']
    #     if self.account_account.isdigit():

#订单
class Order(db_old.Model):
    id = PrimaryKeyField()
    ordernum = CharField(max_length=64, null=True)  #订单号
    user = ForeignKeyField(User, related_name='orders', db_column='user_id')  #买家
    address = ForeignKeyField(UserAddr, db_column='user_address_id')  #收信地址
    distribution = IntegerField(default=1)  #送货方式 1物流公司送货  2我公司自己送  3用户自己来取
    delivery = ForeignKeyField(Delivery, related_name='orders', db_column='delivery_id', null=True)  #物流公司
    deliverynum = CharField(max_length=64, null=True)  #物流单号
    distributiontime = CharField(max_length=24, null=True)  #配送时间
    payment = IntegerField(default=1)  # 付款方式 0货到付款  1支付宝  2账户余额 3网银支付,5积分换购, 6微信 7银联 9补单（4手机合并余额与支付宝，5手机合并余额与货到付款）
    message = CharField(null=True)  # 付款留言
    isinvoice = IntegerField(default=0)  # 是否开发票
    invoicesub = IntegerField(default=0)  # 发票抬头 0个人 1公司
    invoicename = CharField(max_length=80, null=True)  # 个人或公司名称
    invoicecontent = IntegerField(default=1)  # 发票类型 0蔬菜 1食水果
    shippingprice = FloatField(default=0.0)  # 配送价格
    price = FloatField(default=0.0)  # 价格
    currentprice = FloatField(default=0.0)  # 实际订单价格
    status = IntegerField(default=0)  # 0待付款 1已付款 2待发货 3已发货 4交易完成 5已取消,-1已删除
    hascomment = IntegerField(default=0)  # 0未评价 1已评价
    needpayback = IntegerField(default=0)  # 0不用退款 1需退款
    cancelreason = CharField(default='', max_length=1024)  # 取消原因
    canceltime = IntegerField(default=0)  #取消时间
    ip = CharField(max_length=80, null=True)  #来源IP
    ordered = IntegerField(default=0)  #下单时间
    ordereddate = CharField(max_length=16)  #下单日期，文本格式
    orderedtime = CharField(max_length=16)  #下单时间，文本格式
    flag = IntegerField(default=0)  #管理员标签
    summary = CharField(max_length=256, null=True)  #管理员备注
    exportpdf = IntegerField(default=0)  #是否导出到PDF
    lasteditedby = CharField(max_length=64, null=True)  #  #最后修改订单的管理员姓名
    lasteditedtime = IntegerField(default=0)  #修改订单的时间
    paytime = IntegerField(default=0)  # 支付时间
    coupon = ForeignKeyField(Coupon, related_name='orders', db_column='coupon_id', null=True)  #优惠卷
    freight = FloatField(default=0.0)  #实际运费
    weight = FloatField(default=0.0)  #订单重量
    take_name = CharField(default=10, null=True)  #收件人姓名
    take_tel = CharField(default=20, null=True)  #收件人联系电话
    take_address = CharField(default=100, null=True)  #收货地址
    order_from = IntegerField(default=1)  # 1 网站下单，2手机下单，3后台下单
    pay_from = IntegerField(default=1)  # 1 网站支付，2手机支付
    pay_account = CharField(max_length=128, default='')  # 用户支付宝账户or微信支付用户openid or银联支付商户代码
    trade_no = CharField(max_length=64, default='')  # 支付宝交易号or微信支付订单号or银联支付查询流水号
    pay_response = CharField(max_length=4096, default='')  # 支付宝反馈信息汇总
    pay_balance = FloatField(default=0.0)  # 余额支付金额
    delivery_time = IntegerField(default=0)  # 发货时间
    order_type = IntegerField(default=0)    # 订单类型 0普通订单，1预售订单
    store = ForeignKeyField(Store, db_column='store_id', null=True)  #所属店铺
    kdy_name = CharField(max_length=64, default='')     # 快递员姓名
    kdy_mobile = CharField(max_length=64, default='')   # 快递员电话号码
    settlement = ForeignKeyField(Settlement, related_name='settlement_orders', db_column='settlement_id', null=True)  # 完成的订单才可以结算
    agent = ForeignKeyField(Store, related_name='agent_store', db_column='agent_store_id', null=True)  #指定代理商店铺ID
    is_score = IntegerField(default=0)    #是否可以用积分兑换 0雅蠛蝶 1可以兑换
    scoreNum = IntegerField(default=0)    #兑换该商品需要消耗多少积分
    userDel = IntegerField(default=0) #仅用户端删除已经完成的商品


    def change_status(self, status):  #管理员操作时status可能的值：2正在处理 3已发货 4交易完成 5已取消,-1已删除；用户操作时可能的值：5已取消,-1已删除
        if self.status == status:
            return
        if self.status == -1:
            raise Exception('此订单已被删除，不能做任何操作')
        if status == 5:  #取消订单
            if 1 < self.status < 5:
                raise Exception('订单已经处理，不能取消')
            self.status = 5
            self.canceltime = int(time.time())
        elif status == -1:  #删除订单
            if self.status == 5:  #已经取消的订单可以删除
                self.status = -1
            else:
                raise Exception('不能删除没有取消的订单，或者改订单还没有退款')
        elif status == 2:  #标记订单为正在处理
            if self.status == 1 or (self.status == 0 and self.payment == 0):
                self.status = 2
            else:
                raise Exception('用户未付款，或订单已经进入下一环节')
        elif status == 3:  #标记订单到物流公司
            if self.status == 2:
                self.status = 3
            else:
                raise Exception('未先将订单标记为正在处理，或订单已经进入下一环节')
        elif status == 4:  # 订单已经配送到户，标记为完成
            if self.status == 3:
                self.status = 4
            else:
                raise Exception('未先将订单标记为交给物流，或订单已经进入下一环节')

    def containAny(self, seq, aset):
        for c in seq:
            if c in aset:
                return True
        return False

    class Meta:
        db_table = 'tb_orders'

#保险种类
class Insurances(db_old.Model):
    id = PrimaryKeyField()
    eName = CharField(max_length=32, default='')
    name = CharField(max_length=32, default='')
    style = CharField(max_length=32, default='')
    sort = IntegerField()
    class Meta:
        db_table = 'tb_insurances'

class InsurancePrice(db_old.Model):
    id = PrimaryKeyField()
    pid = ForeignKeyField(Insurances, db_column='pid', null=True)
    name = CharField(default='零')
    class Meta:
        db_table = 'tb_insurance_price'

#保险订单
class InsuranceOrder(db_old.Model):
    id = PrimaryKeyField()
    ordernum = CharField(max_length=64, null=True)  #订单号
    user = ForeignKeyField(User, related_name='insurance_orders', db_column='user_id')  #用户
    store = ForeignKeyField(Store, related_name='insurance_orders', db_column='store_id', null=True)  #店铺
    insurance = ForeignKeyField(Product, db_column='product_id')  #所购保险
    idcard = CharField(max_length=255, null=True)   # 身份证
    idcardback = CharField(max_length=255, null=True)   # 身份证背面
    drivercard = CharField(max_length=255, null=True)   # 行驶证
    drivercard2 = CharField(max_length=255, null=True)  # 行驶证副本
    ordertype = IntegerField(default=1)  # 订单类型  1保险订单  2钣喷订单
    payment = IntegerField(default=1)  # 付款方式 0货到付款  1支付宝  2账户余额 3网银支付,5积分换购 6微信支付 7银联
    contact = CharField(null=True)  # 联系人
    mobile = CharField(null=True)  # 用户电话
    message = CharField(null=True)  # 客户留言
    price = FloatField(default=0.0)  # 价格
    forceIprc = FloatField(default=0.0)  # 交强险 价格forceIprc businessIprc vehicleTax
    businessIprc = FloatField(default=0.0)  # 商业险价格
    vehicleTax = FloatField(default=0.0)  # 车船税价格

    status = IntegerField(default=0)  # 0待确认 1待付款 2付款完成 3已办理 5已取消 -1已删除
    cancelreason = CharField(default='', max_length=1024)  # 取消原因
    canceltime = IntegerField(default=0)  #取消时间
    ordered = IntegerField(default=0)  #下单时间
    ordereddate = CharField(max_length=16)  #下单日期，文本格式
    orderedtime = CharField(max_length=16)  #下单时间，文本格式
    summary = CharField(max_length=1024, null=True)  #管理员备注
    localsummary = CharField(max_length=256, null=True)  #本地备注
    lasteditedby = CharField(max_length=64, null=True)  #  #最后修改订单的管理员姓名
    lasteditedtime = IntegerField(default=0)  #修改订单的时间
    paytime = IntegerField(default=0)  #支付时间
    pay_from = IntegerField(default=1)  # 1 网站支付，2手机支付
    pay_account = CharField(max_length=128, default='')  # 用户支付宝账户
    trade_no = CharField(max_length=64, default='')  # 支付宝交易号
    pay_response = CharField(max_length=4096, default='')  # 支付宝反馈信息汇总
    #forceI  ;
    # damageI thirdDutyI  robbingI damageSpecialI thirdDutySpecialI robbingSpecialI  ;
    # driverDutyI thirdDutySpecialI, passengerDutyI passengerDutySpecialI,    glassI, specialI
    # scratchI scratchSpecialI, normalDamageI normalDamageSpecialI,  wadeI wadeSpecialI,  thirdSpecialI thirdSpecialSpecialI
    forceI = CharField(max_length=32, default='')  #交强险
    damageI = CharField(max_length=32, default='')  #车辆损失险
    thirdDutyI = CharField(max_length=32, default='')#第三者责任险
    robbingI = CharField(max_length=32, default='')#机动车全车盗抢险
    driverDutyI = CharField(max_length=32, default='')#机动车车上人员责任险（司机）
    passengerDutyI = CharField(max_length=32, default='')#机动车车上人员责任险（乘客）
    glassI = CharField(max_length=32, default='')#玻璃单独破碎险
    scratchI = CharField(max_length=32, default='')#车身划痕损失险
    normalDamageI = CharField(max_length=32, default='')#自然损失险
    wadeI = CharField(max_length=32, default='')#发动机涉水损失险
    specialI = CharField(max_length=32, default='')    #不计免赔特约险
    thirdSpecialI = CharField(max_length=32, default='')#机动车损失保险无法找到第三方特约险

    damageSpecialI = CharField(max_length=32, default='')
    thirdDutySpecialI = CharField(max_length=32, default='')
    robbingSpecialI = CharField(max_length=32, default='')
    driverDutySpecialI = CharField(max_length=32, default='')
    passengerDutySpecialI = CharField(max_length=32, default='')
    scratchSpecialI = CharField(max_length=32, default='')
    normalDamageSpecialI = CharField(max_length=32, default='')
    wadeSpecialI = CharField(max_length=32, default='')
    thirdSpecialSpecialI = CharField(max_length=32, default='')

    LubeOrScore = IntegerField(default=0)  # 0 1反油， 2反积分
    userDel = IntegerField(default=0) #用户端不显示
    scoreNum = IntegerField(default=0)    #卖的这单保险可以获取多少积分
    profit = FloatField(default=0)    #卖的这单保险可以获取多少利润
    deadline = IntegerField(default=0) #期限

    def change_status(self, status):
        if self.status == status:
            return
        if self.status == -1:
            raise Exception('此订单已被删除，不能做任何操作')
        if status == 5:  #取消订单
            if self.status == 3:
                raise Exception('该保险订单已经办理，不能取消')
            self.status = 5
            self.canceltime = int(time.time())
        elif status == -1:  #删除订单
            if self.status == 5:  #已经取消的订单可以删除
                self.status = -1
            else:
                raise Exception('不能删除没有取消的订单，或者该订单还没有退款')
        elif status == 1:  #标记订单为等待付款
            if self.status == 3:
                raise Exception('该保险订单已经办理，不能标记为待付款')
            else:
                self.status = 1
        elif status == 2:  #付款完成
            self.status = 2

        elif status == 3:  # 办理完成
            if self.status == 2:
                self.status = 3
            else:
                raise Exception('该订单未付款，还不能办理')

    class Meta:
        db_table = 'tb_insurance_orders'

# 保险订单收货信息
class InsuranceOrderReceiving(db_old.Model):
    id = PrimaryKeyField()
    orderid = ForeignKeyField(InsuranceOrder, related_name='i_order_id',
                              db_column='orderid')  # 外键到user表，字段名为user_id，从user引用为addresses
    contact = CharField(max_length=16, null=True)  # 联系人
    mobile = CharField(max_length=11, null=True)  # 手机号码
    address = CharField(max_length=128, default='')  # 省市区
    paddress = CharField(max_length=128, null=True)  # 详细地址
    isdefault = IntegerField(default=0)  # 是否默认 0否 1是

    class Meta:
        db_table = 'tb_insurance_order_receiving'

# 钣喷订单中的图片
class InsuranceOrderImg(db_old.Model):
    id = PrimaryKeyField()
    order = ForeignKeyField(InsuranceOrder, related_name='imgs', db_column='order_id')  #所属保险订单
    name = CharField(max_length=64)  # 图片名称
    imgtype = IntegerField(default=1)  # 1车身受损情况 2保险单

    class Meta:
        db_table = 'tb_insurance_order_img'

#合并订单信息
class GroupOrder(db_old.Model):
    id = PrimaryKeyField()
    order = ForeignKeyField(Order, related_name='group_orders', db_column='order_id')  #所属订单
    name = CharField(max_length=64)  #订单组名称

    class Meta:
        db_table = 'tb_group_orders'

#订单内容
class OrderItem(db_old.Model):
    id = PrimaryKeyField()
    order = ForeignKeyField(Order, related_name='items', db_column='order_id')  #所属订单
    product = ForeignKeyField(Product, related_name='order_items', db_column='product_id')  #所属商品
    product_standard = ForeignKeyField(ProductStandard, db_column='product_standard_id')  #商品规格
    quantity = IntegerField(default=0)  #数量
    price = FloatField(default=0)  #购买时产品价格
    weight = FloatField(default=0)  #商品重量
    hascomment = IntegerField(default=0)  # 0未评价 1已评价
    product_standard_name = CharField(max_length=64)  #产品规格
    item_type = IntegerField(default=0)  # 0普通商品，1秒杀商品，2积分换购，3实物卷商品，4转盘抽奖，5预售商品，9系统赠送
    product_offline = ForeignKeyField(ProductOffline, related_name='product_offline', db_column='product_offline_id', null=True)   # 线下订单ID

    class Meta:
        db_table = 'tb_order_items'

# 订单服务
class OrderItemService(db_old.Model):
    id = PrimaryKeyField()
    order_item = ForeignKeyField(OrderItem, related_name='order_item_service', db_column='order_item_id')  # 所属单品
    store = ForeignKeyField(Store, related_name='store_order_item_services', db_column='store_id')  # 所属门店
    sn = IntegerField(default=1)                # 顺序号
    service_code = CharField(max_length=32)     # 服务码
    service_used = IntegerField(default=0)      # 服务码是否使用 0 未使用，1 已使用
    used_time = IntegerField(default=0)      # 使用时间
    used_year = CharField(max_length=32)     # 使用年
    used_month = CharField(max_length=32)     # 使用月
    used_day = CharField(max_length=32)     # 使用日
    user = ForeignKeyField(User, related_name='item_service_user', db_column='user_id')  # 用户
    reserve_time = IntegerField(default=0, null=True)      # 预约时间

    class Meta:
        db_table = 'tb_order_item_service'

# 退款信息
class PayBack(db_old.Model):
    id = PrimaryKeyField()
    order = ForeignKeyField(Order, related_name='paybacks', db_column='order_id')  # 所属订单
    user = ForeignKeyField(User, related_name='user_paybacks', db_column='user_id')  # 所属订单
    price = FloatField(default=0)  # 退款金额
    trade_no = CharField(max_length=128, default='')  # 支付宝交易流水号
    batch_no = CharField(max_length=64, default='')  # 退款批次号
    pay_account = CharField(max_length=128, default='')  # 用户支付宝账户
    pay_response = CharField(max_length=4096, default='')  # 支付宝退款反馈信息汇总
    createdby = CharField(max_length=64, default='') # 创建人
    createdtime = IntegerField(default=0)  # 创建时间
    paybackby = CharField(max_length=64, default='') # 退款人
    paybacktime = IntegerField(default=0)  # 退款时间
    status = IntegerField(default=0)  # 0等待退款 1退款成功 2退款失败 -1取消退款请求
    reason = CharField(max_length=2048, default='')  # 退款原因
    back_by = IntegerField(default=1)  # 1管理员退款 2用户退款

    class Meta:
        db_table = 'tb_payback'

# 静态页面
class Page(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=20)
    title = CharField(max_length=64)        # 标题
    slug = CharField(index=True, max_length=20)  #访问路径
    content = TextField(default='')  # 页面内容
    template = CharField(max_length=20, default='staticpage.html')
    metakeywords = CharField(max_length=128, default='')  # seo
    metadescription = CharField(max_length=128, default='')  # seo
    metatitle = CharField(max_length=128, default='')  # seo
    updatedtime = IntegerField(default=0)  # 更新时间
    updatedby = ForeignKeyField(AdminUser, db_column='updated_by')  #最后更新人
    isactive = IntegerField(default=1)  # 状态 0删除 1有效

    def validate(self):
        if self.name and self.slug:
            self.slug = self.slug.lower()
            if not re.match('^[0-9a-z]+$', self.slug):
                raise Exception('访问目录只能是字母和数字组合')

            ft = ((Page.name == self.name) | (Page.slug == self.slug))
            if self.id:
                ft = ft & (Page.id != self.id)

            if Page.select().where(ft).count() > 0:
                raise Exception('访问路径同名')
        else:
            raise Exception('请输入分类名或者访问目录')

    class Meta:
        db_table = 'tb_pages'

#用户收藏产品表
class Fav(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='fav_users')
    product_standard = ForeignKeyField(ProductStandard, related_name='fav_products')  #商品
    favtime = IntegerField(default=0)  #收藏时间

    class Meta:
        db_table = 'tb_user_fav_products'

#用户收藏门店表
class FavStore(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='user_fav_stores')
    store = ForeignKeyField(Store, related_name='fav_stores')  # 门店
    favtime = IntegerField(default=0)  #收藏时间

    class Meta:
        db_table = 'tb_user_fav_stores'

#角色
class Role(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=16, default='c')  # 角色名: c顾客，admin超级管理员，cg采购，dd订单管理员，kf客服，

    class Meta:
        db_table = 'tb_role'

#管理员操作日志
class AdminLog(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(AdminUser, related_name='logs', db_column='admin_user_id')  #该操作的管理员
    dotime = IntegerField(default=0)  # 操作时间
    content = TextField(default='')  #操作内容

    class Meta:
        db_table = 'tb_admin_log'

# 首页管理
class PageBlock(db_old.Model):
    id = PrimaryKeyField()
    key = CharField(max_length=64, default='')  #首页区域关键字:fmenu,fsubmenu,vmenu,vsubmenu
    name = CharField(max_length=64, default='')  #首页区域名称:menu,summenu,fruit,vegetable
    content = CharField(max_length=8192, default='')  #页面内容
    type = IntegerField(default=0)  #块类型：0表示html代码，1表示存储的productid集合
    updatedtime = IntegerField(default=0)  #更新时间
    updatedby = ForeignKeyField(AdminUser, db_column='updated_by')  #最后更新人

    class Meta:
        db_table = 'tb_page_block'

#咨询售后
class Consult(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='consult_user', db_column='user_id')
    type = CharField(max_length=128, default='')  #咨询问题类型
    content = CharField(max_length=1024, default='')  #咨询问题内容
    contact = CharField(max_length=64, default='')  #联系人
    mobile = CharField(max_length=20, default='')  #联系电话
    created = IntegerField(default=0)  #提交时间
    reply_content = CharField(max_length=1024, default='')  #回复内容
    reply_time = IntegerField(default=0)  #回复时间
    order = CharField(max_length=20, default='')  #订单号
    isactive = IntegerField(default=1)  #状态 0删除 1未回复 2已回复
    isreceived = IntegerField(default=0)  #是否收到商品 0未收到  1收到

    class Meta:
        db_table = 'tb_consult'

#意见反馈
class Feedback(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, db_column='user_id')
    type = CharField(max_length=128, default='')  # 意见反馈类型
    content = CharField(max_length=1024, default='')  # 意见反馈内容
    contact = CharField(max_length=64, default='')  # 联系人
    mobile = CharField(max_length=20, default='')  # 联系电话
    created = IntegerField(default=0)  # 提交时间
    reply_content = CharField(max_length=1024, default='')  # 回复内容
    reply_time = IntegerField(default=0)  # 回复时间
    has_read = IntegerField(default=0)  # 块类型：0表示未读，1表示已读

    class Meta:
        db_table = 'tb_feedback'

#问答提问表
class Question(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, db_column='user_id') # 提问用户ID
    title = CharField(max_length=128, default='')  # 标题
    content = CharField(max_length=1024, default='')  # 内容
    scores = IntegerField(default=0)  # 悬赏分数
    clicks = IntegerField(default=0)  # 浏览次数
    answers = IntegerField(default=0)  # 回答次数
    publish_from = CharField(max_length=20, default='')  # 发布自哪里(手机，bs...)
    check_status = IntegerField(default=0)  # 审核状态：0未审核，1通过，2未通过
    is_recommend = IntegerField(default=0)  # 是否推荐：0否，1是
    is_anonymous = IntegerField(default=0)  # 是否匿名：0否，1是
    is_finish = IntegerField(default=0)  # 是否结束：0否，1是
    is_delete = IntegerField(default=0)  # 是否删除：0否，1是
    created = IntegerField(default=0)  # 提交时间

    class Meta:
        db_table = 'tb_ask_question'

#问答提问图片表
class QuestionPic(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, db_column='user_id') # 回答用户ID
    question = ForeignKeyField(Question, related_name="question_pics", db_column='question_id', null=True)
    path = CharField(max_length=200, default='')  # 图片地址
    created = IntegerField(default=0)  # 提交时间

    class Meta:
        db_table = 'tb_ask_question_pic'

#问答回答表
class Answer(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, db_column='user_id',related_name="user_id") # 回答用户ID
    question = ForeignKeyField(Question, db_column='question_id',related_name="question_id")
    content = CharField(max_length=1024, default='')  # 内容
    opposes = IntegerField(default=0)  # 反对数
    supports = IntegerField(default=0)  # 支持数
    need_money = FloatField(default=0)  # 预估金额
    publish_from = CharField(max_length=20, default='')  # 发布自哪里(手机，bs...)
    is_best = IntegerField(default=0)  # 是否最佳：0否，1是
    is_anonymous = IntegerField(default=0)  # 是否匿名：0否，1是
    is_delete = IntegerField(default=0)  # 是否删除：0否，1是
    created = IntegerField(default=0)  # 提交时间

    class Meta:
        db_table = 'tb_ask_answer'

#用户过得赞同的问题
class SupportAnswer(db_old.Model):
    id = PrimaryKeyField()
    answer = ForeignKeyField(Answer, db_column='answer_id',related_name="answer_id")
    created = IntegerField(default=0)  # 提交时间
    user = ForeignKeyField(Answer, db_column='user_id',related_name="user_id")

    class Meta:
        db_table = 'tb_user_support_answer'

#圈子话题主表
class CircleTopic(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, db_column='user_id') # 提问用户ID
    title = CharField(max_length=128, default='')  # 标题
    content = CharField(max_length=1024, default='')  # 内容
    clicks = IntegerField(default=0)  # 浏览次数
    publish_from = CharField(max_length=20, default='')  # 发布自哪里(手机，bs...)
    check_status = IntegerField(default=0)  # 审核状态：0未审核，1通过，2未通过
    is_show_address = IntegerField(default=0)  # 是否显示地址：0否，1是
    is_show_contact = IntegerField(default=0)  # 是否显示联系方式：0否，1是
    is_delete = IntegerField(default=0)  # 是否删除：0否，1是
    created = IntegerField(default=0)  # 提交时间

    class Meta:
        db_table = 'tb_circle_topic'

#圈子话题图片表
class CircleTopicPic(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, db_column='user_id') # 回答用户ID
    topic = ForeignKeyField(CircleTopic, related_name="topic_pics", db_column='topic_id', null=True)
    path = CharField(max_length=200, default='')  # 图片地址
    created = IntegerField(default=0)  # 提交时间

    class Meta:
        db_table = 'tb_circle_topic_pic'

#圈子话题回复表
class CircleTopicReply(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, db_column='user_id') # 回答用户ID
    replied_user = ForeignKeyField(User, related_name="replied_user", db_column='replied_user_id',  null=True) # 被回复的User ID
    topic = ForeignKeyField(CircleTopic, related_name="topic_replies", db_column='topic_id')
    content = CharField(max_length=1024, default='')  # 内容
    publish_from = CharField(max_length=20, default='')  # 发布自哪里(手机，bs...)
    is_delete = IntegerField(default=0)  # 是否删除：0否，1是
    created = IntegerField(default=0)  # 提交时间


    class Meta:
        db_table = 'tb_circle_topic_reply'

#圈子话题点赞表
class CircleTopicPraise(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, db_column='user_id') # 点赞用户ID
    topic = ForeignKeyField(CircleTopic, related_name="topic_praises", db_column='topic_id')
    publish_from = CharField(max_length=20, default='')  # 发布自哪里(手机，bs...)
    created = IntegerField(default=0)  # 提交时间

    class Meta:
        db_table = 'tb_circle_topic_praise'

class MobileBlock(db_old.Model):
    id = PrimaryKeyField()
    key = CharField(max_length=64, default='')  # 首页区域关键字:f,v
    name = CharField(max_length=64, default='')  # 首页区域名称:水果,蔬菜
    content = CharField(max_length=1024, default='')  # 页面内容
    updatedtime = IntegerField(default=0)  # 更新时间
    updatedby = ForeignKeyField(AdminUser, db_column='updated_by')  # 最后更新人

    class Meta:
        db_table = 'tb_mobile_block'

class MobileUpdate(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=64, default='')  # 版本名称
    version = CharField(max_length=64, default='')  # 版本号
    path = CharField(max_length=64, default='')  # 版本文件路径
    client = CharField(max_length=64, default='')  # 客户端类型 android ios
    state = IntegerField(default=0)  # 版本是否可用0不可以用，1可以
    updatedtime = IntegerField(default=0)  # 更新时间
    updatedby = ForeignKeyField(AdminUser, db_column='updated_by')  # 最后更新人
    isForce = CharField(max_length=8, default='false')  # 强制更新
    instructions = CharField(max_length=256)  # 强制更新

    class Meta:
        db_table = 'tb_mobile_update'

#库存盘点明细
class Inventory(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='in_product', db_column='product_id')  #商品
    original_weight = FloatField(default=0)  #原库存量
    weight = FloatField(default=0)  #盘点后库存量
    current_total_weight = FloatField(default=0)  #当前总采购量
    loss = FloatField(default=0)  #损耗率 = 总损耗量/总采购量
    updatedtime = IntegerField(default=0)  #更新时间
    updatedby = ForeignKeyField(AdminUser, db_column='updatedby')  #最后更新人

    class Meta:
        db_table = 'tb_inventory'

# 赠品/补发产品
class Gift(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='giftitems', db_column='user_id')
    product = ForeignKeyField(Product, db_column='product_id')  # 所属商品
    product_standard = ForeignKeyField(ProductStandard, db_column='product_standard_id')  # 商品规格
    quantity = IntegerField(default=0)  # 数量
    created = IntegerField(default=0)  # 创建时间/开始时间
    created_by = ForeignKeyField(AdminUser, db_column='created_by')  # 创建人
    status = IntegerField(default=0)    # -1未使用 0准备使用 1已使用  后台下发赠品默认为0，其他默认为-1
    end_time = IntegerField(default=0)    # 礼品过期时间
    used_time = IntegerField(null=True)     # 使用时间
    type = IntegerField(default=0)   # 礼品获取方式，9后台赠送，3实物券发放，4转盘抽奖，2积分兑换   对应orderItem表中的item_type 类型为9默认下单后随单附赠，其他可手动选择是否使用
    class Meta:
        db_table = 'tb_gift'

# 交互/话题
class Topic(db_old.Model):
    id = PrimaryKeyField()
    executor = ForeignKeyField(AdminUser,  related_name='executoradminuser', db_column='executor_id', null=True) #执行人
    title = CharField(max_length=32, default='')   #任务标题
    content = CharField(max_length=32, default='')  #内容
    attachment = CharField(max_length=128, default='')  #附件
    created = IntegerField(default=0)  #创建时间/发起时间
    created_by = ForeignKeyField(AdminUser,  related_name='createadminuser', db_column='created_by')  #创建人/发起人
    status = IntegerField(default=0)  # 0未完成 1已完成 2已关闭
    complete_by = ForeignKeyField(AdminUser,  related_name='completeadminuser', db_column='complete_by')  #完成人
    completed = IntegerField(default=0)  #完成时间
    close_by = ForeignKeyField(AdminUser,  related_name='closeadminuser', db_column='close_by')  #关闭人
    closed = IntegerField(default=0)  #关闭时间
    class Meta:
        db_table = 'tb_topic'

#话题讨论
class Topic_Discuss(db_old.Model):
    id = PrimaryKeyField()
    topic = ForeignKeyField(Topic,  db_column='topic_id', null=True) #任务ID
    content = CharField(max_length=2046, default='')  #执行内容
    attachment = CharField(max_length=128, default='')  #附件
    created = IntegerField(default=0)  #创建时间
    created_by = ForeignKeyField(AdminUser, db_column='created_by')  #创建人/执行人

    class Meta:
        db_table = 'tb_topic_discuss'

#热门搜索
class Hot_Search(db_old.Model):
    id = PrimaryKeyField()
    keywords = CharField(max_length=32, default='') #搜索关键词
    quantity = IntegerField(default=1)    #搜索次数
    status = IntegerField(default=0)    #0未审核   1已审核
    last_time = IntegerField(default=0)  #最后搜索时间

    class Meta:
        db_table = "tb_hot_search"

#用户推广
class User_Promote(db_old.Model):
    id = PrimaryKeyField()
    old_user = ForeignKeyField(User, related_name='old_user', db_column='old_user_id')  #外键到user表，字段名为old_user_id
    new_user = ForeignKeyField(User, related_name='new_user', db_column='new_user_id')  #外键到user表，字段名为new_user_id
    signuped = IntegerField(default=0)  #注册时间
    signup_gift = IntegerField(default=0) #注册礼是否送出，0未送  1已送
    signup_gift_content = CharField(max_length=128, default='') #注册礼内容
    first_order_gift = IntegerField(default=0) #首单礼是否送出 0未送  1已送
    first_order_time = IntegerField(default=0) #首单礼赠送时间
    first_order_content = CharField(max_length=128, default='') #首单礼内容

    class Meta:
        db_table = "tb_user_promote"

# 限时抢购活动商品
class Product_Activity(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, db_column='product_id')  # 所属商品
    product_standard = ForeignKeyField(ProductStandard, db_column='product_standard_id')  # 商品规格
    quantity = IntegerField(default=0)  # 限制数量
    begin_time = IntegerField(default=0)  # 开始时间
    end_time = IntegerField(default=0)  # 结束时间
    price = FloatField(default=0.0)  # 活动商品价格
    platform = IntegerField(default=0)  # 活动平台 0网站和手机App 1网站    2手机App
    status = IntegerField(default=1)  # 状态   0删除 1正常 2暂停
    type = IntegerField(default=1)  # 活动类型   1限时秒杀  2积分换购
    created = IntegerField(default=0)   # 创建时间
    created_by = ForeignKeyField(AdminUser, db_column='created_by')  # 创建人/执行人

    class Meta:
        db_table = "tb_product_activity"

# 用户抽奖记录
class User_Raffle_Log(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='draw_user', db_column='user_id')
    draw_level = IntegerField(default=0)    #奖品等级
    draw_name = CharField(default='')       #奖品名称
    created = IntegerField(default=0)       #获奖时间

    class Meta:
        db_table = "tb_user_raffle_log"

#快递公司反馈订单投寄状态
class DeliveryOrderStatus(db_old.Model):
    id = PrimaryKeyField()
    delivery = ForeignKeyField(Delivery, related_name='mark', db_column='delivery_id')  #物流公司
    order = ForeignKeyField(Order, related_name='delivery_order', db_column='order_id')  # 所属订单
    status = IntegerField(default=0)    # 订单未妥善投递 0为妥投，1已投递
    content = CharField(max_length=256, null=True)  # 订单未妥投原因内容

    class Meta:
        db_table = "tb_delivery_order_status"

# 媒体报道
class MediaNews(db_old.Model):
    id = PrimaryKeyField()
    url = CharField(max_length=250)  # 报道URL地址
    picurl = CharField(max_length=50)  # 报道图片地址
    imgalt = CharField(max_length=50)  # 报道图片描述
    title = CharField(max_length=56)  # 报道标题
    content = TextField()  # 报道内容/摘要
    type = IntegerField(default=1)  # 报道类型  备用
    sort = IntegerField(default=1)  #排序顺序，数字越大排列越靠前
    created = IntegerField(default=0)   # 发布时间

    def validate(self):
        if self.url and self.picurl:
            pass
        else:
            raise Exception('请输入访问url或图片地址')

    class Meta:
        db_table = 'tb_media_news'

# 预订商品
class Product_Reserve(db_old.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, db_column='product_id')  # 所属商品
    product_standard = ForeignKeyField(ProductStandard, db_column='product_standard_id')  # 商品规格
    quantity = IntegerField(default=0)  # 预订数量
    max_quantity = IntegerField(default=0)  # 预售最大数量
    begin_time = IntegerField(default=0)  # 开始时间
    end_time = IntegerField(default=0)  # 结束时间
    price = FloatField(default=0.0)  # 预订价格
    quantity_stage1 = IntegerField(default=0.0)   # 阶段1数量
    price_stage1 = FloatField(default=0.0)   # 阶段1价格
    quantity_stage2 = IntegerField(default=0.0)   # 阶段2数量
    price_stage2 = FloatField(default=0.0)   # 阶段2价格
    platform = IntegerField(default=0)  # 活动平台 0网站和手机App 1网站    2手机App
    status = IntegerField(default=1)  # 状态   0删除 1正常 2暂停
    type = IntegerField(default=1)  # 活动类型   1预售商品
    delivery_time = IntegerField(default=0)     # 发货时间
    created = IntegerField(default=0)   # 创建时间
    created_by = ForeignKeyField(AdminUser, db_column='created_by')  # 创建人/执行人
    original_price = FloatField(default=0.0)  # 市场价
    cover = CharField(max_length=128)       # 头图

    class Meta:
        db_table = "tb_product_reserve"

#用户浏览记录
class User_Browse(db_old.Model):
    user = ForeignKeyField(User, db_column='user_id')   # 用户
    product = ForeignKeyField(Product, db_column='product_id')  # 所属商品
    product_standard = ForeignKeyField(ProductStandard, db_column='product_standard_id')  # 商品规格
    category_front = ForeignKeyField(CategoryFront, db_column='category_front_id')  # 前端商品分类
    created = IntegerField(default=0)   # 创建时间

    class Meta:
        db_table = "tb_user_browse"


#用户登陆记录
class User_Login_Log(db_old.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, db_column='user_id')  # 用户
    x = CharField(max_length=12)                        # 经度坐标
    y = CharField(max_length=12)                        # 纬度坐标
    province = CharField(max_length=12, null=True)                 # 省
    city = CharField(max_length=12, null=True)                     # 市
    region = CharField(max_length=12, null=True)                   # 地区
    address = CharField(max_length=128, null=True)      # 详细地址
    created = IntegerField(default=0)                   # 创建时间

    class Meta:
        db_table = "tb_user_login_log"

#钣喷订单转发记录
class OrderSentHistory(db_old.Model):
    id = PrimaryKeyField()
    store = ForeignKeyField(Store, db_column='store_id')  # 厂家
    order = ForeignKeyField(InsuranceOrder, db_column='order_id')  # 订单
    created = IntegerField(default=0)                   # 创建时间

    class Meta:
        db_table = "tb_order_sent_history"

#保险账户列表
class InsuranceAdmin(db_old.Model):
    id = PrimaryKeyField()
    area = ForeignKeyField(Area, db_column='area_id')  # 地区ID
    insurance = CharField(max_length=8)  #保险
    account = CharField(max_length=32)   # 登录账号， 账户
    adid = ForeignKeyField(Ad, db_column='adid')  # 首页ID
    categoryid = ForeignKeyField(CategoryFront, db_column='categoryid')  # 分类id
    sort = IntegerField(default=9)
    user_id = IntegerField(default=0)

    class Meta:
        db_table = "tb_insurance_account_admin"


#手机端帮助表 area_code insurance iCompany price driverGift  driverGiftNum party2Gift party2GiftNum  sort sort2
class HelpCenter(db_old.Model):
    id = PrimaryKeyField()
    area_code =  CharField(max_length=12)  # 地区ID
    insurance = CharField(max_length=32)  #保险
    iCompany = CharField(max_length=32)  # 保险公司
    price = CharField(max_length=32)   # 价格区间
    driverGift = CharField(max_length=32)  # 车主赠品
    driverGiftNum = IntegerField(default=0)   # 车主赠品数量
    party2Gift = CharField(max_length=32)  # 乙方赠品
    party2GiftNum = IntegerField(default=0)   # 乙方赠品数量
    sort = IntegerField(default=3)   # 单交强险1 单商业险2  商业险+交强险3
    sort2 = IntegerField(default=1)  # 商业险+交强险 or 单商业险 等级排序

    class Meta:
        db_table = "tb_help_center"

# 推广人员表
class Referee(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=12)    #推广人姓名
    number = CharField(max_length=12)  # 推广人编号
    area_code = CharField(max_length=12)  # 推广人负责地区

    class Meta:
        db_table = "tb_referee"

# 推广人 推广成功的客户表
class RefereeUsers(db_old.Model):
    id = PrimaryKeyField()
    refereeId = ForeignKeyField(Referee, related_name='users', db_column='referee_id', default=0)  # 推广人
    refereeNum = CharField(max_length=12)  # 推广人编号
    userMobile = CharField(max_length=12) #用户手机号
    store = IntegerField(default=0)

    class Meta:
        db_table = "tb_referee_users"


# 商家角色管理
class UserGrade(db_old.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=12)
    grade = IntegerField(default=0) # 用户分级，0普通C 端用户，1门店B端用户，2厂商A端用户，3代理商用户

    class Meta:
        db_table = "tb_user_grade"


#商家后台模块管理
class MerchantModel(db_old.Model):
    id = PrimaryKeyField()
    name =  CharField(max_length=12)
    ugid = ForeignKeyField(UserGrade, related_name='models')

    class Meta:
        db_table = "tb_merchant_model"


#手机端帮助表
class MerchantResource(db_old.Model):
    id = PrimaryKeyField()
    name =  CharField(max_length=12)
    pid = ForeignKeyField(MerchantModel, related_name='resource')

    class Meta:
        db_table = "tb_merchant_resource"

#服务商管理保险订单 服务地区
class UserInsuranceServiceArea(db_old.Model):
    id = PrimaryKeyField()
    uid = ForeignKeyField(User, db_column='user_id')
    aid = ForeignKeyField(Area, db_column='area_id')
    iid = ForeignKeyField(Product, db_column='insurance_id')

    class Meta:
        db_table = "tb_user_insurance_service_area"


# 卖保险兑积分，积分兑现表 area_code address iid rate serviceCharge baseMoney date time iswork localtime
class CurrencyExchangeList(db_old.Model):
    id = PrimaryKeyField()
    area_code = CharField(max_length=12)    #地区code
    address = CharField(max_length=12)    #地址中文
    iid = ForeignKeyField(Product, db_column='insurance_id')    #保险ID
    date = CharField(max_length=16)     #创建日期
    time = CharField(max_length=16)     #创建时间
    localtime = IntegerField()    #时间

    rate = FloatField(default=0.0)             #兑换率（商业险）
    businessTaxRate = FloatField(default=0.0)             #商业险税率
    forceRate = FloatField(default=0.0)        #交强险 兑换率
    forceTaxRate = FloatField(default=0.0)        #交强险税率
    aliRate = FloatField(default=0.0)        #银联支付宝微信转账 手续费率
    profitRate = FloatField(default=0.0)     #利润率（车装甲
    baseMoney = FloatField(default=0.0)   #多少元起兑
    iswork = IntegerField(default=1)    #是否起作用
    is_cash = IntegerField()    #卖保险送积分0 ，积分兑现1

    class Meta:
        db_table = "tb_currency_exchange_list"


#检查卖保险是否反积分or返油
class CheckScoreArea():
    def checkLube(self, area_code):
        area = Area.get(code=area_code)
        if area.is_lubearea:
            return True
        else:
            return False

    def checkArea(self, area_code):    #检查积分地区配置
        area = Area.get(code=area_code)
        if area.is_scorearea:
            return True
        else:
            return False

    def checkInsurance(self, area_code, iid):   #检查积分保险+地区+比率配置
        cels = CurrencyExchangeList.select().where(
            (CurrencyExchangeList.area_code == area_code) & (CurrencyExchangeList.iid == iid)
            & (CurrencyExchangeList.is_cash == 0) & (CurrencyExchangeList.iswork == 1))
        if cels.count() > 0:
            return (cels[0].forceRate, cels[0].rate, cels[0].aliRate, cels[0].profitRate, cels[0].baseMoney)
        else:
            area_code = area_code[:4]
            cels = CurrencyExchangeList.select().where(
                (CurrencyExchangeList.area_code == area_code) & (CurrencyExchangeList.iid == iid)
                & (CurrencyExchangeList.is_cash == 0) & (CurrencyExchangeList.iswork == 1))
            if cels.count() > 0:
                return (cels[0].forceRate, cels[0].rate, cels[0].aliRate, cels[0].profitRate, cels[0].baseMoney)
            else:
                return False

    def checkAreaInsurance(self, area_code, iid):    #双检查
        if self.checkArea(area_code):
            return self.checkInsurance(area_code, iid)
        else:
            return False

#ReScore().rewardScore_insurance(self, uid, LubeOrScore, scoreNum, ordernum)
class ReScore():
    #计算保单积分和利润
    def rescore(self, area_code, iid, forceIM, businessIM, totalIM):
        rates = CheckScoreArea().checkAreaInsurance(area_code, iid)
        if rates:
            forceRate, rate, aliRate, profitRate, baseMoney = rates
            if baseMoney > (forceIM + businessIM):
                return (0, 0)
            else:
                total = (forceIM * forceRate) + (businessIM * rate)
                ali = total * aliRate
                score = int(total * (1-aliRate-profitRate))
                profit = round(total-ali-score, 2)
                return (int((forceIM*forceRate + businessIM*rate) * (1-aliRate-profitRate) - totalIM*aliRate), profit)
        else:
            return (0, 0)
    #创建积分记录
    def rewardScore_insurance(self, uid, LubeOrScore, scoreNum, ordernum):
        try:
            if LubeOrScore == 2 and scoreNum > 0:
                score = scoreNum  # asdf
                log = u'卖保险送滴'
                created = int(time.time())
                Score.create(user=uid, stype=0, score=score, log=log, created=created,
                             isactive=1, jftype=3, orderNum=ordernum, remark='')
        except Exception, e:
            logging.info('Error: send score error, %s' % e.message)

#----------------------------------------------------------------------------------------------------------------------#
@post_save(sender=Score)
def resetscore(model_class, instance, created):
    if instance.stype == 0:
        instance.user.score += instance.score
        instance.user.level += instance.score
    elif instance.stype == 1:
        instance.user.score -= instance.score
    instance.user.save()

@post_save(sender=Balance)
def resetbalance(model_class, instance, created):
    if instance.stype == 0:
        instance.user.balance += instance.balance
    elif instance.stype == 1:
        instance.user.balance = round((instance.user.balance - instance.balance), 2)
    instance.user.save()


if __name__ == '__main__':
    pass
    # BankCard.drop_table()
    # BankCard.create_table()
    # UserCarInfo.drop_table()
