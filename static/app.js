/**
 * PharmaGuard AI — Client-Side Controller
 */

// Preset Regimens for fast clinical demonstration
const PRESETS = {
  cardiac: [
    "Warfarin",
    "Simvastatin",
    "Clarithromycin",
    "Ciprofloxacin",
    "Ibuprofen",
    "Calcium Carbonate"
  ],
  psych: [
    "Sertraline",
    "Tramadol",
    "Aspirin"
  ],
  endocrine: [
    "Levothyroxine",
    "Ferrous Sulfate (Iron)",
    "Metformin"
  ],
  safe: [
    "Metformin",
    "Simvastatin",
    "Lisinopril"
  ]
};

let currentRegimen = [...PRESETS.cardiac];
let allAvailableDrugs = [];
let latestAuditResult = null;

// DOM Elements
const drugDropdown = document.getElementById("drug-dropdown");
const btnAddDrug = document.getElementById("btn-add-drug");
const btnClearAll = document.getElementById("btn-clear-all");
const btnRunAudit = document.getElementById("btn-run-audit");
const regimenListEl = document.getElementById("regimen-list");
const medCountBadge = document.getElementById("med-count-badge");

const scoreCard = document.getElementById("safety-score-card");
const scoreValueEl = document.getElementById("score-value");
const scoreStatusText = document.getElementById("score-status-text");
const scoreSummaryMetrics = document.getElementById("score-summary-metrics");
const scoreRecommendationSub = document.getElementById("score-recommendation-sub");

const violationsContainer = document.getElementById("violations-container");
const violationsCountEl = document.getElementById("violations-count");
const timelineContainer = document.getElementById("timeline-container");
const patientAdviceList = document.getElementById("patient-advice-list");

const btnExportSbar = document.getElementById("btn-export-sbar");
const sbarModal = document.getElementById("sbar-modal");
const btnCloseModal = document.getElementById("btn-close-modal");
const btnModalDone = document.getElementById("btn-modal-done");
const btnCopySbar = document.getElementById("btn-copy-sbar");
const sbarTextarea = document.getElementById("sbar-textarea");
const copyBtnText = document.getElementById("copy-btn-text");

// Initialize
document.addEventListener("DOMContentLoaded", async () => {
  await fetchDrugs();
  setupEventListeners();
  renderRegimenCards();
  await runSafetyAudit();
});

// Fetch Available Drugs
async function fetchDrugs() {
  try {
    const res = await fetch("/api/drugs");
    const data = await res.json();
    allAvailableDrugs = data.drugs || [];

    drugDropdown.innerHTML = '<option value="" disabled selected>-- Select a medication to add --</option>';
    allAvailableDrugs.forEach(drug => {
      const opt = document.createElement("option");
      opt.value = drug.name;
      opt.textContent = `${drug.name} (${drug.brand}) — ${drug.class}`;
      drugDropdown.appendChild(opt);
    });
  } catch (err) {
    console.error("Error fetching drug registry:", err);
  }
}

// Event Listeners
function setupEventListeners() {
  // Preset Buttons
  document.querySelectorAll(".btn-preset").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".btn-preset").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const key = btn.dataset.preset;
      currentRegimen = [...(PRESETS[key] || [])];
      renderRegimenCards();
      runSafetyAudit();
    });
  });

  // Add Drug Button
  btnAddDrug.addEventListener("click", () => {
    const selected = drugDropdown.value;
    if (selected && !currentRegimen.includes(selected)) {
      currentRegimen.push(selected);
      renderRegimenCards();
      runSafetyAudit();
    }
  });

  // Clear All
  btnClearAll.addEventListener("click", () => {
    currentRegimen = [];
    renderRegimenCards();
    runSafetyAudit();
  });

  // Run Audit Button
  btnRunAudit.addEventListener("click", () => {
    runSafetyAudit();
  });

  // Tabs
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      const tabId = `tab-${btn.dataset.tab}`;
      document.getElementById(tabId).classList.add("active");
    });
  });

  // SBAR Modal
  btnExportSbar.addEventListener("click", async () => {
    await openSbarModal();
  });

  btnCloseModal.addEventListener("click", () => sbarModal.classList.remove("open"));
  btnModalDone.addEventListener("click", () => sbarModal.classList.remove("open"));

  btnCopySbar.addEventListener("click", () => {
    navigator.clipboard.writeText(sbarTextarea.value);
    copyBtnText.textContent = "Copied to Clipboard!";
    setTimeout(() => {
      copyBtnText.textContent = "Copy to Clipboard";
    }, 2000);
  });
}

