# -*- coding: utf-8 -*-
"""
@author:J.Zhou

@contact:zyfzjsc988@outlook.com

@file:food.py

@time:2017/11/20 21:25

@desc:

"""

import scrapy
import urllib2
import json
import logging
from ranking.items import FoodItem
def download(url,name):

    html = urllib2.urlopen(url)
    data = html.read()
    print data
    # with open('food_hy/'+str(name)+'.xml','wb') as file:
    #     file.write(data)

class rankSpider(scrapy.Spider):
    # 爬虫名称
    name = 'foodhygiene'
    # 允许域名
    allowed_domains = ["gov.uk"]

    # 开始URL
    start_urls = ['http://ratings.food.gov.uk/open-data/en-GB']

    # 解析内容函数
    def parse(self, response):
        # 使用xpath匹配每个response
        # xpath()返回值为selectorList
        for sel in response.xpath('//div[contains(@id,"openDataStatic")]/table'):
            # print sel.xpath('tr/td/a[1]')
            for text in sel.xpath('tr/td/a[1]'):

                # item = FoodItem()
                url = text.xpath('@href').extract()[0]
                # item['url'] = text.xpath('/@href').extract()
                name = text.xpath('@title').extract()[0]
                #
                # print url + ' '+ name
                # item['name'] = text.xpath('/@title').extract()
                # yield (item)
                download(url,name)


