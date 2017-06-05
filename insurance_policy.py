#!/usr/bin/env python
# coding=utf-8
import simplejson
from model import InsuranceArea, SSILubePolicy, Store


# flag:1 单交强，2 单商业， 3 混合
# 太平洋山西返油策略
def ShanXiTaiPingYang():
    lube = [
    {
        "gift": "ZIC X5特级",
        "items": [
            {
                "name": "单交强险",
                "flag": 1,
                "minprice": "",
                "maxprice": "",
                "driver": 1,
                "store": 1
            },
            {
                "name": "交强险+商业险（1200-1499）",
                "flag": 3,
                "minprice": "1200",
                "maxprice": "1499",
                "driver": 3,
                "store": 4
            },
            {
                "name": "交强险+商业险（1500-1799）",
                "flag": 3,
                "minprice": "1500",
                "maxprice": "1799",
                "driver": 3,
                "store": 5
            },
            {
                "name": "交强险+商业险（1800-2099）",
                "flag": 3,
                "minprice": "1800",
                "maxprice": "2099",
                "driver": 3,
                "store": 6
            },
            {
                "name": "交强险+商业险（2100-2399）",
                "flag": 3,
                "minprice": "2100",
                "maxprice": "2399",
                "driver": 3,
                "store": 7
            },
            {
                "name": "交强险+商业险（2400-2699）",
                "flag": 3,
                "minprice": "2400",
                "maxprice": "2699",
                "driver": 3,
                "store": 8
            },
            {
                "name": "交强险+商业险（2700-2999）",
                "flag": 3,
                "minprice": "2700",
                "maxprice": "2999",
                "driver": 3,
                "store": 9
            },
            {
                "name": "交强险+商业险（3000-3299）",
                "flag": 3,
                "minprice": "3000",
                "maxprice": "3299",
                "driver": 3,
                "store": 10
            },
            {
                "name": "交强险+商业险（3300-3599）",
                "flag": 3,
                "minprice": "3300",
                "maxprice": "3599",
                "driver": 3,
                "store": 11
            },
            {
                "name": "交强险+商业险（3600-3899）",
                "flag": 3,
                "minprice": "3600",
                "maxprice": "3899",
                "driver": 3,
                "store": 12
            },
            {
                "name": "交强险+商业险（3900-4199）",
                "flag": 3,
                "minprice": "3900",
                "maxprice": "4199",
                "driver": 3,
                "store": 13
            },
            {
                "name": "交强险+商业险（4200-4499）",
                "flag": 3,
                "minprice": "4200",
                "maxprice": "4499",
                "driver": 3,
                "store": 14
            },
            {
                "name": "交强险+商业险（4500-4799）",
                "flag": 3,
                "minprice": "4500",
                "maxprice": "4799",
                "driver": 3,
                "store": 15
            },
            {
                "name": "交强险+商业险（4800-5099）",
                "flag": 3,
                "minprice": "4800",
                "maxprice": "5099",
                "driver": 3,
                "store": 16
            },
            {
                "name": "交强险+商业险（5100-5399）",
                "flag": 3,
                "minprice": "5100",
                "maxprice": "5399",
                "driver": 3,
                "store": 17
            },
            {
                "name": "交强险+商业险（5400-5699）",
                "flag": 3,
                "minprice": "5400",
                "maxprice": "5699",
                "driver": 3,
                "store": 18
            },
            {
                "name": "交强险+商业险（5700-5999）",
                "flag": 3,
                "minprice": "5700",
                "maxprice": "5999",
                "driver": 3,
                "store": 19
            }
        ]
    },
    {
        "gift": "ZIC X7",
        "items": [
            {
                "name": "交强险+商业险（6000-9999）",
                "flag": 3,
                "minprice": "6000",
                "maxprice": "9999",
                "driver": 3,
                "store": 20
            },
            {
                "name": "交强险+商业险10000以上",
                "flag": 3,
                "minprice": "10000",
                "maxprice": "",
                "driver": 3,
                "store": 21
            },
        ]
    }
    ]
    print '太平洋山西返油策略'
    InsuranceArea.create(area_code='0004', insurance=12, lube_ok=1, dealer_store=1,
                        lube_policy=simplejson.dumps(lube),cash_ok=0, cash_policy='')

