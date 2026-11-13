# RAMI — Review, Act, Measure, Improve

**Status: experimental practice, version 0.1.0.**

RAMI turns review findings into bounded, measured improvements. It supports
SIEVE's corollary: a low acceptance rate is a problem to fix upstream, not an
instruction to spend ever more human time reviewing rejects.

- DAHNIN governs producing one bounded change.
- AIKO records that change's evidence, checks and human-review status.
- SIEVE governs review capacity and the freshness of evidence.
- RAMI records what was learned, what changed and whether it actually helped.

RAMI adds no new law, approval authority or automated release gate. A proposed
fix is not a demonstrated improvement. A measured improvement is not permission
to publish. Use the existing human-review and authorization requirements.

## Start a register

Copy [templates/rami-register.md](../templates/rami-register.md) into the work's
normal evidence location. Use one entry per problem, with a stable ID and an
accountable owner. The template has an index and a repeatable entry; keep enough
detail for another person to reproduce the comparison without guessing.

The [complete synthetic example](../examples/rami/reminder-reliability.md)
shows a proposed fix that introduces a regression, followed by a revised fix
and a narrowly scoped decision. Its results and people are fictional; it is not
evidence about any model or the current SIEVE skill.

## R — Review

Record the actual failure and its consequence, with the artefact revision,
source transcript or test log, reviewer and date. Separate observation from
hypothesis: an unexpected result does not establish its cause. Link existing
AIKO reports, evaluation records or debt items instead of copying their evidence.
If evidence is unavailable, leave the finding unverified and identify what is
needed. Never invent a baseline to justify an already preferred solution.

## A — Act

Choose one bounded intervention: a skill instruction, generation step, check,
review surface or task boundary. Pin the baseline and candidate revisions and
state the hypothesis. Define success and regression criteria **before** rerunning.
Record the accountable owner, permitted actions and rollback or abandonment plan.
RAMI does not authorize changing access, sending messages or publishing work.

## M — Measure

Use comparable inputs, rubric, model/version, settings, tools and loading method.
Record actual run times separately from fixed scenario dates. Preserve complete
outputs and unsuccessful attempts. If a comparison changes several variables,
label it non-comparable and rerun; do not attribute the difference to the fix.
For nondeterministic models, plan repeated fresh trials and report variability.
One successful answer supports only a narrow observation, not general reliability.

Record each criterion and regression result, not just the aggregate. Follow the
[evaluation protocol](../evaluations/sieve/README.md) for assistant trials:
`not_run`, `invalid_run` and `unclear` are not passes. A case passes only when all
its criteria pass. For pass rates, divide passes by valid attempted cases,
including unclear cases in that denominator; separately list invalid and unrun
counts. Do not confuse model evaluation with repository unit-test success.

If the success criteria are not met, keep the failed candidate and its evidence
in the record. Revise or reject it. Do not silently replace the baseline, omit a
regression, backdate evidence or weaken the rubric to manufacture improvement.

## I — Improve

A named human reviews the evidence and records one decision: adopt within a
stated scope, revise, reject or defer. Until that happens, the decision is
pending. An AI can prepare the register, not authenticate or supply its own
human approval. High-consequence changes retain the independent-review
requirements described in [AIKO](AIKO.md).

For adoption, record the actual integrated revision or leave integration pending.
State remaining limitations, a rollback trigger, an owner and a recheck deadline.
Link a real scheduling mechanism when one exists; a proposed reminder is not a
scheduled job. A decision may approve a limited experiment while general rollout
remains held. If no follow-up is needed, explain why rather than leaving it blank.

## Status and closure

Use `open`, `candidate`, `measured`, `adopted`, `rejected` or `deferred` as manual
tracking labels. `measured` means a comparison exists, not that it succeeded.
Use `adopted` only when a human decision and the scoped integration are recorded.
If a regression appears after adoption, reopen the entry and link the new evidence.
A rejected candidate stays in history even when another candidate is adopted.

Keep human decision, integration and follow-up scheduling in separate fields.
Pending review, missing evidence or unscheduled required follow-up must remain
visible. A closed register entry is neither compliance certification nor a
substitute for examining the underlying artefact. No script enforces these
labels in this documentation-only version.
