/**
 * SANITIZED EXAMPLE
 *
 * Reconstructed from a production model-driven app pattern.
 * All schema names, identifiers, role names, and business rules are fictional.
 *
 * Pattern: route a record to an intake form (new record) or the main form
 * (existing record) on load. Uses only invented form identifiers and generalized
 * field names.
 */

"use strict";

const FormRouting = (() => {
  // Centralized, invented constants. Real form GUIDs are never published; these
  // are placeholder tokens a deployment would replace with its own values.
  const CONFIG = {
    intakeFormId: "SAMPLE_INTAKE_FORM_ID",
    mainFormId: "SAMPLE_MAIN_FORM_ID",
    // Generalized boolean column indicating a returning record.
    returningFlagField: "sample_is_returning",
  };

  /**
   * Return the current form id, or null if it cannot be determined.
   * formContext is passed in explicitly rather than read from a global.
   */
  function getCurrentFormId(formContext) {
    const ui = formContext && formContext.ui;
    const currentForm = ui && ui.formSelector && ui.formSelector.getCurrentItem
      ? ui.formSelector.getCurrentItem()
      : null;
    return currentForm ? currentForm.getId() : null;
  }

  /**
   * Navigate to a target form only when it differs from the current one, so we
   * never trigger a redundant reload loop.
   */
  function routeTo(formContext, targetFormId) {
    if (!targetFormId) {
      return; // safe fallback: no target, stay on the current form
    }
    const currentFormId = getCurrentFormId(formContext);
    if (currentFormId && currentFormId.toLowerCase() === targetFormId.toLowerCase()) {
      return; // already on the intended form
    }
    const item = formContext.ui.formSelector.items.get(targetFormId);
    if (item && typeof item.navigate === "function") {
      item.navigate();
    }
    // If the target form is not available to this user, we intentionally do
    // nothing and let them remain on the default form (safe fallback).
  }

  /**
   * OnLoad handler. Detects new vs. existing record and routes accordingly.
   *
   * @param {object} executionContext model-driven form execution context
   */
  function onLoad(executionContext) {
    const formContext = executionContext.getFormContext();
    if (!formContext) {
      return;
    }

    const formType = formContext.ui.getFormType();
    // formType 1 = Create (new record); 2 = Update (existing record).
    const isNewRecord = formType === 1;

    if (isNewRecord) {
      routeTo(formContext, CONFIG.intakeFormId);
      return;
    }

    // Existing record: route returning records to the main form; otherwise
    // leave the default form in place.
    const attr = formContext.getAttribute(CONFIG.returningFlagField);
    const isReturning = attr ? attr.getValue() === true : false;
    if (isReturning) {
      routeTo(formContext, CONFIG.mainFormId);
    }
  }

  return { onLoad, routeTo, getCurrentFormId, CONFIG };
})();

// Model-driven apps invoke the registered handler by name; exported for tests.
if (typeof module !== "undefined" && module.exports) {
  module.exports = FormRouting;
}