# 人保山西返油策略
def ShanXiRenBao():
    lube = [
        {
            "gift": "ZIC X5特级",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 0
                },
                {
                    "name": "交强险+商业险（1200-1399）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1399",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1400-1699）",
                    "flag": 3,
                    "minprice": "1400",
                    "maxprice": "1699",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（1700-1999）",
                    "flag": 3,
                    "minprice": "1700",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 5
                },
                {
                    "name": "交强险+商业险（2000-2299）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2299",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2300-2699）",
                    "flag": 3,
                    "minprice": "2300",
                    "maxprice": "2699",
                    "driver": 3,
                    "store": 7
                },
                {
                    "name": "交强险+商业险（2700-2999）",
                    "flag": 3,
                    "minprice": "2700",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3299）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3299",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3300-3599）",
                    "flag": 3,
                    "minprice": "3300",
                    "maxprice": "3599",
                    "driver": 3,
                    "store": 10
                },
                {
                    "name": "交强险+商业险（3600-3999）",
                    "flag": 3,
                    "minprice": "3600",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4299）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4299",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4300-4599）",
                    "flag": 3,
                    "minprice": "4300",
                    "maxprice": "4599",
                    "driver": 3,
                    "store": 13
                },
                {
                    "name": "交强险+商业险（4600-4899）",
                    "flag": 3,
                    "minprice": "4600",
                    "maxprice": "4899",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（4900-5299）",
                    "flag": 3,
                    "minprice": "4900",
                    "maxprice": "5299",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5300-5599）",
                    "flag": 3,
                    "minprice": "5300",
                    "maxprice": "5599",
                    "driver": 3,
                    "store": 16
                },
                {
                    "name": "交强险+商业险（5600-5999）",
                    "flag": 3,
                    "minprice": "5600",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "交强险+商业险（6000-9999）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "9999",
                    "driver": 3,
                    "store": 18
                },
                {
                    "name": "交强险+商业险10000以上",
                    "flag": 3,
                    "minprice": "10000",
                    "maxprice": "",
                    "driver": 3,
                    "store": 19
                },
            ]
        }
    ]
    print '人保山西返油策略'
    InsuranceArea.create(area_code='0004', insurance=13, lube_ok=1, dealer_store=1,
                         lube_policy=simplejson.dumps(lube), cash_ok=0, cash_policy='')


# 河南周口人保返油策略
def ZhouKouRenBao():
    lube = [
        {
            "gift": "ZIC X5",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1300-1399）",
                    "flag": 2,
                    "minprice": "1300",
                    "maxprice": "1399",
                    "driver": 1,
                    "store": 2
                },
                {
                    "name": "单商业险（1400-1599）",
                    "flag": 2,
                    "minprice": "1300",
                    "maxprice": "1599",
                    "driver": 2,
                    "store": 2
                },
                {
                    "name": "单商业险（1600-1799）",
                    "flag": 2,
                    "minprice": "1600",
                    "maxprice": "1799",
                    "driver": 2,
                    "store": 3
                },
                {
                    "name": "单商业险（1800-1999）",
                    "flag": 2,
                    "minprice": "1800",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2299）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2299",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "单商业险（2300-2499）",
                    "flag": 2,
                    "minprice": "2300",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2799）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2799",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "单商业险（2800-2999）",
                    "flag": 2,
                    "minprice": "2800",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 7
                },
                {
                    "name": "单商业险（3000-3299）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3299",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "单商业险（3300-3499）",
                    "flag": 2,
                    "minprice": "3300",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（3500-3799）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3799",
                    "driver": 3,
                    "store": 10
                },
                {
                    "name": "单商业险（3800-3999）",
                    "flag": 2,
                    "minprice": "3800",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（4000-4299）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4299",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（4300-4499）",
                    "flag": 2,
                    "minprice": "4300",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 13
                },
                {
                    "name": "单商业险（4500-4799）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4799",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "单商业险（4800-4999）",
                    "flag": 2,
                    "minprice": "4800",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "单商业险（5000-5299）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5299",
                    "driver": 3,
                    "store": 16
                },
                {
                    "name": "单商业险（5300-5599）",
                    "flag": 2,
                    "minprice": "5300",
                    "maxprice": "5599",
                    "driver": 3,
                    "store": 17
                },
                {
                    "name": "单商业险（5600-5999）",
                    "flag": 2,
                    "minprice": "5600",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 18
                },
                {
                    "name": "交强险+商业险（1300-1599）",
                    "flag": 3,
                    "minprice": "1300",
                    "maxprice": "1599",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1600-1799）",
                    "flag": 3,
                    "minprice": "1600",
                    "maxprice": "1799",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（1800-1999）",
                    "flag": 3,
                    "minprice": "1800",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 5
                },
                {
                    "name": "交强险+商业险（2000-2299）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2299",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2300-2499）",
                    "flag": 3,
                    "minprice": "2300",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 7
                },
                {
                    "name": "交强险+商业险（2500-2799）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2799",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（2800-2999）",
                    "flag": 3,
                    "minprice": "2800",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3000-3299）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3299",
                    "driver": 3,
                    "store": 10
                },
                {
                    "name": "交强险+商业险（3300-3499）",
                    "flag": 3,
                    "minprice": "3300",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（3500-3799）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3799",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（3800-3999）",
                    "flag": 3,
                    "minprice": "3800",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 13
                },
                {
                    "name": "交强险+商业险（4000-4299）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4299",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（4300-4499）",
                    "flag": 3,
                    "minprice": "4300",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（4500-4799）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4799",
                    "driver": 3,
                    "store": 16
                },
                {
                    "name": "交强险+商业险（4800-4999）",
                    "flag": 3,
                    "minprice": "4800",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 17
                },
                {
                    "name": "交强险+商业险（5000-5299）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5299",
                    "driver": 3,
                    "store": 18
                },
                {
                    "name": "交强险+商业险（5300-5599）",
                    "flag": 3,
                    "minprice": "5300",
                    "maxprice": "5599",
                    "driver": 3,
                    "store": 19
                },
                {
                    "name": "交强险+商业险（5600-5999）",
                    "flag": 3,
                    "minprice": "5600",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 20
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 19
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 21
                },
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 20
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 22
                },
            ]
        }
    ]
    print '周口人保返油策略'
    InsuranceArea.create(area_code='00160016', insurance=13, lube_ok=1, dealer_store=8,
                         lube_policy=simplejson.dumps(lube), cash_ok=0, cash_policy='')

