#!/usr/bin/env python
# coding=utf-8

import time
from peewee import *
import hashlib
#from bootloader import db
from bootloader import db_move3 as db
from lib.util import vmobile
import re
import setting

# 地区表
class Area(db.Model):
    id = PrimaryKeyField()
    pid = ForeignKeyField('self', db_column='pid', null=True)  # 父级ID
    code = CharField(max_length=40)  # 编码
    has_sub = IntegerField(default=0)  # 是否拥有下级
    name = CharField(max_length=30)  # 名称
    spell = CharField(max_length=50)  # 拼音
    spell_abb = CharField(max_length=30)  # 拼音缩写
    show_color = CharField(max_length=30)  # 显示颜色
    show_itf = IntegerField(default=0)  # 是否斜体
    show_btf = IntegerField(default=0)  # 是否粗体
    image = IntegerField(default=0)  # 图片地址
    sort = IntegerField(default=00)  # 排序，数字越小排在越前
    is_delete = IntegerField(default=0)  # 是否删除
    is_site = IntegerField(default=0)  # 是否站点
    is_scorearea = IntegerField(default=0)  # 是否开通积分地区
    is_lubearea = IntegerField(default=0)  # 是否开通返油地区

    @classmethod
    def is_lube_area(cls, area_code):
        try:
            area = Area.get(Area.code == area_code)
            return area.is_lubeare == 1
        except:
            return False

    @classmethod
    def is_score_area(cls, area_code):
        try:
            area = Area.get(Area.code == area_code)
            return area.is_scorearea == 1
        except:
            return False

    @classmethod
    def get_detailed_address(cls, area_code):
        try:
            area_code_len = len(area_code)
            area = Area.get(code=area_code)
            if area_code_len == 12:
                address = area.pid.pid.name + area.pid.name + area.name
            elif area_code_len == 8:
                address = area.pid.name + area.name
            else:
                address = area.name
            return address
        except:
            return ''

    @staticmethod
    def get_area_name(area_code):
        try:
            name = Area.get(code=area_code).name
        except Exception, e:
            name = None
        return name

    class Meta:
        db_table = 'tb_area'


# 管理员用户表
class AdminUser(db.Model):
    id = PrimaryKeyField()  # 主键
    username = CharField(unique=True, max_length=32, null=False)  # 注册用户名
    password = CharField(max_length=32)  # 密码
    mobile = CharField(max_length=12)  # 手机号
    email = CharField(max_length=128)  # email
    code = CharField(max_length=20)  # 业务推广人员编号
    area_code = CharField(max_length=40)  # 区域编码
    realname = CharField(max_length=32)  # 真实姓名
    roles = CharField(max_length=8)  # D开发人员；A管理员；Y运营；S市场；K客服；C仓库；Z直踩点；B编辑；G采购；P批发商；J经销商；R采购APP入库；+经销商价格修改权限（可组合，如：DA）
    signuped = IntegerField(default=0)  # 注册时间
    lsignined = IntegerField(default=0)  # 最后登录时间
    active = IntegerField(default=1)  # 状态 0删除 1有效

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


# 管理员用户表
class AdminUserLog(db.Model):
    id = PrimaryKeyField()  # 主键
    admin_user = ForeignKeyField(AdminUser, related_name='logs', db_column='admin_user_id')  # 后台人员
    created = IntegerField(default=0)  # 创建时间
    content = CharField(max_length=2048)  # 日志内容

    class Meta:
        db_table = 'tb_admin_users_log'


# 门店
class Store(db.Model):
    id = PrimaryKeyField()
    store_type = IntegerField(default=1)  # 门店类型 1经销商 2社会修理厂（门店）
    admin_code = CharField(max_length=20, null=True)  # 业务推广人员编号
    franchiser = IntegerField(default=0)  # 如果门店是修理厂，该字段是给修理厂返油的经销商
    admin_user = ForeignKeyField(AdminUser, related_name='stores', db_column='admin_user_id', null=True)  # 业务推广人员
    name = CharField(max_length=100)  # 门店名称
    area_code = CharField(max_length=40)  # 区域编码
    insurance_policy_code = CharField(max_length=40,null=True)  # 返佣策略区域编码
    address = CharField(max_length=128, null=True)  # 详细地址
    legal_person = CharField(max_length=28, null=True)  # 法人
    license_code = CharField(max_length=128, null=True)  # 营业执照注册号
    license_image = CharField(max_length=128)  # 营业执照图片
    store_image = CharField(max_length=128)  # 门店图片
    lng = CharField(max_length=12, null=True)  # 经度坐标
    lat = CharField(max_length=12, null=True)  # 纬度坐标
    pay_password = CharField(max_length=128, null=True)  # 支付密码
    intro = TextField()  # 店铺介绍 -------------，后台使用
    linkman = CharField(max_length=32)  # 联系人 -------------，默认为法人
    mobile = CharField(max_length=16)  # 联系人手机号 -------------，默认为注册人手机号
    price = FloatField(default=0.0)  # 店铺收入余额
    process_insurance = IntegerField(default=0)  # 经销商是否允许处理保险业务
    score = IntegerField(default=0)  # 店铺积分
    active = IntegerField(default=0)  # 审核状态 0未审核 1审核通过 2审核未通过
    created = IntegerField(default=0)  # 创建时间

    class Meta:
        db_table = "tb_store"


# 用户表
class User(db.Model):
    id = PrimaryKeyField()  # 主键
    mobile = CharField(unique=True, max_length=64, null=False)  # 注册手机号
    password = CharField(max_length=32)  # 密码
    truename = CharField(max_length=32)  # 真实姓名
    role = CharField(max_length=8, null=False, default='A')  # 用户角色，考虑角色数量、类型
    signuped = IntegerField(default=0)  # 注册时间
    lsignined = IntegerField(default=0)  # 最后登录时间
    store = ForeignKeyField(Store, related_name='users', db_column='store_id', null=False)  # 所属店铺
    token = CharField(max_length=128, null=True)  # 用户当前登录的token
    last_pay_type = IntegerField(default=1)  # 用户上一次的支付方式 1支付宝  2微信 3银联 4余额
    active = IntegerField(default=1)  # 用户状态 0被禁止的用户 1正常用户

    @staticmethod
    def create_password(raw):
        return hashlib.new("md5", raw).hexdigest()

    def check_password(self, raw):
        return hashlib.new("md5", raw).hexdigest() == self.password

    def updatesignin(self, token):
        self.lsignined = int(time.time())
        self.token = token
        self.save()

    def validate(self):
        if vmobile(self.mobile):
            if User.select().where(User.mobile == self.mobile).count() > 0:
                raise Exception('此账号已经注册')
        else:
            raise Exception('请输入正确的手机号码或邮寄地址')

    class Meta:
        db_table = 'tb_users'


# 店铺收货地址
class StoreAddress(db.Model):
    id = PrimaryKeyField()
    store = ForeignKeyField(Store, related_name='addresses', db_column='store_id')  # 店铺
    province = CharField(max_length=16, default='陕西')  # 省份
    city = CharField(max_length=16, default='西安')  # 城市
    region = CharField(max_length=32, null='')  # 区域
    address = CharField(max_length=128, null=True)  # 详细地址
    name = CharField(max_length=16, null=True)  # 收件人姓名
    mobile = CharField(max_length=11, null=True)  # 收件人电话
    is_default = IntegerField(default=1)  # 是否默认 0否 1是
    created = IntegerField(default=0)  # 创建时间
    create_by = ForeignKeyField(User, db_column='user_id')  # 创建人

    class Meta:
        db_table = 'tb_store_address'


# 经销商服务区域
class StoreArea(db.Model):
    id = PrimaryKeyField()
    area = ForeignKeyField(Area, db_column='area_id')  # 地区
    store = ForeignKeyField(Store, related_name='service_areas', db_column='store_id')  # 店铺

    class Meta:
        db_table = 'tb_store_area'


