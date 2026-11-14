"""Constraint-based 24-hour medication schedule optimizer.

The scheduler treats every dose as an interval-placement problem:

* fasting drugs must land in the early-morning fasting window;
* with-meal drugs must land near a meal;
* multi-dose drugs must respect a minimum intra-dose interval;
* chelation/absorption interactions impose a minimum separation between two
  different drugs;
* weekly and as-needed medicines are kept out of the daily timeline.

A deterministic backtracking search finds a conflict-free assignment. If the
hard constraints cannot be met, the solver relaxes spacing in stages and reports
the unresolved conflict instead of silently pretending it was fixed.
"""

from __future__ import annotations

import time
from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

DAY_START = 6 * 60
DAY_END = 23 * 60
BEDTIME = 22 * 60

MEAL_ANCHORS: Tuple[Tuple[str, int], ...] = (
    ("Breakfast", 8 * 60),
    ("Lunch", 12 * 60 + 30),
    ("Dinner", 18 * 60 + 30),
)

PERIOD_WINDOWS = {
    "morning": (6 * 60, 11 * 60),
    "midday": (11 * 60, 15 * 60),
    "evening": (16 * 60, 20 * 60),
    "bedtime": (20 * 60, 22 * 60),
    "any": (7 * 60, 22 * 60),
}

MEAL_WINDOWS = tuple(
    (anchor - 30, anchor + 30) for _, anchor in MEAL_ANCHORS
)

NODE_LIMIT = 200_000
SEARCH_TIME_LIMIT_SECONDS = 2.0


def _hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _period_target(period: str) -> int:
    if period == "morning":
        return 8 * 60 + 30
    if period == "midday":
        return 12 * 60 + 30
    if period == "evening":
        return 18 * 60 + 30
    if period == "bedtime":
        return 22 * 60
    return 8 * 60


def _slot_label(minutes: int) -> str:
    if minutes <= 7 * 60 + 30:
        return "Fasting / early morning"
    if minutes <= 10 * 60:
        return "Breakfast"
    if minutes <= 14 * 60:
        return "Midday"
    if minutes <= 17 * 60:
        return "Afternoon"
    if minutes <= 20 * 60 + 30:
        return "Evening"
    return "Bedtime"


