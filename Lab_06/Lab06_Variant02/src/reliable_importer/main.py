import logging
import sys
from pathlib import Path

from reliable_importer.config import load_config
from reliable_importer.exceptions import ApplicationError
from reliable_importer.exporters import export_books
from reliable_importer.logging_config import configure_logging
from reliable_importer.services import (
    ImportStatistics,
    export_error_report,
    import_books,
)
from reliable_importer.utils import logged_operation


logger = logging.getLogger(__name__)


def main() -> int:
    try:
        config = load_config(Path("config.yaml"))

        configure_logging(
            config.log_level,
            config.log_path,
            config.max_bytes,
            config.backup_count,
        )

        logger.info("Application started")

        statistics = ImportStatistics()

        with logged_operation("Book import/export"):
            books = import_books(
                config.input_path,
                input_format=config.input_format,
                min_year=config.min_year,
                max_year=config.max_year,
                skip_invalid=config.skip_invalid,
                statistics=statistics,
            )

            statistics.exported = export_books(
                books,
                config.output_path,
                output_format=config.output_format,
                backup=config.backup,
            )

            export_error_report(
                statistics.errors,
                config.error_report,
            )

        logger.info(
            "Statistics: total=%s, valid=%s, invalid=%s, exported=%s",
            statistics.total,
            statistics.valid,
            statistics.invalid,
            statistics.exported,
        )

        logger.info("Application completed successfully")
        return 0

    except ApplicationError as error:
        logger.error("Application error: %s", error)
        return 1

    except OSError:
        logger.exception("Unexpected file system error")
        return 1


if __name__ == "__main__":
    sys.exit(main())