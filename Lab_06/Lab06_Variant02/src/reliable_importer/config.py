from dataclasses import dataclass
from pathlib import Path

import yaml

from reliable_importer.exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class AppConfig:
    input_path: Path
    input_format: str
    output_path: Path
    output_format: str
    backup: bool
    min_year: int
    max_year: int
    skip_invalid: bool
    error_report: Path
    log_level: str
    log_path: Path
    max_bytes: int
    backup_count: int


def load_config(path: Path) -> AppConfig:
    try:
        with path.open("r", encoding="utf-8") as file:
            raw = yaml.safe_load(file)
    except OSError as error:
        raise ConfigurationError(
            f"Cannot read configuration: {path}"
        ) from error
    except yaml.YAMLError as error:
        raise ConfigurationError(
            "Invalid YAML configuration"
        ) from error

    try:
        if not isinstance(raw, dict):
            raise TypeError("Configuration must be a mapping")

        input_data = raw["input"]
        output_data = raw["output"]
        processing = raw["processing"]
        logging_data = raw["logging"]

        if not all(
            isinstance(section, dict)
            for section in (
                input_data,
                output_data,
                processing,
                logging_data,
            )
        ):
            raise TypeError("Configuration sections must be mappings")

        config = AppConfig(
            input_path=Path(input_data["path"]),
            input_format=str(input_data["format"]).lower(),
            output_path=Path(output_data["path"]),
            output_format=str(output_data["format"]).lower(),
            backup=output_data["backup"],
            min_year=int(processing["min_year"]),
            max_year=int(processing["max_year"]),
            skip_invalid=processing["skip_invalid"],
            error_report=Path(processing["error_report"]),
            log_level=str(logging_data["level"]).upper(),
            log_path=Path(logging_data["path"]),
            max_bytes=int(logging_data["max_bytes"]),
            backup_count=int(logging_data["backup_count"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ConfigurationError(
            "Missing or invalid configuration values"
        ) from error

    if config.input_format not in {"csv", "json"}:
        raise ConfigurationError("Input format must be csv or json")

    if config.output_format not in {"json", "jsonl"}:
        raise ConfigurationError("Output format must be json or jsonl")

    if config.min_year > config.max_year:
        raise ConfigurationError(
            "min_year cannot be greater than max_year"
        )

    if not 0 <= config.min_year <= 9999:
        raise ConfigurationError("Invalid minimum year")

    if not 0 <= config.max_year <= 9999:
        raise ConfigurationError("Invalid maximum year")

    if not isinstance(config.skip_invalid, bool):
        raise ConfigurationError("skip_invalid must be true or false")

    if not isinstance(config.backup, bool):
        raise ConfigurationError("backup must be true or false")

    if config.log_level not in {
        "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    }:
        raise ConfigurationError("Invalid logging level")

    if config.max_bytes <= 0 or config.backup_count < 0:
        raise ConfigurationError("Invalid log rotation settings")

    if not config.input_path.is_file():
        raise ConfigurationError(
            f"Input file does not exist: {config.input_path}"
        )

    expected_suffix = "." + config.input_format
    if config.input_path.suffix.lower() != expected_suffix:
        raise ConfigurationError(
            "Input format does not match file extension"
        )

    expected_output_suffix = (
        ".json" if config.output_format == "json" else ".jsonl"
    )
    if config.output_path.suffix.lower() != expected_output_suffix:
        raise ConfigurationError(
            "Output format does not match file extension"
        )

    if config.error_report.resolve() == config.output_path.resolve():
        raise ConfigurationError(
            "Error report and output paths must be different"
        )

    return config