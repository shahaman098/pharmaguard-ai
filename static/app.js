/**
 * PharmaGuard AI — client controller
 *
 * The browser handles perception (label OCR) and presentation. All clinical
 * decisions stay in the deterministic Python engine.
 */

const PRESETS = {
  cardiac: [
    "Warfarin",
    "Simvastatin",
    "Clarithromycin",
    "Ciprofloxacin",
    "Ibuprofen",
    "Calcium Carbonate"
  ],
  psych: ["Sertraline", "Tramadol", "Aspirin"],
  endocrine: ["Levothyroxine", "Ferrous Sulfate (Iron)", "Metformin"],
  unknown: ["Metformin", "Lisinopril", "Mystery Supplement"],
  safe: ["Metformin", "Simvastatin", "Lisinopril"]
};

let currentRegimen = [...PRESETS.cardiac];
let doseOverrides = new Map();
let allAvailableDrugs = [];
let latestAuditResult = null;
let latestSchedule = null;
let auditRequestId = 0;
let scheduleRequestId = 0;
let scanDetected = [];
let scanBusy = false;
let tesseractWorker = null;
let tesseractLoading = null;
let tesseractScriptPromise = null;

// DOM shortcuts
const $ = (id) => document.getElementById(id);

const drugDropdown = $("drug-dropdown");
const regimenListEl = $("regimen-list");
const medCountBadge = $("med-count-badge");
const scoreCard = $("safety-score-card");
const scoreValueEl = $("score-value");
const scoreStatusText = $("score-status-text");
const scoreSummaryMetrics = $("score-summary-metrics");
const scoreRecommendationSub = $("score-recommendation-sub");
const violationsContainer = $("violations-container");
const violationsCountEl = $("violations-count");
const graphContainer = $("graph-container");
const interactionGraph = $("interaction-graph");
const timelineContainer = $("timeline-container");
const weeklyPrnContainer = $("weekly-prn-container");
const scheduleNotes = $("schedule-notes");
const patientAdviceList = $("patient-advice-list");
const patientDisclaimer = $("patient-disclaimer");
const unverifiedPanel = $("unverified-panel");
const unverifiedList = $("unverified-list");
const scanModal = $("scan-modal");
const sbarModal = $("sbar-modal");

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await Promise.all([fetchDrugs(), fetchMeta()]);
  renderRegimenCards();
  await runSafetyAudit();
});

async function fetchMeta() {
  try {
    const res = await fetch("/api/meta");
    const meta = await res.json();
    const kb = meta.knowledge_base || {};
    $("kb-status-text").textContent = `Local engine · ${kb.drug_count || 0} drugs · ${kb.rule_count || 0} rules`;
    $("footer-kb").textContent = `Knowledge base v${kb.version || "2.0"} · ${kb.drug_count || 0} drugs · ${kb.rule_count || 0} rules · not for clinical use`;
    if (meta.disclaimer) {
      $("global-disclaimer").textContent = `PharmaGuard AI is an educational prototype. ${meta.disclaimer}`;
      patientDisclaimer.textContent = `Demo only. ${meta.disclaimer}`;
    }
  } catch (error) {
    console.warn("Metadata unavailable:", error);
  }
}

async function fetchDrugs() {
  try {
    const res = await fetch("/api/drugs");
    const data = await res.json();
    allAvailableDrugs = data.drugs || [];

    drugDropdown.innerHTML = '<option value="" disabled selected>-- Select a medication to add --</option>';
    allAvailableDrugs.forEach((drug) => {
      const option = document.createElement("option");
      option.value = drug.name;
      option.textContent = `${drug.name} (${drug.brand}) — ${drug.class}`;
      drugDropdown.appendChild(option);
    });
  } catch (error) {
    console.error("Error fetching drug registry:", error);
    toast("Could not load the drug registry. Is the server running?", "error");
  }
}

// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------
function setupEventListeners() {
  document.querySelectorAll(".btn-preset").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".btn-preset").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      currentRegimen = [...(PRESETS[button.dataset.preset] || [])];
      doseOverrides.clear();
      renderRegimenCards();
      runSafetyAudit();
    });
  });

  $("btn-add-drug").addEventListener("click", () => {
    const selected = drugDropdown.value;
    if (!selected) {
      toast("Choose a medication first.", "error");
      return;
    }
    if (!currentRegimen.includes(selected)) {
      currentRegimen.push(selected);
      clearPresetSelection();
      renderRegimenCards();
      runSafetyAudit();
    }
    drugDropdown.value = "";
  });

  $("btn-clear-all").addEventListener("click", () => {
    currentRegimen = [];
    doseOverrides.clear();
    clearPresetSelection();
    renderRegimenCards();
    runSafetyAudit();
  });

  $("btn-run-audit").addEventListener("click", () => runSafetyAudit());

  document.querySelectorAll(".tab-btn").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((item) => {
        item.classList.remove("active");
        item.setAttribute("aria-selected", "false");
      });
      document.querySelectorAll(".tab-pane").forEach((pane) => pane.classList.remove("active"));
      button.classList.add("active");
      button.setAttribute("aria-selected", "true");
      const pane = document.getElementById(`tab-${button.dataset.tab}`);
      if (pane) pane.classList.add("active");
    });
  });

  $("btn-export-sbar").addEventListener("click", openSbarModal);
  $("btn-close-modal").addEventListener("click", () => sbarModal.classList.remove("open"));
  $("btn-modal-done").addEventListener("click", () => sbarModal.classList.remove("open"));

  $("btn-copy-sbar").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText($("sbar-textarea").value);
      $("copy-btn-text").textContent = "Copied!";
      setTimeout(() => { $("copy-btn-text").textContent = "Copy to clipboard"; }, 1800);
    } catch (error) {
      toast("Clipboard permission denied. Select the text and copy manually.", "error");
    }
  });

  $("btn-re-optimize").addEventListener("click", async () => {
    if (!latestAuditResult) return;
    await fetchAndRenderSchedule(latestAuditResult);
    toast("Schedule re-optimized.", "success");
  });

  $("btn-calendar").addEventListener("click", downloadCalendar);

  // Label scan
  $("btn-scan-label").addEventListener("click", openScanModal);
  $("btn-close-scan").addEventListener("click", () => scanModal.classList.remove("open"));
  $("btn-done-scan").addEventListener("click", () => scanModal.classList.remove("open"));
  $("btn-sample-label").addEventListener("click", loadSampleLabel);
  $("btn-clear-scan").addEventListener("click", resetScanResults);
  $("btn-parse-paste").addEventListener("click", () => {
    const text = $("scan-paste-text").value || "";
    if (!text.trim()) {
      toast("Paste some label text first.", "error");
      return;
    }
    handleRecognizedText(text, null);
  });
  $("btn-add-scanned").addEventListener("click", addScannedMedications);

  const fileInput = $("scan-file");
  fileInput.addEventListener("change", () => {
    const file = fileInput.files && fileInput.files[0];
    if (file) handleScanFile(file);
    // Allow selecting the same file again for a re-scan.
    fileInput.value = "";
  });

  const dropzone = $("scan-dropzone");
  ["dragenter", "dragover"].forEach((name) => {
    dropzone.addEventListener(name, (event) => {
      event.preventDefault();
      dropzone.classList.add("dragover");
    });
  });
  ["dragleave", "drop"].forEach((name) => {
    dropzone.addEventListener(name, (event) => {
      event.preventDefault();
      dropzone.classList.remove("dragover");
    });
  });
  dropzone.addEventListener("drop", (event) => {
    const file = event.dataTransfer?.files?.[0];
    if (file) handleScanFile(file);
  });
  dropzone.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      $("scan-file").click();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      scanModal.classList.remove("open");
      sbarModal.classList.remove("open");
    }
  });
}

// ---------------------------------------------------------------------------
// Regimen rendering
// ---------------------------------------------------------------------------
function findDrug(name) {
  return allAvailableDrugs.find(
    (drug) => drug.name.toLowerCase() === name.toLowerCase()
  );
}

function clearPresetSelection() {
  document.querySelectorAll(".btn-preset").forEach((button) => {
    button.classList.remove("active");
  });
}

function renderRegimenCards() {
  regimenListEl.innerHTML = "";
  medCountBadge.textContent = `${currentRegimen.length} Medication${currentRegimen.length === 1 ? "" : "s"}`;

  if (currentRegimen.length === 0) {
    regimenListEl.innerHTML = '<div class="empty-state">No medications selected. Choose a demo case, scan a label, or add a drug above.</div>';
    return;
  }

  currentRegimen.forEach((medName, index) => {
    const drug = findDrug(medName);
    const card = document.createElement("div");
    card.className = `med-card${drug ? "" : " med-card-unknown"}`;

    if (drug) {
      const override = doseOverrides.get(drug.key);
      const displayDose = override || drug.default_dose;
      card.innerHTML = `
        <div class="med-info">
          <h3>${escapeHtml(drug.name)} <span class="med-brand">(${escapeHtml(drug.brand)})</span></h3>
          <div class="med-class">${escapeHtml(drug.class)}</div>
          <div class="med-details-row">
            <span>Dose: ${escapeHtml(displayDose)}${override ? ' <span class="dose-source">from label</span>' : ""}</span>
            <span>•</span>
            <span>${escapeHtml(drug.food_warnings)}</span>
          </div>
        </div>
        <button class="med-remove-btn" title="Remove medication" data-idx="${index}" type="button" aria-label="Remove ${escapeHtml(drug.name)}">&times;</button>
      `;
    } else {
      card.innerHTML = `
        <div class="med-info">
          <h3>${escapeHtml(medName)} <span class="unverified-pill">UNVERIFIED</span></h3>
          <div class="med-class">Not in the demo knowledge base</div>
          <div class="med-details-row">
            <span>This medicine will not be treated as safe. Confirm it with a pharmacist.</span>
          </div>
        </div>
        <button class="med-remove-btn" title="Remove medication" data-idx="${index}" type="button" aria-label="Remove ${escapeHtml(medName)}">&times;</button>
      `;
    }

    card.querySelector(".med-remove-btn").addEventListener("click", () => {
      const removed = currentRegimen[index];
      const removedDrug = findDrug(removed);
      currentRegimen.splice(index, 1);
      if (removedDrug) doseOverrides.delete(removedDrug.key);
      clearPresetSelection();
      renderRegimenCards();
      runSafetyAudit();
    });

    regimenListEl.appendChild(card);
  });
}

