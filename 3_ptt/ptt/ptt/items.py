# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PttItem(scrapy.Item):
    url=scrapy.Field()
    title=scrapy.Field()
    author=scrapy.Field()
    date=scrapy.Field()
    score=scrapy.Field()
    pushes=scrapy.Field()
    comments=scrapy.Field()
    



