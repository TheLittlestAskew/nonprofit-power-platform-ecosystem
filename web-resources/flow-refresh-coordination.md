# Cloud-Flow Refresh Coordination

On a new record's load, wait (bounded) for the record to get an id, then poll by
refreshing form data and checking two related lookup fields that a Power Automate
cloud flow creates out-of-band. Stop when both appear and do one final refresh.

Example: [`examples/flow-refresh-coordination.js`](examples/flow-refresh-coordination.js)

## Evidence

- **Directly supported technique (primary):** run only for a new record; wait,
  with a bounded timeout, until the record receives an id; poll by refreshing form
  data; after each refresh check two related lookup fields; stop when both exist;
  perform one final refresh; stop cleanly after the maximum attempts; include
  error and timeout handling.
- **Sanitized replacement:** production entity/lookup names → invented
  `sample_related_record_a` / `sample_related_record_b`.
- **Alternative (not source-backed):** a Web API baseline-count poll is retained
  only as a clearly labeled alternative; it does **not** replace the primary
  form-data-refresh pattern.
- **Withheld:** the production entity/lookup names.

## What it demonstrates

- **Bounded wait for the record id** after the initial save.
- **Poll via `formContext.data.refresh(false)`**, checking two lookups per pass.
- **Final refresh** once both related records are present.
- **Bounded** loops with error/timeout handling — never an unbounded spin.

## Key technique

```js
// Poll by refreshing form data and checking both lookups (bounded).
for (let i = 0; i < CONFIG.maxPollAttempts; i += 1) {
  await wait(CONFIG.pollIntervalMs);
  await formContext.data.refresh(false);
  if (hasValue(formContext, CONFIG.lookupA) && hasValue(formContext, CONFIG.lookupB)) return true;
}
return false; // bounded timeout
```

## Not preserved / withheld

The production entity and lookup names are withheld; the poll timings shown are
invented defaults.