# 河南周口大地返油策略
def ZhouKouDaDi():
    lube = [
        {
            "gift": "ZIC X5",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1300-1399）",
                    "flag": 2,
                    "minprice": "1300",
                    "maxprice": "1399",
                    "driver": 1,
                    "store": 2
                },
                {
                    "name": "单商业险（1400-1699）",
                    "flag": 2,
                    "minprice": "1400",
                    "maxprice": "1699",
                    "driver": 2,
                    "store": 2
                },
                {
                    "name": "单商业险（1700-1899）",
                    "flag": 2,
                    "minprice": "1700",
                    "maxprice": "1899",
                    "driver": 2,
                    "store": 3
                },
                {
                    "name": "单商业险（1900-2199）",
                    "flag": 2,
                    "minprice": "1900",
                    "maxprice": "2199",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "单商业险（2200-2499）",
                    "flag": 2,
                    "minprice": "2200",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "单商业险（2500-2699）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2699",
                    "driver": 3,
                    "store": 5
                },
                {
                    "name": "单商业险（2700-2999）",
                    "flag": 2,
                    "minprice": "2700",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3299）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3299",
                    "driver": 3,
                    "store": 7
                },
                {
                    "name": "单商业险（3300-3499）",
                    "flag": 2,
                    "minprice": "3300",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "单商业险（3500-3799）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3799",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（3800-4099）",
                    "flag": 2,
                    "minprice": "3800",
                    "maxprice": "4099",
                    "driver": 3,
                    "store": 10
                },
                {
                    "name": "单商业险（4100-4299）",
                    "flag": 2,
                    "minprice": "4100",
                    "maxprice": "4299",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（4300-4599）",
                    "flag": 2,
                    "minprice": "4300",
                    "maxprice": "4599",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（4600-4899）",
                    "flag": 2,
                    "minprice": "4600",
                    "maxprice": "4899",
                    "driver": 3,
                    "store": 13
                },
                {
                    "name": "单商业险（4900-5099）",
                    "flag": 2,
                    "minprice": "4900",
                    "maxprice": "5099",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "单商业险（5100-5999）",
                    "flag": 2,
                    "minprice": "5100",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（1200-1399）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1399",
                    "driver": 2,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1400-1699）",
                    "flag": 3,
                    "minprice": "1400",
                    "maxprice": "1699",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1700-1899）",
                    "flag": 3,
                    "minprice": "1700",
                    "maxprice": "1899",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（1900-2199）",
                    "flag": 3,
                    "minprice": "1900",
                    "maxprice": "2199",
                    "driver": 3,
                    "store": 5
                },
                {
                    "name": "交强险+商业险（2200-2499）",
                    "flag": 3,
                    "minprice": "2200",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2699）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2699",
                    "driver": 3,
                    "store": 7
                },
                {
                    "name": "交强险+商业险（2700-2999）",
                    "flag": 3,
                    "minprice": "2700",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3299）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3299",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3300-3499）",
                    "flag": 3,
                    "minprice": "3300",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 10
                },
                {
                    "name": "交强险+商业险（3500-3799）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3799",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（3800-4099）",
                    "flag": 3,
                    "minprice": "3800",
                    "maxprice": "4099",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4100-4299）",
                    "flag": 3,
                    "minprice": "4100",
                    "maxprice": "4299",
                    "driver": 3,
                    "store": 13
                },
                {
                    "name": "交强险+商业险（4300-4599）",
                    "flag": 3,
                    "minprice": "4300",
                    "maxprice": "4599",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（4600-4899）",
                    "flag": 3,
                    "minprice": "4600",
                    "maxprice": "4899",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（4900-5099）",
                    "flag": 3,
                    "minprice": "4900",
                    "maxprice": "5099",
                    "driver": 3,
                    "store": 16
                },
                {
                    "name": "交强险+商业险（5100-5999）",
                    "flag": 3,
                    "minprice": "5100",
                    "maxprice": "5399",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 16
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                },
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 17
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 19
                },
            ]
        }
    ]
    print '周口大地返油策略'
    InsuranceArea.create(area_code='00160016', insurance=10, lube_ok=1, dealer_store=8,
                         lube_policy=simplejson.dumps(lube), cash_ok=0, cash_policy='')


