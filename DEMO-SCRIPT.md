# PharmaGuard AI — Demo Video Script

**Target:** 2:30 (hard limit: 3:00)
**Format:** 1080p screen recording, clear voiceover, real cursor, no fake features.
**Before recording:** run `python3 server.py --port 8080`, open `http://localhost:8080`, and click **Scan prescription label → Try a sample label** once so the OCR worker is warm. Close other tabs and bookmarks.

---

## Timing overview

| Time | Beat | What the viewer sees |
|---|---|---|
| 0:00–0:15 | Problem | Title + the polypharmacy gap |
| 0:15–0:40 | Multimodal intake | Label photo → OCR → confirmed medicines |
| 0:40–1:05 | Safety audit | Critical + timing alerts, interaction map |
| 1:05–1:30 | Resolution | Constraint-based 24-hour schedule |
| 1:30–1:44 | Patient action | One-click calendar export |
| 1:44–2:03 | Clinician handoff | SBAR draft |
| 2:03–2:18 | Fail-safe | Unknown medicine is marked UNVERIFIED |
| 2:18–2:30 | Proof + close | Tests, repo, impact |

---

## Scene-by-scene

### 0:00–0:15 — The problem

**On screen:** PharmaGuard AI title, then a simple stat card: “Adverse drug events are a leading preventable cause of emergency visits.”

**Narration:**
“Older adults often take five, ten, or more medicines prescribed by different clinicians. The dangerous interactions are usually ordinary — an NSAID with warfarin, a statin with a strong antibiotic, calcium with ciprofloxacin. Most tools stop at a warning. We built PharmaGuard to close the loop.”

### 0:15–0:40 — Scan the regimen

**Clicks:**
1. Click **Clear all** (start from a clean regimen).
2. Click **Scan prescription label**.
3. Click **Try a sample label** (or drag in your own bottle photo).
4. Wait for **Detected medicines — confirm before adding**.
5. Point at the six detected medicines and the parsed doses: Warfarin 5 mg, Ibuprofen 400 mg, Ciprofloxacin 500 mg, Clarithromycin 500 mg, Simvastatin 20 mg, Calcium Carbonate 600 mg.
6. Click **Add selected medicines**.

**Narration:**
“PharmaGuard reads the label in the browser with OCR — the photo never leaves the device. It proposes the six medicines and doses, and the user confirms them. That human check matters: OCR is perception, not a clinical decision.”

### 0:40–1:05 — The safety audit

**Clicks:**
1. The audit runs automatically after adding. If needed, click **Run clinical safety audit**.
2. Point at the score card: **2 Critical**, **3 Timing / monitoring**, **100% verified**.
3. Scroll the alert cards and the **interaction map**.
4. Open the Warfarin + Ibuprofen card and the Ciprofloxacin + Calcium card.

**Narration:**
“The deterministic engine finds two critical interactions: warfarin plus ibuprofen, a severe bleeding risk, and simvastatin plus clarithromycin, a CYP3A4-driven rhabdomyolysis risk. It also catches three timing or monitoring issues, including calcium chelating ciprofloxacin. Every alert has a mechanism, a clinical action, and — for 54 of the 73 pairwise rules — the exact sentence from the official FDA label, pulled from openFDA, with a link to DailyMed.”

### 1:05–1:30 — Resolve the schedule

**Clicks:**
1. Click the **24-hour schedule** tab.
2. Point at the 12:30 midday group (calcium + ibuprofen) and the 22:00 simvastatin bedtime dose.
3. Point at the “Why this schedule” notes: ciprofloxacin/calcium 5.5h apart, simvastatin/clarithromycin separated, warfarin/ibuprofen separated for administration safety.
4. Point at the solver line: “all spacing constraints satisfied.”

**Narration:**
“This is not a hardcoded timetable. A backtracking constraint solver enforces fasting windows, meals, twice-daily intervals, bedtime placement, and three-to-four-hour chelation spacing. Here it keeps calcium five and a half hours from ciprofloxacin, puts simvastatin at bedtime, and separates the contraindicated pairs for administration safety. It tells you why every dose moved — and it reports conflicts it cannot fix instead of hiding them.”

### 1:30–1:44 — Patient action

**Clicks:**
1. Click **Add to calendar**.
2. Show the downloaded `pharmaguard-schedule.ics` briefly.

**Narration:**
“One click turns the plan into calendar events with alarms, so the patient or caregiver has the schedule where they will actually see it.”

### 1:44–2:03 — Clinician handoff

**Clicks:**
1. Click **Export SBAR**.
2. Point at the Situation, Background, Assessment, and Recommendation sections.
3. Highlight the unverified-medicine line and the disclaimer.

**Narration:**
“For the clinician, PharmaGuard drafts a structured SBAR note: the verified interactions, the timing issues, the unverified medicines, and the recommended next steps. It is explicitly a draft for pharmacist verification, not an autonomous prescription.”

### 2:03–2:18 — Fail-safe demo

**Clicks:**
1. Close the SBAR modal.
2. Click the **Unverified medicine** demo case.
3. Point at **INCOMPLETE — UNVERIFIED MEDICATIONS**, **75/100**, **67% verified**, and the unverified chip.
4. Show the patient advice line beginning “UNVERIFIED.”

**Narration:**
“This is the part we care about most. If a medicine is not in our knowledge base, PharmaGuard does not guess. It marks the regimen incomplete and tells the patient to ask a pharmacist. A false ‘safe’ is worse than an honest ‘I don’t know.’”

### 2:18–2:30 — Proof and close

**On screen:** terminal with `python3 -m unittest discover tests -v` → `Ran 53 tests — OK`, then the GitHub repo, then the title card.

**Narration:**
“Fifty-three tests cover aliases, high-yield interactions, fail-safe behavior, scheduling constraints, and determinism. The demo knowledge base has 52 medicines and 77 rules. It is open source, zero-Python-dependency, and built for the last mile of medication safety. Thank you.”

---

## Production notes

- **Do not claim** “100% accuracy,” “clinically validated,” or “FDA-approved.” Say “53 tests on a curated demo knowledge base.”
- **Do not show** features that are not in the build. The current build has OCR intake, the audit, the interaction map, the solver, calendar export, patient advice, and SBAR.
- Keep the browser at **100–110% zoom** so the UI text is readable at 1080p.
- Use a real mouse cursor and pause briefly on each result so judges can read it.
- Record audio separately if possible, then align it; a clean voice track matters more than fancy editing.
- If OCR is slow on the recording machine, cut the wait or use the paste-text fallback — but show the real detection result.
- End with the repo URL on screen for at least 2 seconds.

## Verification

```bash
python3 check_video.py path/to/your-demo.mp4
```

Expected: `PASS (inside 2:00-3:00)`.
