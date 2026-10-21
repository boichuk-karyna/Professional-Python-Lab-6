class ApplicationError(Exception):
    """Базова помилка програми."""


class ConfigurationError(ApplicationError):
    """Помилка конфігурації."""


class DataError(ApplicationError):
    """Базова помилка обробки даних."""


class DataImportError(DataError):
    """Помилка імпорту даних."""


class RecordValidationError(DataError):
    """Помилка перевірки запису."""

    def __init__(
        self,
        message: str,
        *,
        line_number: int | None = None,
        field: str | None = None,
    ) -> None:
        super().__init__(message)
        self.line_number = line_number
        self.field = field


class DataExportError(DataError):
    """Помилка експорту даних."""