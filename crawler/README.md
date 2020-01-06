## Bookdepository crawler
![scrapy-version](https://img.shields.io/badge/Scrapy-1.8.0%2B-green)

This scrapy project is used to extract the majority of books from bookdepository. If you want to extract the data on your own, please keep settings file as is.


## Usage
```bash
scrapy crawl bdepobooks -o books.jsonlines
```

Scraping process will take more than a week. (scraping rate: ~50 items/minute). After crawling, `books.jsonlines` will contains all the raw data of books.
