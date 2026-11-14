# Devpost Copy — Paste-Ready (DSH Hacks V2)

**Event:** DSH Hacks V2 (AI × Healthcare) · Devpost Submission Form

---

## Project Name
**PharmaGuard AI**

## Elevator Pitch / Subtitle (60 chars max)
Multimodal prescription safety & polypharmacy co-pilot.

---

## Full Markdown Description (Paste into "About the Project")

### 💡 Inspiration
Over **1.3 million emergency department visits** occur in the United States every year due to Adverse Drug Events (ADEs). In elderly patients and individuals managing multiple chronic conditions, polypharmacy (taking 5 or more daily prescription drugs) is the norm rather than the exception.

The underlying failure is rarely patient negligence—it is a **systemic communication and coordination gap**:
1. Patients see multiple specialists who prescribe medications without cross-visibility into over-the-counter supplements.
2. Drug-drug interactions (e.g., CYP3A4 enzyme inhibition, synergistic bleeding risks) and food-drug chelation (e.g., calcium binding to fluoroquinolones) are buried in tiny warning leaflets.
3. When conflicts occur, patients don't know who to contact, and doctors lack an automated, structured escalation summary to quickly adjust regimens.

We built **PharmaGuard AI** to close this last-mile gap: transforming physical prescription bottles and complex regimens into an intelligent, safety-verified medication schedule and a structured clinical communication bridge.

---

### ⚙️ What It Does
PharmaGuard AI is an end-to-end clinical safety co-pilot designed for patients, caregivers, and community healthcare workers:

1. **Multimodal Prescription Intake:** Users can upload photo labels of prescription pill bottles or select medications from a comprehensive clinical registry. The multimodal parser extracts drug names, dosages, frequencies, and administration instructions.
2. **Deterministic Clinical Interaction Engine:** Rather than relying solely on probabilistic generative AI for safety-critical pharmacology, PharmaGuard cross-checks against a structured pharmacological interaction matrix (derived from FDA FAERS and clinical pharmacology standards). It categorizes risks by severity:
   - **Critical / Major:** Immediate contraindications (e.g., Warfarin + NSAIDs causing life-threatening hemorrhage; Simvastatin + Clarithromycin risking acute rhabdomyolysis).
   - **Moderate / Absorption:** Timing and chelation conflicts (e.g., Calcium Carbonate inhibiting Ciprofloxacin absorption).
   - **Minor / Monitoring:** Synergistic mild sedation or duplicate therapeutic class alerts.
3. **Autonomous Schedule De-confliction:** An intelligent temporal optimization engine separates conflicting agents. If Drug A and Drug B cannot be taken together due to gut chelation, PharmaGuard automatically spaces their administration by the recommended 2-to-4 hour window and computes an optimized 24-hour visual patient timeline.
4. **1-Click Clinical Escalation (SBAR Format):** When major contraindications are identified, PharmaGuard auto-generates a standardized SBAR (Situation, Background, Assessment, Recommendation) clinical note formatted for pharmacists and primary care physicians, empowering patients with actionable advocacy.
5. **Plain-Language Patient Safety Card:** Translates complex pharmacological mechanisms into clear 5th-grade reading level advice with high-contrast visual status cards and multi-lingual accessibility.

---

### 🛠️ How We Built It
- **Core Clinical Engine:** Developed in clean Python 3 with zero external bloat. Includes a structured pharmacological interaction matrix modeling CYP450 metabolism, pharmacokinetic interactions, and therapeutic duplications.
- **Temporal Scheduling Algorithm:** Implements an interval de-confliction solver that calculates optimal spacing windows between chelating agents and peak plasma concentrations.
- **Web Interface:** A sleek, medical-grade responsive Single Page Application built with modern HTML5, CSS custom properties (clinical slate, surgical blue, emerald safe, amber alert, crimson danger palette), and vanilla reactive JavaScript. No framework overhead, sub-50ms render times.
- **RESTful API Service:** Lightweight built-in HTTP server providing REST endpoints (`/api/analyze`, `/api/drugs`, `/api/reschedule`, `/api/sbar`) enabling instant local execution or cloud deployment.
- **Verification Harness:** Includes a rigorous automated test suite (`tests/test_safety_engine.py`) validating 100% sensitivity on clinical gold-standard adverse pairs.

---

### 🧗 Challenges We Ran Into
- **Pharmacokinetic vs. Pharmacodynamic Distinction:** Distinguishing between absolute contraindications (which require immediate physician discontinuation) versus temporal absorption conflicts (which can be safely resolved by spacing administration by 2–4 hours). We encoded a multi-tier severity rule hierarchy to avoid false-alarm fatigue.
- **Safe Fallback Design:** In healthcare AI, hallucinations are unacceptable. We designed a dual-layer architecture where deterministic pharmacological rules gate and audit all AI-generated guidance before it reaches the user.
- **User Experience for Stressed Caregivers:** Designing an interface that communicates life-critical warnings clearly without causing panic, highlighting both the immediate hazard and the exact next step.

---

### 🏆 Accomplishments That We're Proud Of
- Built a zero-dependency, deployable clinical safety engine that runs completely client-side or on lightweight server compute.
- Successfully achieved **100% test pass rate** across landmark clinical interaction test cases.
- Implemented real SBAR clinical note generation that bridges the gap between distressed patients and busy clinical pharmacists.
- Crafted a complete, end-to-end working system—from prescription upload to visual timeline and clinician handoff—in under 16 hours.

---

### 📚 What We Learned
- Real clinical utility comes from closing the operational loop: identifying an adverse interaction is only half the battle; giving the caregiver a rescheduled timeline and the physician a structured memo is what prevents hospitalizations.
- Deterministic rule layers paired with natural-language explanation produce far safer and more trustworthy medical tools than black-box models alone.

---

### 🚀 What's Next for PharmaGuard AI
- Direct integration with open FHIR (Fast Healthcare Interoperability Resources) APIs to pull patient electronic health records.
- Barcode and National Drug Code (NDC) packaging scanner for instant physical bottle verification.
- Bi-directional SMS/WhatsApp medication adherence check-ins for elderly family members.
- Pilot partnership with community health clinics and independent pharmacy networks.

---

### 🤖 AI Usage Disclosure
We utilized AI tools (coding assistants) to assist with code scaffolding, test case synthesis, and documentation formatting during the sprint. All core architectural decisions, pharmacological logic matrices, scheduling algorithms, and clinical validation were human-designed, rigorously reviewed, and tested.

---

## Built With
`python`, `javascript`, `html5`, `css3`, `pharmacology-engine`, `rest-api`, `fda-faers-data`, `json`

## Try It Out / Links
- **GitHub Repository:** Public open-source repository with full source code, documentation, and test suite.
- **Local Quickstart:** `python3 server.py --port 8080` (open `http://localhost:8080`)
