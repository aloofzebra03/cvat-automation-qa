from __future__ import annotations

import argparse
import json
from pathlib import Path

from .validator import format_text_report, validate_cvat_xml


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate CVAT XML exports and generate annotation QA findings."
    )
    parser.add_argument("xml_file", type=Path, help="Path to CVAT XML export")
    parser.add_argument(
        "--json",
        dest="json_path",
        type=Path,
        help="Optional path for a JSON QA report",
    )
    parser.add_argument(
        "--min-duration",
        type=int,
        default=2,
        help="Warn when an event is shorter than this many frames (default: 2)",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = validate_cvat_xml(
        args.xml_file,
        min_event_duration=args.min_duration,
    )

    print(format_text_report(report))

    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(
            json.dumps(report.to_dict(), indent=2),
            encoding="utf-8",
        )
        print(f"\nJSON report written to: {args.json_path}")

    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
