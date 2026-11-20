#!/usr/bin/env python3
"""Validate recorded JD review judgments, artifact hashes, and readiness arithmetic.

This does not read a JD semantically, detect confidential information, or predict
hiring outcomes. A reviewer must supply evidence-backed ratings and gate results.
Python standard library only. Artifact paths are relative to the review JSON.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

CATEGORIES = {
    'must_have', 'responsibilities', 'preferred', 'ownership_outcomes',
    'communication', 'completeness',
}
GATES = {
    'facts', 'privacy', 'editorial', 'language_parity', 'target_identity',
    'rendering', 'submission',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, minimum, maximum):
    return (type(value) in (int, float) and math.isfinite(value)
            and minimum <= value <= maximum)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def sha256(value):
    return hashlib.sha256(value).hexdigest()


def hash_string(value):
    return (isinstance(value, str) and len(value) == 64
            and all(c in '0123456789abcdef' for c in value))


def unique_rows(rows, key, label):
    require(isinstance(rows, list), f'{label} must be a list')
    result = {}
    for row in rows:
        require(isinstance(row, dict) and text(row.get(key)), f'Invalid {label} entry')
        require(row[key] not in result, f'Duplicate {label} identifier')
        result[row[key]] = row
    return result


def evidence_record(row, label):
    require(text(row.get('reason')), f'{label}: reason is required')
    evidence = row.get('evidence')
    require(isinstance(evidence, list) and evidence and all(text(x) for x in evidence),
            f'{label}: evidence locations or unverified scope are required')


def validate_plan(plan):
    require(plan.get('schema_version') == 1, 'Unsupported criteria schema')
    require(text(plan.get('criteria_id')), 'criteria_id is required')
    jd = plan.get('jd', {})
    require(all(text(jd.get(k)) for k in ['company', 'role', 'source']),
            'JD company, role, and source are required')
    require(hash_string(jd.get('snapshot_sha256')), 'JD snapshot SHA-256 is required')
    docs = unique_rows(plan.get('documents'), 'id', 'planned document')
    require(docs, 'At least one planned document is required')
    for doc in docs.values():
        require(doc.get('kind') in {'resume', 'portfolio'}, 'Invalid document kind')
        require(doc.get('language') in {'ko', 'en'}, 'Document language must be ko or en')
    formats = plan.get('formats')
    require(isinstance(formats, list) and formats and len(formats) == len(set(formats))
            and set(formats) <= {'html', 'pdf'} and 'html' in formats,
            'formats must include html and may include pdf')
    require(number(plan.get('threshold'), 1, 100), 'threshold must be within 1..100')
    floors = plan.get('category_floors')
    require(isinstance(floors, dict) and set(floors) == {'must_have', 'responsibilities'},
            'Both must_have and responsibilities category floors are required')
    require(all(number(x, 1, 100) for x in floors.values()), 'Invalid category floor')
    criteria = unique_rows(plan.get('criteria'), 'id', 'criterion')
    require(criteria, 'At least one criterion is required')
    for row in criteria.values():
        require(row.get('category') in CATEGORIES, 'Invalid criterion category')
        require(number(row.get('weight'), 0.000001, 100), 'Criterion weight must be positive')
        require(type(row.get('min_level')) is int and 1 <= row['min_level'] <= 4,
                'min_level must be an integer in 1..4')
        require(row.get('source_type') in {'explicit', 'inferred'}, 'Invalid source_type')
        require(text(row.get('jd_ref')) and text(row.get('requirement')),
                'Criterion JD reference and requirement are required')
        require(type(row.get('critical')) is bool, 'critical must be boolean')
        if row['critical']:
            require(row['category'] == 'must_have' and row['source_type'] == 'explicit',
                    'Only explicit must-have eligibility may be critical')
            require(row['min_level'] >= 3, 'Critical criteria need direct document evidence (min_level >= 3)')
        acceptance = row.get('acceptance')
        require(isinstance(acceptance, dict) and acceptance
                and set(acceptance) <= {'resume', 'portfolio'}
                and all(text(x) for x in acceptance.values()),
                'Document-specific acceptance text is required')
        require(any(d['kind'] in acceptance for d in docs.values()),
                'A criterion must apply to a planned document')
    require(abs(sum(c['weight'] for c in criteria.values()) - 100) < 0.00001,
            'Criterion weights must total 100')
    for doc in docs.values():
        categories = {c['category'] for c in criteria.values() if doc['kind'] in c['acceptance']}
        require({'must_have', 'responsibilities'} <= categories,
                'Each document needs must_have and responsibilities criteria')
    return docs, criteria


def calculate(plan, review, criteria_hash):
    """Calculate from explicit judgments. Does not itself verify file bytes."""
    docs, criteria = validate_plan(plan)
    require(review.get('schema_version') == 1, 'Unsupported review schema')
    require(review.get('criteria_id') == plan['criteria_id'], 'Criteria ID mismatch')
    require(review.get('criteria_sha256') == criteria_hash, 'Frozen criteria hash mismatch')
    reviewed_docs = unique_rows(review.get('documents'), 'id', 'reviewed document')
    require(set(reviewed_docs) == set(docs), 'Reviewed document scope must match frozen plan')
    expected = {(doc_id, cid) for doc_id, doc in docs.items()
                for cid, c in criteria.items() if doc['kind'] in c['acceptance']}
    ratings = {}
    require(isinstance(review.get('ratings'), list), 'ratings must be a list')
    for row in review['ratings']:
        key = (row.get('document_id'), row.get('criterion_id'))
        require(key in expected and key not in ratings, 'Unexpected or duplicate rating')
        require(type(row.get('level')) is int and 0 <= row['level'] <= 4,
                'Rating level must be an integer in 0..4')
        require(text(row.get('reason')), 'Each rating needs a reason')
        for field in ['document_evidence', 'source_evidence']:
            refs = row.get(field)
            require(isinstance(refs, list) and refs and all(text(x) for x in refs),
                    'Each rating needs document and source evidence locations')
        ratings[key] = row
    require(set(ratings) == expected, 'All document/criterion ratings are required')

    gates = review.get('gates')
    require(isinstance(gates, dict) and set(gates) == GATES, 'All seven gates are required')
    for name, gate in gates.items():
        require(gate.get('status') in {'pass', 'fail', 'unknown', 'na'}, 'Invalid gate status')
        evidence_record(gate, name)
        if gate['status'] == 'na':
            require(name == 'language_parity'
                    and len({d['language'] for d in docs.values()}) == 1,
                    'Only single-language parity may be na')
    critical = {cid for cid, c in criteria.items() if c['critical']}
    eligibility = unique_rows(review.get('critical_requirements'), 'criterion_id', 'eligibility')
    require(set(eligibility) == critical, 'All critical requirements need eligibility judgments')
    for item in eligibility.values():
        require(item.get('status') in {'pass', 'fail', 'unknown'}, 'Invalid eligibility status')
        evidence_record(item, 'eligibility')

    results, format_gaps, critical_document_gaps = {}, [], []
    for doc_id, doc in docs.items():
        artifacts = unique_rows(reviewed_docs[doc_id].get('artifacts'), 'format', 'artifact format')
        require(set(artifacts) <= set(plan['formats']), 'Unexpected artifact format')
        for fmt, artifact in artifacts.items():
            require(text(artifact.get('path')) and hash_string(artifact.get('sha256')),
                    'Artifact path and SHA-256 are required')
            require(Path(artifact['path']).suffix.lower() == '.' + fmt, 'Artifact extension mismatch')
        if set(artifacts) != set(plan['formats']):
            format_gaps.append(doc_id)
        sums = {}
        targets = []
        for cid, c in criteria.items():
            if (doc_id, cid) not in ratings:
                continue
            level = ratings[(doc_id, cid)]['level']
            bucket = sums.setdefault(c['category'], [0.0, 0.0])
            bucket[0] += c['weight'] * level / 4
            bucket[1] += c['weight']
            if level < c['min_level']:
                targets.append(cid)
                if c['critical']:
                    critical_document_gaps.append({'document_id': doc_id, 'criterion_id': cid})
        score = 100 * sum(v[0] for v in sums.values()) / sum(v[1] for v in sums.values())
        percentages = {k: 100 * v[0] / v[1] for k, v in sums.items()}
        floor_ok = all(percentages[k] >= value for k, value in plan['category_floors'].items())
        results[doc_id] = {
            'score': round(score, 2),
            'categories': {k: round(v, 2) for k, v in percentages.items()},
            'below_target_criteria': targets,
            'score_conditions_met': score >= plan['threshold'] and floor_ok,
        }
    gate_fail = [k for k, v in gates.items() if v['status'] == 'fail']
    gate_unknown = [k for k, v in gates.items() if v['status'] == 'unknown']
    eligibility_fail = [k for k, v in eligibility.items() if v['status'] == 'fail']
    eligibility_unknown = [k for k, v in eligibility.items() if v['status'] == 'unknown']
    artifact_ready = (all(r['score_conditions_met'] for r in results.values())
                      and not gate_fail and not gate_unknown and not format_gaps
                      and not critical_document_gaps)
    accepted = artifact_ready and not eligibility_fail and not eligibility_unknown
    if eligibility_fail:
        decision = 'FIT_GAP'
    elif gate_fail or format_gaps or critical_document_gaps:
        decision = 'REVISE'
    elif eligibility_unknown or gate_unknown:
        decision = 'NEEDS_EVIDENCE'
    else:
        decision = 'ACCEPT' if accepted else 'REVISE'
    return {
        'criteria_id': plan['criteria_id'], 'criteria_sha256': criteria_hash,
        'score_meaning': 'Document fit and readiness, not hiring probability',
        'summary_score': min(r['score'] for r in results.values()),
        'summary_method': 'lowest_document_score', 'documents': results,
        'decision': decision, 'artifact_ready': artifact_ready, 'acceptance_met': accepted,
        'failed_gates': gate_fail, 'unknown_gates': gate_unknown,
        'failed_eligibility': eligibility_fail, 'unknown_eligibility': eligibility_unknown,
        'missing_artifact_formats': format_gaps,
        'critical_document_gaps': critical_document_gaps,
        'judgment_boundary': 'Recorded reviewer judgments; content, privacy, and visual QA are not automated by this calculator',
    }


def verify_artifacts(review, directory):
    for doc in review['documents']:
        for artifact in doc['artifacts']:
            file = (directory / artifact['path']).resolve()
            require(file.is_file(), 'A reviewed artifact is missing')
            require(sha256(file.read_bytes()) == artifact['sha256'],
                    'Artifact bytes changed after review; rerun affected checks')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('criteria', type=Path)
    parser.add_argument('review', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            require(args.output.resolve() not in {args.criteria.resolve(), args.review.resolve()},
                    'Output must not replace review inputs')
            require(not args.output.exists(), 'Output exists; choose a new version')
        raw = args.criteria.read_bytes()
        plan = json.loads(raw)
        review = json.loads(args.review.read_bytes())
        result = calculate(plan, review, sha256(raw))
        verify_artifacts(review, args.review.resolve().parent)
        payload = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('x', encoding='utf-8') as stream:
                stream.write(payload)
            print('Saved score report:', args.output)
        else:
            print(payload, end='')
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        print('Review validation failed:', error, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