# 门店银行、支付宝账户
class StoreBankAccount(db.Model):
    id = PrimaryKeyField()
    store = ForeignKeyField(Store, related_name='store_bank_accounts', db_column='store_id')  # 店铺
    account_type = IntegerField(default=0)  # 账户类型 0银联 1支付宝
    alipay_truename = CharField(max_length=32, default='')  # 支付主人宝姓名
    alipay_account = CharField(max_length=128, default='')  # 支付宝账号
    bank_truename = CharField(max_length=32, default='')  # 银行卡主人姓名
    bank_account = CharField(max_length=32, default='')  # 银行卡号
    bank_name = CharField(max_length=64, default='')  # 银行名称
    bank_branch_name = CharField(max_length=64, default='')  # 支行名称
    is_default = IntegerField(default=0)  # 是否默认

    @staticmethod
    def check_bank(name, account):
        if not (re.match('^[A-Za-z]+$', name) or re.match(u'^[\u4e00-\u9fa5]+$', name)):
            return False
        if re.match(r'^[0-9]{17,22}$', account) or re.match(r'^[0-9]{16}$', account):
            return True
        else:
            return False

    @staticmethod
    def check_alipay(name, account):
        if not (re.match('^[A-Za-z]+$', name) or re.match(u'^[\u4e00-\u9fa5]+$', name)):
            return False
        if re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net,cc]{1,3}$', account) or re.match(
                r'^[0-9]{11}$', account):
            return True
        else:
            return False

    @staticmethod
    def get_bank_name(account):
        try:
            bank_name = StoreBankAccount.get(bank_account=account).bank_name
        except Exception, e:
            bank_name = u'获取失败'
        return bank_name

    class Meta:
        db_table = 'tb_store_bank_accounts'


# 手机验证码
class VCode(db.Model):
    id = PrimaryKeyField()
    mobile = CharField(max_length=32, null=False)  # 注册手机号
    vcode = CharField(max_length=16, null=False)
    created = IntegerField(index=True, default=0)
    flag = IntegerField(default=0)  # 0注册 1忘记密码 2绑定银行卡/支付宝 3提现

    def validate(self):
        if self.mobile and vmobile(self.mobile):
            return True
        else:
            return False

    @staticmethod
    def check_vcode(mobile, vcode, flag):
        if not (mobile and vcode and flag):
            return False
        VCode.delete().where(VCode.created < (int(time.time()) - 10 * 60)).execute()
        if VCode.select().where((VCode.mobile == mobile) & (VCode.vcode == vcode) & (VCode.flag == flag)).count() > 0:
            return True
        else:
            return False

    class Meta:
        db_table = 'tb_user_vcodes'


# 提现表
class Withdraw(db.Model):
    id = PrimaryKeyField()
    store = ForeignKeyField(Store, related_name='withdraws', db_column='store_id')  # 用户
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


# 资金变动记录
class MoneyRecord(db.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='money_records', db_column='user_id')  # 用户
    store = ForeignKeyField(Store, related_name='money_records', db_column='store_id')  # 店铺
    process_type = IntegerField(default=0)  # 资金流动类型 1入账 2出账
    type = IntegerField()  # 资金类别 # 1提现、2充值、3售出、4采购商品、5买保险返现、6退款、7补款
    process_message = CharField(max_length=4, default='')  # 提现、充值、售出、采购、保险、退款
    process_log = CharField(max_length=255, default='')  # 资金流动
    in_num = CharField(max_length=32, default='')  # 在线充值订单号
    out_account_type = IntegerField(default=0)  # 提现账户类型 0银行卡 1支付宝
    out_account_truename = CharField(max_length=32, default='')  # 银行卡/支付宝主人姓名
    out_account_account = CharField(max_length=32, default='')  # 银行卡/支付宝账号
    out_account_name = CharField(max_length=64, default='')  # 银行名称
    money = FloatField(default=0.0)  # 提现或支付的金额
    status = IntegerField(default=0)  # 处理状态 0未处理，1已处理
    apply_time = IntegerField(default=0)  # 申请时间
    processing_time = IntegerField(default=0)  # 处理时间
    processing_by = ForeignKeyField(AdminUser, db_column='updated_by', null=True)  # 处理人

    class Meta:
        db_table = 'tb_money_record'


# 积分变动记录
class ScoreRecord(db.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='score_records', db_column='user_id')  # 用户
    store = ForeignKeyField(Store, related_name='score_records', db_column='store_id')  # 店铺
    ordernum = CharField(max_length=16, default='')  # 商品/保险/提现订单号
    type = IntegerField()  # 积分类别 1兑换商品 2兑现 3卖保险获取
    process_type = IntegerField(default=0)  # 积分流动类型 1入账 2出账
    process_log = CharField(max_length=255, default='')  # 积分流动日志
    score = IntegerField(default=0)  # 流动积分数值
    created = IntegerField(default=0)  # 创建时间
    status = IntegerField(default=0)  # 状态 0待定 1确定

    class Meta:
        db_table = 'tb_score_record'

    @classmethod
    def create_score_record(cls, user, type, score, log):
        try:
            now = int(time.time())
            if type == 1:
                process_type = 2
            elif type == 2:
                process_type = 2
            elif type == 3:
                process_type = 1
            else:
                return False
            return ScoreRecord.create(user=user, store=user.store, type=type, process_type=process_type, process_log=log,
                                      score=score, created=now, status=1)
        except:
            return False


# 商品分类
class Category(db.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=20)  # 分类名
    sort = CharField(max_length=20)  # 显示顺序
    category_type = IntegerField(default=0)  # 1配件商城 2汽车装潢
    img_m = CharField(max_length=256, null=True)  # 分类图片手机端
    hot = IntegerField(default=0)  # 热门分类
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_category'


# 商品分类属性
class CategoryAttribute(db.Model):
    id = PrimaryKeyField()
    category = ForeignKeyField(Category, related_name='attributes', db_column='category_id')  # 商品分类
    name = CharField(max_length=20)  # 属性名
    ename = CharField(max_length=20)  # 英文属性名
    sort = IntegerField(default=1)  # 显示顺序
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_category_attribute'


# 商品分类属性可选值
class CategoryAttributeItems(db.Model):
    id = PrimaryKeyField()
    category_attribute = ForeignKeyField(CategoryAttribute, related_name='items', db_column='category_attribute_id')  # 商品分类属性值
    name = CharField(max_length=20)  # 名称
    intro = CharField(max_length=20)  # 简介
    sort = IntegerField(default=1)  # 显示顺序

    class Meta:
        db_table = 'tb_category_attribute_items'


# 商品品牌
class Brand(db.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=50)  # 品牌名称
    engname = CharField(max_length=50)  # 品牌英文名称
    pinyin = CharField(max_length=50, null=True)  # 中文拼音
    logo = CharField(max_length=100, null=True)  # 品牌logo
    intro = CharField(max_length=300, null=True)  # 品牌简介
    hot = IntegerField(default=0)  # 热门品牌
    sort = IntegerField(default=1)  # 排序
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_brand'


# 品牌与分类关系 n:n
class BrandCategory(db.Model):
    id = PrimaryKeyField()
    brand = ForeignKeyField(Brand, db_column='brand_id', null=True)  # 配件品牌分类
    category = ForeignKeyField(Category, db_column='category_id')  # 商品分类

    class Meta:
        db_table = 'tb_brand_category'


# 商品
class Product(db.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=64)  # 商品名称
    brand = ForeignKeyField(Brand, related_name='products', db_column='brand_id', null=True)  # 商品品牌
    category = ForeignKeyField(Category, related_name='products', db_column='category_id')  # 商品分类
    resume = CharField()  # 简单介绍
    unit = CharField()  # 单位
    intro = TextField()  # 详细介绍
    cover = CharField(max_length=128, null=True)  # 头图
    is_score = IntegerField(default=0)  # 是否是积分商品
    created = IntegerField(default=0)  # 添加时间
    active = IntegerField(default=1)  # 0删除 1正常 2下架 在这下架表示用户再发布产品时候看不到这个产品了
    hot = IntegerField(default=0)  # 热门品牌
    sort = IntegerField(default=1)  # 显示顺序

    class Meta:
        db_table = 'tb_product'
        order_by = ('-created',)


