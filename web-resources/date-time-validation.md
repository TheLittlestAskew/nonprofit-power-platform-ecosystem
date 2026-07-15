# Date/Time Validation

Each schedule "slot" has a date lookup and start/end datetime fields. When the
date lookup changes, its scheduled date is applied to start and end (preserving
any existing time). Start must fall on the scheduled date; end may fall on the
scheduled date or the next day (overnight). On save, a slot whose start equals
its end is cleared.

Example: [`examples/date-time-validation.js`](examples/date-time-validation.js)

## Evidence

- **Directly supported technique:** a date lookup identifies the scheduled date;
  `Xrm.WebApi.retrieveRecord` reads that date; on lookup change the scheduled date
  is applied to start and end while preserving existing time components; start is
  validated to match the scheduled date; end is allowed on the scheduled date or
  the immediately following date (overnight); on save, equal start/end pairs are
  cleared.
- **Sanitized replacement:** production date entity/column → invented
  `sample_schedule_dates` / `sample_date_value`; the production **seven** day
  mappings → **two** invented slot configurations.
- **Withheld:** the production entity/column names and the full day set.
- **No duration extension:** the earlier public draft's duration-based end-time
  calculation was **removed**; it was not part of the source. No duration field is
  introduced.

## What it demonstrates

- **Date-lookup-driven** start/end population via `retrieveRecord`.
- **Time-preserving** application of the scheduled date.
- **Match validation** (start on scheduled date) and **overnight support** (end on
  scheduled or next day), each with a correction that keeps the entered time.
- **Clear-on-save** of equal start/end pairs (no interval scheduled).

## Key technique

```js
// Overnight support: end may be the scheduled date or the next day.
const isSameDay = scheduledDate.toDateString() === end.toDateString();
const isNextDay = nextDay.toDateString() === end.toDateString();
if (!isSameDay && !isNextDay) { /* notify + correct, keep time */ }
```

## Not preserved / withheld

The production date entity/column names and the full set of day mappings are
withheld; two invented slots stand in for the production configuration.
