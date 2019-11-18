# -*- coding: utf-8 -*-
import scrapy
from boohee.items import BooheeItem
from urllib import parse


class BooheeSpiderSpider(scrapy.Spider):
    name = 'boohee_spider'
    allowed_domains = ['www.boohee.com']
    start_urls = ['http://www.boohee.com/food/view_group/1']
    handle_httpstatus_list = [404]

    def parse(self, response):
        """
        解析食品列表
        :param response:
        :return:
        """
        url_parts = parse.urlparse(response.url)
        view_group_id = int(url_parts.path.split('/')[-1])
        view_group = response.css('.crumb').xpath('text()').extract_first()
        if view_group:
            view_group = view_group.strip(' /')
        if not view_group:  # 分组内容为空，表明爬取到空分组了，爬取结束
            return True

        # 食品列表
        food_list = response.css('.food-list').xpath('li')
        for food in food_list:
            food_item = BooheeItem()
            food_item['view_group'] = view_group_id
            food_item['view_group_name'] = view_group
            # 发起食品详情抓取
            food_url = 'http://www.boohee.com' + food.css('.text-box').xpath('h4/a/@href').extract_first()
            yield scrapy.Request(url=food_url, callback=self.parse_item, meta={'item': food_item}, dont_filter=True)
        next_page = response.css('.widget-pagination').css('.next_page').xpath('@href').extract_first()
        if next_page:  # 有下一页，查下一页
            yield scrapy.Request(url='https://www.boohee.com' + next_page,
                                 callback=self.parse)
        else:  # 无下一页，查下一分组
            self.logger.info('next view_group_id: %s', view_group_id + 1)
            yield scrapy.Request(url='https://www.boohee.com/food/view_group/{0}'.format(view_group_id + 1),
                                 callback=self.parse)

    def parse_item(self, response):
        """
        解析食物详情
        :param response:
        :return:
        """
        if 'item' in response.meta:
            item = response.meta['item']
        else:
            item = BooheeItem()
        url_parts = parse.urlparse(response.url)
        item['pinyin'] = url_parts.path.split('/')[-1]

        if response.status == 404:
            item['not_found'] = 1
            yield item
            return

        detail = response.css('.widget-food-detail')
        # 名称
        title = detail.xpath('h3[1]/text()').extract_first()
        item['name'] = title.split('的')[0]

        # 基本信息
        info_content = detail.xpath('div[@class="content"]')
        item['image'] = info_content.css('.food-pic').xpath('a/@href').extract_first()
        item['thumb'] = info_content.css('.food-pic').xpath('a/img/@src').extract_first()
        basic_info = info_content.css('.basic-infor').xpath('li')
        for info in basic_info:
            name = info.xpath('b/text()').extract_first()
            if name == '别名：':
                value = info.xpath('text()').extract_first()
                item['nickname'] = value
            elif name == '热量：':
                value = info.xpath('span[@id="food-calory"]/span/text()').extract_first() + ' ' \
                        + info.xpath('span[@id="food-calory"]/text()').extract_first()
                item['calorie'] = value
            elif name == '分类：':
                href = info.xpath('*/a/@href').extract_first()
                title = info.xpath('*/a/text()').extract_first()
                if href:
                    href_parts = href.split('/')
                    if href_parts[-2] == 'group':
                        item['group'] = href_parts[-1]
                        item['group_name'] = title
                    elif href_parts[-2] == 'view_group':
                        item['view_group'] = href_parts[-1]
                        item['view_group_name'] = title
            elif name == '红绿灯：':
                item['light'] = info.xpath('img/@src').extract_first()
        for p in info_content.xpath('p'):
            if p.xpath('b/text()').extract_first() == '评价：':
                comment_str = ''
                comments = p.xpath('text()').extract()
                for comment in comments:
                    comment = comment.strip('\n ')
                    comment_str += comment
                item['comment'] = comment_str

        # 营养信息
        item['nutrition'] = []
        nutrition_list = detail.css('.nutr-tag').css('.content').xpath('dl[not(@class)]/dd')
        for nutrition in nutrition_list:
            nutrition_type = nutrition.xpath('span[1]/text()').extract_first()
            if nutrition_type == '热量(大卡)':
                amount = nutrition.xpath('span[2]/span/text()').extract_first()
            else:
                amount = nutrition.xpath('span[2]/text()').extract_first()
            item['nutrition'].append({
                'nutrition_type': nutrition_type,
                'amount': amount
            })

        # 度量单位
        item['widget_unit'] = []
        widget_unit_list = detail.css('.widget-unit').css('.content').xpath('table/tbody/tr')
        for widget_unit in widget_unit_list:
            if widget_unit.css('.right'):
                unit = widget_unit.xpath('td[1]/text()').extract_first()
                value = widget_unit.xpath('td[2]/text()').extract_first()
                item['widget_unit'].append({
                    'unit': unit,
                    'value': value,
                    'is_standard': 1
                })
            else:
                unit = widget_unit.xpath('td[1]/span/text()').extract_first()
                value = widget_unit.xpath('td[2]/span/text()').extract_first()
                item['widget_unit'].append({
                    'unit': unit,
                    'value': value,
                    'is_standard': 0
                })

        # 相关食物
        item['related_food'] = []
        related_food_list = detail.css('.widget-relative').css('.content').xpath('ul/li')
        for related_food in related_food_list:
            food_url = related_food.xpath('a/@href').extract_first()
            food_url_parts = food_url.split('/')
            food_pinyin = food_url_parts[-1]
            food_name = related_food.xpath('a/span/text()').extract_first()
            item['related_food'].append({
                'pinyin': food_pinyin,
                'name': food_name
            })
            # 抓取相关食物
            food_url = 'https://www.boohee.com' + food_url
            yield scrapy.Request(url=food_url, callback=self.parse_item)

        # 原料
        item['ingredients'] = []
        widget_more_list = detail.css('.widget-more').xpath('*')
        if widget_more_list:
            ingredient_type = ''
            for node in widget_more_list:
                node_str = node.extract()
                if "h3" in node_str:
                    ingredient_type = node.xpath('text()').extract_first()
                elif 'content' in node_str:
                    if node.xpath('ul'):
                        ingredient_list = node.xpath('ul/li')
                        for ingredient in ingredient_list:
                            if ingredient.xpath('a'):
                                name = ingredient.xpath('a/text()').extract_first()
                                href = ingredient.xpath('a/@href').extract_first()
                                pinyin = href.split('/')[-1]
                                amount = ingredient.xpath('text()').extract_first()
                                item['ingredients'].append({
                                    'name': name,
                                    'pinyin': pinyin,
                                    'amount': amount,
                                    'ingredient_type': ingredient_type
                                })
                                # 抓取相关原料
                                food_url = 'https://www.boohee.com' + href
                                yield scrapy.Request(url=food_url, callback=self.parse_item)
                            else:
                                ingredient_str = ingredient.xpath('text()').extract_first()
                                if ingredient_str:
                                    ingredient_parts = ingredient_str.split(' ')
                                    if len(ingredient_parts) >= 2:
                                        name = ingredient_parts[0]
                                        amount = ingredient_parts[1]
                                        item['ingredients'].append({
                                            'name': name,
                                            'pinyin': '',
                                            'amount': amount,
                                            'ingredient_type': ingredient_type
                                        })
                    elif node.xpath('p'):
                        item['instruction'] = node.xpath('p').extract()

        # 来源
        item['source'] = detail.css('.widget-source').css('.source').xpath('text()').extract_first()
        # 完整的页面
        item['html'] = response.body.decode(response.encoding)
        yield item
