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
    "weekly_hours":    50.0,
    "weekly_trips":    50,
    "daily_hours":     10.0,
    "daily_trips":     10,
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

    return round(hrs_score + trp_score + fuel_score, 1)


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


def get_coaching_message(score, remaining, week_info):
    day_name = week_info["day_name"]
    days_left = week_info["days_left"]

    issues = []
    if not remaining["daily_hours_ok"]:
        issues.append(f"{remaining['hours_weekly']}h online — below target pace")
    if not remaining["daily_trips_ok"]:
        issues.append(f"{remaining['trips_weekly']} trips — below target pace")
    if remaining["hours_needed"] > 0:
        issues.append(f"{remaining['hours_needed']}h still needed this week")
    if remaining["trips_needed"] > 0:
        issues.append(f"{remaining['trips_needed']} more trips needed this week")

    # Fuel insight
    issues.append(f"Est. fuel cost: R{remaining['estimated_fuel_cost']} (@ R{remaining['fuel_price_per_litre']}/L)")

    # Peak block guidance
    if week_info.get("peak_block") != "Off-Peak":
        issues.append(f"Peak: {week_info.get('peak_block')} — {week_info.get('peak_strategy')}")

    issue_text = "  |  ".join(issues) if issues else "All targets on track"

    if score >= 85:
        return ("Top Performer",
                f"Excellent work this {day_name}! You are on track for all weekly targets. {issue_text}")
    elif score >= 70:
        return ("Good",
                f"Good progress — {days_left} day(s) left to finish strong. {issue_text}")
    elif score >= 50:
        return ("Needs Improvement",
                f"Falling behind pace. Only {days_left} day(s) left. {issue_text}")
    else:
        return ("Urgent Attention",
                f"Critical — urgent action needed before Sunday. {days_left} day(s) left. {issue_text}")