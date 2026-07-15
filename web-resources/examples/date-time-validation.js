/**
 * SANITIZED EXAMPLE
 *
 * Reconstructed from a production model-driven app pattern.
 * All schema names, identifiers, role names, and business rules are fictional.
 *
 * Pattern: each schedule "slot" has a date lookup and start/end datetime fields.
 * When the date lookup changes, the scheduled date is applied to start and end
 * (preserving any existing time). Start must fall on the scheduled date; end may
 * fall on the scheduled date or the next day (overnight interval). On save, a
 * slot whose start equals its end is cleared (it represents no interval).
 *
 * The production original mapped seven days; this reconstruction uses two
 * invented slot configurations. No duration field is introduced.
 */

"use strict";

const DateTimeValidation = (() => {
  const CONFIG = {
    // Table LOGICAL name (singular) + column holding the scheduled date value.
    // The logical name is the first arg to Xrm.WebApi, NOT the plural entity set.
    dateEntityLogicalName: "sample_schedule_date",
    dateValueColumn: "sample_date_value",
    // Two invented slot configurations (production used more).
    slots: [
      { lookup: "sample_slot_a_date", start: "sample_slot_a_start", end: "sample_slot_a_end" },
      { lookup: "sample_slot_b_date", start: "sample_slot_b_start", end: "sample_slot_b_end" },
    ],
    startNotice: "start_date_mismatch",
    endNotice: "end_date_invalid",
    registerDelayMs: 2000,
  };

  function getLookupId(formContext, field) {
    const attr = formContext.getAttribute(field);
    const value = attr ? attr.getValue() : null;
    if (!value || !value.length || !value[0].id) {
      return null;
    }
    return value[0].id.replace(/[{}]/g, "");
  }

  function getDate(formContext, field) {
    const attr = formContext.getAttribute(field);
    const value = attr ? attr.getValue() : null;
    return value instanceof Date ? value : null;
  }

  /**
   * Retrieve the scheduled date value for a slot's date lookup, or null.
   */
  async function fetchScheduledDate(formContext, slot) {
    const dateId = getLookupId(formContext, slot.lookup);
    if (!dateId) {
      return null;
    }
    const record = await Xrm.WebApi.retrieveRecord(
      CONFIG.dateEntityLogicalName,
      dateId,
      `?$select=${CONFIG.dateValueColumn}`
    );
    const raw = record ? record[CONFIG.dateValueColumn] : null;
    return raw ? new Date(raw) : null;
  }

  // Apply a scheduled date to a datetime field, preserving any existing time.
  function applyDatePreservingTime(formContext, field, scheduledDate) {
    const next = new Date(scheduledDate);
    const existing = getDate(formContext, field);
    if (existing) {
      next.setHours(existing.getHours(), existing.getMinutes(), 0, 0);
    }
    const attr = formContext.getAttribute(field);
    if (attr) {
      attr.setValue(next);
    }
  }

  /**
   * OnChange for a slot's date lookup: apply the scheduled date to start and end.
   */
  async function onDateLookupChange(formContext, slot) {
    try {
      const scheduledDate = await fetchScheduledDate(formContext, slot);
      if (!scheduledDate) {
        return;
      }
      applyDatePreservingTime(formContext, slot.start, scheduledDate);
      applyDatePreservingTime(formContext, slot.end, scheduledDate);
    } catch (err) {
      console.error("date-time-validation: date retrieve failed", err && err.message);
    }
  }

  /**
   * OnChange for a slot's start: the start date must match the scheduled date.
   */
  async function onStartChange(formContext, slot) {
    const start = getDate(formContext, slot.start);
    if (!start) {
      return;
    }
    // Wrap the async retrieval so a dynamically-registered OnChange handler never
    // leaves an unhandled promise rejection.
    let scheduledDate;
    try {
      scheduledDate = await fetchScheduledDate(formContext, slot);
    } catch (err) {
      console.error("date-time-validation: start-date retrieve failed", err && err.message);
      return; // safe diagnostic; leave the field as entered
    }
    if (!scheduledDate) {
      return;
    }
    if (scheduledDate.toDateString() !== start.toDateString()) {
      formContext.ui.setFormNotification(
        "Start date must match the scheduled date for this slot.",
        "ERROR",
        CONFIG.startNotice
      );
      const corrected = new Date(scheduledDate);
      corrected.setHours(start.getHours(), start.getMinutes(), 0, 0);
      formContext.getAttribute(slot.start).setValue(corrected);
    } else {
      // Clear the error on a later successful, valid retrieval.
      formContext.ui.clearFormNotification(CONFIG.startNotice);
    }
  }

  /**
   * OnChange for a slot's end: end may be the scheduled date or the next day
   * (overnight interval).
   */
  async function onEndChange(formContext, slot) {
    const end = getDate(formContext, slot.end);
    if (!end) {
      return;
    }
    // Wrap the async retrieval so a dynamically-registered OnChange handler never
    // leaves an unhandled promise rejection.
    let scheduledDate;
    try {
      scheduledDate = await fetchScheduledDate(formContext, slot);
    } catch (err) {
      console.error("date-time-validation: end-date retrieve failed", err && err.message);
      return; // safe diagnostic; leave the field as entered
    }
    if (!scheduledDate) {
      return;
    }
    const nextDay = new Date(scheduledDate);
    nextDay.setDate(nextDay.getDate() + 1);
    const isSameDay = scheduledDate.toDateString() === end.toDateString();
    const isNextDay = nextDay.toDateString() === end.toDateString();
    if (!isSameDay && !isNextDay) {
      formContext.ui.setFormNotification(
        "End date must be the scheduled date or the next day (overnight).",
        "ERROR",
        CONFIG.endNotice
      );
      const corrected = new Date(scheduledDate);
      corrected.setHours(end.getHours(), end.getMinutes(), 0, 0);
      formContext.getAttribute(slot.end).setValue(corrected);
    } else {
      // Clear the error on a later successful, valid retrieval.
      formContext.ui.clearFormNotification(CONFIG.endNotice);
    }
  }

  /**
   * OnSave: clear any slot whose start equals its end (no interval scheduled).
   */
  function onSave(executionContext) {
    const formContext = executionContext.getFormContext();
    if (!formContext) {
      return;
    }
    for (const slot of CONFIG.slots) {
      const startAttr = formContext.getAttribute(slot.start);
      const endAttr = formContext.getAttribute(slot.end);
      if (!startAttr || !endAttr) {
        continue;
      }
      const start = startAttr.getValue();
      const end = endAttr.getValue();
      if (start instanceof Date && end instanceof Date && start.getTime() === end.getTime()) {
        startAttr.setValue(null);
        endAttr.setValue(null);
      }
    }
  }

  /**
   * OnLoad: register per-slot OnChange handlers. A short delay lets any
   * auto-save refresh settle before wiring events (matches the source).
   */
  function onLoad(executionContext) {
    const formContext = executionContext.getFormContext();
    if (!formContext) {
      return;
    }
    setTimeout(function registerEvents() {
      for (const slot of CONFIG.slots) {
        const lookupAttr = formContext.getAttribute(slot.lookup);
        const startAttr = formContext.getAttribute(slot.start);
        const endAttr = formContext.getAttribute(slot.end);
        if (lookupAttr) {
          lookupAttr.addOnChange(() => onDateLookupChange(formContext, slot));
        }
        if (startAttr) {
          startAttr.addOnChange(() => onStartChange(formContext, slot));
        }
        if (endAttr) {
          endAttr.addOnChange(() => onEndChange(formContext, slot));
        }
      }
    }, CONFIG.registerDelayMs);
  }

  return {
    onLoad,
    onSave,
    onDateLookupChange,
    onStartChange,
    onEndChange,
    fetchScheduledDate,
    applyDatePreservingTime,
    CONFIG,
  };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = DateTimeValidation;
}
