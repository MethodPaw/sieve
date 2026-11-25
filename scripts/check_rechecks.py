#!/usr/bin/env python3
"""Validate a SIEVE recheck schedule and hold expired observations.

Exit codes: 0 = no holds (not release approval); 1 = use held;
2 = invalid input. Empty schedules require explicit --allow-empty.
"""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML is required: pip install -r requirements-test.txt\n")
    sys.exit(2)

REQUIRED = ("id", "artefact", "claim", "source", "checked_on", "recheck_by", "owner", "status")
STATUSES = {"open", "confirmed", "changed", "withdrawn"}


def as_date(value, field, label, errors):
    if type(value) is dt.date:
        return value
    if isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            pass
    errors.append(f"{label}: {field} must be a YYYY-MM-DD date")
    return None


def evaluate(data, today, warn_days=3, artefact=None, allow_empty=False):
    errors, holds, warnings = [], [], []
    if not isinstance(data, dict) or not isinstance(data.get("rechecks"), list):
        return ["schedule must be an object containing a rechecks list"], holds, warnings, 0
    entries = data["rechecks"]
    if not entries and not allow_empty:
        errors.append("empty rechecks list; use --allow-empty only when intentional")
    seen = set()
    matched = checked = 0
    for index, entry in enumerate(entries, 1):
        label = f"entry {index}"
        if not isinstance(entry, dict):
            errors.append(f"{label}: expected object")
            continue
        start_errors = len(errors)
        for field in REQUIRED:
            if field not in entry:
                errors.append(f"{label}: missing {field}")
            elif field not in ("checked_on", "recheck_by") and (
                    not isinstance(entry[field], str) or not entry[field].strip()):
                errors.append(f"{label}: {field} must be a nonempty string")
        ident = entry.get("id")
        if isinstance(ident, str):
            ident = ident.strip()
            if ident in seen:
                errors.append(f"{label}: duplicate id {ident!r}")
            seen.add(ident)
        status = entry.get("status")
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(f"{label}: status must be one of {sorted(STATUSES)}")
        checked_on = as_date(entry.get("checked_on"), "checked_on", label, errors)
        recheck_by = as_date(entry.get("recheck_by"), "recheck_by", label, errors)
        use_on = as_date(entry["use_on"], "use_on", label, errors) if "use_on" in entry else None
        if checked_on and checked_on > today:
            errors.append(f"{label}: checked_on is in the future")
        if checked_on and recheck_by and recheck_by <= checked_on:
            errors.append(f"{label}: recheck_by must be after checked_on")
        # Validate the whole schedule, including filtered and withdrawn entries.
        if len(errors) != start_errors:
            continue
        if artefact is not None and entry["artefact"] != artefact:
            continue
        matched += 1
        if status == "withdrawn":
            continue
        checked += 1
        label = f"{ident} [{entry['artefact']}] owner={entry['owner']}"
        reasons = []
        if status == "changed":
            reasons.append("observation changed; fix the artefact")
        if use_on and recheck_by >= use_on:
            reasons.append("re-check must be before planned use")
        if recheck_by <= today:
            reasons.append("re-check due today or overdue")
        if reasons:
            holds.append(f"{label}: {'; '.join(reasons)}")
        elif (recheck_by - today).days <= warn_days:
            warnings.append(f"{label}: re-check by {recheck_by}")
    if artefact is not None and not matched:
        errors.append(f"no valid entries match artefact {artefact!r}")
    return errors, holds, warnings, checked


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schedule", nargs="?", default="templates/recheck-schedule.yml")
    parser.add_argument("--today", help="YYYY-MM-DD override for repeatable tests")
    parser.add_argument("--warn-days", type=int, default=3)
    parser.add_argument("--artefact")
    parser.add_argument("--allow-empty", action="store_true")
    args = parser.parse_args(argv)
    if args.warn_days < 0:
        parser.error("--warn-days must not be negative")
    date_errors = []
    today = as_date(args.today, "--today", "arguments", date_errors) if args.today is not None else dt.datetime.now(dt.timezone.utc).date()
    if date_errors:
        parser.error(date_errors[0])
    try:
        data = yaml.safe_load(Path(args.schedule).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        print(f"INVALID schedule: {exc}", file=sys.stderr)
        return 2
    errors, holds, warnings, checked = evaluate(data, today, args.warn_days, args.artefact, args.allow_empty)
    for prefix, reasons in (("INVALID", errors), ("HOLD", holds), ("SOON", warnings)):
        for reason in reasons:
            print(f"{prefix} {reason}")
    if errors:
        return 2
    if holds:
        print(f"{len(holds)} of {checked} active verification(s) held.")
        return 1
    if checked == 0:
        print("No active verifications scheduled; no evidence was checked.")
    else:
        print(f"{checked} active verification(s) in date; not release approval.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
