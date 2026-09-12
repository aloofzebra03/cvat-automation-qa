from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    track_id: str | None = None
    label: str | None = None
    frame: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Event:
    track_id: str
    label: str
    start_frame: int
    end_frame: int

    @property
    def duration(self) -> int:
        return self.end_frame - self.start_frame + 1


@dataclass
class QAReport:
    task_size: int | None
    defined_labels: list[str]
    tracks_reviewed: int
    events: list[Event]
    issues: list[Issue]

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "ERROR"]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "WARNING"]

    def to_dict(self) -> dict:
        return {
            "task_size": self.task_size,
            "defined_labels": self.defined_labels,
            "tracks_reviewed": self.tracks_reviewed,
            "events": [asdict(event) for event in self.events],
            "summary": {
                "events": len(self.events),
                "errors": len(self.errors),
                "warnings": len(self.warnings),
            },
            "issues": [issue.to_dict() for issue in self.issues],
        }


def _safe_int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _defined_labels(root: ET.Element) -> list[str]:
    names: list[str] = []
    for node in root.findall("./meta/task/labels/label/name"):
        if node.text and node.text.strip():
            names.append(node.text.strip())
    return names


def _task_size(root: ET.Element) -> int | None:
    size = root.findtext("./meta/task/size")
    parsed = _safe_int(size)
    if parsed is None or parsed <= 0:
        return None
    return parsed


def _visible_frames(track: ET.Element) -> list[int]:
    frames: list[int] = []
    for shape in list(track):
        if "frame" not in shape.attrib:
            continue
        frame = _safe_int(shape.attrib.get("frame"))
        if frame is None:
            continue
        outside = shape.attrib.get("outside", "0")
        if outside != "1":
            frames.append(frame)
    return sorted(frames)


def _event_overlap_ratio(first: Event, second: Event) -> float:
    overlap_start = max(first.start_frame, second.start_frame)
    overlap_end = min(first.end_frame, second.end_frame)
    if overlap_end < overlap_start:
        return 0.0
    overlap = overlap_end - overlap_start + 1
    shorter = min(first.duration, second.duration)
    return overlap / shorter if shorter else 0.0


def validate_cvat_xml(
    xml_path: str | Path,
    *,
    min_event_duration: int = 2,
    duplicate_overlap_threshold: float = 0.8,
) -> QAReport:
    path = Path(xml_path)
    root = ET.parse(path).getroot()

    issues: list[Issue] = []
    labels = _defined_labels(root)
    size = _task_size(root)

    if size is None:
        issues.append(
            Issue(
                severity="ERROR",
                code="INVALID_TASK_SIZE",
                message="Task size is missing, non-numeric, or not greater than zero.",
            )
        )

    if not labels:
        issues.append(
            Issue(
                severity="ERROR",
                code="NO_LABELS",
                message="No labels are defined in task metadata.",
            )
        )

    tracks = root.findall("./track")
    if not tracks:
        issues.append(
            Issue(
                severity="WARNING",
                code="NO_TRACKS",
                message="No annotation tracks were found.",
            )
        )

    events: list[Event] = []

    for track in tracks:
        track_id = track.attrib.get("id", "?")
        label = track.attrib.get("label", "").strip()

        if label not in labels:
            issues.append(
                Issue(
                    severity="ERROR",
                    code="UNKNOWN_LABEL",
                    message=f"Track uses undefined label '{label}'.",
                    track_id=track_id,
                    label=label or None,
                )
            )

        frames = _visible_frames(track)
        if not frames:
            issues.append(
                Issue(
                    severity="ERROR",
                    code="EMPTY_TRACK",
                    message="Track contains no visible annotation frames.",
                    track_id=track_id,
                    label=label or None,
                )
            )
            continue

        if size is not None:
            for frame in frames:
                if frame < 0 or frame >= size:
                    issues.append(
                        Issue(
                            severity="ERROR",
                            code="FRAME_OUT_OF_RANGE",
                            message=f"Frame {frame} is outside valid range 0..{size - 1}.",
                            track_id=track_id,
                            label=label or None,
                            frame=frame,
                        )
                    )

        event = Event(
            track_id=track_id,
            label=label,
            start_frame=min(frames),
            end_frame=max(frames),
        )
        events.append(event)

        if event.duration < min_event_duration:
            issues.append(
                Issue(
                    severity="WARNING",
                    code="SHORT_EVENT",
                    message=(
                        f"Event duration is {event.duration} frame(s); "
                        f"review against annotation guidelines."
                    ),
                    track_id=track_id,
                    label=label or None,
                    frame=event.start_frame,
                )
            )

    for index, first in enumerate(events):
        for second in events[index + 1 :]:
            if first.label != second.label:
                continue
            ratio = _event_overlap_ratio(first, second)
            if ratio >= duplicate_overlap_threshold:
                issues.append(
                    Issue(
                        severity="WARNING",
                        code="POSSIBLE_DUPLICATE",
                        message=(
                            f"Tracks {first.track_id} and {second.track_id} overlap "
                            f"by {ratio:.0%} of the shorter event."
                        ),
                        track_id=second.track_id,
                        label=second.label,
                    )
                )

    return QAReport(
        task_size=size,
        defined_labels=labels,
        tracks_reviewed=len(tracks),
        events=events,
        issues=issues,
    )


def format_text_report(report: QAReport) -> str:
    lines = [
        f"Task size: {report.task_size if report.task_size is not None else 'INVALID'} frames",
        f"Tracks reviewed: {report.tracks_reviewed}",
        f"Visible events: {len(report.events)}",
        f"Errors: {len(report.errors)}",
        f"Warnings: {len(report.warnings)}",
        "",
    ]

    for issue in report.issues:
        context: list[str] = []
        if issue.track_id is not None:
            context.append(f"track={issue.track_id}")
        if issue.label is not None:
            context.append(f"label={issue.label}")
        if issue.frame is not None:
            context.append(f"frame={issue.frame}")
        suffix = " " + " ".join(context) if context else ""
        lines.append(
            f"[{issue.severity}] {issue.code}{suffix}: {issue.message}"
        )

    if not report.issues:
        lines.append("PASS: No QA issues detected.")

    return "\n".join(lines)
