# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BoxOfficeItem(scrapy.Item):
    film_id = scrapy.Field()
    entries = scrapy.Field()
