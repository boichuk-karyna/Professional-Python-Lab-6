import json
import logging
from collections.abc import Iterable
from pathlib import Path

from reliable_importer.exceptions import DataExportError
from reliable_importer.models import Book


logger = logging.getLogger(__name__)


def export_books(
    books: Iterable[Book],
    path: Path,
    *,
    output_format: str = "json",
    backup: bool = False,
) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_name(path.name + ".tmp")
    backup_path = path.with_name(path.name + ".bak")
    count = 0

    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as file:
            if output_format == "json":
                file.write("[\n")

            first = True

            for book in books:
                record = book.to_dict()

                if output_format == "json":
                    if not first:
                        file.write(",\n")

                    file.write(
                        json.dumps(
                            record,
                            ensure_ascii=False,
                            indent=2,
                        )
                    )
                elif output_format == "jsonl":
                    file.write(
                        json.dumps(
                            record,
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                else:
                    raise ValueError(
                        f"Unsupported output format: {output_format}"
                    )

                first = False
                count += 1

            if output_format == "json":
                file.write("\n]\n")

            file.flush()

        if backup and path.exists():
            backup_temporary = path.with_name(path.name + ".bak.tmp")
            try:
                with path.open("rb") as source:
                    with backup_temporary.open("wb") as destination:
                        while chunk := source.read(1024 * 1024):
                            destination.write(chunk)
                        destination.flush()

                backup_temporary.replace(backup_path)
            finally:
                backup_temporary.unlink(missing_ok=True)

        temporary.replace(path)

        logger.info("Export completed: %s records to %s", count, path)
        return count

    except (OSError, TypeError, ValueError) as error:
        temporary.unlink(missing_ok=True)

        logger.exception("Export failed: %s", path)

        raise DataExportError(
            f"Cannot export books to {path}"
        ) from error