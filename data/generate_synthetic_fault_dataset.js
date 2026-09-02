// Deterministic synthetic fault dataset generator for the Heat Pump Field
// Commissioning & Connectivity Copilot (Round 1 POC). Self-authored — not
// derived from any real customer, installer, or telemetry data.

// Simple seeded PRNG (mulberry32) for reproducibility.
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rand = mulberry32(42);
function pick(arr) { return arr[Math.floor(rand() * arr.length)]; }
function chance(p) { return rand() < p; }
function randInt(min, max) { return Math.floor(rand() * (max - min + 1)) + min; }

const models = ["TF-08", "TF-12", "AS-10", "AS-16"]; // fictional Chleo model codes
const firmwareByRecency = ["2.3.1", "2.4.0", "2.4.2", "3.0.0"]; // older -> newer
const installerTypes = ["own_field_installer", "partner_SHK"];

// Fault archetypes: each has a category, a pool of symptom phrasings, a
// pool of fault codes (or none, for connectivity), a fix/escalation action,
// typical commissioning time range (minutes), and first-visit-fix probability.
const archetypes = [
  {
    category: "hardware_fault",
    codes: ["E4", "E7", "E12"],
    symptoms: [
      "No heat output, outdoor unit fan not spinning",
      "Compressor short-cycling, error code {code} on display",
      "Low refrigerant pressure alarm, error code {code}",
      "Outdoor unit making grinding noise then shutting down, {code} logged"
    ],
    fix: "Escalate to hardware service technician (compressor/refrigerant circuit inspection). Not resolvable by app/firmware update.",
    time: [90, 180],
    firstVisitFixProb: 0.55
  },
  {
    category: "connectivity_issue",
    codes: [null, null, "CONN-01"],
    symptoms: [
      "App shows unit offline, unit itself is heating normally",
      "Wi-Fi pairing fails after firmware update to {fw}",
      "Smart meter gateway will not pair with the control unit",
      "Intermittent 'lost connection' notifications, no fault at the unit"
    ],
    fix: "Re-pair the control unit via the installer app, confirm router 2.4GHz band is enabled, and check smart-meter-gateway certificate status. No hardware visit required.",
    time: [20, 45],
    firstVisitFixProb: 0.85
  },
  {
    category: "installer_error",
    codes: [null, "E2"],
    symptoms: [
      "Unit trips on startup, wiring terminal check shows a loose connection",
      "Heating circuit pressure too low after commissioning, {code} on display",
      "Flow/return sensors reversed during install",
      "Buffer tank valve left in service position after commissioning"
    ],
    fix: "Correct commissioning step per install checklist (wiring, pressure fill, sensor orientation, or valve position); no manufacturer escalation needed.",
    time: [30, 75],
    firstVisitFixProb: 0.9
  }
];

// Confusable pairs used to inject realistic misclassification noise, since
// hardware-vs-connectivity is the exact ambiguity this copilot exists to
// resolve (see research/opportunities_risks.md).
function confusedGuess(trueCategory) {
  if (trueCategory === "hardware_fault") return chance(0.18) ? "connectivity_issue" : "hardware_fault";
  if (trueCategory === "connectivity_issue") return chance(0.22) ? "hardware_fault" : "connectivity_issue";
  return chance(0.12) ? "hardware_fault" : "installer_error"; // installer_error
}

const rows = [];
let id = 1;
const startDate = new Date("2025-03-01T00:00:00Z");
const N = 220;
const ROLLOUT_DAY = 100; // day (of 180) firmware 3.0.0 rollout begins on the TF-12 line

for (let i = 0; i < N; i++) {
  const dayOffset = Math.floor((i / N) * 180);
  const postRollout = dayOffset >= ROLLOUT_DAY;
  const arch = pick(archetypes);
  // Narrative: a 3.0.0 firmware rollout on the TF-12 line coincides with a
  // spike in connectivity issues (illustrates a real rollout-quality risk,
  // and gives the dashboard a concrete "which firmware/model to investigate"
  // insight rather than flat, uninformative distributions).
  let model, fw;
  if (arch.category === "connectivity_issue" && postRollout && chance(0.65)) {
    model = "TF-12";
    fw = "3.0.0";
  } else {
    model = pick(models);
    fw = postRollout ? pick(firmwareByRecency) : pick(["2.3.1", "2.4.0", "2.4.2"]);
  }
  const installer = pick(installerTypes);
  const codeRaw = pick(arch.codes);
  const code = codeRaw ? codeRaw : "";
  const symptomTemplate = pick(arch.symptoms);
  const symptom = symptomTemplate.replace("{code}", code || "n/a").replace("{fw}", fw);
  const predicted = confusedGuess(arch.category);
  const correctPrediction = predicted === arch.category;
  // If the model wrongly predicted "hardware_fault" for a non-hardware issue,
  // that's a false-hardware-fault (drives an unnecessary parts dispatch).
  const falseHardwareFault = predicted === "hardware_fault" && arch.category !== "hardware_fault";
  const firstVisitFixed = chance(correctPrediction ? arch.firstVisitFixProb : arch.firstVisitFixProb * 0.5);
  const commissioningMinutes = randInt(arch.time[0], arch.time[1]) + (correctPrediction ? 0 : randInt(20, 60));
  const day = new Date(startDate.getTime() + dayOffset * 86400000 + randInt(0, 20) * 3600000);
  const dateStr = day.toISOString().slice(0, 10);

  rows.push({
    fault_id: `FLT-${String(id).padStart(4, "0")}`,
    date: dateStr,
    model,
    firmware_version: fw,
    installer_type: installer,
    reported_symptom: symptom,
    fault_code: code,
    true_category: arch.category,
    predicted_category: predicted,
    correct_prediction: correctPrediction,
    false_hardware_fault: falseHardwareFault,
    fix_or_escalation_action: arch.fix,
    first_visit_fixed: firstVisitFixed,
    commissioning_time_minutes: commissioningMinutes
  });
  id++;
}

const headers = Object.keys(rows[0]);
const escape = (v) => {
  const s = String(v);
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};
const lines = [headers.join(",")].concat(rows.map(r => headers.map(h => escape(r[h])).join(",")));
console.log(lines.join("\n"));
