#!/usr/bin/env python
# coding=utf8
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from model import *

def catch_brand(browser):
    browser.get("http://car.bitauto.com/")  # Load page
    m = browser.find_element_by_class_name("list-con")

    brand_list = m.find_elements_by_xpath("./li")
    for brand in brand_list:
        # 获取品牌
        char = brand.find_element_by_class_name('num-tit').text
        subList = brand.find_elements_by_tag_name('li')
        for sub in subList:
            # 品牌车型
            a = sub.find_element_by_tag_name('a')
            cb = CarBrand()
            cb.brand_name = a.find_element_by_class_name("brand-name").find_element_by_tag_name('span').text
            cb.logo = a.find_element_by_tag_name('img').get_attribute('src')
            cb.brand_pinyin_first = char
            cb.catch_url = a.get_attribute('href')
            cb.save()
            print cb.brand_name
    print 'finished'


def catch_car(browser):

    brands = CarBrand.select()
    for cb in brands:
        browser.get(cb.catch_url)
        d = browser.find_element_by_id("curObjTreeNode")
        lilist = d.find_elements_by_xpath('./div/ul/li')
        for li in lilist:
            a = None
            try:
                a = li.find_element_by_xpath('./a')
            except:
                pass

            factory = None
            if a is not None:
                fname = a.find_element_by_tag_name('span').text
                print 'factory ', fname
                q = CarBrandFactory.select().where(CarBrandFactory.factory_name == fname)
                if q.count() > 0:
                    factory = q[0]
                else:
                    factory = CarBrandFactory()
                    factory.factory_name = fname
                    factory.save()

            bs = li.find_elements_by_xpath('./ul/li')
            for b in bs:
                saleoff = 0
                if b.get_attribute('class') == 'saleoff':
                    saleoff = 1
                aa = b.find_element_by_tag_name('a')
                car = Car()
                car.car_name = aa.find_element_by_tag_name('span').text
                car.brand = cb
                car.factory = factory
                car.stop_sale = saleoff
                car.catch_url = aa.get_attribute('href')
                if saleoff == 1:
                    car.car_name = car.car_name.split(' ')[0]
                car.save()
                print car.car_name


def catch_car_item(browser, start):
    cars = Car.select().where(Car.id >= start)
    for car in cars:
        ok_list.append(car.id - 1)
        browser.get(car.catch_url)
        # time.sleep(1)
        d = browser.find_element_by_class_name("card-layout")
        car.car_name = d.find_element_by_class_name('box').text
        car.logo = d.find_element_by_tag_name('img').get_attribute('src')
        car.save()
        print car.id, ' saved ', car.car_name
        try:
            d = browser.find_element_by_class_name("onsale-car-box")
        except:
            continue
        tag = d.find_element_by_class_name('current').text
        trlist = d.find_elements_by_tag_name('tr')
        group = None
        for tr in trlist:
            isTitle = False
            try:
                tr.find_element_by_class_name('first-item')
                isTitle = True
            except:
                pass
            if isTitle:
                group_name = tr.find_element_by_class_name('first-item').text
                q = CarItemGroup.select().where((CarItemGroup.group_name==group_name) & (CarItemGroup.car==car))

                if q.count() > 0:
                    group = q[0]
                else:
                    group = CarItemGroup()
                    group.car = car
                    group.group_name = group_name
                    group.save()
                    print 'saved group name', group_name
            else:
                tds = tr.find_elements_by_xpath('./td')
                carItem = CarItem()
                a = tds[0].find_elements_by_xpath('./a')[0]
                carItem.car_item_name = a.text
                carItem.car = car
                carItem.group = group
                carItem.gearbox = tds[2].text
                carItem.catch_url = a.get_attribute('href')
                carItem.sale_category = tag
                stop_sale = 0
                try:
                    span = tds[0].find_elements_by_tag_name('span')
                    if len(span) > 0:
                        stop_sale = 1
                except:
                    pass
                carItem.stop_sale = stop_sale
                carItem.save()
                print 'saved car item', carItem.car_item_name
        noSale = None
        try:
            noSale = d.find_element_by_id('pop_nosale')
        except:
            pass
        urls = []
        if noSale is not None:
            tag = noSale.find_element_by_xpath('./a').text
            alist = noSale.find_elements_by_xpath('./div/a')
            for a in alist:
                urls.append(a.get_attribute('href'))

        for url in urls:
            print url
            # time.sleep(2)
            browser.get(url)
            group = None
            d = browser.find_element_by_class_name('list-table')
            trlist = d.find_elements_by_tag_name('tr')
            group = None
            for tr in trlist:
                isTitle = False
                try:
                    tr.find_element_by_class_name('first-item')
                    isTitle = True
                except:
                    pass
                if isTitle:
                    group_name = tr.find_element_by_class_name('first-item').text
                    q = CarItemGroup.select().where(
                        (CarItemGroup.group_name == group_name) & (CarItemGroup.car == car))

                    if q.count() > 0:
                        group = q[0]
                    else:
                        group = CarItemGroup()
                        group.car = car
                        group.group_name = group_name
                        group.save()
                        print 'saved group name', group_name
                else:
                    tds = tr.find_elements_by_xpath('./td')
                    carItem = CarItem()
                    a = tds[0].find_elements_by_xpath('./a')[0]
                    carItem.car_item_name = a.text
                    carItem.car = car
                    carItem.group = group
                    carItem.gearbox = tds[2].text
                    carItem.catch_url = a.get_attribute('href')
                    carItem.sale_category = tag
                    carItem.stop_sale = 1
                    carItem.save()
                    print 'saved car item', carItem.car_item_name
    return 1


def catch_car_item_detail(browser):
    items = CarItem.select().where(CarItem.pl >> None).limit(1)
    while len(items) == 1:
        item = items[0]
        browser.get(item.catch_url)
        # time.sleep(1)
        d = browser.find_element_by_class_name("mid row")
        lilist = d.find_elements_by_xpath('./div/h5')
        if len(lilist) > 0:
            item.price = float(lilist[0].text.replace(u'万元', ''))
            item.car_type = lilist[0].text.replace(u'万元', '')
        d = browser.find_element_by_class_name("col-xs-4 brand-rank")
        ll = d.find_elements_by_xpath('./h6/a')
        if len(ll) > 0:
            item.car_type = ll[0].text.replace(u'周关注排行', '')

        item.save()
        items = CarItem.select().where(CarItem.pl >> None).limit(1)
        pass


browser = webdriver.Firefox()
# catch_brand(browser)
# catch_car(browser)
flag = 0
start = 0
ok_list = range(0, start)
# while flag == 0:
#     try:
#         flag = catch_car_item(browser, start)
#     except:
#         print 'get error, delete last item'
#         try:
#             carItem = CarItem.select().order_by(CarItem.id.desc()).limit(1)[0]
#             if carItem is not None:
#                 start = carItem.car.id
#                 if ok_list.index(start) == -1:
#                     CarItem.delete().where(CarItem.car == carItem.car).execute()
#                     CarItemGroup.delete().where(CarItemGroup.car == carItem.car).execute()
#                     print '--continue-- ', start
#                 else:
#                     print 'need help 2!'
#                     flag = 1
#         except:
#             print 'need help!'
#             flag = 1
catch_car_item_detail(browser)
