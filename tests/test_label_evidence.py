"""Tests for the cached FDA-label evidence layer.

These run against pharmaguard/label_evidence.json (built offline from the public
openFDA drug label API), so they never touch the network.
"""

import unittest

from pharmaguard.engine import ClinicalSafetyEngine
from pharmaguard.interactions import (
    INTERACTION_RULES,
    KNOWLEDGE_BASE_META,
    LABEL_EVIDENCE,
)

VALID_TIERS = {"direct", "class", "not_found"}


class TestLabelEvidenceCache(unittest.TestCase):
    def test_every_pairwise_rule_has_an_evidence_record(self):
        rule_ids = {f"{r['pair'][0]}+{r['pair'][1]}" for r in INTERACTION_RULES}
        self.assertEqual(rule_ids, set(LABEL_EVIDENCE["rules"]))

    def test_tiers_are_valid_and_counts_add_up(self):
        tiers = [v["tier"] for v in LABEL_EVIDENCE["rules"].values()]
        self.assertTrue(set(tiers) <= VALID_TIERS)
        counts = LABEL_EVIDENCE["counts"]
        for tier in VALID_TIERS:
            self.assertEqual(counts[tier], tiers.count(tier))
        self.assertEqual(sum(counts.values()), len(INTERACTION_RULES))

    def test_matches_carry_provenance_and_quote_the_matched_term(self):
        for rule_id, ev in LABEL_EVIDENCE["rules"].items():
            if ev["tier"] == "not_found":
                continue
            with self.subTest(rule=rule_id):
                self.assertTrue(ev["set_id"])
                self.assertTrue(ev["effective_time"])
                self.assertIn(ev["set_id"], ev["dailymed_url"])
                self.assertIn(ev["matched"].lower(), ev["excerpt"].lower())

    def test_known_label_statements_are_direct(self):
        # Each of these is verified against the cached label excerpt.
        expected = {
            "warfarin+ibuprofen": "warfarin",
            "simvastatin+clarithromycin": "simvastatin",
            "clopidogrel+omeprazole": "clopidogrel",
            "ciprofloxacin+tizanidine": "ciprofloxacin",
            "sildenafil+nitroglycerin": "sildenafil",
        }
        for rule_id, label_of in expected.items():
            with self.subTest(rule=rule_id):
                ev = LABEL_EVIDENCE["rules"][rule_id]
                self.assertEqual(ev["tier"], "direct")
                self.assertEqual(ev["label_of"], label_of)

    def test_reviewed_false_positives_are_not_counted_as_corroboration(self):
        for rule_id in ("glipizide+insulin", "clopidogrel+aspirin"):
            with self.subTest(rule=rule_id):
                ev = LABEL_EVIDENCE["rules"][rule_id]
                self.assertEqual(ev["tier"], "not_found")
                self.assertTrue(ev.get("review_note"))

    def test_meta_exposes_summary(self):
        summary = KNOWLEDGE_BASE_META["label_evidence"]
        self.assertEqual(summary["pairwise_rules"], len(INTERACTION_RULES))
        self.assertEqual(summary["counts"], LABEL_EVIDENCE["counts"])


class TestEvidenceInAudit(unittest.TestCase):
    def setUp(self):
        self.engine = ClinicalSafetyEngine()

    def test_audit_alerts_include_evidence_without_changing_severity(self):
        result = self.engine.audit_regimen(["warfarin", "ibuprofen", "levothyroxine", "omeprazole"])
        by_id = {i["rule_id"]: i for i in result["interactions"]}
        self.assertEqual(by_id["warfarin+ibuprofen"]["label_evidence"]["tier"], "direct")
        self.assertEqual(by_id["warfarin+ibuprofen"]["severity"], "CRITICAL")
        # A rule with no label mention keeps its curated severity.
        missing = by_id["levothyroxine+omeprazole"]
        self.assertEqual(missing["label_evidence"]["tier"], "not_found")
        self.assertTrue(missing["severity"])


if __name__ == "__main__":
    unittest.main()