function renderUnverifiedPanel(result) {
  const unknown = result?.unknown_drugs || [];
  if (!unknown.length) {
    unverifiedPanel.classList.add("hidden");
    unverifiedList.innerHTML = "";
    return;
  }

  unverifiedPanel.classList.remove("hidden");
  unverifiedList.innerHTML = unknown
    .map((name) => `<span class="unverified-chip">❓ ${escapeHtml(name)}</span>`)
    .join("");
}

// ---------------------------------------------------------------------------
// Audit
// ---------------------------------------------------------------------------
async function runSafetyAudit() {
  const requestId = ++auditRequestId;
  latestSchedule = null;

  if (currentRegimen.length === 0) {
    latestAuditResult = null;
    resetAuditView();
    return;
  }

  try {
    const res = await fetch("/api/audit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        medications: currentRegimen,
        dose_overrides: Object.fromEntries(doseOverrides)
      })
    });
    if (!res.ok) throw new Error(`Audit failed (${res.status})`);
    const result = await res.json();
    if (requestId !== auditRequestId) return;
    latestAuditResult = result;

    updateScoreCard(result);
    renderViolations(result);
    renderInteractionGraph(result);
    renderPatientAdvice(result);
    renderUnverifiedPanel(result);
    await fetchAndRenderSchedule(result, requestId);
  } catch (error) {
    if (requestId !== auditRequestId) return;
    console.error("Audit error:", error);
    toast("The audit could not run. Check that the local server is running.", "error");
  }
}

function resetAuditView() {
  scoreValueEl.textContent = "100";
  scoreStatusText.textContent = "NO MEDICATIONS TO REVIEW";
  scoreCard.className = "score-card score-safe";
  scoreSummaryMetrics.innerHTML = '<span class="metric-tag green">0 Conflicts</span>';
  scoreRecommendationSub.textContent = "Add medications to run a safety audit.";
  violationsContainer.innerHTML = '<div class="empty-state">Add medications to run the safety audit.</div>';
  violationsCountEl.textContent = "0";
  graphContainer.classList.add("hidden");
  timelineContainer.innerHTML = "";
  weeklyPrnContainer.innerHTML = "";
  scheduleNotes.innerHTML = "";
  patientAdviceList.innerHTML = "";
  unverifiedPanel.classList.add("hidden");
}

function updateScoreCard(result) {
  scoreValueEl.textContent = result.safety_score;
  scoreStatusText.textContent = result.overall_status;

  scoreCard.className = "score-card";
  if (result.critical_count > 0) {
    scoreCard.classList.add("score-danger");
  } else if (result.moderate_count > 0) {
    scoreCard.classList.add("score-warning");
  } else if ((result.unverified_count || 0) > 0) {
    scoreCard.classList.add("score-incomplete");
  } else {
    scoreCard.classList.add("score-safe");
  }

  const tags = [];
  if (result.critical_count > 0) {
    tags.push(`<span class="metric-tag red">${result.critical_count} Critical</span>`);
  }
  if (result.moderate_count > 0) {
    tags.push(`<span class="metric-tag amber">${result.moderate_count} Timing / monitoring</span>`);
  }
  if ((result.unverified_count || 0) > 0) {
    tags.push(`<span class="metric-tag slate">${result.unverified_count} Unverified</span>`);
  }
  if (result.verified_count > 0) {
    tags.push(`<span class="metric-tag ${result.coverage_pct === 100 ? "green" : "slate"}">${result.coverage_pct}% verified</span>`);
  }
  scoreSummaryMetrics.innerHTML = tags.join("");

  if (result.critical_count > 0) {
    scoreRecommendationSub.textContent = "Critical interaction detected. Do not start or change these medicines without pharmacist or prescriber review.";
  } else if (result.moderate_count > 0) {
    scoreRecommendationSub.textContent = "Timing or monitoring issue detected. Review the schedule and the pharmacist questions below.";
  } else if ((result.unverified_count || 0) > 0) {
    scoreRecommendationSub.textContent = "Some medicines could not be checked. This regimen is not certified safe until they are verified.";
  } else if (result.verified_count > 0) {
    scoreRecommendationSub.textContent = "No known interactions in the demo knowledge base. Continue standard monitoring and pharmacist review.";
  } else {
    scoreRecommendationSub.textContent = "Add medications to run a safety audit.";
  }
}

