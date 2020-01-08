from collections import OrderedDict

keep_cols = {
    'id': "Book's unique id (`int`)",
    'isbn10': "Book's ISBN-10 (`str`)",
    'isbn13': "Book's ISBN-13 (`str`)",
    'publication-date': "Publication date (`date`)",
    'publication-place': "Publication place (`id`)",
    'authors': 'Book\'s author(s) (`list of str`)',
    'bestsellers-rank': 'Bestsellers ranking (`int`)',
    'categories': 'Book\'s categories. Check `authors.csv` for mapping (`list of int`)',
    'description': "Book's description (`str`)",
    'edition': 'Edition (`str`)',
    'edition-statement': 'Edition statement (`str`)',
    'for-ages': 'Range of ages (`str`)',
    'format': "Book's format. Check `formats.csv` for mapping (`int`)",
    'illustrations-note': '',
    'imprint': '',
    'index-date': 'Book\'s crawling date (`date`)',
    'lang': 'List of book\' language(s)',
    'dimension_x': 'Book\'s dimension X (`float` in cm)',
    'dimension_y': 'Book\'s dimension Y (`float` in cm)',
    'dimension_z': 'Book\'s dimension Z (`float` in mm)',
    'description': 'Book description (`str`)',
    'title': 'Book\'s title (`str`)',
    'rating-avg': 'Rating average [0-5] (`float`)',
    'rating-count': 'Number of ratings',
    'weight': 'Book\'s weight (in kgr)',
    'url': 'Book relative url (https://bookdepository.com + `url`)',
    'publisher': 'Publisher (`str`)',

}
sort_cols = list(keep_cols.keys())
sort_cols.sort()
keep_cols = OrderedDict((k, keep_cols[k]) for k in sort_cols)

kaggle_description = """### Contextin order

While I was trying to master `scrapy` framework I came up with this project. I decided to create a large dataset of books.


### Content

This dataset contains books from [bookdepository.com](https://bookdepository.com), not the actual content of the book but a list of meta data like title, description, dimensions, categorization and others. Please find below an extensive list of fields for every book:

{}

### Acknowledgements

I would like to thank bookdepository and specifically it's [`robots.txt`](https://bookdepository.com/robots.txt)


### Inspiration

This dataset could be used for NLP, Text Classification and other tasks. Any feedback regarding dataset is more than welcomed.
""".format('\n'.join(
    ' * `{}`: {}'.format(k, v) for k, v in keep_cols.items()
))