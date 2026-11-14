# 13 — Demo Production & Submission Quality Assurance

---

## 1. Demo Video Blueprint (Target: 2:30)

| Timestamp | Visual Element | Spoken Key Message |
|---|---|---|
| **0:00 – 0:25** | Title Card & Problem Stat (1.3M emergency visits annually). | "Every year, over 1.3 million emergency visits occur from adverse drug interactions. For elderly patients taking 5+ prescriptions, the interactions can be fatal." |
| **0:25 – 0:50** | Live app at `localhost:8080`. Load Preset 1 (Cardiac Polypharmacy). | "We load a real-world case: an elderly cardiac patient on Warfarin and Simvastatin prescribed an antibiotic and an NSAID for joint pain." |
| **0:50 – 1:30** | Click "Run Safety Audit". Show crimson alerts (Warfarin+Ibuprofen bleeding, Simvastatin+Clarithromycin CYP3A4 toxicity, Cipro+Calcium chelation). | "PharmaGuard immediately flags lethal hemorrhage and acute rhabdomyolysis risks, plus an 80% antibiotic absorption loss from calcium chelation." |
| **1:30 – 1:55** | Click "24-Hour De-conflicted Schedule". Show calcium automatically spaced to lunch. | "PharmaGuard solves the timing conflict: our temporal algorithm spaces calcium 4 hours away from morning ciprofloxacin, preserving therapeutic efficacy." |
| **1:55 – 2:15** | Click "Export SBAR Memo". Show physician-ready clinical handoff note. | "For the critical contraindications requiring prescription changes, PharmaGuard generates a standardized SBAR memo ready to message to the doctor." |
| **2:15 – 2:30** | Terminal unit tests (12/12 passing in 0.001s) & clean GitHub repo. | "Backed by automated clinical verification tests, zero cloud bloat, and open-source for community health. Thank you." |

---

## 2. Final Submission Checklist
- [ ] Working prototype hosted locally / deployed.
- [ ] Demo video duration verified with `check_video.py` (2:00 – 3:00 band).
- [ ] YouTube video uploaded as **Unlisted** or **Public** with working audio.
- [ ] One-Page PDF generated from `ONE-PAGE-SUMMARY.html` and attached.
- [ ] Public GitHub repository pushed with updated README and passing tests.
- [ ] Project ZIP (`dsh-hacks-v2-submission.zip`) attached to Devpost form.
- [ ] Incognito browser check confirms public access without login.
