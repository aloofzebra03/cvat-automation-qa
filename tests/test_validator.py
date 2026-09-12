from pathlib import Path

from cvat_qa.validator import validate_cvat_xml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "sample_data"


def test_valid_annotations_have_no_issues():
    report = validate_cvat_xml(DATA / "annotations_valid.xml")

    assert report.task_size == 120
    assert report.tracks_reviewed == 3
    assert len(report.events) == 3
    assert report.errors == []
    assert report.warnings == []


def test_problematic_annotations_are_flagged():
    report = validate_cvat_xml(DATA / "annotations_with_issues.xml")

    codes = {issue.code for issue in report.issues}

    assert "UNKNOWN_LABEL" in codes
    assert "FRAME_OUT_OF_RANGE" in codes
    assert "EMPTY_TRACK" in codes
    assert "SHORT_EVENT" in codes
    assert "POSSIBLE_DUPLICATE" in codes


def test_out_of_range_frame_is_reported_with_frame_number():
    report = validate_cvat_xml(DATA / "annotations_with_issues.xml")

    issue = next(
        issue for issue in report.issues if issue.code == "FRAME_OUT_OF_RANGE"
    )

    assert issue.frame == 130
    assert issue.track_id == "3"


def test_duplicate_check_only_compares_same_label():
    report = validate_cvat_xml(DATA / "annotations_with_issues.xml")

    duplicate_issues = [
        issue for issue in report.issues if issue.code == "POSSIBLE_DUPLICATE"
    ]

    assert duplicate_issues
    assert all(issue.label == "walking" for issue in duplicate_issues)
