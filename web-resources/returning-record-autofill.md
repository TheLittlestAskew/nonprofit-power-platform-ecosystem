# Returning-Record Auto-Fill

When a person lookup is set, retrieve that person with an expanded prior related
record, copy generalized field groups forward, and — when the prior record is
flagged for review — lock the copied fields and require an override.

Example: [`examples/returning-record-autofill.js`](examples/returning-record-autofill.js)

## Evidence

- **Directly supported technique:** register an OnChange on the lookup
  *attribute*; clear copied fields and reset control state when the lookup is
  cleared; retrieve the selected primary record with selected fields and an
  expanded related record; copy generalized field groups; conditionally lock
  copied fields on a status flag; keep override controls enabled; make the
  override required when review is needed; show/clear a notification; handle
  missing attributes/controls safely.
- **Sanitized replacement:** protected identifier/demographic field groups → a
  generalized `mappedFields` group; the domain rule → a generalized
  `sample_requires_review` flag; override fields → `sample_override` /
  `sample_override_reason`; lookup → `sample_person`.
- **Modernization:** the production original issued a raw `fetch()` against
  `/api/data/v9.2`. This reconstruction uses `Xrm.WebApi.retrieveRecord` with
  invented `$select` / `$expand` options.
- **Withheld:** the protected field groups (identifiers, demographics) and the
  production qualification rule are **not** reproduced.

## What it demonstrates

- **Attribute OnChange** wiring (not control-level) from an OnLoad initializer.
- **Retrieve selected primary + expanded related record** via
  `Xrm.WebApi.retrieveRecord` with `$expand`.
- **Copy field groups**, then **conditionally lock** copied fields and **require
  an override** when the prior record's review flag is set.
- **Reset on clear** — clearing the lookup clears copied values and control state.

## Key technique

```js
const options = `?$select=${select}&$expand=${prior}($select=${reviewFlag})`;
const record = await Xrm.WebApi.retrieveRecord(entityLogicalName, personId, options);
// copy mapped fields, then:
if (record[prior] && record[prior][reviewFlag] === true) {
  mappedFields.forEach((f) => setDisabled(formContext, f, true));
  setRequired(formContext, "sample_override", true);
}
```

## Not preserved / withheld

The protected field groups and the production review/qualification rule are
withheld; a neutral review flag stands in for the domain-specific logic.
