# Devpost Submission Form Answers (DSH Hacks V2)

Quick-reference sheet for the Devpost form. Keep every claim consistent with the repo.

---

### Project Name

`PharmaGuard AI`

### Elevator Pitch (under 60 characters)

`Scan prescriptions. Catch dangerous interactions. Fix the schedule.`

### Project Story / Description

Copy the full text from `DEVPOST-COPY.md` → “Full Markdown Description.”

---

### Track & Prize Category Selection

- **Primary:** DSH Hacks V2 main track (AI × Healthcare)
- **Optional:** Best Research-Oriented Project (YRI) — the repo includes `RESEARCH.md`, a verification report, a reproducible test suite, and explicit limitations. Do **not** call it a clinical validation study.
- **Optional:** Tin Computer Growth Plan — the app is a small, deployable web service with zero Python dependencies.

---

### Built With (enter one by one)

- `python`
- `javascript`
- `html5`
- `css3`
- `tesseract.js`
- `ocr`
- `constraint-solver`
- `rest-api`
- `healthcare`
- `clinical-pharmacology`
- `sbar`

---

### Links & URLs

- **GitHub Repository:** https://github.com/shahaman098/pharmaguard-ai
- **Demo Video:** _(paste your unlisted YouTube/Vimeo URL)_
- **Live Demo:** _(paste your deployed URL, if available)_
- **One-Pager PDF:** attach `PharmaGuard-AI-One-Page-Summary.pdf`
- **Source ZIP:** attach `dsh-hacks-v2-submission.zip`

---

### Common Questions

**Q: How does the project address the AI × Healthcare theme?**

A: PharmaGuard uses AI for perception — browser OCR reads a prescription-label photo and proposes medicines and doses for human confirmation. The safety decisions are deliberately deterministic: a 52-drug, 77-rule engine screens for CYP450, renal, pharmacodynamic, QT, bleeding, hyperkalemia, and chelation risks, then a backtracking constraint solver builds a safe 24-hour schedule. The clinician handoff is an SBAR draft for pharmacist review.

**Q: Did you build this during the hackathon period?**

A: Yes. The prototype, knowledge base, solver, tests, and submission materials were developed during the DSH Hacks V2 submission window.

**Q: What makes it different from a generic AI health chatbot?**

A: It does not let a generative model make clinical calls. It reads the label, detects specific interactions with mechanisms and actions, refuses to certify unknown medicines as safe, resolves timing with a real constraint solver, and produces artifacts a patient or pharmacist can act on (calendar export and SBAR draft).

**Q: What are the external dependencies?**

A: The Python server uses only the standard library. The browser loads Tesseract.js from a CDN for OCR; the paste-text fallback and manual entry work without it. There is no database, no account system, and no stored patient data.

**Q: How was the project validated?**

A: 35 automated tests pass, covering alias resolution, 20+ high-yield interaction pairs, unknown-drug fail-safe behavior, SBAR structure, chelation spacing, fasting/meal/bedtime placement, weekly/PRN handling, determinism, and day-window bounds. This is engineering verification on a curated demo set — not a clinical validation study. The limitations are stated in `BENCHMARK-REPORT.md`.

**Q: Is this safe to use for real patients?**

A: No. It is an educational prototype with a curated knowledge base. It is not a validated clinical device and does not replace a pharmacist or physician.

**Q: What would you build next?**

A: A licensed interaction dataset, clinician-adjudicated validation, FHIR medication-list import, renal/hepatic dose checks, real-world OCR validation, and a community-pharmacy pilot.

---

### Submission Checklist

- [ ] Repo is public and the latest commit is pushed.
- [ ] Video is 2:00–3:00 and plays in incognito.
- [ ] One-page PDF is exactly one page.
- [ ] Source ZIP contains `server.py`, `pharmaguard/`, `static/`, `tests/`.
- [ ] No placeholders (`<YOUR_USERNAME>`, `[TODO]`, `localhost`) in the writeup.
- [ ] Claims match the build: 35 tests, 52 drugs, 77 rules, no “100% accuracy.”
- [ ] Submission saved and confirmed.
