#!/usr/bin/env python
# coding=utf8

import datetime
import simplejson
'''
# 数据库迁移代码
# 思路：
# 1、首先迁移顶层没有外键依赖的数据。
# 2、其次迁移重要的有依赖的数据。
# 3、最后迁移日志类型的记录数据。
'''

# old database
from db_model import Delivery as Old_Delivery
from db_model import Area as Old_Area
from db_model import AdType as Old_AdType
from db_model import Ad as Old_Ad
from db_model import AdminUser as Old_AdminUser
from db_model import AdminLog as Old_AdminLog
from db_model import User as Old_User
from db_model import UserAddr as Old_UserAddr
from db_model import Score as Old_Score
from db_model import Withdraw as Old_Withdraw
from db_model import Feedback as Old_Feedback # 意见反馈
from db_model import PinPaiType as Old_PinPaiType
from db_model import PPTAttribute as Old_PPTAttribute
from db_model import PPTAQuantity as Old_PPTAQuantity
from db_model import PinPai as Old_PinPai
from db_model import Store as Old_Store
from db_model import StoreServerArea as Old_StoreServerArea
from db_model import Product as Old_Product
from db_model import ProductPic as Old_ProductPic
from db_model import ProductAttribute as Old_ProductAttribute
from db_model import ProductStandard as Old_ProductStandard # 商品发布
from db_model import ReleaseArea as Old_ReleaseArea
from db_model import CurrencyExchangeList as Old_CurrencyExchangeList # 积分兑换规则表
from db_model import Cart as Old_Cart
from db_model import Settlement as Old_Settlement
from db_model import BankCard as Old_BankCard
from db_model import Order as Old_Order # 订单
from db_model import Insurances as Old_Insurances  # 保险
from db_model import InsurancePrice as Old_InsurancePrice
from db_model import InsuranceOrder as Old_InsuranceOrder
from db_model import InsuranceOrderReceiving as Old_InsuranceOrderReceiving
from db_model import GroupOrder as Old_GroupOrder
from db_model import OrderItem as Old_OrderItem
from db_model import HelpCenter as Old_HelpCenter
from db_model import Hot_Search as Old_HotSearch
# newdatabase
from model_move import Delivery as New_Delivery
from model_move import Area as New_Area
from model_move import User as New_User
from model_move import AdminUser as New_AdminUser
from model_move import AdminUserLog as New_AdminUserLog
from model_move import Store as New_Store
from model_move import StoreAddress as New_StoreAddress
from model_move import StoreBankAccount as New_StoreBankAccount
from model_move import StoreArea as New_StoreArea
from model_move import MoneyRecord as New_MoneyRecord
from model_move import ScoreRecord as New_ScoreRecord
from model_move import Category as New_Category
from model_move import CategoryAttribute as New_CategoryAttribute
from model_move import CategoryAttributeItems as New_CategoryAttributeItems
from model_move import Brand as New_Brand
from model_move import BrandCategory as New_BrandCategory
from model_move import Product as New_Product
from model_move import ProductPic as New_ProductPic
from model_move import ProductAttributeValue as New_ProductAttributeValue
from model_move import ProductRelease as New_ProductRelease
from model_move import StoreProductPrice as New_StoreProductPrice
from model_move import ShopCart as New_ShopCart
from model_move import Settlement as New_Settlement
from model_move import Order as New_Order
from model_move import SubOrder as New_SubOrder
from model_move import OrderItem as New_OrderItem
from model_move import Insurance as New_Insurance
from model_move import InsuranceArea as New_InsuranceArea
from model_move import InsuranceItem as New_InsuranceItem
from model_move import InsuranceScoreExchange as New_InsuranceScoreExchange
from model_move import InsurancePrice as New_InsurancePrice
from model_move import InsuranceOrderPrice as New_InsuranceOrderPrice
from model_move import InsuranceOrder as New_InsuranceOrder
from model_move import Block as New_Block
from model_move import BlockItem as New_BlockItem
from model_move import BlockItemArea as New_BlockItemArea
from model_move import Feedback as New_Feedback
from model_move import BankCard as New_BankCard
from model_move import LubePolicy as New_LubePolicy
from model_move import HotSearch as New_HotSearch

