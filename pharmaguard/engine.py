"""Core safety audit and clinical reasoning engine for PharmaGuard AI.

The engine deliberately uses a deterministic rule layer rather than a generative
model for safety-critical decisions. Unknown medications fail closed: they are
surfaced as UNVERIFIED instead of being silently treated as safe.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

from .interactions import (
    DISCLAIMER,
    DRUG_REGISTRY,
    DUPLICATE_CLASS_RULES,
    INTERACTION_RULES,
    KNOWLEDGE_BASE_META,
    RENAL_RULES,
    label_evidence_for,
)

MEASURE_LABELS = {
    "egfr": "eGFR (mL/min/1.73 m²)",
    "crcl": "CrCl, Cockcroft-Gault (mL/min)",
    "age": "Age (years)",
}
PATIENT_LIMITS = {"age": (0, 120), "egfr": (0, 200), "crcl": (0, 200)}


def parse_patient(raw: Any) -> Tuple[Optional[Dict[str, Optional[float]]], Optional[str]]:
    """Validates patient context. Blank values mean "not provided", never "normal"."""
    if raw is None:
        return None, None
    if not isinstance(raw, dict):
        return None, "patient must be an object"
    patient: Dict[str, Optional[float]] = {}
    for field, (low, high) in PATIENT_LIMITS.items():
        value = raw.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            patient[field] = None
            continue
        if isinstance(value, bool):
            return None, f"patient.{field} must be a number"
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None, f"patient.{field} must be a number"
        if number != number or not low <= number <= high:
            return None, f"patient.{field} must be between {low} and {high}"
        patient[field] = number
    return patient, None


def _rule_applies(rule: Dict[str, Any], value: float) -> bool:
    checks = {
        "lt": lambda bound: value < bound,
        "le": lambda bound: value <= bound,
        "gt": lambda bound: value > bound,
        "ge": lambda bound: value >= bound,
    }
    return all(check(rule[key]) for key, check in checks.items() if key in rule)

# Words that add no drug-identification value when users paste label text.
_NOISE_WORDS = {
    "take", "takes", "taking", "daily", "tablet", "tablets", "tab", "tabs",
    "capsule", "capsules", "cap", "caps", "prescription", "rx", "medication",
    "medicine", "the", "a", "an", "and", "with", "for", "of", "one", "two",
    "each", "morning", "evening", "night", "bedtime", "as", "needed", "by",
    "mouth", "orally", "oral", "mg", "mcg", "g", "ml", "units", "unit", "iu",
    "meq", "percent", "extended", "release", "er", "xr", "sr", "dr", "hcl",
    "hydrochloride", "sodium", "salt", "generic",
    "brand", "name", "patient", "directions", "refills", "remaining", "qty",
    "quantity", "date", "filled", "discard", "after", "before", "food",
    "meal", "meals", "water", "swallow", "whole", "do", "not", "crush",
}

_DOSE_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|units?|iu|meq|%|tablets?|tabs?|capsules?|caps?)\b",
    re.IGNORECASE,
)


def _normalize_text(value: str) -> str:
    """Lowercase, strip punctuation, and collapse whitespace."""
    text = value.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _alias_variants(value: str) -> List[str]:
    """Expands brand strings such as 'Coumadin / Jantoven' or names with parentheses."""
    variants: List[str] = []
    for part in re.split(r"[/]", value):
        part = part.strip()
        if not part:
            continue
        variants.append(part)
        # Add the text inside parentheses as a separate alias, e.g. "(Iron)".
        for inner in re.findall(r"\(([^)]+)\)", part):
            variants.append(inner)
        # Add the text outside parentheses, e.g. "Ferrous Sulfate (Iron)".
        outside = re.sub(r"\([^)]*\)", " ", part).strip()
        if outside:
            variants.append(outside)
    return variants


class ClinicalSafetyEngine:
    """Evaluates a multi-drug regimen against curated interaction rules,
    computes a transparent risk index, and generates clinician/patient artifacts.
    """

    def __init__(self) -> None:
        self.rules = INTERACTION_RULES
        self.registry = DRUG_REGISTRY
        self.duplicate_rules = DUPLICATE_CLASS_RULES
        self.meta = KNOWLEDGE_BASE_META

        self._alias_index: Dict[str, str] = {}
        for key, data in self.registry.items():
            candidates = [data["name"], data["brand"], *data.get("aliases", [])]
            for candidate in candidates:
                for variant in _alias_variants(candidate):
                    normalized = _normalize_text(variant)
                    if normalized and normalized not in self._alias_index:
                        self._alias_index[normalized] = key

        self._pair_index: Dict[frozenset, Dict[str, Any]] = {
            frozenset(rule["pair"]): rule for rule in self.rules
        }

    # ------------------------------------------------------------------
    # Name resolution
    # ------------------------------------------------------------------
    def normalize_drug_name(self, raw_name: str) -> Optional[str]:
        """Resolve a free-text drug string to a canonical registry key.

        Matching is exact at the string level, then token-aware. We never use
        substring matching, which previously made "iron" resolve to
        "spironolactone".
        """
        if not isinstance(raw_name, str):
            return None

        text = _normalize_text(raw_name)
        if not text:
            return None

        if text in self._alias_index:
            return self._alias_index[text]

        text = _DOSE_PATTERN.sub(" ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if text in self._alias_index:
            return self._alias_index[text]

        tokens = [token for token in text.split() if token not in _NOISE_WORDS]
        if not tokens:
            return None

        cleaned = " ".join(tokens)
        if cleaned in self._alias_index:
            return self._alias_index[cleaned]

        # Longest contiguous alias wins. Token matching prevents "iron" from
        # matching inside "spironolactone".
        best: Optional[Tuple[int, str]] = None
        for alias, key in self._alias_index.items():
            alias_tokens = alias.split()
            if not alias_tokens:
                continue
            width = len(alias_tokens)
            for index in range(len(tokens) - width + 1):
                if tokens[index:index + width] == alias_tokens:
                    if best is None or width > best[0]:
                        best = (width, key)
                    break
        return best[1] if best else None

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------
    def audit_regimen(
        self,
        drug_list: List[str],
        dose_overrides: Optional[Dict[str, str]] = None,
        patient: Optional[Dict[str, Optional[float]]] = None,
    ) -> Dict[str, Any]:
        """Run a comprehensive safety audit over a list of medication names.

        ``dose_overrides`` maps a registry key, generic name, or brand to a dose
        confirmed from a scanned label. It is optional; invalid values fall back
        to the registry default dose.
        """
        if not isinstance(drug_list, list):
            drug_list = []
        drug_list = [
            str(item).strip()
            for item in drug_list
            if item is not None and str(item).strip()
        ][:50]
        overrides: Dict[str, str] = {}
        if isinstance(dose_overrides, dict):
            for raw_key, value in dose_overrides.items():
                canonical = self.normalize_drug_name(str(raw_key))
                if canonical and isinstance(value, str) and value.strip():
                    overrides[canonical] = " ".join(value.split())[:40]

        def resolved_dose(key: str) -> str:
            return overrides.get(key) or self.registry[key]["default_dose"]

        normalized_keys: List[str] = []
        unknown_drugs: List[str] = []
        duplicates: List[str] = []

        for raw in drug_list:
            norm = self.normalize_drug_name(raw)
            if norm is None:
                if raw.strip() not in unknown_drugs:
                    unknown_drugs.append(raw.strip())
            elif norm in normalized_keys:
                if raw.strip() not in duplicates:
                    duplicates.append(raw.strip())
            else:
                normalized_keys.append(norm)

        interactions: List[Dict[str, Any]] = []

        # Pairwise graph traversal.
        for first, second in combinations(normalized_keys, 2):
            match = self._find_interaction(first, second)
            if match:
                interactions.append(match)

        # Therapeutic duplication checks (only pairs not already covered).
        for rule in self.duplicate_rules:
            present = [key for key in rule["keys"] if key in normalized_keys]
            for first, second in combinations(present, 2):
                if frozenset((first, second)) in self._pair_index:
                    continue
                interactions.append(self._build_interaction(rule, first, second))

        interactions.sort(
            key=lambda item: (
                0 if item["severity"] == "CRITICAL" else 1,
                item["title"],
            )
        )

        patient_checks = (
            self._patient_checks(normalized_keys, patient) if patient is not None else None
        )
        patient_flags = patient_checks["flags"] if patient_checks else []

        critical_count = sum(
            1 for item in interactions + patient_flags if item["severity"] == "CRITICAL"
        )
        moderate_count = sum(
            1 for item in interactions + patient_flags if item["severity"] == "MODERATE"
        )

        penalty = (critical_count * 35) + (moderate_count * 12)
        safety_score = max(5, 100 - penalty)
        if unknown_drugs:
            # Never present a regimen with unchecked medicines as fully safe.
            safety_score = min(safety_score, max(40, 80 - (5 * len(unknown_drugs))))

        if critical_count > 0:
            overall_status = "CRITICAL RISK — PHARMACIST REVIEW REQUIRED"
            status_color = "red"
        elif moderate_count > 0:
            overall_status = "MODERATE RISK — TIMING OR MONITORING REVIEW REQUIRED"
            status_color = "amber"
        elif unknown_drugs:
            overall_status = "INCOMPLETE — UNVERIFIED MEDICATIONS"
            status_color = "slate"
        elif normalized_keys:
            overall_status = "SAFE — NO KNOWN INTERACTIONS IN DEMO KB"
            status_color = "green"
        else:
            overall_status = "NO MEDICATIONS TO REVIEW"
            status_color = "slate"

        total_medications = len(normalized_keys) + len(unknown_drugs)
        coverage_pct = (
            round((len(normalized_keys) / total_medications) * 100)
            if total_medications
            else 100
        )

        regimen_details = [
            {
                "key": key,
                "name": self.registry[key]["name"],
                "brand": self.registry[key]["brand"],
                "class": self.registry[key]["class"],
                "default_dose": resolved_dose(key),
                "default_time": self.registry[key]["default_time"],
                "food_warnings": self.registry[key]["food_warnings"],
                "schedule": self.registry[key]["schedule"],
            }
            for key in normalized_keys
        ]

        result = {
            "total_medications": total_medications,
            "verified_count": len(normalized_keys),
            "unverified_count": len(unknown_drugs),
            "coverage_pct": coverage_pct,
            "safety_score": safety_score,
            "overall_status": overall_status,
            "status_color": status_color,
            "critical_count": critical_count,
            "moderate_count": moderate_count,
            "regimen": regimen_details,
            "interactions": interactions,
            "unknown_drugs": unknown_drugs,
            "duplicates_removed": duplicates,
            "patient_summary": self._generate_patient_summary(interactions, unknown_drugs),
            "knowledge_base": self.meta,
            "disclaimer": DISCLAIMER,
        }
        if patient_checks is not None:
            result["patient_checks"] = patient_checks
        return result

    def _patient_checks(
        self, keys: List[str], patient: Dict[str, Optional[float]]
    ) -> Dict[str, Any]:
        """Applies FDA-label kidney-function and age dosing rules to the regimen.

        A drug whose label rule needs a measurement the user did not enter is
        listed as not checked, so a blank field is never read as normal kidney
        function.
        """
        flags: List[Dict[str, Any]] = []
        not_checked: Dict[Tuple[str, str], Dict[str, Any]] = {}
        checked_drugs: List[str] = []
        for rule in RENAL_RULES:
            key = rule["drug"]
            if key not in keys:
                continue
            measure = rule["measure"]
            value = patient.get(measure)
            if value is None:
                not_checked.setdefault((key, measure), {
                    "drug": self.registry[key]["name"],
                    "measure": measure,
                    "measure_label": MEASURE_LABELS[measure],
                })
                continue
            if key not in checked_drugs:
                checked_drugs.append(key)
            if _rule_applies(rule, value):
                flags.append({
                    "drug": self.registry[key]["name"],
                    "drug_key": key,
                    "severity": rule["severity"],
                    "title": rule["title"],
                    "clinical_action": rule["action"],
                    "measure": measure,
                    "measure_label": MEASURE_LABELS[measure],
                    "patient_value": value,
                    "label_evidence": {
                        "quote": rule["quote"],
                        "section": rule["section"],
                        "label_name": rule["label_name"],
                        "set_id": rule["set_id"],
                        "effective_time": rule["effective_time"],
                        "dailymed_url": rule["dailymed_url"],
                    },
                })
        flags.sort(key=lambda item: (0 if item["severity"] == "CRITICAL" else 1, item["title"]))
        return {
            "inputs": {field: patient.get(field) for field in PATIENT_LIMITS},
            "flags": flags,
            "not_checked": list(not_checked.values()),
            "checked_drugs": [self.registry[key]["name"] for key in checked_drugs],
        }

    def _find_interaction(self, first: str, second: str) -> Optional[Dict[str, Any]]:
        rule = self._pair_index.get(frozenset((first, second)))
        if not rule:
            return None
        return self._build_interaction(rule, first, second)

    def _build_interaction(
        self, rule: Dict[str, Any], first: str, second: str
    ) -> Dict[str, Any]:
        pair = rule.get("pair")
        rule_id = f"{pair[0]}+{pair[1]}" if pair else f"{first}+{second}"
        return {
            "rule_id": rule_id,
            "label_evidence": label_evidence_for(rule_id) if pair else {"tier": "class_rule"},
            "drug_a": self.registry[first]["name"],
            "drug_b": self.registry[second]["name"],
            "pair_keys": (first, second),
            "severity": rule["severity"],
            "title": rule["title"],
            "mechanism": rule["mechanism"],
            "clinical_action": rule["clinical_action"],
            "category": rule["category"],
            "spacing_resolvable": rule.get("spacing_resolvable", False),
            "recommended_spacing_hours": rule.get("recommended_spacing_hours", 0),
            "source": rule.get("source", "FDA-approved labeling"),
        }

    # ------------------------------------------------------------------
    # Patient-facing copy
    # ------------------------------------------------------------------
    def _generate_patient_summary(
        self, interactions: List[Dict[str, Any]], unknown_drugs: List[str]
    ) -> List[str]:
        advice: List[str] = []

        for item in interactions:
            drug_a = item["drug_a"]
            drug_b = item["drug_b"]

            if item["severity"] == "CRITICAL":
                advice.append(
                    f"🚨 DANGER: Do not take {drug_a} and {drug_b} together without "
                    f"talking to your doctor or pharmacist. {item['title']}. "
                    f"{item['clinical_action']}"
                )
            elif item["spacing_resolvable"]:
                hours = item["recommended_spacing_hours"]
                advice.append(
                    f"⚠️ TIMING: Take {drug_a} and {drug_b} at least {hours:g} hours "
                    f"apart. Taking them too close together can stop one medicine from "
                    f"working properly."
                )
            else:
                advice.append(
                    f"⚠️ CAUTION: {drug_a} and {drug_b} need extra care. "
                    f"{item['title']}. Ask your pharmacist what to watch for."
                )

        for drug in unknown_drugs:
            advice.append(
                f"❓ UNVERIFIED: We could not check “{drug}” against our demo "
                f"knowledge base. Do not assume it is safe. Show this list to a "
                f"pharmacist and ask about interactions."
            )

        if not advice:
            advice.append(
                "✅ No known interactions were found in this demo knowledge base. "
                "This does not replace a review by your pharmacist or doctor."
            )
        return advice

    # ------------------------------------------------------------------
    # Clinician artifact
    # ------------------------------------------------------------------
    def generate_sbar_note(
        self,
        audit_result: Dict[str, Any],
        patient_name: str = "Patient Jane Doe",
        age: int = 74,
    ) -> str:
        """Generate a structured SBAR draft for pharmacist/physician review."""
        interactions = [
            item for item in audit_result.get("interactions", [])
            if isinstance(item, dict)
        ]
        regimen = [
            item for item in audit_result.get("regimen", [])
            if isinstance(item, dict)
        ]
        raw_unknown = audit_result.get("unknown_drugs", [])
        unknown = [
            str(item) for item in raw_unknown
            if item is not None
        ] if isinstance(raw_unknown, list) else []
        med_names = [
            f"{m.get('name', 'Medication')} ({m.get('default_dose', 'dose n/a')})"
            for m in regimen
        ]

        critical = [i for i in interactions if i.get("severity") == "CRITICAL"]
        moderate = [i for i in interactions if i.get("severity") == "MODERATE"]

        critical_lines = [
            f"- {i.get('drug_a', '?')} + {i.get('drug_b', '?')}: "
            f"{i.get('title', 'Interaction')} — {i.get('mechanism', '')}"
            for i in critical
        ]
        moderate_lines = [
            f"- {i.get('drug_a', '?')} + {i.get('drug_b', '?')}: "
            f"{i.get('title', 'Interaction')} — {i.get('clinical_action', '')}"
            for i in moderate
        ]

        recommendations: List[str] = []
        for item in critical:
            recommendations.append(
                f"Resolve {item.get('drug_a', '?')} + {item.get('drug_b', '?')}: "
                f"{item.get('clinical_action', 'review the combination')}"
            )
        for item in moderate:
            if item.get("spacing_resolvable"):
                recommendations.append(
                    f"Separate {item.get('drug_a', '?')} and {item.get('drug_b', '?')} "
                    f"by at least {item.get('recommended_spacing_hours', 0):g} hours."
                )
            else:
                recommendations.append(
                    f"Review {item.get('drug_a', '?')} + {item.get('drug_b', '?')} "
                    f"and arrange the recommended monitoring."
                )
        for drug in unknown:
            recommendations.append(
                f"Verify “{drug}” — not present in the demo knowledge base; screen it with a "
                f"validated interaction database before administration."
            )
        raw_checks = audit_result.get("patient_checks")
        checks = raw_checks if isinstance(raw_checks, dict) else {}
        dose_flags = [f for f in checks.get("flags", []) if isinstance(f, dict)]
        not_checked = [n for n in checks.get("not_checked", []) if isinstance(n, dict)]
        dose_lines = [
            f"- {f.get('title', '')} (patient {f.get('measure_label', '')}: "
            f"{f.get('patient_value', '?'):g}). FDA label: \"{(f.get('label_evidence') or {}).get('quote', '')}\""
            if isinstance(f.get("patient_value"), (int, float)) else f"- {f.get('drug', '?')}: {f.get('title', '')}"
            for f in dose_flags
        ]
        for f in dose_flags:
            recommendations.insert(0, f"{f.get('drug', '?')}: {f.get('clinical_action', 'review dose')}")
        for n in not_checked:
            recommendations.append(
                f"Kidney dosing for {n.get('drug', '?')} not checked: enter {n.get('measure_label', 'kidney function')}."
            )
        if not checks:
            dose_section = "Not assessed (no kidney function entered)."
        elif dose_lines:
            dose_section = chr(10).join(dose_lines)
        else:
            dose_section = "No label dose adjustments triggered for the values entered."
        recommendations.append(
            "Pharmacist to confirm the final regimen, hepatic dosing, and monitoring plan."
            if checks and not not_checked
            else "Pharmacist to confirm the final regimen, renal/hepatic dosing, and monitoring plan."
        )

        generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        return f"""CLINICAL PHARMACY REVIEW DRAFT (SBAR)
