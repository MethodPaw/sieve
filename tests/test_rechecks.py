"""Regression coverage for the schedule gate and CLI exit contract."""
import copy
import datetime as dt
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/check_rechecks.py'
spec = importlib.util.spec_from_file_location('rechecks', SCRIPT)
rechecks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rechecks)
TODAY = dt.date(2026, 11, 25)


def fixture():
    return {'rechecks': [dict(id='one', artefact='doc', claim='price', source='fixture',
        checked_on='2026-11-24', recheck_by='2026-11-28', owner='owner', status='confirmed')]}


class RecheckTests(unittest.TestCase):
    def test_invalid_shapes_and_missing_fields(self):
        for data in (None, [], {}, {'rechecks': None}, {'rechecks': {}},
                     {'rechecks': [42]}, {'rechecks': [{}]}):
            with self.subTest(data=data):
                self.assertTrue(rechecks.evaluate(data, TODAY)[0])

    def test_empty_requires_opt_in_but_missing_list_never_passes(self):
        self.assertTrue(rechecks.evaluate({'rechecks': []}, TODAY)[0])
        self.assertFalse(rechecks.evaluate({'rechecks': []}, TODAY, allow_empty=True)[0])
        self.assertTrue(rechecks.evaluate({}, TODAY, allow_empty=True)[0])

    def test_dates_and_types(self):
        for field, value in [('checked_on', '2026-11-26'), ('checked_on', '2026-02-30'),
                ('checked_on', dt.datetime(2026, 11, 24)), ('checked_on', '20261124'),
                ('recheck_by', '2026-11-24'), ('recheck_by', '2026-11-23'),
                ('use_on', None), ('owner', ' '), ('status', []), ('id', 12)]:
            with self.subTest(field=field, value=value):
                data = fixture()
                data['rechecks'][0][field] = value
                self.assertTrue(rechecks.evaluate(data, TODAY)[0])

    def test_yaml_date_objects_accepted(self):
        data = fixture()
        data['rechecks'][0]['checked_on'] = dt.date(2026, 11, 24)
        self.assertFalse(rechecks.evaluate(data, TODAY)[0])

    def test_duplicate_ids(self):
        data = fixture()
        data['rechecks'].append(copy.deepcopy(data['rechecks'][0]))
        self.assertTrue(rechecks.evaluate(data, TODAY)[0])

    def test_due_overdue_changed_and_use_boundary_hold(self):
        for updates in ({'recheck_by': '2026-11-25'},
                        {'checked_on': '2026-11-20', 'recheck_by': '2026-11-24'},
                        {'status': 'changed'}, {'use_on': '2026-11-28'}):
            with self.subTest(updates=updates):
                data = fixture()
                data['rechecks'][0].update(updates)
                errors, holds, _, checked = rechecks.evaluate(data, TODAY)
                self.assertFalse(errors)
                self.assertEqual((len(holds), checked), (1, 1))

    def test_warning_boundary_does_not_hold(self):
        errors, holds, warnings, checked = rechecks.evaluate(fixture(), TODAY)
        self.assertEqual((errors, holds, len(warnings), checked), ([], [], 1, 1))
        self.assertFalse(rechecks.evaluate(fixture(), TODAY, warn_days=2)[2])

    def test_filter_cannot_hide_invalid_entries_or_no_match(self):
        self.assertTrue(rechecks.evaluate(fixture(), TODAY, artefact='missing')[0])
        data = fixture()
        data['rechecks'].append({'id': 'broken', 'artefact': 'other'})
        self.assertTrue(rechecks.evaluate(data, TODAY, artefact='doc')[0])

    def test_withdrawn_skips_holds_but_not_validation(self):
        data = fixture()
        data['rechecks'][0].update(status='withdrawn', recheck_by='2026-11-25')
        self.assertEqual(rechecks.evaluate(data, TODAY), ([], [], [], 0))
        data['rechecks'][0]['checked_on'] = 'bad'
        self.assertTrue(rechecks.evaluate(data, TODAY)[0])

    def test_cli_inputs_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'schedule.yml'
            def run(*args):
                return subprocess.run([sys.executable, str(SCRIPT), str(path), *args],
                    capture_output=True, text=True)
            self.assertEqual(run().returncode, 2)
            for body in ('[bad', '{}', 'rechecks: [42]', 'checked_on: 2026-02-30', ''):
                path.write_text(body)
                result = run()
                self.assertEqual(result.returncode, 2)
                self.assertNotIn('Traceback', result.stdout + result.stderr)
            path.write_text('rechecks: []')
            self.assertEqual(run('--allow-empty').returncode, 0)
            self.assertEqual(run('--today', 'bad').returncode, 2)
            self.assertEqual(run('--warn-days', '-1').returncode, 2)
            path.write_text(rechecks.yaml.safe_dump(fixture()))
            self.assertEqual(run('--today', '2026-11-25').returncode, 0)
            self.assertEqual(run('--today', '2026-11-28').returncode, 1)
