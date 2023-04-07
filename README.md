# Book Depository Dataset

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sp1thas/book-depository-dataset/master.svg)](https://results.pre-commit.ci/latest/github/sp1thas/book-depository-dataset/master)
![testing](https://github.com/sp1thas/book-depository-dataset/workflows/testing/badge.svg)
![python-version](https://img.shields.io/badge/python-3.9-blue)
[![kaggle-dataset](https://img.shields.io/badge/KAGGLE_DATASET-20beff)](https://www.kaggle.com/sp1thas/book-depository-dataset/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The source code of `Book Depository Dataset`. Here you will find the implementation for data extraction (scrapy spider), parsing and EDA.

Dataset is also available [here](https://www.kaggle.com/sp1thas/book-depository-dataset/) as kaggle dataset

## Project Structure

- **crawler**: scrapy crawler for data extraction

- **parser**: python script for data transformation and dataset creation

- **eda**: Exploratory Data Analysis on dataset

## Step to reproduce

1.  Run scrapy crawler in order to retrieve data from `bookdepository.com`
2.  Run parser in order to create the dataset

## Crawler

![scrapy-version](https://img.shields.io/badge/Scrapy-1.8.0%2B-green)

This scrapy project is used to extract the majority of books from [bookdepository.com](https://bookdepository.com). If you want to extract the data on your own, please keep settings file as is.

### Usage

Use crawler as a common scrapy project:

```bash
poetry run scrapy crawl bdepobooks -o data/raw/textual/books.jsonlines
```

Scraping process will take more than a week. (scraping rate: ~50 items/minute). After crawling,
`data/raw/textual/books.jsonlines` will contain all the raw data of books. Downloaded images can be found under the
`data/raw/media/full` folder.

## Parser

This submodule is about parsing and manipulating the raw data in order to create the dataset in a tabular format (`csv`).

### Usage

Use the parser directly from command line, just provide the `.jsonlines` file with raw data and the output directory.

```bash
python parse_dataset.py -h
optional arguments:
  -h, --help            show this help message and exit
  -i INP, --input-file INP
                        Input file path
  -o OUT, --output-folder OUT
                        Output folder path
```

### Working example

```bash
poetry run python src/parser/parse_dataset.py \
                  --input-jsonb data/raw/textual/books.jsonlines \
                  --input-images data/raw/media/full \
                  --output-folder data/parsed
```

This script will create a collection of `.csv` and `.zip` files in `data/parsed/` folder.

## Citation

```
 @misc{simakis_2020,
	title={Book Depository Dataset},
	url={https://www.kaggle.com/ds/467291},
	DOI={10.34740/kaggle/ds/467291},
	publisher={Kaggle},
	author={Simakis, Panagiotis},
	year={2020}
}
```
## Sponsor

A shout-out for the sponsors of this project:

 - Konrad Mazanowski [@konradm](https://github.com/konradm)


## Disclaimer

All books are hosted by [bookdepository.com](https://bookdepository.com). The use of dataset is fair use for academic purposes.
