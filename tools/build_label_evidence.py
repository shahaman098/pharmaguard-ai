"""Build the FDA-label evidence cache for PharmaGuard's interaction rules.

For every curated rule (drug A + drug B), this script searches the official
FDA structured product labels (via the public openFDA drug label API) of both
drugs for a mention of the other drug, and records what it finds:

  direct     - the partner drug's name or a specific synonym appears in the label
  class      - only the partner's pharmacological class appears (e.g. "NSAIDs")
  not_found  - neither appears in the searched label sections

Only "direct" counts as corroboration in headline figures. The result is
written to pharmaguard/label_evidence.json and committed, so the app and the
tests never call the network at runtime.

Usage:  python3 tools/build_label_evidence.py
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pharmaguard.interactions import DRUG_REGISTRY, INTERACTION_RULES  # noqa: E402

API = "https://api.fda.gov/drug/label.json"
OUT = ROOT / "pharmaguard" / "label_evidence.json"

# Label sections searched (Rx PLR, older Rx, and OTC "Drug Facts" layouts).
SECTIONS = [
    "boxed_warning", "contraindications", "drug_interactions",
    "warnings_and_cautions", "warnings", "precautions",
    "do_not_use", "ask_doctor_or_pharmacist", "ask_doctor", "stop_use",
    "when_using", "clinical_pharmacology", "pharmacokinetics",
]

# openFDA generic_name used to find each drug's own label.
LABEL_QUERY = {
    "trimethoprim_sulfamethoxazole": "sulfamethoxazole and trimethoprim",
    "ferrous_sulfate": "ferrous sulfate",
    "calcium_carbonate": "calcium carbonate",
    "potassium_chloride": "potassium chloride",
    "insulin": "insulin glargine",
    "levothyroxine": "levothyroxine sodium",
    "iodinated_contrast": "iohexol",
    "lithium": "lithium carbonate",
    "metoprolol": "metoprolol succinate",
    "losartan": "losartan potassium",
    "sildenafil": "sildenafil citrate",
}

# Specific terms that identify the partner drug itself (word-boundary regex).
# Defaults are the drug name plus its brand aliases; overrides avoid false hits
# such as "calcium" inside "calcium channel blockers".
DIRECT_TERMS = {
    "calcium_carbonate": [r"calcium(?!\s+channel)", r"antacids?"],
    "ferrous_sulfate": [r"iron", r"ferrous"],
    "potassium_chloride": [r"potassium chloride", r"potassium supplements?",
                           r"potassium[- ]containing", r"salt substitutes?"],
    "trimethoprim_sulfamethoxazole": [r"trimethoprim", r"sulfamethoxazole", r"co-trimoxazole"],
    # Bare "insulin" is ambiguous in sulfonylurea labels ("non-insulin-dependent",
    # "diet plus insulin"), so only named insulin products count as direct.
    "insulin": [r"insulin (?:glargine|lispro|aspart|detemir|degludec|glulisine)",
                r"(?:regular|nph) insulin", r"insulin therapy with"],
    "iodinated_contrast": [r"iodinated contrast", r"contrast (?:media|agents?|materials?)"],
    "lithium": [r"lithium"],
    "levothyroxine": [r"levothyroxine", r"thyroid hormones?"],
    "nitroglycerin": [r"nitroglycerin"],
    "acetaminophen": [r"acetaminophen"],
}
SKIP_ALIASES = {"asa", "t4", "contrast", "calcium", "potassium", "iron", "bayer"}

CLASS_TERMS = {
    "ibuprofen": [r"nsaids?", r"non-?steroidal anti-?inflammatory"],
    "naproxen": [r"nsaids?", r"non-?steroidal anti-?inflammatory"],
    "aspirin": [r"salicylates?", r"antiplatelet", r"nsaids?"],
    "clopidogrel": [r"antiplatelet", r"p2y12"],
    "warfarin": [r"anticoagulants?", r"vitamin k antagonists?"],
    "simvastatin": [r"statins?", r"hmg-?coa reductase inhibitors?"],
    "atorvastatin": [r"statins?", r"hmg-?coa reductase inhibitors?"],
    "gemfibrozil": [r"fibrates?", r"fibric acid"],
    "clarithromycin": [r"macrolides?", r"strong cyp3a4? inhibitors?"],
    "azithromycin": [r"macrolides?"],
    "ciprofloxacin": [r"(?:fluoro)?quinolones?"],
    "levofloxacin": [r"(?:fluoro)?quinolones?"],
    "fluconazole": [r"azole antifungals?", r"cyp2c9 inhibitors?"],
    "itraconazole": [r"azole antifungals?", r"strong cyp3a4? inhibitors?"],
    "omeprazole": [r"proton pump inhibitors?", r"ppis?"],
    "pantoprazole": [r"proton pump inhibitors?", r"ppis?"],
    "lisinopril": [r"ace inhibitors?", r"angiotensin[- ]converting enzyme"],
    "losartan": [r"angiotensin ii receptor (?:blockers?|antagonists?)", r"arbs?"],
    "spironolactone": [r"potassium[- ]sparing diuretics?"],
    "furosemide": [r"loop diuretics?", r"diuretics?"],
    "hydrochlorothiazide": [r"thiazides?", r"diuretics?"],
    "amlodipine": [r"calcium channel blockers?", r"dihydropyridine"],
    "verapamil": [r"calcium channel blockers?"],
    "metoprolol": [r"beta[- ](?:adrenergic )?block(?:ers?|ing agents?)"],
    "digoxin": [r"cardiac glycosides?", r"digitalis"],
    "amiodarone": [r"antiarrhythmics?"],
    "glipizide": [r"sulfonylureas?"],
    "sertraline": [r"ssris?", r"selective serotonin reuptake inhibitors?", r"serotonergic"],
    "fluoxetine": [r"ssris?", r"selective serotonin reuptake inhibitors?", r"serotonergic"],
    "citalopram": [r"ssris?", r"selective serotonin reuptake inhibitors?", r"serotonergic"],
    "tramadol": [r"opioids?", r"serotonergic"],
    "linezolid": [r"maois?", r"mao inhibitors?", r"monoamine oxidase inhibitors?"],
    "methotrexate": [r"antimetabolites?", r"folate antagonists?"],
    "azathioprine": [r"thiopurines?", r"immunosuppressants?"],
    "allopurinol": [r"xanthine oxidase inhibitors?"],
    "sildenafil": [r"pde-?5 inhibitors?", r"phosphodiesterase"],
    "nitroglycerin": [r"nitrates?", r"nitric oxide donors?"],
    "ondansetron": [r"5-?ht3", r"serotonergic"],
    "phenytoin": [r"antiepileptics?", r"anticonvulsants?", r"cyp3a4? inducers?"],
    "rifampin": [r"rifamycins?", r"strong cyp3a4? inducers?", r"cyp3a4? inducers?"],
    "tizanidine": [r"alpha-?2"],
    "metformin": [r"biguanides?"],
    "insulin": [r"antidiabetic", r"hypoglycemic agents?"],
}


def _fetch(query: str) -> list:
    params = urllib.parse.urlencode({"search": f'openfda.generic_name:"{query}"', "limit": 20})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(f"{API}?{params}", timeout=30) as resp:
                return json.load(resp).get("results", [])
        except Exception as exc:  # network hiccup or 404 (no match)
            if "404" in str(exc):
                return []
            time.sleep(1.5 * (attempt + 1))
    return []


def _pick_label(key: str) -> dict | None:
    """Chooses a single-ingredient label whose generic name matches the drug."""
    query = LABEL_QUERY.get(key, DRUG_REGISTRY[key]["name"].lower())
    results = _fetch(query)

    def score(label: dict) -> tuple:
        names = [n.lower() for n in label.get("openfda", {}).get("generic_name", [])]
        exact = any(n == query.lower() for n in names)
        single = len(names) == 1 and " and " not in names[0] or query in (
            "sulfamethoxazole and trimethoprim",)
        rx = "HUMAN PRESCRIPTION DRUG" in label.get("openfda", {}).get("product_type", [""])[0] if label.get("openfda", {}).get("product_type") else False
        sections = sum(1 for s in SECTIONS if label.get(s))
        return (exact, single, rx, sections, label.get("effective_time", ""))

    results = [r for r in results if r.get("openfda", {}).get("generic_name")]
    if not results:
        return None
    return max(results, key=score)


def _label_text(label: dict) -> str:
    parts = []
    for section in SECTIONS:
        for chunk in label.get(section) or []:
            parts.append(chunk)
    return re.sub(r"\s+", " ", " ".join(parts))


def _terms_direct(key: str) -> list:
    if key in DIRECT_TERMS:
        return DIRECT_TERMS[key]
    entry = DRUG_REGISTRY[key]
    terms = [re.escape(entry["name"].lower())]
    for alias in entry["aliases"]:
        if alias.lower() not in SKIP_ALIASES and len(alias) > 3:
            terms.append(re.escape(alias.lower()))
    return terms


# Matches rejected on human review: the term appears, but not as an interaction.
REVIEW_REJECT = {
    "this condition should be treated with insulin":
        "glipizide label mentions insulin as treatment for ketoacidosis, not an interaction",
    "with glipizide or any other antidiabetic":
        "glipizide label macrovascular-risk statement, not an interaction",
    "diminished antiplatelet effect in patients with two":
        "clopidogrel boxed-warning title about CYP2C19 genotype, not about aspirin",
    "diet plus insulin":
        "glipizide label UGDP mortality warning mentions insulin therapy, not an interaction",
}


# Rule-level review overrides: automated class-level matches judged irrelevant.
REVIEW_OVERRIDE = {
    "glipizide+insulin": "Class terms in the glipizide label are generic diabetes "
                         "statements, not an interaction with insulin.",
    "clopidogrel+aspirin": "Only class hit is a boxed-warning title about CYP2C19 "
                           "genotype, not about aspirin.",
}


def _search(text: str, patterns: list) -> tuple[str, str] | None:
    lowered = text.lower()
    for pattern in patterns:
        for match in re.finditer(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", lowered):
            window = lowered[max(0, match.start() - 60):match.end() + 10]
            if any(phrase in window for phrase in REVIEW_REJECT):
                continue
            start = max(0, match.start() - 220)
            end = min(len(text), match.end() + 220)
            excerpt = text[start:end].strip()
            if start > 0:
                excerpt = "…" + excerpt
            if end < len(text):
                excerpt += "…"
            return text[match.start():match.end()], excerpt
    return None
    return None


def main() -> None:
    retrieved = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    labels: dict = {}
    texts: dict = {}
    for key in DRUG_REGISTRY:
        label = _pick_label(key)
        time.sleep(0.25)  # stay well under openFDA's anonymous rate limit
        if not label:
            labels[key] = None
            print(f"  no label: {key}")
            continue
        set_id = label.get("set_id", "")
        labels[key] = {
            "generic_name": label["openfda"]["generic_name"][0],
            "brand_name": (label["openfda"].get("brand_name") or [""])[0],
            "set_id": set_id,
            "effective_time": label.get("effective_time", ""),
            "dailymed_url": f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={set_id}",
        }
        texts[key] = _label_text(label)
        print(f"  {key}: {labels[key]['generic_name']} ({labels[key]['effective_time']})")

    evidence = {}
    counts = {"direct": 0, "class": 0, "not_found": 0}
    for rule in INTERACTION_RULES:
        a, b = rule["pair"]
        best = {"tier": "not_found"}
        for owner, partner in ((a, b), (b, a)):
            text = texts.get(owner)
            if not text:
                continue
            hit = _search(text, _terms_direct(partner))
            if hit:
                best = {"tier": "direct", "label_of": owner, "matched": hit[0], "excerpt": hit[1]}
                break
            if best["tier"] == "not_found":
                hit = _search(text, CLASS_TERMS.get(partner, []))
                if hit:
                    best = {"tier": "class", "label_of": owner, "matched": hit[0], "excerpt": hit[1]}
        rule_id = f"{a}+{b}"
        if rule_id in REVIEW_OVERRIDE and best["tier"] != "direct":
            best = {"tier": "not_found", "review_note": REVIEW_OVERRIDE[rule_id]}
        if best.get("label_of"):
            best.update(labels[best["label_of"]])
        counts[best["tier"]] += 1
        evidence[f"{a}+{b}"] = best

    payload = {
        "source": "openFDA drug label API (FDA Structured Product Labeling)",
        "api": API,
        "retrieved": retrieved,
        "method": (
            "Both drugs' labels are searched for the partner drug. 'direct' = partner "
            "name or specific synonym found; 'class' = only the partner's drug class "
            "found; 'not_found' = neither found in the searched sections. Only 'direct' "
            "is reported as corroboration. Evidence never changes a rule's severity."
        ),
        "sections_searched": SECTIONS,
        "review_rejections": list(REVIEW_REJECT.values()) + list(REVIEW_OVERRIDE.values()),
        "rule_count": len(INTERACTION_RULES),
        "counts": counts,
        "labels": labels,
        "rules": evidence,
    }
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(counts), "->", OUT)


if __name__ == "__main__":
    main()
