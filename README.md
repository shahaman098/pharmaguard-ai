# PharmaGuard AI 🛡️💊
> **Multimodal Prescription Safety & Polypharmacy Co-Pilot**  
> *Built for DSH Hacks V2 (AI × Healthcare)*

[![Tests](https://img.shields.io/badge/tests-12%2F12%20passing-brightgreen)](#clinical-benchmarks)
[![Zero Cloud Bloat](https://img.shields.io/badge/dependencies-0%20external-blue)](#architecture)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Theme: AI × Healthcare](https://img.shields.io/badge/Theme-AI%20%C3%97%20Healthcare-crimson)](#)

---

## 💡 The Clinical Problem
Over **1.3 million emergency department visits** occur annually in the United States due to Adverse Drug Events (ADEs). In elderly patients managing multiple chronic conditions, **polypharmacy** (taking 5 or more daily medications) is standard. 

When patients see multiple specialists, lethal drug interactions and gut absorption conflicts (such as mineral chelation of antibiotics) frequently slip through fragmented electronic records. Most existing tools only emit generic, alarming warnings without providing a **temporal schedule resolution** or a **standardized clinician escalation bridge**.

---

## ⚡ What PharmaGuard AI Does
PharmaGuard AI closes this last-mile gap with an end-to-end clinical workflow:

1. **Deterministic Pharmacology Engine:** Cross-checks patient regimens against a structured interaction knowledge graph (derived from FDA FAERS, RxNorm, and CYP450 metabolism data).
2. **Multi-Tier Severity Categorization:** Distinguishes absolute contraindications (e.g. Warfarin + Ibuprofen &rarr; GI bleeding; Simvastatin + Clarithromycin &rarr; acute rhabdomyolysis) from temporal absorption conflicts.
3. **Autonomous 24-Hour Schedule De-confliction:** An algorithmic temporal solver spaces chelating agents (e.g. Calcium Carbonate, Iron) by 3–4 hours away from antibiotics (Ciprofloxacin) and thyroid hormones (Levothyroxine) to guarantee therapeutic drug absorption.
4. **1-Click Clinical SBAR Memo:** Auto-generates structured **Situation, Background, Assessment, Recommendation** documentation formatted for pharmacists and primary care physicians.
5. **Plain-Language Patient Safety Cards:** Translates complex pharmacology into 5th-grade reading level advice for patients and family caregivers.

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────┐
│              Patient / Caregiver Regimen               │
│   (Prescription Intake / Search / Polypharmacy Presets)│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│      PharmaGuard Clinical Decision Support Engine      │
│  - Normalized RxNorm & Brand-Name Resolution           │
│  - Pairwise Knowledge Graph Traversal                  │
│  - Cytochrome P450 & Absorption Kinetic Rules          │
└──────────────┬───────────────────────────┬─────────────┘
               │                           │
               ▼                           ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  Algorithmic Temporal Solver │  │  Clinical Escalation Bridge  │
│  - Chelation Window Spacing  │  │  - Standardized SBAR Memo    │
│  - 24-Hour Patient Timeline  │  │  - Grade 5 Plain-Text Advice │
└──────────────────────────────┘  └──────────────────────────────┘
```

---

## 🧪 Clinical Benchmarks & Test Suite

PharmaGuard includes an automated clinical test suite covering landmark pharmacological contraindications:

| Benchmark Case | Mechanism Tested | Expected Severity | PharmaGuard Action | Status |
|---|---|---|---|---|
| **Warfarin + Ibuprofen** | Synergistic GI mucosal bleeding & platelet inhibition | **CRITICAL** | Contraindication alert; drafts SBAR memo | ✅ PASS |
| **Simvastatin + Clarithromycin** | Potent CYP3A4 inhibition & acute rhabdomyolysis | **CRITICAL** | Statin holiday prompt; physician escalation | ✅ PASS |
| **Ciprofloxacin + Calcium** | Polyvalent cation chelation & 80% absorption loss | **MODERATE / TIMING** | Shifts calcium to lunch (3h spacing) | ✅ PASS |
| **Lisinopril + Spironolactone** | Additive potassium retention & hyperkalemia | **MODERATE / LAB** | Serum K+/Cr lab monitoring alert | ✅ PASS |
| **Methotrexate + Aspirin** | Impaired renal tubular clearance & bone marrow toxicity | **CRITICAL** | Immediate oncology consultation alert | ✅ PASS |
| **Sertraline + Tramadol** | Synergistic serotonergic agonism & Serotonin Syndrome | **CRITICAL** | Dual SSRI/opioid toxicity warning | ✅ PASS |
| **Levothyroxine + Iron** | Intestinal divalent iron chelation of exogenous T4 | **MODERATE / TIMING** | Spaces iron to midday (4h separation) | ✅ PASS |

Run the unit tests:
```bash
python3 -m unittest discover tests -v
```

---

## 🚀 Quick Start (Local Run)

PharmaGuard AI requires **Python 3.8+** with **zero external pip dependencies**:

```bash
# 1. Clone the repository
git clone https://github.com/<YOUR_USERNAME>/pharmaguard-ai.git
cd pharmaguard-ai

# 2. Run unit tests
python3 -m unittest discover tests

# 3. Start the application server
python3 server.py --port 8080

# 4. Open in your browser:
# http://localhost:8080
```

---

## 📁 Repository Structure

```
.
├── COMMAND-CENTRE.md          # Complete hackathon intelligence, strategy & rubric compliance
├── DEVPOST-COPY.md            # Paste-ready Devpost submission text & project description
├── DEVPOST-ANSWERS.md         # Field-by-field answers for the Devpost submission form
├── DEMO-SCRIPT.md             # Timed 2:30 video walkthrough script with visual cues
├── SUBMISSION-KIT.md          # Step-by-step submission checklist & QA audit protocol
├── ONE-PAGE-SUMMARY.html      # Printable One-Page Project PDF (DSH Hacks V2 deliverable)
├── ONE-PAGE-SUMMARY.md        # Markdown version of One-Page summary
├── BENCHMARK-REPORT.md        # Formal clinical validation & test verification report
├── check_video.py             # Standalone tool to verify demo video duration (2:00-3:00)
├── server.py                  # Zero-dependency HTTP REST API & web server
├── pharmaguard/               # Core pharmacology package
│   ├── engine.py              # Safety scoring & clinical reasoning
│   ├── interactions.py        # Pharmacological knowledge graph & rules
│   └── scheduler.py           # 24-hour temporal de-confliction algorithm
├── tests/
│   └── test_safety_engine.py  # 12 automated unit tests across clinical edge cases
└── static/                    # Responsive web dashboard
    ├── index.html             # Medical-grade single-page interface
    ├── style.css              # Custom styling & clinical color palette
    └── app.js                 # Reactive client controller & timeline renderer
```

---

## 📄 License
MIT License — free for educational and clinical community use.
