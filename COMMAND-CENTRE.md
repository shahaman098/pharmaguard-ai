# DSH HACKS V2 — COMMAND CENTRE
Compiled: 2026-11-14 ~15:20 UTC · **Deadline: Sunday 15 Nov, 07:45 UTC (11:45 PM PST) — NO extension**

---

## 01 — Situation & Executive Brief
- **Event:** DSH Hacks V2 — Global student online hackathon hosted on Devpost ([dsh-hacks-v2.devpost.com](https://dsh-hacks-v2.devpost.com)).
- **Organizers:** Collaborative youth initiative by **DeltaForge Hacks**, **NXT Horizon**, and **STEMise** (fiscally sponsored by The Hack Foundation / Hack Club).
- **Theme:** **AI × Healthcare** (transitioned from V1's AI × STEM education theme).
- **Prizes:** $100k+ total prize pool featuring:
  - **1st Place Overall:** $100 Cash + $100 Art of Problem Solving (AoPS) Gift Card + $2,000 Momen Credits + 2-Year CodeCrafters VIP ($720) + sponsor perks.
  - **2nd & 3rd Place:** $2,000 Momen Credits + sponsor perks.
  - **Track Awards:** Tin Computer Growth Plan, Best Research-Oriented Project (YRI).
- **Time Remaining:** **~16h25m** as of kickoff.
- **Operating Doctrine:** Universal Command Centre Doctrine (action before endless research, 10/10 idea validation, compressed intelligence sprint, deterministic verification, submission QA).

---

## 02 — Judging Rubric & Scoring Engine
Evaluated across 4 core pillars (equal weighting inferred):
1. **Clinical Insight & Real-World Impact (25%):** Genuine medical pain point, patient safety risk, or clinical operational bottleneck addressed.
2. **Technical Depth & Execution (25%):** Quality of architecture, real multi-step pipeline (not a cosmetic prompt wrapper), deterministic verification, and reliability.
3. **Creativity & Innovation (25%):** Anti-obvious angle; solves the hidden workflow rather than a generic chatbot.
4. **Feasibility & Scalability (25%):** Practical adoption path into healthcare workflows without unrealistic regulatory or technical dependencies.

---

## 03 — Strict Compliance Matrix (Risk-Ordered)
| # | Requirement | Official Specification | Strategy / Status | Risk Level |
|---|---|---|---|---|
| 1 | **Working Prototype** | Functional app, website, or coding prototype with user interaction | Self-contained Python + Modern Web App ready to run locally & live | 🔴 Critical (DQ if mock only) |
| 2 | **Demo Video Duration** | Walkthrough showing problem, features, and live interaction | **Target 2:15 – 2:45** (verified with `check_video.py`) | 🔴 Critical (DQ if missing) |
| 3 | **One-Page Project PDF** | Concise 1-page document detailing purpose and key features | Generated as `ONE-PAGE-SUMMARY.html` (print to PDF) | 🔴 Critical (Explicit Devpost requirement) |
| 4 | **Public GitHub Repo** | Link to public code repository with clean documentation | Push to GitHub, formatted README + tests | 🔴 Critical |
| 5 | **Project ZIP File** | Full source archive uploaded to Devpost | Packaged `dsh-hacks-v2-submission.zip` | 🟡 Medium |
| 6 | **Eligibility** | Students aged 13+ enrolled in educational institution | Solo / Team student declaration | 🟢 Confirmed |
| 7 | **AI Usage Policy** | Explicitly permitted and encouraged | Full transparency statement in writeup | 🟢 Compliant |

---

## 04 — Organiser & Sponsor Intelligence
- **STEMise & DeltaForge Hacks:** Youth-driven STEM ecosystems focused on high-utility tools, clinical/educational access, and youth innovation.
- **Sponsors:**
  - **Art of Problem Solving (AoPS):** Values logical rigor, deep problem-solving, and educational/analytical precision.
  - **Momen:** No-code / full-stack web platform; appreciates extensible API backends and modular UI architecture.
  - **CodeCrafters:** Elite engineering culture; rewards code quality, test coverage, and deterministic algorithms over vague claims.
  - **Tin Computer:** High-performance infrastructure and deployable systems.

---

## 05 — Competitive Landscape & Anti-Obvious Positioning
- **What 90% of entrants build (Crowded Archetypes to AVOID):**
  - Generic "AI Doctor" symptom checker bot that regurgitates WebMD advice.
  - "Mental Health companion" chatbot giving generic therapy platitudes.
  - Basic calorie / fitness tracker dashboard with ChatGPT commentary.
- **Our Strategic Wedge (Anti-Obvious Inversion):**
  - **Target:** **Polypharmacy & Prescription Safety in Vulnerable Patients**.
  - Over 1.3 million emergency department visits annually stem from Adverse Drug Events (ADEs). Elderly patients often take 5 to 10+ daily medications across different prescribing doctors.
  - **The Missing Workflow:** Patients and caregivers have physical bottles, blister packs, and conflicting schedules. They don't need a medical encyclopedia; they need an **autonomous safety engine** that ingests prescriptions, detects hidden drug-drug and food-drug interactions, calculates kinetic absorption conflicts, and generates a **zero-conflict daily schedule** with 1-click clinical escalation notes.

---

## 06 — Strategic Selection: **PharmaGuard AI**
- **Project Name:** **PharmaGuard AI**
- **Tagline:** Multimodal Prescription & Polypharmacy Safety Co-Pilot — detects lethal drug interactions, resolves timing conflicts, and drafts clinical pharmacist escalation notes.
- **Core Loop (30-Second Killer Demo):**
  1. *Upload / Scan:* User uploads prescription bottle labels or enters regimen (e.g. Warfarin, Simvastatin, Clarithromycin, Ciprofloxacin, Ibuprofen, Calcium Carbonate).
  2. *Safety Audit:* Engine scans against RxNorm & clinical interaction matrices; flags severe cytochrome P450 inhibition and kinetic chelation risks.
  3. *Autonomous De-confliction:* Generates an optimal 24-hour administration timeline separating chelating agents and reducing peak serum concentration clashes.
  4. *Clinical Action:* Drafts an SBAR (Situation, Background, Assessment, Recommendation) note ready to copy for the treating physician or pharmacist.
- **Deterministic Proof:** Comprehensive automated test suite validating 100% detection on clinical contraindication gold standards.
