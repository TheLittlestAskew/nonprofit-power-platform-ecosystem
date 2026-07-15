# Command Security

Show or enable a command only for users holding a given role.

> **Evidence:** Sanitized reconstruction of a documented production
> command-visibility pattern. Role names are **invented** (`Sample Administrator`,
> `Sample Reviewer`). The private original was not present in this build; nothing
> was read from it.

Example: [`examples/command-security.js`](examples/command-security.js)

## What it demonstrates

- **Role-aware command visibility/enablement** — a command rule calls
  `canSeePrivilegedCommand()`, which checks the current user's roles.
- **Generalized role names** — placeholder names only; real security-role and
  business-unit names are never published.
- **Reading roles defensively** from `Xrm.Utility.getGlobalContext().userSettings.roles`,
  returning an empty set on any failure.

## Key technique

```js
function hasAnyRole(requiredRoleNames) {
  const userRoles = getUserRoleNames(); // Set of lowercased role names
  return requiredRoleNames.some((n) => userRoles.has(String(n).toLowerCase()));
}
```

## ⚠️ Security caveat (important)

**Hiding a command in the UI is a convenience, not an authorization control.**

A determined user can still call the underlying operation directly (via the Web
API, a bookmark, or dev tools). Any action a privileged command performs **must
be enforced server-side** — through Dataverse security roles, table/column
permissions, or plug-in/business logic. Treat this script purely as UX: it
declutters the ribbon for users who cannot perform the action, and it must never
be the only thing standing between a user and a protected operation.

## Not preserved / withheld

The production role names, the real command(s) protected, and the underlying
server-side security configuration are withheld.