======================================================
DATE/TIME: {generated}
PATIENT:   {patient_name} (Age: {age})
SETTING:   Community ambulatory / polypharmacy review
STATUS:    Decision-support draft — requires pharmacist verification

[S] SITUATION
-------------
Automated screening found {len(critical)} critical interaction(s), {len(moderate)}
monitoring/timing issue(s), and {len(unknown)} unverified medication(s).
Safety index: {audit_result.get('safety_score', 'n/a')}/100. Knowledge-base coverage:
{audit_result.get('coverage_pct', 'n/a')}%.

[B] BACKGROUND
--------------
Active medication list ({len(med_names)} verified agents):
{', '.join(med_names) if med_names else 'None verified.'}

Unverified agents:
{', '.join(unknown) if unknown else 'None.'}

[A] ASSESSMENT
--------------
Critical interactions:
{chr(10).join(critical_lines) if critical_lines else 'None detected in the demo knowledge base.'}

Timing / monitoring issues:
{chr(10).join(moderate_lines) if moderate_lines else 'None detected in the demo knowledge base.'}

Kidney-function / age dosing (FDA label thresholds):
{dose_section}

[R] RECOMMENDATION
------------------
{chr(10).join(f'{index}. {text}' for index, text in enumerate(recommendations, 1))}

DISCLAIMER
----------
{DISCLAIMER}

Generated by PharmaGuard AI. This draft is not a prescription or a substitute for
professional clinical judgment.
"""
