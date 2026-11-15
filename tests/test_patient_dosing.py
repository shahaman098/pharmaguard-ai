"""Tests for patient-specific kidney-function and age dosing checks.

Every threshold comes from pharmaguard/renal_evidence.json, built offline from
FDA labels with each quote verified word-for-word, so these run offline.
"""

import json
import re
import unittest

from pharmaguard.engine import ClinicalSafetyEngine, parse_patient
from pharmaguard.interactions import DRUG_REGISTRY, KNOWLEDGE_BASE_META, RENAL_RULES


def patient(age=None, egfr=None, crcl=None):
    return {"age": age, "egfr": egfr, "crcl": crcl}


class TestRenalRuleProvenance(unittest.TestCase):
    def test_every_rule_is_sourced_and_quotes_its_threshold(self):
        self.assertGreaterEqual(len(RENAL_RULES), 10)
        for rule in RENAL_RULES:
            with self.subTest(drug=rule["drug"], measure=rule["measure"]):
                self.assertIn(rule["drug"], DRUG_REGISTRY)
                self.assertIn(rule["measure"], {"egfr", "crcl", "age"})
                self.assertIn(rule["severity"], {"CRITICAL", "MODERATE"})
                self.assertTrue(rule["set_id"])
                self.assertIn(rule["set_id"], rule["dailymed_url"])
                self.assertRegex(rule["effective_time"], r"^\d{8}$")
                bounds = [rule[k] for k in ("lt", "le", "gt", "ge") if k in rule]
                self.assertTrue(bounds, "rule needs at least one bound")
                quoted = {int(n) for n in re.findall(r"\d+", rule["quote"])}
                self.assertTrue(
                    any(int(b) in quoted or int(b) - 1 in quoted for b in bounds),
                    f"quote does not contain any threshold {bounds}",
                )

    def test_meta_reports_patient_dosing_coverage(self):
        meta = KNOWLEDGE_BASE_META["patient_dosing"]
        self.assertEqual(meta["rule_count"], len(RENAL_RULES))
        self.assertIn("metformin", meta["drugs"])


