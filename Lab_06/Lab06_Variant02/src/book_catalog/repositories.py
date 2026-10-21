"""In-memory repository for the book catalog (variant 2)."""
from .models import Book


class BookRepository:
    """Store and retrieve books by ISBN; suitable as a fake repository in tests."""

    def __init__(self):
        self._books: dict[str, Book] = {}

    def add(self, book: Book) -> None:
        if not isinstance(book, Book):
            raise TypeError('Expected Book')
        if book.isbn in self._books:
            raise ValueError('Duplicate ISBN')
        self._books[book.isbn] = book

    def get(self, isbn: str) -> Book | None:
        return self._books.get(isbn)

    def all(self) -> list[Book]:
        return list(self._books.values())

    def by_author(self, author: str) -> list[Book]:
        return [book for book in self._books.values() if author.casefold() in book.author.casefold()]

    def by_title(self, title: str) -> list[Book]:
        return [book for book in self._books.values() if title.casefold() in book.title.casefold()]
