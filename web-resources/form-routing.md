# Form Routing

Route a record to an **intake** form (new record) or the **main** form (existing
record) on load.

> **Evidence:** Sanitized reconstruction of a documented production form-routing
> pattern. Form identifiers, the returning-record flag, and routing rules are
> **invented**. The private original was not present in this build; nothing was
> read from it.

Example: [`examples/form-routing.js`](examples/form-routing.js)

## What it demonstrates

- **New vs. existing detection** via `formContext.ui.getFormType()`
  (`1` = create, `2` = update).
- **Routing** to an invented `SAMPLE_INTAKE_FORM_ID` or `SAMPLE_MAIN_FORM_ID`
  using `formContext.ui.formSelector`.
- **Generalized form identifiers** — placeholder tokens, never production GUIDs.
- **Safe fallback** — if the target form is unavailable to the user, or matches
  the current form, the handler does nothing and leaves the default form in
  place (no reload loop).

## Key technique

```js
const formType = formContext.ui.getFormType(); // 1 = new, 2 = existing
if (formType === 1) {
  routeTo(formContext, CONFIG.intakeFormId);
}
```

`routeTo()` compares the current form id to the target and only calls
`item.navigate()` when they differ — avoiding an infinite navigate/reload cycle.

## Notes

- Registered as an **OnLoad** handler on the table's form(s).
- `formContext` is derived from the execution context and passed explicitly to
  helpers, never read from a global.

## Not preserved / withheld

The production form names and GUIDs, the real returning-record indicator column,
and the exact routing conditions are withheld. Only the generalized technique is
shown.
