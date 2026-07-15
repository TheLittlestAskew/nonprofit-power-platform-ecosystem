# Form Routing

Keep records on the correct form: a **new** record opened on the main form is
redirected to the intake form; a new record already on the intake form stays;
**existing** records are never auto-rerouted.

Example: [`examples/form-routing.js`](examples/form-routing.js)

## Evidence

- **Directly supported technique:** two form-scoped OnLoad handlers; detecting
  create vs. existing with `getFormType()`; identifying the current form via
  `formSelector.getCurrentItem()`; redirecting a new record on the main form to
  the intake form with `Xrm.Navigation.navigateTo`.
- **Sanitized replacement:** production form GUIDs → `SAMPLE_INTAKE_FORM_ID` /
  `SAMPLE_MAIN_FORM_ID`; production entity name → `sample_person`.
- **Withheld:** the two production form GUIDs and the real entity name.

## What it demonstrates

- **New vs. existing detection** via `formContext.ui.getFormType()`
  (`1` = create).
- **Form-scoped handlers** — one registered on the intake form (stay-only) and
  one on the main form (redirect new records only).
- **Redirect** with `Xrm.Navigation.navigateTo` using invented form/entity
  tokens.
- **No auto-reroute of existing records**, and a **safe fallback**: if a handler
  runs on an unexpected form or navigation fails, the user simply stays put.

## Key technique

```js
// Main-form handler: only a NEW record is redirected to the intake form.
if (formContext.ui.getFormType() !== 1) return; // existing record stays
Xrm.Navigation.navigateTo(
  { pageType: "entityrecord", entityName: CONFIG.entityName, formId: CONFIG.intakeFormId },
  { target: 1, position: 1 }
);
```

The intake-form handler performs no navigation — a new record belongs there, and
an existing record opened there is treated as intentional.

## Not preserved / withheld

The production form GUIDs and entity name are withheld; only the generalized
two-handler routing technique is shown.
