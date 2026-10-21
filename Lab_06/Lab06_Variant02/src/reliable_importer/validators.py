import math
import re
from collections.abc import Mapping

from reliable_importer.exceptions import RecordValidationError
from reliable_importer.models import Book


def is_valid_isbn(isbn: str) -> bool:
    value = re.sub(r"[- ]", "", isbn).upper()

    if re.fullmatch(r"\d{13}", value):
        digits = [int(char) for char in value]
        checksum = sum(
            digit * (1 if index % 2 == 0 else 3)
            for index, digit in enumerate(digits)
        )
        return checksum % 10 == 0

    if re.fullmatch(r"\d{9}[\dX]", value):
        digits = [
            10 if char == "X" else int(char)
            for char in value
        ]
        return sum(
            digit * (10 - index)
            for index, digit in enumerate(digits)
        ) % 11 == 0

    return False


def parse_book(
    row: Mapping[str, object],
    *,
    line_number: int,
    min_year: int,
    max_year: int,
) -> Book:
    isbn = row.get("isbn")

    if not isinstance(isbn, str) or not is_valid_isbn(isbn):
        raise RecordValidationError(
            "Invalid ISBN-10 or ISBN-13",
            line_number=line_number,
            field="isbn",
        )

    isbn = re.sub(r"[- ]", "", isbn).upper()

    title = row.get("title")
    if not isinstance(title, str) or not title.strip():
        raise RecordValidationError(
            "Book title cannot be empty",
            line_number=line_number,
            field="title",
        )

    author = row.get("author")
    if not isinstance(author, str) or not author.strip():
        raise RecordValidationError(
            "Book author cannot be empty",
            line_number=line_number,
            field="author",
        )

    try:
        raw_year = row["year"]
        if isinstance(raw_year, bool):
            raise ValueError("Boolean is not a year")
        year = int(str(raw_year).strip())
    except (KeyError, TypeError, ValueError) as error:
        raise RecordValidationError(
            "Year must be an integer",
            line_number=line_number,
            field="year",
        ) from error

    if not min_year <= year <= max_year:
        raise RecordValidationError(
            f"Year must be between {min_year} and {max_year}",
            line_number=line_number,
            field="year",
        )

    try:
        raw_pages = row["pages"]
        if isinstance(raw_pages, bool):
            raise ValueError("Boolean is not a page count")

        pages_text = str(raw_pages).strip()
        if not re.fullmatch(r"\+?\d+", pages_text):
            raise ValueError("Pages must be a whole number")

        pages = int(pages_text)
    except (KeyError, TypeError, ValueError) as error:
        raise RecordValidationError(
            "Pages must be a positive integer",
            line_number=line_number,
            field="pages",
        ) from error

    if pages <= 0:
        raise RecordValidationError(
            "Pages must be greater than zero",
            line_number=line_number,
            field="pages",
        )

    return Book(
        isbn=isbn,
        title=title.strip(),
        author=author.strip(),
        year=year,
        pages=pages,
    )