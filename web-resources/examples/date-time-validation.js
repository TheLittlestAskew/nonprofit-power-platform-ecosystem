/**
 * SANITIZED EXAMPLE
 *
 * Reconstructed from a production model-driven app pattern.
 * All schema names, identifiers, role names, and business rules are fictional.
 *
 * Pattern: auto-populate an end time from a start time and duration, handle an
 * event that crosses midnight, validate before save, and clean up transient
 * form state afterward.
 */

"use strict";

const DateTimeValidation = (() => {
  const CONFIG = {
    startField: "sample_start_time",
    endField: "sample_end_time",
    durationField: "sample_duration_minutes", // whole number of minutes
    defaultDurationMinutes: 60,
    notificationId: "datetime_validation_notice",
    transientFlag: "sample_end_autofilled",
  };

  function getDate(formContext, field) {
    const attr = formContext.getAttribute(field);
    const value = attr ? attr.getValue() : null;
    return value instanceof Date ? value : null;
  }

  function getDuration(formContext) {
    const attr = formContext.getAttribute(CONFIG.durationField);
    const raw = attr ? attr.getValue() : null;
    const minutes = Number.isFinite(raw) ? raw : CONFIG.defaultDurationMinutes;
    return minutes > 0 ? minutes : CONFIG.defaultDurationMinutes;
  }

  /**
   * Compute an end time from a start time plus a duration in minutes. Because
   * this is date-arithmetic, an end that lands past midnight naturally rolls to
   * the next day, so overnight events are handled without special casing.
   */
  function computeEnd(start, durationMinutes) {
    if (!(start instanceof Date)) {
      return null;
    }
    return new Date(start.getTime() + durationMinutes * 60 * 1000);
  }

  /**
   * OnChange handler for start time or duration: recompute the end time.
   */
  function onStartOrDurationChange(executionContext) {
    const formContext = executionContext.getFormContext();
    if (!formContext) {
      return;
    }
    const start = getDate(formContext, CONFIG.startField);
    if (!start) {
      return; // nothing to compute from
    }
    const end = computeEnd(start, getDuration(formContext));
    const endAttr = formContext.getAttribute(CONFIG.endField);
    if (end && endAttr) {
      endAttr.setValue(end);
      // Mark that we auto-filled the end so cleanup can distinguish it from a
      // value a user typed manually.
      const flag = formContext.getAttribute(CONFIG.transientFlag);
      if (flag) {
        flag.setValue(true);
      }
    }
  }

  /**
   * OnSave handler: validate that end is strictly after start. An overnight
   * event (end on the following day) is valid; end before start is not.
   */
  function onSave(executionContext) {
    const formContext = executionContext.getFormContext();
    const eventArgs = executionContext.getEventArgs();
    if (!formContext || !eventArgs) {
      return;
    }
    const start = getDate(formContext, CONFIG.startField);
    const end = getDate(formContext, CONFIG.endField);
    if (start && end && end.getTime() <= start.getTime()) {
      eventArgs.preventDefault(); // cancel the save
      formContext.ui.setFormNotification(
        "End time must be after start time.",
        "ERROR",
        CONFIG.notificationId
      );
      return;
    }
    formContext.ui.clearFormNotification(CONFIG.notificationId);
    cleanupTransientState(formContext);
  }

  /**
   * Clear the transient auto-fill marker so it does not persist between edits.
   */
  function cleanupTransientState(formContext) {
    const flag = formContext.getAttribute(CONFIG.transientFlag);
    if (flag) {
      flag.setValue(false);
    }
  }

  return {
    onStartOrDurationChange,
    onSave,
    computeEnd,
    cleanupTransientState,
    CONFIG,
  };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = DateTimeValidation;
}
