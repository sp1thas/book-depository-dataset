# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy  # type: ignore


class BookItem(scrapy.Item):
    _id = scrapy.Field(serialize=str)
    authors = scrapy.Field(serialize=list)
    bestsellers_rank = scrapy.Field(serialize=int)
    categories = scrapy.Field(serialize=list)
    description = scrapy.Field(serialize=str)
    dimensions = scrapy.Field(serialize=str)
    edition = scrapy.Field(serialize=str)
    edition_statement = scrapy.Field(serialize=str)
    for_ages = scrapy.Field(serialize=str)
    format = scrapy.Field(serialize=str)
    illustrations_note = scrapy.Field(serialize=str)
    image_urls = scrapy.Field(serialize=list)
    images = scrapy.Field()
    imprint = scrapy.Field(serialize=str)
    indexed_date = scrapy.Field(serialize=str)
    isbn10 = scrapy.Field(serialize=str)
    isbn13 = scrapy.Field(serialize=str)
    language = scrapy.Field(serialize=str)
    price = scrapy.Field(serialize=float)
    publication_city_country = scrapy.Field(serialize=str)
    publication_date = scrapy.Field(serialize=str)
    publisher = scrapy.Field(serialize=str)
    rating_avg = scrapy.Field(serialize=float)
    rating_count = scrapy.Field(serialize=int)
    title = scrapy.Field(serialize=str)
    url = scrapy.Field(serialize=str)