function renderViolations(result) {
  violationsContainer.innerHTML = "";
  const list = result.interactions || [];
  violationsCountEl.textContent = list.length;

  if (list.length === 0) {
    violationsContainer.innerHTML = `
      <div class="safe-banner">
        <h4>✅ No known interactions in the demo knowledge base</h4>
        <p>${(result.unverified_count || 0) > 0
          ? "However, some medicines are unverified, so this regimen is not certified safe."
          : "This is not a clinical validation. Keep the pharmacist review."}</p>
      </div>
    `;
    return;
  }

  list.forEach((item) => {
    const card = document.createElement("div");
    card.className = `violation-card ${item.severity.toLowerCase()}`;
    const spacingBadge = item.spacing_resolvable
      ? `<span class="spacing-badge">Timing-fixable · ${item.recommended_spacing_hours}h</span>`
      : "";
    card.innerHTML = `
      <div class="violation-header">
        <div class="violation-title-group">
          <h4>${escapeHtml(item.title)}</h4>
          <div class="violation-drugs"><strong>Interacting pair:</strong> ${escapeHtml(item.drug_a)} + ${escapeHtml(item.drug_b)} ${spacingBadge}</div>
        </div>
        <span class="severity-pill ${item.severity.toLowerCase()}">${item.severity}</span>
      </div>
      <div class="violation-body">
        <p><strong>Mechanism:</strong> ${escapeHtml(item.mechanism)}</p>
      </div>
      <div class="violation-action">
        <span class="action-label">Clinical action:</span>
        <span>${escapeHtml(item.clinical_action)}</span>
      </div>
      <div class="violation-source">Source: ${escapeHtml(item.source || "FDA-approved labeling")}</div>
    `;
    violationsContainer.appendChild(card);
  });
}

