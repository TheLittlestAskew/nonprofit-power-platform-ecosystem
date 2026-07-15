/**
 * SANITIZED EXAMPLE
 *
 * Reconstructed from a production model-driven app pattern.
 * All schema names, identifiers, role names, and business rules are fictional.
 *
 * Pattern: when a new record is linked to a person who has a prior related
 * record, retrieve the most recent prior record, map selected values forward,
 * and conditionally lock the copied fields. Uses async Xrm.WebApi.
 */

"use strict";

const ReturningRecordAutoFill = (() => {
  const CONFIG = {
    // Generalized entity/logical set names and columns (all invented).
    personLookupField: "sample_person",
    relatedEntitySet: "sample_related_records",
    personColumn: "_sample_person_value",
    createdOnColumn: "createdon",
    // Columns copied forward from the prior related record.
    mappedFields: ["sample_phone", "sample_preferred_contact", "sample_notes"],
    lockWhenCopied: true,
  };

  /**
   * Read the selected person's id from a lookup, or null when unset.
   */
  function getSelectedPersonId(formContext) {
    const attr = formContext.getAttribute(CONFIG.personLookupField);
    const value = attr ? attr.getValue() : null;
    if (!value || !value.length || !value[0].id) {
      return null;
    }
    // Xrm returns lookup ids wrapped in braces; normalize to a bare id.
    return value[0].id.replace(/[{}]/g, "");
  }

  /**
   * Retrieve the most recent prior related record for a person, or null.
   * Query filter values are invented; no production query is reproduced.
   */
  async function fetchMostRecentRelated(personId) {
    if (!personId) {
      return null;
    }
    const cols = CONFIG.mappedFields.join(",");
    const options =
      `?$select=${cols}` +
      `&$filter=${CONFIG.personColumn} eq ${personId}` +
      `&$orderby=${CONFIG.createdOnColumn} desc` +
      `&$top=1`;
    const result = await Xrm.WebApi.retrieveMultipleRecords(
      CONFIG.relatedEntitySet,
      options
    );
    return result && result.entities && result.entities.length
      ? result.entities[0]
      : null;
  }

  /**
   * Copy mapped values into the current form and optionally lock them.
   */
  function applyValues(formContext, prior) {
    if (!prior) {
      return;
    }
    for (const field of CONFIG.mappedFields) {
      const attr = formContext.getAttribute(field);
      if (!attr) {
        continue; // field not on this form: skip safely
      }
      const value = Object.prototype.hasOwnProperty.call(prior, field)
        ? prior[field]
        : null;
      if (value !== null && value !== undefined) {
        attr.setValue(value);
        if (CONFIG.lockWhenCopied) {
          const control = formContext.getControl(field);
          if (control && typeof control.setDisabled === "function") {
            control.setDisabled(true);
          }
        }
      }
    }
  }

  /**
   * OnChange handler for the person lookup. Async: awaits the Web API call,
   * with explicit error handling so a lookup failure never blocks the form.
   */
  async function onPersonChange(executionContext) {
    const formContext = executionContext.getFormContext();
    if (!formContext) {
      return;
    }
    // Only auto-fill on new records; never overwrite an existing record.
    if (formContext.ui.getFormType() !== 1) {
      return;
    }
    const personId = getSelectedPersonId(formContext);
    if (!personId) {
      return;
    }
    try {
      const prior = await fetchMostRecentRelated(personId);
      applyValues(formContext, prior);
    } catch (err) {
      // Non-fatal: log for diagnostics, leave the form usable.
      console.error("returning-record-autofill: retrieve failed", err && err.message);
    }
  }

  return {
    onPersonChange,
    getSelectedPersonId,
    fetchMostRecentRelated,
    applyValues,
    CONFIG,
  };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = ReturningRecordAutoFill;
}
