from unittest.mock import Mock, AsyncMock
import asyncio
import pytest
from book_catalog.services import Catalog, BookLookupService, AsyncCatalogLookup, ReportService


def test_count(catalog):
    assert len(catalog.all()) == 2


def test_find(catalog, novel):
    assert catalog.find('A1') == novel


def test_missing(catalog):
    assert catalog.find('unknown') is None


def test_author_search(catalog):
    assert len(catalog.by_author('КОВАЛЬ')) == 1


def test_title_search(catalog):
    assert catalog.by_title('python')[0].isbn == 'B2'


def test_year_range(catalog):
    assert [b.isbn for b in catalog.by_year(2000, 2025)] == ['B2']


def test_year_range_invalid(catalog):
    with pytest.raises(ValueError, match='interval'):
        catalog.by_year(2025, 2000)


def test_largest(catalog):
    assert catalog.largest().pages == 320


def test_average(catalog):
    assert catalog.average_pages() == pytest.approx(220.0)


def test_empty():
    c = Catalog()
    assert c.all() == [] and c.largest() is None and c.average_pages() == 0


def test_duplicate(catalog, novel):
    with pytest.raises(ValueError, match='Duplicate'):
        catalog.add(novel)


def test_wrong_item():
    with pytest.raises(TypeError):
        Catalog().add('not a book')


def test_repository_mock(novel):
    repository = Mock(spec=['get'])
    repository.get.return_value = novel
    assert BookLookupService(repository).get('A1') == novel
    repository.get.assert_called_once_with('A1')


def test_repository_failure():
    repository = Mock(spec=['get'])
    repository.get.side_effect = ConnectionError('Repository down')
    with pytest.raises(ConnectionError, match='down'):
        BookLookupService(repository).get('A1')


def test_report_interaction(novel, tmp_path):
    exporter = Mock(spec=['write'])
    exporter.write.return_value = 'OK'
    path = tmp_path / 'report.json'
    assert ReportService(exporter).save([novel], path) == 'OK'
    exporter.write.assert_called_once_with([novel], path)


def test_async_provider(novel):
    provider = Mock(spec=['fetch'])
    provider.fetch = AsyncMock(return_value=novel)
    assert asyncio.run(AsyncCatalogLookup(provider).get('A1')) == novel
    provider.fetch.assert_awaited_once_with('A1')


def test_async_provider_failure():
    provider = Mock(spec=['fetch'])
    provider.fetch = AsyncMock(side_effect=ConnectionError('Offline'))
    with pytest.raises(ConnectionError, match='Offline'):
        asyncio.run(AsyncCatalogLookup(provider).get('A1'))
