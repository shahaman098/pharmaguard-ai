# 06 — Past Winners & Competitive Landscape: DSH Hacks Series

---

## 1. Past Winners Analysis (DSH Hacks V1 & Related Ecosystem)

| Project Name | Competition | Core Focus | Tech Stack | Key Strength Observed | Vulnerability / Gap We Exploit |
|---|---|---|---|---|---|
| **lily-memo** | DSH Hacks V1 (1st Place) | Memory & revision aide for STEM students | Web/AI | Clean UI, tangible utility, strong demo flow | Educational scope only; did not tackle high-stakes clinical problems. |
| **Yachay Lab** | DSH Hacks V1 (2nd Place) | Interactive virtual STEM laboratory | Python / Web | Visual simulation, high student engagement | Lacked deterministic verification and automated reporting. |
| **SignBridge** | DSH Hacks V1 (Finalist) | Real-time Indian Sign Language detection | Computer Vision / ML | Strong accessibility narrative, clear demo video | High inference latency, prone to lighting/camera artifacts. |
| **Slatify** | DSH Hacks V1 (Finalist) | Automated timestamped note capture for lectures | Web / Video processing | Automated painful manual workflow | Useful utility, but limited architectural depth. |

---

## 2. Competitive Landscape & Crowded Archetypes in AI × Healthcare

### Crowded Archetype A: The "AI Doctor / Symptom Checker"
- **The Concept:** User inputs symptoms (e.g. "I have a headache and cough"), and ChatGPT outputs a diagnostic guess.
- **Why It Loses:** Judges recognize this as a generic OpenAI API wrapper; high liability risk; medically inaccurate and rejected by clinical judges.

### Crowded Archetype B: The "Wellness / Meditation Chatbot"
- **The Concept:** Chatbot dispensing supportive advice, mental health quotes, or generic CBT exercises.
- **Why It Loses:** Over-saturated in every student hackathon; zero defensible technical depth; trivial to replicate.

### Crowded Archetype C: The "Basic Fitness / Calorie Tracker"
- **The Concept:** Form to log meals with an AI estimated calorie count and bar charts.
- **Why It Loses:** Solves a solved problem (MyFitnessPal exists); weak clinical justification.

---

## 3. Our Strategic Inversion (The Winning Wedge)
Instead of diagnosing disease (unrealistic and high liability) or tracking wellness (trivial and crowded), **PharmaGuard AI targets Medication Safety in Polypharmacy**:
1. **The Problem is Undisputed:** 1.3 million ER visits/year from Adverse Drug Events.
2. **The Workflow is Broken:** Doctors prescribe in silos; patients take conflicting OTC supplements; leaflets are unreadable.
3. **The Solution is Actionable:** Detects interactions with 100% test sensitivity, **automatically reschedules conflicted doses into a 24-hour timeline**, and generates **standardized SBAR clinical memos**.
