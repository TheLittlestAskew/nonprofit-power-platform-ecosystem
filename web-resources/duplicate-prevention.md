# Duplicate Prevention

Before saving a new related record, check whether an equivalent record already
exists for the same parent within a time window. If so, cancel the save and
notify the user.

> **Evidence:** Sanitized reconstruction of a documented production duplicate-check
> pattern. Entity/column names, the window, and messages are **invented**. The
> private original was not present in this build; nothing was read from it.

Example: [`examples/duplicate-prevention.js`](examples/duplicate-prevention.js)

## What it demonstrates

- **Checking for an existing related record before save** via an async
  `Xrm.WebApi` query filtered by parent and a date window.
- **Async validation inside OnSave** using `eventArgs.preventDefault()` to defer
  the platform save while the query runs.
- **Cancelling the save safely** and re-issuing it exactly once when the check
  passes (a re-entrancy flag prevents an infinite save loop).
- **User-facing notification** through `formContext.ui.setFormNotification()`.

## Key technique

```js
eventArgs.preventDefault();               // defer the save
const duplicate = await existsDuplicate(parentId, date);
if (duplicate) {
  formContext.ui.setFormNotification(msg, "WARNING", CONFIG.notificationId);
  return;                                 // save stays cancelled
}
formContext.data.__dupCheckPassed = true; // mark validated
formContext.data.save();                  // re-issue once
```

On a query error the handler **fails closed** — it surfaces an error and does not
silently allow a possible duplicate.

## Not preserved / withheld

The production entity and column names, the real matching window, and the exact
notification wording are withheld.