// ---------------------------------------------------------------------------
// Interaction map (SVG, no dependency)
// ---------------------------------------------------------------------------
function renderInteractionGraph(result) {
  const interactions = result.interactions || [];
  const drugs = result.regimen || [];

  if (interactions.length === 0 || drugs.length < 2) {
    graphContainer.classList.add("hidden");
    interactionGraph.innerHTML = "";
    return;
  }

  graphContainer.classList.remove("hidden");
  const width = 820;
  const height = 330;
  const centerX = width / 2;
  const centerY = height / 2 - 4;
  const radiusX = Math.min(320, 130 + drugs.length * 18);
  const radiusY = Math.min(125, 70 + drugs.length * 8);
  const positions = {};

  drugs.forEach((drug, index) => {
    const angle = (Math.PI * 2 * index) / drugs.length - Math.PI / 2;
    positions[drug.key] = {
      x: centerX + radiusX * Math.cos(angle),
      y: centerY + radiusY * Math.sin(angle)
    };
  });

  const worst = {};
  interactions.forEach((item) => {
    const [a, b] = item.pair_keys;
    [a, b].forEach((key) => {
      if (!worst[key] || item.severity === "CRITICAL") worst[key] = item.severity;
    });
  });

  const edges = interactions.map((item) => {
    const [a, b] = item.pair_keys;
    const start = positions[a];
    const end = positions[b];
    if (!start || !end) return "";
    const critical = item.severity === "CRITICAL";
    const color = critical ? "#dc2626" : "#d97706";
    const dash = item.spacing_resolvable ? 'stroke-dasharray="7 5"' : "";
    return `<line x1="${start.x}" y1="${start.y}" x2="${end.x}" y2="${end.y}" stroke="${color}" stroke-width="${critical ? 3 : 2}" ${dash} opacity="0.75"><title>${escapeHtml(item.drug_a)} + ${escapeHtml(item.drug_b)}: ${escapeHtml(item.title)}</title></line>`;
  }).join("");

  const nodes = drugs.map((drug) => {
    const pos = positions[drug.key];
    const severity = worst[drug.key];
    const stroke = severity === "CRITICAL" ? "#dc2626" : severity === "MODERATE" ? "#d97706" : "#94a3b8";
    const initials = drug.name.replace(/[^A-Za-z ]/g, "").split(/\s+/).filter(Boolean).slice(0, 2).map((word) => word[0]).join("").toUpperCase();
    const label = drug.name.length > 20 ? `${drug.name.slice(0, 18)}…` : drug.name;
    return `
      <g>
        <circle cx="${pos.x}" cy="${pos.y}" r="25" fill="#ffffff" stroke="${stroke}" stroke-width="2.5"></circle>
        <text x="${pos.x}" y="${pos.y + 4}" text-anchor="middle" font-size="12" font-weight="700" fill="#0f172a">${escapeHtml(initials)}</text>
        <text x="${pos.x}" y="${pos.y + 42}" text-anchor="middle" font-size="11" fill="#475569">${escapeHtml(label)}</text>
        <title>${escapeHtml(drug.name)}</title>
      </g>
    `;
  }).join("");

  interactionGraph.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Interaction map of the current regimen">
      ${edges}
      ${nodes}
    </svg>
  `;
}

// ---------------------------------------------------------------------------
// Schedule
// ---------------------------------------------------------------------------
async function fetchAndRenderSchedule(auditResult, parentRequestId = auditRequestId) {
  const requestId = ++scheduleRequestId;
  try {
    const res = await fetch("/api/reschedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        regimen: auditResult.regimen,
        interactions: auditResult.interactions
      })
    });
    if (!res.ok) throw new Error(`Schedule failed (${res.status})`);
    const schedule = await res.json();
    if (parentRequestId !== auditRequestId || requestId !== scheduleRequestId) return;
    latestSchedule = schedule;
    renderTimeline(schedule);
    renderWeeklyAndPrn(schedule);
    renderScheduleNotes(schedule);
  } catch (error) {
    if (parentRequestId !== auditRequestId || requestId !== scheduleRequestId) return;
    console.error("Schedule error:", error);
    timelineContainer.innerHTML = '<div class="empty-state">Could not build a schedule.</div>';
  }
}

function renderTimeline(schedule) {
  timelineContainer.innerHTML = "";
  const groups = schedule.groups || [];

  if (groups.length === 0) {
    timelineContainer.innerHTML = '<div class="empty-state">No daily doses to schedule. Check the weekly and as-needed sections below.</div>';
    return;
  }

  groups.forEach((group) => {
    const groupEl = document.createElement("div");
    groupEl.className = "timeline-slot";
    const doses = (group.doses || []).map((dose) => `
      <div class="dose-row">
        <div class="dose-line">
          <span class="slot-med-tag ${dose.status === "rescheduled" ? "rescheduled" : ""}">
            <strong>${escapeHtml(dose.drug)}</strong> (${escapeHtml(dose.dose)})
          </span>
          <span class="dose-status ${dose.status}">${statusLabel(dose.status)}</span>
          ${dose.critical_conflict ? '<span class="dose-critical">Critical conflict</span>' : ""}
        </div>
        <div class="slot-instruction">${escapeHtml(dose.instruction)}</div>
      </div>
    `).join("");

    groupEl.innerHTML = `
      <div class="slot-time-col">
        <div class="slot-time">${escapeHtml(group.time)}</div>
        <div class="slot-label">${escapeHtml(group.label)}</div>
      </div>
      <div class="slot-content-col">${doses}</div>
    `;
    timelineContainer.appendChild(groupEl);
  });
}

function renderWeeklyAndPrn(schedule) {
  weeklyPrnContainer.innerHTML = "";
  const weekly = schedule.weekly || [];
  const prn = schedule.prn || [];

  if (weekly.length) {
    const section = document.createElement("div");
    section.className = "weekly-card";
    section.innerHTML = `
      <h4>Weekly medicines</h4>
      ${weekly.map((item) => `
        <div class="weekly-item">
          <strong>${escapeHtml(item.drug)}</strong> (${escapeHtml(item.dose)}) — ${escapeHtml(item.time)}
          <div class="slot-instruction">${escapeHtml(item.instruction)}</div>
          <div class="weekly-warning">${escapeHtml(item.warning)}</div>
        </div>
      `).join("")}
    `;
    weeklyPrnContainer.appendChild(section);
  }

  if (prn.length) {
    const section = document.createElement("div");
    section.className = "prn-card";
    section.innerHTML = `
      <h4>As-needed medicines (not auto-scheduled)</h4>
      ${prn.map((item) => `
        <div class="prn-item">
          <strong>${escapeHtml(item.drug)}</strong> (${escapeHtml(item.dose)})
          <div class="slot-instruction">${escapeHtml(item.instruction)}</div>
        </div>
      `).join("")}
    `;
    weeklyPrnContainer.appendChild(section);
  }
}

function renderScheduleNotes(schedule) {
  const adjustments = schedule.adjustments_made || [];
  const unresolved = schedule.unresolved || [];
  const criticalConflicts = schedule.critical_conflicts || [];
  const solver = schedule.solver || {};

  const adjustmentHtml = adjustments.length
    ? `<div class="note-card"><h4>Why this schedule</h4><ul>${adjustments.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>`
    : "";

  const unresolvedHtml = unresolved.length
    ? `<div class="note-card unresolved"><h4>Unresolved timing conflicts</h4><ul>${unresolved.map((item) => `<li>${escapeHtml(item.drug_a)} + ${escapeHtml(item.drug_b)}: ${item.actual_hours}h apart, ${item.required_hours}h recommended.</li>`).join("")}</ul></div>`
    : "";

  const criticalHtml = criticalConflicts.length
    ? `<div class="note-card critical-conflicts"><h4>Critical pairs could not be fully separated</h4><p>Do not use this timeline as a medication order. Review the contraindications above.</p><ul>${criticalConflicts.map((item) => `<li>${escapeHtml(item.drug_a)} + ${escapeHtml(item.drug_b)}: ${item.actual_hours}h apart, ${item.required_hours}h minimum for administration.</li>`).join("")}</ul></div>`
    : "";

  const constraintStatus = solver.fully_constrained
    ? "all spacing constraints satisfied"
    : solver.critical_relaxed
      ? "constraints relaxed — review critical conflicts"
      : "spacing relaxed";

  const solverHtml = `
    <div class="solver-meta">
      ${escapeHtml(solver.algorithm || "constraint solver")} ·
      ${solver.nodes_explored || 0} search nodes ·
      ${constraintStatus}
    </div>
  `;

  scheduleNotes.innerHTML = adjustmentHtml + unresolvedHtml + criticalHtml + solverHtml;
}

function statusLabel(status) {
  const labels = {
    fasting: "Fasting",
    with_meal: "With meal",
    rescheduled: "Moved for safety",
    standard: "Standard"
  };
  return labels[status] || "Standard";
}

// ---------------------------------------------------------------------------
// Patient advice
// ---------------------------------------------------------------------------
function renderPatientAdvice(result) {
  patientAdviceList.innerHTML = "";
  (result.patient_summary || []).forEach((text) => {
    const item = document.createElement("div");
    item.className = "advice-card";
    item.textContent = text;
    patientAdviceList.appendChild(item);
  });
}

// ---------------------------------------------------------------------------
// Calendar export (.ics)
// ---------------------------------------------------------------------------
function downloadCalendar() {
  const hasDaily = !!(latestSchedule && (latestSchedule.doses || []).length);
  const hasWeekly = !!(latestSchedule && (latestSchedule.weekly || []).length);
  if (!hasDaily && !hasWeekly) {
    toast("Run an audit with at least one scheduled medicine first.", "error");
    return;
  }

  const now = new Date();
  const stamp = icsStamp(now);
  const patient = ($("patient-name").value || "Patient").trim();
  const lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//PharmaGuard AI//Medication Schedule//EN",
    "CALSCALE:GREGORIAN",
    `X-WR-CALNAME:${icsEscape(`PharmaGuard — ${patient}`)}`,
    "METHOD:PUBLISH"
  ];

  latestSchedule.doses.forEach((dose, index) => {
    const [hour, minute] = dose.time.split(":").map(Number);
    const start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hour, minute, 0, 0);
    if (start < now) start.setDate(start.getDate() + 1);
    const end = new Date(start.getTime() + 10 * 60 * 1000);
    lines.push(
      "BEGIN:VEVENT",
      `UID:pharmaguard-${stamp}-${index}@local`,
      `DTSTAMP:${stamp}`,
      `DTSTART:${icsStamp(start)}`,
      `DTEND:${icsStamp(end)}`,
      "RRULE:FREQ=DAILY;COUNT=30",
      `SUMMARY:${icsEscape(`Take ${dose.drug} ${dose.dose}`)}`,
      `DESCRIPTION:${icsEscape(`${dose.instruction}\n\nDemo schedule — confirm with your pharmacist.`)}`,
      "BEGIN:VALARM",
      "TRIGGER:-PT0M",
      "ACTION:DISPLAY",
      `DESCRIPTION:${icsEscape(`Take ${dose.drug}`)}`,
      "END:VALARM",
      "END:VEVENT"
    );
  });

  (latestSchedule.weekly || []).forEach((dose, index) => {
    const [hour, minute] = String(dose.time || "08:00").split(":").map(Number);
    const start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hour, minute, 0, 0);
    if (start < now) start.setDate(start.getDate() + 7);
    const end = new Date(start.getTime() + 10 * 60 * 1000);
    lines.push(
      "BEGIN:VEVENT",
      `UID:pharmaguard-weekly-${stamp}-${index}@local`,
      `DTSTAMP:${stamp}`,
      `DTSTART:${icsStamp(start)}`,
      `DTEND:${icsStamp(end)}`,
      "RRULE:FREQ=WEEKLY;COUNT=12",
      `SUMMARY:${icsEscape(`WEEKLY: ${dose.drug} ${dose.dose}`)}`,
      `DESCRIPTION:${icsEscape(`${dose.instruction}\n\nWEEKLY dosing — never take daily.`)}`,
      "BEGIN:VALARM",
      "TRIGGER:-PT0M",
      "ACTION:DISPLAY",
      `DESCRIPTION:${icsEscape(`Take weekly ${dose.drug}`)}`,
      "END:VALARM",
      "END:VEVENT"
    );
  });

  lines.push("END:VCALENDAR");
  downloadBlob(lines.join("\r\n"), "pharmaguard-schedule.ics", "text/calendar;charset=utf-8");
  toast("Calendar file downloaded. Open it to add the doses.", "success");
}

function icsStamp(date) {
  const pad = (value) => String(value).padStart(2, "0");
  return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}T${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`;
}

function icsEscape(value) {
  return String(value)
    .replace(/\\/g, "\\\\")
    .replace(/;/g, "\\;")
    .replace(/,/g, "\\,")
    .replace(/\r?\n/g, "\\n");
}

function downloadBlob(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

// ---------------------------------------------------------------------------
// SBAR
// ---------------------------------------------------------------------------
async function openSbarModal() {
  if (!latestAuditResult) {
    toast("Run an audit first.", "error");
    return;
  }
  try {
    const res = await fetch("/api/sbar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        audit_result: latestAuditResult,
        patient_name: ($("patient-name").value || "Patient").trim(),
        age: Number($("patient-age").value) || 74
      })
    });
    if (!res.ok) throw new Error(`SBAR failed (${res.status})`);
    const data = await res.json();
    $("sbar-textarea").value = data.sbar;
    sbarModal.classList.add("open");
  } catch (error) {
    console.error("SBAR error:", error);
    toast("Could not generate the SBAR draft.", "error");
  }
}

