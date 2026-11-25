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
