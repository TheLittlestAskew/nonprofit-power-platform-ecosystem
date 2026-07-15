/**
 * SANITIZED EXAMPLE
 *
 * Reconstructed from a production model-driven app pattern.
 * All schema names, identifiers, role names, and business rules are fictional.
 *
 * Pattern: prevent creating more than one related record for the same parent.
 * On save of a NEW record, look up the selected parent, check whether ANY
 * related record already exists for it, defer the save during the async check,
 * block + notify on a duplicate, and re-issue the save when clean. Existing
 * records update normally.
 *
 * INTENTIONAL DEVIATION FROM SOURCE (hardening):
 *   Production source allowed the save after a query failure (fail-open). This
 *   public reconstruction blocks the save and asks the user to retry
 *   (fail-closed). This is a deliberate hardening, NOT historical production
 *   behavior.
 */

"use strict";

const DuplicatePrevention = (() => {
  const CONFIG = {
    parentLookupField: "sample_case_record",
    relatedEntitySet: "sample_related_records",
    parentColumn: "_sample_case_record_value",
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

  /**
   * True if ANY related record already exists for this parent. There is no time
   * window — one related record per parent is the rule. Query values invented.
   */
  async function existsForParent(parentId) {
    if (!parentId) {
      return false;
    }
    const options =
      `?$select=${CONFIG.parentColumn}` +
      `&$filter=${CONFIG.parentColumn} eq ${parentId}` +
      `&$top=1`;
    const result = await Xrm.WebApi.retrieveMultipleRecords(CONFIG.relatedEntitySet, options);
    return Boolean(result && result.entities && result.entities.length);
  }

  /**
   * OnSave handler. Only new records are guarded; existing records update
   * normally. The save is deferred with preventDefault() while the async check
   * runs, then re-issued exactly once (a re-entrancy flag prevents a save loop).
   */
  async function onSave(executionContext) {
    const formContext = executionContext.getFormContext();
    const eventArgs = executionContext.getEventArgs();
    if (!formContext || !eventArgs) {
      return;
    }
    if (formContext.ui.getFormType() !== 1) {
      return; // existing record: allow normal update
    }
    // Re-entrancy guard (modernization): a validated, re-issued save skips the
    // check exactly once, avoiding an infinite save loop.
    if (formContext.data && formContext.data.__dupCheckPassed) {
      formContext.data.__dupCheckPassed = false;
      return;
    }

    const parentId = getParentId(formContext);
    if (!parentId) {
      return; // no parent selected; let platform validation handle it
    }

    eventArgs.preventDefault(); // defer the save during the async check

    try {
      const duplicate = await existsForParent(parentId);
      if (duplicate) {
        formContext.ui.setFormNotification(
          "A related record already exists for the selected parent. Only one is allowed.",
          "ERROR",
          CONFIG.notificationId
        );
        return; // save stays cancelled
      }
      formContext.ui.clearFormNotification(CONFIG.notificationId);
      if (formContext.data) {
        formContext.data.__dupCheckPassed = true;
      }
      formContext.data.save(); // re-issue once
    } catch (err) {
      // INTENTIONAL DEVIATION (fail-closed): unlike the source, do not allow the
      // save on a query error — surface it and ask the user to retry.
      console.error("duplicate-prevention: check failed", err && err.message);
      formContext.ui.setFormNotification(
        "Could not verify duplicates. Please retry.",
        "ERROR",
        CONFIG.notificationId
      );
    }
  }

  return { onSave, existsForParent, getParentId, CONFIG };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = DuplicatePrevention;
}
