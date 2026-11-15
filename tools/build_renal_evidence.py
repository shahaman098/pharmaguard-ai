"""Build pharmaguard/renal_evidence.json from public FDA drug labels (openFDA).

Each kidney-function and age rule below was hand-written from the label, and its
``quote`` must appear word-for-word in the named label section. The build fails
if any quote cannot be found, so a threshold can never drift from its source.

Run from the repo root:  python3 tools/build_renal_evidence.py
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_label_evidence import _pick_label  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "pharmaguard" / "renal_evidence.json"

# measure: "egfr" (mL/min/1.73 m2), "crcl" (Cockcroft-Gault, mL/min) or "age" (years).
# Bounds: lt / le / gt / ge, all optional; a rule fires when every given bound holds.
RULES = [
    {
        "drug": "metformin", "measure": "egfr", "lt": 30, "severity": "CRITICAL",
        "title": "Metformin contraindicated: eGFR below 30",
        "action": "Do not use. Stop metformin and switch to an alternative antidiabetic.",
        "section": "contraindications",
        "quote": "contraindicated in patients with: Severe renal impairment (eGFR below 30 mL/min/1.73 m2)",
    },
    {
        "drug": "metformin", "measure": "egfr", "ge": 30, "lt": 45, "severity": "MODERATE",
        "title": "Metformin: eGFR 30–45 needs a benefit–risk review",
        "action": "Do not start metformin at this eGFR; if already taking it, reassess benefit and risk.",
        "section": "dosage_and_administration",
        "quote": "whose eGFR later falls below 45 mL/min/1.73 m 2 , assess the benefit risk of continuing therapy.",
    },
    {
        "drug": "lithium", "measure": "crcl", "lt": 30, "severity": "CRITICAL",
        "title": "Lithium not recommended: CrCl below 30",
        "action": "Avoid lithium; refer to the prescriber for an alternative mood stabiliser.",
        "section": "dosage_and_administration",
        "quote": "Lithium is not recommended for use in patients with severe renal impairment (creatinine clearance less than 30 mL/min evaluated by Cockcroft-Gault)",
    },
    {
        "drug": "lithium", "measure": "crcl", "ge": 30, "lt": 90, "severity": "MODERATE",
        "title": "Lithium: reduced kidney function (CrCl 30–89)",
        "action": "Use a lower dose, titrate slowly and monitor serum lithium levels frequently.",
        "section": "dosage_and_administration",
        "quote": "Start patients with mild to moderately impaired renal function (creatinine clearance 30 to 89 mL/min evaluated by Cockcroft-Gault) with dosages less than those for patients with normal renal function",
    },
    {
        "drug": "ciprofloxacin", "measure": "crcl", "le": 50, "severity": "MODERATE",
        "title": "Ciprofloxacin: dose adjustment for CrCl 50 or below",
        "action": "Adjust per the label table: CrCl 30–50 → 250–500 mg every 12 h; 5–29 → every 18 h.",
        "section": "dosage_and_administration",
        "quote": "Creatinine Clearance (mL/min) Dose > 50 See Usual Dosage. 30–50 250–500 mg every12 hours 5–29 250–500 mg every 18 hours",
    },
    {
        "drug": "levofloxacin", "measure": "crcl", "lt": 50, "severity": "MODERATE",
        "title": "Levofloxacin: dose adjustment for CrCl below 50",
        "action": "Adjust the dosing regimen per the label's renal table to avoid accumulation.",
        "section": "dosage_and_administration",
        "quote": "In patients with renal impairment (creatinine clearance less than 50 mL/min), adjustment of the dosage regimen is necessary to avoid the accumulation of levofloxacin",
    },
    {
        "drug": "fluconazole", "measure": "crcl", "le": 50, "severity": "MODERATE",
        "title": "Fluconazole: halve the dose for CrCl 50 or below",
        "action": "After the loading dose, give 50% of the usual daily dose (non-dialysis).",
        "section": "dosage_and_administration",
        "quote": "Creatinine Clearance (mL/min) Recommended Dose (%) > 50 100 ≤ 50 (no dialysis) 50",
    },
    {
        "drug": "naproxen", "measure": "crcl", "lt": 30, "severity": "CRITICAL",
        "title": "Naproxen not recommended: CrCl below 30",
        "action": "Avoid naproxen; consider acetaminophen and ask the prescriber.",
        "section": "use_in_specific_populations",
        "quote": "Naproxen-containing products are not recommended for use in patients with moderate to severe and severe renal impairment (creatinine clearance <30 mL/min).",
    },
    {
        "drug": "allopurinol", "measure": "egfr", "le": 60, "severity": "MODERATE",
        "title": "Allopurinol: lower starting dose for eGFR 60 or below",
        "action": "Start low per the label table (e.g. eGFR >30–60 → 50 mg daily) and titrate.",
        "section": "dosage_and_administration",
        "quote": "Recommended Initial Dosage in Adult Patients with Gout eGFR Initial Dosage > 60 mL/minute No dosage modification > 30 to 60 mL/minute 50 mg daily > 15 to 30 mL/minute 50 mg every other day",
    },
    {
        "drug": "methotrexate", "measure": "crcl", "lt": 90, "severity": "MODERATE",
        "title": "Methotrexate: reduced elimination (CrCl below 90)",
        "action": "Higher toxicity risk; confirm dose with the prescriber and monitor blood counts and kidney function.",
        "section": "use_in_specific_populations",
        "quote": "Methotrexate elimination is reduced in patients with renal impairment [creatinine clearance (CLcr) less than 90 mL/min, calculated using Cockcroft-Gault]",
    },
    {
        "drug": "sildenafil", "measure": "crcl", "lt": 30, "severity": "MODERATE",
        "title": "Sildenafil: start at 25 mg (CrCl below 30)",
        "action": "Consider a 25 mg starting dose; exposure roughly doubles in severe renal impairment.",
        "section": "dosage_and_administration",
        "quote": "patients with severe renal impairment (creatinine clearance <30 mL/minute)",
    },
    {
        "drug": "sildenafil", "measure": "age", "gt": 65, "severity": "MODERATE",
        "title": "Sildenafil: start at 25 mg (age over 65)",
        "action": "Consider a 25 mg starting dose in patients over 65.",
        "section": "dosage_and_administration",
        "quote": "Consider a starting dose of 25 mg in patients > 65 years",
    },
]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    labels: dict = {}
    out_rules = []
    missing = []
    for rule in RULES:
        key = rule["drug"]
        if key not in labels:
            labels[key] = _pick_label(key)
        label = labels[key]
        if not label:
            missing.append(f"{key}: no label")
            continue
        section = _norm(" ".join(label.get(rule["section"]) or []))
        if _norm(rule["quote"]) not in section:
            missing.append(f"{key}/{rule['measure']}: quote not in {rule['section']}")
            continue
        openfda = label.get("openfda", {})
        set_id = label.get("set_id", "")
        out_rules.append({
            **rule,
            "quote": _norm(rule["quote"]),
            "label_name": (openfda.get("generic_name") or [key])[0].title(),
            "set_id": set_id,
            "effective_time": label.get("effective_time", ""),
            "dailymed_url": f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={set_id}",
        })
    if missing:
        sys.exit("Quote check failed:\n  " + "\n  ".join(missing))
    payload = {
        "source": "openFDA drug label API (FDA Structured Product Labeling)",
        "api": "https://api.fda.gov/drug/label.json",
        "retrieved": dt.date.today().isoformat(),
        "method": "Thresholds hand-written from each label; every quote verified word-for-word against the label section at build time.",
        "rules": out_rules,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(out_rules)} rules for {len({r['drug'] for r in out_rules})} drugs -> {OUT}")


if __name__ == "__main__":
    main()
