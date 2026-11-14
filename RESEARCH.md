# PharmaGuard AI — Research-Oriented Project Statement

**For:** DSH Hacks V2 · Best Research-Oriented Project (YRI)
**Project:** PharmaGuard AI — a fail-safe, deterministic prescription-safety and scheduling prototype
**Repo:** https://github.com/shahaman098/pharmaguard-ai

> This is a research-oriented engineering statement, not a clinical trial or a validated diagnostic study. The claims are scoped to the artifact and the test suite in the repository.

---

## Abstract

Polypharmacy creates a last-mile safety problem: interaction alerts are common, but **timing resolution and clinician handoff are rare**. PharmaGuard AI explores a safety-first architecture in which AI is used only for perception (label OCR), while interaction detection and scheduling are deterministic and auditable. The prototype combines a 52-drug, 77-rule knowledge base, a fail-closed unknown-medication policy, a backtracking interval-constraint scheduler, and two artifacts (an SBAR draft and a calendar export). We evaluate the artifact with 45 engineering tests covering interaction detection, alias resolution, fail-safe behavior, and scheduling properties. We report the scope and limitations explicitly and outline the clinical validation work required before any real-world use.

---

## 1. Research question

**Can a small, deterministic, fail-safe system close the “detect → resolve → hand off” loop for polypharmacy better than a generic LLM wrapper?**

Sub-questions:

1. Can drug-name resolution be made robust to brand/generic variation without dangerous substring matches?
2. Can scheduling constraints (fasting, meals, intervals, chelation) be solved explicitly and reproducibly?
3. Does a fail-closed unknown-medication policy improve the safety posture of a demo CDS tool?
4. What artifacts make the output actionable for patients and clinicians?

---

## 2. Motivation and related work

- **Adverse drug events (ADEs)** are a major preventable source of morbidity and emergency care. Public-health agencies and clinical societies have long emphasized medication reconciliation and interaction screening.
- **Clinical decision support (CDS)** systems can reduce errors, but alert fatigue is a well-documented failure mode. Generic, non-actionable warnings are often ignored.
- **Polypharmacy** guidelines (e.g., the AGS Beers Criteria) emphasize avoiding inappropriate medications and reviewing the whole regimen, not just pairwise alerts.
- **LLM-based health assistants** are fluent but probabilistic; using them for safety-critical interaction calls creates reproducibility and hallucination risks.
- **Constraint scheduling** is well studied in operations research; medication timing is a natural interval-constraint problem with fasting, meal, and spacing rules.

PharmaGuard’s contribution is architectural rather than pharmacological: it separates **perception (AI)** from **safety (deterministic rules)** from **resolution (constraint search)**, and makes the unknowns visible.

---

## 3. System design

### 3.1 Perception layer

- Tesseract.js (LSTM-based OCR) runs in the browser.
- OCR text is parsed against a token-aware alias index built from generic names, US brand names, and common abbreviations.
- Every detection is presented for **human confirmation**; the system never silently adds a medicine from OCR.

### 3.2 Safety layer

- A curated 52-drug registry with 77 rules.
- Rule categories: CYP450, renal clearance, pharmacodynamic synergy, QT prolongation, bleeding, hyperkalemia, chelation/absorption, therapeutic duplication.
- **Fail-closed policy:** unknown drugs are returned as `unknown_drugs`, coverage drops, and the overall status becomes `INCOMPLETE — UNVERIFIED MEDICATIONS`. The score is capped so the regimen cannot appear fully safe.
- **Alias resolution:** exact and token-sequence matching only. Regression test: `"Iron"` must resolve to `ferrous_sulfate`, not `spironolactone`.

### 3.3 Resolution layer

- A deterministic backtracking search assigns each dose to a minute-level time.
- Hard constraints: fasting windows, meal alignment, bedtime placement, minimum intra-dose intervals, interaction-driven spacing, critical-pair administration separation.
- Soft preferences: distance from the preferred period, meal alignment.
- Output: daily timeline, weekly/PRN buckets, `adjustments_made`, `unresolved`, and solver metadata (nodes explored, relaxation stage).
- If hard spacing cannot be met, the solver relaxes in stages and reports the unresolved conflict rather than hiding it.

