import argparse
import csv
import datetime
import json
import os
import re
from pprint import pprint
from typing import NoReturn, Dict, List, Union, Any, Tuple
import jsonlines
import pandas as pd
from utils import keep_cols, lang_mapping, kaggle_description


class BookParser:
    """
    Class for book parsing

    :param input_file: input file
    :type input_file: str
    :param output_folder: output folder path
    :type output_folder: str
    :return; Nada
    :rtype: None

    :cvar re_dim_x: compiled regex for dimension x
    :cvar re_dim_y: compiled regex for dimension y
    :cvar re_dim_z: compiled regex for dimension z
    :cvar re_w: compiled regex for weight
    :cvar re_format: compiled regex for format
    :cvar re_id: compiled regex for book id


    """
    re_dim_x = re.compile(r"[\d.,]+")
    re_dim_y = re.compile(r"x\s+([\d.,]+)\s+")
    re_dim_z = re.compile(r"([\d.,]+)mm")
    re_w = re.compile(r"([\d.,]+)g")
    re_format = re.compile(r'\w+')
    re_id = re.compile(r'/(\d+)/')
    re_url = re.compile(r'bookdepository.com([\w\-_\d\/]+)[\?^]?')

    id2author = {}
    author2id = {}
    author_id = 0
    format2id = {}
    id2format = {}
    categories = {}
    format_id = 0
    city_country2id = {}
    city_i = 0

    dupl = set()
    cols = set()
    c = 0

    def __init__(self, input_file: str, output_folder: str) -> NoReturn:
        self.input_file = input_file
        self.output_folder = output_folder
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        self.f = open(os.path.join(self.output_folder, 'dataset.csv'), 'w')
        self.wr = csv.writer(self.f, quoting=csv.QUOTE_ALL)
        self.wr.writerow([_ for _ in keep_cols])

    def run(self):
        with jsonlines.open(self.input_file) as rd:
            for row in rd:
                parsed = self.parse_entry(row)
                if not all((
                    parsed.get('id'), parsed.get('isbn10')
                )):
                    continue
                if parsed['id'] in self.dupl:
                    continue
                else:
                    self.dupl.add(parsed['id'])

                self.write_entry(parsed)
        with open(os.path.join(self.output_folder, 'authors.csv'), 'w') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(['author_id', 'author_name'])
            for k, v in sorted(self.author2id.items(), key=lambda item: item[0]):
                wr.writerow([v, k])
        with open(os.path.join(self.output_folder, 'categories.csv'), 'w') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(['category_id', 'category_name'])
            for k, v in sorted(self.categories.items(), key=lambda item: item[1]):
                wr.writerow([k, v])
        with open(os.path.join(self.output_folder, 'formats.csv'), 'w') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(['format_id', 'format_name'])
            for k, v in sorted(self.id2format.items(), key=lambda item: item[1]):
                wr.writerow([k, v])
        with open(os.path.join(self.output_folder, 'places.csv'), 'w') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(['place_id', 'place_name'])
            for k, v in sorted(self.city_country2id.items(), key=lambda item: item[0]):
                wr.writerow([v, k])

        with open(os.path.join(self.output_folder, 'KAGGLE_README.md'), 'w') as f:
            f.write(kaggle_description)

        print(self.cols - set(keep_cols.keys()))
        self.close()

    def close(self):
        """
        Close open file
        :return:
        """
        self.f.close()

    def extract_relative_url(self, url):
        if url:
            return re.findall(self.re_url, url)[0]


    def write_entry(self, entry: Dict[str, Any]) -> NoReturn:
        row = []
        if isinstance(entry.get('dimensions'), str):
            entry['dimensions'], entry['weight'] = self.extract_dimensions(entry['dimensions'])
        for k, v in entry.pop('dimensions', {}).items():
            entry['dimension_{}'.format(k)] = v
        for k in keep_cols:
            v = entry.get(k)
            if isinstance(v, (list, dict)):
                v = json.dumps(v)
            row.append(v)
        self.wr.writerow(row)

    def extract_publish_place(self, place):
        if place in self.city_country2id:
            return self.city_country2id[place]
        else:
            self.city_i += 1
            self.city_country2id[place] = self.city_i
            return self.city_country2id[place]

    def extract_dimensions(self, dims: str) -> Tuple[Dict[str, Union[float, None]], Union[float, None]]:
        """
        Extract dimensions from raw text
        :param dims: raw text with dimensions and weight
        :type dims: str
        :return: Dimensions and weith
        :rype: tuple
        """
        dims = dims.strip()
        if not dims:
            return {'x': None, 'y': None, 'z': None}, None
        try:
            x = float(re.findall(self.re_dim_x, dims)[0].replace(',', ''))
        except Exception as e:
            x = None
            print('{}\n{}\n{}'.format(e, 'x not found', dims))
        try:
            y = float(re.findall(self.re_dim_y, dims)[0].replace(',', ''))
        except Exception as e:
            y = None
            # print('{}\n{}\n{}'.format(e, 'y not found', dims))
        try:
            z = float(re.findall(self.re_dim_z, dims)[0].replace(',', ''))
        except Exception as e:
            z = None
            print('{}\n{}\n{}'.format(e, 'z not found', dims))
        try:
            w = float(re.findall(self.re_w, dims)[0].replace(',', ''))
        except Exception as e:
            w = None
        return {'x': x, 'y': y, 'z': z}, w

    def extract_format(self, frmt: str) -> Union[int, None]:
        """
        Extract format id from raw text

        :param frmt: format raw text
        :type frmt: str
        :return: format id
        :rtype: int
        """
        if not frmt:
            return None

        frmt = re.findall(self.re_format, frmt)[0]
        if frmt in self.format2id:
            pass
        else:
            self.format_id += 1
            self.format2id[frmt] = self.format_id
            self.id2format[self.format_id] = frmt
        return self.format2id[frmt]

    @staticmethod
    def extract_lang(lang: str) -> List[str]:
        """
        Extract language code from raw text
        :param lang: language raw text
        :return: list of language codes
        :rtype: list
        """
        if not lang.strip():
            return []
        langs = []
        for lng in lang.split(','):
            langs.append(lang_mapping[lng.strip()])
        return langs

    def extract_id(self, url: str) -> Union[None, str]:
        """
        Extract book id from given url

        :param url: book url
        :tyoe url: str
        :return: book id
        :rtype: str
        """
        try:
            return re.findall(self.re_id, url)[0]
        except Exception as e:
            print(url)

    def parse_entry(self, entry):
        """
        Parse a book entry and return in proper format

        :param entry: book entry
        :type entry: dict
        :return: book entry in proper format
        :rtype: dict
        """
        if entry.get('_id'):
            entry['id'] = entry.pop('_id')
        if entry.get('indexed-date'):
            entry['index-date'] = entry.pop('indexed-date')
        if not entry['id']:
            entry['id'] = self.extract_id(entry['url'])
        if entry.get('rating-avg', None) is None:
            entry['rating-avg'] = None
        else:
            entry['rating-avg'] = float(entry['rating-avg'])
        if entry.get('rating-count') is None:
            pass
        else:
            entry['rating-count'] = int(entry['rating-count'])
        if entry.get('bestsellers-rank') is None:
            pass
        else:
            entry['bestsellers-rank'] = int(entry['bestsellers-rank'])

        if entry.get('url'):
            entry['url'] = self.extract_relative_url(entry.pop('url'))

        if entry.get('publication-city-country'):
            entry['publication-place'] = self.extract_publish_place(entry.pop('publication-city-country'))
            # break
        categories__ = []

        categories_labels = entry.pop('categories', [])
        if categories_labels:
            for category in categories_labels:
                if category['id'] in self.categories:
                    pass
                else:
                    self.categories[category['id']] = category['name']
                if category['id'] not in categories__:
                    categories__.append(category['id'])
        else:
            pass

        authors__ = []

        authors_labels = entry.pop('authors', [])

        if authors_labels:
            for author in authors_labels:
                if author in self.author2id:
                    pass
                else:
                    self.author_id += 1
                    self.author2id[author] = self.author_id
                    self.id2author[self.author_id] = author

                if self.author2id[author] not in authors__:
                    authors__.append(self.author2id[author])
        else:
            pass

        if 'ISBN10' in entry:
            entry['isbn10'] = entry.pop('ISBN10')
        if 'ISBN13' in entry:
            entry['isbn10'] = entry.pop('ISBN13')

        entry['dimensions'], entry['weight'] = self.extract_dimensions(entry.pop('dimensions', ''))
        entry.update({
            'categories': categories__,
            'authors': authors__,
            'format': self.extract_format(entry.pop('format', '')),
            'lang': self.extract_lang(entry.pop('language', '')),
            'publication-date': datetime.datetime.strptime(
                entry['publication-date'], '%Y-%m-%d %H:%M:%S'
            ).strftime('%Y-%m-%d') if entry.get('publication-date') else None
        })

        c = tuple(entry.keys())
        for k in c:
            entry[k.lower().replace(' ', '-').replace('/', '-').replace('_', '-')] = entry.pop(k)

        for k in entry.keys():
            self.cols.add(k)
        entry = {k: v for k, v in entry.items() if k in keep_cols}

        return entry


def argparsing():
    argus = argparse.ArgumentParser()
    argus.add_argument("-i", "--input-file", dest="inp", help="Input file path", required=True, type=str)
    argus.add_argument("-o", "--output-folder", dest="out", help="Output folder path", required=False, type=str,
                       default='../export')
    return argus.parse_args()


if __name__ == "__main__":
    args = argparsing()
    bp = BookParser(input_file=args.inp, output_folder=args.out)
    bp.run()
