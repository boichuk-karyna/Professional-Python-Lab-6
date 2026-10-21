import pytest
from book_catalog.models import Book, BookValidationError


def test_create_book(novel):
    assert novel.title == 'Кобзар'


@pytest.mark.parametrize('field,value', [('isbn', ''), ('title', '   '), ('author', None)])
def test_required_fields(book_factory, field, value):
    with pytest.raises(BookValidationError) as exc:
        book_factory(**{field: value})
    assert exc.value.field == field


@pytest.mark.parametrize('pages', [-2, 0, 2.5, True])
def test_invalid_pages(book_factory, pages):
    with pytest.raises(BookValidationError, match='pages'):
        book_factory(pages=pages)


@pytest.mark.parametrize('year', [1449, -1, 9999, 2020.5, True])
def test_invalid_year(book_factory, year):
    with pytest.raises(BookValidationError, match='year'):
        book_factory(year=year)


def test_minimum_year(book_factory):
    assert book_factory(year=1450).year == 1450


def test_minimum_pages(book_factory):
    assert book_factory(pages=1).pages == 1


def test_immutable(novel):
    from dataclasses import FrozenInstanceError
    with pytest.raises(FrozenInstanceError):
        novel.pages = 9