// ---------------------------------------------------------------------------
// Label scanning / OCR
// ---------------------------------------------------------------------------
function openScanModal() {
  scanModal.classList.add("open");
}

async function loadSampleLabel() {
  try {
    const response = await fetch("/samples/sample-label.png");
    if (!response.ok) throw new Error("Sample label missing");
    const blob = await response.blob();
    const file = new File([blob], "sample-label.png", { type: "image/png" });
    handleScanFile(file);
  } catch (error) {
    console.error(error);
    toast("Sample label unavailable. Choose your own image or paste text.", "error");
  }
}

async function handleScanFile(file) {
  if (!file || scanBusy) return;
  scanBusy = true;
  try {
    await processScanFile(file);
  } finally {
    scanBusy = false;
  }
}

async function processScanFile(file) {
  if (file.size > 8 * 1024 * 1024) {
    toast("Image is larger than 8 MB. Choose a smaller photo.", "error");
    return;
  }

  const preview = $("scan-preview");
  if (preview.src.startsWith("blob:")) URL.revokeObjectURL(preview.src);
  preview.src = URL.createObjectURL(file);
  $("scan-preview-wrap").classList.remove("hidden");
  resetScanResults(true);

  $("scan-progress").classList.remove("hidden");
  updateScanProgress(5, "Loading the label reader…");

  try {
    await loadTesseract();
    const worker = await getTesseractWorker();
    updateScanProgress(35, "Reading the label…");
    const { data } = await worker.recognize(file);
    updateScanProgress(100, "Label read.");
    handleRecognizedText(data.text || "", file);
  } catch (error) {
    console.error("OCR error:", error);
    showScanError("Could not read this image. Try a sharper photo or paste the label text.");
  }
}