# 宁夏固原人保返油策略
def GuYuanRenBao():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1200-1499）",
                    "flag": 2,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 1,
                    "store": 2
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 7
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 8
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 10
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 13
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 10
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 16
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 18
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 20
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-9999）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "9999",
                    "driver": 3,
                    "store": 17
                },
                {
                    "name": "单商业险10000以上",
                    "flag": 2,
                    "minprice": "10000",
                    "maxprice": "",
                    "driver": 3,
                    "store": 27
                },
                {
                    "name": "交强险+商业险（6000-9999）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "9999",
                    "driver": 3,
                    "store": 20
                },
                {
                    "name": "交强险+商业险10000以上",
                    "flag": 3,
                    "minprice": "10000",
                    "maxprice": "",
                    "driver": 3,
                    "store": 30
                }
            ]
        }
    ]
    print '宁夏固原人保返油策略'
    InsuranceArea.create(area_code='00300004', insurance=13, lube_ok=1, dealer_store=1,
                         lube_policy=simplejson.dumps(lube), cash_ok=0, cash_policy='')

# 宁夏固原平安返油策略
def GuYuanPingAn():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1200-1499）",
                    "flag": 2,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 1,
                    "store": 2
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 7
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 8
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 10
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 13
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 10
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 16
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 18
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 20
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-9999）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "9999",
                    "driver": 3,
                    "store": 17
                },
                {
                    "name": "单商业险10000以上",
                    "flag": 2,
                    "minprice": "10000",
                    "maxprice": "",
                    "driver": 3,
                    "store": 27
                },
                {
                    "name": "交强险+商业险（6000-9999）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "9999",
                    "driver": 3,
                    "store": 20
                },
                {
                    "name": "交强险+商业险10000以上",
                    "flag": 3,
                    "minprice": "10000",
                    "maxprice": "",
                    "driver": 3,
                    "store": 30
                }
            ]
        }
    ]
    print '宁夏固原平安返油策略'
    InsuranceArea.create(area_code='00300004', insurance=7, lube_ok=1, dealer_store=1,
                         lube_policy=simplejson.dumps(lube), cash_ok=0, cash_policy='')

