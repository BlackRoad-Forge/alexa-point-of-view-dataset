# Point of View (POV) Message Conversion Dataset

![CI](https://github.com/blackboxprogramming/alexa-point-of-view-dataset/actions/workflows/ci.yml/badge.svg)
![Pages](https://github.com/blackboxprogramming/alexa-point-of-view-dataset/actions/workflows/pages.yml/badge.svg)

**Status: Production** · **Version: 1.0** · **Pairs: 46,562**

---

Virtual assistants (VAs) tend to be literal in their delivery of messages. To make incremental improvement towards a virtual assistant that you may speak to conversationally and naturally, we have provided the data necessary to build AI systems that can convert the point of view of messages spoken to virtual assistants.

If a sender asks the virtual assistant to relay a message to a receiver, the virtual assistant converts the message to VA's perspective and composes a conversational relay message:

- **Sender (isabelle):** ask nick if he wants anything from trader joe's
- **VA to receiver (nick):** hi nick, isabelle wants to know if you want anything from trader joe's?

## Table of Contents

1. [Quick Start](#quick-start)
2. [Data](#data)
3. [Surveys](#surveys)
4. [Human Evaluation](#human-evaluation)
5. [API](#api)
6. [Development](#development)
7. [Citation](#citation)
8. [Acknowledgements](#acknowledgements)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/blackboxprogramming/alexa-point-of-view-dataset.git
cd alexa-point-of-view-dataset

# Validate dataset integrity
python3 scripts/validate_data.py

# Load the data in Python
import csv
with open("data/train.tsv") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        print(f"Input:  {row['input']}")
        print(f"Output: {row['output']}")
        break
```

**Expected output:**
```
Input:  ask @CN@ ,how come i can't see her?
Output: hi @CN@ , @SCN@ requests to know why she couldn't see her
```

## Data

The dataset contains parallel corpus of input (`input` column) message and POV converted messages (`output` column). An example of a pair is:

```
tell @CN@ that i'll be late [\t] hi @CN@, @SCN@ would like you to know that they'll be late.
```

The input and POV-converted output pair is tab separated. `@CN@` is a placeholder for the contact name (receiver) and `@SCN@` is a placeholder for source contact name (sender).

| Split | Rows   | File          |
| ----- | ------ | ------------- |
| Total | 46,562 | `data/total.tsv` |
| Train | 32,593 | `data/train.tsv` |
| Dev   | 6,984  | `data/dev.tsv`   |
| Test  | 6,985  | `data/test.tsv`  |

### Data Integrity

Run the validation script to verify dataset integrity:

```bash
python3 scripts/validate_data.py
```

This checks: file existence, UTF-8 encoding, column format, row counts, and placeholder tags.

## Surveys

This release contains the surveys used to collect our data. Our primary source of data was Amazon-internal associates and crowdsourcing on Amazon Mechanical Turk. The surveys are in HTML format compatible for MTurk.

| Type of Input | Description | Example | Survey File |
| ------------- | ----------- | ------- | ----------- |
| Statement | Statement from sender to receiver | tell priya that i'll be late | `surveys/stmt.html` |
| AskYN | Yes/no question | ask priya if they'll be late | `surveys/askyn.html` |
| AskIN | Vague question *about* a subject | ask priya about the apartment lease | `surveys/askin.html` |
| AskWH | WH-interrogative question | ask priya what time is the meeting | `surveys/askwh.html` |
| Request | Request for action | ask priya to please get back to me | `surveys/req.html` |
| Do | Auxiliary verb *do* questions | ask priya did she like her present? | `surveys/do.html` |

Validate surveys:
```bash
python3 scripts/check_surveys.py
```

## Human Evaluation

We evaluated output of rule-based model, T5, and CopyNet trained on this corpus. For each output, 3 associates evaluated faithfulness (binary) and naturalness (1-4 scale, converted to natural/unnatural).

| Model | Annotator Agreement (Faithfulness) | Annotator Agreement (Naturalness) | Faithfulness Accuracy | Naturalness Accuracy |
| --- | --- | --- | --- | --- |
| CopyNet | 0.94 | 0.89 | 0.94 | 0.97 |
| T5 | 0.86 | 0.88 | 0.98 | 0.98 |
| Rule-based | 0.72 | 0.71 | 0.85 | 0.76 |

CopyNet's human evaluation results are included in `human-evaluations/`.

## API

A Cloudflare Worker provides a lightweight REST API for dataset metadata:

| Endpoint | Description |
| -------- | ----------- |
| `GET /` | API info and available endpoints |
| `GET /stats` | Dataset statistics and metadata |
| `GET /sample?n=5` | Sample data rows |
| `GET /health` | Health check |

Deploy the worker:
```bash
cd workers
npx wrangler deploy
```

## Development

### Project Structure

```
├── data/                    # TSV dataset files
│   ├── total.tsv            # Complete dataset (46,562 pairs)
│   ├── train.tsv            # Training split (32,593 pairs)
│   ├── dev.tsv              # Development split (6,984 pairs)
│   └── test.tsv             # Test split (6,985 pairs)
├── surveys/                 # MTurk survey HTML templates
├── human-evaluations/       # CopyNet evaluation Excel files
├── scripts/                 # Validation and build scripts
│   ├── validate_data.py     # Dataset integrity checker
│   ├── check_surveys.py     # Survey file validator
│   └── build_pages.py       # GitHub Pages site builder
├── workers/                 # Cloudflare Worker API
│   ├── dataset-api.js       # Worker source
│   └── wrangler.toml        # Wrangler configuration
├── tests/                   # End-to-end tests
│   ├── test_end_to_end.py   # Full repository validation
│   └── test_worker.py       # Worker smoke tests
├── .github/
│   ├── workflows/
│   │   ├── ci.yml           # CI: data validation, linting, security
│   │   ├── pages.yml        # Deploy documentation to GitHub Pages
│   │   ├── stale.yml        # Auto-close stale issues/PRs
│   │   └── automerge.yml    # Auto-merge Dependabot PRs
│   ├── dependabot.yml       # Automated dependency updates
│   ├── SECURITY.md          # Security policy
│   └── ISSUE_TEMPLATE/      # Issue templates
├── README.md
├── LICENSE
├── NOTICE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── version
```

### CI/CD Workflows

All GitHub Actions are pinned to commit hashes for supply-chain security:

| Workflow | Trigger | Purpose |
| -------- | ------- | ------- |
| `ci.yml` | Push/PR to main, weekly | Data validation, survey linting, security scan |
| `pages.yml` | Push to main | Build and deploy GitHub Pages documentation |
| `stale.yml` | Weekly | Auto-close stale issues and PRs |
| `automerge.yml` | PR events | Auto-merge Dependabot dependency updates |

### Running Tests

```bash
# Validate dataset integrity
python3 scripts/validate_data.py

# Validate survey files
python3 scripts/check_surveys.py

# Run worker smoke tests
python3 tests/test_worker.py

# Run full end-to-end validation
python3 tests/test_end_to_end.py

# Build GitHub Pages site locally
python3 scripts/build_pages.py
```

### Security

- All GitHub Actions pinned to commit SHAs (not tags)
- Dependabot monitors action versions weekly
- Auto-merge enabled for Dependabot PRs
- Security scanning in CI pipeline
- Report vulnerabilities per `.github/SECURITY.md`

## Citation

```bibtex
@inproceedings{iglee2020,
  author={Isabelle G. Lee and Vera Zu and Sai Srujana Buddi and Dennis Liang and Purva Kulkarni and Jack Fitzgerald},
  title={{Converting the Point of View of Messages Spoken to Virtual Assistants}},
  year=2020,
  booktitle={Findings of EMNLP 2020}
}
```

Paper: [https://arxiv.org/abs/2010.02600](https://arxiv.org/abs/2010.02600)

## Acknowledgements

We'd like to thank Steven Spielberg P. for coordinating our efforts and for early contribution, and we'd like to thank Adrien Carre and Minh Nguyen on coordinating with associates for the dataset and human evaluation of model output.

## License

See [LICENSE](LICENSE) for details.
