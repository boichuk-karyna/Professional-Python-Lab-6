import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from reliable_importer.exceptions import RecordValidationError
from reliable_importer.exporters import JsonExporter
from reliable_importer.models import Book
from reliable_importer.validators import parse_book


class BookValidationTests(unittest.TestCase):
    def test_valid_book(self):
        book = parse_book(
            {"isbn": "9780306406157", "title": "Title", "author": "Author", "year": "2020", "pages": "100"},
            line_number=2, minimum_year=1450, maximum_year=2026,
        )
        self.assertEqual(book.pages, 100)

    def test_invalid_pages(self):
        with self.assertRaises(RecordValidationError):
            parse_book(
                {"isbn": "9780306406157", "title": "Title", "author": "Author", "year": "2020", "pages": "0"},
                line_number=2, minimum_year=1450, maximum_year=2026,
            )

    def test_atomic_json_export(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "books.json"
            path.write_text('[{"old": true}]', encoding="utf-8")
            count = JsonExporter(backup_existing=True).export(
                [Book("9780306406157", "Title", "Author", 2020, 100)], path
            )
            self.assertEqual(count, 1)
            self.assertTrue(path.with_suffix(".json.bak").exists())
            self.assertFalse(path.with_suffix(".json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