# 商品附图
class ProductPic(db.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='pics', db_column='product_id')  # 所属商品
    pic = CharField(max_length=255)
    sort = IntegerField(default=0)  # 排序

    class Meta:
        db_table = 'tb_product_pics'


# 产品属性值
class ProductAttributeValue(db.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='attributes', db_column='product_id')  # 所属商品
    attribute = ForeignKeyField(CategoryAttribute, db_column='category_attribute_id')  # 产品属性
    attribute_item = ForeignKeyField(CategoryAttributeItems, db_column='category_attribute_item_id')  # 产品属性值
    value = CharField(max_length=255)  # 属性值

    class Meta:
        db_table = 'tb_product_attribute_value'


# 发布商品
class ProductRelease(db.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, db_column='product_id')  # 所属商品
    store = ForeignKeyField(Store, related_name='products', db_column='store_id')  # 所属店铺
    price = FloatField()  # 原始销售价
    score = IntegerField(default=0)  # 原始销售积分
    buy_count = IntegerField(default=0)  # 购买次数
    is_score = IntegerField(default=0)  # 是否可以用积分兑换 0不可积分兑换 1可以兑换
    sort = IntegerField(default=0)  # 排序
    active = IntegerField(default=1)  # 状态 0下架 1有效

    class Meta:
        db_table = 'tb_product_release'


# 发布的商品对应地区及价格
class StoreProductPrice(db.Model):
    id = PrimaryKeyField()
    product_release = ForeignKeyField(ProductRelease, related_name='area_prices', db_column='product_release_id')  # 所属商品
    store = ForeignKeyField(Store, related_name='area_products', db_column='store_id')  # 所属店铺
    area_code = CharField(max_length=20)  # 地区code
    price = FloatField()  # 当前始销售价，负数或0为不能购物
    score = IntegerField(default=0)  # 积分兑换额度，负数或0为不能兑换
    created = IntegerField(default=0)  # 发布时间
    active = IntegerField(default=1)  # 状态 0下架 1有效

    class Meta:
        db_table = 'tb_store_product_price'


# 购物车
class ShopCart(db.Model):
    id = PrimaryKeyField()
    store = ForeignKeyField(Store, related_name='cart_items', db_column='store_id')  # 门店店铺
    store_product_price = ForeignKeyField(StoreProductPrice, db_column='store_product_price_id')  # 商品价格
    quantity = IntegerField(default=0)  # 数量
    created = IntegerField(default=0)  # 创建时间 即加入购物车时间

    class Meta:
        db_table = 'tb_shop_cart'


# 结算表
class Settlement(db.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='settlements', db_column='user_id')  # 用户
    sum_money = FloatField(default=0.0)  # 订单总金额
    created = IntegerField(default=0)  # 结算时间

    class Meta:
        db_table = 'tb_settlement'


# 快递公司
class Delivery(db.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=50)  # 快递公司名称
    img = CharField(max_length=150)  # 快递公司logo

    class Meta:
        db_table = 'tb_delivery'


# 订单
class Order(db.Model):
    id = PrimaryKeyField()
    ordernum = CharField(max_length=64, null=True)  # 订单号
    user = ForeignKeyField(User, related_name='orders', db_column='user_id')  # 买家
    buyer_store = ForeignKeyField(Store, related_name='orders', db_column='buyer_store_id')  # 买家所属店铺
    # 订单后货地址信息
    delivery_to = CharField(max_length=255)  # 邮寄接收人名称
    delivery_tel = CharField(max_length=255)  # 邮寄接收人电话
    delivery_province = CharField(max_length=16, default='陕西')  # 邮寄接收省份
    delivery_city = CharField(max_length=16, default='西安')  # 邮寄接收城市
    delivery_region = CharField(max_length=32, null='')  # 邮寄接收区域
    delivery_address = CharField(max_length=128, null=True)  # 邮寄接收详细地址

    order_type = IntegerField(default=1)  # 付款方式 1金钱订单 2积分订单
    payment = IntegerField(default=0)  # 支付方式  1支付宝  2微信 3银联 4余额 5积分 6支付宝二维码 7微信二维码
    total_price = FloatField(default=0.0)  # 价格，实际所有子订单商品价格之和
    total_score = IntegerField(default=0)  # 积分
    pay_balance = FloatField(default=0.0)  # 余额支付金额
    pay_price = FloatField(default=0.0)  # 实际第三方支付价格
    ordered = IntegerField(default=0)  # 下单时间
    pay_time = IntegerField(default=0)  # 支付时间
    status = IntegerField(default=0)  # 0待付款 1待发货 2待收货 3交易完成（待评价） 4已评价 5申请退款 6已退款 -1已取消
    trade_no = CharField(max_length=64, default='')  # 支付宝交易号or微信支付订单号or银联支付查询流水号
    order_count = IntegerField(default=0)  # 首单、二单、三单
    message = CharField(null=True)  # 留言/备注
    buyer_del = IntegerField(default=0)  # 买家删除已经完成的订单 1删除

    def change_status(self, status):  # -1已删除, 0待付款 1待发货 2待收货 3交易完成（待评价） 4已评价 5申请退款 6已退款 9已取消
        if self.status == status:
            return
        if self.status == -1:
            raise Exception('此订单已被删除，不能做任何操作')
        if status == 5:  # 取消订单
            if 1 < self.status < 5:
                raise Exception('订单已经处理，不能取消')
            self.status = 5
            self.canceltime = int(time.time())
        elif status == -1:  # 删除订单
            if self.status == 5:  # 已经取消的订单可以删除
                self.status = -1
            else:
                raise Exception('不能删除没有取消的订单，或者改订单还没有退款')
        elif status == 2:  # 标记订单为正在处理
            if self.status == 1 or (self.status == 0 and self.payment == 0):
                self.status = 2
            else:
                raise Exception('用户未付款，或订单已经进入下一环节')
        elif status == 3:  # 标记订单到物流公司
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


# 子订单
class SubOrder(db.Model):
    id = PrimaryKeyField()
    order = ForeignKeyField(Order, related_name='sub_orders', db_column='order_id')  # 所属订单
    saler_store = ForeignKeyField(Store, related_name='saler_sub_orders', db_column='saler_store_id')  # 卖家
    buyer_store = ForeignKeyField(Store, related_name='buyer_sub_orders', db_column='buyer_store_id')  # 买家
    price = FloatField(default=0)  # 购买时产品价格
    score = IntegerField(default=0)  # 积分
    status = IntegerField(default=0)  # 0待付款 1待发货 2待收货 3交易完成（待评价） 4已评价 5申请退款 6已退款 -1已取消
    delivery = ForeignKeyField(Delivery, db_column='delivery_id', null=True)  # 物流公司
    delivery_num = CharField(max_length=64, null=True)  # 物流单号
    fail_reason = CharField(default='', max_length=1024)  # 取消或退款原因
    fail_time = IntegerField(default=0)  # 取消或退款时间
    delivery_time = IntegerField(default=0)  # 发货时间
    settlement = ForeignKeyField(Settlement, related_name='settlement_orders', db_column='settlement_id', null=True)  # 完成的订单才可以结算
    saler_del = IntegerField(default=0)  # 卖家删除已经完成的订单 1删除
    buyer_del = IntegerField(default=0)  # 买家删除已经完成的订单 1删除

    class Meta:
        db_table = 'tb_order_sub'


# 订单内容
class OrderItem(db.Model):
    id = PrimaryKeyField()
    order = ForeignKeyField(Order, related_name='items', db_column='order_id')  # 所属订单
    sub_order = ForeignKeyField(SubOrder, related_name='items', db_column='sub_order_id')  # 所属子订单
    product = ForeignKeyField(Product, db_column='product_id')  # 所属商品
    store_product_price = ForeignKeyField(StoreProductPrice, db_column='store_product_price_id')  # 经销商商品
    quantity = IntegerField(default=0)  # 数量
    price = FloatField(default=0)  # 购买时产品价格或积分

    class Meta:
        db_table = 'tb_order_items'


