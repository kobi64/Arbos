# EX-291 — Remaining Unknown-State Contract Audit

## Purpose

Audit remaining result-model defaults after EX-286 through EX-290
to determine whether additional values incorrectly represent
unknown or unevaluated state as concrete values.

## Findings

### Boolean result fields

Fields such as:

- `valid`
- `executable`
- `profitable`
- `acceptable`
- `feasible`

retain boolean semantics.

`False` represents a deliberate fail-closed or evaluated-negative
state and is not treated as an unknown measurement.

No conversion to `Optional[bool]` is required.

### Exchange health state booleans

Operational state fields such as:

- `online`
- `authenticated`
- `maintenance`

remain boolean state indicators.

Unknown quantitative health telemetry is represented separately
using optional metric fields introduced by EX-288.

### Reason fields

Audited result models commonly declare:

    reason: str = ""

Production evaluator paths explicitly populate `reason` with a
defined outcome such as:

- `ok`
- `invalid_amount`
- `withdrawal_fee_unknown`
- `route_not_feasible`
- `below_minimum_profit`
- other domain-specific failure reasons

Repository searches found no direct dependency on an empty-string
reason sentinel in the audited execution paths.

Although `Optional[str] = None` could provide a stricter distinction
for directly constructed, unevaluated result objects, no current
production semantic defect was identified.

Changing this contract would therefore be cleanup rather than a
required correctness fix and is intentionally deferred.

### Numeric unknown-state contracts

Previous audits established the required distinction between:

- genuine calculated numeric zero
- unknown / unavailable / uncalculated values

These contracts are now represented with optional numeric fields
where required.

## Decision

No production-code change is required for EX-291.

The remaining audited defaults have intentional domain semantics or
do not currently create a false known-value condition.

Future changes to result-model reason semantics should be handled as
a separate contract migration with explicit consumer tests.

## Result

EX-291 closes as a no-production-change semantic audit.
