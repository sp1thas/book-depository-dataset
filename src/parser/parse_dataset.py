import argparse
import csv
import datetime
import json
import os
import re
from typing import Dict, List, Any, Tuple, Optional
from zipfile import ZipFile

import jsonlines  # type: ignore
import langcodes  # type: ignore
from tqdm import tqdm  # type: ignore

from utils import keep_cols, kaggle_description  # type: ignore


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
    re_format = re.compile(r"\w+")
    re_id = re.compile(r"/(\d+)/")
    re_url = re.compile(r"bookdepository.com([\w\-_\d/]+)[?^]?")

    missing_languages: set = set()

    new_ugc: int = 0
    new_places: int = 0
    new_authors: int = 0
    new_categories: int = 0
    new_formats: int = 0

    total_ugc: int = 0
    total_places: int = 0
    total_authors: int = 0
    total_categories: int = 0
    total_formats: int = 0

    dupl: set = set()
    cols: set = set()
    c: int = 0
    n_rows: int = 0

    def __init__(
        self,
        input_file: str,
        output_folder: str,
        dataset: str,
        image_folder: str = None,
    ) -> None:
        self.input_file = input_file
        self.image_folder = image_folder
        self.output_folder = output_folder
        self.dataset_path = dataset
        self.harvested: set = set()

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        self.f = open(os.path.join(self.output_folder, "dataset.csv"), "w")
        self.wr = csv.writer(self.f, quoting=csv.QUOTE_ALL)
        self.wr.writerow([_ for _ in keep_cols])

    def load_authors(self):
        self.f_authors = open(os.path.join(self.output_folder, "authors.csv"), "w")
        self.wr_authors = csv.writer(self.f_authors, quoting=csv.QUOTE_ALL)
        self.wr_authors.writerow(["author_id", "author_name"])
        self.author_map = {}
        if self.dataset_path:
            with open(os.path.join(self.dataset_path, "authors.csv"), "r") as f:
                for id, name in csv.reader(f):
                    if id == "author_id":
                        continue
                    self.author_map[name] = int(id)
                    self.wr_authors.writerow([id, name])
            self.max_author_id = max(self.author_map.values())
        else:
            self.max_author_id = 1

    def load_categories(self):
        self.f_categories = open(
            os.path.join(self.output_folder, "categories.csv"), "w"
        )
        self.wr_categories = csv.writer(self.f_categories, quoting=csv.QUOTE_ALL)
        self.wr_categories.writerow(["category_id", "category_name"])
        self.category_map = {}
        if self.dataset_path:
            with open(os.path.join(self.dataset_path, "categories.csv"), "r") as f:
                for id, name in csv.reader(f):
                    if id == "category_id":
                        continue
                    self.category_map[name] = int(id)
                    self.wr_categories.writerow([id, name])
            self.max_category_id = max(self.category_map.values())
        else:
            self.max_category_id = 1

    def load_formats(self):
        self.f_formats = open(os.path.join(self.output_folder, "formats.csv"), "w")
        self.wr_formats = csv.writer(self.f_formats, quoting=csv.QUOTE_ALL)
        self.wr_formats.writerow(["format_id", "format_name"])
        self.format_map = {}
        if self.dataset_path:
            with open(os.path.join(self.dataset_path, "formats.csv"), "r") as f:
                for id, name in csv.reader(f):
                    if id == "format_id":
                        continue
                    self.format_map[name] = int(id)
                    self.wr_formats.writerow([id, name])
            self.max_format_id = max(self.format_map.values())
        else:
            self.max_format_id = 1

    def add_authors(self, authors) -> List[int]:
        ids = []
        for author in authors:
            if author in self.author_map:
                ids.append(self.author_map[author])
                continue
            self.max_author_id += 1
            self.author_map[author] = self.max_author_id
            self.wr_authors.writerow([self.max_author_id, author])
            ids.append(self.author_map[author])
        return ids

    def add_categories(self, categories) -> List[int]:
        ids = []
        for category in categories:
            if category in self.category_map:
                ids.append(self.category_map[category])
                continue
            self.max_category_id += 1
            self.category_map[category] = self.max_category_id
            self.wr_categories.writerow([self.max_category_id, category])
            ids.append(self.category_map[category])
        return ids

    def add_formats(self, format: str) -> int:
        format_id = None
        if format in self.format_map:
            format_id = self.format_map[format]
            return format_id
        self.max_format_id += 1
        self.format_map[format] = self.max_format_id
        self.wr_formats.writerow([self.max_format_id, format])
        format_id = self.format_map[format]
        return format_id

    def run(self):
        with open(self.input_file, "r") as rd:
            for _ in rd:
                self.n_rows += 1

        self.load_categories()
        self.load_formats()
        self.load_authors()

        with jsonlines.open(self.input_file) as rd:
            for row in tqdm(rd, total=self.n_rows):
                parsed = self.parse_entry(row)
                if not all((parsed.get("id"), parsed.get("isbn10"))):
                    continue
                if parsed["id"] in self.dupl:
                    continue
                else:
                    self.dupl.add(parsed["id"])

                self.write_entry(parsed)

        if self.dataset_path:
            with open(os.path.join(self.dataset_path, "dataset.csv"), "r") as f:
                rd = csv.reader(f)
                for header in rd:
                    break
                self.col_to_index = {_: i for i, _ in enumerate(header)}
                for row in rd:
                    entry = {n: row[i] for n, i in self.col_to_index.items()}
                    self.write_entry(entry, processed=True, new_content=False)

        with open(os.path.join(self.output_folder, "KAGGLE_README.md"), "w") as f:
            f.write(kaggle_description)

        print(self.cols - set(keep_cols.keys()))
        print(
            """
          New UGC: {}
        Total UGC: {}
        """.format(
                self.new_ugc, self.total_ugc
            )
        )
        self.close()

    @staticmethod
    def _split_all(path):
        allparts = []
        while 1:
            parts = os.path.split(path)
            if parts[0] == path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path:  # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                allparts.insert(0, parts[1])
        return allparts

    @staticmethod
    def _extract_zip_path(full_path):
        zip_path = []
        flag = False

        for _ in BookParser._split_all(full_path):
            if _ == "full":
                flag = True

            if flag:
                zip_path.append(_)
        return os.path.join(*zip_path)

    def zip(self):
        textual_file = f"bdd_{datetime.date.today().strftime('%Y%m%d')}_text.zip"
        image_file = f"bdd_{datetime.date.today().strftime('%Y%m%d')}_images.zip"
        with ZipFile(os.path.join(self.output_folder, textual_file), "w") as zf:
            for filename in ("dataset.csv",):
                zf.write(os.path.join(self.output_folder, filename), arcname=filename)
            print(f"generated zip: {textual_file}")
        if self.image_folder:
            with ZipFile(os.path.join(self.output_folder, image_file), "w") as zf:
                for path, dirs, filenames in os.walk(self.image_folder):
                    for filename in filenames:
                        zip_path = self._extract_zip_path(os.path.join(path, filename))
                        zf.write(os.path.join(path, filename), arcname=zip_path)

    def close(self):
        """
        Close open file
        :return:
        """
        self.f.close()
        self.f_formats.close()
        self.f_authors.close()
        self.f_categories.close()

    def extract_relative_url(self, url):
        if url:
            return re.findall(self.re_url, url)[0]

    def write_entry(self, entry: Dict[str, Any], processed=False, new_content=True):
        row = []
        if processed is False:
            if isinstance(entry.get("dimensions"), str):
                _ = self.extract_dimensions(entry["dimensions"])
                entry["dimensions"], entry["weight"] = _[:4], _[4]
            for k, v in entry.pop("dimensions", {}).items():
                entry["dimension_{}".format(k)] = v

        if int(entry["id"]) in self.harvested:
            return
        self.harvested.add(int(entry["id"]))
        for k in keep_cols:
            v = entry.get(k)
            if isinstance(v, (list, dict)):
                v = json.dumps(v)
            row.append(v)
        self.total_ugc += 1
        self.new_ugc += int(new_content)
        self.wr.writerow(row)

    def extract_dimensions(
        self, dims: str
    ) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """
        Extract dimensions from raw text
        :param dims: raw text with dimensions and weight
        :type dims: str
        :return: Dimensions and weith
        :rype: tuple
        """
        dims = dims.strip()
        x = None
        y = None
        z = None
        w = None
        if not dims:
            return x, y, z, w
        try:
            x = float(re.findall(self.re_dim_x, dims)[0].replace(",", ""))
        except Exception as e:
            print("{}\n{}\n{}".format(e, "x not found", dims))
        try:
            y = float(re.findall(self.re_dim_y, dims)[0].replace(",", ""))
        except Exception as e:
            pass
            # print('{}\n{}\n{}'.format(e, 'y not found', dims))
        try:
            z = float(re.findall(self.re_dim_z, dims)[0].replace(",", ""))
        except Exception as e:
            print("{}\n{}\n{}".format(e, "z not found", dims))
        try:
            w = float(re.findall(self.re_w, dims)[0].replace(",", ""))
        except Exception as e:
            pass
        return x, y, z, w

    def extract_lang(self, lang: str) -> Optional[List[str]]:
        """
        Extract language code from raw text
        :param lang: language raw text
        :return: list of language codes
        :rtype: list
        """
        if not lang.strip():
            return None
        lng = lang.strip()
        if lng:
            try:
                return langcodes.find(lng).language
            except LookupError:
                if lng in self.missing_languages:
                    pass
                else:
                    self.missing_languages.add(lng)
                    print("unknown language: {}".format(lng))
        return None

    def extract_id(self, url: str) -> Optional[str]:
        """
        Extract book id from given url

        :param url: book url
        :return: book id
        :rtype: str
        """
        try:
            return re.findall(self.re_id, url)[0]
        except IndexError as _:
            print(url)
        return None

    def extract_format(self, frmt: str) -> Optional[str]:
        """
        Extract format id from raw text
        :param frmt: format raw text
        :type frmt: str
        :return: format id
        :rtype: str
        """
        if frmt and (frmt_matches := re.findall(self.re_format, frmt)):
            return json.dumps(self.add_formats(frmt_matches[0]))
        return None

    def parse_entry(self, entry):
        """
        Parse a book entry and return in proper format

        :param entry: book entry
        :type entry: dict
        :return: book entry in proper format
        :rtype: dict
        """
        entry["description"] = entry["description"].strip()

        if entry.get("_id"):
            entry["id"] = entry.pop("_id")
        if entry.get("description"):
            entry["description"] = "\n".join(
                l.strip() for l in entry["descitpion"] if l
            )
        if entry.get("indexed-date"):
            entry["index-date"] = entry.pop("indexed-date")
        if entry.get("indexed_date"):
            entry["index-date"] = entry.pop("indexed_date")
        if not entry["id"]:
            entry["id"] = self.extract_id(entry["url"])
        if entry.get("rating-avg", None) is None:
            entry["rating-avg"] = None
        else:
            entry["rating-avg"] = float(entry["rating-avg"])
        if rating_count := entry.pop("rating_count"):
            try:
                entry["rating-count"] = int(re.findall(r"\d+", rating_count)[0])
            except:
                entry["rating-count"] = None

        if bestsellers_rank := entry.pop("bestsellers_rank", None):
            entry["bestsellers-rank"] = int(bestsellers_rank.strip().replace(",", ""))

        if entry.get("url"):
            entry["url"] = self.extract_relative_url(entry.pop("url"))

        if entry.get("price"):
            entry["price"] = float(entry["price"])
        else:
            entry["price"] = None

        entry["publication-place"] = entry.get("publication_city_country", "").strip()

        if entry.get("images"):
            img_obj = entry["images"]
            if isinstance(img_obj, list) and len(img_obj) > 0:
                entry["image-url"] = img_obj[0].get("url")
                entry["image-path"] = img_obj[0].get("path")
                entry["image-checksum"] = img_obj[0].get("checksum")

            # break
        # print(entry.pop('categories'))
        categories__ = json.dumps(
            self.add_categories(
                [
                    cat["name"]
                    for cat in (
                        sorted(
                            entry.pop("categories", []), key=lambda x: x.pop("id", None)
                        )
                    )
                ]
            )
        )

        authors__ = json.dumps(self.add_authors(entry.pop("authors", [])))

        if "ISBN10" in entry:
            entry["isbn10"] = entry.pop("ISBN10")
        if "ISBN13" in entry:
            entry["isbn10"] = entry.pop("ISBN13")

        (
            entry["dimension-x"],
            entry["dimension-y"],
            entry["dimension-z"],
            entry["weight"],
        ) = self.extract_dimensions(entry.pop("dimensions", ""))

        entry["publication-date"] = (
            datetime.datetime.strptime(
                entry.pop("publication_date"), "%d %b %Y"
            ).strftime("%Y-%m-%d %H:%M:%S")
            if entry.get("publication_date")
            else None
        )

        entry.update(
            {
                "categories": categories__,
                "authors": authors__,
                "format": self.extract_format(entry.pop("format", "")),
                "lang": self.extract_lang(entry.pop("language", "")),
            }
        )

        c = tuple(entry.keys())
        for k in c:
            entry[
                k.lower().replace(" ", "-").replace("/", "-").replace("_", "-")
            ] = entry.pop(k)

        for k in entry.keys():
            self.cols.add(k)
        entry = {k: v for k, v in entry.items() if k in keep_cols}

        return entry


def argparsing():
    argus = argparse.ArgumentParser()
    argus.add_argument(
        "--input-jsonb",
        dest="input_jsonb",
        help="Input file of jsonb",
        required=True,
        type=str,
    )
    argus.add_argument(
        "--input-images",
        dest="input_images",
        help="Input folder with images",
        required=False,
        type=str,
    )
    argus.add_argument(
        "-o",
        "--output-folder",
        dest="out",
        help="Output folder path",
        required=False,
        type=str,
        default="../export",
    )
    argus.add_argument("-d", "--dataset", help="Existing dataset", required=False)
    return argus.parse_args()


if __name__ == "__main__":
    args = argparsing()
    bp = BookParser(
        input_file=args.input_jsonb,
        output_folder=args.out,
        dataset=args.dataset,
        image_folder=args.input_images,
    )
    bp.run()
    bp.zip()
