from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Book:
    isbn: str
    title: str
    author: str
    year: int
    pages: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class Importer(Protocol):
    def read(
        self,
        path: Path,
    ) -> Iterator[dict[str, object]]:
        ...


class Exporter(Protocol):
    def export(
        self,
        records: Iterable[Book],
        path: Path,
    ) -> int:
        ...