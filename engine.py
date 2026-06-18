# engine.py
# Scoring and coaching — SparklingBlu Fleet Performance System
# Phase 2: Hotspot-aligned targets with fuel efficiency metrics
# Targets: 40-50h/week | 50-75 trips/week (hotspot-dependent) | R28.06/L fuel

from datetime import datetime
from hotspots import (
    HOTSPOT_WEEKLY_TARGETS, COST_PER_KM, FUEL_PRICE_PER_LITRE,
    PEAK_BLOCKS, get_current_peak_block
)

# Default weekly targets (used when hotspot not assigned)
DEFAULT_WEEKLY_TARGETS = {
    "weekly_hours_min": 50.0,
    "weekly_hours_max": 50.0,
    "weekly_trips_min": 50,
    "weekly_trips_max": 50,
    "daily_hours":       10.0,
    "daily_trips":       10,
}

SHIFT_START = 5       # 5:00 AM
SHIFT_END   = 19.5    # 7:30 PM
SHIFT_HOURS = SHIFT_END - SHIFT_START  # 14.5h per day


def get_week_progress():
    now        = datetime.now()
    day_number = now.weekday()      # Mon=0, Sun=6
    day_name   = now.strftime("%A")
    hour       = now.hour + now.minute / 60

    if hour < SHIFT_START:
        day_fraction = 0.0
    elif hour > SHIFT_END:
        day_fraction = 1.0
    else:
        day_fraction = (hour - SHIFT_START) / SHIFT_HOURS

    days_elapsed = day_number + day_fraction
    progress     = days_elapsed / 7.0
    days_left    = 6 - day_number

    peak_block, peak_strategy = get_current_peak_block()

    return {
        "day_number":   day_number,
        "day_name":     day_name,
        "progress":     round(progress, 4),
        "days_elapsed": round(days_elapsed, 2),
        "days_left":    days_left,
        "current_hour": round(hour, 2),
        "in_shift":     SHIFT_START <= hour <= SHIFT_END,
        "peak_block":   peak_block,
        "peak_strategy": peak_strategy,
        "fuel_price":   FUEL_PRICE_PER_LITRE,
        "cost_per_km":  round(COST_PER_KM, 2),
    }


def get_hotspot_targets(hotspot_name=None):
    """Get weekly targets for a specific hotspot or defaults"""
    if hotspot_name and hotspot_name in HOTSPOT_WEEKLY_TARGETS:
        targets = HOTSPOT_WEEKLY_TARGETS[hotspot_name].copy()
        targets["daily_hours"] = targets["weekly_hours_min"] / 7
        targets["daily_trips"] = targets["weekly_trips_min"] / 7
        return targets
    return DEFAULT_WEEKLY_TARGETS.copy()


def calculate_performance_score(hours_online, trips_taken, report_days=1, hotspot_name=None):
    """
    Scores a driver 0-100 based on hotspot-aligned targets.

    Phase 2 scoring weights:
      Hours vs hotspot target   40%
      Trips vs hotspot target   40%
      Fuel efficiency           20% (future: actual km/trip data)

    A driver at Midrand Hub (target: 60-75 trips/week) by Thursday (day 4) needs:
      ≥ 34h online
      ≥ 34 trips
    to score in the Top Performer band (≥85).

    Returns a tuple: (score, status_label)
    """
    targets = get_hotspot_targets(hotspot_name)
    days = max(int(report_days), 1)

    expected_hours = targets["daily_hours"] * days
    expected_trips = targets["daily_trips"] * days

    # 1. Hours score (40%)
    hrs_ratio = hours_online / expected_hours if expected_hours > 0 else 0
    hrs_score = min(hrs_ratio, 1.0) * 100 * 0.40

    # 2. Trips score (40%)
    trp_ratio = trips_taken / expected_trips if expected_trips > 0 else 0
    trp_score = min(trp_ratio, 1.0) * 100 * 0.40

    # 3. Fuel efficiency placeholder (20%) — will use actual km data in future
    fuel_score = 100 * 0.20  # Default perfect score until km data available

    score = round(hrs_score + trp_score + fuel_score, 1)

    if score >= 85:
        status = "Top Performer"
    elif score >= 70:
        status = "Good"
    elif score >= 50:
        status = "Needs Improvement"
    else:
        status = "Urgent Attention"

    return score, status


