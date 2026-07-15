/**
 * SANITIZED EXAMPLE
 *
 * Reconstructed from a production model-driven app pattern.
 * All schema names, identifiers, role names, and business rules are fictional.
 *
 * Pattern: before saving a new related record, check whether an equivalent
 * record already exists for the same parent within a time window. If so, cancel
 * the save and notify the user. Uses async Xrm.WebApi and defers the save.
 */

"use strict";

const DuplicatePrevention = (() => {
  const CONFIG = {
    parentLookupField: "sample_case_record",
    dateField: "sample_meeting_date",
    relatedEntitySet: "sample_related_records",
    parentColumn: "_sample_case_record_value",
    dateColumn: "sample_meeting_date",
    // Invented window: treat records on the same calendar day as duplicates.
    windowHours: 24,
    notificationId: "duplicate_prevention_notice",
  };

  function getParentId(formContext) {
    const attr = formContext.getAttribute(CONFIG.parentLookupField);
    const value = attr ? attr.getValue() : null;
    if (!value || !value.length || !value[0].id) {
      return null;
    }
    return value[0].id.replace(/[{}]/g, "");
  }

  function getDate(formContext) {
    const attr = formContext.getAttribute(CONFIG.dateField);
    const value = attr ? attr.getValue() : null;
    return value instanceof Date ? value : null;
  }

  /**
   * Return true if a matching record already exists for this parent in the
   * configured window. Query values are invented.
   */
  async function existsDuplicate(parentId, date) {
    if (!parentId || !date) {
      return false;
    }
    const windowMs = CONFIG.windowHours * 60 * 60 * 1000;
    const start = new Date(date.getTime() - windowMs).toISOString();
    const end = new Date(date.getTime() + windowMs).toISOString();
    const options =
      `?$select=${CONFIG.dateColumn}` +
      `&$filter=${CONFIG.parentColumn} eq ${parentId}` +
      ` and ${CONFIG.dateColumn} ge ${start}` +
      ` and ${CONFIG.dateColumn} le ${end}` +
      `&$top=1`;
    const result = await Xrm.WebApi.retrieveMultipleRecords(
      CONFIG.relatedEntitySet,
      options
    );
    return Boolean(result && result.entities && result.entities.length);
  }

  /**
   * OnSave handler. Only new records are checked. The save is deferred with
   * preventDefault() while the async check runs, then re-issued if clean.
   */
  async function onSave(executionContext) {
    const formContext = executionContext.getFormContext();
    const eventArgs = executionContext.getEventArgs();
    if (!formContext || !eventArgs) {
      return;
    }
    if (formContext.ui.getFormType() !== 1) {
      return; // only guard creation of new records
    }
    // Avoid re-entrancy: a flag on the form marks a validated, re-issued save.
    if (formContext.data && formContext.data.__dupCheckPassed) {
      formContext.data.__dupCheckPassed = false;
      return;
    }

    const parentId = getParentId(formContext);
    const date = getDate(formContext);
    if (!parentId || !date) {
      return; // insufficient data to check; let platform validation handle it
    }

    // Defer the save until the async check completes.
    eventArgs.preventDefault();

    try {
      const duplicate = await existsDuplicate(parentId, date);
      if (duplicate) {
        formContext.ui.setFormNotification(
          "A matching record already exists for this parent in the selected window.",
          "WARNING",
          CONFIG.notificationId
        );
        return; // save stays cancelled
      }
      formContext.ui.clearFormNotification(CONFIG.notificationId);
      // Mark as validated and re-issue the save exactly once.
      if (formContext.data) {
        formContext.data.__dupCheckPassed = true;
      }
      formContext.data.save();
    } catch (err) {
      // On error, do not silently allow a possible duplicate; surface it.
      console.error("duplicate-prevention: check failed", err && err.message);
      formContext.ui.setFormNotification(
        "Could not verify duplicates. Please retry.",
        "ERROR",
        CONFIG.notificationId
      );
    }
  }

  return { onSave, existsDuplicate, getParentId, getDate, CONFIG };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = DuplicatePrevention;
}
