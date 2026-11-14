# 10 — Project Architecture & Technical Specification: PharmaGuard AI

---

## 1. Technical Architecture Overview

PharmaGuard AI is designed with an air-gapped, zero-dependency philosophy: high performance, zero cloud latency, and 100% deterministic safety verification.

```
+-------------------------------------------------------------------------------+
|                               Browser Client (SPA)                            |
|  - Reactive Vanilla JS (app.js) with 1-click clinical presets                 |
|  - Medical UI Design System (style.css) with high-contrast clinical palettes  |
|  - Interactive 24-Hour Timeline & Modal SBAR Clinical Memo Exporter           |
+---------------------------------------+---------------------------------------+
                                        |  REST over HTTP (JSON)
                                        v
+-------------------------------------------------------------------------------+
|                       Local Web & API Server (server.py)                      |
|  - Built-in Python 3 HTTPServer (Zero external pip dependencies)              |
|  - Endpoints: /api/drugs, /api/audit, /api/reschedule, /api/sbar              |
+---------------------------------------+---------------------------------------+
                                        |
       +--------------------------------+--------------------------------+
       |                                                                 |
       v                                                                 v
+----------------------------------+            +----------------------------------+
|   Clinical Safety Engine         |            |   Temporal Schedule Solver       |
|   (pharmaguard/engine.py)        |            |   (pharmaguard/scheduler.py)     |
|   - RxNorm Key Normalization     |            |   - Canonical Daily Slots        |
|   - Pairwise Rule Graph Traversal|            |   - Kinetic Chelation Spacing    |
|   - SBAR Clinical Synthesis      |            |   - 24-Hour Timeline Optimizer   |
+-----------------+----------------+            +----------------------------------+
                  |
                  v
+-------------------------------------------------------------------------------+
|                  Pharmacological Knowledge Graph (interactions.py)            |
|  - RxNorm & Brand-Name Registry (Coumadin, Cipro, Zocor, Tums, Advil, etc.)   |
|  - Curated FDA FAERS Interaction Matrix (CYP450, Chelation, Pharmacodynamics) |
+-------------------------------------------------------------------------------+
```

---

## 2. API Contract Specification

### `GET /api/drugs`
Returns the active clinical registry of medications with indications, classes, and food warnings.

### `POST /api/audit`
**Request:**
```json
{
  "medications": ["Warfarin", "Ibuprofen", "Simvastatin", "Clarithromycin"]
}
```
**Response:**
```json
{
  "total_medications": 4,
  "safety_score": 30,
  "overall_status": "CRITICAL RISK — PHYSICIAN CONSULTATION REQUIRED",
  "critical_count": 2,
  "moderate_count": 0,
  "interactions": [...],
  "patient_summary": [...]
}
```

### `POST /api/reschedule`
Calculates optimal 24-hour spacing allocations separating chelating minerals by $\ge 3$ hours.

### `POST /api/sbar`
Formats a clinical Situation, Background, Assessment, Recommendation document for clinician handoff.
