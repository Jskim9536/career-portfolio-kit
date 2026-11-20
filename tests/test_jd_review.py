"""Synthetic reviews exercise scoring boundaries, frozen scope, and file integrity."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/jd-application-review/scripts/score_review.py'
SPEC = importlib.util.spec_from_file_location('jd_score', SCRIPT)
SCORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORE)


def fixture():
    categories = [('M1', 'must_have', 35), ('R1', 'responsibilities', 25),
                  ('P1', 'preferred', 10), ('O1', 'ownership_outcomes', 15),
                  ('C1', 'communication', 10), ('D1', 'completeness', 5)]
    plan = {
        'schema_version': 1, 'criteria_id': 'synthetic-jd-v1',
        'jd': {'company': 'Synthetic organization', 'role': 'Test role',
               'source': 'Synthetic JD fixture', 'snapshot_sha256': SCORE.sha256(b'Synthetic JD')},
        'documents': [{'id': 'resume-ko', 'kind': 'resume', 'language': 'ko'},
                      {'id': 'resume-en', 'kind': 'resume', 'language': 'en'}],
        'formats': ['html', 'pdf'], 'threshold': 80,
        'category_floors': {'must_have': 75, 'responsibilities': 75},
        'criteria': [
            {'id': cid, 'category': category, 'weight': weight,
             'source_type': 'explicit' if cid == 'M1' else 'inferred',
             'jd_ref': 'Synthetic source section', 'requirement': 'Synthetic criterion',
             'critical': cid == 'M1', 'min_level': 3,
             'acceptance': {'resume': 'Show evidence of scope and result'}}
            for cid, category, weight in categories],
    }
    review = {
        'schema_version': 1, 'criteria_id': plan['criteria_id'],
        'criteria_sha256': SCORE.sha256(json.dumps(plan).encode()),
        'documents': [
            {'id': d['id'], 'artifacts': [
                {'format': fmt, 'path': d['id'] + '.' + fmt,
                 'sha256': SCORE.sha256((d['id'] + fmt).encode())}
                for fmt in ['html', 'pdf']]}
            for d in plan['documents']],
        'ratings': [
            {'document_id': d['id'], 'criterion_id': cid, 'level': 4,
             'reason': 'Synthetic direct evidence',
             'document_evidence': ['Synthetic document location'],
             'source_evidence': ['Synthetic source location']}
            for d in plan['documents'] for cid, _, _ in categories],
        'critical_requirements': [
            {'criterion_id': 'M1', 'status': 'pass', 'reason': 'Synthetic eligibility',
             'evidence': ['Synthetic source']}],
        'gates': {name: {'status': 'pass', 'reason': 'Synthetic recorded judgment',
                         'evidence': ['Synthetic checked scope']}
                  for name in SCORE.GATES},
    }
    return plan, review


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.plan, self.review = fixture()

    def calculate(self):
        return SCORE.calculate(self.plan, self.review, self.review['criteria_sha256'])

    def test_full_evidence_accepts(self):
        result = self.calculate()
        self.assertEqual(result['summary_score'], 100)
        self.assertEqual(result['decision'], 'ACCEPT')

    def test_low_must_have_cannot_hide_behind_high_total(self):
        self.review['ratings'][0]['level'] = 2
        result = self.calculate()
        self.assertEqual(result['documents']['resume-ko']['score'], 82.5)
        self.assertEqual(result['decision'], 'REVISE')

    def test_preferred_gap_is_not_mandatory(self):
        self.review['ratings'][2]['level'] = 0
        result = self.calculate()
        self.assertEqual(result['summary_score'], 90)
        self.assertEqual(result['decision'], 'ACCEPT')
        self.assertIn('P1', result['documents']['resume-ko']['below_target_criteria'])

    def test_low_weight_critical_document_gap_still_blocks(self):
        self.plan['criteria'][0]['weight'] = 5
        additional = copy.deepcopy(self.plan['criteria'][0])
        additional.update(id='M2', weight=30, critical=False)
        self.plan['criteria'].append(additional)
        for doc in self.plan['documents']:
            rating = copy.deepcopy(self.review['ratings'][0])
            rating.update(document_id=doc['id'], criterion_id='M2')
            self.review['ratings'].append(rating)
        self.review['ratings'][0]['level'] = 2
        result = self.calculate()
        self.assertEqual(result['summary_score'], 97.5)
        self.assertGreater(result['documents']['resume-ko']['categories']['must_have'], 75)
        self.assertEqual(result['decision'], 'REVISE')
        self.assertEqual(result['critical_document_gaps'], [{'document_id': 'resume-ko', 'criterion_id': 'M1'}])

    def test_weak_language_is_not_averaged_away(self):
        for rating in self.review['ratings']:
            if rating['document_id'] == 'resume-en':
                rating['level'] = 2
        result = self.calculate()
        self.assertEqual(result['summary_score'], 50)
        self.assertEqual(result['decision'], 'REVISE')

    def test_actual_eligibility_gap_is_separate_from_artifact(self):
        self.review['critical_requirements'][0]['status'] = 'fail'
        result = self.calculate()
        self.assertTrue(result['artifact_ready'])
        self.assertFalse(result['acceptance_met'])
        self.assertEqual(result['decision'], 'FIT_GAP')

    def test_unverified_eligibility_does_not_accept(self):
        self.review['critical_requirements'][0]['status'] = 'unknown'
        self.assertEqual(self.calculate()['decision'], 'NEEDS_EVIDENCE')

    def test_privacy_failure_blocks_perfect_score(self):
        self.review['gates']['privacy']['status'] = 'fail'
        result = self.calculate()
        self.assertEqual(result['summary_score'], 100)
        self.assertFalse(result['artifact_ready'])
        self.assertEqual(result['decision'], 'REVISE')

    def test_unverified_facts_do_not_accept(self):
        self.review['gates']['facts']['status'] = 'unknown'
        self.assertEqual(self.calculate()['decision'], 'NEEDS_EVIDENCE')

    def test_missing_pdf_cannot_accept_even_if_gate_claims_pass(self):
        self.review['documents'][0]['artifacts'].pop()
        result = self.calculate()
        self.assertEqual(result['decision'], 'REVISE')
        self.assertEqual(result['missing_artifact_formats'], ['resume-ko'])

    def test_frozen_criteria_hash_is_enforced(self):
        with self.assertRaises(ValueError):
            SCORE.calculate(self.plan, self.review, '0' * 64)

    def test_dropping_a_document_is_rejected(self):
        self.review['documents'].pop()
        with self.assertRaises(ValueError):
            self.calculate()

    def test_omitted_or_duplicate_ratings_are_rejected(self):
        for duplicate in [False, True]:
            with self.subTest(duplicate=duplicate):
                self.plan, self.review = fixture()
                if duplicate:
                    self.review['ratings'].append(copy.deepcopy(self.review['ratings'][0]))
                else:
                    self.review['ratings'].pop()
                with self.assertRaises(ValueError):
                    self.calculate()

    def test_missing_gate_or_critical_check_is_rejected(self):
        for field in ['gates', 'critical_requirements']:
            with self.subTest(field=field):
                self.plan, self.review = fixture()
                self.review[field].pop('privacy') if field == 'gates' else self.review[field].pop()
                with self.assertRaises(ValueError):
                    self.calculate()

    def test_invalid_levels_are_rejected(self):
        for level in [True, -1, 5, 2.5]:
            with self.subTest(level=level):
                self.review['ratings'][0]['level'] = level
                with self.assertRaises(ValueError):
                    self.calculate()

    def test_inferred_critical_requirement_is_rejected(self):
        self.plan['criteria'][0]['source_type'] = 'inferred'
        with self.assertRaises(ValueError):
            self.calculate()

    def test_invalid_weights_are_rejected(self):
        for weight in [0, float('nan'), 30]:
            with self.subTest(weight=weight):
                self.plan['criteria'][0]['weight'] = weight
                with self.assertRaises(ValueError):
                    self.calculate()

    def test_bilingual_parity_cannot_be_skipped(self):
        self.review['gates']['language_parity']['status'] = 'na'
        with self.assertRaises(ValueError):
            self.calculate()

    def test_single_language_parity_may_be_na(self):
        self.plan['documents'] = self.plan['documents'][:1]
        self.review['documents'] = self.review['documents'][:1]
        self.review['ratings'] = self.review['ratings'][:6]
        self.review['gates']['language_parity']['status'] = 'na'
        self.assertEqual(self.calculate()['decision'], 'ACCEPT')

    def test_same_criteria_can_measure_a_real_revision(self):
        self.review['ratings'][0]['level'] = 2
        before = self.calculate()
        self.review['ratings'][0].update(level=4, reason='Synthetic contribution clarified')
        after = self.calculate()
        self.assertEqual(before['decision'], 'REVISE')
        self.assertEqual(after['decision'], 'ACCEPT')
        self.assertEqual(before['criteria_sha256'], after['criteria_sha256'])

    def test_artifact_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for doc in self.review['documents']:
                for artifact in doc['artifacts']:
                    payload = (doc['id'] + artifact['format']).encode()
                    (root / artifact['path']).write_bytes(payload)
            SCORE.verify_artifacts(self.review, root)
            (root / self.review['documents'][0]['artifacts'][0]['path']).write_text('Changed')
            with self.assertRaises(ValueError):
                SCORE.verify_artifacts(self.review, root)

    def test_cli_checks_files_and_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for doc in self.review['documents']:
                for artifact in doc['artifacts']:
                    (root / artifact['path']).write_bytes((doc['id'] + artifact['format']).encode())
            criteria = root / 'criteria.json'
            criteria.write_text(json.dumps(self.plan))
            review = root / 'review.json'
            review.write_text(json.dumps(self.review))
            output = root / 'score.json'
            command = [sys.executable, str(SCRIPT), str(criteria), str(review), '--output', str(output)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue(json.loads(output.read_text())['acceptance_met'])
            original = output.read_bytes()
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(second.returncode, 2)
            self.assertEqual(output.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
