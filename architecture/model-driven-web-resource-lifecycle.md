# Model-Driven Web Resource Lifecycle

Where client-side web resources fit in a model-driven Power Apps form's lifecycle,
and how the six documented patterns map onto its events.

> **Evidence tier:** Reconstructed. A generalized rendering of the standard
> model-driven form event model; all pattern names are invented reconstructions.
> No production script, schema, or identifier is shown.

## Form event lifecycle

```mermaid
flowchart TD
    LOAD["Form OnLoad"]
    ROUTE["Form routing\n(new vs. existing -> intake/main)"]
    CHANGE["Attribute OnChange"]
    AUTOFILL["Returning-record auto-fill\n(async Web API)"]
    DATETIME["Date/time auto-populate\n(compute end, overnight)"]
    SAVE["Form OnSave"]
    DUP["Duplicate prevention\n(defer, async check, re-issue)"]
    VALIDATE["Date/time validation\n(end after start)"]
    COMMAND["Ribbon command rule"]
    SECURITY["Command security\n(role-aware visibility)"]
    FLOW["Command triggers cloud flow"]
    REFRESH["Flow refresh coordination\n(bounded poll, refresh)"]

    LOAD --> ROUTE
    LOAD --> COMMAND
    COMMAND --> SECURITY
    ROUTE --> CHANGE
    CHANGE --> AUTOFILL
    CHANGE --> DATETIME
    AUTOFILL --> SAVE
    DATETIME --> SAVE
    SAVE --> DUP
    SAVE --> VALIDATE
    COMMAND --> FLOW --> REFRESH --> CHANGE
```

## Pattern-to-event map

| Event | Pattern | Async? |
|---|---|---|
| OnLoad | Form routing | No |
| OnChange (lookup) | Returning-record auto-fill | Yes (Web API) |
| OnChange (start/duration) | Date/time auto-populate | No |
| OnSave | Duplicate prevention | Yes (deferred save) |
| OnSave | Date/time validation | No |
| Command rule | Command security | No |
| Post-command | Cloud-flow refresh coordination | Yes (bounded poll) |

## Design rules carried across patterns

- Derive `formContext` from the execution context; pass it explicitly.
- Guard on form type so create-only logic never touches existing records.
- Prefer `Xrm.WebApi` (async) over legacy synchronous calls.
- Defer saves for async validation with a re-entrancy guard.
- Bound every retry/poll; never spin.
- Treat UI command-hiding as UX, **not** authorization — enforce server-side.

Full detail:
[`../web-resources/README.md`](../web-resources/README.md).
