#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from fixturelib import DATASET_ID, DATASET_VERSION, generate_dataset, relative_file_map


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TARGET = REPOSITORY_ROOT / "datasets" / DATASET_ID / DATASET_VERSION


def check_dataset(target: Path) -> int:
    if not target.is_dir():
        print(f"dataset is missing: {target}")
        return 1
    with tempfile.TemporaryDirectory(prefix="erp-docflow-fixtures-") as temporary:
        regenerated = Path(temporary) / DATASET_ID / DATASET_VERSION
        generate_dataset(regenerated)
        expected = relative_file_map(regenerated)
        actual = relative_file_map(target)
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        changed = sorted(
            name for name in set(expected) & set(actual) if expected[name] != actual[name]
        )
        if missing or extra or changed:
            for label, values in (("missing", missing), ("extra", extra), ("changed", changed)):
                for value in values:
                    print(f"{label}: {value}")
            return 1
    print(f"dataset is deterministic and current: {target}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic synthetic document fixtures")
    parser.add_argument("--check", action="store_true", help="regenerate in a temporary directory and compare")
    parser.add_argument("--output", type=Path, default=DEFAULT_TARGET, help="dataset output directory")
    arguments = parser.parse_args()
    target = arguments.output.resolve()
    if arguments.check:
        return check_dataset(target)
    manifest = generate_dataset(target)
    print(f"generated {len(manifest['fixtures'])} fixtures in {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