class TestPatientChecks(unittest.TestCase):
    def setUp(self):
        self.engine = ClinicalSafetyEngine()

    def flags(self, drugs, **kwargs):
        result = self.engine.audit_regimen(drugs, patient=patient(**kwargs))
        return result, {(f["drug_key"], f["severity"]) for f in result["patient_checks"]["flags"]}

    def test_no_patient_leaves_output_unchanged(self):
        drugs = ["warfarin", "ibuprofen", "metformin"]
        baseline = self.engine.audit_regimen(drugs)
        self.assertNotIn("patient_checks", baseline)
        again = self.engine.audit_regimen(drugs, patient=None)
        self.assertEqual(json.dumps(baseline, sort_keys=True), json.dumps(again, sort_keys=True))

    def test_metformin_egfr_boundaries(self):
        cases = {29.9: "CRITICAL", 30: "MODERATE", 44: "MODERATE", 45: None, 90: None}
        for egfr, expected in cases.items():
            with self.subTest(egfr=egfr):
                _, flags = self.flags(["metformin"], egfr=egfr)
                if expected:
                    self.assertEqual(flags, {("metformin", expected)})
                else:
                    self.assertEqual(flags, set())

    def test_lithium_crcl_boundaries(self):
        cases = {29: "CRITICAL", 30: "MODERATE", 89: "MODERATE", 90: None}
        for crcl, expected in cases.items():
            with self.subTest(crcl=crcl):
                _, flags = self.flags(["lithium"], crcl=crcl)
                self.assertEqual(flags, {("lithium", expected)} if expected else set())

    def test_crcl_inclusive_and_exclusive_bounds(self):
        self.assertEqual(self.flags(["ciprofloxacin"], crcl=50)[1], {("ciprofloxacin", "MODERATE")})
        self.assertEqual(self.flags(["ciprofloxacin"], crcl=51)[1], set())
        self.assertEqual(self.flags(["levofloxacin"], crcl=50)[1], set())
        self.assertEqual(self.flags(["levofloxacin"], crcl=49)[1], {("levofloxacin", "MODERATE")})
        self.assertEqual(self.flags(["naproxen"], crcl=29)[1], {("naproxen", "CRITICAL")})
        self.assertEqual(self.flags(["naproxen"], crcl=30)[1], set())

    def test_age_rule(self):
        self.assertEqual(self.flags(["sildenafil"], age=66)[1], {("sildenafil", "MODERATE")})
        self.assertEqual(self.flags(["sildenafil"], age=65)[1], set())

    def test_eGFR_and_CrCl_are_not_interchangeable(self):
        # Lithium's label uses CrCl; an eGFR value alone must not satisfy it.
        result, flags = self.flags(["lithium", "metformin"], egfr=20)
        self.assertEqual(flags, {("metformin", "CRITICAL")})
        missing = result["patient_checks"]["not_checked"]
        self.assertEqual([(m["drug"], m["measure"]) for m in missing], [("Lithium", "crcl")])

    def test_blank_kidney_function_is_not_checked_never_normal(self):
        result, flags = self.flags(["metformin", "warfarin"], age=74)
        self.assertEqual(flags, set())
        self.assertEqual(
            [(m["drug"], m["measure"]) for m in result["patient_checks"]["not_checked"]],
            [("Metformin", "egfr")],
        )

    def test_flags_change_score_and_status(self):
        safe = self.engine.audit_regimen(["metformin"], patient=patient(egfr=80))
        unsafe = self.engine.audit_regimen(["metformin"], patient=patient(egfr=20))
        self.assertEqual(safe["critical_count"], 0)
        self.assertEqual(unsafe["critical_count"], 1)
        self.assertLess(unsafe["safety_score"], safe["safety_score"])
        self.assertEqual(unsafe["status_color"], "red")
        # The patient-facing advice must agree with the verdict, never say "no clashes".
        text = " ".join(unsafe["patient_summary"])
        self.assertIn("DANGER", text)
        self.assertNotIn("no known clashes", text)
        gap = self.engine.audit_regimen(["metformin"], patient=patient(age=70))
        self.assertTrue(any("NOT CHECKED" in a and "Metformin" in a for a in gap["patient_summary"]))

    def test_flag_carries_label_quote(self):
        result, _ = self.flags(["metformin"], egfr=20)
        evidence = result["patient_checks"]["flags"][0]["label_evidence"]
        self.assertIn("eGFR below 30", evidence["quote"])
        self.assertIn("dailymed", evidence["dailymed_url"])

    def test_sbar_lists_dosing_flags_and_gaps(self):
        result = self.engine.audit_regimen(["metformin", "lithium"], patient=patient(age=80, egfr=20))
        note = self.engine.generate_sbar_note(result, "Test Patient", 80)
        self.assertIn("Metformin contraindicated", note)
        self.assertIn("Kidney dosing for Lithium not checked", note)
        self.assertIn("eGFR below 30", note)


class TestParsePatient(unittest.TestCase):
    def test_valid_and_blank_values(self):
        parsed, error = parse_patient({"age": "74", "egfr": 42.5, "crcl": ""})
        self.assertIsNone(error)
        self.assertEqual(parsed, {"age": 74.0, "egfr": 42.5, "crcl": None})
        self.assertEqual(parse_patient(None), (None, None))

    def test_rejects_bad_values(self):
        for raw in ({"age": 150}, {"egfr": -1}, {"crcl": 201}, {"egfr": "abc"},
                    {"age": True}, {"egfr": float("nan")}, "not an object"):
            with self.subTest(raw=raw):
                parsed, error = parse_patient(raw)
                self.assertIsNone(parsed)
                self.assertTrue(error)


if __name__ == "__main__":
    unittest.main()