// Render Regimen List
function renderRegimenCards() {
  regimenListEl.innerHTML = "";
  medCountBadge.textContent = `${currentRegimen.length} Medication${currentRegimen.length === 1 ? '' : 's'}`;

  if (currentRegimen.length === 0) {
    regimenListEl.innerHTML = '<div style="padding: 20px; text-align: center; color: #94a3b8; font-size: 0.85rem;">No medications selected. Choose a preset or select a drug above.</div>';
    return;
  }

  currentRegimen.forEach((medName, idx) => {
    const card = document.createElement("div");
    card.className = "med-card";

    const drugData = allAvailableDrugs.find(d => d.name.toLowerCase() === medName.toLowerCase()) || {
      name: medName,
      brand: "Generic",
      class: "Prescription Therapeutic",
      default_dose: "Standard Dose",
      food_warnings: "Take as directed."
    };

    card.innerHTML = `
      <div class="med-info">
        <h4>${drugData.name} <span class="med-brand">(${drugData.brand})</span></h4>
        <div class="med-class">${drugData.class}</div>
        <div class="med-details-row">
          <span>Dose: ${drugData.default_dose}</span>
          <span>•</span>
          <span>${drugData.food_warnings}</span>
        </div>
      </div>
      <button class="med-remove-btn" title="Remove medication" data-idx="${idx}">&times;</button>
    `;

    card.querySelector(".med-remove-btn").addEventListener("click", (e) => {
      const removeIdx = parseInt(e.target.dataset.idx, 10);
      currentRegimen.splice(removeIdx, 1);
      renderRegimenCards();
      runSafetyAudit();
    });

    regimenListEl.appendChild(card);
  });
}

// Run Safety Audit
async function runSafetyAudit() {
  if (currentRegimen.length === 0) {
    scoreValueEl.textContent = "100";
    scoreStatusText.textContent = "NO MEDICATIONS ACTIVE";
    scoreCard.className = "score-card score-safe";
    scoreSummaryMetrics.innerHTML = '<span class="metric-tag green">0 Conflicts</span>';
    violationsContainer.innerHTML = '<p style="color: #64748b; font-size: 0.85rem;">Add medications to run safety audit.</p>';
    violationsCountEl.textContent = "0";
    timelineContainer.innerHTML = "";
    patientAdviceList.innerHTML = "";
    return;
  }

  try {
    const res = await fetch("/api/audit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ medications: currentRegimen })
    });
    const result = await res.json();
    latestAuditResult = result;

    updateScoreCard(result);
    renderViolations(result);
    renderPatientAdvice(result);
    await fetchAndRenderSchedule(result);
  } catch (err) {
    console.error("Audit error:", err);
  }
}

// Update Score Card
function updateScoreCard(result) {
  scoreValueEl.textContent = result.safety_score;
  scoreStatusText.textContent = result.overall_status;

  scoreCard.className = "score-card";
  if (result.critical_count > 0) {
    scoreCard.classList.add("score-danger");
    scoreSummaryMetrics.innerHTML = `
      <span class="metric-tag red">${result.critical_count} Critical Contraindication${result.critical_count > 1 ? 's' : ''}</span>
      ${result.moderate_count > 0 ? `<span class="metric-tag amber">${result.moderate_count} Absorption Conflict${result.moderate_count > 1 ? 's' : ''}</span>` : ''}
    `;
    scoreRecommendationSub.textContent = "High-risk regimen. Urgent clinical intervention required to prevent adverse drug events.";
  } else if (result.moderate_count > 0) {
    scoreCard.classList.add("score-warning");
    scoreSummaryMetrics.innerHTML = `
      <span class="metric-tag amber">${result.moderate_count} Temporal Absorption Conflict${result.moderate_count > 1 ? 's' : ''}</span>
    `;
    scoreRecommendationSub.textContent = "Requires 3-to-4 hour dose separation to prevent malabsorption or lab monitoring.";
  } else {
    scoreCard.classList.add("score-safe");
    scoreSummaryMetrics.innerHTML = `<span class="metric-tag green">0 Known Adverse Clashes</span>`;
    scoreRecommendationSub.textContent = "No major contraindications identified. Follow standard administration schedules.";
  }
}

