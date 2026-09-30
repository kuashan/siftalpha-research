# XMA Falsification v2 — GitHub Actions Execution Diagnostic v1

Status: **REPOSITORY/ACCOUNT EXECUTION GATE CONFIRMED; EXACT BILLING ANNOTATION NOT READABLE VIA CONNECTOR**

Date: 2026-09-28

## Evidence

The v2 workflow was reduced to:
- pure shell checkout;
- no marketplace `uses:` actions;
- direct Python/pip commands.

It still fails before any step starts.

Observed v2 jobs repeatedly return:
- `conclusion = failure`
- `steps = null`
- `logs_url = null`

This is not isolated to the new v2 workflow.

Existing independent scheduled workflow:

`E043 5m Paper Engine`

also shows the same pre-step failure signature on at least:

- run 36363343725 / job 108744752556
- run 36354238235 / job 108718642867

Both return:
- completed/failure
- `steps = null`
- `logs_url = null`

Therefore the v2 Python code and v2 workflow YAML are not a sufficient explanation.

## Classification

`GITHUB_HOSTED_ACTIONS_EXECUTION_GATE`

The current GitHub connector exposes that the failed check runs have annotations, but does not expose the annotation text.

Public GitHub reports in September 2026 document an identical zero-step failure pattern when GitHub-hosted Actions are blocked by account billing/spending/payment entitlement gates.

Because the private annotation text is unavailable here, the narrower label:

`LIKELY_BILLING_OR_HOSTED_RUNNER_ENTITLEMENT_GATE`

is evidence-based but not treated as confirmed.

## Repository action

No additional changes to scientific code are authorized merely to make hosted Actions start.

Two recovery paths are valid:

1. restore GitHub-hosted Actions by resolving the account/billing/entitlement gate; or
2. register an approved self-hosted runner and execute the same deterministic workflow there.

The test result must be attributed to the execution environment actually used.
