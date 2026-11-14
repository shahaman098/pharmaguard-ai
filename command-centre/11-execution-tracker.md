# 11 — Execution Tracker & Risk Register: DSH Hacks V2

**Submission Deadline:** Sunday 15 Nov 2026, 07:45 UTC (11:45 PM PST) · **Status:** ON SCHEDULE

---

## 1. Milestone Execution Schedule

| Milestone / Task | Target Window | Deliverable Asset | Status |
|---|---|---|---|
| **Phase 1–8: Recon & Architecture** | T-16h | `COMMAND-CENTRE.md`, `briefs/dsh-hacks-v2.md` | ✅ **DONE** |
| **Phase 9–10: Core Build & Engine** | T-15h | `pharmaguard/`, `server.py`, `static/` | ✅ **DONE** |
| **Phase 11: Unit Verification** | T-14h | `tests/test_safety_engine.py` (12/12 passing) | ✅ **DONE** |
| **Phase 12: Submission Kit Prep** | T-13h | `DEVPOST-COPY.md`, `DEVPOST-ANSWERS.md`, `DEMO-SCRIPT.md` | ✅ **DONE** |
| **Phase 13: One-Page PDF Ready** | T-12h | `ONE-PAGE-SUMMARY.html` (print-ready) | ✅ **DONE** |
| **Phase 14: Submission Archive** | T-11h | `dsh-hacks-v2-submission.zip` | ✅ **DONE** |
| **Phase 15: Demo Video Recording** | T-6h | 2:30 screen recording + voiceover | 🟡 Pending User Recording |
| **Phase 16: Devpost Entry & QA** | T-3h | Public Devpost URL & logged-out QA check | 🟡 Pending User Upload |

---

## 2. Risk Management Register

| Risk | Likelihood | Impact | Trigger | Mitigation & Fallback | Owner | Status |
|---|---|---|---|---|---|---|
| **Video over/under time** | Medium | High | Video length outside 2:00–3:00 | Standalone `check_video.py` tool confirms duration before upload | Team | **Mitigated** |
| **Missing One-Page PDF** | Low | Critical | Devpost requires PDF file | `ONE-PAGE-SUMMARY.html` calibrated for 1-click print to PDF | Team | **Mitigated** |
| **Server installation error** | Low | High | Python dependencies missing | Pure standard library implementation; zero pip packages required | Team | **Mitigated** |
| **Devpost traffic slowdown** | High | High | Server latency in final 30 minutes | Target initial submission 2 hours before deadline | Team | **Active** |
| **Broken video audio/link** | Low | High | YouTube permissions set to private | Incognito browser audit checklist in `SUBMISSION-KIT.md` | Team | **Active** |
