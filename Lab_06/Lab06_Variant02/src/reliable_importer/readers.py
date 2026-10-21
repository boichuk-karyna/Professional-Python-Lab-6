import csv
import json
from collections.abc import Iterator
from pathlib import Path

from reliable_importer.exceptions import DataImportError


REQUIRED_FIELDS = {"isbn", "title", "author", "year", "pages"}


def read_csv_rows(
    path: Path,
) -> Iterator[tuple[int, dict[str, str]]]:
    try:
        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise DataImportError("CSV file has no header")

            if (
                len(reader.fieldnames) != len(set(reader.fieldnames))
                or not REQUIRED_FIELDS.issubset(reader.fieldnames)
            ):
                raise DataImportError(
                    "CSV header is missing required fields "
                    "or contains duplicate names"
                )

            for line_number, row in enumerate(reader, start=2):
                if None in row or any(
                    value is None for value in row.values()
                ):
                    yield line_number, {}
                else:
                    yield line_number, row

    except OSError as error:
        raise DataImportError(
            f"Cannot read CSV file: {path}"
        ) from error
    except csv.Error as error:
        raise DataImportError(
            f"Invalid CSV file: {path}"
        ) from error


def read_json_rows(
    path: Path,
) -> Iterator[tuple[int, dict[str, object]]]:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except OSError as error:
        raise DataImportError(
            f"Cannot read JSON file: {path}"
        ) from error
    except json.JSONDecodeError as error:
        raise DataImportError(
            f"Invalid JSON file: {path}"
        ) from error

    if not isinstance(data, list):
        raise DataImportError("JSON input must contain an array")

    for index, record in enumerate(data, start=1):
        if not isinstance(record, dict):
            yield index, {}
        else:
            yield index, record