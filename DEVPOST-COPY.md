# Devpost Copy — Paste-Ready (DSH Hacks V2)

**Event:** DSH Hacks V2 (AI × Healthcare) · Devpost submission
**Project:** PharmaGuard AI
**Repo:** https://github.com/shahaman098/pharmaguard-ai
**Run locally:** `python3 server.py --port 8080` (no install step; see README)
**Video:** see the demo video link on the Devpost page

---

## Project Name

**PharmaGuard AI**

## Elevator Pitch (under 60 characters)

Scan prescriptions. Catch dangerous interactions. Fix the schedule.

---

## Full Markdown Description (paste into “About the Project”)

### 💡 Inspiration

Adverse drug events are a leading preventable cause of emergency visits, and polypharmacy is routine for older adults. A patient may see a cardiologist, a primary care doctor, and an urgent-care clinician in the same month — and no one sees the whole medication list.

The dangerous gaps are often ordinary: warfarin plus an NSAID, a statin plus a strong CYP3A4 inhibitor, calcium binding ciprofloxacin in the gut, or levothyroxine and iron taken together. Most tools stop at a generic warning. We wanted to close the last mile: **detect the conflict, resolve the timing where possible, and hand the patient and clinician something actionable.**

### ⚙️ What It Does

PharmaGuard AI is an end-to-end prescription-safety co-pilot:

1. **Read the regimen from a label photo.** The app uses Tesseract.js, an LSTM-based OCR engine, to read a prescription label in the browser, then proposes medicines and doses for the user to confirm. Confirmed doses flow through the audit and schedule. The image never leaves the browser.
2. **Screen against a deterministic knowledge base.** 52 medicines and 77 curated rules cover CYP450 interactions, renal clearance, pharmacodynamic synergy, QT prolongation, bleeding, hyperkalemia, and GI chelation. Results are reproducible and auditable.
3. **Fail closed, not open.** If a medicine is not in the demo knowledge base, the app marks it **UNVERIFIED** and refuses to call the regimen safe. This was a deliberate design choice: a false “safe” is worse than an honest “I don’t know.”
4. **Resolve timing with a real constraint solver.** A deterministic backtracking scheduler enforces fasting windows, meal alignment, bedtime placement, twice-daily intervals, and 3–4 hour chelation spacing. It reports unresolved conflicts instead of pretending they were fixed.
5. **Hand off to the care team.** One click generates a structured SBAR draft with the verified interactions, unverified medicines, timing issues, and monitoring recommendations.
6. **Give the patient an action.** Plain-language advice and a `.ics` calendar export add every scheduled dose to a phone calendar with alarms.

### 🛠️ How We Built It

- **Perception layer:** Tesseract.js OCR runs locally in the browser. Recognized text is parsed against a token-aware alias index of generic names, US brand names, and common abbreviations.
- **Safety layer:** a pure-Python deterministic engine. Drug resolution is exact/token-based (never substring matching), so `"iron"` can never resolve to `"spironolactone"`.
- **Optimization layer:** a backtracking search over interval constraints. The solver checks meal/fasting rules, minimum intra-dose intervals, and interaction-driven spacing, then reports the reasons for every move.
- **Interface:** a responsive single-page clinical UI with a regimen panel, risk score, interaction map, 24-hour timeline, patient guide, and SBAR modal. Vanilla HTML/CSS/JS — no framework overhead.
- **API:** a zero-dependency Python HTTP server exposing `/api/audit`, `/api/reschedule`, `/api/sbar`, `/api/drugs`, and `/api/meta`.
- **Verification:** 46 automated tests covering aliases, high-yield interactions, fail-safe behavior, SBAR structure, scheduler spacing, meal/fasting placement, weekly/PRN handling, label dose overrides, large-regimen fallback, determinism, and day-window bounds.

### 🧗 Challenges We Ran Into

- **Safety-critical UX:** A risk score of “100” is misleading if the app silently ignored an unknown medicine. We redesigned the audit to expose coverage and unverified medicines, and to cap the score when the regimen is incomplete.
- **Real scheduling, not a lookup table:** Our first scheduler was a per-drug switch statement. We replaced it with a constraint search so the schedule is derived from rules and verifiable with property tests.
- **Noisy OCR:** Labels contain pharmacy names, directions, refill text, and dosage noise. We built a human-confirmation step rather than auto-adding medicines, because OCR errors in a safety tool are unacceptable.
- **Clinical honesty:** We deliberately avoided claiming “100% sensitivity” from a small self-authored test set. The README, one-pager, and SBAR all state the scope and limitations.

### 🏆 Accomplishments We’re Proud Of

- A complete, working loop: **label photo → verified regimen → interaction map → rescheduled timeline → calendar export → SBAR draft.**
- A genuinely fail-safe audit that surfaces unknown medicines instead of hiding them.
- A real interval-constraint scheduler with deterministic, testable output.
- A focused demo knowledge base (52 drugs, 77 rules) that a judge can audit in the repo.
- 46/46 tests passing with no external Python dependencies.

### 📚 What We Learned

- In healthcare AI, the model is not the product. **The safety architecture is the product.** Separating perception (AI) from clinical decisions (deterministic rules) makes the system easier to explain, test, and trust.
- The most valuable output is often the next action, not the alert: a safe time, a calendar entry, or a note the pharmacist can act on.
- Honest limitations increase credibility. “Unverified” is a feature, not a failure.

### 🚀 What’s Next

- Integrate a licensed drug-interaction dataset and a clinician review workflow.
- Add FHIR/Medication List import for real electronic health records.
- Validate OCR across real bottle photos, lighting conditions, and label formats.
- Add renal/hepatic dose checks and indication-specific contraindications.
- Pilot with community pharmacies and caregiver groups.

### 🤖 AI Usage Disclosure

We used AI coding assistants for scaffolding, test-case synthesis, and documentation editing. The clinical rule curation, safety architecture, solver design, and final verification were human-reviewed. The product itself uses AI for **perception only** (browser OCR); all interaction and scheduling decisions are deterministic and reproducible.

### 🧪 Verification & Limitations

- **46 automated tests pass** (`python3 -m unittest discover tests -v`).
- The tests cover 20+ curated high-yield interaction pairs and scheduler properties.
- The knowledge base is a **curated demo subset**, not a validated clinical database.
- This is not a clinical validation study, and the app is not for real clinical use.

### 🔗 Try It Out

- **GitHub:** https://github.com/shahaman098/pharmaguard-ai
- **Local:** `python3 server.py --port 8080` → `http://localhost:8080`
- **Demo cases:** Cardiac polypharmacy, serotonin risk, thyroid + minerals, unverified medicine, no known interactions.

### Built With

`python`, `javascript`, `html5`, `css3`, `tesseract.js`, `ocr`, `constraint-solver`, `rest-api`, `healthcare`, `clinical-pharmacology`, `sbar`
