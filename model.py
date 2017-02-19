#!/usr/bin/env python
# coding=utf-8

import time
from peewee import *
import hashlib
from bootloader import db
from lib.util import vmobile


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
        if lenAreaCode == 12 or lenAreaCode == 8 or lenAreaCode == 4:
            try:
                a = Area.get(code=area_code)
                if lenAreaCode == 12:
                    addr = a.pid.pid.name + a.pid.name + a.name
                elif lenAreaCode == 8:
                    addr = a.pid.name + a.name
                else:
                    addr = a.name
                return addr
            except:
                return ''
        else:
            return ''

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


# 门店
class Store(db.Model):
    id = PrimaryKeyField()
    store_type = IntegerField(default=1)  # 门店类型 1服务商 2社会修理厂（门店）
    admin_code = CharField(max_length=20, null=True)  # 业务推广人员编号
    admin_user = ForeignKeyField(AdminUser, related_name='stores', db_column='admin_user_id', null=True)  # 业务推广人员
    name = CharField(max_length=100)  # 门店名称
    area_code = CharField(max_length=40)  # 区域编码
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


# 手机验证码
class VCode(db.Model):
    id = PrimaryKeyField()
    mobile = CharField(max_length=32, null=False)  # 注册手机号
    vcode = CharField(max_length=16, null=False)
    created = IntegerField(index=True, default=0)
    flag = IntegerField(default=0)  # 0注册 1忘记密码 2绑定手机号 3提现

    def validate(self):
        if self.mobile and vmobile(self.mobile):
            return True
        else:
            return False

    class Meta:
        db_table = 'tb_user_vcodes'


# 店铺联系地址
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
    active = IntegerField(default=1)  # 状态 0删除 1有效
    created = IntegerField(default=0)  # 创建时间
    create_by = ForeignKeyField(User, db_column='user_id')  # 创建人

    class Meta:
        db_table = 'tb_store_address'


# 资金变动记录
class MoneyRecord(db.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='money_records', db_column='user_id')  # 用户
    store = ForeignKeyField(Store, related_name='money_records', db_column='store_id')  # 店铺
    process_type = IntegerField(default=0)  # 资金流动类型 1入账 2出账
    process_log = CharField(max_length=255, default='')  # 资金流动
    in_num = CharField(max_length=32, default='')  # 在线充值订单号
    out_account_type = IntegerField(default=0)  # 提现账户类型 0银行卡 1支付宝
    out_account_truename = CharField(max_length=32, default='')  # 银行卡姓名
    out_account_name = CharField(max_length=64, default='')  # 银行名称
    out_account_branchname = CharField(max_length=64, default='')  # 支行名称
    out_account_account = CharField(max_length=32, default='')  # 银行卡号
    money = FloatField(default=0.0)  # 提现或支付的金额
    status = IntegerField(default=0)  # 处理状态
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
    process_type = IntegerField(default=0)  # 积分流动类型 1入账 2出账
    process_log = CharField(max_length=255, default='')  # 积分流动
    score = IntegerField(default=0)  # 流动积分数值
    status = IntegerField(default=0)  # 状态 0待定 1确定

    class Meta:
        db_table = 'tb_score_record'


# 门店银行、支付宝账户
class StoreBankAccount(db.Model):
    id = PrimaryKeyField()
    store = ForeignKeyField(Store, related_name='store_bank_accounts', db_column='store_id')  # 店铺
    account_type = IntegerField(default=0)  # 账户类型
    alipay_truename = CharField(max_length=32, default='')  # 支付宝姓名
    alipay_account = CharField(max_length=128, default='')  # 支付宝账号
    bank_truename = CharField(max_length=32, default='')  # 银行卡姓名
    bank_account = CharField(max_length=32, default='')  # 银行卡号
    bank_name = CharField(max_length=64, default='')  # 银行名称
    bank_branchname = CharField(max_length=64, default='')  # 支行名称
    is_default = IntegerField(default=0)  # 是否默认

    class Meta:
        db_table = 'tb_score_record'


# 门店服务区域
class StoreArea(db.Model):
    id = PrimaryKeyField()
    area = ForeignKeyField(Area, db_column='area_id')  # 用户
    store = ForeignKeyField(Store, related_name='service_areas', db_column='store_id')  # 店铺

    class Meta:
        db_table = 'tb_store_area'


# 商品分类
class Category(db.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=20)  # 分类名
    sort = CharField(max_length=20)  # 显示顺序
    img_m = CharField(max_length=256, null=True)  # 分类图片手机端
    img_pc = CharField(max_length=256, null=True)  # 分类图片PC端
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_category'


# 商品分类属性
class CategoryAttribute(db.Model):
    id = PrimaryKeyField()
    category = ForeignKeyField(Category, related_name='attributes',
                               db_column='category_id')  # 商品分类
    name = CharField(max_length=20)  # 属性名
    ename = CharField(max_length=20)  # 英文属性名
    sort = IntegerField(default=1)  # 显示顺序
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_category_attribute'


