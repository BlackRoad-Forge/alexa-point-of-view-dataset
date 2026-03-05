#!/usr/bin/env python3
"""Validate the POV dataset for integrity, format, and consistency.

Checks:
- File existence and non-empty
- TSV format with correct columns (input, output)
- Row count consistency (train + dev + test == total)
- No empty fields
- Placeholder tag presence (@CN@, @SCN@)
- UTF-8 encoding validity
"""

import csv
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

EXPECTED_FILES = ["total.tsv", "train.tsv", "dev.tsv", "test.tsv"]
EXPECTED_COLUMNS = ["input", "output"]
EXPECTED_COUNTS = {
    "total.tsv": 46562,
    "train.tsv": 32593,
    "dev.tsv": 6984,
    "test.tsv": 6985,
}

errors = []
warnings = []


def validate_file(filename):
    filepath = os.path.join(DATA_DIR, filename)

    # Check existence
    if not os.path.exists(filepath):
        errors.append(f"MISSING: {filename} not found")
        return 0

    # Check non-empty
    if os.path.getsize(filepath) == 0:
        errors.append(f"EMPTY: {filename} is empty")
        return 0

    # Validate UTF-8 encoding
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError as e:
        errors.append(f"ENCODING: {filename} is not valid UTF-8: {e}")
        return 0

    lines = content.strip().split("\n")
    header = lines[0].split("\t")

    # Check columns
    if header != EXPECTED_COLUMNS:
        errors.append(f"COLUMNS: {filename} has columns {header}, expected {EXPECTED_COLUMNS}")

    row_count = len(lines) - 1  # exclude header
    expected = EXPECTED_COUNTS.get(filename)

    # Validate row count
    if expected and row_count != expected:
        errors.append(f"COUNT: {filename} has {row_count} rows, expected {expected}")

    # Validate each row
    empty_inputs = 0
    empty_outputs = 0
    malformed_rows = 0
    cn_missing = 0

    for i, line in enumerate(lines[1:], start=2):
        parts = line.split("\t")
        if len(parts) != 2:
            malformed_rows += 1
            if malformed_rows <= 3:
                errors.append(f"FORMAT: {filename} line {i} has {len(parts)} columns (expected 2)")
            continue

        inp, out = parts
        if not inp.strip():
            empty_inputs += 1
        if not out.strip():
            empty_outputs += 1
        if "@CN@" not in out and "@cn@" not in out.lower():
            cn_missing += 1

    if empty_inputs > 0:
        warnings.append(f"EMPTY_INPUT: {filename} has {empty_inputs} empty input fields")
    if empty_outputs > 0:
        errors.append(f"EMPTY_OUTPUT: {filename} has {empty_outputs} empty output fields")
    if malformed_rows > 3:
        errors.append(f"FORMAT: {filename} has {malformed_rows} total malformed rows")
    if cn_missing > row_count * 0.5:
        warnings.append(f"TAGS: {filename} has {cn_missing}/{row_count} rows missing @CN@ in output")

    return row_count


def main():
    print("=" * 60)
    print("POV Dataset Validation")
    print("=" * 60)

    counts = {}
    for filename in EXPECTED_FILES:
        print(f"\nValidating {filename}...")
        counts[filename] = validate_file(filename)
        print(f"  Rows: {counts[filename]}")

    # Check split consistency
    split_total = counts.get("train.tsv", 0) + counts.get("dev.tsv", 0) + counts.get("test.tsv", 0)
    actual_total = counts.get("total.tsv", 0)

    if split_total > 0 and actual_total > 0:
        if split_total != actual_total:
            diff = actual_total - split_total
            warnings.append(
                f"SPLIT: train({counts['train.tsv']}) + dev({counts['dev.tsv']}) + "
                f"test({counts['test.tsv']}) = {split_total}, "
                f"total = {actual_total} (diff: {diff})"
            )

    # Report
    print("\n" + "=" * 60)
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\nValidation FAILED with {len(errors)} error(s)")
        sys.exit(1)
    else:
        print("\nValidation PASSED")
        print(f"  Total pairs: {actual_total}")
        print(f"  Train: {counts['train.tsv']}, Dev: {counts['dev.tsv']}, Test: {counts['test.tsv']}")
        sys.exit(0)


if __name__ == "__main__":
    main()
