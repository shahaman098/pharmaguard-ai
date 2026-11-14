# 07 — Global Hackathon Winning Playbook

Synthesized from MLH, Devpost elite winners, Stanford Health++, and Hack Club judging panels.

---

## 1. Core Principles of Winning Judged Hackathons

1. **The 30-Second Hook:** Hackathon judges review 50–100 submissions in a few hours. If the core problem and working product aren't clear in the first 30 seconds of the video, the project gets lost in the middle pack.
2. **Workflow Collapse ("Before vs. After"):**
   - *Before:* Patient or caregiver juggles 6 pill bottles, Googles interactions across 10 forum tabs, misses calcium chelation, and ends up in the emergency department.
   - *After:* PharmaGuard ingests the regimen in 1 second, flags lethal bleeding and statin toxicity risks, reschedules doses to zero conflict, and produces a doctor-ready memo.
3. **Closing the Operational Loop:** Tools that only display an alert leave the user stranded. Tools that **resolve the conflict** (de-conflicted daily schedule) and **enable clinical action** (SBAR memo) win first place.
4. **The ChatGPT Test:** If a judge could get the exact same output by typing one sentence into ChatGPT, the project fails. PharmaGuard uses a deterministic graph traversal, temporal scheduling arithmetic, and an interactive UI that no single LLM prompt can reproduce.
5. **Deterministic Trust Layer:** In medicine, hallucination equals death. Combining an audited pharmacological rule matrix with an automated unit test suite (100% pass) gives judges complete confidence in the technology.
