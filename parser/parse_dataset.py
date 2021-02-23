import argparse
import csv
import datetime
import json
import os
import re
import sys
import shutil
from typing import Dict, List, Union, Any, Tuple, Optional
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
    re_url = re.compile(r"bookdepository.com([\w\-_\d\/]+)[\?^]?")

    id2author: dict = {}
    author2id: dict = {}
    author_id: int = 0
    format2id: dict = {}
    id2format: dict = {}
    categories: dict = {}
    format_id: int = 0
    city_country2id: dict = {}
    city_i: int = 0
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
        self.harvested = set()

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        if self.dataset_path and os.path.exists(self.dataset_path):
            with open(os.path.join(self.dataset_path, "dataset.csv"), "r") as f:
                rd = csv.reader(f)
                for header in rd:
                    break
                self.col_to_index = {_: i for i, _ in enumerate(header)}
                for row in rd:
                    self.harvested.add(int(row[self.col_to_index["id"]]))
                    self.total_ugc += 1

            print("Harvested id successfully loaded")
            for filename in (
                "dataset.csv",
                "authors.csv",
                "categories.csv",
                "places.csv",
                "formats.csv",
            ):
                shutil.copy(
                    os.path.join(self.dataset_path, filename),
                    os.path.join(self.output_folder, filename),
                )
                print(
                    "Successfully copied: {} --> {}".format(
                        self.dataset_path, os.path.join(self.output_folder, filename)
                    )
                )
            with open(os.path.join(self.output_folder, "authors.csv"), "r") as f:
                rd = csv.reader(f)
                for h in rd:
                    name_2_index = {_: i for i, _ in enumerate(h)}
                for row in rd:
                    if row[name_2_index["author_name"]]:
                        self.author2id[row[name_2_index["author_name"]]] = int(
                            row[name_2_index["author_id"]]
                        )
            with open(os.path.join(self.output_folder, "categories.csv"), "r") as f:
                rd = csv.reader(f)
                for h in rd:
                    name_2_index = {_: i for i, _ in enumerate(h)}
                for row in rd:
                    if row[name_2_index["category_name"]]:
                        self.categories[row[name_2_index["category_id"]]] = row[
                            name_2_index["category_name"]
                        ]

            with open(os.path.join(self.output_folder, "places.csv"), "r") as f:
                rd = csv.reader(f)
                for h in rd:
                    name_2_index = {_: i for i, _ in enumerate(h)}
                for row in rd:
                    if row[name_2_index["place_name"]]:
                        self.city_country2id[row[name_2_index["place_name"]]] = int(
                            row[name_2_index["place_id"]]
                        )

            with open(os.path.join(self.output_folder, "formats.csv"), "r") as f:
                rd = csv.reader(f)
                for h in rd:
                    name_2_index = {_: i for i, _ in enumerate(h)}
                for row in rd:
                    if row[name_2_index["format_name"]]:
                        self.id2format[int(row[name_2_index["format_id"]])] = row[
                            name_2_index["format_name"]
                        ]

            self.f = open(os.path.join(self.output_folder, "dataset.csv"), "a")
            self.wr = csv.writer(self.f, quoting=csv.QUOTE_ALL)
        else:
            self.f = open(os.path.join(self.output_folder, "dataset.csv"), "w")
            self.wr = csv.writer(self.f, quoting=csv.QUOTE_ALL)
            self.wr.writerow([_ for _ in keep_cols])

    def run(self):
        with open(self.input_file, "r") as rd:
            for row in rd:
                self.n_rows += 1

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
        with open(os.path.join(self.output_folder, "authors.csv"), "w") as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(["author_id", "author_name"])
            for k, v in sorted(self.author2id.items(), key=lambda item: item[0]):
                wr.writerow([v, k])
        with open(os.path.join(self.output_folder, "categories.csv"), "w") as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(["category_id", "category_name"])
            for k, v in sorted(self.categories.items(), key=lambda item: item[1]):
                wr.writerow([k, v])
        with open(os.path.join(self.output_folder, "formats.csv"), "w") as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(["format_id", "format_name"])
            for k, v in sorted(self.id2format.items(), key=lambda item: item[1]):
                wr.writerow([k, v])
        with open(os.path.join(self.output_folder, "places.csv"), "w") as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(["place_id", "place_name"])
            for k, v in sorted(self.city_country2id.items(), key=lambda item: item[0]):
                wr.writerow([v, k])

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
        cnt = 1
        with ZipFile(os.path.join(self.output_folder, "bdd_0.zip"), "w") as zf:
            for filename in (
                "authors.csv",
                "categories.csv",
                "formats.csv",
                "places.csv",
                "dataset.csv",
            ):
                zf.write(os.path.join(self.output_folder, filename), arcname=filename)
                print(f"generated zip: 'bdd_{cnt}.zip'")
        if self.image_folder:
            cnt = cnt + 1
            zf = ZipFile(os.path.join(self.output_folder, f"bdd_{cnt}.zip"), "w")
            max_zip_size = 3 * 1024 ** 3
            for path, dirs, filenames in os.walk(self.image_folder):
                for filename in filenames:
                    zip_path = self._extract_zip_path(os.path.join(path, filename))
                    zf.write(os.path.join(path, filename), arcname=zip_path)
                    if sys.getsizeof(zf) >= max_zip_size:
                        zf.close()
                        print(f"generated zip: 'bdd_{cnt}.zip'")
                        cnt = cnt + 1
                        zf = ZipFile(
                            os.path.join(self.output_folder, f"bdd_{cnt}.zip"), "w"
                        )
            zf.close()

    def close(self):
        """
        Close open file
        :return:
        """
        self.f.close()

    def extract_relative_url(self, url):
        if url:
            return re.findall(self.re_url, url)[0]

    def write_entry(self, entry: Dict[str, Any]):
        row = []
        if isinstance(entry.get("dimensions"), str):
            _ = self.extract_dimensions(entry["dimensions"])
            entry["dimensions"], entry["weight"] = _[:4], _[4]
        for k, v in entry.pop("dimensions", {}).items():
            entry["dimension_{}".format(k)] = v

        if int(entry["id"]) in self.harvested:
            return
        for k in keep_cols:
            v = entry.get(k)
            if isinstance(v, (list, dict)):
                v = json.dumps(v)
            row.append(v)
        self.total_ugc += 1
        self.new_ugc += 1
        self.wr.writerow(row)

    def extract_publish_place(self, place):
        if not place:
            return None
        place = str(place).strip()
        if place in self.city_country2id:
            return self.city_country2id[place]
        else:
            self.city_i += 1
            self.city_country2id[place] = self.city_i
            return self.city_country2id[place]

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

    def parse_entry(self, entry):
        """
        Parse a book entry and return in proper format

        :param entry: book entry
        :type entry: dict
        :return: book entry in proper format
        :rtype: dict
        """
        if entry.get("_id"):
            entry["id"] = entry.pop("_id")
        if entry.get("indexed-date"):
            entry["index-date"] = entry.pop("indexed-date")
        if not entry["id"]:
            entry["id"] = self.extract_id(entry["url"])
        if entry.get("rating-avg", None) is None:
            entry["rating-avg"] = None
        else:
            entry["rating-avg"] = float(entry["rating-avg"])
        if entry.get("rating-count") is None:
            pass
        else:
            entry["rating-count"] = int(entry["rating-count"])
        if entry.get("bestsellers-rank") is None:
            pass
        else:
            entry["bestsellers-rank"] = int(entry["bestsellers-rank"])

        if entry.get("url"):
            entry["url"] = self.extract_relative_url(entry.pop("url"))

        if entry.get("publication-city-country"):
            entry["publication-place"] = self.extract_publish_place(
                entry.pop("publication-city-country")
            )

        if entry.get("images"):
            img_obj = entry["images"]
            if isinstance(img_obj, list) and len(img_obj) > 0:
                entry["image-url"] = img_obj[0].get("url")
                entry["image-path"] = img_obj[0].get("path")
                entry["image-checksum"] = img_obj[0].get("checksum")

            # break
        categories__ = []

        categories_labels = entry.pop("categories", [])
        if categories_labels:
            for category in categories_labels:
                if category["id"] in self.categories:
                    pass
                else:
                    self.categories[category["id"]] = category["name"]
                if category["id"] not in categories__:
                    categories__.append(category["id"])
        else:
            pass

        authors__ = []

        authors_labels = entry.pop("authors", [])

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

        try:
            entry["publication-date"] = (
                datetime.datetime.strptime(
                    entry["publication-date"], "%Y-%m-%d %H:%M:%S"
                ).strftime("%Y-%m-%d")
                if entry.get("publication-date")
                else None
            )
        except:
            entry["publication-date"] = None

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
