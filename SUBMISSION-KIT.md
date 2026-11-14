# PharmaGuard AI — Submission Kit (DSH Hacks V2)

**Submission lock:** Nov 14, 2026 · 11:45 PM PST (Nov 15 · 07:45 UTC)
**Devpost:** https://dsh-hacks-v2.devpost.com
**Repo:** https://github.com/shahaman098/pharmaguard-ai

---

## 0. Status

| Deliverable | Status |
|---|---|
| Working prototype | ✅ Complete: OCR intake, audit, interaction map, solver, calendar, SBAR |
| Public GitHub repo | ✅ Live at the URL above |
| Tests | ✅ 46/46 passing |
| One-page PDF | ⏳ Print `ONE-PAGE-SUMMARY.html` to PDF |
| Demo video | ⏳ Record from `DEMO-SCRIPT.md` (2:30 target) |
| Live demo URL | ⏳ Deploy with `render.yaml` / `Procfile`, then add the URL |
| Devpost submission | ⏳ Paste from `DEVPOST-COPY.md` |

---

## 1. Verify the app locally

```bash
cd "/Users/krishshah/Hackathons/DSH Hacks V2"

# 1. Tests
python3 -m unittest discover tests -v

# 2. Server
python3 server.py --port 8080

# 3. Open
open http://localhost:8080
```

Smoke test:

- [ ] **Cardiac polypharmacy** shows **2 Critical** and **3 Timing / monitoring**, score 5/100.
- [ ] **Alerts & interaction map** shows both critical cards and the SVG map.
- [ ] **24-hour schedule** shows fasting levothyroxine, spaced calcium, bedtime simvastatin.
- [ ] **Why this schedule** lists the spacing decisions and solver status.
- [ ] **Add to calendar** downloads `pharmaguard-schedule.ics`.
- [ ] **Export SBAR** opens a draft with all four sections and the disclaimer.
- [ ] **Unverified medicine** preset shows `INCOMPLETE — UNVERIFIED MEDICATIONS`, 75/100, 67% verified.
- [ ] **Scan prescription label → Try a sample label** detects six medicines and doses. (First run may take 10–20s while OCR loads.)
- [ ] **Re-optimize** re-runs the solver and shows a toast.
- [ ] No console errors in DevTools.

---

## 2. Generate the one-page PDF

1. Open `ONE-PAGE-SUMMARY.html` in Chrome/Safari/Edge.
2. `Cmd + P` → **Save as PDF**.
3. Paper: **Letter**; margins: **Default**; enable **Background graphics**.
4. Confirm it is exactly **one page**.
5. Save as `PharmaGuard-AI-One-Page-Summary.pdf`.

---

## 3. Record the demo video

Follow `DEMO-SCRIPT.md`.

- [ ] 1080p, clear audio, real cursor.
- [ ] Show the label scan, audit, interaction map, schedule, calendar export, SBAR, and fail-safe demo.
- [ ] Do not claim clinical validation or “100% accuracy.”
- [ ] Duration 2:00–3:00.
- [ ] Verify with `python3 check_video.py path/to/demo.mp4`.
- [ ] Upload to YouTube as **Unlisted** or **Public**.

---

## 4. Deploy a live demo (recommended)

The server already binds `0.0.0.0` and reads `$PORT`.

**Render (free tier):**
1. New → **Blueprint** → connect `shahaman098/pharmaguard-ai`.
2. Render reads `render.yaml`.
3. Wait for the deploy, open the URL, and verify `/api/health`.
4. Add the URL to the README, one-pager, and Devpost form.

**Any other host:** start command `python3 server.py`, environment `PORT` provided by the host. No build step and no pip install required.

> The OCR library loads from a CDN. If the host blocks it, the paste-text fallback and manual entry still work.

---

## 5. Fill the Devpost form

1. **Project name:** `PharmaGuard AI`
2. **Elevator pitch:** `Scan prescriptions. Catch dangerous interactions. Fix the schedule.`
3. **Description:** paste the section starting at `### 💡 Inspiration` through the end of `DEVPOST-COPY.md` (skip the metadata header).
4. **Video:** paste the YouTube/Vimeo URL.
5. **Files:** upload `PharmaGuard-AI-One-Page-Summary.pdf` and the source ZIP.
6. **GitHub:** `https://github.com/shahaman098/pharmaguard-ai`
7. **Thumbnail (if asked):** upload `thumbnail.png` (1200×675).
8. **Tags:** from `DEVPOST-ANSWERS.md`.
9. **Prize categories:** Main track; optionally **Best Research-Oriented Project (YRI)** and **Tin Computer Growth Plan**.
10. Click **Save & Submit**. You can edit until the lock.

Create the ZIP:

```bash
zip -r dsh-hacks-v2-submission.zip . \
  -x "*.git*" ".notes/*" "*.DS_Store*" "*__pycache__*" "*.mp4" "*.mov" "*.zip"
```

---

## 6. Logged-out QA

Open an incognito window and check:

- [ ] Devpost page loads without login.
- [ ] Video plays immediately with audio.
- [ ] GitHub repo loads without a 404 and shows the README.
- [ ] One-page PDF is readable and one page.
- [ ] ZIP downloads and contains `server.py`, `pharmaguard/`, `static/`, `tests/`.
- [ ] No unresolved placeholders like `<YOUR_USERNAME>` or `[TODO]` in the submission copy. (Local `localhost` run commands are fine.)
- [ ] Live demo URL works (if deployed).
- [ ] Submission says “46 tests,” “52 drugs,” “77 rules,” not “100% accuracy.”

---

## 7. Final freeze checklist

- [ ] Deadline converted to local time and an alarm set 2 hours before.
- [ ] Repo is public and the latest commit is pushed.
- [ ] `python3 -m unittest discover tests` passes from a clean clone.
- [ ] Video URL is public/unlisted and playable in incognito.
- [ ] PDF is attached and one page.
- [ ] Submission saved **and** confirmed on the Devpost page.
