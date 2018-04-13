# -*- coding: utf-8 -*-
"""
@author:J.Zhou

@contact:zyfzjsc988@outlook.com

@file:rankSpider.py

@time:2017/11/13 10:42

@desc:

"""

import scrapy
from ranking.items import RankingItem
import json
import logging
tlist = []
for i in range(1,381):
    tlist.append("https://bbc001.carto.com/api/v1/map/bbc001@454ab34f@7c82cfb90be773dbb0c11a6ee23e32d7:1505124712927/1/attributes/%d" % i)

class rankSpider(scrapy.Spider):
    # 爬虫名称
    name = 'rank'
    # 允许域名
    allowed_domains = ["carto.com"]

    # 开始URL
    start_urls = tlist

    # 解析内容函数
    def parse(self, response):
        # 使用xpath匹配每个response
        # xpath()返回值为selectorList
        for sel in response.xpath("//body/p/text()"):
            json_form = json.loads(sel.extract())
            item = RankingItem()
            item['place_name'] = json_form['lad_women_']
            item['over_all_rank'] = json_form['lad_wome_2']
            item['INCOME'] = json_form['lad_wome_3']
            item['HOUSING_AFFORDABILITY'] = json_form['lad_wome_4']
            item['WELLBEING'] = json_form['lad_wome_5']
            item['SAFETY'] = json_form['lad_wome_6']
            item['EDUCATION'] = json_form['lad_wome_7']
            item['LIFE_EXPECTANCY'] = json_form['lad_wome_8']
            item['ENVIRONMENT'] = json_form['lad_wome_9']
            item['CULTURE'] = int(json_form['lad_wome10'])


            yield(item)

