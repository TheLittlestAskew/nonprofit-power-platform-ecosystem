# Dataverse Web API Patterns

Reusable **`Xrm.WebApi`** techniques used across the examples. All table and
column names are invented; query values are placeholders.

> **Evidence tier:** Reference / reconstructed. Standard `Xrm.WebApi` usage; no
> production query is reproduced.

## First argument is the table logical name

The first argument to `Xrm.WebApi.retrieveRecord` and
`Xrm.WebApi.retrieveMultipleRecords` is the **table (entity) logical name** —
singular, e.g. `sample_person` — **not** the plural entity-set name. (The plural
entity set appears only in *raw* Web API URLs like `/api/data/v9.2/sample_people`,
which these examples do not build.)

## Prefer Xrm.WebApi over legacy APIs

Use the asynchronous, promise-based `Xrm.WebApi`. Do **not** use synchronous
`XMLHttpRequest` or `async: false` — they block the UI thread and are disallowed
in these examples.

```js
const result = await Xrm.WebApi.retrieveMultipleRecords(entityLogicalName, options);
const rows = result && result.entities ? result.entities : [];
```

## Building OData options

```js
const options =
  `?$select=${columns.join(",")}` +
  `&$filter=${parentColumn} eq ${parentId}` +
  `&$orderby=createdon desc` +
  `&$top=1`;
```

- `$select` to fetch only needed columns.
- `$filter` with an invented column and a normalized id.
- `$orderby ... desc` + `$top=1` to get the most recent record.

## Most-recent-record lookup

```js
async function fetchMostRecent(entityLogicalName, parentColumn, parentId, cols) {
  if (!parentId) return null;
  const options = `?$select=${cols}&$filter=${parentColumn} eq ${parentId}` +
                  `&$orderby=createdon desc&$top=1`;
  const r = await Xrm.WebApi.retrieveMultipleRecords(entityLogicalName, options);
  return r && r.entities && r.entities.length ? r.entities[0] : null;
}
```

## Existence / count checks

For a "does any match exist?" check, select a single column and `$top=1`, then
test `entities.length` — cheaper than retrieving full records.

## Error handling

Wrap calls in `try/catch`. Decide per feature whether to **fail open** (log and
continue, e.g. optional auto-fill) or **fail closed** (block and warn, e.g.
duplicate prevention). Never swallow an error silently where correctness depends
on the result.

## Never in public examples

Real table logical names, real column logical names, real filter values,
environment URLs, or record GUIDs. Everything here is a placeholder.
