from statistics import mean
from .models import Book


class Catalog:
    def __init__(self, books=()):
        self._items: dict[str, Book] = {}
        for book in books:
            self.add(book)

    def add(self, book: Book) -> None:
        if not isinstance(book, Book):
            raise TypeError('Expected Book')
        if book.isbn in self._items:
            raise ValueError('Duplicate ISBN')
        self._items[book.isbn] = book

    def find(self, isbn: str) -> Book | None:
        return self._items.get(isbn)

    def by_author(self, term: str) -> list[Book]:
        return [b for b in self._items.values() if term.casefold() in b.author.casefold()]

    def by_title(self, term: str) -> list[Book]:
        return [b for b in self._items.values() if term.casefold() in b.title.casefold()]

    def by_year(self, minimum: int, maximum: int) -> list[Book]:
        if minimum > maximum:
            raise ValueError('Invalid year interval')
        return [b for b in self._items.values() if minimum <= b.year <= maximum]

    def largest(self) -> Book | None:
        return max(self._items.values(), key=lambda b: b.pages, default=None)

    def average_pages(self) -> float:
        return mean(b.pages for b in self._items.values()) if self._items else 0.0

    def all(self) -> list[Book]:
        return list(self._items.values())


class BookLookupService:
    def __init__(self, repository):
        self.repository = repository

    def get(self, isbn):
        return self.repository.get(isbn)


class AsyncCatalogLookup:
    def __init__(self, provider):
        self.provider = provider

    async def get(self, isbn):
        return await self.provider.fetch(isbn)


class ReportService:
    def __init__(self, exporter):
        self.exporter = exporter

    def save(self, books, path):
        return self.exporter.write(books, path)
