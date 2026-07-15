# Duplicate Prevention

Prevent creating more than one related record for the same parent. On save of a
**new** record, check whether any related record already exists for the selected
parent; block and notify if so.

Example: [`examples/duplicate-prevention.js`](examples/duplicate-prevention.js)

## Evidence

- **Directly supported technique:** OnSave guard for create forms only; reading
  the parent lookup; an async `Xrm.WebApi` existence check for the parent;
  `eventArgs.preventDefault()` to defer the save; blocking + notifying on a
  duplicate; re-issuing the save when clean; existing records update normally.
- **Sanitized replacement:** production entity/columns and the FetchXML query →
  invented `sample_case_record` / `sample_related_records` and an OData filter.
- **Intentional hardening (documented deviation):** the production source **failed
  open** — it allowed the save if the duplicate query errored. This public
  reconstruction **fails closed**: on a query error it blocks the save and asks
  the user to retry. This is a deliberate hardening, **not** historical production
  behavior.
- **Modernization:** a re-entrancy guard prevents the re-issued save from looping.
- **Withheld:** the production entity/column names and the exact query.

## What it demonstrates

- **Existence check before save** — is there *any* related record for this
  parent? (One per parent; there is no time window.)
- **Async validation inside OnSave** with a deferred, then re-issued, save.
- **User-facing notification** via `setFormNotification`.

## Key technique

```js
eventArgs.preventDefault();                 // defer the save
const duplicate = await existsForParent(parentId);
if (duplicate) { formContext.ui.setFormNotification(msg, "ERROR", id); return; }
formContext.data.__dupCheckPassed = true;   // re-entrancy guard
formContext.data.save();                    // re-issue once
```

```js
// Intentional deviation from source: fail CLOSED on query error.
catch (err) {
  formContext.ui.setFormNotification("Could not verify duplicates. Please retry.", "ERROR", id);
}
```

## Not preserved / withheld

Production entity/column names, the exact duplicate query, and the production
alert wording are withheld.
