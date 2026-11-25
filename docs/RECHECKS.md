# Recheck validation

Install the pinned dependency with `python3 -m pip install -r requirements-test.txt`.
Run `python3 scripts/check_rechecks.py path/to/recheck-schedule.yml`.
The historical default remains the example in `templates/`; pass your real
schedule explicitly. The example dates are not current evidence.

Exit 0 means no active holds, **not** release approval. Exit 1 means a valid
schedule has due, overdue, changed or incorrectly timed-for-use observations.
Exit 2 means invalid input, including missing/unreadable files, malformed YAML,
wrong shapes, missing fields, duplicate IDs and invalid date relationships.

Dates use YYYY-MM-DD; quoted strings and YAML calendar dates are supported,
but timestamps are not. `checked_on` cannot be in the future and `recheck_by`
must be later than `checked_on`. The current date defaults to UTC; `--today`
is for explicit historical evaluation or tests, not bypassing expiry.

An explicit `rechecks: []` is invalid unless `--allow-empty` is passed. Empty
files, `{}` and missing/null lists remain invalid even with that option. A
successful empty run states that no evidence was checked. This option is for
projects intentionally tracking no observations, not evidence of coverage.

`--artefact` selects holds for an exact artefact value; no match is invalid.
All entries still undergo structural/date validation, even outside that filter.
`withdrawn` means the observation is intentionally retired from tracking:
validate it but do not apply expiry holds. It does not mean the old claim is
safe to reuse. Record withdrawals honestly; neither this script nor AIKO can
authenticate the underlying decision. Unlike AIKO's report gate, which holds
on withdrawn observations still attached to a report, this schedule omits them
from its active inventory.

`--warn-days N` must be nonnegative; near-due warnings do not themselves hold.
Due today is already a hold. Negative values and invalid `--today` arguments
exit 2 without a traceback. The gate does not modify, publish or schedule work.

## Automatic verification

`.github/workflows/recheck.yml` checks the root `recheck-schedule.yml`, not the
historical examples in `templates/`. It runs on pull requests, pushes to `main`,
manual dispatch and a daily schedule at **07:17 UTC** (08:17 Brussels winter time,
09:17 summer time). Scheduled runs require the workflow on the default branch;
GitHub may delay scheduled jobs, so this is not an exact-time reminder service.

The workflow has read-only repository permissions and never publishes, changes
the schedule, refreshes sources or sends custom messages. It only evaluates
recorded dates and statuses. Failed runs appear in Actions; notification delivery
depends on each account's GitHub settings.

This framework repository starts with an explicit empty root schedule and invokes
`--allow-empty`. The successful output says **No active verifications scheduled;
no evidence was checked.** Missing or malformed root files still fail. Projects
that require at least one observation should remove `--allow-empty`. Neither
mode can detect an observation omitted from the inventory. Review additions,
removals and withdrawals as changes to the project's evidence coverage.

### Adoption and enforcement

1. Replace the root empty list with your real observations using the template's
   fields. Do not copy its expired sample dates as live evidence.
2. Run the workflow manually after merge and inspect its log. Test deadlines
   locally with `--today`; the automatic job uses the actual UTC date.
3. Have a repository administrator make the `sieve-recheck` job a required check
   in the applicable branch rules. This PR does not change those settings.
4. For deployment or publication, run the same validator against the reviewed
   schedule immediately before the action and stop on any nonzero exit code.
   A prior successful PR check does not remain fresh indefinitely, and a daily
   failure does not by itself cancel or block a separate release workflow.

On a hold, the owner reopens the evidence source, performs the real check and
records the resulting dates/status through review. Do not advance dates just to
make CI pass. If evidence changed, fix or withdraw the dependent claim as needed.