def get_remaining_targets(hours_online, trips_taken, progress, report_days=1, hotspot_name=None):
    targets = get_hotspot_targets(hotspot_name)
    days = max(int(report_days), 1)

    rem = {}

    # Weekly remaining
    rem["hours_needed"] = round(max(targets["weekly_hours_min"] - hours_online, 0), 1)
    rem["trips_needed"] = max(targets["weekly_trips_min"] - int(trips_taken), 0)
    rem["hours_on_track"] = hours_online >= (targets["weekly_hours_min"] * max(progress, 0.01))
    rem["trips_on_track"] = trips_taken >= (targets["weekly_trips_min"] * max(progress, 0.01))

    # Current totals
    rem["hours_weekly"] = round(hours_online, 1)
    rem["trips_weekly"] = int(trips_taken)
    rem["daily_hours_ok"] = (hours_online / days) >= targets["daily_hours"] if days > 0 else False
    rem["daily_trips_ok"] = (trips_taken / days) >= targets["daily_trips"] if days > 0 else False

    # Fuel cost estimate (based on avg 5km per trip)
    estimated_km = trips_taken * 5
    rem["estimated_fuel_cost"] = round(estimated_km * COST_PER_KM, 2)
    rem["fuel_price_per_litre"] = FUEL_PRICE_PER_LITRE
    rem["cost_per_km"] = round(COST_PER_KM, 2)

    return rem


def kpi_fully_met(hours_online, trips_taken, report_days=1, hotspot_name=None):
    """
    KPI is met when weekly hotspot targets are hit.
    """
    targets = get_hotspot_targets(hotspot_name)
    return (
        hours_online >= targets["weekly_hours_min"] and
        trips_taken >= targets["weekly_trips_min"]
    )


def get_coaching_message(score, remaining, week_info, hotspot_name=None):
    """
    Builds a day-aware coaching message.

    Tone escalates across the week:
      Mon/Tue   -> informational, no pressure
      Wed/Thu   -> pace check, gentle nudge
      Fri/Sat   -> urgent, direct numbers, hotspot relocation suggestion
      Sun       -> week-end recap

    If the driver is behind pace on Fri/Sat, this also recommends the
    nearest hotspot with a higher trip target (via hotspots.py), so the
    message tells them not just "how much" but "go where" to close the gap.
    """
    from hotspots import get_busier_nearby_hotspot

    day_name   = week_info["day_name"]
    days_left  = week_info["days_left"]
    day_number = week_info.get("day_number", 0)  # Mon=0 ... Sun=6

    behind_pace = (not remaining["daily_hours_ok"]) or (not remaining["daily_trips_ok"])

    # ── Build the core numbers line (always shown) ────────────────────
    facts = []
    if remaining["hours_needed"] > 0:
        facts.append(f"{remaining['hours_needed']}h still needed this week")
    if remaining["trips_needed"] > 0:
        facts.append(f"{remaining['trips_needed']} more trips needed this week")
    if not facts:
        facts.append("Weekly hours and trips targets already met")

    facts.append(f"Current: {remaining['hours_weekly']}h online, {remaining['trips_weekly']} trips")
    facts.append(f"Est. fuel cost: R{remaining['estimated_fuel_cost']} (@ R{remaining['fuel_price_per_litre']}/L)")

    if week_info.get("peak_block") != "Off-Peak":
        facts.append(f"Peak: {week_info.get('peak_block')} — {week_info.get('peak_strategy')}")

    # ── Hotspot relocation suggestion — only when behind pace AND
    #    it's late in the week (Thu=3 onward), so we don't nag on Monday ──
    relocation_note = ""
    if behind_pace and day_number >= 3 and hotspot_name:
        better_spot = get_busier_nearby_hotspot(hotspot_name)
        if better_spot:
            relocation_note = (
                f" Consider shifting toward {better_spot} — it has a higher "
                f"trip volume nearby and could help you close the gap faster."
            )

    issue_text = "  |  ".join(facts) + relocation_note

    # ── Day-based tone escalation ──────────────────────────────────────
    # Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    if day_number <= 1:
        # Monday / Tuesday — informational, no pressure
        tone_prefix = f"Week is just getting started ({day_name}) — here's where you stand."
    elif day_number <= 3:
        # Wednesday / Thursday — pace check
        tone_prefix = f"Midweek check ({day_name}) — {days_left} day(s) left to stay on pace."
    elif day_number <= 5:
        # Friday / Saturday — urgent, direct
        tone_prefix = f"⚠️ {day_name} — only {days_left} day(s) left. Time to close the gap NOW."
    else:
        # Sunday — recap
        tone_prefix = f"Week wrap-up ({day_name}) — here's how the week finished."

    if score >= 85:
        message = f"🌟 Excellent work! {tone_prefix} You're on track for all weekly targets. {issue_text}"
    elif score >= 70:
        message = f"✅ {tone_prefix} Good progress overall. {issue_text}"
    elif score >= 50:
        message = f"⚠️ {tone_prefix} Falling behind pace. {issue_text}"
    else:
        message = f"🚨 {tone_prefix} Critical — urgent action needed. {issue_text}"

    return message