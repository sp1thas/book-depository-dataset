from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Unicode,
    Float,
    Date,
    ForeignKey,
    UniqueConstraint,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func

Base = declarative_base()


class TimestampMixin(object):
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class PrimaryKeyMixin(object):
    id = Column(Integer, primary_key=True)


class NameMixin(object):
    name = Column(Unicode, unique=True)


class Author(PrimaryKeyMixin, NameMixin, TimestampMixin, Base):
    __tablename__ = "authors"


class Book(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "books"

    bestsellers_rank = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    dimension_x = Column(Float, nullable=True)
    dimension_y = Column(Float, nullable=True)
    dimension_z = Column(Float, nullable=True)
    edition = Column(Unicode, nullable=True)
    edition_statement = Column(Unicode, nullable=True)
    for_ages = Column(Unicode, nullable=True)
    illustrations_note = Column(Unicode, nullable=True)
    image_checksum = Column(String(32), nullable=True)
    image_path = Column(Unicode(1024), nullable=True)
    image_url = Column(Unicode(1024), nullable=True)
    imprint = Column(Unicode(1024), nullable=True)
    index_date = Column(Date, nullable=True)
    isbn10 = Column(Unicode(24), nullable=True, unique=True)
    isbn13 = Column(Unicode(24), nullable=True, unique=True)
    lang = Column(Unicode(12), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    publication_place = Column(Unicode, nullable=True)
    rating_avg = Column(Float, nullable=True)
    rating_count = Column(Integer, nullable=True)
    title = Column(Unicode(1024), nullable=True)
    url = Column(Unicode(1024), nullable=False, unique=True)
    weight = Column(Float, nullable=True)


class Category(PrimaryKeyMixin, NameMixin, TimestampMixin, Base):
    __tablename__ = "categories"


class Place(PrimaryKeyMixin, NameMixin, TimestampMixin, Base):
    __tablename__ = "places"


class Format(PrimaryKeyMixin, NameMixin, TimestampMixin, Base):
    __tablename__ = "formats"


class BookAuthor(PrimaryKeyMixin, Base):
    __tablename__ = "book_authors"

    author_id = Column(Integer, ForeignKey(f"{Author.__tablename__}.id"))
    book_id = Column(Integer, ForeignKey(f"{Book.__tablename__}.id"))

    __table_args__ = (
        UniqueConstraint(
            "author_id",
            "book_id",
            name="_book_author_uc",
        ),
    )


class BookCategory(PrimaryKeyMixin, Base):
    __tablename__ = "book_categories"
    category_id = Column(Integer, ForeignKey(f"{Category.__tablename__}.id"))
    book_id = Column(Integer, ForeignKey(f"{Book.__tablename__}.id"))

    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "book_id",
            name="_book_category_uc",
        ),
    )


class BookFormat(PrimaryKeyMixin, Base):
    __tablename__ = "book_formats"
    format_id = Column(Integer, ForeignKey(f"{Format.__tablename__}.id"))
    book_id = Column(Integer, ForeignKey(f"{Book.__tablename__}.id"))

    __table_args__ = (
        UniqueConstraint(
            "format_id",
            "book_id",
            name="_book_format_uc",
        ),
    )


class BookPlace(PrimaryKeyMixin, Base):
    __tablename__ = "book_place"
    place_id = Column(Integer, ForeignKey(f"{Place.__tablename__}.id"))
    book_id = Column(Integer, ForeignKey(f"{Book.__tablename__}.id"))

    __table_args__ = (
        UniqueConstraint(
            "place_id",
            "book_id",
            name="_book_place_uc",
        ),
    )
