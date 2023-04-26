import json

base_metadata = {
    "title": "Book Depository Dataset",
    "subtitle": "A large collection of books, scraped from bookdepository.com",
    "description": "## Context\n"
    "While I was trying to master scrapy framework I came up with this project. This is a large "
    "collection of books, scraped from bookdepository.com. sp1thas/book-depository-dataset repository "
    "contains the implementation of this dataset. Feel free to contribute in any way.\n"
    "## Content\n"
    "This dataset contains books from bookdepository.com, not the actual content of the book but a list "
    "of metadata like title, description, dimensions, category, cover image and others.\n"
    "## Acknowledgements\n"
    "I would like to thank bookdepository and specifically it's "
    "[robots.txt](https://bookdepository.com/robots.txt)\n"
    "## Inspiration\n"
    "This dataset could be used for NLP, Text Classification, Computer Vision and other tasks. Any "
    "feedback regarding dataset is more than welcome.\n",
    "id": "sp1thas/book-depository-dataset",
    "licenses": [{"name": "CC-BY-NC-SA-4.0"}],
    "resources": [
        {
            "path": "dataset.csv",
            "description": "The actual dataset",
            "name": "dataset",
            "schema": {
                "fields": [
                    {
                        "name": "authors",
                        "description": "List of author ids",
                        "type": "array",
                    },
                    {
                        "name": "bestsellers-rank",
                        "description": "Bestsellers rank",
                        "type": "integer",
                    },
                    {
                        "name": "categories",
                        "description": "List of category ids",
                        "type": "array",
                    },
                    {"name": "description", "description": "", "type": "string"},
                    {"name": "dimension-x", "description": "", "type": "number"},
                    {"name": "dimension-y", "description": "", "type": "number"},
                    {"name": "dimension-z", "description": "", "type": "number"},
                    {"name": "edition", "description": "", "type": "string"},
                    {"name": "edition-statement", "description": "", "type": "string"},
                    {"name": "for-ages", "description": "", "type": "string"},
                    {"name": "format", "description": "", "type": "integer"},
                    {
                        "name": "id",
                        "description": "",
                        "type": "string",
                        "format": "uuid",
                    },
                    {"name": "illustrations-note", "description": "", "type": "string"},
                    {"name": "image-checksum", "description": "", "type": "string"},
                    {"name": "image-path", "description": "", "type": "string"},
                    {
                        "name": "image-url",
                        "description": "",
                        "type": "string",
                        "format": "uri",
                    },
                    {"name": "imprint", "description": "", "type": "string"},
                    {"name": "index-date", "description": "", "type": "datetime"},
                    {
                        "name": "isbn10",
                        "description": "",
                        "type": "string",
                        "format": "uuid",
                    },
                    {
                        "name": "isbn13",
                        "description": "",
                        "type": "uuid",
                        "format": "uuid",
                    },
                    {"name": "lang", "description": "", "type": "string"},
                    {"name": "price", "description": "", "type": "number"},
                    {"name": "publication-date", "description": "", "type": "date"},
                    {"name": "publication-place", "description": "", "type": "string"},
                    {"name": "rating-avg", "description": "", "type": "number"},
                    {"name": "rating-count", "description": "", "type": "integer"},
                    {"name": "title", "description": "", "type": "string"},
                    {
                        "name": "url",
                        "description": "",
                        "type": "string",
                        "format": "uri",
                    },
                    {"name": "weight", "description": "", "type": "number"},
                ]
            },
        },
        {
            "path": "authors.csv",
            "description": "This file should be used to match `authors` in `dataset.csv` with the actual author name.",
            "name": "authors",
            "schema": {
                "fields": [
                    {
                        "name": "author_id",
                        "description": "Author ID.",
                        "type": "string",
                        "format": "uuid",
                    },
                    {
                        "name": "author_name",
                        "description": "Author name.",
                        "type": "string",
                    },
                ]
            },
        },
        {
            "path": "categories.csv",
            "description": "This file should be used to match `categories` in `dataset.csv` with the actual category name.",
            "name": "categories",
            "schema": {
                "fields": [
                    {
                        "name": "category_id",
                        "description": "Author ID.",
                        "type": "string",
                        "format": "uuid",
                    },
                    {
                        "name": "author_name",
                        "description": "Category name.",
                        "type": "string",
                    },
                ]
            },
        },
        {
            "path": "formats.csv",
            "description": "This file should be used to match `format` in `dataset.csv` with the actual format value.",
            "name": "formats",
            "schema": {
                "fields": [
                    {
                        "name": "format_id",
                        "description": "Format ID.",
                        "type": "string",
                        "format": "uuid",
                    },
                    {
                        "name": "format_name",
                        "description": "Format name.",
                        "type": "string",
                    },
                ]
            },
        },
    ],
    "keywords": ["books", "metadata"],
}

with open("data/parsed/dataset-metadata.json", "w") as f:
    json.dump(base_metadata, f, indent=2)
