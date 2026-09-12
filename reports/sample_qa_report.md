# Sample Annotation QA Report

**Dataset:** Synthetic action demo  
**Format:** CVAT XML  
**Task size:** 120 frames

## Summary

| Metric | Value |
|---|---:|
| Tracks reviewed | 6 |
| Errors | 3 |
| Warnings | 2+ |
| Overall status | FAIL — correction required |

## Findings

### Error — Unknown label

Track 4 uses `running`, but that label is not defined in task metadata.

**Action:** Relabel according to the project taxonomy or update the approved label set.

### Error — Out-of-range frame

Track 3 contains frame 130 while the task contains only 120 frames (valid range 0–119).

**Action:** Correct the frame boundary and re-export.

### Error — Empty visible track

Track 5 contains only an `outside=1` shape.

**Action:** Remove the empty track or restore the intended visible annotation.

### Warning — Short event

Track 2 contains a one-frame `jump` event.

**Action:** Manually confirm whether a one-frame event is valid under annotation guidelines.

### Warning — Possible duplicate

Tracks 0 and 1 are both labeled `walking` and substantially overlap.

**Action:** Review for duplicate annotation or confirm that two distinct subjects/events are intended.

## Retest procedure

1. Correct findings in CVAT.
2. Export XML.
3. Rerun the validator.
4. Confirm zero blocking errors.
5. Manually review remaining warnings.
