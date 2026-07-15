/**
 * SANITIZED EXAMPLE
 *
 * Reconstructed from a production model-driven app pattern.
 * All schema names, identifiers, role names, and business rules are fictional.
 *
 * Pattern: show or enable a command only for users holding a given role. Role
 * names are invented. IMPORTANT: hiding a command in the UI is a convenience,
 * NOT a security control. Any operation the command performs must be enforced
 * server-side (security roles, column/table permissions, or plug-in logic).
 */

"use strict";

const CommandSecurity = (() => {
  // Invented role names. Real security-role and business-unit names are never
  // published; a deployment maps these placeholders to its own roles.
  const ROLES = {
    administrator: "Sample Administrator",
    reviewer: "Sample Reviewer",
  };

  /**
   * Return the set of role names for the current user, lowercased for
   * case-insensitive comparison. Returns an empty set on any failure.
   */
  function getUserRoleNames() {
    try {
      const settings = Xrm.Utility.getGlobalContext().userSettings;
      const roles = settings && settings.roles;
      const names = new Set();
      if (roles && typeof roles.forEach === "function") {
        roles.forEach((role) => {
          const name = role && role.name ? String(role.name).toLowerCase() : "";
          if (name) {
            names.add(name);
          }
        });
      }
      return names;
    } catch (err) {
      console.error("command-security: could not read roles", err && err.message);
      return new Set();
    }
  }

  /**
   * True if the current user holds any of the supplied role names.
   */
  function hasAnyRole(requiredRoleNames) {
    if (!Array.isArray(requiredRoleNames) || requiredRoleNames.length === 0) {
      return false;
    }
    const userRoles = getUserRoleNames();
    return requiredRoleNames.some((name) =>
      userRoles.has(String(name).toLowerCase())
    );
  }

  /**
   * Command-visibility rule for a privileged command. Ribbon/command rules call
   * this and use the boolean to show or enable the button.
   *
   * Reminder: this only affects what the user SEES. It does not authorize the
   * underlying action — that must be enforced by server-side security.
   */
  function canSeePrivilegedCommand() {
    return hasAnyRole([ROLES.administrator, ROLES.reviewer]);
  }

  /**
   * Enable/disable a command's control if the host exposes it. Falls back to
   * doing nothing (safe) when the control cannot be resolved.
   */
  function applyEnablement(formContext, controlName) {
    if (!formContext || !controlName) {
      return;
    }
    const control = formContext.getControl(controlName);
    if (control && typeof control.setDisabled === "function") {
      control.setDisabled(!canSeePrivilegedCommand());
    }
  }

  return {
    canSeePrivilegedCommand,
    hasAnyRole,
    getUserRoleNames,
    applyEnablement,
    ROLES,
  };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = CommandSecurity;
}
