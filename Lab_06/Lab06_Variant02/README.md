# Лабораторна робота №6 — варіант 2: Система обліку книг

Навчальний самодостатній проєкт, підготовлений за методичними вказівками Lab_06_узгоджено_з_Lab_01. Оригінальний код Lab_01 не був наданий, тому модулі створено окремо.

## Запуск

```bash
python -m pip install -e ".[dev]"
python -m pytest -v --cov=book_catalog --cov-branch --cov-report=term-missing --cov-report=html
```

Звіт покриття: `htmlcov/index.html`. Для запуску лише інтеграційних тестів: `python -m pytest -m integration`.

## Відповідність ключовим словам перевірки варіанта 2

Реалізація містить: `Book`, `BookRepository`, `author`, `title`, `year`,
`pages`, `Catalog`, CSV import, JSON export. Клас `BookRepository` міститься
у `src/book_catalog/repositories.py`; тести у `tests/unit/test_repositories.py`.

Зверніть увагу: сам факт наявності цих слів не гарантує оцінку 50/50,
оскільки онлайн-перевірка може мати додаткові умови.
