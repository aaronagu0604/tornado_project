#!/usr/bin/env python
# coding=utf8
# 数据库迁移代码

from db_model import CategoryFront, PinPai, Product as ProductOld, ProductStandard
from model import Category, Brand, Product, ProductRelease, StoreProductPrice


def move_category():
    old_categorys = CategoryFront.select()
    for item in old_categorys:
        Category.create(name=item.name, sort=1, active=1, has_sub=item.has_sub,
                        pid=item.pid, img_m=item.img_m, img_pc=item.img_pc)

def move_pinpai():
    pps = PinPai.select()
    for p in pps:
        Brand.create(name=p.name, engname=p.engname, pinyin=p.pinyin, logo=p.logo, intro=p.intro)


def move_product():
    pps = ProductOld.select().limit(2)
    for p in pps:
        Product.create(name=p.name, brand=1, category=1, resume=p.resume, unit='unit', intro='intro', cover=p.cover,
                       is_score=0, created=p.created)
        print 'moved ' + p.name


def move_product_release():
    # ProductRelease.create(product=1, store=1, name='name', price=0.4)
    # ProductRelease.create(product=2, store=1, name='22 name', price=4.3)

    # product_release = ForeignKeyField(ProductRelease, related_name='area_prices',
    #                                   db_column='product_release_id')  # 所属商品
    # store = ForeignKeyField(Store, related_name='area_products', db_column='store_id')  # 所属店铺
    # area_code = CharField(max_length=20)  # 地区code
    # price = FloatField()
    #
    StoreProductPrice.create(product_release=1, store=1, area_code='', price=12)
    StoreProductPrice.create(product_release=2, store=1, area_code='', price=32)


if __name__ == '__main__':
    move_product_release()
    pass