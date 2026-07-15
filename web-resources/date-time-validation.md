# Date/Time Validation

Auto-populate an end time from a start time and duration, handle an event that
crosses midnight, validate before save, and clean up transient form state.

> **Evidence:** Sanitized reconstruction of a documented production scheduling
> pattern. Column names, the default duration, and messages are **invented**. The
> private original was not present in this build; nothing was read from it.

Example: [`examples/date-time-validation.js`](examples/date-time-validation.js)

## What it demonstrates

- **Automatic end-time calculation** from start + duration (in minutes).
- **Overnight-event handling** — because the end is computed with date
  arithmetic (`start.getTime() + minutes * 60000`), an end past midnight rolls to
  the next day naturally, with no special casing.
- **Validation before save** — OnSave cancels via `preventDefault()` when the end
  is not strictly after the start.
- **Cleanup of transient state** — an auto-fill marker is cleared so it does not
  persist between edits.

## Key technique

```js
function computeEnd(start, durationMinutes) {
  return new Date(start.getTime() + durationMinutes * 60 * 1000);
}
// OnSave: an overnight end (next day) is valid; end <= start is not.
if (start && end && end.getTime() <= start.getTime()) {
  eventArgs.preventDefault();
}
```

## Notes

- OnChange handler on start-time or duration recomputes the end.
- Values are read defensively (`instanceof Date`, finite-number checks) with a
  sensible default duration.

## Not preserved / withheld

The production column names, the real default duration, and the exact validation
messages are withheld.
