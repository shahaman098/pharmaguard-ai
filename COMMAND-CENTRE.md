# DSH Hacks V2 — Strategy & Status

**Event:** DSH Hacks V2 — global student online hackathon (AI × Healthcare)
**Organizers:** DeltaForge Hacks, NXT Horizon, STEMise
**Submission lock:** Nov 14, 2026 · 11:45 PM PST (Nov 15 · 07:45 UTC)
**Judging:** Nov 15–22 · **Winners:** Nov 23
**Repo:** https://github.com/shahaman098/pharmaguard-ai

> This file replaces the earlier strategy notes. Prize details, deadlines, and claims here are the verified ones.

---

## 1. Verified event facts

| Item | Reality |
|---|---|
| Participants | 1,243 registered |
| Submissions in gallery | 227+ at the time of writing |
| Judging criteria | **Idea, Implementation, Design, Presentation** (no published weights) |
| Judging format | Asynchronous review of the Devpost page, video, repo, and one-pager |
| Overall prizes | 1st, 2nd, 3rd (sponsor credits: Momen, Adaption Labs, CodeCrafters, Devswarm, Cleanshot, AoPS) |
| Other prizes | Tin Computer Growth Plan (up to 100 teams) and Best Research-Oriented Project (YRI) |
| Requirements | Working project, demo video, one-page PDF, public GitHub repo or code PDF |

There is **no $100 cash prize**. The `$100k+` headline is the aggregate value of sponsor credits, not cash.

---

## 2. Competitive read

The medication space is not empty. Adjacent entries in the public gallery include:

- **Tabble-It** — medication management for patients, caregivers, and pharmacies.
- **GenMed** — AI prescription decoding and medicine guidance.
- **Medi Bridge** — real-time pharmacy/hospital medicine availability.

Most entries, however, are shallow AI wrappers. The winning wedge is **execution + a defensible safety architecture**, not a broader feature list.

---

## 3. Positioning

> **"AI perception + deterministic clinical safety + real constraint resolution."**

PharmaGuard is not an AI doctor and does not let a generative model make clinical calls:

1. **Perception:** browser OCR reads a label photo; the user confirms the result.
2. **Safety:** a 52-drug, 77-rule deterministic engine detects interactions and refuses to certify unknown medicines.
3. **Resolution:** a backtracking constraint solver builds a 24-hour schedule with fasting, meal, bedtime, interval, and chelation constraints.
4. **Handoff:** SBAR draft, plain-language advice, and `.ics` calendar export.

This story is easy to explain in 30 seconds, defensible under code review, and visually demoable.

---

## 4. What shipped

- Label OCR intake with human confirmation and paste fallback.
- 52-drug / 77-rule knowledge base with alias-safe resolution.
- Fail-safe `UNVERIFIED` state and coverage accounting.
- Backtracking scheduler with explicit adjustments and unresolved-conflict reporting.
- Interaction map, 24-hour timeline, weekly/PRN buckets.
- Patient advice, SBAR draft, and `.ics` calendar export.
- 35 automated tests, all passing.
- Deployment configs (`render.yaml`, `Procfile`, `Dockerfile`).

---

## 5. Remaining owner tasks

1. Deploy a live URL (Render blueprint or any host with `$PORT`).
2. Record the 2:30 demo video from `DEMO-SCRIPT.md`.
3. Print `ONE-PAGE-SUMMARY.html` to a one-page PDF.
4. Fill the Devpost form from `DEVPOST-COPY.md` and `DEVPOST-ANSWERS.md`.
5. Run the incognito QA checklist in `SUBMISSION-KIT.md`.
6. Submit at least 2 hours before the lock.

---

## 6. Risk register

| Risk | Status | Mitigation |
|---|---|---|
| False “safe” on an unknown drug | Fixed | Fail-closed `UNVERIFIED` state with visible coverage |
| “Iron” resolving to spironolactone | Fixed | Token-aware alias index + regression test |
| Scheduler is a lookup table | Fixed | Backtracking constraint solver + property tests |
| Claims exceed the build | Fixed | All docs rewritten to match shipped features |
| No public repo | Fixed | Repo is live and pushed |
| No video/PDF yet | Open | Owner tasks above |
| Overclaiming clinical accuracy | Fixed | “35 tests on a curated demo set — not clinical validation” |

---

## 7. Judge-facing proof points

- Open the repo and run `python3 -m unittest discover tests -v` → 35/35.
- Open the app, load the cardiac case, and see two critical interactions plus timing resolution.
- Type an unknown medicine and watch the app refuse to call the regimen safe.
- Export the schedule to a calendar and the SBAR draft for a clinician.
- Read `BENCHMARK-REPORT.md` for the honest scope and limitations.
