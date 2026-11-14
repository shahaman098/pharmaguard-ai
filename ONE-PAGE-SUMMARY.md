# PharmaGuard AI — One-Page Project Summary

**DSH Hacks V2 · AI × Healthcare**
**Repo:** https://github.com/shahaman098/pharmaguard-ai · **Live demo:** _(add deployed URL)_
**Demo video:** _(add video URL)_

---

## 1. The problem

Adverse drug events are a leading preventable cause of emergency visits, and polypharmacy — five or more medicines across multiple prescribers — is routine for older adults. The highest-risk gaps are ordinary: warfarin plus an NSAID, a statin plus a strong CYP3A4 inhibitor, calcium binding ciprofloxacin in the gut, or levothyroxine and iron taken together.

Most tools stop at a generic warning. They do not resolve the timing, and they do not give the patient or clinician a next action.

## 2. The solution

PharmaGuard AI closes the last mile:

1. **Read the regimen from a label photo.** LSTM-based browser OCR proposes medicines and doses; the user confirms. Images never leave the device.
2. **Screen deterministically.** A 52-drug, 77-rule demo knowledge base covers CYP450, renal clearance, pharmacodynamic synergy, QT, bleeding, hyperkalemia, and GI chelation. Outputs are reproducible and auditable.
3. **Fail closed.** Medicines outside the knowledge base are marked **UNVERIFIED**; the app refuses to call the regimen safe. Coverage is shown explicitly.
4. **Resolve timing with a real solver.** A backtracking constraint search enforces fasting windows, meals, bedtime, BID intervals, and 3–4 hour chelation spacing. It reports unresolved conflicts instead of hiding them.
5. **Hand off.** One-click SBAR draft for pharmacist review, plain-language patient advice, and a `.ics` calendar export with dose alarms.

## 3. Architecture

```
Label photo → browser OCR → human confirmation → /api/audit
                                                    │
                          deterministic interaction engine
                          (aliases, rule graph, coverage, risk index)
                                                    │
                          /api/reschedule → backtracking constraint solver
                                                    │
                          daily timeline · weekly/PRN · unresolved report · .ics
                                                    │
                          /api/sbar → pharmacist-review SBAR draft
```

**Design principle:** AI for perception, deterministic rules for safety, deterministic search for scheduling. No generative model makes a clinical call.

## 4. Verification

- **35/35 automated tests pass** (`python3 -m unittest discover tests -v`).
- Coverage includes 20+ high-yield interaction pairs, alias regressions, unknown-drug fail-safe behavior, SBAR structure, chelation spacing, fasting/meal/bedtime placement, weekly/PRN handling, determinism, and day-window bounds.
- The suite is an engineering check on a curated demo set — **not** a clinical validation study.

## 5. Impact and feasibility

- **Patient:** a safe daily schedule and a plain-language explanation, exported to the calendar they already use.
- **Caregiver:** one place to see the whole regimen and the exact questions to ask.
- **Pharmacist/physician:** a structured SBAR draft with verified interactions, unverified medicines, and monitoring recommendations.
- **Feasibility:** zero Python dependencies, no database, no accounts, no stored patient data. Deployable on a small web service; OCR runs in the browser.

## 6. Limitations

- The knowledge base is a curated demonstration subset, not a licensed clinical database.
- OCR requires human confirmation; it can misread labels.
- The scheduler optimizes timing, not renal/hepatic dosing or indication appropriateness.
- Not for real clinical use.

## 7. Why it can win

A complete, working loop with a defensible safety architecture: **multimodal intake → deterministic interaction detection → real constraint-based resolution → patient and clinician artifacts.** It is honest about its limits, and every claim in the submission is reproducible from the repository.

**Stack:** Python 3 (stdlib), vanilla HTML/CSS/JS, Tesseract.js, custom constraint solver.
**License:** MIT.