# 商品分类属性可选值
class CategoryAttributeItems(db.Model):
    id = PrimaryKeyField()
    category_attribute = ForeignKeyField(CategoryAttribute, related_name='items',
                                         db_column='category_attribute_id')  # 商品分类属性值

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
    brand = ForeignKeyField(Brand, related_name='products', db_column='brand_id', null=True)  # 配件品牌分类
    category = ForeignKeyField(Category, related_name='products', db_column='category_id')  # 商品分类
    resume = CharField()  # 简单介绍
    unit = CharField()  # 单位
    intro = TextField()  # 详细介绍
    cover = CharField(max_length=128)  # 头图
    is_score = IntegerField(default=0)  # 是否是积分商品
    created = IntegerField(default=0)  # 添加时间
    active = IntegerField(default=1)  # 0删除 1正常 2下架 在这下架表示用户再发布产品时候看不到这个产品了

    class Meta:
        db_table = 'tb_product'
        order_by = ('-created',)


# 商品附图
class ProductPic(db.Model):
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='pics', db_column='product_id')  # 所属商品
    pic = CharField(max_length=255)

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
    buy_count = IntegerField(default=0)  # 购买次数
    is_score = IntegerField(default=0)  # 是否可以用积分兑换 0不可积分兑换 1可以兑换
    sort = IntegerField(default=0)  # 排序
    active = IntegerField(default=1)  # 状态 0下架 1有效

    class Meta:
        db_table = 'tb_product_release'


# 发布商品
class StoreProductPrice(db.Model):
    id = PrimaryKeyField()
    product_release = ForeignKeyField(ProductRelease, related_name='area_prices',
                                      db_column='product_release_id')  # 所属商品
    store = ForeignKeyField(Store, related_name='area_products', db_column='store_id')  # 所属店铺
    area_code = CharField(max_length=20)  # 地区code
    price = FloatField()  # 当前始销售价，负数或0为不能购物
    score = IntegerField(default=0)  # 积分兑换额度，负数或0为不能兑换
    active = IntegerField(default=1)  # 状态 0下架 1有效

    class Meta:
        db_table = 'tb_store_product_price'


# 结算表
class Settlement(db.Model):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='settlements', db_column='user_id')  # 用户
    sum_money = FloatField(default=0.0)  # 订单总金额
    created = IntegerField(default=0)  # 结算时间

    class Meta:
        db_table = 'tb_settlement'


# 订单
class Order(db.Model):
    id = PrimaryKeyField()
    ordernum = CharField(max_length=64, null=True)  # 订单号
    user = ForeignKeyField(User, related_name='orders', db_column='user_id')  # 买家
    buyer_store = ForeignKeyField(Store, related_name='orders', db_column='buyer_store_id')  # 买家所属店铺
    address = ForeignKeyField(StoreAddress, db_column='store_address_id')  # 收信地址
    ordered = IntegerField(default=0)  # 下单时间
    payment = CharField(default='')  # 付款方式  1支付宝  2微信 3银联 4余额
    message = CharField(null=True)  # 付款留言
    order_type = IntegerField(default=1)  # 付款方式 2积分订单  1金钱订单
    total_price = FloatField(default=0.0)  # 价格，实际所有子订单商品价格之和
    pay_balance = FloatField(default=0.0)  # 余额支付金额
    pay_price = FloatField(default=0.0)  # 实际第三方支付价格
    pay_time = IntegerField(default=0)  # 支付时间
    status = IntegerField(default=0)  # 0待付款 1待发货 2待收货 3交易完成（待评价） 4已评价 5申请退款 6已退款 -1已取消
    trade_no = CharField(max_length=64, default='')  # 支付宝交易号or微信支付订单号or银联支付查询流水号
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
    price = FloatField(default=0)  # 购买时产品价格或积分
    status = IntegerField(default=0)  # 0待付款 1待发货 2待收货 3交易完成（待评价） 4已评价 5申请退款 6已退款 -1已取消
    fail_reason = CharField(default='', max_length=1024)  # 取消或退款原因
    fail_time = IntegerField(default=0)  # 取消或退款时间
    delivery_time = IntegerField(default=0)  # 发货时间
    settlement = ForeignKeyField(Settlement, related_name='settlement_orders', db_column='settlement_id',
                                 null=True)  # 完成的订单才可以结算
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


# 保险
class Insurance(db.Model):
    id = PrimaryKeyField()
    name = CharField(max_length=32, default='')  # 名称
    eName = CharField(max_length=32, default='')  # 拼音简写
    intro = CharField(max_length=128, default='')  # 简介
    logo = CharField(max_length=255, default='')  # logo
    sort = IntegerField(default=1)  # 显示顺序
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_insurance'