# 保险公司
class Insurance(db.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=32, default='')  # 名称
    eName = CharField(max_length=32, default='')  # 拼音简写
    intro = CharField(max_length=255, default='')  # 简介
    logo = CharField(max_length=255, default='')  # logo
    hot = IntegerField(default=0)  # 热门品牌
    sort = IntegerField(default=1)  # 显示顺序
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_insurance'


# 保险公司开通地域
class InsuranceArea(db.Model):
    id = PrimaryKeyField()
    area_code = CharField(max_length=32, default='')
    insurance = ForeignKeyField(Insurance, db_column='insurance_id')
    lube_ok = IntegerField(default=1)  # 开通反油
    dealer_store = ForeignKeyField(Store, db_column='dealer_store_id')  # 送油经销商
    lube_policy = TextField(default='')  # 返油政策的json串
    cash_ok = IntegerField(default=1)  # 开通反现
    cash_policy = TextField(default='')  # 返现政策的json串
    score_ok = IntegerField(default=1)  # 开通积分
    score_policy = TextField(default='')  # 返积分政策的json串
    sort = IntegerField(default=1)  # 显示顺序
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_insurance_area'

    # 获取该地区下的所有返油返现规则
    @classmethod
    def get_area_insurance(cls, area_code):
        result = []
        ft = (InsuranceArea.active == 1)
        if len(area_code) == 12:    # 门店是区，能查发布到省市和该区的规则
            codes = [area_code, area_code[:8], area_code[:4]]
            ft &= (InsuranceArea.area_code << codes)
        elif len(area_code) == 8:    # 门店地区是市，只能查发布到省和该市的规则
            codes = [area_code, area_code[:4]]
            ft &= (InsuranceArea.area_code << codes)
        elif len(area_code) == 4:    # 门店地区是省，只能查发布到省得规则
            ft &= (InsuranceArea.area_code == area_code)
        tmp_dict = {}
        tmp_i_list = []
        for i in InsuranceArea.select().where(ft).order_by(InsuranceArea.area_code.asc()):    # 顺序省->市->区
            if i.insurance not in tmp_i_list:
                tmp_i_list.append(i.insurance)
                result.append({
                            'insurance': i.insurance,
                            'lube': i.lube_policy,
                            'cash': i.cash_policy,
                            'dealer_store': i.dealer_store
                        })
            else:
                for r in result:
                    if r['insurance'] == i.insurance:
                        if i.cash_policy:
                            r['cash'] = i.cash_policy
                        if i.lube_policy:
                            r['lube'] = i.lube_policy
        return result

    @classmethod
    def get_insurances_link(cls, area_code):  # 获取该地区所有保险公司及链接
        temp_insurance_id = []
        insurance_list = []
        ft = (InsuranceArea.active == 1)
        if len(area_code) == 12:
            codes = [area_code, area_code[:8], area_code[:4]]
            ft &= (InsuranceArea.area_code << codes)
        elif len(area_code) == 8:
            tmp_code = area_code+'%'
            ft &= ((InsuranceArea.area_code == area_code[:4]) | (InsuranceArea.area_code % tmp_code))
        elif len(area_code) == 4:
            tmp_code = area_code+'%'
            ft &= (InsuranceArea.area_code % tmp_code)
        for i in InsuranceArea.select().where(ft):
            result.append({
                'insurance': i.insurance,
                'lube': i.lube_policy,
                'cash': i.cash_policy,
                'dealer_store': i.dealer_store
            })
        return result


# 保险子险种
class InsuranceItem(db.Model):
    id = PrimaryKeyField()
    eName = CharField(max_length=32, default='')  # 英文名
    name = CharField(max_length=32, default='')  # 中文名
    style = CharField(max_length=32, default='')  # 分类名
    style_id = IntegerField(default=0)  # 分类id 交强险1  商业险主险2  商业险附加险3
    sort = IntegerField(default=1)  # 排序

    class Meta:
        db_table = 'tb_insurance_item'


# 保险子险种额度
class InsurancePrice(db.Model):
    id = PrimaryKeyField()
    insurance_item = ForeignKeyField(InsuranceItem, related_name='insurance_prices', db_column='insurance_item_id', null=True)  # 子险种
    coverage = CharField()  # 保险额度
    coveragenum = IntegerField()  # 保险额度数字

    class Meta:
        db_table = 'tb_insurance_price'


# 保险订单报价信息，创建保险订单时默认创建该表数据
class InsuranceOrderPrice(db.Model):
    id = PrimaryKeyField()
    insurance_order_id = IntegerField()  # 所属保险订单ID
    insurance = ForeignKeyField(Insurance, db_column='insurance_id')  # 所购保险公司ID
    created = IntegerField(default=0)  # 报价/修改 时间
    admin_user = ForeignKeyField(AdminUser, db_column='admin_user_id', null=True)  # 操作人员
    response = IntegerField(default=0)  # 0未报价 1已经报价 2不可再修改 -1关闭
    status = IntegerField(default=1)  # 状态 0已过期, 1有效
    read = IntegerField(default=0)  # 状态 0未读, 1已读
    gift_policy = IntegerField(default=0)  # 礼品策略 1反油， 2反现金，3返积分
    score = IntegerField(default=0)  # 卖的这单保险可以获取多少积分
    driver_lube_type = CharField(default='')    # 返车主油品型号
    driver_lube_num = IntegerField(default=0)  # 返车主油品数量
    store_lube_type = CharField(default='')    # 返修理厂油品型号
    store_lube_num = IntegerField(default=0)  # 返修理厂油品数量
    cash = FloatField(default=0.0)  # 返现金额
    total_price = FloatField(default=0.0)  # 保险订单总价格
    force_price = FloatField(default=0.0)  # 交强险 价格
    force_rate = FloatField(null=True)    # 交强险折扣
    business_price = FloatField(default=0.0)  # 商业险价格
    business_rate = FloatField(null=True)    # 商业险折扣
    vehicle_tax_price = FloatField(default=0.0)  # 车船税价格
    sms_content = CharField(max_length=1024, null=True)  # 短信通知内容

    append_refund_status = IntegerField(default=0)    # 补退款状态 0无需补退款 1待补款
    append_refund_time = IntegerField(default=0)    # 补退款时间
    append_refund_reason = CharField(max_length=128, default='')    # 补退款原因
    append_refund_num = FloatField(default=0.0)    # 补退款金额

    # 交强险
    forceI = CharField(max_length=32, default='')  # 是否包含交强险
    forceIPrice = FloatField(null=True)

    # 商业险-主险-车辆损失险
    damageI = CharField(max_length=32, default='')
    damageIPrice = FloatField(null=True)
    damageIPlus = CharField(max_length=32, default='')
    damageIPlusPrice = FloatField(null=True)

    # 商业险-主险-第三者责任险，含保额
    thirdDutyI = CharField(max_length=32, default='')
    thirdDutyIPrice = FloatField(null=True)
    thirdDutyIPlus = CharField(max_length=32, default='')
    thirdDutyIPlusPrice = FloatField(null=True)

    # 商业险-主险-机动车全车盗抢险
    robbingI = CharField(max_length=32, default='')
    robbingIPrice = FloatField(null=True)
    robbingIPlus = CharField(max_length=32, default='')
    robbingIPlusPrice = FloatField(null=True)

    # 商业险-主险-机动车车上人员责任险（司机），含保额
    driverDutyI = CharField(max_length=32, default='')
    driverDutyIPrice = FloatField(null=True)
    driverDutyIPlus = CharField(max_length=32, default='')
    driverDutyIPlusPrice = FloatField(null=True)

    # 商业险-主险-机动车车上人员责任险（乘客），含保额
    passengerDutyI = CharField(max_length=32, default='')
    passengerDutyIPrice = FloatField(null=True)
    passengerDutyIPlus = CharField(max_length=32, default='')
    passengerDutyIPlusPrice = FloatField(null=True)

    # 商业险-附加险-玻璃单独破碎险
    glassI = CharField(max_length=32, default='')
    glassIPrice = FloatField(null=True)

    # 商业险-附加险-车身划痕损失险，含保额
    scratchI = CharField(max_length=32, default='')
    scratchIPrice = FloatField(null=True)
    scratchIPlus = CharField(max_length=32, default='')
    scratchIPlusPrice = FloatField(null=True)

    # 商业险-附加险-自燃损失险
    fireDamageI = CharField(max_length=32, default='')
    fireDamageIPrice = FloatField(null=True)
    fireDamageIPlus = CharField(max_length=32, default='')
    fireDamageIPlusPrice = FloatField(null=True)

    # 商业险-附加险-发动机涉水损失险
    wadeI = CharField(max_length=32, default='')
    wadeIPrice = FloatField(null=True)
    wadeIPlus = CharField(max_length=32, default='')
    wadeIPlusPrice = FloatField(null=True)

    # 商业险-附加险-机动车损失保险无法找到第三方特约金
    thirdSpecialI = CharField(max_length=32, default='')
    thirdSpecialIPrice = FloatField(null=True)

    class Meta:
        db_table = 'tb_insurance_order_price'