'''
# 第一部分：无依赖的基础数据
'''
def move_hotsearch():
    old_hot = Old_HotSearch.select()
    old_data = [{
        'keywords':item.keywords,
        'quantity':item.quantity,
        'status':item.status,
        'last_time':item.last_time
    } for item in old_hot]
    New_HotSearch.insert_many(old_data)

# delivery:物流公司
delivery_map = {}

def move_delivery():
    old_delivery = Old_Delivery.select()
    for item in old_delivery:
        delivery = New_Delivery.create(
            name=item.name
        )
        delivery_map[item.id] = delivery.id

# bank:银行卡类型
def move_bankcard():
    old_bankcard = Old_BankCard.select()
    old_data = [{
        'card_bin': item.card_bin,
        'bank_name': item.bank_name,
        'bank_id': item.bank_id,
        'card_name': item.card_name,
        'card_type': item.card_type,
        'bin_digits': item.bin_digits,
        'card_digits': item.card_digits,
        'demo': item.demo
    } for item in old_bankcard]
    print old_data
    New_BankCard.insert_many(old_data)

# area: 区域
area_map = {}

def move_area():
    old_area = Old_Area.select()
    for item in old_area:
        area = New_Area.create(
            pid=area_map[item.pid] if area_map.has_key(item.pid) else None,
            code=item.code,
            has_sub=item.has_sub,
            name=item.name,
            spell=item.spell,
            spell_abb=item.spell_abb,
            show_color=item.show_color,
            show_itf=item.show_itf,
            show_btf=item.show_btf,
            image=item.image,
            sort=item.sort,
            is_delete=item.is_delete,
            is_site=item.is_site,
            is_scorearea=item.is_scorearea,
            is_lubearea=item.is_lubearea
        )
        print area.id
        area_map[item.id] = area.id

'''
# 第二部分：互相依赖基础数据
'''
'''
# 商品分类部分
'''
# category:分类
category_map = {}

def move_category():
    old_category = Old_PinPaiType.select()
    for item in old_category:
        category = New_Category.create(
            name=item.name,
            sort=1,  # 旧的没有
            img_m=None,  # 旧的没有
            img_pc=None,  # 旧的没有
            hot=1,  # 旧的没有,设置默认值：0
            active=item.flag
        )
        print 'move_category:%d--%d' % (old_category.count(), category.id)
        category_map[item.id] = category.id

# categoryattribute:类型属性
category_attribute_map = {}

def move_categoryattribute():
    old_attribute = Old_PPTAttribute.select()
    for item in old_attribute:
        attribute = New_CategoryAttribute.create(
            category=category_map[item.PinPaiType.id],
            name=item.name,
            ename=item.ename,
            sort=0,  # 旧的没有，设置默认值：0（有效）
            active=1,  # 旧的没有，设置默认值：1（有效）
        )
        print 'move_categoryattribute:%d'%(attribute.id)
        category_attribute_map[item.id] = attribute.id

# categoryattributeitem:类型属性具体类型
category_att_item_map = {}

def move_categoryattributeitem():
    old_item = Old_PPTAQuantity.select()
    for item in old_item:
        att_item = New_CategoryAttributeItems.create(
            category_attribute=category_attribute_map[item.PPTA_id.id],
            name=item.name,
            intro="默认",
            sort=0  # 旧的没有，设置默认值：0（有效）
        )
        print 'move_categoryattributeitem:%d' % att_item.id
        category_att_item_map[item.id] = att_item.id

'''
# 商品品牌部分
'''
# brand:品牌
# 备注：保险品牌是否和商品品牌分开
brand_map = {}

