# Client API Patterns

Reusable model-driven **Client API** techniques used across the examples. All
names are invented.

> **Evidence tier:** Reference / reconstructed. Standard `Xrm` Client API usage;
> no production detail.

## formContext, not Xrm.Page

Always derive `formContext` from the execution context and pass it explicitly:

```js
function onLoad(executionContext) {
  const formContext = executionContext.getFormContext();
  // ... pass formContext into helpers; never rely on the deprecated global
}
```

## Form type

```js
const formType = formContext.ui.getFormType(); // 1 = create, 2 = update
```

Guarding on form type keeps create-only logic (routing, auto-fill) from touching
existing records.

## Attributes and controls

```js
const attr = formContext.getAttribute("sample_field");
const value = attr ? attr.getValue() : null;      // explicit null check
attr && attr.setValue(newValue);

const control = formContext.getControl("sample_field");
control && control.setDisabled(true);              // UX only, not security
```

Reading through short-circuit checks means a field that is absent from the
current form is skipped instead of throwing.

## Lookups

```js
const value = attr.getValue();
const id = value && value.length ? value[0].id.replace(/[{}]/g, "") : null;
```

Lookup ids arrive wrapped in braces; strip them before use in a Web API filter.

## Notifications

```js
formContext.ui.setFormNotification(message, "WARNING", "unique_notice_id");
formContext.ui.clearFormNotification("unique_notice_id");
```

Use a stable notification id so the same message can be cleared later. Keep public
example wording generic — never reproduce production notification text.

## OnSave deferral

```js
const eventArgs = executionContext.getEventArgs();
eventArgs.preventDefault(); // defer the platform save for async validation
```

See [`async-form-events.md`](async-form-events.md) for the re-entrancy pattern
that safely re-issues a deferred save.
