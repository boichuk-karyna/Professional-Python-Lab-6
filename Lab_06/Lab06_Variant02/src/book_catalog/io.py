import csv
import json
from dataclasses import asdict
from pathlib import Path
from .models import Book, BookValidationError


class CatalogImportError(ValueError):
    def __init__(self, line, message):
        self.line = line
        super().__init__(f'CSV line {line}: {message}')


def read_csv(path: str | Path):
    """Streaming generator: one Book per CSV row."""
    with Path(path).open('r', encoding='utf-8-sig', newline='') as file:
        reader = csv.DictReader(file)
        mandatory = {'isbn', 'title', 'author', 'year', 'pages'}
        if not mandatory.issubset(reader.fieldnames or []):
            raise CatalogImportError(1, 'Required columns missing')
        for line, record in enumerate(reader, 2):
            try:
                yield Book(record['isbn'], record['title'], record['author'],
                           int(record['year']), int(record['pages']))
            except (ValueError, TypeError, BookValidationError) as error:
                raise CatalogImportError(line, str(error)) from error


def write_json(books, path: str | Path) -> None:
    target = Path(path)
    payload = [asdict(book) for book in books]
    temp = target.with_name(target.name + '.tmp')
    try:
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        temp.replace(target)
    finally:
        temp.unlink(missing_ok=True)