function loadTesseract() {
  if (typeof Tesseract !== "undefined") return Promise.resolve(Tesseract);
  if (tesseractScriptPromise) return tesseractScriptPromise;

  tesseractScriptPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js";
    script.async = true;
    script.onload = () => {
      if (typeof Tesseract !== "undefined") resolve(Tesseract);
      else reject(new Error("Tesseract.js did not initialize"));
    };
    script.onerror = () => reject(new Error("Tesseract.js failed to load"));
    document.head.appendChild(script);
  }).catch((error) => {
    tesseractScriptPromise = null;
    throw error;
  });

  return tesseractScriptPromise;
}

async function getTesseractWorker() {
  if (tesseractWorker) return tesseractWorker;
  if (tesseractLoading) return tesseractLoading;

  await loadTesseract();
  tesseractLoading = Tesseract.createWorker("eng", 1, {
    logger: (message) => {
      if (message.status === "recognizing text") {
        updateScanProgress(35 + Math.round((message.progress || 0) * 60), "Reading the label…");
      } else if (message.status) {
        updateScanProgress(10, `${message.status}…`);
      }
    }
  }).then((worker) => {
    tesseractWorker = worker;
    return worker;
  }).finally(() => {
    tesseractLoading = null;
  });

  return tesseractLoading;
}

function updateScanProgress(percent, text) {
  $("scan-progress-bar").style.width = `${Math.max(0, Math.min(100, percent))}%`;
  $("scan-progress-text").textContent = text;
}

function handleRecognizedText(text, file) {
  const cleaned = String(text || "").trim();
  $("scan-progress").classList.add("hidden");

  if (!cleaned) {
    showScanError("No text was found. Try a clearer image or paste the label text.");
    return;
  }

  $("scan-text").textContent = cleaned;
  $("scan-results").classList.remove("hidden");

  scanDetected = parseMedications(cleaned);
  renderScanDetected();

  if (scanDetected.length === 0) {
    $("scan-detected").innerHTML = `
      <div class="scan-empty">
        No known medicines were found in this label. Check the text above, or add the medicine manually.
      </div>
    `;
  }
}

function parseMedications(text) {
  const normalized = normalizeText(text);
  const tokens = normalized.split(" ").filter(Boolean);
  const found = new Map();

  allAvailableDrugs.forEach((drug) => {
    const aliases = buildAliasList(drug);
    let best = null;

    aliases.forEach((alias) => {
      const aliasTokens = normalizeText(alias).split(" ").filter(Boolean);
      if (!aliasTokens.length) return;
      for (let index = 0; index <= tokens.length - aliasTokens.length; index += 1) {
        const slice = tokens.slice(index, index + aliasTokens.length);
        if (slice.join(" ") === aliasTokens.join(" ")) {
          if (!best || aliasTokens.length > best.length) {
            best = { length: aliasTokens.length, index };
          }
          break;
        }
      }
    });

    if (best) {
      const dose = findDoseNear(tokens, best.index);
      const existing = found.get(drug.key);
      if (!existing || (dose && !existing.dose)) {
        found.set(drug.key, {
          key: drug.key,
          name: drug.name,
          brand: drug.brand,
          dose: dose || drug.default_dose,
          checked: true
        });
      }
    }
  });

  return [...found.values()];
}