# 保险订单
class InsuranceOrder(db.Model):
    id = PrimaryKeyField()
    ordernum = CharField(max_length=64, null=True)  # 订单号
    user = ForeignKeyField(User, related_name='insurance_orders', db_column='user_id')  # 用户
    store = ForeignKeyField(Store, related_name='insurance_orders', db_column='store_id')  # 店铺
    current_order_price = ForeignKeyField(InsuranceOrderPrice, db_column='current_order_price_id', null=True)  # 最终报价ID

    id_card_front = CharField(max_length=255, null=True)  # 身份证 投保人
    icfstatus = IntegerField(default=0) # 是否需要重新上传：0不需要1需要
    id_card_back = CharField(max_length=255, null=True)  # 身份证背面 投保人
    icbstatus = IntegerField(default=0)  # 是否需要重新上传：0不需要1需要

    is_same_person = IntegerField(default=1)  # 投保人与车主是否是同一人 默认是
    id_card_front_owner = CharField(max_length=255, null=True)  # 身份证 车主
    icfostatus = IntegerField(default=0)  # 是否需要重新上传：0不需要1需要
    id_card_back_owner = CharField(max_length=255, null=True)  # 身份证背面 车主
    icbostatus = IntegerField(default=0)  # 是否需要重新上传：0不需要1需要

    drive_card_front = CharField(max_length=255, null=True)  # 行驶证
    dcfstatus = IntegerField(default=0)  # 是否需要重新上传：0不需要1需要
    drive_card_back = CharField(max_length=255, null=True)  # 行驶证副本
    dcbstatus = IntegerField(default=0)  # 是否需要重新上传：0不需要1需要
    payment = IntegerField(default=1)  # 付款方式  1支付宝  2微信 3银联 4余额 5积分 6支付宝二维码 7微信二维码
    ordered = IntegerField(default=0)  # 下单时间

    delivery_to = CharField(max_length=255)  # 保单邮寄接收人名称
    delivery_tel = CharField(max_length=255)  # 保单邮寄接收人电话
    delivery_province = CharField(max_length=16, default='陕西')  # 保单邮寄接收省份
    delivery_city = CharField(max_length=16, default='西安')  # 保单邮寄接收城市
    delivery_region = CharField(max_length=32, null='')  # 保单邮寄接收区域
    delivery_address = CharField(max_length=128, null=True)  # 保单邮寄接收详细地址
    deliver_company = CharField(max_length=255, null=True)  # 快递公司
    deliver_num = CharField(max_length=255, null=True)  # 保单邮寄快递号

    status = IntegerField(default=0)  # 0待报价 1已核价/待支付 2已支付/待出单 3完成（已送积分/油） -1已删除(取消)
    cancel_reason = CharField(default='', max_length=1024)  # 取消原因
    cancel_time = IntegerField(default=0)  # 取消时间
    sms_content = CharField(max_length=1024, null=True)  # 短信通知内容
    sms_sent_time = IntegerField(default=1)  # 短信发送时间
    local_summary = CharField(max_length=256, null=True)  # 本地备注
    pay_time = IntegerField(default=0)  # 支付时间
    deal_time = IntegerField(default=0)  # 完成时间
    order_count = IntegerField(default=0)  # 首单、二单、三单
    pay_account = CharField(max_length=128, default='')  # 用户支付宝、微信账户
    trade_no = CharField(max_length=64, default='')  # 支付宝/微信交易号
    user_del = IntegerField(default=0)  # 用户端不显示

    @classmethod
    def buy_count(cls,io_id):
        i = InsuranceOrder.get(id=io_id)
        io = InsuranceOrder.select().where((InsuranceOrder.id < io_id) & (InsuranceOrder.store == i.store.id) & (InsuranceOrder.status == 3))
        return io.count()+1

    def change_status(self, status):
        if self.status == status:
            return
        if self.status == -1:
            raise Exception('此订单已被删除，不能做任何操作')
        if status == 5:  # 取消订单
            if self.status == 3:
                raise Exception('该保险订单已经办理，不能取消')
            self.status = 5
            self.canceltime = int(time.time())
        elif status == -1:  # 删除订单
            if self.status == 5:  # 已经取消的订单可以删除
                self.status = -1
            else:
                raise Exception('不能删除没有取消的订单，或者该订单还没有退款')
        elif status == 1:  # 标记订单为等待付款
            if self.status == 3:
                raise Exception('该保险订单已经办理，不能标记为待付款')
            else:
                self.status = 1
        elif status == 2:  # 付款完成
            self.status = 2

        elif status == 3:  # 办理完成
            if self.status == 2:
                self.status = 3
            else:
                raise Exception('该订单未付款，还不能办理')

    class Meta:
        db_table = 'tb_insurance_orders'


# 补退款
class AppendRefundMoney(db.Model):
    id = PrimaryKeyField()
    insurance_order = ForeignKeyField(InsuranceOrder, related_name='append_refunds')
    type = IntegerField(default=0)  # 补退款状态 0无需补退款 1待补款
    status = IntegerField(default=0)  # 补退款状态 0无需补退款 1待补款
    amount = FloatField(default=0.0)  # 补退款金额
    reason = CharField(max_length=128)  # 补退款原因
    created = IntegerField(default=0)  # 补退款时间

    class Meta:
        db_table = 'tb_insurance_order_arm'