# 保险子险种
class InsuranceItem(db.Model):
    id = PrimaryKeyField()
    eName = CharField(max_length=32, default='')  # 英文名
    name = CharField(max_length=32, default='')  # 中文名
    style = CharField(max_length=32, default='')  # 分类
    sort = IntegerField(default=1)  # 排序
    active = IntegerField(default=1)  # 状态 0删除 1有效

    class Meta:
        db_table = 'tb_insurance_item'


# 保险子险种额度
class InsurancePrice(db.Model):
    id = PrimaryKeyField()
    insurance_item = ForeignKeyField(InsuranceItem, db_column='insurance_item_id', null=True)  # 子险种
    coverage = CharField()  # 保险额度

    class Meta:
        db_table = 'tb_insurance_price'


# 保险订单
class InsuranceOrder(db.Model):
    id = PrimaryKeyField()
    ordernum = CharField(max_length=64, null=True)  # 订单号
    user = ForeignKeyField(User, related_name='insurance_orders', db_column='user_id')  # 用户
    store = ForeignKeyField(Store, related_name='insurance_orders', db_column='store_id', null=True)  # 店铺
    insurance = ForeignKeyField(Insurance, db_column='insurance_id')  # 所购保险
    idcard = CharField(max_length=255, null=True)  # 身份证
    idcardback = CharField(max_length=255, null=True)  # 身份证背面
    drivercard = CharField(max_length=255, null=True)  # 行驶证
    drivercard2 = CharField(max_length=255, null=True)  # 行驶证副本
    payment = IntegerField(default=1)  # 付款方式 0货到付款  1支付宝  2账户余额 3网银支付 6微信支付 7银联
    contact = CharField(null=True)  # 联系人
    mobile = CharField(null=True)  # 用户电话
    message = CharField(null=True)  # 客户留言
    price = FloatField(default=0.0)  # 价格
    forceIprc = FloatField(default=0.0)  # 交强险 价格forceIprc businessIprc vehicleTax
    businessIprc = FloatField(default=0.0)  # 商业险价格
    vehicleTax = FloatField(default=0.0)  # 车船税价格

    status = IntegerField(default=0)  # 0待确认 1待付款 2付款完成 3已办理 5已取消 -1已删除
    cancelreason = CharField(default='', max_length=1024)  # 取消原因
    canceltime = IntegerField(default=0)  # 取消时间
    ordered = IntegerField(default=0)  # 下单时间
    summary = CharField(max_length=1024, null=True)  # 短信通知内容
    localsummary = CharField(max_length=256, null=True)  # 本地备注
    paytime = IntegerField(default=0)  # 支付时间
    deal_time = IntegerField(default=0)  # 完成时间
    pay_account = CharField(max_length=128, default='')  # 用户支付宝账户
    trade_no = CharField(max_length=64, default='')  # 支付宝交易号
    # forceI  ;
    # damageI thirdDutyI  robbingI damageSpecialI thirdDutySpecialI robbingSpecialI  ;
    # driverDutyI thirdDutySpecialI, passengerDutyI passengerDutySpecialI,    glassI, specialI
    # scratchI scratchSpecialI, normalDamageI normalDamageSpecialI,  wadeI wadeSpecialI,  thirdSpecialI thirdSpecialSpecialI
    forceI = CharField(max_length=32, default='')  # 交强险
    damageI = CharField(max_length=32, default='')  # 车辆损失险
    thirdDutyI = CharField(max_length=32, default='')  # 第三者责任险
    robbingI = CharField(max_length=32, default='')  # 机动车全车盗抢险
    driverDutyI = CharField(max_length=32, default='')  # 机动车车上人员责任险（司机）
    passengerDutyI = CharField(max_length=32, default='')  # 机动车车上人员责任险（乘客）
    glassI = CharField(max_length=32, default='')  # 玻璃单独破碎险
    scratchI = CharField(max_length=32, default='')  # 车身划痕损失险
    normalDamageI = CharField(max_length=32, default='')  # 自然损失险
    wadeI = CharField(max_length=32, default='')  # 发动机涉水损失险
    specialI = CharField(max_length=32, default='')  # 不计免赔特约险
    thirdSpecialI = CharField(max_length=32, default='')  # 机动车损失保险无法找到第三方特约险

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
    userDel = IntegerField(default=0)  # 用户端不显示
    scoreNum = IntegerField(default=0)  # 卖的这单保险可以获取多少积分
    deadline = IntegerField(default=0)  # 期限

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
    Store.create(store_type=1, name='name', address='address', license_image='', store_image='', lng='', lat='',
                 pay_password='', intro='', linkman='', mobile='18189279823', active=1, created=1487032696,
                 area_code='002700010001')
    User.create(mobile='18189279823', password='e10adc3949ba59abbe56e057f20f883e', role='A', signuped=1487032696,
                lsignined=1487032696, store=1, active=1)

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

    StoreProductPrice.create(product_release=1, store=1, area_code='002700010001', price=3)
    StoreProductPrice.create(product_release=2, store=1, area_code='00270001', price=4)

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


if __name__ == '__main__':
    init_db()
    load_test_data()
    pass
