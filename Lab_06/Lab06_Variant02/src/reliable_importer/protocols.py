from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Protocol

from reliable_importer.models import Book


class Importer(Protocol):
    def read(self, path: Path) -> Iterator[dict[str, object]]:
        """Read external records incrementally where the format allows it."""


class Exporter(Protocol):
    def export(self, books: Iterable[Book], path: Path) -> int:
        """Export books and return the number of exported records."""
