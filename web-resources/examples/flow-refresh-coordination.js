/**
 * SANITIZED EXAMPLE
 *
 * Reconstructed from a production model-driven app pattern.
 * All schema names, identifiers, role names, and business rules are fictional.
 *
 * Primary pattern (source-backed): on a NEW record's OnLoad, wait (bounded) for
 * the record to receive an id after its initial save, then poll by refreshing
 * form data and checking two related lookup fields created out-of-band by a
 * Power Automate cloud flow. Stop when both are present, do one final refresh,
 * and stop cleanly after the maximum attempts. Includes error/timeout handling.
 *
 * An ALTERNATIVE Web API baseline-count implementation is included at the bottom,
 * clearly labeled; it does not replace the primary source-backed pattern.
 */

"use strict";

const FlowRefreshCoordination = (() => {
  const CONFIG = {
    lookupA: "sample_related_record_a",
    lookupB: "sample_related_record_b",
    waitForIdIntervalMs: 1000,
    waitForIdMaxAttempts: 30, // ~30s bounded wait for the initial id
    pollIntervalMs: 1000,
    maxPollAttempts: 20,
  };

  function wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function hasValue(formContext, field) {
    const attr = formContext.getAttribute(field);
    const value = attr ? attr.getValue() : null;
    return Array.isArray(value) ? value.length > 0 : Boolean(value);
  }

  /**
   * Bounded wait for the new record to receive an id after its initial save.
   * Resolves the id, or null on timeout.
   */
  async function waitForRecordId(formContext) {
    for (let attempt = 0; attempt < CONFIG.waitForIdMaxAttempts; attempt += 1) {
      const id = formContext.data.entity.getId();
      if (id) {
        return id;
      }
      await wait(CONFIG.waitForIdIntervalMs);
    }
    return null; // bounded timeout
  }

  /**
   * Poll by refreshing form data and checking both related lookups. Resolves
   * true once both are present, false on timeout. Bounded — never spins.
   */
  async function pollForBothRecords(formContext) {
    for (let attempt = 0; attempt < CONFIG.maxPollAttempts; attempt += 1) {
      await wait(CONFIG.pollIntervalMs);
      try {
        await formContext.data.refresh(false);
      } catch (err) {
        console.error("flow-refresh: refresh failed", err && err.message);
        return false; // fail closed rather than spin
      }
      if (hasValue(formContext, CONFIG.lookupA) && hasValue(formContext, CONFIG.lookupB)) {
        return true;
      }
    }
    return false; // bounded timeout
  }

  /**
   * OnLoad handler. Runs only for new records; coordinates the wait-and-refresh
   * while the cloud flow creates the two related records.
   */
  async function onLoad(executionContext) {
    const formContext = executionContext.getFormContext();
    if (!formContext) {
      return;
    }
    if (formContext.ui.getFormType() !== 1) {
      return; // only new records
    }
    try {
      const id = await waitForRecordId(formContext);
      if (!id) {
        return; // record never saved within the bounded window
      }
      const bothPresent = await pollForBothRecords(formContext);
      if (bothPresent) {
        await formContext.data.refresh(false); // one final refresh
      }
    } catch (err) {
      console.error("flow-refresh: coordination failed", err && err.message);
    }
  }

  // ----------------------------------------------------------------------- //
  // ALTERNATIVE pattern (not the source-backed primary): poll a Web API count
  // of related records against a baseline captured before the flow ran. Kept
  // for reference only; prefer the form-data-refresh primary above.
  // ----------------------------------------------------------------------- //
  const ALTERNATIVE = {
    relatedEntitySet: "sample_related_records",
    parentColumn: "_sample_case_record_value",

    async countRelated(parentId) {
      const options =
        `?$select=${this.parentColumn}` +
        `&$filter=${this.parentColumn} eq ${parentId}` +
        `&$top=1`;
      const result = await Xrm.WebApi.retrieveMultipleRecords(this.relatedEntitySet, options);
      return result && result.entities ? result.entities.length : 0;
    },

    async pollForNewRecord(parentId, baseline, maxAttempts, delayMs) {
      for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
        await wait(delayMs);
        let current;
        try {
          current = await this.countRelated(parentId);
        } catch (err) {
          console.error("flow-refresh(alt): poll failed", err && err.message);
          return false;
        }
        if (current > baseline) {
          return true;
        }
      }
      return false;
    },
  };

  return {
    onLoad,
    waitForRecordId,
    pollForBothRecords,
    hasValue,
    wait,
    ALTERNATIVE,
    CONFIG,
  };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = FlowRefreshCoordination;
}