class ScheduleOptimizer:
    """Computes a daily administration plan with explicit constraint checks."""

    def __init__(self) -> None:
        self.meal_anchors = MEAL_ANCHORS
        self.period_windows = PERIOD_WINDOWS
        self.meal_windows = MEAL_WINDOWS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def build_schedule(
        self,
        regimen: List[Dict[str, Any]],
        interactions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if not isinstance(regimen, list):
            regimen = []
        if not isinstance(interactions, list):
            interactions = []
        regimen = [
            med for med in regimen
            if isinstance(med, dict) and (med.get("key") or med.get("name"))
        ]
        interactions = [item for item in interactions if isinstance(item, dict)]

        plans: List[Dict[str, Any]] = []
        prn: List[Dict[str, Any]] = []
        weekly: List[Dict[str, Any]] = []

        for med in regimen:
            plan = self._make_plan(med)
            if plan["frequency"] == "as_needed":
                prn.append(self._prn_entry(plan))
            elif plan["frequency"] == "weekly":
                weekly.append(self._weekly_entry(plan))
            else:
                plans.append(plan)

        spacing_constraints = self._spacing_constraints(interactions)
        critical_constraints = self._critical_constraints(interactions)
        all_constraints = spacing_constraints + critical_constraints
        assignment, solver_meta = self._solve(plans, all_constraints)

        doses: List[Dict[str, Any]] = []
        for plan in plans:
            times = assignment.get(plan["key"], [])
            for index, minute in enumerate(times):
                doses.append(self._dose_entry(plan, minute, index, interactions))

        doses.sort(key=lambda item: (item["minutes"], item["drug"]))

        groups: List[Dict[str, Any]] = []
        for minute in sorted({dose["minutes"] for dose in doses}):
            group_doses = [dose for dose in doses if dose["minutes"] == minute]
            groups.append({
                "time": _hhmm(minute),
                "minutes": minute,
                "label": _slot_label(minute),
                "doses": group_doses,
            })

        unresolved = self._unresolved(spacing_constraints, assignment)
        critical_conflicts = self._critical_conflicts(critical_constraints, assignment)
        adjustments = self._adjustments(plans, assignment, all_constraints)

        return {
            "groups": groups,
            "doses": doses,
            "weekly": weekly,
            "prn": prn,
            "adjustments_made": adjustments,
            "unresolved": unresolved,
            "critical_conflicts": critical_conflicts,
            "total_slots_used": len(groups),
            "total_doses": len(doses),
            "constraints_checked": len(all_constraints),
            "solver": solver_meta,
            "disclaimer": (
                "Demo schedule only. Confirm every dose and timing change with a "
                "pharmacist or prescriber before use."
            ),
        }

    # ------------------------------------------------------------------
    # Plan preparation
    # ------------------------------------------------------------------
    def _make_plan(self, med: Dict[str, Any]) -> Dict[str, Any]:
        schedule = med.get("schedule", {}) or {}
        frequency = schedule.get("frequency", "daily")
        doses_per_day = int(schedule.get("doses_per_day", 1) or 1)

        if frequency == "bid":
            doses_per_day = max(2, doses_per_day)
        elif frequency == "tid":
            doses_per_day = max(3, doses_per_day)
        elif frequency in ("weekly", "as_needed"):
            doses_per_day = 1

        return {
            "key": med.get("key", med.get("name", "unknown").lower().replace(" ", "_")),
            "name": med.get("name", "Medication"),
            "dose": med.get("default_dose", "As prescribed"),
            "frequency": frequency,
            "doses_per_day": doses_per_day,
            "meal_relation": schedule.get("meal_relation", "any"),
            "preferred_period": schedule.get("preferred_period", "any"),
            "min_interval_hours": float(schedule.get("min_interval_hours", 20)),
            "note": schedule.get("note", ""),
            "food": med.get("food_warnings", ""),
            "candidates": [],
        }

    def _candidate_times(self, plan: Dict[str, Any]) -> List[int]:
        """All legal base times for this plan, respecting meal/fasting rules."""
        if plan["meal_relation"] == "fasting":
            times = list(range(DAY_START, 7 * 60 + 31, 15))
        elif plan["meal_relation"] == "with_meal":
            times = [
                minute
                for start, end in self.meal_windows
                for minute in range(start, end + 1, 15)
            ]
        else:
            times = list(range(7 * 60, DAY_END + 1, 15))

        window = self.period_windows.get(plan["preferred_period"], self.period_windows["any"])
        preferred = [minute for minute in times if window[0] <= minute <= window[1]]
        return preferred or times

    def _candidate_schedules(self, plan: Dict[str, Any]) -> List[List[int]]:
        if plan["frequency"] in ("as_needed", "weekly"):
            return [[self._preferred_time(plan)]]

        base_times = self._candidate_times(plan)
        count = max(1, plan["doses_per_day"])
        min_gap = max(1, int(round(plan["min_interval_hours"] * 60)))

        if count == 1:
            schedules = [[minute] for minute in base_times]
        elif plan["meal_relation"] == "with_meal":
            anchors = [anchor for _, anchor in self.meal_anchors]
            schedules = []
            for combo in combinations(anchors, count):
                ordered = list(combo)
                if all(b - a >= min_gap for a, b in zip(ordered, ordered[1:])):
                    schedules.append(ordered)
            if not schedules:
                # Fall back to evenly spaced meal-adjacent times.
                schedules = self._evenly_spaced(base_times, count, min_gap)
        else:
            interval = max(24 * 60 // count, min_gap)
            schedules = []
            for minute in base_times:
                candidate = [minute + index * interval for index in range(count)]
                if candidate[-1] <= DAY_END:
                    schedules.append(candidate)

        if not schedules:
            schedules = [[self._preferred_time(plan)]]

        target = _period_target(plan["preferred_period"])
        schedules.sort(key=lambda values: (sum(abs(v - target) for v in values), values))
        return schedules

    def _evenly_spaced(self, base_times: List[int], count: int, min_gap: int) -> List[List[int]]:
        schedules = []
        for minute in base_times:
            candidate = [minute + index * min_gap for index in range(count)]
            if candidate[-1] <= DAY_END:
                schedules.append(candidate)
        return schedules

    def _preferred_time(self, plan: Dict[str, Any]) -> int:
        if plan["meal_relation"] == "fasting":
            return 6 * 60 + 30
        if plan["meal_relation"] == "with_meal":
            return 8 * 60
        if plan["preferred_period"] == "bedtime":
            return BEDTIME
        return _period_target(plan["preferred_period"])

    # ------------------------------------------------------------------
    # Backtracking solver
    # ------------------------------------------------------------------
    def _spacing_constraints(
        self, interactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        constraints = []
        for item in interactions:
            if not item.get("spacing_resolvable"):
                continue
            hours = float(item.get("recommended_spacing_hours", 0) or 0)
            if hours <= 0:
                continue
            pair = tuple(item.get("pair_keys", ()))
            if len(pair) != 2:
                continue
            constraints.append({
                "a": pair[0],
                "b": pair[1],
                "hours": hours,
                "title": item.get("title", "Timing interaction"),
                "kind": "spacing",
            })
        return constraints

    def _critical_constraints(
        self, interactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Keep contraindicated pairs from being displayed at the same minute.

        This is an administration-safety floor, not a claim that the interaction
        is resolved. The UI still shows the critical warning.
        """
        constraints = []
        for item in interactions:
            if item.get("severity") != "CRITICAL":
                continue
            pair = tuple(item.get("pair_keys", ()))
            if len(pair) != 2:
                continue
            constraints.append({
                "a": pair[0],
                "b": pair[1],
                "hours": 2.0,
                "title": item.get("title", "Critical interaction"),
                "kind": "critical",
            })
        return constraints

    def _solve(
        self,
        plans: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, List[int]], Dict[str, Any]]:
        for plan in plans:
            plan["candidates"] = self._candidate_schedules(plan)

        # Most constrained first: fewer candidates, more doses.
        ordered = sorted(
            plans,
            key=lambda plan: (len(plan["candidates"]), -plan["doses_per_day"], plan["name"]),
        )

        total_candidates = sum(len(plan["candidates"]) for plan in plans)
        attempts = 0

        # Progressively relax hard constraints. The final stage drops every
        # constraint so the caller always receives a complete schedule; any
        # violations are reported in `unresolved` / `critical_conflicts`.
        for relax_factor, relax_critical in (
            (1.0, False),
            (0.5, False),
            (0.0, False),
            (0.0, True),
        ):
            relaxed_constraints = [
                {
                    **constraint,
                    "hours": (
                        constraint["hours"] * relax_factor
                        if (constraint.get("kind") != "critical" or relax_critical)
                        else constraint["hours"]
                    ),
                }
                for constraint in constraints
            ]
            assignment: Dict[str, List[int]] = {}
            self._nodes = 0
            self._deadline = time.perf_counter() + SEARCH_TIME_LIMIT_SECONDS
            result = self._search(ordered, relaxed_constraints, assignment, 0)
            attempts += 1
            if result is not None:
                return result, {
                    "algorithm": "deterministic backtracking with interval constraints",
                    "candidate_schedules": total_candidates,
                    "nodes_explored": self._nodes,
                    "relaxation": relax_factor,
                    "critical_relaxed": relax_critical,
                    "fully_constrained": relax_factor == 1.0 and not relax_critical,
                    "attempts": attempts,
                }

        return {}, {
            "algorithm": "deterministic backtracking with interval constraints",
            "candidate_schedules": total_candidates,
            "nodes_explored": getattr(self, "_nodes", 0),
            "relaxation": None,
            "critical_relaxed": True,
            "fully_constrained": False,
            "attempts": attempts,
        }

    def _search(
        self,
        plans: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        assignment: Dict[str, List[int]],
        index: int,
    ) -> Optional[Dict[str, List[int]]]:
        self._nodes += 1
        if self._nodes > NODE_LIMIT or time.perf_counter() > getattr(
            self, "_deadline", float("inf")
        ):
            return None
        if index == len(plans):
            return dict(assignment)

        plan = plans[index]
        for candidate in plan["candidates"]:
            if not self._candidate_is_valid(plan["key"], candidate, assignment, constraints):
                continue
            assignment[plan["key"]] = candidate
            result = self._search(plans, constraints, assignment, index + 1)
            if result is not None:
                return result
            del assignment[plan["key"]]
        return None

    def _candidate_is_valid(
        self,
        key: str,
        times: List[int],
        assignment: Dict[str, List[int]],
        constraints: List[Dict[str, Any]],
    ) -> bool:
        for constraint in constraints:
            if key not in (constraint["a"], constraint["b"]):
                continue
            other = constraint["b"] if key == constraint["a"] else constraint["a"]
            if other not in assignment:
                continue
            minimum = int(round(constraint["hours"] * 60))
            for first in times:
                for second in assignment[other]:
                    if abs(first - second) < minimum:
                        return False
        return True

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------
    def _dose_entry(
        self,
        plan: Dict[str, Any],
        minute: int,
        index: int,
        interactions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        critical = self._critical_partners(plan["key"], interactions)
        naive = self._preferred_time(plan)
        moved = index == 0 and abs(minute - naive) > 60

        instruction = plan.get("note") or plan.get("food") or "Take as directed."
        if plan["doses_per_day"] > 1:
            instruction = f"Dose {index + 1} of {plan['doses_per_day']}. {instruction}"
        if critical:
            instruction += " CRITICAL: do not co-administer with " + ", ".join(critical) + " without clinician review."

        if plan["meal_relation"] == "fasting":
            status = "fasting"
        elif plan["meal_relation"] == "with_meal":
            status = "with_meal"
        elif moved:
            status = "rescheduled"
        else:
            status = "standard"

        return {
            "time": _hhmm(minute),
            "minutes": minute,
            "drug": plan["name"],
            "key": plan["key"],
            "dose": plan["dose"],
            "instruction": instruction,
            "status": status,
            "moved": moved,
            "critical_conflict": bool(critical),
            "label": _slot_label(minute),
        }

    def _prn_entry(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "drug": plan["name"],
            "key": plan["key"],
            "dose": plan["dose"],
            "instruction": plan.get("note") or "Take only when needed, following the prescription label.",
        }

    def _weekly_entry(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "drug": plan["name"],
            "key": plan["key"],
            "dose": plan["dose"],
            "time": _hhmm(self._preferred_time(plan)),
            "instruction": plan.get("note") or "Take once weekly on the day chosen with your prescriber.",
            "warning": "WEEKLY dosing — never take daily.",
        }

    def _critical_partners(
        self, key: str, interactions: List[Dict[str, Any]]
    ) -> List[str]:
        partners = []
        for item in interactions:
            if item.get("severity") != "CRITICAL":
                continue
            pair = item.get("pair_keys", ())
            if key in pair:
                other = pair[0] if key == pair[1] else pair[1]
                name = item.get("drug_b") if other == pair[1] else item.get("drug_a")
                name = name or other
                if name not in partners:
                    partners.append(name)
        return partners

    def _unresolved(
        self,
        constraints: List[Dict[str, Any]],
        assignment: Dict[str, List[int]],
    ) -> List[Dict[str, Any]]:
        unresolved = []
        for constraint in constraints:
            first = assignment.get(constraint["a"])
            second = assignment.get(constraint["b"])
            if not first or not second:
                continue
            actual = min(abs(a - b) for a in first for b in second) / 60
            if actual + 0.01 < constraint["hours"]:
                unresolved.append({
                    "drug_a": constraint["a"],
                    "drug_b": constraint["b"],
                    "title": constraint["title"],
                    "required_hours": constraint["hours"],
                    "actual_hours": round(actual, 1),
                })
        return unresolved

    def _critical_conflicts(
        self,
        constraints: List[Dict[str, Any]],
        assignment: Dict[str, List[int]],
    ) -> List[Dict[str, Any]]:
        """Report critical pairs that could not be separated in the final plan."""
        conflicts = []
        for constraint in constraints:
            first = assignment.get(constraint["a"])
            second = assignment.get(constraint["b"])
            if not first or not second:
                continue
            actual = min(abs(a - b) for a in first for b in second) / 60
            if actual + 0.01 < constraint["hours"]:
                conflicts.append({
                    "drug_a": constraint["a"],
                    "drug_b": constraint["b"],
                    "title": constraint["title"],
                    "required_hours": constraint["hours"],
                    "actual_hours": round(actual, 1),
                    "severity": "CRITICAL",
                })
        return conflicts

    def _adjustments(
        self,
        plans: List[Dict[str, Any]],
        assignment: Dict[str, List[int]],
        constraints: List[Dict[str, Any]],
    ) -> List[str]:
        messages: List[str] = []
        by_key = {plan["key"]: plan for plan in plans}

        for constraint in constraints:
            first = assignment.get(constraint["a"])
            second = assignment.get(constraint["b"])
            if not first or not second:
                continue
            actual = min(abs(a - b) for a in first for b in second) / 60
            if actual + 0.01 >= constraint["hours"]:
                if constraint.get("kind") == "critical":
                    messages.append(
                        f"Kept {by_key[constraint['a']]['name']} and "
                        f"{by_key[constraint['b']]['name']} {actual:g}h apart for "
                        f"administration safety; the contraindication still requires "
                        f"clinician review."
                    )
                else:
                    messages.append(
                        f"Kept {by_key[constraint['a']]['name']} and "
                        f"{by_key[constraint['b']]['name']} {actual:g}h apart "
                        f"(minimum {constraint['hours']:g}h)."
                    )

        for plan in plans:
            times = assignment.get(plan["key"], [])
            if not times:
                continue
            if plan["meal_relation"] == "fasting":
                messages.append(f"Scheduled {plan['name']} in the early-morning fasting window.")
            elif plan["meal_relation"] == "with_meal":
                messages.append(f"Aligned {plan['name']} with meals.")
            elif plan["preferred_period"] == "bedtime":
                messages.append(f"Scheduled {plan['name']} at bedtime.")

        # Deduplicate while preserving order.
        seen = set()
        unique = []
        for message in messages:
            if message not in seen:
                seen.add(message)
                unique.append(message)
        return unique
