import json
import pytest
from book_catalog.io import read_csv, write_json, CatalogImportError
from book_catalog.services import Catalog
from book_catalog.config import allowed_years


@pytest.mark.integration
def test_csv_search_json(temporary_catalog, tmp_path):
    catalog = Catalog(read_csv(temporary_catalog))
    result = catalog.by_title('Кобзар')
    output = tmp_path / 'filtered.json'
    write_json(result, output)
    assert json.loads(output.read_text(encoding='utf-8'))[0]['author'] == 'Шевченко'


@pytest.mark.integration
def test_csv_aggregate_export(tmp_path):
    source = tmp_path / 'books.csv'
    source.write_text('isbn,title,author,year,pages\n1,A,B,2020,100\n2,C,D,2022,200\n', encoding='utf-8')
    catalog = Catalog(read_csv(source))
    assert catalog.average_pages() == pytest.approx(150)
    output = tmp_path / 'all.json'
    write_json(catalog.all(), output)
    assert len(json.loads(output.read_text(encoding='utf-8'))) == 2


@pytest.mark.integration
def test_malformed_csv_does_not_export(tmp_path):
    source = tmp_path / 'bad.csv'
    source.write_text('isbn,title,author,year,pages\n1,A,B,2020,wrong\n', encoding='utf-8')
    output = tmp_path / 'result.json'
    with pytest.raises(CatalogImportError):
        write_json(Catalog(read_csv(source)).all(), output)
    assert not output.exists()


@pytest.mark.integration
def test_config_filter_flow(tmp_path, monkeypatch):
    monkeypatch.setenv('BOOK_MIN_YEAR', '2000')
    monkeypatch.setenv('BOOK_MAX_YEAR', '2024')
    path = tmp_path / 'books.csv'
    path.write_text('isbn,title,author,year,pages\n1,A,B,1900,100\n2,C,D,2022,200\n', encoding='utf-8')
    catalog = Catalog(read_csv(path))
    selected = catalog.by_year(*allowed_years())
    assert [b.isbn for b in selected] == ['2']