# 车主信息表
class UserCarInfo(db.Model):
    id = PrimaryKeyField()
    insuranceorder = ForeignKeyField(InsuranceOrder, related_name='insurance_orders_car_infos', db_column='insurance_order_id')  # 保险订单ID
    # 车主信息
    car_owner_type = CharField(max_length=50, null=True)  # 车主类型:个人private(中华必填)
    ## 车主机构信息
    car_owner_num = CharField(max_length=50, null=True)  # 车辆所属组织机构代码
    ## 车主人信息
    car_owner_name = CharField(max_length=50, null=True)  # 车主姓名
    car_owner_idcard = CharField(max_length=50, null=True)  # 车主身份证号
    car_owner_idcard_date = CharField(max_length=50, null=True)  # 车主身份证住址
    car_owner_address = CharField(max_length=150, null=True)  # 被保险地址

    # 被保险人信息
    owner_buyer_isone = IntegerField(default=0)  # 0不是 1是
    buy_name = CharField(max_length=50, null=True)  # 姓名
    buy_idcard = CharField(max_length=50, null=True)  # 身份证号

    # 车辆信息
    car_num = CharField(max_length=50, null=True)  # 车牌号
    car_frame_num = CharField(max_length=50, null=True)  # 车架号
    car_engine_num = CharField(max_length=50, null=True)  # 发动机号
    car_passenger_number = CharField(max_length=50, null=True)  # 车座位数
    car_quality = CharField(max_length=50, null=True)  # 整车质量
    car_glass_type = IntegerField(default=0)  # 0国产 1进口

    car_type = CharField(max_length=50, null=True)  # 车型：小客车car
    car_use_type = CharField(max_length=50, null=True)  # 车辆使用类型：非运营non_operation,运营operation
    car_nengyuan_type = CharField(max_length=50, null=True)  # 车主能源情况：燃油ranyou，混合hunhe

    car_model_type = CharField(max_length=50, null=True)  # 品牌厂型
    car_model_code = CharField(max_length=50, null=True)  # 车辆精友码
    car_displacement = CharField(max_length=50, null=True)  # 车排量
    car_price = CharField(max_length=50, null=True)  # 车价格

    assigned = IntegerField(default=1)  # 是否过户：0没有1有
    first_register_date = CharField(max_length=50, null=True) # 初次等级日期
    assigned_date = CharField(max_length=50, null=True) # 过户日期
    # 保险信息
    start_date_enforce = CharField(max_length=50, null=True) # 交强险起保日期
    start_date_trade = CharField(max_length=50, null=True)  # 商业险起保日期
    # 中华联合额外字段
    rta_type = CharField(max_length=50, null=True)  # 交管所车辆类型
    car_detail_type = CharField(max_length=50, null=True)  # 细化车型
    car_num_type = CharField(max_length=50, null=True)  # 车牌类型
    license_type = CharField(max_length=50, null=True)  # 行驶证车辆类型
    status = IntegerField(default=0)  # 0新报价 1已读报价

    class Meta:
        db_table = 'tb_insurance_order_car_info'


# 保代宝报价回调记录表
class BaoDaiBaoQuote(db.Model):
    id = PrimaryKeyField()
    insuranceorder = ForeignKeyField(InsuranceOrder, db_column='insurance_order_id')  # 保险订单ID
    content = CharField(max_length=400, null=True)  # 消息内容
    quotenum = CharField(max_length=50, null=True)  # 报价单号
    status = IntegerField(default=0)  # 0新报价 1已读报价

    class Meta:
        db_table = 'tb_baodaibao_quote'


# # 卖保险兑现规则 返现政策
# class InsuranceScoreExchange(db.Model):
#     id = PrimaryKeyField()
#     area_code = CharField(max_length=12)  # 地区code
#     insurance = ForeignKeyField(Insurance, db_column='insurance_id')  # 保险公司ID
#     created = IntegerField()  # 创建时间
#
#     business_exchange_rate = FloatField(default=0.0)  # 兑换率（商业险），仅商业险
#     business_exchange_rate2 = FloatField(default=0.0)  # 兑换率（商业险），商业险+交强险
#     business_tax_rate = FloatField(default=0.0)  # 商业险税率
#
#     force_exchange_rate = FloatField(default=0.0)  # 交强险兑换率, 仅交强险
#     force_exchange_rate2 = FloatField(default=0.0)  # 交强险兑换率, 商业险+交强险
#     force_tax_rate = FloatField(default=0.0)  # 交强险税率
#
#     ali_rate = FloatField(default=0.0)  # 银联支付宝微信转账 手续费率
#     profit_rate = FloatField(default=0.0)  # 利润率（车装甲）
#     base_money = FloatField(default=0.0)  # 多少元起兑
#
#     class Meta:
#         db_table = "tb_insurance_score_exchange"
#

# 帮助中心 返油政策
# class LubePolicy(db.Model):
#     id = PrimaryKeyField()
#     area_code = CharField(max_length=12)  # 地区code
#     insurance = ForeignKeyField(Insurance, related_name='lube_policy', db_column='insurance_id')
#     policy = CharField(max_length=4000)  # 返油政策的json串
#
#     class Meta:
#         db_table = "tb_lube_policy"


# 店铺经销商返油返现映射表
class SSILubePolicy(db.Model):
    id = PrimaryKeyField()
    store = ForeignKeyField(Store, related_name='store_policy', db_column='store_id')  # 门店
    insurance = ForeignKeyField(Insurance, related_name='insurance_policy', db_column='insurance_id')  # 保险公司
    dealer_store = ForeignKeyField(Store, related_name='dealer_store_policy', db_column='dealer_store_id')  # 经销商
    cash = TextField(default='')  # 返现政策的json串  # 返现政策
    lube = TextField(default='')  # 返油政策的json串  # 返油政策
    score = TextField(default='')  # 返油政策的json串  # 返积分政策

    class Meta:
        db_table = "tb_store_gift_policy"


# 手机端区块: 广告
class Block(db.Model):
    id = PrimaryKeyField()
    tag = CharField(max_length=20)  # 程序中使用标记
    name = CharField(max_length=50)  # 类区块名称
    remark = CharField(max_length=50, null=True)  # 备注
    img = CharField(max_length=100, null=True)  # 图片名
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_block'


# 手机端区块内容
class BlockItem(db.Model):
    id = PrimaryKeyField()
    area_code = CharField(max_length=50)  # 所属区域
    block = ForeignKeyField(Block, related_name='items', db_column='block_id', null=True)  # 所属区块
    name = CharField(max_length=50)  # 名称
    link = CharField(max_length=255)  # 链接地址；协议区分 1保险（选择保险） 2图片链接 3产品（选择产品）
    ext_id = IntegerField(null=True)  # 外部引用的ID
    remark = CharField(max_length=255, null=True)  # 备注
    img = CharField(max_length=100, null=True)  # 图片名
    sort = IntegerField(default=1)  # 排序
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_block_item'


# 手机端广告发布地区
class BlockItemArea(db.Model):
    id = PrimaryKeyField()
    block_item = ForeignKeyField(BlockItem)  # 广告ID
    area_code = CharField(max_length=50)  # 发布地区的code

    class Meta:
        db_table = 'tb_block_item_area'


# 热搜
class HotSearch(db.Model):
    id = PrimaryKeyField()
    keywords = CharField(max_length=32, default='')    # 搜索关键词
    quantity = IntegerField(default=1)    # 搜索次数
    status = IntegerField(default=0)    # 0未审核   1已审核
    last_time = IntegerField(default=0)    # 最后搜索时间

    class Meta:
        db_table = "tb_hot_search"


# 支付通知内容
class PaymentNotify(db.Model):
    id = PrimaryKeyField()
    content = CharField(max_length=2048)   # 支付通知内容
    payment = IntegerField(default=1)  # 通知来源  1支付宝  2微信 3银联 4余额 5积分 6支付宝二维码 7微信二维码
    notify_time = IntegerField(default=0)  # 通知时间
    notify_type = IntegerField(default=0)  # 通知类型 1同步 2异步
    function_type = IntegerField(default=0)  # 功能类型 1购买 2充值

    class Meta:
        db_table = 'tb_payment_notify'


# 意见反馈
class Feedback(db.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, db_column='user_id', null=True)  # 用户
    suggest = CharField(max_length=255)  # 意见建议
    img = CharField(max_length=255)  # 图片

    class Meta:
        db_table = "tb_feedback"


class MobileUpdate(db.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=64, default='')  # 版本名称
    version = CharField(max_length=64, default='')  # 版本号
    path = CharField(max_length=64, default='')  # 版本文件路径
    client = CharField(max_length=64, default='')  # 客户端类型 android ios
    state = IntegerField(default=0)  # 版本是否可用0不可以用，1可以
    updatedtime = IntegerField(default=0)  # 更新时间
    updatedby = ForeignKeyField(AdminUser, db_column='updated_by')  # 最后更新人
    isForce = CharField(max_length=8, default='false')  # 强制更新
    instruction = CharField(max_length=256)  # 强制更新

    class Meta:
        db_table = 'tb_mobile_update'


