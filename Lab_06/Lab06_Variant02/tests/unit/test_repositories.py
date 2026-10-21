import pytest
from book_catalog.repositories import BookRepository
from book_catalog.services import BookLookupService


def test_repository_add_and_get(novel):
    repository = BookRepository()
    repository.add(novel)
    assert repository.get(novel.isbn) == novel
    assert BookLookupService(repository).get(novel.isbn) == novel


def test_repository_missing():
    assert BookRepository().get('missing') is None


def test_repository_all(novel):
    repository = BookRepository()
    assert repository.all() == []
    repository.add(novel)
    assert repository.all() == [novel]


def test_repository_duplicate(novel):
    repository = BookRepository()
    repository.add(novel)
    with pytest.raises(ValueError, match='Duplicate'):
        repository.add(novel)


def test_repository_rejects_invalid_book():
    with pytest.raises(TypeError, match='Book'):
        BookRepository().add(object())


def test_repository_filters(novel):
    repository = BookRepository()
    repository.add(novel)
    assert repository.by_author(novel.author.upper()) == [novel]
    assert repository.by_title(novel.title.upper()) == [novel]
    assert repository.by_title('NONEXISTENT') == []
