import unittest

import requests
import scrapy  # type: ignore

from src.bdepo.spiders.bdepobooks import BdepobooksSpider


class SpiderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.spider = BdepobooksSpider()
        url = "https://www.bookdepository.com/Sapiens-Yuval-Noah-Harari/9780099590088"
        req = scrapy.http.Request(url)
        res = scrapy.http.TextResponse(url, body=requests.get(url).content, request=req)
        self.item = [_ for _ in self.spider.parse_book(res)][0]

    def test_float_fields(self):
        for f in ("rating_avg", "price"):
            self.assertIsInstance(self.item.get(f), float)

    def test_regex_field(self):
        self.assertRegex(
            self.item.get("rating_count"), r"(\d+,\d+ ratings by Goodreads)"
        )
        self.assertRegex(self.item.get("bestsellers_rank"), r"\d+")

    def test_book_item(self):
        self.maxDiff = None
        self.item.pop("indexed_date")
        ignore = ("rating_avg", "price", "rating_count", "bestsellers_rank")

        self.assertDictEqual(
            {
                "description": [
                    "\n\n                            'Interesting and provocative... It gives you a sense of how briefly we've been on this Earth' Barack Obama",
                    "\n                            ",
                    "\n                            What makes us brilliant? What makes us deadly? What makes us Sapiens?",
                    "\n                            ",
                    "\n                            One of the world's preeminent historians and thinkers, Yuval Noah Harari challenges everything we know about being human.",
                    "\n                            ",
                    "\n                            Earth is 4.5 billion years old. In just a fraction of that time, one species among countless others has conquered it: us.",
                    "\n                            ",
                    "\n                            In this bold and provocative book, Yuval Noah Harari explores who we are, how we got here and where we're going.",
                    "\n                            ",
                    "\n                            **ONE OF THE GUARDIAN'S 100 BEST BOOKS OF THE 21st CENTURY**",
                    "\n                            ",
                    "\n                            PRAISE FOR SAPIENS:",
                    "\n                            ",
                    "\n                            'Jaw-dropping from the first word to the last... It may be the best book I've ever read' Chris Evans",
                    "\n                            ",
                    "\n                            'Startling... It changes the way you look at the world' Simon Mayo",
                    "\n                            ",
                    "\n                            'I would recommend Sapiens to anyone who's interested in the history and future of our species' Bill Gates",
                    "\n                            ",
                    "\n                        ",
                ],
                "title": "Sapiens : THE MULTI-MILLION COPY BESTSELLER",
                "image_urls": [
                    "https://d1w7fb2mkkr3kw.cloudfront.net/assets/images/book/lrg/9780/0995/9780099590088.jpg"
                ],
                "url": "https://www.bookdepository.com/Sapiens-Yuval-Noah-Harari/9780099590088",
                "currency": "euro",
                "categories": [
                    {"name": "General & World History", "id": 2642},
                    {"name": "Classical History / Classical Civilisation", "id": 2654},
                    {"name": "Social & Cultural History", "id": 2663},
                    {"name": "Society & Social Sciences", "id": 632},
                    {"name": "History Of Ideas", "id": 639},
                    {"name": "Social & Cultural Anthropology", "id": 719},
                    {"name": "Physical Anthropology & Ethnography", "id": 720},
                    {"name": "Popular Science", "id": 1532},
                    {"name": "Early Man", "id": 1649},
                ],
                "authors": ["Yuval Noah Harari"],
                "_id": "9780099590088",
                "format": "\n                                Paperback\n                                    | ",
                "dimensions": "\n                                129\n                                    x 198\n     "
                "                               x 37mm\n                                \n              "
                "                      | 437g\n                                ",
                "publication_date": "30 Apr 2015",
                "publisher": "\n                                ",
                "imprint": "VINTAGE",
                "publication_city_country": "\n                                London, United Kingdom",
                "language": "\n                                English",
                "isbn13": "9780099590088",
            },
            {k: v for k, v in self.item.items() if k not in ignore},
        )
