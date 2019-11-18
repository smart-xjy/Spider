# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BooheeItem(scrapy.Item):
    name = scrapy.Field()  # 名称
    image = scrapy.Field()  # 图片
    thumb = scrapy.Field()  # 缩略图
    pinyin = scrapy.Field()  # 拼音
    nickname = scrapy.Field()  # 别名
    calorie = scrapy.Field()  # 热量
    view_group = scrapy.Field()  # 小分组 id
    view_group_name = scrapy.Field()  # 小分组名
    group = scrapy.Field()  # 大分组id
    group_name = scrapy.Field()  # 大分组名
    light = scrapy.Field()  # 红绿灯
    comment = scrapy.Field()  # 评价
    source = scrapy.Field()  # 来源
    instruction = scrapy.Field()  # 详细说明
    ingredients = scrapy.Field()  # 原料
    related_food = scrapy.Field()  # 相关食物
    widget_unit = scrapy.Field()  # 度量单位
    nutrition = scrapy.Field()  # 营养信息
    html = scrapy.Field()  # html
    not_found = scrapy.Field()  # 404