def move_brand():
    old_brand = Old_PinPai.select()
    for item in old_brand:
        if not item.name:
            continue
        print item.name
        brand = New_Brand.create(
            name=item.name,
            engname=item.engname,
            pinyin=item.pinyin,
            logo=item.logo,
            intro=item.intro,
            hot=0,  # 旧的没有，设置默认值：0(否)
            sort=1,  # 旧的没有,设置默认值：1
            active=1
        )
        print 'move_brand:%d' % brand.id
        brand_map[item.id] = brand.id

# brandcategory:品牌产品类型
def move_brandcategory():
    old_brandcategory = Old_PinPai.select()  # 过滤后只余下新数据库brand对应的PinPai数据
    print old_brandcategory.count(),brand_map,category_map
    old_data = [{
        'brand': brand_map[item.id],
        'category': category_map[item.ptype.id]
    } for item in old_brandcategory]
    print old_data
    New_BrandCategory.insert_many(old_data)

'''
# 管理员账号
'''
# adminuser:管理员账户
adminuser_map = {}  # adminuser id 映射表，在转移的时候记录下来，后边有需要指向其的外键的时候替换即可

def move_adminuser():
    old_adminuser = Old_AdminUser.select()
    for item in old_adminuser:
        adminuser = New_AdminUser.create(
            username=item.username,
            password=item.password,
            mobile=item.mobile,
            email=item.email,
            code="",  # 旧的没找到，暂时设置空
            realname=item.realname,
            roles=item.roles,
            signuped=item.signuped,
            lsignined=item.lsignined,
            active=item.isactive
        )
        print adminuser.id,adminuser.username
        adminuser_map[item.id] = adminuser.id

# adminuserlog: 管理账户日志
def move_adminuserlog():
    old_adminlog = Old_AdminLog.select().where(Old_AdminLog.user.id << adminuser_map.keys())
    old_data = [{
        'admin_user': adminuser_map[item.user.id],
        'created': item.dotime,
        'content': item.content
    } for item in old_adminlog]
    print 'move_adminlog',old_adminlog.count()
    New_AdminUserLog.insert_many(old_data)
'''
# 店铺相关
'''
# store:店铺
store_map = {}

def move_store():
    old_store = Old_Store.select()
    for item in old_store:
        try:
            user = Old_User.get(Old_User.store == item)
        except Exception:
            continue
        store = New_Store.create(
            store_type=item.store_type,
            admin_code=None,  # 旧的没有
            admin_user=None,  # 旧的没有
            name=item.name,
            area_code=item.area_code,
            address=item.address,
            legal_person=item.link_man,
            license_code=None,  # 旧的没有
            license_image=item.image_license,
            store_image=item.image,
            lng=item.x,
            lat=item.y,
            pay_password=None,  # 旧的没有
            intro=item.intro,
            linkman=item.link_man,
            mobile=item.mobile,
            price=user.cashed_money,  # 由店铺对应用户转移而来
            process_insurance=item.business_type,  # 旧的没有，暂时这样处理
            score=user.score,  # 旧的没有，不知道这样处理对不对
            active=item.check_state,
            created=item.created
        )
        print store.id
        store_map[item.id] = store.id

# storebank:店铺账户
def move_storebankaccount():
    old_bank = Old_User.select()
    old_data = [{
        'store': store_map[item.store.id] if item.store else None,
        'account_type': 0,  # 旧的没有，设置默认值：0
        'alipay_truename': item.alipay_truename,
        'alipay_account': item.alipay_account,
        'bank_truename': item.bank_truename,
        'bank_account': item.bank_account,
        'bank_name': item.bank_name,
        'is_default': 0  # 旧的没有，设置默认值：0（否）
    } for item in old_bank]
    print old_data
    New_StoreBankAccount.insert_many(old_data)

# storeaddress:店铺收货地址
def move_storeaddress():
    old_address = Old_UserAddr.select()
    old_data = [{
                    'store': store_map[item.user.store.id],
                    'province': item.province,
                    'city': item.city,
                    'region': item.region,
                    'address': item.address,
                    'name': item.name,
                    'mobile': item.mobile,
                    'is_default': item.isdefault,
                    'created': 0,  # 旧的没有，设置默认值：0
                    'create_by': user_map[item.user.id],
                } for item in old_address]
    print old_data
    New_StoreAddress.insert_many(old_data)

