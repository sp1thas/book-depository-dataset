# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from slugify import slugify
from dateparser import parse
import re


class BdepoPipeline(object):
    """
    Main pipeline class for book item parsing
    """
    @staticmethod
    def process_item(self, item, spider):
        if not (item.get('_id') or item.get('title')):
            raise DropItem('Missing Values: {}'.format(item.get('url')))

        _id = item['_id']
        for k in item.keys():
            item[slugify(k)] = item.pop(k)
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
