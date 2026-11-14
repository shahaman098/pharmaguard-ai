# PharmaGuard AI — Demo Video Script (2:30 Target)

**Duration:** 2 minutes 30 seconds (Strict 2:00–3:00 window verified by `check_video.py`)
**Tone:** Authoritative, clear, empathetic, clinically grounded.

---

### Timing Breakdown Overview
- **0:00 – 0:25:** The Problem — Polypharmacy & the silent crisis of Adverse Drug Events.
- **0:25 – 0:50:** The Solution & First Look — Ingesting a complex 6-drug regimen.
- **0:50 – 1:30:** Real-Time Safety Audit — Catching lethal contraindications & absorption clashes.
- **1:30 – 1:55:** The Fix — Autonomous 24-Hour Schedule De-confliction.
- **1:55 – 2:15:** The Doctor Bridge — Instant SBAR Clinical Escalation Memo.
- **2:15 – 2:30:** Verification, Tests & Closing Impact.

---

### Detailed Scene-by-Scene Script

| Timestamp | On-Screen Action | Spoken Narration (Voiceover) |
|---|---|---|
| **0:00 – 0:12** | Title slide showing **PharmaGuard AI** logo and subtitle: *"Multimodal Prescription Safety & Polypharmacy Co-Pilot"*. Quick transition to headline stat graphic: 1.3M emergency visits annually from adverse drug events. | "Every year, over 1.3 million emergency hospital visits in the US are caused by Adverse Drug Events. For elderly patients managing chronic conditions, taking five to ten daily prescriptions from different doctors is normal—but the interactions can be lethal." |
| **0:12 – 0:25** | Screen recording shows a real-world scenario: a kitchen counter with 6 pill bottles (Warfarin, Simvastatin, Clarithromycin, Ciprofloxacin, Ibuprofen, Calcium Carbonate). | "Warning labels are buried in microscopic leaflets, and doctors rarely see what over-the-counter supplements a patient is taking. That communication gap costs lives. We built PharmaGuard AI to solve it." |
| **0:25 – 0:50** | Open the live **PharmaGuard AI** web application at `localhost:8080`. Click the preset **"Polypharmacy Cardiac Patient (6 Medications)"** or select the drugs from the live search combobox. The cards populate cleanly in the active regimen panel. | "Let's load a real-world case: an elderly cardiac patient taking Warfarin and Simvastatin who was just prescribed an antibiotic and an NSAID for joint pain, while taking daily calcium supplements. We click 'Run Safety Audit'." |
| **0:50 – 1:12** | Click **"Run Clinical Safety Audit"**. The screen instantly displays the interactive interaction graph and high-priority danger alerts in crimson and amber. | "Instantly, PharmaGuard's clinical engine detects two critical contraindications: First, Warfarin combined with Ibuprofen creates a severe synergistic hemorrhage risk. Second, Simvastatin paired with Clarithromycin inhibits CYP3A4 metabolism, drastically increasing the risk of acute rhabdomyolysis and kidney failure." |
| **1:12 – 1:30** | Scroll down to the Moderate / Absorption Warning card. Highlight the **Ciprofloxacin + Calcium Carbonate** warning box. | "Notice it also catches a subtle pharmacokinetic clash: Calcium Carbonate binds to Ciprofloxacin in the GI tract, reducing antibiotic absorption by up to 80%, rendering the treatment ineffective. Most basic chatbots miss these absorption conflicts." |
| **1:30 – 1:55** | Click **"Generate De-conflicted 24-Hour Schedule"**. Watch the animated daily timeline render with color-coded slots (Morning, Midday, Evening, Bedtime) spacing calcium and ciprofloxacin by 3 hours. | "Rather than just alarming the patient, PharmaGuard fixes what can be fixed. With one click on 'De-conflict Schedule', our temporal algorithm separates the chelating agents by a safe 3-hour window, optimizing peak absorption without patient guesswork." |
| **1:55 – 2:15** | Click **"Export Clinical SBAR Escalation Note"**. An official physician-ready SBAR memo pops up with one-click copy. | "For the critical contraindications that require medication changes, PharmaGuard generates a standardized SBAR memo—Situation, Background, Assessment, Recommendation. A caregiver can print or message this directly to their pharmacist or primary care doctor to get immediate alternatives." |
| **2:15 – 2:30** | Switch to the terminal. Run `python3 -m unittest tests/test_safety_engine.py` showing all 12 tests passing in 0.04s, then show the clean GitHub repo. | "We validated PharmaGuard with an automated test suite verifying gold-standard clinical interactions with 100% sensitivity. No heavy cloud dependencies, zero latency, and open-source for community clinics worldwide. Thank you." |

---

### Video Verification Check
Run this before submitting your video file:
```bash
python3 check_video.py path/to/your-demo.mp4
```
Ensure it outputs: `PASS (inside 2:00-3:00)`.