# 银行卡数据库
class BankCard(db.Model):
    id = PrimaryKeyField()
    card_bin = CharField(max_length=50, null=True)  # 卡号范围
    bank_name = CharField(max_length=100, null=True)  # 银行名称
    bank_id = IntegerField(null=True)  # 银行标示
    card_name = CharField(max_length=100,null=True)  # 卡名称
    card_type = CharField(max_length=50,null=True)  # 卡类型
    bin_digits = IntegerField(null=True)
    card_digits = IntegerField(null=True)
    demo = CharField(max_length=50,null=True)

    class Meta:
        db_table = 'tb_bank_card_bin'


# 推广底图
class Popularize(db.Model):
    id = PrimaryKeyField()
    img = CharField(max_length=100, null=True)  # 图片名
    sort = IntegerField(default=1)  # 排序
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_popularize'


# 汽车品牌
class CarBrand(db.Model):
    id = PrimaryKeyField()
    brand_name = CharField(max_length=50)  # 汽车品牌
    brand_pinyin_name = CharField(max_length=100, null=True)  # 汽车品牌拼音
    logo = CharField(max_length=1000, null=True)  # 汽车品牌logo
    brand_intro = CharField(max_length=800, null=True)  # 汽车品牌简介
    brand_pinyin_first = CharField(max_length=1, null=True)  # 汽车品牌拼音首字母
    catch_url = CharField(max_length=1000, null=True)  # 抓取详情页面路径
    sort = FloatField(default=0.0)  # 同拼音下的排序
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_car_brand'


# 汽车品牌厂家，主要是中国的厂家，如大众下的一汽和上汽
class CarBrandFactory(db.Model):
    id = PrimaryKeyField()
    brand = ForeignKeyField(CarBrand, related_name='factories', db_column='car_brand_id', null=True)  # 汽车品牌
    factory_name = CharField(max_length=50)  # 汽车品牌厂家
    logo = CharField(max_length=1000, null=True)  # 汽车品牌logo
    factory_intro = CharField(max_length=800, null=True)  # 汽车品牌简介
    sort = FloatField(default=0.0)  # 同品牌下的排序
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_car_factory'


# 汽车
class Car(db.Model):
    id = PrimaryKeyField()
    car_name = CharField(max_length=50)  # 汽车
    car_pinyin_name = CharField(max_length=100, null=True)  # 汽车拼音
    brand = ForeignKeyField(CarBrand, related_name='cars', db_column='car_brand_id')  # 汽车品牌
    factory = ForeignKeyField(CarBrandFactory, related_name='cars', db_column='car_brand_factory_id', null=True)  # 汽车厂家
    logo = CharField(max_length=1000, null=True)  # 汽车logo，汽车的图片
    catch_url = CharField(max_length=1000, null=True)  # 抓取详情页面路径
    stop_sale = IntegerField(default=0)  # 停产？ 0正常销售 1已停产
    sort = FloatField(default=0.0)  # 厂家或品牌下的排序
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_car'


# 车型分类，如：1.6L/115kW 涡轮增压，2.0L/135kW 涡轮增压
class CarItemGroup(db.Model):
    id = PrimaryKeyField()
    car = ForeignKeyField(Car, related_name='groups', db_column='car_id')  # 汽车
    group_name = CharField(max_length=50)  # 汽车型号

    class Meta:
        db_table = 'tb_car_item_group'


# SK产品列表
class CarSK(db.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=50)  # SK产品名
    intro = CharField(max_length=500)  # SK产品介绍
    api_level = CharField(max_length=100, null=True)  # api级别
    logo = CharField(max_length=1000, null=True)  # SK产品logo
    category = IntegerField(default=1)  # 状态 1发动机油，2变速箱油
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_car_sk'


# 汽车型号，如翼虎2.0T
class CarItem(db.Model):
    id = PrimaryKeyField()
    car_item_name = CharField(max_length=100)  # 汽车型号
    car = ForeignKeyField(Car, related_name='items', db_column='car_id')  # 汽车
    group = ForeignKeyField(CarItemGroup, related_name='items', db_column='car_item_group_id')  # 所在分组
    displacement = FloatField(default=0.0)  # 排量
    gearbox = CharField(max_length=50, null=True)  # 变速箱，AT自动，MT手动，8挡手自一体
    actuator = CharField(max_length=50, null=True)  # 驱动方式，四驱，前驱，后驱
    power = CharField(max_length=50, null=True)  # 动力来源，汽油，柴油，电动，油电混合
    sale_category = CharField(max_length=50, null=True)  # 销售分组，如：在售，停售
    catch_url = CharField(max_length=1000, null=True)  # 抓取详情页面路径
    stop_sale = IntegerField(default=0)  # 停产？ 0正常销售 1已停产
    sort = FloatField(default=0.0)  # 厂家或品牌下的排序
    car_type = CharField(max_length=50, null=True)  # 车型：suv或紧凑型车……
    price = FloatField(default=0.0)  # 指导价格
    car_sk_engine_1 = ForeignKeyField(CarSK, related_name='engine_items_1', db_column='car_sk_engine_id_1', null=True)  # SK产品发动机推荐1
    car_sk_engine_2 = ForeignKeyField(CarSK, related_name='engine_items_2', db_column='car_sk_engine_id_2', null=True)  # SK产品发动机推荐2
    car_sk_gearbox_1 = ForeignKeyField(CarSK, related_name='gearbox_items_1', db_column='car_sk_gearbox_id_1', null=True)  # SK产品变速箱推荐1
    car_sk_gearbox_2 = ForeignKeyField(CarSK, related_name='gearbox_items_2', db_column='car_sk_gearbox_id_2', null=True)  # SK产品变速箱推荐2
    brake_oil = ForeignKeyField(CarSK, related_name='brake_items', db_column='car_sk_brake_id', null=True)  # SK产品刹车油
    antifreeze_solution = ForeignKeyField(CarSK, related_name='antifreeze_items', db_column='car_sk_antifreeze_id', null=True)  # SK产品防冻液
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_car_item'


# 消息
class Message(db.Model):
    id = PrimaryKeyField()
    other_id = IntegerField(default=0)  # 关联表主键id
    store = ForeignKeyField(Store, related_name='store_messages', db_column='store_id')  # 店铺
    status = IntegerField(default=0)  # 消息状态：0 未读，1已读
    type = CharField(max_length=30)  # 消息类型:'insuranceorder','order'等
    content = CharField(max_length=50, null=True)  # 消息内容
    link = CharField(max_length=50, null=True)  # 跳转链接

    class Meta:
        db_table = 'tb_message'


# 极光推送内容
class JPushActive(db.Model):
    id = PrimaryKeyField()
    title = CharField(default='')
    intro = TextField(default='')
    active = IntegerField(default=1)    # 0失效，1有效

    class Meta:
        db_table = 'tb_jpush_active'


# 极光推送内容
class JPushMsg(db.Model):
    id = PrimaryKeyField()
    title = CharField(default='')
    content = TextField(default='')
    img_url = CharField(default='')
    jpush_active = ForeignKeyField(JPushActive, db_column='jpush_active_id', null=True)
    active = IntegerField(default=1)  # 0失效，1有效

    class Meta:
        db_table = 'tb_jpush_msg'


# 极光推送计划
class JPushPlan(db.Model):
    id = PrimaryKeyField()
    title = CharField(default='')    # 标题
    type = IntegerField()    # 推送类别 1
    time = CharField(max_length=64)    # 推送时间（例：10:30十点半推送）
    rate = CharField(max_length=64)    # 推送频率（例：0每天，1,2,5,7周一二五七，2017-8-8只2017年八月八号一天）
    intro = ForeignKeyField(JPushMsg)
    active = IntegerField(default=1)    # 0失效，1有效

    class Meta:
        db_table = 'tb_jpush_plan'


def init_db():
    from lib.util import find_subclasses

    models = find_subclasses(db.Model)
    for model in models:
        if model.table_exists():
            print model
            model.drop_table()
        model.create_table()


