#!/usr/bin/env python3
"""Validate survey HTML files for structural integrity."""

import os
import sys

SURVEYS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "surveys")
EXPECTED_SURVEYS = ["stmt.html", "askin.html", "askyn.html", "askwh.html", "req.html", "do.html"]

errors = []


def validate_survey(filename):
    filepath = os.path.join(SURVEYS_DIR, filename)

    if not os.path.exists(filepath):
        errors.append(f"MISSING: {filename}")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if len(content) == 0:
        errors.append(f"EMPTY: {filename}")
        return False

    # Check for required crowd-html elements
    if "crowd-form" not in content:
        errors.append(f"STRUCTURE: {filename} missing crowd-form element")

    if "crowd-input" not in content and "crowd-text-area" not in content:
        errors.append(f"STRUCTURE: {filename} missing input elements")

    print(f"  {filename}: {len(content)} bytes - OK")
    return True


def main():
    print("=" * 60)
    print("Survey Validation")
    print("=" * 60)

    for filename in EXPECTED_SURVEYS:
        validate_survey(filename)

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print("\nAll surveys validated successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
