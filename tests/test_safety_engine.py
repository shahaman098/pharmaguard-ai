"""Clinical safety engine and scheduler tests for PharmaGuard AI.

These tests validate the demo knowledge base and the scheduling logic. They are
not a clinical validation study and do not establish real-world sensitivity.
"""

import unittest

from pharmaguard.engine import ClinicalSafetyEngine
from pharmaguard.scheduler import ScheduleOptimizer


def _time_to_minutes(value: str) -> int:
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)


class TestDrugResolution(unittest.TestCase):
    def setUp(self):
        self.engine = ClinicalSafetyEngine()

    def test_brand_and_generic_names(self):
        cases = {
            "Coumadin": "warfarin",
            "CIPRO": "ciprofloxacin",
            "Advil": "ibuprofen",
            "Tums": "calcium_carbonate",
            "Synthroid": "levothyroxine",
            "Glucophage": "metformin",
            "Zocor": "simvastatin",
            "Plavix": "clopidogrel",
            "Prozac": "fluoxetine",
            "Lasix": "furosemide",
            "Lanoxin": "digoxin",
            "Zofran": "ondansetron",
            "Bactrim": "trimethoprim_sulfamethoxazole",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(self.engine.normalize_drug_name(raw), expected)

    def test_iron_no_longer_matches_spironolactone(self):
        # Regression: substring matching used to map "iron" -> spironolactone.
        self.assertEqual(self.engine.normalize_drug_name("Iron"), "ferrous_sulfate")
        self.assertEqual(self.engine.normalize_drug_name("spironolactone"), "spironolactone")
        self.assertEqual(
            self.engine.normalize_drug_name("Ferrous Sulfate (Iron)"),
            "ferrous_sulfate",
        )

    def test_dose_and_noise_tokens_are_stripped(self):
        self.assertEqual(
            self.engine.normalize_drug_name("Take Metformin HCl 500 mg by mouth"),
            "metformin",
        )
        self.assertEqual(
            self.engine.normalize_drug_name("Ciprofloxacin 500mg twice daily"),
            "ciprofloxacin",
        )

    def test_mineral_names_survive_direction_words(self):
        self.assertEqual(
            self.engine.normalize_drug_name("Calcium Carbonate 600 mg with meals"),
            "calcium_carbonate",
        )
        self.assertEqual(
            self.engine.normalize_drug_name("Potassium Chloride 20 mEq with meals"),
            "potassium_chloride",
        )

    def test_unknown_name_returns_none(self):
        self.assertIsNone(self.engine.normalize_drug_name("Unobtainium"))

    def test_short_aliases_do_not_misfire(self):
        # "ct" used to resolve to iodinated contrast via a brand string split.
        self.assertIsNone(self.engine.normalize_drug_name("ct"))
        self.assertIsNone(self.engine.normalize_drug_name("example"))
        self.assertEqual(
            self.engine.normalize_drug_name("ct contrast"),
            "iodinated_contrast",
        )


class TestClinicalAudit(unittest.TestCase):
    def setUp(self):
        self.engine = ClinicalSafetyEngine()

    def test_warfarin_ibuprofen_critical(self):
        result = self.engine.audit_regimen(["Warfarin", "Ibuprofen"])
        self.assertEqual(result["critical_count"], 1)
        self.assertEqual(result["status_color"], "red")
        self.assertTrue(any("Bleeding" in item["title"] for item in result["interactions"]))
        self.assertLess(result["safety_score"], 70)

    def test_simvastatin_clarithromycin_critical(self):
        result = self.engine.audit_regimen(["Simvastatin", "Clarithromycin"])
        self.assertEqual(result["critical_count"], 1)
        self.assertTrue(any("Rhabdomyolysis" in item["title"] for item in result["interactions"]))

    def test_cipro_calcium_chelation(self):
        result = self.engine.audit_regimen(["Ciprofloxacin", "Calcium Carbonate"])
        self.assertEqual(result["moderate_count"], 1)
        interaction = result["interactions"][0]
        self.assertTrue(interaction["spacing_resolvable"])
        self.assertEqual(interaction["recommended_spacing_hours"], 3)

    def test_levothyroxine_iron_chelation(self):
        result = self.engine.audit_regimen(["Levothyroxine", "Iron"])
        self.assertEqual(result["moderate_count"], 1)
        self.assertTrue(result["interactions"][0]["spacing_resolvable"])
        self.assertEqual(result["interactions"][0]["recommended_spacing_hours"], 4)

    def test_levothyroxine_calcium_chelation(self):
        result = self.engine.audit_regimen(["Levothyroxine", "Calcium Carbonate"])
        self.assertEqual(result["moderate_count"], 1)
        self.assertIn("Calcium", result["interactions"][0]["title"])

    def test_lisinopril_spironolactone_hyperkalemia(self):
        result = self.engine.audit_regimen(["Lisinopril", "Spironolactone"])
        self.assertEqual(result["moderate_count"], 1)
        self.assertTrue(any("Hyperkalemia" in item["title"] for item in result["interactions"]))

    def test_methotrexate_aspirin_critical(self):
        result = self.engine.audit_regimen(["Methotrexate", "Aspirin"])
        self.assertEqual(result["critical_count"], 1)
        self.assertTrue(any("Methotrexate" in item["title"] for item in result["interactions"]))

    def test_sertraline_tramadol_serotonin(self):
        result = self.engine.audit_regimen(["Sertraline", "Tramadol"])
        self.assertEqual(result["critical_count"], 1)
        self.assertTrue(any("Serotonin" in item["title"] for item in result["interactions"]))

    def test_expanded_high_yield_pairs(self):
        cases = [
            (["Warfarin", "Amiodarone"], "CRITICAL"),
            (["Sildenafil", "Nitroglycerin"], "CRITICAL"),
            (["Allopurinol", "Azathioprine"], "CRITICAL"),
            (["Ciprofloxacin", "Tizanidine"], "CRITICAL"),
            (["Glipizide", "Insulin"], "CRITICAL"),
            (["Clopidogrel", "Omeprazole"], "MODERATE"),
            (["Lithium", "Ibuprofen"], "CRITICAL"),
            (["Metformin", "Contrast Dye"], "MODERATE"),
            (["Aspirin", "Clopidogrel"], "MODERATE"),
        ]
        for medications, severity in cases:
            with self.subTest(medications=medications):
                result = self.engine.audit_regimen(medications)
                self.assertTrue(
                    any(item["severity"] == severity for item in result["interactions"]),
                    msg=f"expected {severity} for {medications}",
                )

    def test_safe_regimen_is_safe(self):
        result = self.engine.audit_regimen(["Metformin", "Simvastatin"])
        self.assertEqual(result["critical_count"], 0)
        self.assertEqual(result["moderate_count"], 0)
        self.assertEqual(result["safety_score"], 100)
        self.assertEqual(result["status_color"], "green")

    def test_unknown_drug_fails_closed(self):
        result = self.engine.audit_regimen(["Metformin", "Mystery Drug"])
        self.assertIn("Mystery Drug", result["unknown_drugs"])
        self.assertEqual(result["unverified_count"], 1)
        self.assertEqual(result["status_color"], "slate")
        self.assertLess(result["safety_score"], 100)
        self.assertTrue(any("Mystery Drug" in line for line in result["patient_summary"]))

    def test_duplicate_medication_is_deduplicated(self):
        result = self.engine.audit_regimen(["Warfarin", "warfarin", "Coumadin"])
        self.assertEqual(result["verified_count"], 1)
        self.assertEqual(len(result["duplicates_removed"]), 2)

    def test_therapeutic_duplication_ssris(self):
        result = self.engine.audit_regimen(["Sertraline", "Fluoxetine"])
        self.assertEqual(result["critical_count"], 1)
        self.assertTrue(any("Duplication" in item["title"] for item in result["interactions"]))

    def test_therapeutic_duplication_nsaids(self):
        result = self.engine.audit_regimen(["Ibuprofen", "Naproxen"])
        self.assertEqual(result["moderate_count"], 1)
        self.assertTrue(any("Duplication" in item["title"] for item in result["interactions"]))

    def test_duplicate_rule_ids_are_unique(self):
        result = self.engine.audit_regimen(["Sertraline", "Fluoxetine", "Citalopram"])
        ids = [item["rule_id"] for item in result["interactions"]]
        self.assertEqual(len(ids), 3)
        self.assertEqual(len(ids), len(set(ids)))

    def test_score_is_bounded(self):
        result = self.engine.audit_regimen(
            ["Warfarin", "Ibuprofen", "Sildenafil", "Nitroglycerin", "Sertraline", "Tramadol"]
        )
        self.assertGreaterEqual(result["safety_score"], 5)
        self.assertLessEqual(result["safety_score"], 100)

    def test_empty_regimen(self):
        result = self.engine.audit_regimen([])
        self.assertEqual(result["total_medications"], 0)
        self.assertEqual(result["safety_score"], 100)
        self.assertEqual(result["coverage_pct"], 100)

    def test_coverage_percentage(self):
        result = self.engine.audit_regimen(["Metformin", "Unknown A", "Unknown B"])
        self.assertEqual(result["verified_count"], 1)
        self.assertEqual(result["coverage_pct"], 33)

    def test_none_entries_are_ignored(self):
        result = self.engine.audit_regimen([None, "Warfarin", ""])
        self.assertEqual(result["verified_count"], 1)
        self.assertEqual(result["unknown_drugs"], [])

    def test_label_dose_override_is_applied(self):
        result = self.engine.audit_regimen(["Warfarin"], {"warfarin": "2 mg"})
        self.assertEqual(result["regimen"][0]["default_dose"], "2 mg")
        sbar = self.engine.generate_sbar_note(result)
        self.assertIn("Warfarin (2 mg)", sbar)

    def test_invalid_dose_override_falls_back(self):
        result = self.engine.audit_regimen(["Warfarin"], {"warfarin": 123})
        self.assertEqual(result["regimen"][0]["default_dose"], "5 mg")

    def test_dose_override_accepts_brand_keys(self):
        result = self.engine.audit_regimen(["Warfarin"], {"Coumadin": "2 mg"})
        self.assertEqual(result["regimen"][0]["default_dose"], "2 mg")

    def test_sbar_survives_malformed_audit(self):
        sbar = self.engine.generate_sbar_note({
            "interactions": [{}],
            "regimen": [{}],
            "unknown_drugs": [None],
        })
        self.assertIn("[S] SITUATION", sbar)
        self.assertIn("dose n/a", sbar)

        sbar = self.engine.generate_sbar_note({
            "interactions": [],
            "regimen": [],
            "unknown_drugs": "not-a-list",
        })
        self.assertIn("[S] SITUATION", sbar)

    def test_sbar_generation(self):
        audit = self.engine.audit_regimen(["Warfarin", "Ibuprofen", "Simvastatin"])
        sbar = self.engine.generate_sbar_note(audit, patient_name="John Doe", age=68)
        for section in ("[S] SITUATION", "[B] BACKGROUND", "[A] ASSESSMENT", "[R] RECOMMENDATION"):
            self.assertIn(section, sbar)
        self.assertIn("John Doe", sbar)
        self.assertIn("DISCLAIMER", sbar)
        self.assertIn("pharmacist", sbar.lower())

    def test_sbar_includes_unverified_drugs(self):
        audit = self.engine.audit_regimen(["Metformin", "Mystery Drug"])
        sbar = self.engine.generate_sbar_note(audit)
        self.assertIn("Mystery Drug", sbar)
        self.assertIn("Verify", sbar)


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.engine = ClinicalSafetyEngine()
        self.scheduler = ScheduleOptimizer()

    def _schedule(self, medications):
        audit = self.engine.audit_regimen(medications)
        return audit, self.scheduler.build_schedule(audit["regimen"], audit["interactions"])

    def _doses_by_key(self, schedule, key):
        return [dose for dose in schedule["doses"] if dose["key"] == key]

    def test_no_missing_daily_medications(self):
        audit, schedule = self._schedule(["Warfarin", "Simvastatin", "Metformin", "Lisinopril"])
        scheduled_keys = {dose["key"] for dose in schedule["doses"]}
        expected = {med["key"] for med in audit["regimen"]}
        self.assertEqual(scheduled_keys, expected)

    def test_cipro_calcium_spacing(self):
        _, schedule = self._schedule(["Ciprofloxacin", "Calcium Carbonate"])
        cipro = self._doses_by_key(schedule, "ciprofloxacin")
        calcium = self._doses_by_key(schedule, "calcium_carbonate")
        distances = [
            abs(c["minutes"] - ca["minutes"]) / 60
            for c in cipro for ca in calcium
        ]
        self.assertGreaterEqual(min(distances), 3.0)
        self.assertEqual(schedule["unresolved"], [])

    def test_levothyroxine_iron_spacing_and_fasting(self):
        _, schedule = self._schedule(["Levothyroxine", "Ferrous Sulfate"])
        levo = self._doses_by_key(schedule, "levothyroxine")[0]
        iron = self._doses_by_key(schedule, "ferrous_sulfate")[0]
        self.assertLessEqual(levo["minutes"], 7 * 60 + 30)
        self.assertGreaterEqual(abs(levo["minutes"] - iron["minutes"]) / 60, 4.0)

    def test_simvastatin_at_bedtime(self):
        _, schedule = self._schedule(["Simvastatin"])
        dose = self._doses_by_key(schedule, "simvastatin")[0]
        self.assertGreaterEqual(dose["minutes"], 20 * 60)

    def test_bid_doses_are_separated(self):
        _, schedule = self._schedule(["Metformin"])
        doses = self._doses_by_key(schedule, "metformin")
        self.assertEqual(len(doses), 2)
        self.assertGreaterEqual(abs(doses[0]["minutes"] - doses[1]["minutes"]) / 60, 10.0)

    def test_with_meal_drugs_land_near_meals(self):
        _, schedule = self._schedule(["Metformin", "Ibuprofen"])
        meal_windows = [(450, 510), (720, 780), (1080, 1140)]
        for key in ("metformin", "ibuprofen"):
            for dose in self._doses_by_key(schedule, key):
                self.assertTrue(
                    any(start <= dose["minutes"] <= end for start, end in meal_windows),
                    msg=f"{key} at {dose['time']} is not near a meal",
                )

    def test_weekly_methotrexate_is_not_daily(self):
        _, schedule = self._schedule(["Methotrexate", "Metformin"])
        self.assertEqual(len(schedule["weekly"]), 1)
        self.assertEqual(schedule["weekly"][0]["key"], "methotrexate")
        self.assertFalse(any(dose["key"] == "methotrexate" for dose in schedule["doses"]))
        self.assertIn("WEEKLY", schedule["weekly"][0]["warning"])

    def test_prn_medications_are_not_scheduled(self):
        _, schedule = self._schedule(["Tramadol", "Sertraline"])
        self.assertTrue(any(item["key"] == "tramadol" for item in schedule["prn"]))
        self.assertFalse(any(dose["key"] == "tramadol" for dose in schedule["doses"]))

    def test_critical_pairs_are_not_co_scheduled(self):
        _, schedule = self._schedule(["Warfarin", "Ibuprofen"])
        warfarin = self._doses_by_key(schedule, "warfarin")[0]
        ibuprofen = self._doses_by_key(schedule, "ibuprofen")
        self.assertTrue(all(abs(warfarin["minutes"] - dose["minutes"]) >= 120 for dose in ibuprofen))
        self.assertTrue(all(dose["critical_conflict"] for dose in ibuprofen))

    def test_adjustments_and_solver_metadata(self):
        _, schedule = self._schedule(["Ciprofloxacin", "Calcium Carbonate", "Simvastatin"])
        self.assertTrue(schedule["adjustments_made"])
        self.assertEqual(schedule["solver"]["relaxation"], 1.0)
        self.assertTrue(schedule["solver"]["fully_constrained"])
        self.assertGreater(schedule["solver"]["nodes_explored"], 0)

    def test_schedule_is_deterministic(self):
        audit, first = self._schedule(["Warfarin", "Simvastatin", "Ciprofloxacin", "Calcium Carbonate"])
        second = self.scheduler.build_schedule(audit["regimen"], audit["interactions"])
        self.assertEqual(
            [(d["key"], d["time"]) for d in first["doses"]],
            [(d["key"], d["time"]) for d in second["doses"]],
        )

    def test_all_doses_are_inside_day_window(self):
        _, schedule = self._schedule(
            ["Warfarin", "Simvastatin", "Clarithromycin", "Ciprofloxacin", "Ibuprofen", "Calcium Carbonate"]
        )
        for dose in schedule["doses"]:
            self.assertGreaterEqual(_time_to_minutes(dose["time"]), 6 * 60)
            self.assertLessEqual(_time_to_minutes(dose["time"]), 23 * 60)

    def test_large_regimen_gets_a_complete_schedule(self):
        medications = [
            "Warfarin", "Ibuprofen", "Aspirin", "Naproxen", "Clopidogrel",
            "Sertraline", "Tramadol", "Lisinopril", "Spironolactone",
            "Potassium Chloride", "Metformin", "Simvastatin",
            "Clarithromycin", "Ciprofloxacin", "Calcium Carbonate",
            "Levothyroxine", "Ferrous Sulfate",
        ]
        audit, schedule = self._schedule(medications)
        daily_plans = [
            med for med in audit["regimen"]
            if med["schedule"]["frequency"] not in ("as_needed", "weekly")
        ]
        self.assertGreaterEqual(len(schedule["doses"]), len(daily_plans))
        self.assertIn("critical_conflicts", schedule)
        self.assertIn("critical_relaxed", schedule["solver"])

    def test_invalid_schedule_items_are_ignored(self):
        schedule = self.scheduler.build_schedule(
            ["not a medication", None, 42, {}],
            [None, "not an interaction", {}],
        )
        self.assertEqual(schedule["doses"], [])
        self.assertEqual(schedule["groups"], [])
        self.assertEqual(schedule["critical_conflicts"], [])

    def test_label_dose_override_reaches_schedule(self):
        result = self.engine.audit_regimen(["Warfarin"], {"warfarin": "2 mg"})
        schedule = self.scheduler.build_schedule(result["regimen"], result["interactions"])
        warfarin = [dose for dose in schedule["doses"] if dose["key"] == "warfarin"][0]
        self.assertEqual(warfarin["dose"], "2 mg")


if __name__ == "__main__":
    unittest.main()
