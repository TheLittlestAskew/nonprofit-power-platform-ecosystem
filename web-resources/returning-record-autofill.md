# Returning-Record Auto-Fill

When a new record is linked to a person who has a **prior** related record,
retrieve the most recent one, map selected values forward, and conditionally lock
the copied fields.

> **Evidence:** Sanitized reconstruction of a documented production auto-fill
> pattern. Entity/column names, mapped fields, and locking rules are **invented**.
> The private originals were not present in this build; nothing was read from them.

Example: [`examples/returning-record-autofill.js`](examples/returning-record-autofill.js)

## What it demonstrates

- **Retrieving prior related data** with an async `Xrm.WebApi`
  `retrieveMultipleRecords` call, ordered newest-first, top 1.
- **Mapping prior values** into the new form via `attribute.setValue()`.
- **Conditionally locking** copied fields with `control.setDisabled(true)`.
- **Async Dataverse Web API** usage with `async/await` and explicit error
  handling so a lookup failure never blocks the form.

## Key technique

```js
const options =
  `?$select=${cols}` +
  `&$filter=${CONFIG.personColumn} eq ${personId}` +
  `&$orderby=${CONFIG.createdOnColumn} desc` +
  `&$top=1`;
const result = await Xrm.WebApi.retrieveMultipleRecords(CONFIG.relatedEntitySet, options);
```

The lookup id from `getValue()` is stripped of its `{}` braces before use, and the
handler only runs on **new** records (`getFormType() === 1`) so it never
overwrites an existing record.

## Notes

- Registered as an **OnChange** handler on the person lookup.
- Only fields present on the current form are written; missing fields are skipped
  safely.

## Not preserved / withheld

The production entity and column names, the exact set of mapped fields, and the
real lock conditions are withheld. Query filter values are invented.