# 宁夏银川人保返油策略
def YinChuanRenBao():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1200-1499）",
                    "flag": 2,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 1,
                    "store": 2
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 7
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 8
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 10
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 13
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 10
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 16
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 18
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 20
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-9999）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "9999",
                    "driver": 3,
                    "store": 17
                },
                {
                    "name": "单商业险10000以上",
                    "flag": 2,
                    "minprice": "10000",
                    "maxprice": "",
                    "driver": 3,
                    "store": 27
                },
                {
                    "name": "交强险+商业险（6000-9999）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "9999",
                    "driver": 3,
                    "store": 20
                },
                {
                    "name": "交强险+商业险10000以上",
                    "flag": 3,
                    "minprice": "10000",
                    "maxprice": "",
                    "driver": 3,
                    "store": 30
                }
            ]
        }
    ]
    print '宁夏银川人保返油策略'
    InsuranceArea.create(area_code='00300001', insurance=13, lube_ok=1, dealer_store=26,
                         lube_policy=simplejson.dumps(lube), cash_ok=0, cash_policy='')
    InsuranceArea.create(area_code='00300003', insurance=13, lube_ok=1, dealer_store=26,
                         lube_policy=simplejson.dumps(lube), cash_ok=0, cash_policy='')
    InsuranceArea.create(area_code='00300005', insurance=13, lube_ok=1, dealer_store=26,
                         lube_policy=simplejson.dumps(lube), cash_ok=0, cash_policy='')


# 宁夏银川国寿财返油策略
def YinChuanGuoShouCai():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1200-1499）",
                    "flag": 2,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 1,
                    "store": 2
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 7
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 8
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 10
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 13
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 10
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 16
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 18
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 20
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-9999）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "9999",
                    "driver": 3,
                    "store": 17
                },
                {
                    "name": "单商业险10000以上",
                    "flag": 2,
                    "minprice": "10000",
                    "maxprice": "",
                    "driver": 3,
                    "store": 27
                },
                {
                    "name": "交强险+商业险（6000-9999）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "9999",
                    "driver": 3,
                    "store": 20
                },
                {
                    "name": "交强险+商业险10000以上",
                    "flag": 3,
                    "minprice": "10000",
                    "maxprice": "",
                    "driver": 3,
                    "store": 30
                }
            ]
        }
    ]
    print '宁夏银川国寿财返油策略'
    InsuranceArea.create(area_code='00300001', insurance=11, lube_ok=1, dealer_store=26,
                         lube_policy=simplejson.dumps(lube), cash_ok=0, cash_policy='')
    InsuranceArea.create(area_code='00300003', insurance=11, lube_ok=1, dealer_store=26,
                         lube_policy=simplejson.dumps(lube), cash_ok=0, cash_policy='')
    InsuranceArea.create(area_code='00300005', insurance=11, lube_ok=1, dealer_store=26,
                         lube_policy=simplejson.dumps(lube), cash_ok=0, cash_policy='')

