/**
 * SANITIZED EXAMPLE
 *
 * Reconstructed from a production model-driven app pattern.
 * All schema names, identifiers, role names, and business rules are fictional.
 *
 * Pattern: two form-scoped OnLoad handlers keep records on the correct form.
 * A NEW record opened on the main form is redirected to the intake form; a new
 * record already on the intake form stays; existing records are never
 * auto-rerouted (a user who intentionally opens an existing record on the intake
 * form is left alone). Uses invented form tokens and an invented entity name.
 */

"use strict";

const FormRouting = (() => {
  // Invented placeholders. Production form GUIDs and entity names are never
  // published; a deployment replaces these with its own values.
  const CONFIG = {
    intakeFormId: "SAMPLE_INTAKE_FORM_ID",
    mainFormId: "SAMPLE_MAIN_FORM_ID",
    entityName: "sample_person",
  };

  function getCurrentFormId(formContext) {
    const selector = formContext && formContext.ui && formContext.ui.formSelector;
    const current = selector && selector.getCurrentItem ? selector.getCurrentItem() : null;
    return current ? current.getId().toLowerCase() : null;
  }

  /**
   * Handler for the INTAKE form. New records belong here, so nothing is routed.
   * Existing records on the intake form are intentional; leave them in place.
   * Register on the intake form's OnLoad.
   */
  function ensureIntakeFormForNewOnly(executionContext) {
    const formContext = executionContext.getFormContext();
    if (!formContext) {
      return;
    }
    const currentFormId = getCurrentFormId(formContext);
    if (currentFormId !== CONFIG.intakeFormId.toLowerCase()) {
      return; // safe fallback: not on the intake form, do nothing
    }
    // New record on the intake form = correct; existing record = intentional.
    // Either way, no navigation occurs here.
  }

  /**
   * Handler for the MAIN form. Only a NEW record is redirected to the intake
   * form; existing records stay on the main form. Register on the main form's
   * OnLoad.
   */
  function ensureMainFormForExistingOnly(executionContext) {
    const formContext = executionContext.getFormContext();
    if (!formContext) {
      return;
    }
    const currentFormId = getCurrentFormId(formContext);
    if (currentFormId !== CONFIG.mainFormId.toLowerCase()) {
      return; // safe fallback: not on the main form, do nothing
    }
    // formType 1 = Create (new). Only new records are redirected.
    if (formContext.ui.getFormType() !== 1) {
      return; // existing record: stay on the main form
    }
    redirectToIntake();
  }

  function redirectToIntake() {
    const pageInput = {
      pageType: "entityrecord",
      entityName: CONFIG.entityName,
      formId: CONFIG.intakeFormId,
    };
    const navigationOptions = { target: 1, position: 1 };
    Xrm.Navigation.navigateTo(pageInput, navigationOptions).then(
      function success() {},
      function error(err) {
        // Safe fallback: if navigation fails, the user simply stays on the
        // current form rather than being blocked.
        console.error("form-routing: redirect failed", err && err.message);
      }
    );
  }

  return { ensureIntakeFormForNewOnly, ensureMainFormForExistingOnly, getCurrentFormId, CONFIG };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = FormRouting;
}
