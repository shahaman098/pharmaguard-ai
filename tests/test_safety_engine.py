"""Comprehensive clinical test suite for PharmaGuard AI safety engine."""

import unittest
from pharmaguard.engine import ClinicalSafetyEngine
from pharmaguard.scheduler import ScheduleOptimizer


class TestPharmaGuardSafetyEngine(unittest.TestCase):

    def setUp(self):
        self.engine = ClinicalSafetyEngine()
        self.scheduler = ScheduleOptimizer()

    def test_warfarin_ibuprofen_critical(self):
        """Verifies detection of lethal synergistic hemorrhage between Warfarin and NSAID."""
        result = self.engine.audit_regimen(["Warfarin", "Ibuprofen"])
        self.assertEqual(result["critical_count"], 1)
        self.assertEqual(result["overall_status"], "CRITICAL RISK — PHYSICIAN CONSULTATION REQUIRED")
        self.assertTrue(any("Bleeding" in i["title"] for i in result["interactions"]))
        self.assertLess(result["safety_score"], 70)

    def test_simvastatin_clarithromycin_critical(self):
        """Verifies detection of potent CYP3A4 inhibition and rhabdomyolysis hazard."""
        result = self.engine.audit_regimen(["Simvastatin", "Clarithromycin"])
        self.assertEqual(result["critical_count"], 1)
        self.assertTrue(any("CYP3A4" in i["title"] or "Rhabdomyolysis" in i["title"] for i in result["interactions"]))

    def test_cipro_calcium_chelation(self):
        """Verifies detection of polyvalent cation chelation between Ciprofloxacin and Calcium."""
        result = self.engine.audit_regimen(["Ciprofloxacin", "Calcium Carbonate"])
        self.assertEqual(result["moderate_count"], 1)
        interaction = result["interactions"][0]
        self.assertEqual(interaction["severity"], "MODERATE")
        self.assertTrue(interaction["spacing_resolvable"])
        self.assertEqual(interaction["recommended_spacing_hours"], 3)

    def test_lisinopril_spironolactone_hyperkalemia(self):
        """Verifies detection of dual potassium retention risk requiring lab monitoring."""
        result = self.engine.audit_regimen(["Lisinopril", "Spironolactone"])
        self.assertEqual(result["moderate_count"], 1)
        self.assertTrue(any("Hyperkalemia" in i["title"] for i in result["interactions"]))

    def test_methotrexate_aspirin_critical(self):
        """Verifies detection of reduced renal clearance and methotrexate toxicity."""
        result = self.engine.audit_regimen(["Methotrexate", "Aspirin"])
        self.assertEqual(result["critical_count"], 1)
        self.assertTrue(any("Methotrexate Toxicity" in i["title"] for i in result["interactions"]))

    def test_sertraline_tramadol_serotonin(self):
        """Verifies detection of synergistic serotonergic agonism."""
        result = self.engine.audit_regimen(["Sertraline", "Tramadol"])
        self.assertEqual(result["critical_count"], 1)
        self.assertTrue(any("Serotonin Syndrome" in i["title"] for i in result["interactions"]))

    def test_levothyroxine_iron_chelation(self):
        """Verifies detection of intestinal iron chelation of exogenous thyroxine."""
        result = self.engine.audit_regimen(["Levothyroxine", "Ferrous Sulfate"])
        self.assertEqual(result["moderate_count"], 1)
        self.assertTrue(result["interactions"][0]["spacing_resolvable"])

    def test_aspirin_warfarin_synergy(self):
        """Verifies detection of dual antiplatelet and anticoagulant bleeding risk."""
        result = self.engine.audit_regimen(["Aspirin", "Warfarin"])
        self.assertEqual(result["critical_count"], 1)

    def test_safe_regimen(self):
        """Verifies that non-interacting medications score 100/100 and safe status."""
        result = self.engine.audit_regimen(["Metformin", "Simvastatin"])
        self.assertEqual(result["critical_count"], 0)
        self.assertEqual(result["moderate_count"], 0)
        self.assertEqual(result["safety_score"], 100)
        self.assertEqual(result["overall_status"], "SAFE — NO KNOWN MAJOR INTERACTIONS")

    def test_sbar_generation(self):
        """Verifies that SBAR document contains all required clinical sections."""
        audit = self.engine.audit_regimen(["Warfarin", "Ibuprofen", "Simvastatin"])
        sbar = self.engine.generate_sbar_note(audit, patient_name="John Doe", age=68)
        self.assertIn("[S] SITUATION", sbar)
        self.assertIn("[B] BACKGROUND", sbar)
        self.assertIn("[A] ASSESSMENT", sbar)
        self.assertIn("[R] RECOMMENDATION", sbar)
        self.assertIn("John Doe", sbar)

    def test_schedule_deconfliction(self):
        """Verifies that schedule optimizer separates chelating calcium to lunch."""
        audit = self.engine.audit_regimen(["Ciprofloxacin", "Calcium Carbonate", "Simvastatin"])
        schedule = self.scheduler.build_schedule(audit["regimen"], audit["interactions"])
        timeline = schedule["timeline"]

        breakfast = next(t for t in timeline if t["slot_id"] == "breakfast")
        lunch = next(t for t in timeline if t["slot_id"] == "lunch")
        bedtime = next(t for t in timeline if t["slot_id"] == "bedtime")

        # Ciprofloxacin in breakfast, Calcium moved to Lunch, Simvastatin in Bedtime
        self.assertTrue(any(m["name"] == "Ciprofloxacin" for m in breakfast["medications"]))
        self.assertTrue(any(m["name"] == "Calcium Carbonate" for m in lunch["medications"]))
        self.assertTrue(any(m["name"] == "Simvastatin" for m in bedtime["medications"]))
        self.assertTrue(len(schedule["adjustments_made"]) > 0)

    def test_drug_name_normalization(self):
        """Verifies that brand names and case-insensitive strings resolve to canonical keys."""
        self.assertEqual(self.engine.normalize_drug_name("Coumadin"), "warfarin")
        self.assertEqual(self.engine.normalize_drug_name("CIPRO"), "ciprofloxacin")
        self.assertEqual(self.engine.normalize_drug_name("Advil"), "ibuprofen")
        self.assertEqual(self.engine.normalize_drug_name("Tums"), "calcium_carbonate")
        self.assertEqual(self.engine.normalize_drug_name("Synthroid"), "levothyroxine")


if __name__ == "__main__":
    unittest.main()
