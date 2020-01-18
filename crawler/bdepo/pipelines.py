# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from slugify import slugify
from dateparser import parse
import pymongo
from pymongo.errors import DuplicateKeyError
import re


class BdepoPipeline(object):
    """
    Main pipeline class for book item parsing
    """
    def process_item(self, item, spider):
        _id = item['_id']
        for k in item.keys():
            item[slugify(k.lower())] = item.pop(k)

        if not all((
            _id,
            item.get('title'),
            # item.get('description'),
            item.get('url'),
        )):
            raise DropItem('Missing Values: {}'.format(item.get('url')))

        item['_id'] = _id
        keys = item.keys()

        for k in keys:
            if isinstance(item[k], str):
                item[k] = item[k].strip()
                if item[k].isdigit():
                    item[k] = int(item[k])
            if not item[k]:
                item[k] = None

        if '_id' in keys:
            item['_id'] = int(item['_id'])

        if 'publication-date' in keys:
            item['publication-date'] = parse(item['publication-date'])
        if 'Publication date' in keys:
            item['publication-date'] = parse(item.pop('Publication date'))

        if 'bestsellers-rank' in keys and isinstance(item['bestsellers-rank'], str):
            item['bestsellers-rank'] = int(item['bestsellers-rank'].replace(',', ''))
        else:
            item['bestsellers-rank'] = None

        if 'rating-count' in keys and isinstance(item['rating-count'], str):
            r = item['rating-count'].replace(',', '')
            r = re.findall(r'\d+', r)
            if r:
                item['rating-count'] = int(r[0])
            else:
                item['rating-count'] = None
        else:
            item['rating-count'] = None

        if item.get('rating_avg'):
            try:
                item['rating_avg'] = float(item['rating_avg'])
            except ValueError:
                pass

        if item.get('price'):
            try:
                item['price'] = float(item.replace(',', '.'))
            except Exception as e:
                item['price'] = None
        else:
            item['price'] = None

        return item


class MongoPipeline(object):

    collection_name = 'dataset'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # if not item:
        #     DropItem('Empty item: {}'.format(item))
        try:
            self.db['dataset'].insert_one({
                '_id': int(item['_id']),
                'ok': True
            })
        except:
            DropItem('Item Already Exists {}'.format(item['_id']))
        finally:
            return item
