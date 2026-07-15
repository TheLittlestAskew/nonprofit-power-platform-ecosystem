/**
 * SANITIZED EXAMPLE
 *
 * Reconstructed from a production model-driven app pattern.
 * All schema names, identifiers, role names, and business rules are fictional.
 *
 * Pattern: when a person lookup is set, retrieve that person record together
 * with an expanded prior related record, copy generalized field groups forward,
 * and — when the prior record is flagged for review — lock the copied fields and
 * require an override before proceeding. Clearing the lookup resets everything.
 *
 * MODERNIZATION FROM SOURCE: the production original issued a raw fetch() against
 * /api/data/v9.2. This reconstruction uses Xrm.WebApi.retrieveRecord with
 * invented $select / $expand options.
 *
 * Protected identifier and demographic field groups and the production
 * qualification rule are intentionally withheld; a generalized review flag
 * stands in for the domain-specific rule.
 */

"use strict";

const ReturningRecordAutoFill = (() => {
  const CONFIG = {
    personLookupField: "sample_person",
    primaryEntitySet: "sample_people",
    // Single-valued navigation property to the prior related record.
    priorRecordExpand: "sample_prior_record",
    // Generalized field group copied forward from the primary record.
    mappedFields: ["sample_summary", "sample_notes", "sample_contact_pref"],
    // Generalized status flag on the prior record that drives locking.
    requiresReviewFlag: "sample_requires_review",
    overrideField: "sample_override",
    overrideReasonField: "sample_override_reason",
    notificationId: "returning_record_autofill",
  };

  // ---- small, null-safe helpers ------------------------------------------- //
  function setValue(formContext, field, value) {
    const attr = formContext.getAttribute(field);
    if (attr) {
      attr.setValue(value === undefined ? null : value);
    }
  }
  function setDisabled(formContext, field, disabled) {
    const control = formContext.getControl(field);
    if (control && typeof control.setDisabled === "function") {
      control.setDisabled(disabled);
    }
  }
  function setRequired(formContext, field, required) {
    const attr = formContext.getAttribute(field);
    if (attr && typeof attr.setRequiredLevel === "function") {
      attr.setRequiredLevel(required ? "required" : "none");
    }
  }

  function getPersonId(formContext) {
    const attr = formContext.getAttribute(CONFIG.personLookupField);
    const value = attr ? attr.getValue() : null;
    if (!value || !value.length || !value[0].id) {
      return null;
    }
    return value[0].id.replace(/[{}]/g, "");
  }

  /**
   * Retrieve the selected person plus an expanded prior related record.
   */
  async function fetchPersonWithPrior(personId) {
    const select = CONFIG.mappedFields.join(",");
    const options =
      `?$select=${select}` +
      `&$expand=${CONFIG.priorRecordExpand}($select=${CONFIG.requiresReviewFlag})`;
    return Xrm.WebApi.retrieveRecord(CONFIG.primaryEntitySet, personId, options);
  }

  function clearCopiedFields(formContext) {
    for (const field of CONFIG.mappedFields) {
      setValue(formContext, field, null);
    }
  }
  function resetControlState(formContext) {
    for (const field of CONFIG.mappedFields) {
      setDisabled(formContext, field, false);
    }
    setRequired(formContext, CONFIG.overrideField, false);
    const control = formContext.getControl(CONFIG.overrideField);
    if (control && typeof control.clearNotification === "function") {
      control.clearNotification();
    }
    formContext.ui.clearFormNotification(CONFIG.notificationId);
  }
  function clearOverride(formContext) {
    setValue(formContext, CONFIG.overrideField, null);
    setValue(formContext, CONFIG.overrideReasonField, null);
  }

  function applyPrimary(formContext, record) {
    for (const field of CONFIG.mappedFields) {
      if (Object.prototype.hasOwnProperty.call(record, field)) {
        setValue(formContext, field, record[field]);
      }
    }
  }

  /**
   * When the prior record requires review, lock the copied fields and require an
   * override; the override controls themselves stay enabled. Otherwise, unlock.
   */
  function applyReviewLock(formContext, record) {
    const prior = record[CONFIG.priorRecordExpand];
    const requiresReview = Boolean(prior && prior[CONFIG.requiresReviewFlag] === true);

    if (requiresReview) {
      for (const field of CONFIG.mappedFields) {
        setDisabled(formContext, field, true);
      }
      // Keep override controls usable.
      setDisabled(formContext, CONFIG.overrideField, false);
      setDisabled(formContext, CONFIG.overrideReasonField, false);
      setRequired(formContext, CONFIG.overrideField, true);
      const control = formContext.getControl(CONFIG.overrideField);
      if (control && typeof control.setNotification === "function") {
        control.setNotification("This record is flagged for review. Override to proceed.");
      }
    } else {
      resetControlState(formContext);
    }
  }

  /**
   * OnChange handler for the person lookup. Clearing the lookup resets the form;
   * selecting a person copies values forward and applies the review lock.
   */
  async function onPersonChange(executionContext) {
    const formContext = executionContext.getFormContext();
    if (!formContext) {
      return;
    }
    const personId = getPersonId(formContext);
    if (!personId) {
      clearCopiedFields(formContext);
      resetControlState(formContext);
      clearOverride(formContext);
      return;
    }
    try {
      const record = await fetchPersonWithPrior(personId);
      if (record) {
        applyPrimary(formContext, record);
        applyReviewLock(formContext, record);
      }
    } catch (err) {
      console.error("returning-record-autofill: retrieve failed", err && err.message);
      formContext.ui.setFormNotification(
        "Could not load prior record. Please try again.",
        "ERROR",
        CONFIG.notificationId
      );
    }
  }

  /**
   * OnLoad initializer: register the OnChange on the lookup attribute (not the
   * control), matching the source technique.
   */
  function initialize(executionContext) {
    const formContext = executionContext.getFormContext();
    if (!formContext) {
      return;
    }
    const attr = formContext.getAttribute(CONFIG.personLookupField);
    if (attr && typeof attr.addOnChange === "function") {
      attr.addOnChange(onPersonChange);
    }
  }

  return {
    initialize,
    onPersonChange,
    fetchPersonWithPrior,
    applyPrimary,
    applyReviewLock,
    getPersonId,
    CONFIG,
  };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = ReturningRecordAutoFill;
}
