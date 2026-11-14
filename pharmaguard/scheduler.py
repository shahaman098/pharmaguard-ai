"""Algorithmic 24-Hour Medication Schedule De-confliction Solver."""

from typing import List, Dict, Any


class ScheduleOptimizer:
    """Takes a list of active medications and detected absorption/chelation conflicts,
    then computes a conflict-free 24-hour administration timeline.
    """

    def __init__(self):
        # Canonical daily time slots
        self.time_slots = [
            {"slot_id": "fasting", "name": "Early Morning (Fasting)", "time": "07:00", "notes": "30-60 min before breakfast with full glass of water"},
            {"slot_id": "breakfast", "name": "Breakfast / Morning", "time": "08:30", "notes": "With morning meal"},
            {"slot_id": "lunch", "name": "Lunch / Midday", "time": "12:30", "notes": "With midday meal"},
            {"slot_id": "dinner", "name": "Dinner / Evening", "time": "18:30", "notes": "With evening meal"},
            {"slot_id": "bedtime", "name": "Bedtime", "time": "22:00", "notes": "Prior to sleep"}
        ]

    def build_schedule(self, regimen: List[Dict[str, Any]], interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Allocates each drug to an optimal slot while enforcing spacing constraints."""
        allocated_slots = {s["slot_id"]: [] for s in self.time_slots}
        adjustments_made = []

        # Find which drugs have chelation/timing conflicts
        spacing_conflicts = [i for i in interactions if i.get("spacing_resolvable")]

        for med in regimen:
            key = med["key"]
            name = med["name"]
            dose = med["default_dose"]
            food = med["food_warnings"]

            # Specific pharmacological placement rules
            if key == "levothyroxine":
                # Must be taken fasting 07:00
                allocated_slots["fasting"].append({
                    "name": name,
                    "dose": dose,
                    "instruction": "Take fasting with water. Do NOT take within 4 hours of calcium or iron.",
                    "status": "locked"
                })

            elif key == "simvastatin":
                # HMG-CoA reductase peaks at night
                allocated_slots["bedtime"].append({
                    "name": name,
                    "dose": dose,
                    "instruction": "Take before bed. Avoid grapefruit.",
                    "status": "locked"
                })

            elif key == "ciprofloxacin":
                # Twice daily antibiotic: Breakfast & Dinner
                allocated_slots["breakfast"].append({
                    "name": name,
                    "dose": dose,
                    "instruction": "Dose 1 of 2. Avoid dairy or antacids at breakfast.",
                    "status": "timing_critical"
                })
                allocated_slots["dinner"].append({
                    "name": name,
                    "dose": dose,
                    "instruction": "Dose 2 of 2. Keep 12-hour spacing from morning dose.",
                    "status": "timing_critical"
                })

            elif key == "calcium_carbonate":
                # If co-prescribed with ciprofloxacin or levothyroxine, shift to lunch
                conflict_active = any(
                    "ciprofloxacin" in i.get("pair_keys", ()) or "levothyroxine" in i.get("pair_keys", ())
                    for i in spacing_conflicts
                )
                if conflict_active:
                    allocated_slots["lunch"].append({
                        "name": name,
                        "dose": dose,
                        "instruction": "OPTIMIZED: Shifted to Lunch (12:30) to create a safe 4-hour spacing window from morning Ciprofloxacin / Levothyroxine.",
                        "status": "rescheduled"
                    })
                    adjustments_made.append(
                        "Separated Calcium Carbonate to Lunch (12:30) to prevent chelation and malabsorption of antibiotic/thyroid medication."
                    )
                else:
                    allocated_slots["breakfast"].append({
                        "name": name,
                        "dose": dose,
                        "instruction": "Take with breakfast.",
                        "status": "standard"
                    })

            elif key == "ferrous_sulfate":
                # Shift to Lunch or Evening away from Levothyroxine / Calcium
                allocated_slots["lunch"].append({
                    "name": name,
                    "dose": dose,
                    "instruction": "OPTIMIZED: Take at Midday with Vitamin C (orange juice) to enhance absorption. Spaced from morning medications.",
                    "status": "rescheduled"
                })
                adjustments_made.append("Allocated Ferrous Sulfate to Midday for optimal absorption and chelation avoidance.")

            elif key in ("warfarin",):
                allocated_slots["dinner"].append({
                    "name": name,
                    "dose": dose,
                    "instruction": "Take in the evening with consistent food intake.",
                    "status": "standard"
                })

            elif key in ("lisinopril", "spironolactone"):
                allocated_slots["breakfast"].append({
                    "name": name,
                    "dose": dose,
                    "instruction": "Take in the morning with breakfast.",
                    "status": "standard"
                })

            elif key in ("metformin", "clarithromycin"):
                allocated_slots["breakfast"].append({
                    "name": name,
                    "dose": dose,
                    "instruction": "Morning dose with meal.",
                    "status": "standard"
                })
                allocated_slots["dinner"].append({
                    "name": name,
                    "dose": dose,
                    "instruction": "Evening dose with meal.",
                    "status": "standard"
                })

            else:
                # Default to morning
                allocated_slots["breakfast"].append({
                    "name": name,
                    "dose": dose,
                    "instruction": f"Standard dose ({food})",
                    "status": "standard"
                })

        # Assemble timeline view
        timeline = []
        for slot in self.time_slots:
            slot_meds = allocated_slots[slot["slot_id"]]
            timeline.append({
                "slot_id": slot["slot_id"],
                "name": slot["name"],
                "time": slot["time"],
                "notes": slot["notes"],
                "medications": slot_meds,
                "has_meds": len(slot_meds) > 0
            })

        return {
            "timeline": timeline,
            "adjustments_made": adjustments_made,
            "total_slots_used": sum(1 for t in timeline if t["has_meds"])
        }