# storearea:店铺服务区域
def move_storearea():
    old_area = Old_StoreServerArea.select()
    old_data = [{
        'area': area_map[item.aid.id],
        'store': store_map[item.sid.id]
    } for item in old_area]
    print old_data
    New_StoreArea.insert_many(old_data)
'''
# 店铺用户
'''
# user:用户账号
user_map = {}

def move_user():
    old_user = Old_User.select()
    for item in old_user:
        user = New_User.create(
            mobile=item.mobile,
            password=item.password,
            truename=item.nickname,
            role=item.userlevel,
            signuped=item.signuped,
            lsignined=item.lsignined,
            store=store_map[item.store.id],
            token=item.token,  # 旧的没有
            last_pay_type=1,  # 旧的没有，设置默认值：1
            active=item.isactive
        )
        print user.id
        user_map[item.id] = user.id

# scorerecord:积分流水
def move_scorerecord():
    old_record = Old_Score.select()
    old_data = [{
        'user': user_map[item.user.id],
        'store': store_map[item.user.store.id],
        'ordernum': item.orderNum,
        'type': item.jftype,
        'process_type': item.stype,
        'process_log': item.log,
        'score': item.score,
        'created': item.created,
        'isactive': item.isactive
    } for item in old_record]
    print old_data
    New_ScoreRecord.insert_many(old_data)

# moneyrecord:资金流水
def move_moneyrecord():
    old_record = Old_Withdraw.select()
    old_data = [{
        'user': user_map[item.user.id],
        'store': store_map[item.user.store.id],
        'process_type': 2,  # 1.0系统提现都为出钱。所以设置为2
        'process_message': item.remark,
        'process_log': item.log,
        'in_num': None,  # 旧的没有
        'out_account_type': item.account_type,
        'out_account_truename': item.account_truename,
        'out_account_account': item.account_account,
        'out_account_name': item.account_branchname,
        'money': item.balance,
        'status': item.isactive,
        'apply_time': item.apply_time,
        'processing_time': item.processing_time,
        'processing_by': adminuser_map[item.processing_by.id]
    } for item in old_record]
    print old_data
    New_MoneyRecord.insert_many(old_data)

# block:广告区域
block_map = {}
'''
# 广告部分
'''
def move_block():
    old_block = Old_AdType.select()
    for item in old_block:
        block = New_Block.create(
            tag=None,
            name=item.name,
            remark=item.remark,
            img=item.imagename,
            active=1  # 旧的没有，设置默认 值1（有效）
        )
        print block.id
        block_map[item.id] = block.id

# blockitem：广告
block_item_map = {}

def move_blockitem():
    old_blockitem = Old_Ad.select()
    for item in old_blockitem:
        blockitem = New_BlockItem.create(
            area_code=item.city_code,
            block=block_map[item.atype.id],
            name='数据库迁移数据',  # 旧的没有，暂时设置，后期人工处理
            link=0,  # 旧的没有，设置默认值：0
            ext_id=0,  # 旧的没有，设置默认值：0
            remark=item.remark,
            img=item.imgalt,
            sort=item.sort,
            activ=item.flag
        )
        print blockitem.id
        block_item_map[item.id] = blockitem.id

# blockitemarea:广告投放区域
def move_blockitemarea():
    old_blockitem = Old_Ad.select()
    old_data = [{
        'block_item': block_item_map[item.id],
        'area_code': item.city_code
    } for item in old_blockitem]
    print old_data
    New_BlockItemArea.insert_many(old_data)
'''
# 产品部分
'''
# product:产品
product_map = {}

