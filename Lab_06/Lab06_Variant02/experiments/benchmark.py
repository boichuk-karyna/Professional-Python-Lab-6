import csv
import time
import tracemalloc
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def create_csv(path: Path, count: int) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["isbn", "title", "author", "year", "pages"])
        for index in range(count):
            writer.writerow(["9780306406157", f"Book {index}", "Test Author", 2020, 200 + index % 500])


def eager(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as file:
        return len(list(csv.DictReader(file)))


def streaming(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as file:
        return sum(1 for _ in csv.DictReader(file))


def measure(function, path: Path):
    tracemalloc.start()
    started = time.perf_counter()
    count = function(path)
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return count, elapsed, peak / 1024 / 1024


def main() -> None:
    temporary_dir = ROOT / "output" / "benchmark"
    temporary_dir.mkdir(parents=True, exist_ok=True)
    print("records,method,count,time_seconds,peak_memory_mb")
    for size in (10_000, 100_000, 500_000):
        path = temporary_dir / f"books_{size}.csv"
        create_csv(path, size)
        for label, function in (("eager", eager), ("streaming", streaming)):
            count, elapsed, peak = measure(function, path)
            print(f"{size},{label},{count},{elapsed:.4f},{peak:.2f}")
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
