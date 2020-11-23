# -*- coding: utf-8 -*-
import datetime
import logging
import re
from random import shuffle

import pymongo
import scrapy
from scrapy.utils.project import get_project_settings
from slugify import slugify

from ..items import BookItem

settings = get_project_settings()


class BdepobooksSpider(scrapy.Spider):
    name = "bdepobooks"
    allowed_domains = ["bookdepository.com"]

    client = None
    if settings.get("MONGO_URI"):
        client = pymongo.MongoClient(settings["MONGO_URI"])
        db = client[settings["MONGO_DATABASE"]]
        col = db["dataset"]

    start_urls = [
        "https://www.bookdepository.com/category/2/Art-Photography",
        "https://www.bookdepository.com/category/3389/Audio-Books",
        "https://www.bookdepository.com/category/213/Biography",
        "https://www.bookdepository.com/category/928/Business-Finance-Law",
        "https://www.bookdepository.com/category/2455/Childrens-Books",
        "https://www.bookdepository.com/category/1897/Computing",
        "https://www.bookdepository.com/category/2942/Crafts-Hobbies",
        "https://www.bookdepository.com/category/2616/Crime-Thriller",
        "https://www.bookdepository.com/category/240/Dictionaries-Languages",
        "https://www.bookdepository.com/category/3245/Entertainment",
        "https://www.bookdepository.com/category/333/Fiction",
        "https://www.bookdepository.com/category/2858/Food-Drink",
        "https://www.bookdepository.com/category/2633/Graphic-Novels-Anime-Manga",
        "https://www.bookdepository.com/category/2770/Health",
        "https://www.bookdepository.com/category/2638/History-Archaeology",
        "https://www.bookdepository.com/category/2892/Home-Garden",
        "https://www.bookdepository.com/category/2978/Humour",
        "https://www.bookdepository.com/category/1279/Medical",
        "https://www.bookdepository.com/category/2819/Mind-Body-Spirit",
        "https://www.bookdepository.com/category/2985/Natural-History",
        "https://www.bookdepository.com/category/2802/Personal-Development",
        "https://www.bookdepository.com/category/283/Poetry-Drama",
        "https://www.bookdepository.com/category/375/Reference",
        "https://www.bookdepository.com/category/3120/Religion",
        "https://www.bookdepository.com/category/2630/Romance",
        "https://www.bookdepository.com/category/1476/Science-Geography",
        "https://www.bookdepository.com/category/2623/Science-Fiction-Fantasy-Horror",
        "https://www.bookdepository.com/category/632/Society-Social-Sciences",
        "https://www.bookdepository.com/category/3013/Sport",
        "https://www.bookdepository.com/category/3385/Stationery",
        "https://www.bookdepository.com/category/3328/Teaching-Resources-Education",
        "https://www.bookdepository.com/category/1708/Technology-Engineering",
        "https://www.bookdepository.com/category/3391/Teen-Young-Adult",
        "https://www.bookdepository.com/category/2967/Transport",
        "https://www.bookdepository.com/category/3098/Travel-Holiday-Guides",
    ]
    shuffle(start_urls)

    def parse(self, response):
        for subcategory_url in response.xpath(
            '//ul[@class="category-list sidebar-nav has-parent"]/li[position() > 4]/a/@href'
        ).getall():
            yield scrapy.Request(
                url="https://www.bookdepository.com" + subcategory_url,
                callback=self.parse_subcategory,
            )

    def parse_subcategory(self, response):
        for book_url in response.xpath(
            '//div[@class="book-item"]//h3/a/@href'
        ).getall():
            book_url = "https://www.bookdepository.com" + book_url
            book_id = re.findall(r"\/(\d+)", book_url)
            if book_id:
                book_id = book_id[0]
            else:
                logging.error("could not extract book id from url: {}".format(book_url))
                continue
            # try:
            #     d = self.col.find_one({"_id": int(book_id)})
            # except Exception as e:
            #     print('error {}'.format(book_id))
            #     d = False
            # if d is False:
            #     continue
            # elif d:
            #     logging.debug('{} already harvested {}'.format(book_id, book_url))
            #     continue
            # else:
            yield scrapy.Request(url=book_url, callback=self.parse_book)

        next_href = response.xpath('//li[@id="next-top"]/a/@href').extract_first()
        if next_href:
            yield scrapy.Request(
                url="https://www.bookdepository.com" + next_href,
                callback=self.parse_subcategory,
            )

    @staticmethod
    def extract_authors(response):
        ua = set()
        for author in response.xpath(
            '//div[@class="item-block"]//span[@itemprop="author"]/@itemscope'
        ).getall():
            ua.add(author.strip())
        return list(ua)

    @staticmethod
    def extract_categories(response):
        ucats = set()
        t = response.xpath('//ol[@class="breadcrumb"]/li[1]/text()').extract_first()
        if "Categories:" not in t:
            logging.warning("different breadcrumb type: {}".format(t))
            return []

        categories = []
        for category in response.xpath('//ol[@class="breadcrumb"]/li/a'):
            category_name = category.xpath("./text()").extract_first()
            category_url = category.xpath("./@href").extract_first()
            category_id = int(re.findall(r"category/(\d+)", category_url)[0])
            if category_id in ucats:
                continue
            ucats.add(category_id)
            categories.append({"name": category_name.strip(), "id": category_id})
        return categories

    def parse_book(self, response):
        book = BookItem()
        book["description"] = response.xpath(
            '//div[@class="item-description"]/div/text()'
        ).extract_first()
        book["title"] = response.xpath("//h1/text()").extract_first()
        book["image_urls"] = [
            response.xpath('//div[@class="item-img-content"]/img/@src').extract_first()
        ]
        rating_avg = response.xpath(
            '//span[@itemprop="ratingValue"]/text()'
        ).extract_first()
        price = response.xpath('//span[@class="sale-price"]/text()').extract_first()
        if price:
            try:
                price = float(re.findall(r"\d+,\d+", price)[0])
            except Exception as e:
                price = None
        else:
            price = None

        if rating_avg:
            try:
                rating_avg = float(rating_avg.strip())
            except Exception as e:
                rating_avg = None
        else:
            rating_avg = None

        book["rating_avg"] = rating_avg

        book.update(
            {
                "price": price,
                "rating_avg": rating_avg,
                "rating_count": response.xpath(
                    '//span[@class="rating-count"]/text()'
                ).extract_first(),
                "indexed_date": datetime.datetime.now(),
                "url": response.url,
                "categories": self.extract_categories(response),
                "authors": self.extract_authors(response),
            }
        )

        f = re.findall(r"bookdepository.com/[\w\-_]+/(\d+)", response.url)
        if f:
            _id = f[0]
            book["_id"] = _id

            for item in response.xpath('//ul[@class="biblio-info"]/li'):
                label = item.xpath("./label/text()").extract_first()
                if label is not None:
                    label = slugify(label.lower().strip()).replace("-", "_")
                else:
                    continue
                value = item.xpath("./span/text()").extract_first()
                book.update({label: value})
            yield book