def move_product():
    old_prodcut = Old_Product.select()
    for item in old_prodcut:
        product = New_Product.create(
            name=item.name,
            brand=brand_map[item.pinpai.id],
            category=category_map[item.categoryfront.id],
            resume=item.resume,
            unit='单位',  # 旧的没有，暂时设置，后期人工处理
            intro=item.intro,
            cover=item.cover,
            is_score=item.is_score,
            created=item.created,
            active=item.status  # 旧的没有，暂时这样处理
        )
        print product.id
        product_map[item.id] = product.id

# productpic:产品附图
def move_productpic():
    old_productpic = Old_ProductPic.select()
    old_data = [{
                    'product': product_map[item.product.id],
                    'pic': item.path,
                    'sort': 0  # 旧的没有，设置为默认值：0
                } for item in old_productpic]
    print old_data
    New_ProductPic.insert_many(old_data)

# productattributevalue:产品型号
def move_productattributevalue():
    old_attribute = Old_ProductAttribute.select()
    old_data = [{
        'product': product_map[item.product.id],
        'attribute': item.attribute,
        'attribute_item': 0,  # 旧的没有，需要额外处理
        'value': 0,  # 旧的没有，需要额外处理
    } for item in old_attribute]
    print old_data
    New_ProductAttributeValue.insert_many(old_data)

# productrelease:产品发布
product_release_map = {}

def move_productrelease():
    old_release = Old_ProductStandard.select()
    for item in old_release:
        release = New_ProductRelease.create(
            product=product_map[item.product.id],
            store=store_map[item.store.id],
            price=item.price,
            buy_count=item.orders,
            is_score=item.is_score,
            sort=item.weights,
            active=item.is_pass
        )
        product_release_map[item.id] = release.id

        print release.id,release.name

# storeproductprice:店铺区域产品价格
store_product_price_map = {}

def move_storeproductprice():
    old_price = Old_ReleaseArea.select()
    for item in old_price:
        price = New_StoreProductPrice.create(
            product_release=store_product_price_map[item.psid],
            store=store_map[item.store.id],
            area_code=item.area_code,
            price=item.price,
            score=0,  # 旧的没有，设置默认值：0
            created=datetime.datetime.now(),
            active=1  # 旧的没有，设置默认值：1
        )
        store_product_price_map[item.id] = price.id
        print price.id,price.name

'''
# 保险部分
'''
# insurance:保险公司
insurance_map = {}

def move_insurance():
    old_insurance = Old_Product.select(Old_Product.is_index == 1)
    for item in old_insurance:
        insurance = New_Insurance.create(
            name=item.name,
            eName=None,
            intro=item.resume,
            logo=item.cover,
            sort=0,  # 旧的没有，设置默认值：0
            active=item.status  # 旧的没有，设置默认值：1（有效）
        )
        insurance_map[item.id] = insurance.id
    print insurance.id.insurance.name

# insuranceitems:保险子项目
insurance_item_map = {}

def move_insuranceitems():
    old_insurance_items = Old_Insurances.select()
    for item in old_insurance_items:
        insurance_item = New_InsuranceItem.create(
            name=item.name,
            eName=item.eName,
            style=item.style,
            style_id=item.style_id,
            sort=item.sort,
        )
        insurance_item_map[item.id] = insurance_item.id
    print insurance_item.id,insurance_item.name

def move_insurancearea():
    old_area = Old_CurrencyExchangeList.select()
    old_data = [{
        'area_code': item.area_code,
        'insurance': insurance_item_map[item.iid.id],
        'lube_ok': 1,  # 旧的没有，设置默认值：1
        'score_ok': 1,  # 旧的没有，设置默认值：1
        'sort': 0,  # 旧的没有，设置默认值：0
        'active': item.iswork
    } for item in old_area]
    print old_data
    New_InsuranceArea.insert_many(old_data)

# insuranceprice:保额
def move_insuranceprice():
    old_price = Old_InsurancePrice.select()
    old_data = [{
        'insurance_item': insurance_item_map[item.pid.id],
        'coverage': item.name
    } for item in old_price]
    print old_data
    New_InsurancePrice.insert_many(old_data)

