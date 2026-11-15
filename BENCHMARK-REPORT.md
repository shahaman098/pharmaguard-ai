# PharmaGuard AI — Verification Report

**Project:** PharmaGuard AI
**Event:** DSH Hacks V2 (AI × Healthcare)
**Knowledge base:** v2.0 · 52 medicines · 77 curated rules
**Test suite:** 53 tests · 53 passing
**Date:** 2026-11-14

> **Scope statement:** This is an engineering verification report, **not** a clinical validation study. The knowledge base is a curated demonstration subset. No sensitivity, specificity, or real-world safety claim is made.

---

## 1. What was verified

| Area | What the tests check | Result |
|---|---|---|
| Drug resolution | Generic names, US brand names, aliases, dose/noise stripping | ✅ |
| Regression | `"Iron"` resolves to `ferrous_sulfate`, **not** `spironolactone` | ✅ |
| Unknown handling | Unknown drugs are surfaced, coverage drops, status becomes incomplete | ✅ |
| Interaction detection | 20+ high-yield pairs across CYP450, renal, serotonergic, chelation, cardiac, endocrine categories | ✅ |
| Deduplication | Duplicate entries collapse without losing the regimen | ✅ |
| SBAR | All four sections present; unverified medicines and disclaimer included | ✅ |
| Scheduler spacing | Ciprofloxacin/calcium ≥ 3h; levothyroxine/iron ≥ 4h | ✅ |
| Scheduler rules | Fasting, meals, bedtime, BID intervals, weekly, PRN | ✅ |
| Scheduler safety | Critical pairs are not co-scheduled; unresolved conflicts reported | ✅ |
| Large regimens | 17-drug stress case always receives a complete schedule | ✅ |
| Label dose overrides | Confirmed scanned doses reach the audit, schedule, and SBAR | ✅ |
| Determinism | Repeated runs produce identical dose times | ✅ |
| Bounds | All doses fall inside the 06:00–23:00 day window | ✅ |

Run it:

```bash
python3 -m unittest discover tests -v
```

Observed:

```text
Ran 53 tests in ~0.03s

OK
```

---

## 2. Curated interaction coverage

The demo knowledge base includes:

| Category | Examples |
|---|---|
| Bleeding / anticoagulation | warfarin + ibuprofen/naproxen/aspirin, aspirin + clopidogrel |
| CYP450 | simvastatin + clarithromycin/itraconazole, warfarin + amiodarone/metronidazole/fluconazole/TMP-SMX, clopidogrel + omeprazole, ciprofloxacin + tizanidine |
| Renal / transport | lithium + NSAIDs/ACE inhibitor, methotrexate + NSAIDs/aspirin, metformin + iodinated contrast |
| Serotonergic | sertraline/fluoxetine/citalopram + tramadol/linezolid |
| Chelation / absorption | ciprofloxacin/levofloxacin + calcium/iron, levothyroxine + calcium/iron, levothyroxine + PPI |
| Cardiac | sildenafil + nitroglycerin, metoprolol + verapamil, digoxin + amiodarone, QT combinations |
| Metabolic / electrolyte | glipizide + insulin, ACE inhibitor/ARB/spironolactone + potassium |
| Therapeutic duplication | two NSAIDs, two SSRIs, two statins, ACE inhibitor + ARB |

Each rule carries a severity, mechanism, clinical action, category, and source note.

---

## 3. Scheduler verification

The scheduler is a deterministic backtracking search, not a lookup table. It enforces:

- fasting windows for levothyroxine, omeprazole, pantoprazole, glipizide, rifampin;
- meal alignment for metformin, ibuprofen, verapamil, metoprolol, and others;
- bedtime placement for simvastatin and tizanidine;
- minimum intra-dose intervals for BID/TID regimens;
- interaction-driven spacing for chelation and absorption conflicts;
- critical-pair separation as an administration-safety floor;
- weekly and as-needed medicines outside the daily timeline.

The API returns:

- `groups` — the daily timeline;
- `weekly` and `prn` — medicines that should not be auto-scheduled;
- `adjustments_made` — why each move happened;
- `unresolved` — constraints the solver could not satisfy;
- `solver` — algorithm, search nodes, relaxation stage.

Example property tests:

| Property | Test | Result |
|---|---|---|
| Ciprofloxacin and calcium are ≥ 3h apart | `test_cipro_calcium_spacing` | ✅ |
| Levothyroxine is fasting and ≥ 4h from iron | `test_levothyroxine_iron_spacing_and_fasting` | ✅ |
| Simvastatin is at bedtime | `test_simvastatin_at_bedtime` | ✅ |
| Metformin BID doses are ≥ 10h apart | `test_bid_doses_are_separated` | ✅ |
| Methotrexate is weekly, never daily | `test_weekly_methotrexate_is_not_daily` | ✅ |
| Tramadol is PRN, not auto-scheduled | `test_prn_medications_are_not_scheduled` | ✅ |
| Warfarin and ibuprofen are not co-scheduled | `test_critical_pairs_are_not_co_scheduled` | ✅ |
| Repeated runs are identical | `test_schedule_is_deterministic` | ✅ |

---

## 4. What is *not* verified

This report does **not** establish:

- clinical sensitivity or specificity;
- performance against a licensed interaction database;
- correctness of every mechanism or management recommendation;
- safety in pregnancy, pediatrics, renal/hepatic impairment, or critical illness;
- OCR accuracy across real-world lighting, curvature, glare, or handwriting;
- usability with patients or clinicians.

The 53 tests are engineering checks on a small curated set. They are useful for regression and demo credibility, not for regulatory or bedside claims.

---

## 5. Threats to validity

| Threat | Mitigation in this build | Remaining risk |
|---|---|---|
| Curated rules may be incomplete | Fail-safe unknown handling; explicit coverage percentage | A known drug can still have an unmodeled interaction |
| Hardcoded aliases may miss variants | Token-aware alias index + manual entry | Unusual brand names may not resolve |
| OCR can misread a label | Human confirmation step; paste fallback | A user could confirm a wrong detection |
| Label directions are not parsed | Registry-default frequencies; UI asks for pharmacist confirmation | A label with a non-default frequency may be scheduled incorrectly |
| Scheduler spacing is conservative | Reports exact separation and unresolved conflicts | Timing does not fix pharmacodynamic interactions |
| Risk score is heuristic | Transparent counts and coverage; no “safe” claim with unknowns | Score is not a clinical probability |

---

## 6. Reproducibility

```bash
git clone https://github.com/shahaman098/pharmaguard-ai.git
cd pharmaguard-ai
python3 -m unittest discover tests -v
python3 server.py --port 8080
```

Expected: 53 tests pass; the app serves at `http://localhost:8080`.

---

## 7. Next validation steps

1. Replace the demo KB with a licensed interaction dataset (e.g., a commercial drug-knowledge base).
2. Build a clinician-adjudicated gold-standard set of at least several hundred pairs.
3. Report sensitivity, specificity, and false-negative rate with confidence intervals.
4. Validate OCR on a diverse corpus of real bottle photos.
5. Run a usability study with caregivers and community pharmacists.
6. Add renal/hepatic dosing and indication-specific contraindications.
7. Pursue clinical decision-support regulatory review before any real-world use.
