# -*- coding: utf-8 -*-
import logging
import os
import re

import sqlalchemy.exc
from dateparser import parse  # type: ignore
from scrapy.exceptions import DropItem  # type: ignore
from scrapy.pipelines.images import ImagesPipeline  # type: ignore
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import models, config


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

        item["publication_date"] = (
            parse(item["publication_date"])
            if item.get("publication_date") is not None
            else None
        )
        item["bestsellers_rank"] = (
            int(item["bestsellers_rank"].replace(",", ""))
            if item.get("bestsellers_rank")
            and isinstance(item["bestsellers_rank"], str)
            else None
        )

        if item.get("rating_count") and isinstance(item["rating_count"], str):
            r = re.findall(r"\d+", item["rating_count"].replace(",", ""))
            item["rating_count"] = int(r[0]) if r else None
        else:
            item["rating_count"] = None

        if item.get("rating_avg"):
            try:
                item["rating_avg"] = float(item["rating_avg"])
            except ValueError:
                pass

        if item.get("price"):
            try:
                item["price"] = float(str(item["price"]).replace(",", "."))
            except ValueError:
                pass
        return item


class PostgresPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        Session = sessionmaker(bind=create_engine(config.url))
        self.session = Session()

    def process_item(self, item: dict, spider):
        """Save deals in the database.

        This method is called for every item pipeline component.

        """
        if not item:
            return {}
        book = models.Book(
            **{
                attr: item.get(attr)
                for attr in (
                    "bestsellers_rank",
                    "description",
                    "dimension_x",
                    "dimension_y",
                    "dimension_z",
                    "edition",
                    "edition_statement",
                    "for_ages",
                    "illustrations_note",
                    "image_checksum",
                    "image_path",
                    "image_url",
                    "imprint",
                    "index_date",
                    "isbn10",
                    "isbn13",
                    "lang",
                    "publication_date",
                    "publication_place",
                    "rating_avg",
                    "rating_count",
                    "title",
                    "url",
                    "weight",
                )
            }
        )

        try:
            self.session.add(book)
            self.session.commit()
        except (sqlalchemy.exc.PendingRollbackError, sqlalchemy.exc.InternalError) as e:
            return {}

        for author_s in item["authors"]:
            author = models.Author(name=author_s)
            self.session.add(author)
            self.session.commit()
            self.session.add(models.BookAuthor(book_id=book.id, author_id=author.id))
            self.session.commit()

        return item

    def close_spider(self, spider):
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()


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