# insurancescoreexchange:保险积分兑换规则
def move_insuranceexchange():
    old_exchange = Old_CurrencyExchangeList.select()
    old_data = [{
        'area_code': item.area_code,
        'insurance': insurance_item_map[item.iid.id],
        'created': item.time,

        'business_exchange_rate': item.rate,
        'business_exchange_rate2': 0,  # 旧的没有
        'business_tax_rate': item.businessTaxRate,

        'force_exchange_rate': item.forceRate,
        'force_exchange_rate2': 0,  # 旧的没有
        'force_tax_rate': item.forceTaxRate,

        'ali_rate': item.aliRate,
        'profit_rate': item.profitRate,
        'base_money': item.baseMoney
    } for item in old_exchange]
    print old_data
    New_InsuranceScoreExchange.insert_many(old_data)


def _has_dic(src=[], dickey=None):
    for index, item in enumerate(src):
        if item['gift'] == dickey:
            return index
    else:
        return -1
# 送油策略
def move_lubeexchange():
    old_policy = Old_HelpCenter.select()
    for item in old_policy:
        insurance = New_Insurance.get(New_Insurance.name.contains(item.iCompany))
        try:
            tmppolicy = New_LubePolicy.get(New_LubePolicy.area_code == item.area_code,
                                                  New_LubePolicy.insurance == insurance)
        except Exception:
            tmppolicy = None

        if tmppolicy:
            policy = simplejson.loads(tmppolicy.policy)
            index = _has_dic(policy, item.driverGift)
            if index >= 0:
                policy[index]['item'].append(
                    {
                        'name': item.insurance,
                        'driver': item.driverGiftNum,
                        'store': item.party2GiftNum,
                        'minprice': int(minp),
                        'maxprice': int(maxp),
                        'flag': 1  # 暂时不知道设置为什么值，设置为1
                    }
                )
            else:
                policy.append(
                    {
                        'gift': item.driverGift,
                        'items': [{
                            'name': item.insurance,
                            'driver': item.driverGiftNum,
                            'store': item.party2GiftNum,
                            'minprice': int(minp),
                            'maxprice': int(maxp),
                            'flag': 1  # 暂时不知道设置为什么值，设置为1
                        }]
                    }
                )
            tmppolicy.policy(simplejson.dumps(policy))
            tmppolicy.save()
        else:
            minp,maxp = item.price.split()
            data = [{
                'gift': item.driverGift,
                'items': [{
                    'name': item.insurance,
                    'driver': item.driverGiftNum,
                    'store': item.party2GiftNum,
                    'minprice': int(minp),
                    'maxprice': int(maxp),
                    'flag': 1  # 暂时不知道设置为什么值，设置为1
                }]
            }]
            New_LubePolicy.create(
                area_code=item.area_code,
                insurance=insurance,
                policy=simplejson.dumps(data)
            )

'''
# 第三部分：互相依赖记录数据
'''
# feedback:反馈建议
def move_feedback():
    old_feedback = Old_Feedback.select()
    old_data = [{
        'user': user_map[item.user.id],
        'suggest': item.content,
        'img': None  # 旧的没有
    } for item in old_feedback]
    print old_data
    New_Feedback.insert_many(old_data)

# insuranceorderprice:保险报价单
insurance_order_price_map = {}

