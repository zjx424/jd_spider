# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class JdItem(scrapy.Item):    # 标题
    price=scrapy.Field()
    price_url=scrapy.Field()
    _id=scrapy.Field()
    url=scrapy.Field()
    title=scrapy.Field()
    brand=scrapy.Field()
    分辨率=scrapy.Field()
    后置摄像头=scrapy.Field()
    前置摄像头=scrapy.Field()
    cpu型号=scrapy.Field()
    ROM = scrapy.Field()
    RAM = scrapy.Field()
    主屏幕尺寸=scrapy.Field()
