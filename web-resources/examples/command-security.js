/**
 * SANITIZED EXAMPLE
 *
 * Reconstructed from a production model-driven app pattern.
 * All schema names, identifiers, role names, and business rules are fictional.
 *
 * Primary pattern (source-backed): gate a command by comparing the current
 * user's security-role IDs against invented role-ID tokens. Supports a single
 * role check and a multiple-role check.
 *
 * IMPORTANT: hiding a command in the UI is a convenience, NOT a security
 * control. Any operation a privileged command performs must be enforced
 * server-side (security roles, table/column permissions, or plug-in logic). A
 * user can still invoke the underlying operation directly.
 */

"use strict";

const CommandSecurity = (() => {
  // Invented role-ID tokens. Production role GUIDs are never published; a
  // deployment replaces these placeholders with its own role ids.
  const ROLE_IDS = {
    admin: "SAMPLE_ADMIN_ROLE_ID",
    reviewer: "SAMPLE_REVIEWER_ROLE_ID",
  };

  /**
   * The current user's security-role IDs, lowercased. Empty array on failure.
   */
  function getUserSecurityRoleIds() {
    try {
      const roles = Xrm.Utility.getGlobalContext().userSettings.securityRoles;
      return Array.isArray(roles) ? roles.map((r) => String(r).toLowerCase()) : [];
    } catch (err) {
      console.error("command-security: could not read securityRoles", err && err.message);
      return [];
    }
  }

  /**
   * Single-role check: does the user hold the given role id?
   */
  function hasRole(roleId) {
    if (!roleId) {
      return false;
    }
    const target = String(roleId).toLowerCase();
    return getUserSecurityRoleIds().some((id) => id === target);
  }

  /**
   * Multiple-role check: does the user hold ANY of the given role ids?
   */
  function hasAnyRole(roleIds) {
    if (!Array.isArray(roleIds) || roleIds.length === 0) {
      return false;
    }
    const userRoleIds = getUserSecurityRoleIds();
    return roleIds.some((rid) => userRoleIds.includes(String(rid).toLowerCase()));
  }

  /**
   * Command-visibility rule. A ribbon/command Enable rule calls this and uses the
   * boolean to show/enable the button. It affects UI only — not authorization.
   */
  function canSeePrivilegedCommand() {
    return hasAnyRole([ROLE_IDS.admin, ROLE_IDS.reviewer]);
  }

  // ----------------------------------------------------------------------- //
  // ALTERNATIVE (modern) approach: compare role NAMES via userSettings.roles
  // instead of role IDs. Documented for reference; the primary uses role IDs to
  // mirror the source technique.
  // ----------------------------------------------------------------------- //
  const ALTERNATIVE = {
    roleNames: { admin: "sample administrator", reviewer: "sample reviewer" },
    getUserRoleNames() {
      try {
        const roles = Xrm.Utility.getGlobalContext().userSettings.roles;
        const names = [];
        if (roles && typeof roles.forEach === "function") {
          roles.forEach((role) => {
            if (role && role.name) {
              names.push(String(role.name).toLowerCase());
            }
          });
        }
        return names;
      } catch (err) {
        console.error("command-security(alt): could not read roles", err && err.message);
        return [];
      }
    },
    hasAnyRoleName(requiredNames) {
      const userNames = this.getUserRoleNames();
      return requiredNames.some((n) => userNames.includes(String(n).toLowerCase()));
    },
  };

  return { canSeePrivilegedCommand, hasRole, hasAnyRole, getUserSecurityRoleIds, ALTERNATIVE, ROLE_IDS };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = CommandSecurity;
}
