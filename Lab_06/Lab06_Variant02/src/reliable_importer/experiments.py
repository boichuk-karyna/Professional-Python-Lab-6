import csv
import gc
import time
import tracemalloc
from pathlib import Path
from collections.abc import Iterator


def eager_import(path: Path) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def streaming_import(path: Path) -> Iterator[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        yield from csv.DictReader(file)


def measure_memory_and_time(
    function,
    path: Path,
) -> tuple[float, int, int]:
    gc.collect()
    tracemalloc.start()
    start = time.perf_counter()

    count = 0

    try:
        result = function(path)

        for _ in result:
            count += 1

        elapsed = time.perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()

        return elapsed, peak, count
    finally:
        tracemalloc.stop()


def main() -> None:
    sizes = [10_000, 100_000, 500_000]
    directory = Path("output/benchmarks")
    directory.mkdir(parents=True, exist_ok=True)

    for size in sizes:
        path = directory / f"books_{size}.csv"

        with path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(
                ["isbn", "title", "author", "year", "pages"]
            )

            for index in range(size):
                writer.writerow(
                    [
                        "9780306406157",
                        f"Book {index}",
                        "Test Author",
                        2020,
                        200,
                    ]
                )

        for name, function in (
            ("Eager", eager_import),
            ("Streaming", streaming_import),
        ):
            elapsed, peak, count = measure_memory_and_time(
                function,
                path,
            )

            print(
                f"Records={size} | {name} | "
                f"Time={elapsed:.4f}s | "
                f"Peak RAM={peak / 1024 / 1024:.2f} MB | "
                f"Count={count}"
            )


if __name__ == "__main__":
    main()