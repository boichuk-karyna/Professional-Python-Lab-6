import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path
from collections.abc import Iterator

from reliable_importer.exceptions import (
    DataImportError,
    RecordValidationError,
)
from reliable_importer.models import Book
from reliable_importer.readers import read_csv_rows, read_json_rows
from reliable_importer.validators import parse_book


logger = logging.getLogger(__name__)


@dataclass
class ImportStatistics:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    exported: int = 0
    errors: list[dict[str, object]] = field(default_factory=list)


def import_books(
    path: Path,
    *,
    input_format: str,
    min_year: int,
    max_year: int,
    skip_invalid: bool,
    statistics: ImportStatistics,
) -> Iterator[Book]:
    if input_format == "csv":
        rows = read_csv_rows(path)
    elif input_format == "json":
        rows = read_json_rows(path)
    else:
        raise DataImportError(
            f"Unsupported input format: {input_format}"
        )

    for line_number, row in rows:
        statistics.total += 1

        try:
            book = parse_book(
                row,
                line_number=line_number,
                min_year=min_year,
                max_year=max_year,
            )
        except RecordValidationError as error:
            statistics.invalid += 1

            logger.warning(
                "Invalid record at line %s, field %s: %s",
                error.line_number,
                error.field,
                error,
            )

            statistics.errors.append(
                {
                    "line_number": line_number,
                    "field": error.field or "",
                    "error": str(error),
                }
            )

            if skip_invalid:
                continue

            raise

        statistics.valid += 1
        yield book


def export_error_report(
    errors: list[dict[str, object]],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")

    try:
        with temporary.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["line_number", "field", "error"],
            )
            writer.writeheader()
            writer.writerows(errors)

        temporary.replace(path)

    except OSError as error:
        temporary.unlink(missing_ok=True)
        raise DataImportError(
            f"Cannot write error report: {path}"
        ) from error