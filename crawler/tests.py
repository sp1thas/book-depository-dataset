import unittest
from .bdepo.spiders.bdepobooks import BdepobooksSpider
import scrapy
import requests


class SpiderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.spider = BdepobooksSpider()

    def test_book_item(self):
        url = "https://www.bookdepository.com/Sapiens-Yuval-Noah-Harari/9780099590088"
        req = scrapy.http.Request(url)

        res = scrapy.http.TextResponse(url, body=requests.get(url).content, request=req)
        book_item = [_ for _ in self.spider.parse_book(res)][0]

        self.assertEqual("Sapiens : A Brief History of Humankind", book_item["title"])

        self.assertIn("Yuval Noah Harari", book_item["authors"])

        self.assertIsNotNone(book_item["description"])
        self.assertIsNotNone(book_item["rating_count"])
        self.assertIsNotNone(book_item["format"])
        self.assertIsNotNone(book_item["dimensions"])
        self.assertEqual("15 Sep 2016", book_item["publication_date"])
        self.assertIn("English", book_item["language"])
        self.assertEqual("0099590085", book_item["isbn10"])
        self.assertEqual("9780099590088", book_item["isbn13"])
        self.assertIn("London", book_item["publication_city_country"])
