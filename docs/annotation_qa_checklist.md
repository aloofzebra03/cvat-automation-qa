# Annotation QA Checklist

Use this checklist when reviewing action annotations in CVAT.

## 1. Label correctness

- Is the selected label present in the project guidelines?
- Does the visible action actually match the label?
- Are visually similar classes being confused?
- Is the same label used consistently across annotators?

## 2. Start boundary

- Does the annotation begin on the first frame where the action is observable?
- Is the boundary too early because of preparation/motion before the actual action?
- Is the boundary too late because the first valid frames were missed?

## 3. End boundary

- Does the annotation include the final frame where the action is still observable?
- Does it continue after the action has ended?
- Is the event truncated?

## 4. Missed events

- Review the full clip, not only annotated regions.
- Check transitions between events.
- Check short-duration actions that may be easy to miss.

## 5. Duplicate / overlap review

- Are two tracks describing the same event?
- Is overlap allowed by the project guidelines?
- Are simultaneous different actions valid or mutually exclusive?

## 6. Frame-range validity

- No annotation should use a negative frame.
- No annotation should exceed `task_size - 1`.
- Empty tracks should be removed or corrected.

## 7. Consistency

- Apply the same decision rule across the dataset.
- Follow guideline exceptions consistently.
- Record ambiguous cases for adjudication.

## 8. Final QA

Before marking a task complete:

- Run automated validation.
- Resolve all errors.
- Review warnings.
- Spot-check event boundaries.
- Confirm no obvious missed events.
- Re-export and validate again.
