# Command Security

Gate a command by comparing the current user's **security-role IDs** against
invented role-ID tokens. Supports single-role and multiple-role checks.

Example: [`examples/command-security.js`](examples/command-security.js)

## Evidence

- **Directly supported technique (primary):** read
  `Xrm.Utility.getGlobalContext().userSettings.securityRoles` (an array of role
  IDs) and compare against configured role IDs; support both a single-role check
  and a multiple-role check.
- **Sanitized replacement:** the production role GUID → invented
  `SAMPLE_ADMIN_ROLE_ID` / `SAMPLE_REVIEWER_ROLE_ID`.
- **Alternative (modern) approach:** a role-**name** comparison via
  `userSettings.roles` is documented as an alternative; the primary example uses
  the role-**ID** technique to mirror the source.
- **Withheld:** the production security-role GUID(s).

## What it demonstrates

- **Role-ID membership** checks against `userSettings.securityRoles`.
- **Single-role** (`hasRole`) and **multiple-role** (`hasAnyRole`) helpers.
- Defensive reads that return an empty list on any failure.

## ⚠️ Security caveat (important)

**Hiding a command in the UI is a convenience, not an authorization control.** A
user can still invoke the underlying operation directly (Web API, bookmark, dev
tools). Any action a privileged command performs **must be enforced server-side**
— via Dataverse security roles, table/column permissions, or plug-in/business
logic. This script is UX only.

## Key technique

```js
function hasAnyRole(roleIds) {
  const userRoleIds = getUserSecurityRoleIds(); // from userSettings.securityRoles
  return roleIds.some((rid) => userRoleIds.includes(String(rid).toLowerCase()));
}
```

## Not preserved / withheld

The production security-role GUID(s) and the specific command(s) protected are
withheld, as is the underlying server-side security configuration.
