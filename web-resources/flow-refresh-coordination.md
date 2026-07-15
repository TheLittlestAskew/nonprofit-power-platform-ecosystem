# Cloud-Flow Refresh Coordination

A command triggers a Power Automate cloud flow that creates a related record
asynchronously. The form polls (bounded) for that record to appear, then
refreshes a subgrid or the form.

> **Evidence:** Sanitized reconstruction of a documented production
> flow-coordination pattern. Entity/column/subgrid names and timings are
> **invented**. The private original was not present in this build; nothing was
> read from it.

Example: [`examples/flow-refresh-coordination.js`](examples/flow-refresh-coordination.js)

## What it demonstrates

- **Polling for a flow-created record** by comparing a related-record count
  against a baseline captured before the flow ran.
- **Bounded retry logic** — at most `maxAttempts` polls, `delayMs` apart, using an
  `await`-able `wait()` wrapper around `setTimeout` (no busy loop, no unbounded
  spin).
- **Refreshing the form or subgrid** via `grid.refresh()`, falling back to
  `formContext.data.refresh(false)`.
- **Timeout and failure handling** — a timeout shows a "refresh manually"
  message; a query error fails closed rather than spinning.

## Key technique

```js
for (let attempt = 0; attempt < CONFIG.maxAttempts; attempt += 1) {
  await wait(CONFIG.delayMs);
  const current = await countRelated(parentId);
  if (current > baseline) return true; // appeared
}
return false; // bounded timeout
```

## Notes

- The cloud flow itself is triggered by the platform command; this script
  coordinates the **client-side** wait-and-refresh only.
- An INFO notification communicates progress and is cleared when polling ends.

## Not preserved / withheld

The production entity/column/subgrid names, the real poll interval and attempt
count, and the exact notification wording are withheld.
