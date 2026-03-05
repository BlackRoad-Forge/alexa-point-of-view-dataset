#!/usr/bin/env python3
"""End-to-end tests for the POV dataset repository.

Validates all components: data, surveys, scripts, workflows, and configs.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
passed = 0


def check(condition, name):
    global passed
    if condition:
        print(f"  PASS: {name}")
        passed += 1
    else:
        print(f"  FAIL: {name}")
        errors.append(name)


def file_exists(path):
    return os.path.exists(os.path.join(ROOT, path))


def file_nonempty(path):
    fp = os.path.join(ROOT, path)
    return os.path.exists(fp) and os.path.getsize(fp) > 0


def file_contains(path, text):
    fp = os.path.join(ROOT, path)
    if not os.path.exists(fp):
        return False
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        return text in f.read()


def main():
    print("=" * 60)
    print("End-to-End Repository Validation")
    print("=" * 60)

    # Data files
    print("\n[Data Files]")
    for f in ["data/total.tsv", "data/train.tsv", "data/dev.tsv", "data/test.tsv"]:
        check(file_nonempty(f), f"Data file exists: {f}")

    # Surveys
    print("\n[Survey Files]")
    for f in ["surveys/stmt.html", "surveys/askin.html", "surveys/askyn.html",
              "surveys/askwh.html", "surveys/req.html", "surveys/do.html"]:
        check(file_nonempty(f), f"Survey exists: {f}")

    # Core files
    print("\n[Core Files]")
    for f in ["README.md", "LICENSE", "NOTICE", "version",
              "CODE_OF_CONDUCT.md", "CONTRIBUTING.md", ".gitignore"]:
        check(file_nonempty(f), f"Core file exists: {f}")

    # Scripts
    print("\n[Scripts]")
    for f in ["scripts/validate_data.py", "scripts/check_surveys.py", "scripts/build_pages.py"]:
        check(file_nonempty(f), f"Script exists: {f}")

    # Workflows
    print("\n[GitHub Actions Workflows]")
    for f in [".github/workflows/ci.yml", ".github/workflows/pages.yml",
              ".github/workflows/stale.yml", ".github/workflows/automerge.yml"]:
        check(file_nonempty(f), f"Workflow exists: {f}")

    # Workflow pinning (commit hashes)
    print("\n[Action Pinning]")
    check(file_contains(".github/workflows/ci.yml", "actions/checkout@"),
          "CI: checkout action pinned")
    check(file_contains(".github/workflows/ci.yml", "actions/setup-python@"),
          "CI: setup-python action pinned")
    check(file_contains(".github/workflows/pages.yml", "actions/checkout@"),
          "Pages: checkout action pinned")

    # Cloudflare Worker
    print("\n[Cloudflare Worker]")
    check(file_nonempty("workers/dataset-api.js"), "Worker source exists")
    check(file_nonempty("workers/wrangler.toml"), "Wrangler config exists")
    check(file_contains("workers/dataset-api.js", "/health"), "Worker has health endpoint")
    check(file_contains("workers/dataset-api.js", "/stats"), "Worker has stats endpoint")
    check(file_contains("workers/dataset-api.js", "Access-Control-Allow-Origin"),
          "Worker has CORS headers")

    # Security
    print("\n[Security]")
    check(file_exists(".github/SECURITY.md"), "Security policy exists")
    check(file_exists(".github/dependabot.yml"), "Dependabot config exists")

    # Tests
    print("\n[Tests]")
    check(file_nonempty("tests/test_worker.py"), "Worker tests exist")
    check(file_nonempty("tests/test_end_to_end.py"), "E2E tests exist")

    # Human evaluations
    print("\n[Human Evaluations]")
    for f in ["human-evaluations/copynet-faithfulness.xlsx",
              "human-evaluations/copynet-naturalness.xlsx"]:
        check(file_nonempty(f), f"Evaluation file exists: {f}")

    # Summary
    print("\n" + "=" * 60)
    total = passed + len(errors)
    print(f"Results: {passed}/{total} passed")
    if errors:
        print(f"\nFailed checks ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\nAll checks PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
