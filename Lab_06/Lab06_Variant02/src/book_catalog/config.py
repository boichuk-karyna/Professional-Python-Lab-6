import json
import os
from pathlib import Path


def allowed_years():
    minimum = int(os.getenv('BOOK_MIN_YEAR', '1450'))
    maximum = int(os.getenv('BOOK_MAX_YEAR', '2100'))
    if minimum > maximum:
        raise ValueError('Invalid configured year range')
    return minimum, maximum


def load_config(path: str | Path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not isinstance(data.get('min_year'), int):
        raise ValueError('Invalid config')
    return data
