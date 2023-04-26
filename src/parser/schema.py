import datetime
import re
from typing import List

import langcodes  # type: ignore
from pydantic import BaseModel, Field, validator, root_validator
from pydantic import HttpUrl

author_map: dict = dict()
format_map: dict = dict()
missing_languages: set = set()

re_dim_x = re.compile(r"[\d.,]+")
re_dim_y = re.compile(r"x\s+([\d.,]+)\s+")
re_dim_z = re.compile(r"([\d.,]+)mm")
re_w = re.compile(r"([\d.,]+)g")


def to_kebab_case(v: str) -> str:
    return v.replace("_", "-")


class Category(BaseModel):
    id: int = Field(..., description="", ge=1)
    name: str = Field(..., description="")


class Author(BaseModel):
    id: int = Field(..., description="", ge=1)
    name: str = Field(..., description="")


class Format(BaseModel):
    id: int = Field(..., description="", ge=1)
    name: str = Field(..., description="")


class Dimensions(BaseModel):
    x: float = Field(None, description="", gt=0)
    y: float = Field(None, description="", gt=0)
    z: float = Field(None, description="", gt=0)


class Book(BaseModel):
    authors: List[Author] = Field(None)
    bestsellers_rank: int = Field(None, description="", ge=1)
    categories: List[str] = Field(None, description="")
    description: str = Field(None, description="")
    dimensions: Dimensions = Field(None, description="")
    edition: str = Field(None, description="")
    edition_statement: str = Field(None, description="")
    for_ages: str = Field(None, description="")
    format: Format = Field(None, description="")
    id: int = Field(..., description="", ge=1)
    illustrations_note: str = Field(None, description="")
    image_url: HttpUrl = Field(None, description="")
    imprint: str = Field(None, description="")
    index_date: datetime.datetime = Field(None, description="")
    isbn10: str = Field(..., description="")
    isbn13: str = Field(..., description="")
    lang: str = Field(..., description="")
    publication_date: datetime.datetime = Field(None, description="")
    publication_place: str = Field(None, description="")
    rating_avg: float = Field(None, description="", ge=0, le=10)
    rating_count: int = Field(None, description="", ge=0)
    title: str = Field(None, description="")
    url: HttpUrl = Field(..., description="")
    weight: float = Field(None, description="", ge=0)

    @validator("authors", each_item=True, pre=True)
    def parse_authors(cls, v: str):
        name = v
        if name in author_map:
            _id = author_map[v]
        else:
            _id = max(author_map.keys()) + 1
            author_map[v] = _id
        return Author(id=_id, name=name)

    @validator("bestsellers_rank", pre=True)
    def parse_bestsellers_rank(cls, v: str):
        return int(v.strip().replace(",", ""))

    @validator("categories", each_item=True, pre=True)
    def parse_categories(cls, v: dict):
        return Category(id=int(v["id"]), name=v["name"].strip())

    @validator("description", pre=True)
    def parse_description(cls, v):
        if isinstance(v, list):
            return "\n".join(re.sub(r"\s\s+", "", l) for l in v if l)
        if v:
            return v.strip()

    @validator("dimensions", "weight", pre=True)
    def parse_dimensions_n_weight(cls, v):
        """
        Extract dimensions from raw text
        """
        dims = v[0].strip()
        x = None
        y = None
        z = None
        w = None
        if not dims:
            return x, y, z, w
        try:
            x = float(re.findall(re_dim_x, dims)[0].replace(",", ""))
        except Exception as e:
            print("{}\n{}\n{}".format(e, "x not found", dims))
        try:
            y = float(re.findall(re_dim_y, dims)[0].replace(",", ""))
        except Exception as e:
            pass
            # print('{}\n{}\n{}'.format(e, 'y not found', dims))
        try:
            z = float(re.findall(re_dim_z, dims)[0].replace(",", ""))
        except Exception as e:
            print("{}\n{}\n{}".format(e, "z not found", dims))
        try:
            w = float(re.findall(re_w, dims)[0].replace(",", ""))
        except Exception as e:
            pass

        return Dimensions(x=x, y=y, z=z), w

    @validator("edition")
    def parse_edition(cls, v):
        if v:
            return v.strip()
        return None

    @validator("edition_statement")
    def parse_edition_statement(cls, v):
        if v:
            return v.strip()
        return None

    @validator("for_ages")
    def parse_for_ages(cls, v):
        if v:
            return v.strip()
        return None

    @validator("format", pre=True)
    def parse_format(cls, v: str):
        name = v
        if name in format_map:
            _id = format_map[v]
        else:
            _id = max(format_map.keys()) + 1
            format_map[v] = _id
        return Format(id=_id, name=name)

    @validator("id")  # type: ignore
    def parse_for_ages(cls, v):
        return v.strip()

    @validator("illustrations_note", pre=True)
    def parse_illustrations_note(cls, v: str):
        if v:
            return v.strip()
        return None

    @root_validator(pre=True)
    def parse_image_url(cls, values):
        if images := values.get("images"):
            values["image_url"] = images[0].get("url")
        return values

    @validator("imprint", pre=True)
    def parse_imprint(cls, v):
        return v.strip() if v else None

    @root_validator(pre=True)
    def rename_index_date(cls, values):
        if not values.get("index_date"):
            values["index_date"] = values.pop("indexed_date")
        return values

    @validator("index_date", pre=True)
    def parse_index_date(cls, v):
        if v:
            return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return None

    @root_validator("isbn10", pre=True)
    def parse_isbn10(cls, values):
        if isbn10 := values.pop("ISBN10"):
            values["isbn10"] = isbn10.strip()
        return values

    @root_validator("isbn13", pre=True)  # type: ignore
    def parse_isbn10(cls, values):
        if isbn10 := values.pop("ISBN13"):
            values["isbn13"] = isbn10.strip()
        return values

    @validator("lang", pre=True)
    def parse_lang(cls, v: str):
        lang = v
        if not lang.strip():
            return None
        lng = lang.strip()
        if lng:
            try:
                return langcodes.find(lng).language
            except LookupError:
                if lng in missing_languages:
                    pass
                else:
                    missing_languages.add(lng)
                    print("unknown language: {}".format(lng))
        return None

    @validator("publication_date", pre=True)
    def parse_publication_date(cls, v):
        return (
            datetime.datetime.strptime(v, "%d %b %Y").strftime("%Y-%m-%d %H:%M:%S")
            if v
            else None
        )
