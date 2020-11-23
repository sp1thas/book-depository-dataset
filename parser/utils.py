from collections import OrderedDict

lang_mapping = {
    "Ancient (to 1453)": "grc",
    "Modern (1453-)": "el",
    "Middle (1100-1500)": "enm",
    "Old (ca.450-1100)": "ang",
    "Middle High (ca.1050-1500)": "gmh",
}

keep_cols = {
    "id": "Unique identifier (`int`)",
    "isbn10": "ISBN-10 (`str`)",
    "isbn13": "ISBN-13 (`str`)",
    "publication-date": "Publication date (`date`)",
    "publication-place": "Publication place (`id`)",
    "authors": "Author(s) (`list of str`)",
    "bestsellers-rank": "Bestsellers ranking (`int`)",
    "categories": "Categories. Check `authors.csv` for mapping (`list of int`)",
    "description": "Description (`str`)",
    "edition": "Edition (`str`)",
    "edition-statement": "Edition statement (`str`)",
    "for-ages": "Range of ages (`str`)",
    "format": "Format. Check `formats.csv` for mapping (`int`)",
    "illustrations-note": "",
    "imprint": "",
    "index-date": "Crawling date (`date`)",
    "lang": "List of book's language(s)",
    "dimension-x": "Dimension X (`float` in cm)",
    "dimension-y": "Dimension Y (`float` in cm)",
    "dimension-z": "Dimension Z (`float` in mm)",
    "title": "Book's title (`str`)",
    "rating-avg": "Rating average [0-5] (`float`)",
    "rating-count": "Number of ratings",
    "weight": "Weight (in kgr)",
    "url": "Relative url (https://bookdepository.com + `url`)",
    "image-url": "Cover image url",
    "image-path": "Cover image file path",
    "image-checksum": "Cover image checksum",
    # 'publisher': 'Publisher (`str`)',
}
sort_cols = list(keep_cols.keys())
sort_cols.sort()
keep_cols = OrderedDict((k, keep_cols[k]) for k in sort_cols)

kaggle_description = """### Context

While I was trying to master `scrapy` framework I came up with this project. This is a large collection of books, scraped from bookdepository.com. [sp1thas/book-depository-dataset](https://github.com/sp1thas/book-depository-dataset) repository contains the implementation of this dataset. Feel free to contribute in any way.


### Content

This dataset contains books from [bookdepository.com](https://bookdepository.com), not the actual content of the book but a list of metadata like title, description, dimensions, category, cover image and others. Please find below an extensive list of fields for every sample:

{}

### Acknowledgements

I would like to thank bookdepository and specifically it's [`robots.txt`](https://bookdepository.com/robots.txt)


### Inspiration

This dataset could be used for NLP, Text Classification, Computer Vision and other tasks. Any feedback regarding dataset is more than welcome.
""".format(
    "\n".join(" * `{}`: {}".format(k, v) for k, v in keep_cols.items())
)
