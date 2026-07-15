# Async Form Events

Patterns for doing asynchronous work inside synchronous-looking form events
(OnSave, OnChange) without blocking the UI or corrupting state.

> **Evidence tier:** Reference / reconstructed. Standard model-driven async
> techniques; no production detail.

## Deferring a save for async validation

The platform's OnSave is synchronous, but validation often needs an async query.
Defer the save, run the check, then re-issue it:

```js
async function onSave(executionContext) {
  const formContext = executionContext.getFormContext();
  const eventArgs = executionContext.getEventArgs();

  // Re-entrancy guard: a re-issued save skips the check exactly once.
  if (formContext.data.__checkPassed) {
    formContext.data.__checkPassed = false;
    return;
  }

  eventArgs.preventDefault();               // defer
  const problem = await runAsyncCheck();
  if (problem) {
    formContext.ui.setFormNotification(/* ... */);
    return;                                 // stays cancelled
  }
  formContext.data.__checkPassed = true;    // mark validated
  formContext.data.save();                  // re-issue once
}
```

The re-entrancy flag is essential: without it, calling `save()` inside OnSave
would re-enter the handler and loop forever.

## Bounded retries / polling

When waiting for an out-of-band process (a cloud flow), poll a bounded number of
times with an `await`-able delay — never a busy loop or unbounded `while`:

```js
function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function pollBounded(check, maxAttempts, delayMs) {
  for (let i = 0; i < maxAttempts; i += 1) {
    await wait(delayMs);
    if (await check()) return true;
  }
  return false; // timeout
}
```

## Fail-open vs. fail-closed

Choose deliberately:

- **Fail open** — optional enhancements (auto-fill): on error, log and let the
  user continue.
- **Fail closed** — correctness guards (duplicate prevention): on error, block and
  warn rather than risk a bad write.

## Avoiding shared mutable state

Prefer passing `formContext` and ids as parameters. Where a transient flag is
unavoidable (the re-entrancy marker above), scope it to `formContext.data` and
reset it immediately, rather than using a module-level mutable global.