def move_insuranceporderprice():
    old_insurance_order_price = Old_InsuranceOrder.select()
    for item in old_insurance_order_price:
        try:
            adminuser = New_AdminUser.get(New_AdminUser.name == item.lasteditedby)
        except Exception:
            adminuser = 0
        insuranceorderprice = New_InsuranceOrderPrice.create(
            insurance_order_id=None,  # 旧的没有
            insurance=insurance_map[item.insurance.id],
            created=item.ordered,  # 旧的没有
            admin_user=adminuser,  # 旧的没有
            gift_policy=item.LubeOrScore,
            response=1,  # 旧的没有
            status=1,  # 旧的没有
            score=0,  # 旧的没有
            total_price=item.price,  # 保险订单总价格
            force_price=item.forceIprc,  # 交强险 价格
            business_price=item.businessIprc,  # 商业险价格
            vehicle_tax_price=item.vehicleTax,  # 车船税价格
            sms_content=0,  # 旧的没有

            # 交强险
            forceI=item.forceI,  # 是否包含交强险
            forceIPrice=0,

            # 商业险-主险-车辆损失险
            damageI=item.damageI,
            damageIPrice=0,
            damageIPlus=item.damageSpecialI,
            damageIPlusPrice=0,

            # 商业险-主险-第三者责任险，含保额
            thirdDutyI=item.thirdDutyI,
            thirdDutyIPrice=0,
            thirdDutyIPlus=item.thirdDutySpecialI,
            thirdDutyIPlusPrice=0,

            # 商业险-主险-机动车全车盗抢险
            robbingI=item.robbingI,
            robbingIPrice=0,
            robbingIPlus=item.robbingSpecialI,
            robbingIPlusPrice=0,

            # 商业险-主险-机动车车上人员责任险（司机），含保额
            driverDutyI=item.driverDutyI,
            driverDutyIPrice=0,
            driverDutyIPlus=item.driverDutySpecialI,
            driverDutyIPlusPrice=0,

            # 商业险-主险-机动车车上人员责任险（乘客），含保额
            passengerDutyI=item.passengerDutyI,
            passengerDutyIPrice=0,
            passengerDutyIPlus=item.passengerDutySpecialI,
            passengerDutyIPlusPrice=0,

            # 商业险-附加险-玻璃单独破碎险
            glassI=item.glassI,
            glassIPrice=0,

            # 商业险-附加险-车身划痕损失险，含保额
            scratchI=item.scratchI,
            scratchIPrice=0,
            scratchIPlus=item.scratchSpecialI,
            scratchIPlusPrice=0,

            # 商业险-附加险-自燃损失险
            fireDamageI=item.normalDamageI,
            fireDamageIPrice=0,
            fireDamageIPlus=item.normalDamageSpecialI,
            fireDamageIPlusPrice=0,

            # 商业险-附加险-发动机涉水损失险
            wadeI=item.wadeI,
            wadeIPrice=0,
            wadeIPlus=item.wadeSpecialI,
            wadeIPlusPrice=0,

            # 商业险-附加险-机动车损失保险无法找到第三方特约金
            thirdSpecialI=item.thirdSpecialI,
            thirdSpecialIPrice=0,
        )
        insurance_order_price_map[item.id] = insuranceorderprice.id
        print insuranceorderprice.id

# insuranceorder:保险订单
def move_insuranceorder():
    old_order = Old_InsuranceOrder.select()
    old_data = []
    for item in old_order:
        try:
            reciver = Old_InsuranceOrderReceiving.get(Old_InsuranceOrderReceiving.orderid.id == item.id)
        except Exception:
            reciver = 0
        old_data.append({
            'ordernum': item.ordernum,
            'user': user_map[item.user.id],
            'store': store_map[item.store.id],
            'current_order_price': item.product,

            'id_card_front': item.idcard,
            'id_card_back': item.idcardback,
            'drive_card_front': item.drivercard,
            'drive_card_back': item.drivercard2,
            'payment': item.payment,
            'ordered': item.ordered,

            'delivery_to': reciver.contact,
            'delivery_tel': reciver.mobile,
            'delivery_province': reciver.address,
            'delivery_city': None,
            'delivery_region': None,
            'delivery_address': reciver.paddress,
            'deliver_company': None,
            'deliver_num': None,

            'status': item.status,
            'cancel_reason': item.cancelreason,
            'cancel_time': item.cancel_time,
            'sms_content': '',  # 就得没有，暂时设置，后期需要人工处理
            'sms_sent_time': item.lasteditedtime,
            'local_summary': item.localsummary,
            'pay_time': item.paytime,
            'deal_time': item.ordered,
            'order_count': 0,
            'pay_account': item.pay_account,
            'trade_no': item.trade_no,
            'user_del': item.userDel
        })
    print old_data
    New_InsuranceOrder.insert_many(old_data)