# 陕西人保返油、返现策略
def ShannXiRenBao():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    lubex5 = [
        {
            "gift": "ZIC X5",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    cash = {
        "ar": 0,
        "ber": 23.0,
        "ber2": 23.0,
        "bm": 0,
        "btr": 0,
        "fer": 23.0,
        "fer2": 23.0,
        "ftr": 0,
        "pr": 0
    }
    print '陕西人保返油、返现策略'
    # 西安
    InsuranceArea.create(area_code='00270001', insurance=13, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 宝鸡
    InsuranceArea.create(area_code='00270003', insurance=13, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 咸阳
    InsuranceArea.create(area_code='00270004', insurance=13, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 渭南
    InsuranceArea.create(area_code='00270005', insurance=13, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 汉中
    InsuranceArea.create(area_code='00270007', insurance=13, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))

    # 安康
    InsuranceArea.create(area_code='00270009', insurance=13, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 商洛
    InsuranceArea.create(area_code='00270010', insurance=13, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))


# 陕西中华联合返油、返现策略
def ShannXiZhongHuaLianHe():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    lubex5 = [
        {
            "gift": "ZIC X5",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    cash = {
        "ar": 0,
        "ber": 25.0,
        "ber2": 25.0,
        "bm": 0,
        "btr": 0,
        "fer": 25.0,
        "fer2": 25.0,
        "ftr": 0,
        "pr": 0
    }
    print '陕西中华联合返油、返现策略'
    # 西安
    InsuranceArea.create(area_code='00270001', insurance=1, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 宝鸡
    InsuranceArea.create(area_code='00270003', insurance=1, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 咸阳
    InsuranceArea.create(area_code='00270004', insurance=1, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 渭南
    InsuranceArea.create(area_code='00270005', insurance=1, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 汉中
    InsuranceArea.create(area_code='00270007', insurance=1, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))

    # 安康
    InsuranceArea.create(area_code='00270009', insurance=1, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 商洛
    InsuranceArea.create(area_code='00270010', insurance=1, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))


# 陕西平安返油、返现策略
def ShannXiPingAn():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    lubex5 = [
        {
            "gift": "ZIC X5",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    cash = {
        "ar": 0,
        "ber": 23.0,
        "ber2": 23.0,
        "bm": 0,
        "btr": 0,
        "fer": 23.0,
        "fer2": 23.0,
        "ftr": 0,
        "pr": 0
    }
    print '陕西平安返油、返现策略'
    # 西安
    InsuranceArea.create(area_code='00270001', insurance=7, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 宝鸡
    InsuranceArea.create(area_code='00270003', insurance=7, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 咸阳
    InsuranceArea.create(area_code='00270004', insurance=7, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 渭南
    InsuranceArea.create(area_code='00270005', insurance=7, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 汉中
    InsuranceArea.create(area_code='00270007', insurance=7, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))

    # 安康
    InsuranceArea.create(area_code='00270009', insurance=7, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 商洛
    InsuranceArea.create(area_code='00270010', insurance=7, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))


# 陕西安盛返油、返现策略
def ShannXiAnSheng():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    lubex5 = [
        {
            "gift": "ZIC X5",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-2499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    cash = {
        "ar": 0,
        "ber": 27.0,
        "ber2": 27.0,
        "bm": 0,
        "btr": 0,
        "fer": 27.0,
        "fer2": 27.0,
        "ftr": 0,
        "pr": 0
    }
    print '陕西安盛返油、返现策略'
    # 西安
    InsuranceArea.create(area_code='00270001', insurance=15, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 宝鸡
    InsuranceArea.create(area_code='00270003', insurance=15, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 咸阳
    InsuranceArea.create(area_code='00270004', insurance=15, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 渭南
    InsuranceArea.create(area_code='00270005', insurance=15, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 汉中
    InsuranceArea.create(area_code='00270007', insurance=15, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))

    # 安康
    InsuranceArea.create(area_code='00270009', insurance=15, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 商洛
    InsuranceArea.create(area_code='00270010', insurance=15, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))


# 陕西天安返油、返现策略
def ShannXiTianAn():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    lubex5 = [
        {
            "gift": "ZIC X5",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    cash = {
        "ar": 0,
        "ber": 32.0,
        "ber2": 32.0,
        "bm": 0,
        "btr": 0,
        "fer": 32.0,
        "fer2": 32.0,
        "ftr": 0,
        "pr": 0
    }
    print '陕西天安返油、返现策略'
    # 西安
    InsuranceArea.create(area_code='00270001', insurance=9, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 宝鸡
    InsuranceArea.create(area_code='00270003', insurance=9, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 咸阳
    InsuranceArea.create(area_code='00270004', insurance=9, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 渭南
    InsuranceArea.create(area_code='00270005', insurance=9, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 汉中
    InsuranceArea.create(area_code='00270007', insurance=9, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))

    # 安康
    InsuranceArea.create(area_code='00270009', insurance=9, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 商洛
    InsuranceArea.create(area_code='00270010', insurance=9, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))

# 陕西太平洋返油、返现策略
def ShannXiTaiPingYang():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    lubex5 = [
        {
            "gift": "ZIC X5",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    cash = {
        "ar": 0,
        "ber": 28.0,
        "ber2": 28.0,
        "bm": 0,
        "btr": 0,
        "fer": 28.0,
        "fer2": 28.0,
        "ftr": 0,
        "pr": 0
    }
    print '陕西太平洋返油、返现策略'
    # 西安
    InsuranceArea.create(area_code='00270001', insurance=12, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 宝鸡
    InsuranceArea.create(area_code='00270003', insurance=12, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 咸阳
    InsuranceArea.create(area_code='00270004', insurance=12, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 渭南
    InsuranceArea.create(area_code='00270005', insurance=12, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 汉中
    InsuranceArea.create(area_code='00270007', insurance=12, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))

    # 安康
    InsuranceArea.create(area_code='00270009', insurance=12, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 商洛
    InsuranceArea.create(area_code='00270010', insurance=12, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))


# 陕西大地返油、返现策略
def ShannXiDaDi():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    lubex5 = [
        {
            "gift": "ZIC X5",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    cash = {
        "ar": 0,
        "ber": 30.0,
        "ber2": 30.0,
        "bm": 0,
        "btr": 0,
        "fer": 30.0,
        "fer2": 30.0,
        "ftr": 0,
        "pr": 0
    }
    print '陕西大地返油、返现策略'
    # 西安
    InsuranceArea.create(area_code='00270001', insurance=10, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 宝鸡
    InsuranceArea.create(area_code='00270003', insurance=10, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 咸阳
    InsuranceArea.create(area_code='00270004', insurance=10, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 渭南
    InsuranceArea.create(area_code='00270005', insurance=10, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 汉中
    InsuranceArea.create(area_code='00270007', insurance=10, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))

    # 安康
    InsuranceArea.create(area_code='00270009', insurance=10, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 商洛
    InsuranceArea.create(area_code='00270010', insurance=10, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))


# 陕西太平返油、返现策略
def ShannXiTaiPing():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    lubex5 = [
        {
            "gift": "ZIC X5",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    cash = {
        "ar": 0,
        "ber": 31.0,
        "ber2": 31.0,
        "bm": 0,
        "btr": 0,
        "fer": 31.0,
        "fer2": 31.0,
        "ftr": 0,
        "pr": 0
    }
    print '陕西太平返油、返现策略'
    # 西安
    InsuranceArea.create(area_code='00270001', insurance=6, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 宝鸡
    InsuranceArea.create(area_code='00270003', insurance=6, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 咸阳
    InsuranceArea.create(area_code='00270004', insurance=6, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 渭南
    InsuranceArea.create(area_code='00270005', insurance=6, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 汉中
    InsuranceArea.create(area_code='00270007', insurance=6, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))

    # 安康
    InsuranceArea.create(area_code='00270009', insurance=6, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 商洛
    InsuranceArea.create(area_code='00270010', insurance=6, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))

# 陕西永安返油、返现策略
def ShannXiYongAn():
    lube = [
        {
            "gift": "ZIC X5特",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    lubex5 = [
        {
            "gift": "ZIC X5",
            "items": [
                {
                    "name": "单交强险",
                    "flag": 1,
                    "minprice": "",
                    "maxprice": "",
                    "driver": 1,
                    "store": 1
                },
                {
                    "name": "单商业险（1500-1999）",
                    "flag": 2,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 1,
                    "store": 3
                },
                {
                    "name": "单商业险（2000-2499）",
                    "flag": 2,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 1,
                    "store": 5
                },
                {
                    "name": "单商业险（2500-2999）",
                    "flag": 2,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 1,
                    "store": 6
                },
                {
                    "name": "单商业险（3000-3499）",
                    "flag": 2,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 2,
                    "store": 7
                },
                {
                    "name": "单商业险（3500-3999）",
                    "flag": 2,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 2,
                    "store": 9
                },
                {
                    "name": "单商业险（4000-4499）",
                    "flag": 2,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "单商业险（4500-4999）",
                    "flag": 2,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "单商业险（5000-5499）",
                    "flag": 2,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "单商业险（5500-5999）",
                    "flag": 2,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（1200-1499）",
                    "flag": 3,
                    "minprice": "1200",
                    "maxprice": "1499",
                    "driver": 3,
                    "store": 3
                },
                {
                    "name": "交强险+商业险（1500-1999）",
                    "flag": 3,
                    "minprice": "1500",
                    "maxprice": "1999",
                    "driver": 3,
                    "store": 4
                },
                {
                    "name": "交强险+商业险（2000-2499）",
                    "flag": 3,
                    "minprice": "2000",
                    "maxprice": "2499",
                    "driver": 3,
                    "store": 6
                },
                {
                    "name": "交强险+商业险（2500-2999）",
                    "flag": 3,
                    "minprice": "2500",
                    "maxprice": "2999",
                    "driver": 3,
                    "store": 8
                },
                {
                    "name": "交强险+商业险（3000-3499）",
                    "flag": 3,
                    "minprice": "3000",
                    "maxprice": "3499",
                    "driver": 3,
                    "store": 9
                },
                {
                    "name": "交强险+商业险（3500-3999）",
                    "flag": 3,
                    "minprice": "3500",
                    "maxprice": "3999",
                    "driver": 3,
                    "store": 11
                },
                {
                    "name": "交强险+商业险（4000-4499）",
                    "flag": 3,
                    "minprice": "4000",
                    "maxprice": "4499",
                    "driver": 3,
                    "store": 12
                },
                {
                    "name": "交强险+商业险（4500-4999）",
                    "flag": 3,
                    "minprice": "4500",
                    "maxprice": "4999",
                    "driver": 3,
                    "store": 14
                },
                {
                    "name": "交强险+商业险（5000-5499）",
                    "flag": 3,
                    "minprice": "5000",
                    "maxprice": "5499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（5500-5999）",
                    "flag": 3,
                    "minprice": "5500",
                    "maxprice": "5999",
                    "driver": 3,
                    "store": 17
                }
            ]
        },
        {
            "gift": "ZIC X7",
            "items": [
                {
                    "name": "单商业险（6000-12499）",
                    "flag": 2,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险（6000-12499）",
                    "flag": 3,
                    "minprice": "6000",
                    "maxprice": "12499",
                    "driver": 3,
                    "store": 18
                }
            ]
        },
        {
            "gift": "ZIC X9",
            "items": [
                {
                    "name": "单商业险12500以上",
                    "flag": 2,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 15
                },
                {
                    "name": "交强险+商业险12500以上",
                    "flag": 3,
                    "minprice": "12500",
                    "maxprice": "",
                    "driver": 3,
                    "store": 18
                }
            ]
        }
    ]

    cash = {
        "ar": 0,
        "ber": 28.0,
        "ber2": 28.0,
        "bm": 0,
        "btr": 0,
        "fer": 28.0,
        "fer2": 28.0,
        "ftr": 0,
        "pr": 0
    }
    print '陕西永安返油、返现策略'
    # 西安
    InsuranceArea.create(area_code='00270001', insurance=8, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 宝鸡
    InsuranceArea.create(area_code='00270003', insurance=8, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 咸阳
    InsuranceArea.create(area_code='00270004', insurance=8, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 渭南
    InsuranceArea.create(area_code='00270005', insurance=8, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 汉中
    InsuranceArea.create(area_code='00270007', insurance=8, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lubex5), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))

    # 安康
    InsuranceArea.create(area_code='00270009', insurance=8, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))
    # 商洛
    InsuranceArea.create(area_code='00270010', insurance=8, lube_ok=1,
                         dealer_store=15,
                         lube_policy=simplejson.dumps(lube), cash_ok=1,
                         cash_policy=simplejson.dumps(cash))

def update_store_policy():
    SSILubePolicy.delete().execute()
    stores = Store.select().where(Store.active == 1)


    for store in stores:
        run_four_code = True
        extras = ['003000030003', # 宁夏吴忠市同心县
                  '003000050003', # 宁夏中卫市海原县
                  '002800080007' # 甘肃平凉市静宁县
                  ]
        if (store.area_code in extras) or (store.address.find('红寺堡')>=0):
            insurace_area = InsuranceArea.select().where(
                (InsuranceArea.area_code == '00300004') & (InsuranceArea.active == 1))
        else:
            insurace_area = InsuranceArea.select().where(
                (InsuranceArea.area_code == store.area_code[:8]) & (InsuranceArea.active == 1))
        for item in insurace_area:
            run_four_code = False
            print '1---', store.name, item.insurance.name, store.area_code[:8]
            SSILubePolicy.create(store=store,
                                     insurance=item.insurance,
                                     cash=item.cash_policy,
                                     dealer_store=item.dealer_store,
                                     lube=item.lube_policy)
        if run_four_code:
            insurace_area2 = InsuranceArea.select().where(
                (InsuranceArea.area_code == store.area_code[:4]) & (InsuranceArea.active == 1))
            for item in insurace_area2:
                print '2---', store.name, item.insurance.name, store.area_code[:4]
                SSILubePolicy.create(store=store,
                                         insurance=item.insurance,
                                         cash=item.cash_policy,
                                         dealer_store=item.dealer_store,
                                         lube=item.lube_policy)

if __name__ == '__main__':
    InsuranceArea.delete().execute()
    ShanXiTaiPingYang()
    ShanXiRenBao()
    ZhouKouRenBao()
    ZhouKouDaDi()
    GuYuanPingAn()
    GuYuanRenBao()
    YinChuanRenBao()
    YinChuanGuoShouCai()
    ShannXiRenBao()
    ShannXiZhongHuaLianHe()
    ShannXiPingAn()
    ShannXiAnSheng()
    ShannXiTianAn()
    ShannXiTaiPingYang()
    ShannXiDaDi()
    ShannXiTaiPing()
    ShannXiYongAn()
    update_store_policy()
