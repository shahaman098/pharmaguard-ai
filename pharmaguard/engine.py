"""Core safety audit and clinical reasoning engine for PharmaGuard AI."""

from typing import List, Dict, Any, Tuple
from .interactions import DRUG_REGISTRY, INTERACTION_RULES


class ClinicalSafetyEngine:
    """Evaluates a multi-drug regimen against clinical interaction rules,
    computes an aggregate risk index, and generates clinician/patient artifacts.
    """

    def __init__(self):
        self.rules = INTERACTION_RULES
        self.registry = DRUG_REGISTRY

    def normalize_drug_name(self, raw_name: str) -> str:
        """Converts user input or brand name to canonical registry key."""
        clean = raw_name.strip().lower().replace(" ", "_").replace("-", "_")
        if clean in self.registry:
            return clean
        for key, data in self.registry.items():
            if clean in key or key in clean:
                return key
            if clean in data["name"].lower() or clean in data["brand"].lower():
                return key
        return clean

    def audit_regimen(self, drug_list: List[str]) -> Dict[str, Any]:
        """Performs a comprehensive safety audit over a list of active medications."""
        normalized_keys = []
        unknown_drugs = []

        for d in drug_list:
            norm = self.normalize_drug_name(d)
            if norm in self.registry:
                if norm not in normalized_keys:
                    normalized_keys.append(norm)
            else:
                unknown_drugs.append(d)

        detected_interactions = []
        critical_count = 0
        moderate_count = 0

        # Pairwise graph traversal
        for i in range(len(normalized_keys)):
            for j in range(i + 1, len(normalized_keys)):
                d1, d2 = normalized_keys[i], normalized_keys[j]
                match = self._find_interaction(d1, d2)
                if match:
                    detected_interactions.append(match)
                    if match["severity"] == "CRITICAL":
                        critical_count += 1
                    elif match["severity"] == "MODERATE":
                        moderate_count += 1

        # Calculate Clinical Safety Index (0 to 100)
        # 100 = flawless, <60 = high risk, <40 = critical danger
        penalty = (critical_count * 35) + (moderate_count * 12)
        safety_score = max(5, 100 - penalty)

        if critical_count > 0:
            overall_status = "CRITICAL RISK — PHYSICIAN CONSULTATION REQUIRED"
            status_color = "red"
        elif moderate_count > 0:
            overall_status = "MODERATE RISK — TEMPORAL ADJUSTMENT REQUIRED"
            status_color = "amber"
        else:
            overall_status = "SAFE — NO KNOWN MAJOR INTERACTIONS"
            status_color = "green"

        # Detailed regimen info
        regimen_details = [
            {
                "key": k,
                "name": self.registry[k]["name"],
                "brand": self.registry[k]["brand"],
                "class": self.registry[k]["class"],
                "default_dose": self.registry[k]["default_dose"],
                "default_time": self.registry[k]["default_time"],
                "food_warnings": self.registry[k]["food_warnings"]
            }
            for k in normalized_keys
        ]

        # Plain language patient guidance summary
        patient_summary = self._generate_patient_summary(detected_interactions)

        return {
            "total_medications": len(normalized_keys),
            "safety_score": safety_score,
            "overall_status": overall_status,
            "status_color": status_color,
            "critical_count": critical_count,
            "moderate_count": moderate_count,
            "regimen": regimen_details,
            "interactions": detected_interactions,
            "unknown_drugs": unknown_drugs,
            "patient_summary": patient_summary
        }

    def _find_interaction(self, d1: str, d2: str) -> Dict[str, Any]:
        """Checks if an interaction rule exists for the pair."""
        pair_set = {d1, d2}
        for rule in self.rules:
            if set(rule["pair"]) == pair_set:
                r1_name = self.registry[d1]["name"]
                r2_name = self.registry[d2]["name"]
                return {
                    "drug_a": r1_name,
                    "drug_b": r2_name,
                    "pair_keys": (d1, d2),
                    "severity": rule["severity"],
                    "title": rule["title"],
                    "mechanism": rule["mechanism"],
                    "clinical_action": rule["clinical_action"],
                    "category": rule["category"],
                    "spacing_resolvable": rule.get("spacing_resolvable", False),
                    "recommended_spacing_hours": rule.get("recommended_spacing_hours", 0)
                }
        return None

    def _generate_patient_summary(self, interactions: List[Dict[str, Any]]) -> List[str]:
        """Generates plain-language 5th-grade reading level advice."""
        advice = []
        for item in interactions:
            d_a = item["drug_a"]
            d_b = item["drug_b"]
            if item["severity"] == "CRITICAL":
                if "Bleeding" in item["title"]:
                    advice.append(
                        f"🚨 DANGER: Do not take {d_a} with {d_b}. Taking both together greatly increases your chance of severe internal stomach bleeding. Ask your doctor for a safer painkiller like acetaminophen."
                    )
                elif "Rhabdomyolysis" in item["title"]:
                    advice.append(
                        f"🚨 DANGER: {d_b} causes your body to absorb dangerously high levels of {d_a}, which can destroy muscle tissue and damage your kidneys. Call your doctor immediately to pause {d_a} while on this antibiotic."
                    )
                else:
                    advice.append(
                        f"🚨 DANGER: Serious conflict between {d_a} and {d_b}. Contact your prescribing doctor or pharmacist before taking both."
                    )
            elif item["severity"] == "MODERATE":
                if item["spacing_resolvable"]:
                    hrs = item["recommended_spacing_hours"]
                    advice.append(
                        f"⚠️ TIMING ALERT: {d_b} stops your body from absorbing {d_a}. Space them at least {hrs} hours apart so your medicine works properly."
                    )
                else:
                    advice.append(
                        f"⚠️ CAUTION: {d_a} and {d_b} both affect your body's salt/potassium levels. Your doctor needs to check your blood tests regularly."
                    )
        if not advice:
            advice.append("✅ No major conflicts detected between your listed medications. Continue taking them as prescribed.")
        return advice

    def generate_sbar_note(self, audit_result: Dict[str, Any], patient_name: str = "Patient Jane Doe", age: int = 74) -> str:
        """Generates a standardized clinical SBAR memo for a pharmacist or physician."""
        interactions = audit_result.get("interactions", [])
        med_names = [m["name"] + f" ({m['default_dose']})" for m in audit_result.get("regimen", [])]

        critical_lines = [
            f"- {i['drug_a']} + {i['drug_b']}: {i['title']} ({i['mechanism']})"
            for i in interactions if i["severity"] == "CRITICAL"
        ]
        moderate_lines = [
            f"- {i['drug_a']} + {i['drug_b']}: {i['title']}"
            for i in interactions if i["severity"] == "MODERATE"
        ]

        actions = [i["clinical_action"] for i in interactions if i["severity"] == "CRITICAL"]
        if not actions:
            actions = ["Continue current regimen with temporal dose spacing where indicated."]

        sbar = f"""CLINICAL PHARMACY ESCALATION MEMO (SBAR FORMAT)
======================================================
DATE/TIME: Automated Pharmacovigilance Report
PATIENT:   {patient_name} (Age: {age})
SETTING:   Community Ambulatory / Polypharmacy Review

[S] SITUATION
-------------
Automated safety screening detected {len(critical_lines)} critical contraindication(s) and {len(moderate_lines)} absorption/monitoring conflict(s) in the patient's current multi-prescriber regimen. Overall Safety Index: {audit_result['safety_score']}/100.

[B] BACKGROUND
--------------
Patient active medication list ({len(med_names)} agents):
{', '.join(med_names)}

[A] ASSESSMENT
--------------
Critical Contraindications Identified:
{chr(10).join(critical_lines) if critical_lines else 'None.'}

Temporal & Absorption Interactions:
{chr(10).join(moderate_lines) if moderate_lines else 'None.'}

[R] RECOMMENDATION
------------------
{chr(10).join(['1. ' + a for a in actions])}
2. Instruct patient on 3-to-4 hour temporal separation for chelating minerals/antacids.
3. Review patient renal function panel and complete medication reconciliation.

Transmitted via PharmaGuard AI Clinical Decision Support Engine.
"""
        return sbar
