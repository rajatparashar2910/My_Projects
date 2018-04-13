# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RankingItem(scrapy.Item):

    place_name = scrapy.Field()
    over_all_rank = scrapy.Field()
    INCOME = scrapy.Field()
    HOUSING_AFFORDABILITY = scrapy.Field()
    WELLBEING = scrapy.Field()
    SAFETY = scrapy.Field()
    EDUCATION = scrapy.Field()
    LIFE_EXPECTANCY = scrapy.Field()
    ENVIRONMENT = scrapy.Field()
    CULTURE = scrapy.Field()

class FoodItem(scrapy.Item):

    name = scrapy.Field()
    url = scrapy.Field()