### 3.4 Handoff layer

- SBAR draft with Situation, Background, Assessment, Recommendation.
- Plain-language patient advice.
- `.ics` calendar export with daily/weekly recurrence and alarms.
- Explicit disclaimer in the UI, SBAR, README, and one-pager.

---

## 4. Evaluation

### 4.1 Method

Engineering verification via `python3 -m unittest discover tests -v`. The suite is designed to test **properties and regressions**, not clinical accuracy.

### 4.2 Results

| Dimension | Result |
|---|---|
| Automated tests | **46/46 passing** |
| Drug registry | 52 medicines |
| Rules | 77 (pairwise + therapeutic duplication) |
| High-yield interaction pairs covered | 20+ |
| Scheduler properties tested | spacing, fasting, meals, bedtime, BID intervals, weekly, PRN, determinism, bounds |
| External Python dependencies | 0 |

Representative tests:

- warfarin + ibuprofen → critical
- simvastatin + clarithromycin → critical
- ciprofloxacin + calcium → moderate, ≥3h spacing
- levothyroxine + iron → moderate, ≥4h spacing and fasting placement
- sertraline + tramadol → critical
- unknown medicine → incomplete, coverage <100%, score capped
- two SSRIs → critical therapeutic duplication
- methotrexate → weekly, never daily
- tramadol → PRN, not auto-scheduled
- repeated runs → identical dose times
- scanned dose overrides → the confirmed label dose reaches the audit and schedule
- 17-drug stress case → every daily medicine receives a scheduled dose

### 4.3 What the evaluation does *not* show

- clinical sensitivity or specificity;
- performance against a licensed interaction database;
- correctness of every mechanism or management recommendation;
- safety in pregnancy, pediatrics, renal/hepatic impairment, or critical illness;
- OCR accuracy across real-world lighting, curvature, glare, or handwriting;
- correctness of parsed label directions/frequencies (the demo uses registry defaults);
- usability with patients or clinicians.

These are explicit non-claims, not omissions.

---

## 5. Threats to validity

| Threat | Mitigation | Residual risk |
|---|---|---|
| Curated rules incomplete | Fail-closed unknowns; visible coverage | A known drug can still have an unmodeled interaction |
| Alias variants missed | Token-aware index + manual entry | Unusual brand names may not resolve |
| OCR errors | Human confirmation; paste fallback | A user could confirm a wrong detection |
| Scheduler is conservative | Reports exact separation and unresolved conflicts | Timing does not fix pharmacodynamic interactions |
| Score is heuristic | Transparent counts and coverage | Not a clinical probability |
| Small test set | Property/regression tests; honest scope | Not a validation study |

---

## 6. Ethical and safety considerations

- **No real patient data** is stored; the app has no database or accounts.
- Patient name/age remain in the browser and are used only in generated artifacts.
- The UI and SBAR explicitly state that the output is a draft for pharmacist review.
- The system refuses to certify a regimen as safe when it contains unknown medicines.
- The project does not claim regulatory clearance or clinical validity.

---

## 7. Future work

1. Replace the demo KB with a licensed interaction dataset.
2. Build a clinician-adjudicated gold-standard set (hundreds of pairs) and report sensitivity, specificity, and false-negative rate with confidence intervals.
3. Validate OCR on a diverse corpus of real bottle photos.
4. Add renal/hepatic dosing and indication-specific contraindications.
5. Conduct a usability study with caregivers and community pharmacists.
6. Integrate FHIR medication lists and a pharmacist review workflow.
7. Pursue clinical decision-support regulatory review before any real-world use.

---

## 8. References (selected)

- U.S. Food and Drug Administration. Drug interaction labeling and prescribing information.
- National Library of Medicine. RxNorm nomenclature.
- Centers for Disease Control and Prevention. Medication safety and adverse drug event resources.
- American Geriatrics Society. AGS Beers Criteria for potentially inappropriate medication use in older adults.
- Standard clinical pharmacology references on CYP450 metabolism, renal clearance, and GI chelation.

> Reference categories are provided for orientation; the implementation uses curated rules, not a licensed dataset. See `BENCHMARK-REPORT.md` for the full verification scope.
