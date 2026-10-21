import json
import pytest
from book_catalog.io import read_csv, write_json, CatalogImportError
from book_catalog.config import allowed_years, load_config


def test_csv_stream(temporary_catalog):
    assert next(read_csv(temporary_catalog)).isbn == 'A1'


def test_missing_column(tmp_path):
    f = tmp_path / 'bad.csv'
    f.write_text('isbn,title\nA1,Book\n', encoding='utf-8')
    with pytest.raises(CatalogImportError, match='columns'):
        list(read_csv(f))


def test_invalid_csv_record(tmp_path):
    f = tmp_path / 'bad.csv'
    f.write_text('isbn,title,author,year,pages\n1,A,B,2020,xyz\n', encoding='utf-8')
    with pytest.raises(CatalogImportError) as exc:
        list(read_csv(f))
    assert exc.value.line == 2
    assert isinstance(exc.value.__cause__, ValueError)


def test_json_export(tmp_path, novel):
    path = tmp_path / 'out.json'
    write_json([novel], path)
    assert json.loads(path.read_text(encoding='utf-8'))[0]['isbn'] == 'A1'
    assert not (tmp_path / 'out.json.tmp').exists()


def test_default_env(monkeypatch):
    monkeypatch.delenv('BOOK_MIN_YEAR', raising=False)
    monkeypatch.delenv('BOOK_MAX_YEAR', raising=False)
    assert allowed_years() == (1450, 2100)


def test_custom_env(monkeypatch):
    monkeypatch.setenv('BOOK_MIN_YEAR', '1800')
    monkeypatch.setenv('BOOK_MAX_YEAR', '2025')
    assert allowed_years() == (1800, 2025)


def test_bad_env(monkeypatch):
    monkeypatch.setenv('BOOK_MIN_YEAR', '2300')
    monkeypatch.setenv('BOOK_MAX_YEAR', '2020')
    with pytest.raises(ValueError):
        allowed_years()


def test_json_config(tmp_path):
    path = tmp_path / 'config.json'
    path.write_text('{"min_year": 1800}', encoding='utf-8')
    assert load_config(path)['min_year'] == 1800


def test_invalid_config(tmp_path):
    path = tmp_path / 'config.json'
    path.write_text('{"min_year": "invalid"}', encoding='utf-8')
    with pytest.raises(ValueError, match='config'):
        load_config(path)