def load_test_data():
    AdminUser.create(username='18189279823', password='e10adc3949ba59abbe56e057f20f883e', mobile='18189279823',
                     email='xiaoming.liu@520czj.com', code='0001', realname='刘晓明', roles='D')
    AdminUserLog.create(admin_user=1, created=int(time.time()), content='测试日志记录')
    Store.create(store_type=1, name='name', address='address', license_image='', store_image='', lng='', lat='',
                 pay_password='', intro='', linkman='', mobile='18189279823', active=1, created=1487032696,
                 area_code='002700010001')
    Store.create(store_type=1, name='测试店铺', address='测试地址', license_image='', store_image='', lng='', lat='',
                 pay_password='', intro='', linkman='', mobile='17629260130', active=1, created=1487032696,
                 area_code='002700010001')
    User.create(mobile='18189279823', password='e10adc3949ba59abbe56e057f20f883e', role='A', signuped=1487032696,
                lsignined=1487032696, store=1, active=1, truename='刘晓明')

    User.create(mobile='17629260130', password='e10adc3949ba59abbe56e057f20f883e', role='A', signuped=1487032696,
                lsignined=1487032696, store=2, active=1, truename='郭晓宏')

    Category.create(name='润滑油', sort=1, active=1,
                    img_m='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png',
                    img_pc='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')
    Category.create(name='导航仪', sort=2, active=1,
                    img_m='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png',
                    img_pc='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')

    CategoryAttribute.create(category=1, name='容量', ename='rl', sort=1)
    CategoryAttribute.create(category=1, name='粘度', ename='nd', sort=2)
    CategoryAttribute.create(category=1, name='级别', ename='jb', sort=3)
    CategoryAttribute.create(category=2, name='配置', ename='pz', sort=1)
    CategoryAttribute.create(category=2, name='屏幕尺寸', ename='pmcc', sort=2)

    CategoryAttributeItems.create(category_attribute=1, name='5L', intro='5L')
    CategoryAttributeItems.create(category_attribute=1, name='8L', intro='8L')
    CategoryAttributeItems.create(category_attribute=2, name='5W-30', intro='5W-30')
    CategoryAttributeItems.create(category_attribute=2, name='0W-40', intro='0w-40')
    CategoryAttributeItems.create(category_attribute=3, name='SF', intro='SF')
    CategoryAttributeItems.create(category_attribute=3, name='SM', intro='SM')
    CategoryAttributeItems.create(category_attribute=4, name='标配', intro='标配')
    CategoryAttributeItems.create(category_attribute=4, name='选配', intro='选配')
    CategoryAttributeItems.create(category_attribute=5, name='8寸', intro='8寸')
    CategoryAttributeItems.create(category_attribute=5, name='10寸', intro='10寸')

    Brand.create(name='SK', engname='SK', pinyin='SK',
                 logo='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png', intro='SK')
    Brand.create(name='壳牌', engname='qp', pinyin='qp',
                 logo='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png', intro='壳牌润滑油')
    Brand.create(name='飞影', engname='fy', pinyin='fy',
                 logo='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png', intro='飞影导航仪')
    Brand.create(name='安畅星', engname='acx', pinyin='acx',
                 logo='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png', intro='安畅星导航仪')

    BrandCategory.create(brand=1, category=1)
    BrandCategory.create(brand=2, category=1)
    BrandCategory.create(brand=3, category=2)
    BrandCategory.create(brand=4, category=2)
    BrandCategory.create(brand=1, category=2)  # SK拥有润滑油、导航仪两类产品

    Product.create(name='SK合成机油', brand=1, category=1, resume='SK合成机油', unit='桶', intro='intro',
                   cover='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')
    Product.create(name='SK导航仪', brand=1, category=2, resume='SK导航仪', unit='个', intro='intro',
                   cover='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')

    ProductPic.create(product=1, pic='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')
    ProductPic.create(product=1,
                      pic='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')
    ProductPic.create(product=1,
                      pic='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')
    ProductPic.create(product=2,
                      pic='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')
    ProductPic.create(product=2,
                      pic='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')
    ProductAttributeValue.create(product=1, attribute=1, attribute_item=1, value='5L')
    ProductAttributeValue.create(product=1, attribute=2, attribute_item=3, value='5W-30')
    ProductAttributeValue.create(product=1, attribute=3, attribute_item=5, value='SF')

    ProductAttributeValue.create(product=2, attribute=4, attribute_item=7, value='标配')
    ProductAttributeValue.create(product=2, attribute=5, attribute_item=9, value='8寸')

    ProductRelease.create(product=1, store=1, price=1)
    ProductRelease.create(product=2, store=1, price=2)

    ProductRelease.create(product=1, store=2, price=0.1)
    ProductRelease.create(product=2, store=2, price=0.01)

    StoreProductPrice.create(product_release=1, store=1, area_code='002700010001', price=3)
    StoreProductPrice.create(product_release=2, store=1, area_code='00270001', price=4)
    StoreProductPrice.create(product_release=2, store=1, area_code='00270001', price=4, score=3)

    StoreProductPrice.create(product_release=3, store=2, area_code='002700010001', price=0.3)
    StoreProductPrice.create(product_release=4, store=2, area_code='00270001', price=0.01)
    StoreProductPrice.create(product_release=4, store=2, area_code='00270001', price=0.01, score=3)

    Block.create(tag='banner', name='首页轮播广告', remark='',
                 img='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')
    Block.create(tag='insurance', name='首页保险区块', remark='',
                 img='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')
    Block.create(tag='hot_category', name='热门分类', remark='',
                 img='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')
    Block.create(tag='hot_brand', name='热销品牌', remark='',
                 img='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')
    Block.create(tag='recommend', name='为你推荐', remark='',
                 img='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')

    Insurance.create(name='人保车险', eName='rbcx',
                     logo='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')
    Insurance.create(name='平安车险', eName='pacx',
                     logo='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')

    BlockItem.create(area_code='00270001', block=1, name='ceshi', link='http://www.baidu.com',
                     img='http://img.520czj.com/image/2017/02/15/server1_20170215111526VDJrFZYbKUeiLjuGkcsxTIhW.png')

    BlockItem.create(area_code='00270001', block=2, name='人保车险', link='czj://insurance/1', img='', ext_id=1)
    BlockItem.create(area_code='00270001', block=3, name='分类', link='czj://category/1', img='', ext_id=1)
    BlockItem.create(area_code='00270001', block=4, name='品牌', link='czj://brand/1', img='', ext_id=1)
    BlockItem.create(area_code='00270001', block=5, name='产品', link='czj://product/1', img='', ext_id=1)
    BlockItem.create(area_code='00270001', block=5, name='产品', link='czj://product/2', img='', ext_id=2)

    # 积分变动记录
    ScoreRecord.create(user=1, store=1, ordernum='789899', type=1, process_type=1, process_log='测试收入积分', score=5,
                       created=1487032696, status=1)
    ScoreRecord.create(user=1, store=1, ordernum='667433', type=2, process_type=2, process_log='测试使用积分', score=8,
                       created=1487032696, status=1)

    # 余额变动记录
    MoneyRecord.create(user=1, store=1, process_type=1, process_message='售出', process_log='销售获得余额', in_num='CZ334',
                       money=567.5, status=1, apply_time=1487032696)
    MoneyRecord.create(user=1, store=1, process_type=2, process_message='提现', process_log='提现', in_num='CZ334',
                       money=100.5, status=1, apply_time=1487032696)

if __name__ == '__main__':
    init_db()
    # load_test_data()
    # LubePolicy.create_table()

    # CarItem.drop_table()
    # CarItemGroup.drop_table()
    # Car.drop_table()
    # CarBrandFactory.drop_table()
    # CarItemSK.drop_table()
    # CarBrand.create_table()
    # CarBrandFactory.create_table()
    # Car.create_table()
    # CarItemGroup.create_table()
    # CarItem.create_table()
    # CarSK.create_table()
    # CarItemSK.create_table()
    pass
