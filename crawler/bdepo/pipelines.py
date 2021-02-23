# -*- coding: utf-8 -*-

import os
import re

import pymongo  # type: ignore
from dateparser import parse  # type: ignore
from scrapy.exceptions import DropItem  # type: ignore
from scrapy.pipelines.images import ImagesPipeline  # type: ignore


class BdepoPipeline(object):
    """Main pipeline class for book item parsing"""

    def process_item(self, item, spider):
        _id = item["_id"]

        if not all(
            (
                _id,
                item.get("title"),
                # item.get('description'),
                item.get("url"),
            )
        ):
            raise DropItem("Missing Values: {}".format(item.get("url")))

        for k in item.keys():
            if isinstance(item[k], str):
                item[k] = item[k].strip()
                if item[k].isdigit():
                    item[k] = int(item[k])
            if not item[k]:
                item[k] = None

        item["_id"] = int(item["_id"])

        if item.get("publication_date") is not None:
            item["publication_date"] = parse(item["publication_date"])

        if item.get("bestsellers_rank") and isinstance(item["bestsellers_rank"], str):
            item["bestsellers_rank"] = int(item["bestsellers_rank"].replace(",", ""))
        else:
            item["bestsellers_rank"] = None

        if item.get("rating_count") and isinstance(item["rating_count"], str):
            r = item["rating_count"].replace(",", "")
            r = re.findall(r"\d+", r)
            if r:
                item["rating_count"] = int(r[0])
            else:
                item["rating_count"] = None
        else:
            item["rating_count"] = None

        if item.get("rating_avg"):
            try:
                item["rating_avg"] = float(item["rating_avg"])
            except ValueError:
                pass

        if item.get("price") is not None:
            try:
                item["price"] = float(item.replace(",", "."))
            except Exception as e:
                item["price"] = None
        else:
            item["price"] = None

        return item


class MongoPipeline(object):

    collection_name = "dataset"
    client = None
    db = None

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "items"),
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
            self.db["dataset"].insert_one({"_id": int(item["_id"]), "ok": True})
        except:
            DropItem("Item Already Exists {}".format(item["_id"]))
        finally:
            return item


class FolderStructureImagePipeline(ImagesPipeline):
    """Store Images using a folder tree structure. DEPTH attribute can be used to specify the depth of the tree."""

    DEPTH = 3

    def tree_path(self, path: str) -> str:
        """Generate a folder tree based on given path. I.e: path/to/image.jpg -> path/to/i/m/a/image.jpg

        :param path: original image filepath.
        :return: image filepath with extra folder tree.
        """
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)
        return os.path.join(dirname, *[_ for _ in filename[: self.DEPTH]], filename)

    def file_path(self, request, response=None, info=None):
        return self.tree_path(super().file_path(request, response, info))

    def thumb_path(self, request, thumb_id, response=None, info=None):
        return self.tree_path(
            super().thumb_path(request, thumb_id, response=response, info=info)
        )
