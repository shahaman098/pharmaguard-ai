# PharmaGuard AI — Submission Kit (DSH Hacks V2)

**Final Submission Lock:** Sunday 15 Nov, 07:45 UTC (11:45 PM PST)
**Devpost Portal:** https://dsh-hacks-v2.devpost.com

---

## 0. Sequence of Execution (Strict Order)

Follow these steps in order to guarantee a flawless submission with zero last-minute panic:

```
[Step 1: Test & Verify App] ──> [Step 2: Generate One-Page PDF] ──> [Step 3: Record Demo Video]
                                                                             │
[Step 6: Submit & Incognito QA] <── [Step 5: Fill Devpost Form] <── [Step 4: Push GitHub & Zip]
```

---

## Step 1: Verify the Local Application & Run Test Suite
Open terminal in `/Users/krishshah/Hackathons/DSH Hacks V2`:
```bash
# 1. Run unit test suite:
python3 -m unittest discover tests

# 2. Launch the local web application:
python3 server.py --port 8080

# 3. Open in browser:
http://localhost:8080
```
Verify:
- Presets load with one click.
- "Run Safety Audit" displays red/amber interaction cards.
- "De-conflict Schedule" renders the 24-hour visual schedule.
- "Export Clinical SBAR Memo" copies to clipboard cleanly.

---

## Step 2: Generate the One-Page Project PDF
The hackathon officially requires a **One-Page Project Description PDF**.
We have generated `ONE-PAGE-SUMMARY.html` formatted with print CSS specifically calibrated to a single A4/Letter page.

1. Open `ONE-PAGE-SUMMARY.html` in Chrome / Safari / Edge:
   ```bash
   open ONE-PAGE-SUMMARY.html
   ```
2. Press `Cmd + P` (Print).
3. Set destination: **Save as PDF**.
4. Check margins: **Default** or **Minimum**; enable **Background graphics**.
5. Save as `PharmaGuard-AI-One-Page-Summary.pdf`.

---

## Step 3: Record the Demo Video (Target 2:15 – 2:45)
1. Use Loom, QuickTime Screen Recording, or OBS.
2. Follow the exact timed cues in `DEMO-SCRIPT.md`.
3. Check video length with our zero-dependency verification tool:
   ```bash
   python3 check_video.py path/to/your-demo.mp4
   ```
   *Confirm it prints: `PASS (inside 2:00-3:00)`.*
4. Upload to YouTube as **Unlisted** (or Public). Title it: `PharmaGuard AI — DSH Hacks V2 Demo`.

---

## Step 4: Push GitHub Repository & Create Submission ZIP
1. Initialize and push your repository to your GitHub account:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: PharmaGuard AI complete clinical safety engine and web app"
   # Create a public repo on GitHub named 'pharmaguard-ai' and push:
   git remote add origin https://github.com/<YOUR_USERNAME>/pharmaguard-ai.git
   git branch -M main
   git push -u origin main
   ```
2. Create the clean project ZIP file for Devpost:
   ```bash
   zip -r dsh-hacks-v2-submission.zip . -x "*.git*" "*.DS_Store*" "*__pycache__*"
   ```

---

## Step 5: Fill the Devpost Submission Form
1. Go to `https://dsh-hacks-v2.devpost.com` and click **"Enter a submission"**.
2. **Project Name:** `PharmaGuard AI`
3. **Elevator Pitch:** `Multimodal prescription safety & polypharmacy co-pilot.`
4. **Description:** Copy the full Markdown text from `DEVPOST-COPY.md`.
5. **Video URL:** Paste the YouTube link.
6. **Files:** Upload `PharmaGuard-AI-One-Page-Summary.pdf` and `dsh-hacks-v2-submission.zip`.
7. **GitHub URL:** Paste your public repository link.
8. **Tags:** Copy from `DEVPOST-ANSWERS.md`.
9. Click **Save & Submit**. (Note: You can continue editing your submission until the deadline lock).

---

## Step 6: Logged-Out Incognito QA Audit
Open an **Incognito / Private browser window** and verify:
- [ ] Devpost submission page loads publicly without login prompt.
- [ ] YouTube demo video plays immediately with clear audio and 1080p video.
- [ ] GitHub repository link opens without a 404 error.
- [ ] One-page PDF preview is readable.
- [ ] No placeholder text (e.g. `[TODO]`, `username`) left in the submission copy.