# cart:购物车:购物车建议可以不导入
def move_cart():
    old_cart = Old_Cart.select()
    old_data = [{
        'store': store_map[item.user.store.id],  # 旧的没有,是否指的是购买方
        'store_product_price': 0,  # 旧的没有,暂时设置，后期需要人工处理
        'quantity': item.quantity,
        'created': item.created
    } for item in old_cart]
    print old_data
    New_ShopCart.insert_many(old_data)

# settlement:结算
settlement_map = {}
def move_settlement():
    old_settlement = Old_Settlement.select()
    for item in old_settlement:
        settlement = New_Settlement.create(
            user=user_map[item.user.id],
            sum_money=item.sum_money,
            created=item.created
        )
        settlement_map[item.id] = settlement.id
    print settlement.id

# order:产品订单
order_map = {}

def move_Order():
    old_order = Old_Order.select()
    old_data = [{
        'ordernum': item.ordernum,
        'user': item.user,
        'buyer_store': 0,  # 旧的没有，暂时设置0
        'address': item.address,
        'delivery': delivery_map[item.delivery.id],
        'delivery_num': item.deliverynum,
        'ordered': item.ordered,
        'payment': item.payment,
        'message': item.message,
        'order_type': item.order_type,  # 付款方式 1金钱订单 2积分订单
        'total_price': item.currentprice,  # 就得没有，暂时设置为这个
        'pay_balance': item.pay_balance,
        'pay_price': 0,  # 旧的没有，暂时设置默认值
        'pay_time': item.paytime,
        'status': item.status,
        'trade_no': item.trade_no,
        'order_count': 0,
        'buyer_del': 0  # 旧的没有，暂时设置
    } for item in old_order]
    print old_data
    New_Order.insert_many(old_data)

# suborder:子订单
suborder_map = {}

def move_suborder():
    old_suborder = Old_GroupOrder.select()
    for item in old_suborder:
        suborder = New_SubOrder.create(
            order=order_map[item.order.id],
            saler_store=0,
            buyer_store=0,
            price=item.order.price,
            status=item.order.status,
            fail_reason=None,
            fail_time=0,
            delivery_time=delivery_map[item.order.delivery.item.id],
            settlement=settlement_map[item.order.settlement.id],
            saler_del=0,
            buyer_del=0,
        )
        suborder_map[item.id] = suborder.id

# orderitem:订单内容
def move_orderitem():
    old_orderitem = Old_OrderItem.select()
    old_data = [{
        'order': order_map[item.order.id],
        'sub_order': 0,  # 旧的没有，需要处理
        'product': product_map[item.product.id],
        'store_product_price': 0,
        'quantity': item.quantity,
        'price': item.price
    } for item in old_orderitem]
    print old_data
    New_OrderItem.insert_many(old_data)

if __name__ == '__main__':
    move_hotsearch()
    move_delivery()
    move_bankcard()
    move_area()
    move_category()
    move_categoryattribute()
    move_categoryattributeitem()
    move_brand()
    move_brandcategory()
    move_adminuser()
    move_adminuserlog()
    move_store()
    move_storebankaccount()
    move_storeaddress()
    move_storearea()
    move_user()
    move_scorerecord()
    move_moneyrecord()
    move_block()
    move_blockitem()
    move_blockitemarea()
    move_product()
    move_productpic()
    move_productattributevalue()
    move_productrelease()
    move_storeproductprice()
    move_insurance()
    move_insuranceitems()
    move_insurancearea()
    move_insuranceprice()
    move_insuranceexchange()
    move_lubeexchange()
    move_feedback()
    move_insuranceporderprice()
    move_insuranceorder()
    move_cart()
    move_settlement()
    move_Order()
    move_suborder()
    move_orderitem()
