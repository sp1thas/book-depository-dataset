# -*- coding: utf-8 -*-
import datetime
import logging
import re
from random import shuffle

import scrapy  # type: ignore
from scrapy.utils.project import get_project_settings  # type: ignore
from slugify import slugify  # type: ignore

from src.bdepo.items import BookItem

settings = get_project_settings()


class BdepobooksSpider(scrapy.Spider):
    name = "bdepobooks"
    allowed_domains = ["bookdepository.com"]

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

    RE_REF = re.compile(r"\?ref=[\w|\-]+$")

    def __init__(self, dev="", **kwargs):
        self.dev = bool(dev)
        if dev:
            self.start_urls = self.start_urls[:1]
        super().__init__(**kwargs)

    def parse(self, response):
        subcategory_urls = response.xpath(
            '//ul[@class="category-list sidebar-nav has-parent"]/li[position() > 4]/a/@href'
        ).getall()
        if self.dev:
            subcategory_urls = subcategory_urls[:1]

        for subcategory_url in subcategory_urls:
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

        next_href = (
            None if self.dev else response.xpath('//li[@id="next-top"]/a/@href').get()
        )
        if next_href and not self.dev:
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
        t = response.xpath('//ol[@class="breadcrumb"]/li[1]/text()').get()
        if "Categories:" not in t:
            logging.warning("different breadcrumb type: {}".format(t))
            return []

        categories = []
        for category in response.xpath('//ol[@class="breadcrumb"]/li/a'):
            category_name = category.xpath("./text()").get()
            category_url = category.xpath("./@href").get()
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
        ).getall()
        book["title"] = response.xpath("//h1/text()").get()
        book["image_urls"] = response.xpath(
            '//div[@class="item-img-content"]/img/@src'
        ).getall()
        rating_avg = response.xpath('//span[@itemprop="ratingValue"]/text()').get()
        price = response.xpath('//span[@class="sale-price"]/text()').get()
        currency = None
        if price:
            currency = "euro" if price and "€" in price else None
            try:
                price = float(re.findall(r"\d+\.\d+", price.replace(",", "."))[0])
            except Exception as e:
                print(e)
                price = None
                currency = None
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
                "currency": currency,
                "rating_avg": rating_avg,
                "rating_count": response.xpath(
                    '//span[@class="rating-count"]/text()'
                ).get(),
                "indexed_date": datetime.datetime.now(),
                "url": re.sub(self.RE_REF, "", response.url),
                "categories": self.extract_categories(response),
                "authors": self.extract_authors(response),
            }
        )

        f = re.findall(r"bookdepository.com/[\w\-_]+/(\d+)", response.url)
        if f:
            _id = f[0]
            book["_id"] = _id

            for item in response.xpath('//ul[@class="biblio-info"]/li'):
                label = item.xpath("./label/text()").get()
                if label is not None:
                    label = slugify(label.lower().strip()).replace("-", "_")
                else:
                    continue
                value = item.xpath("./span/text()").get()
                book.update({label: value})
            yield book