// Render Violations
function renderViolations(result) {
  violationsContainer.innerHTML = "";
  const list = result.interactions || [];
  violationsCountEl.textContent = list.length;

  if (list.length === 0) {
    violationsContainer.innerHTML = `
      <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 6px; padding: 18px; color: #065f46; text-align: center;">
        <h4 style="font-weight: 700; font-size: 0.95rem;">✅ Regimen Verified Safe</h4>
        <p style="font-size: 0.82rem; margin-top: 4px;">No critical or moderate pairwise contraindications detected between the listed medications.</p>
      </div>
    `;
    return;
  }

  list.forEach(v => {
    const card = document.createElement("div");
    card.className = `violation-card ${v.severity.toLowerCase()}`;
    card.innerHTML = `
      <div class="violation-header">
        <div class="violation-title-group">
          <h4>${v.title}</h4>
          <div class="violation-drugs"><strong>Interacting Pair:</strong> ${v.drug_a} + ${v.drug_b}</div>
        </div>
        <span class="severity-pill ${v.severity.toLowerCase()}">${v.severity}</span>
      </div>
      <div class="violation-body">
        <p><strong>Clinical Mechanism:</strong> ${v.mechanism}</p>
      </div>
      <div class="violation-action">
        <span class="action-label">Clinical Action:</span>
        <span>${v.clinical_action}</span>
      </div>
    `;
    violationsContainer.appendChild(card);
  });
}

// Fetch & Render 24-Hour Schedule
async function fetchAndRenderSchedule(auditResult) {
  try {
    const res = await fetch("/api/reschedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        regimen: auditResult.regimen,
        interactions: auditResult.interactions
      })
    });
    const sched = await res.json();
    renderTimeline(sched);
  } catch (err) {
    console.error("Schedule error:", err);
  }
}

function renderTimeline(sched) {
  timelineContainer.innerHTML = "";
  const timeline = sched.timeline || [];

  timeline.forEach(slot => {
    const slotEl = document.createElement("div");
    slotEl.className = "timeline-slot";

    let medsHtml = '<span style="color: #94a3b8; font-size: 0.8rem; font-style: italic;">No medications scheduled in this slot</span>';
    if (slot.medications.length > 0) {
      medsHtml = slot.medications.map(m => `
        <div style="margin-bottom: 6px;">
          <span class="slot-med-tag ${m.status === 'rescheduled' ? 'rescheduled' : ''}">
            <strong>${m.name}</strong> (${m.dose})
          </span>
          <div class="slot-instruction">${m.instruction}</div>
        </div>
      `).join("");
    }

    slotEl.innerHTML = `
      <div class="slot-time-col">
        <div class="slot-time">${slot.time}</div>
        <div class="slot-label">${slot.name}</div>
      </div>
      <div class="slot-content-col">
        ${medsHtml}
      </div>
    `;

    timelineContainer.appendChild(slotEl);
  });
}

// Render Patient Advice
function renderPatientAdvice(result) {
  patientAdviceList.innerHTML = "";
  const advice = result.patient_summary || [];

  advice.forEach(text => {
    const item = document.createElement("div");
    item.className = "advice-card";
    item.textContent = text;
    patientAdviceList.appendChild(item);
  });
}

// Open SBAR Modal
async function openSbarModal() {
  if (!latestAuditResult) return;
  try {
    const res = await fetch("/api/sbar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        audit_result: latestAuditResult,
        patient_name: "Patient Jane Doe",
        age: 74
      })
    });
    const data = await res.json();
    sbarTextarea.value = data.sbar;
    sbarModal.classList.add("open");
  } catch (err) {
    console.error("SBAR error:", err);
  }
}
