## Bookdepository crawler
![scrapy-version](https://img.shields.io/badge/Scrapy-1.8.0%2B-green)

This scrapy project is used to extract the majority of books from [bookdepository.com](https://bookdepository.com). If you want to extract the data on your own, please keep settings file as is.

## Usage
Use crawler as a common scrapy project:
```bash
scrapy crawl bdepobooks -o books.jsonlines
```

Scraping process will take more than a week. (scraping rate: ~50 items/minute). After crawling, `books.jsonlines` will contains all the raw data of books.
