/**
 * SANITIZED EXAMPLE
 *
 * Reconstructed from a production model-driven app pattern.
 * All schema names, identifiers, role names, and business rules are fictional.
 *
 * Pattern: a command triggers a Power Automate cloud flow that creates a related
 * record asynchronously. The form polls (bounded) for that record to appear,
 * then refreshes a subgrid or the form. Includes timeout and failure handling.
 */

"use strict";

const FlowRefreshCoordination = (() => {
  const CONFIG = {
    parentColumn: "_sample_case_record_value",
    relatedEntitySet: "sample_related_records",
    subgridName: "sample_related_subgrid",
    // Bounded retry: at most maxAttempts polls, delayMs apart.
    maxAttempts: 6,
    delayMs: 1500,
    notificationId: "flow_refresh_notice",
  };

  /**
   * Await a fixed delay. Uses a Promise wrapper around setTimeout so callers can
   * `await` between polls without blocking the UI thread.
   */
  function wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Count related records for a parent. Query values are invented.
   */
  async function countRelated(parentId) {
    const options =
      `?$select=${CONFIG.parentColumn}` +
      `&$filter=${CONFIG.parentColumn} eq ${parentId}` +
      `&$top=1`;
    const result = await Xrm.WebApi.retrieveMultipleRecords(
      CONFIG.relatedEntitySet,
      options
    );
    return result && result.entities ? result.entities.length : 0;
  }

  function refreshSubgrid(formContext) {
    const grid = formContext.getControl(CONFIG.subgridName);
    if (grid && typeof grid.refresh === "function") {
      grid.refresh();
    } else if (formContext.data && typeof formContext.data.refresh === "function") {
      // Fall back to a form data refresh if the subgrid is not present.
      formContext.data.refresh(false);
    }
  }

  /**
   * Poll for a flow-created record, bounded by maxAttempts. Resolves true if a
   * record appeared, false on timeout. Never loops unbounded.
   *
   * @param {string} parentId invented parent record id
   * @param {number} baseline record count observed before the flow ran
   */
  async function pollForNewRecord(parentId, baseline) {
    for (let attempt = 0; attempt < CONFIG.maxAttempts; attempt += 1) {
      await wait(CONFIG.delayMs);
      let current;
      try {
        current = await countRelated(parentId);
      } catch (err) {
        console.error("flow-refresh: poll query failed", err && err.message);
        return false; // fail closed rather than spin
      }
      if (current > baseline) {
        return true;
      }
    }
    return false; // bounded timeout
  }

  /**
   * Command handler: run after the cloud flow has been triggered elsewhere.
   * Assumes the flow itself is invoked by the platform command; this coordinates
   * the client-side wait-and-refresh.
   */
  async function onAfterFlowTriggered(formContext, parentId) {
    if (!formContext || !parentId) {
      return;
    }
    let baseline = 0;
    try {
      baseline = await countRelated(parentId);
    } catch (err) {
      console.error("flow-refresh: baseline query failed", err && err.message);
      return;
    }

    formContext.ui.setFormNotification(
      "Processing… waiting for the new record.",
      "INFO",
      CONFIG.notificationId
    );

    const appeared = await pollForNewRecord(parentId, baseline);
    formContext.ui.clearFormNotification(CONFIG.notificationId);

    if (appeared) {
      refreshSubgrid(formContext);
    } else {
      formContext.ui.setFormNotification(
        "The record was not ready in time. Refresh manually in a moment.",
        "WARNING",
        CONFIG.notificationId
      );
    }
  }

  return {
    onAfterFlowTriggered,
    pollForNewRecord,
    countRelated,
    refreshSubgrid,
    wait,
    CONFIG,
  };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = FlowRefreshCoordination;
}
