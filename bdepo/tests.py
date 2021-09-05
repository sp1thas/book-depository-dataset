import unittest

import requests
import scrapy  # type: ignore

from spiders.bdepobooks import BdepobooksSpider


class SpiderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.spider = BdepobooksSpider()

    def test_book_item(self):
        url = "https://www.bookdepository.com/Sapiens-Yuval-Noah-Harari/9780099590088"
        req = scrapy.http.Request(url)

        res = scrapy.http.TextResponse(url, body=requests.get(url).content, request=req)
        book_item = [_ for _ in self.spider.parse_book(res)][0]

        book_item.pop("indexed_date")

        self.assertDictEqual(
            {
                "description": "\n\n                    **THE MILLION COPY BESTSELLER**",
                "title": "Sapiens : A Brief History of Humankind",
                "image_urls": [
                    "https://d1w7fb2mkkr3kw.cloudfront.net/assets/images/book/lrg/9780/0995/9780099590088.jpg"
                ],
                "rating_avg": 4.41,
                "price": 11.66,
                "rating_count": "\n                            (489,149 ratings by Goodreads)\n",
                # 'indexed_date': datetime.datetime(2020, 12, 6, 1, 24, 13, 416042),
                "url": "https://www.bookdepository.com/Sapiens-Yuval-Noah-Harari/9780099590088",
                "categories": [
                    {"name": "General & World History", "id": 2642},
                    {"name": "Classical History / Classical Civilisation", "id": 2654},
                    {"name": "History Of Ideas", "id": 639},
                    {"name": "Social & Cultural Anthropology", "id": 719},
                    {"name": "Physical Anthropology & Ethnography", "id": 720},
                    {"name": "Popular Science", "id": 1532},
                ],
                "authors": ["Yuval Noah Harari"],
                "_id": "9780099590088",
                "format": "\n                                Paperback\n                                    | ",
                "dimensions": "\n                                129\n                                    x 198\n                                    x 37mm\n                                \n                                    | 437g\n                                ",
                "publication_date": "15 Sep 2016",
                "publisher": "\n                                ",
                "imprint": "VINTAGE",
                "publication_city_country": "\n                                London, United Kingdom",
                "language": "\n                                English",
                "isbn10": "0099590085",
                "isbn13": "9780099590088",
                "bestsellers_rank": "\n                                25",
            },
            dict(book_item),
        )
