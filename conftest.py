import pytest
from book_catalog.models import Book
from book_catalog.services import Catalog


@pytest.fixture
def novel():
    return Book('A1', 'Кобзар', 'Тарас Шевченко', 1840, 120)


@pytest.fixture
def textbook():
    return Book('B2', 'Python для всіх', 'Олена Коваль', 2023, 320)


@pytest.fixture
def catalog(novel, textbook):
    return Catalog([novel, textbook])


@pytest.fixture
def book_factory():
    def build(**kwargs):
        fields = dict(isbn='X', title='Тест', author='Автор', year=2020, pages=100)
        fields.update(kwargs)
        return Book(**fields)
    return build


@pytest.fixture
def temporary_catalog(tmp_path):
    path = tmp_path / 'books.csv'
    path.write_text('isbn,title,author,year,pages\nA1,Кобзар,Шевченко,1840,120\n', encoding='utf-8')
    yield path
    path.unlink(missing_ok=True)
