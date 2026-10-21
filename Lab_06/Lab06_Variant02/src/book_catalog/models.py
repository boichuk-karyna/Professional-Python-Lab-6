from dataclasses import dataclass
from datetime import date


class BookValidationError(ValueError):
    """Incorrect book data, with a machine-readable field name."""

    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(message)


@dataclass(frozen=True)
class Book:
    isbn: str
    title: str
    author: str
    year: int
    pages: int

    def __post_init__(self):
        for key in ('isbn', 'title', 'author'):
            value = getattr(self, key)
            if not isinstance(value, str) or not value.strip():
                raise BookValidationError(key, f'{key} must be non-empty')
        if type(self.year) is not int or not (1450 <= self.year <= date.today().year + 1):
            raise BookValidationError('year', 'year is outside allowed range')
        if type(self.pages) is not int or self.pages <= 0:
            raise BookValidationError('pages', 'pages must be positive integer')
