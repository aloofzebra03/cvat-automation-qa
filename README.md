# CVAT Annotation Quality Assurance

A portfolio project for validating **CVAT video annotation exports** and generating reproducible QA reports for human-data workflows.

The project focuses on annotation quality dimensions commonly used in AI-training pipelines:

- Label validity
- Frame-boundary accuracy
- Out-of-range annotations
- Duplicate/overlapping events
- Empty tracks
- Event-duration checks
- Annotation consistency
- Dataset-level summary statistics

It includes intentionally valid and invalid sample CVAT XML exports so the QA logic can be demonstrated without sharing proprietary data.

## What this project demonstrates

- Human-data / annotation quality evaluation
- CVAT XML parsing
- Structured QA rules
- Frame-accurate event-boundary validation
- Reproducible issue reports
- Severity classification
- Automated regression tests for validation logic
- Clear annotation-review guidelines

## Project structure

```text
cvat-annotation-qa/
├── cvat_qa/
│   ├── __init__.py
│   ├── cli.py
│   └── validator.py
├── sample_data/
│   ├── annotations_valid.xml
│   └── annotations_with_issues.xml
├── tests/
│   └── test_validator.py
├── docs/
│   └── annotation_qa_checklist.md
├── reports/
│   └── sample_qa_report.md
├── .github/workflows/
│   └── tests.yml
├── requirements.txt
└── README.md
```

## Supported QA checks

The validator inspects CVAT XML and reports:

| Rule | Severity |
|---|---|
| Unknown label | Error |
| Frame outside task range | Error |
| Track with no visible annotation | Error |
| Duplicate / highly overlapping same-label events | Warning |
| Very short event | Warning |
| Invalid or missing task size | Error |
| No labels defined | Error |
| No tracks found | Warning |

## Run the validator

No third-party runtime dependency is required.

```bash
python -m cvat_qa.cli sample_data/annotations_valid.xml
```

Validate a deliberately problematic export:

```bash
python -m cvat_qa.cli sample_data/annotations_with_issues.xml
```

Write a JSON report:

```bash
python -m cvat_qa.cli sample_data/annotations_with_issues.xml --json reports/issues.json
```

## Run tests

```bash
pip install -r requirements.txt
pytest -v
```

## Example output

```text
Task size: 120 frames
Tracks reviewed: 5
Visible events: 5
Errors: 3
Warnings: 2

[ERROR] UNKNOWN_LABEL track=4 label=running
[ERROR] FRAME_OUT_OF_RANGE track=3 frame=130
[WARNING] SHORT_EVENT track=2 label=jump duration=1
```

## QA workflow

1. Export annotations from CVAT as XML.
2. Run the validator.
3. Review errors first.
4. Inspect warnings for false positives or guideline exceptions.
5. Correct annotations in CVAT.
6. Re-export and rerun the validator.
7. Record the final pass/fail status.

## Resume-ready description

> Reviewed video annotation quality with frame-level checks for missed events, timestamp accuracy, boundary precision, label consistency, and guideline adherence. Built Python-based validation utilities for CVAT XML exports to flag out-of-range frames, invalid labels, empty tracks, duplicate events, and suspiciously short annotations.

## Privacy / data note

The XML files in `sample_data/` are synthetic and contain no proprietary or personal data.

## License

MIT