function buildAliasList(drug) {
  const values = [drug.name, drug.brand, ...(drug.aliases || [])];
  const aliases = [];
  values.forEach((value) => {
    if (!value) return;
    String(value).split("/").forEach((part) => {
      const trimmed = part.trim();
      if (!trimmed) return;
      aliases.push(trimmed);
      const withoutParens = trimmed.replace(/\([^)]*\)/g, " ").trim();
      if (withoutParens && withoutParens !== trimmed) aliases.push(withoutParens);
      const inner = trimmed.match(/\(([^)]+)\)/);
      if (inner) aliases.push(inner[1]);
    });
  });
  return [...new Set(aliases)];
}

function findDoseNear(tokens, matchIndex) {
  const windowStart = Math.max(0, matchIndex - 4);
  const windowEnd = Math.min(tokens.length, matchIndex + 8);
  const window = tokens.slice(windowStart, windowEnd);
  for (let index = 0; index < window.length - 1; index += 1) {
    if (/^\d+(?:\.\d+)?$/.test(window[index]) && /^(mg|mcg|g|ml|units|iu|meq)$/.test(window[index + 1])) {
      return `${window[index]} ${window[index + 1]}`;
    }
  }
  return null;
}

function renderScanDetected() {
  const container = $("scan-detected");
  if (!scanDetected.length) {
    container.innerHTML = "";
    $("btn-add-scanned").disabled = true;
    return;
  }

  container.innerHTML = `
    <div class="scan-detected-title">Detected medicines — confirm before adding</div>
    ${scanDetected.map((item, index) => `
      <label class="scan-result-item">
        <input type="checkbox" data-scan-index="${index}" ${item.checked ? "checked" : ""}>
        <span class="scan-result-main"><strong>${escapeHtml(item.name)}</strong> <span class="scan-result-brand">${escapeHtml(item.brand || "")}</span></span>
        <span class="scan-result-dose">${escapeHtml(item.dose || "")}</span>
      </label>
    `).join("")}
  `;

  container.querySelectorAll("input[type=checkbox]").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      const index = Number(checkbox.dataset.scanIndex);
      if (scanDetected[index]) scanDetected[index].checked = checkbox.checked;
      $("btn-add-scanned").disabled = !scanDetected.some((item) => item.checked);
    });
  });

  $("btn-add-scanned").disabled = !scanDetected.some((item) => item.checked);
}

function addScannedMedications() {
  const selected = scanDetected.filter((item) => item.checked);
  if (!selected.length) return;

  let added = 0;
  let dosesUpdated = 0;
  selected.forEach((item) => {
    if (!currentRegimen.some((name) => name.toLowerCase() === item.name.toLowerCase())) {
      currentRegimen.push(item.name);
      added += 1;
    }
    if (item.key && item.dose) {
      const previous = doseOverrides.get(item.key);
      if (previous !== item.dose) {
        doseOverrides.set(item.key, item.dose);
        dosesUpdated += 1;
      }
    }
  });

  scanModal.classList.remove("open");
  clearPresetSelection();
  renderRegimenCards();
  runSafetyAudit();
  const parts = [];
  if (added) parts.push(`added ${added} medicine${added === 1 ? "" : "s"}`);
  if (dosesUpdated) parts.push(`applied ${dosesUpdated} label dose${dosesUpdated === 1 ? "" : "s"}`);
  toast(parts.length ? `From label: ${parts.join(", ")}.` : "Those medicines are already in the regimen.", parts.length ? "success" : "info");
}

function showScanError(message) {
  $("scan-progress").classList.add("hidden");
  $("scan-results").classList.remove("hidden");
  $("scan-text").textContent = "";
  $("scan-detected").innerHTML = `<div class="scan-empty error">${escapeHtml(message)}</div>`;
  $("btn-add-scanned").disabled = true;
  toast(message, "error");
}

function resetScanResults(keepPreview = false) {
  scanDetected = [];
  $("scan-text").textContent = "";
  $("scan-detected").innerHTML = "";
  $("scan-results").classList.add("hidden");
  $("btn-add-scanned").disabled = true;
  if (!keepPreview) {
    const preview = $("scan-preview");
    if (preview.src.startsWith("blob:")) URL.revokeObjectURL(preview.src);
    $("scan-preview-wrap").classList.add("hidden");
    preview.removeAttribute("src");
    $("scan-file").value = "";
  }
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------
function normalizeText(value) {
  return String(value)
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

let toastTimer = null;
function toast(message, type = "info") {
  let element = document.getElementById("toast");
  if (!element) {
    element = document.createElement("div");
    element.id = "toast";
    element.className = "toast";
    document.body.appendChild(element);
  }
  element.textContent = message;
  element.className = `toast ${type} visible`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => element.classList.remove("visible"), 4200);
}
