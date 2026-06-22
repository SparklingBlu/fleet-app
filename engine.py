# engine.py
# Scoring and coaching — SparklingBlu Fleet Performance System
# Targets: 50 Hours Online / 35 Trips per week (universal, no hotspot dependency)

from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# UNIVERSAL WEEKLY TARGETS
# ─────────────────────────────────────────────────────────────────────────────
WEEKLY_HOURS_TARGET = 50.0
WEEKLY_TRIPS_TARGET = 35

DAILY_HOURS_TARGET = WEEKLY_HOURS_TARGET / 7   # ≈ 7.14h
DAILY_TRIPS_TARGET = WEEKLY_TRIPS_TARGET / 7   # = 5.0

SHIFT_START = 5       # 05:00
SHIFT_END   = 19.5    # 19:30
SHIFT_HOURS = SHIFT_END - SHIFT_START  # 14.5h


# ─────────────────────────────────────────────────────────────────────────────
# get_week_progress
# ─────────────────────────────────────────────────────────────────────────────
def get_week_progress():
    """
    Returns a dict describing where we are in the current week.
    Used by the admin view header banner and coaching messages.
    """
    now        = datetime.now()
    day_number = now.weekday()          # Mon=0 … Sun=6
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

    return {
        "day_number":   day_number,
        "day_name":     day_name,
        "progress":     round(progress, 4),
        "days_elapsed": round(days_elapsed, 2),
        "days_left":    days_left,
        "current_hour": round(hour, 2),
        "in_shift":     SHIFT_START <= hour <= SHIFT_END,
    }


# ─────────────────────────────────────────────────────────────────────────────
# calculate_performance_score
# CHANGE 2 — fixed universal targets, equal hours/trips weighting, no hotspot
# ─────────────────────────────────────────────────────────────────────────────
def calculate_performance_score(hours_online, trips_taken, report_days=1, hotspot_name=None):
    """
    Scores a driver 0–100 against universal SparklingBlu targets.

    Scoring weights (equal):
      Hours Online vs pace target   50%
      Total Trips  vs pace target   50%

    Pace target for report_days d:
      expected_hours = (50 / 7) * d
      expected_trips = (35 / 7) * d

    Example — by Thursday (day 4):
      expected_hours ≈ 28.6h   expected_trips ≈ 20
      A driver with 40h+ and 20+ trips scores ≥ 85 (Top Performer).

    Status bands:
      85+    → Top Performer
      70–84  → Good
      50–69  → Needs Improvement
      < 50   → Urgent Attention

    hotspot_name is accepted for API compatibility but ignored.
    """
    days = max(int(report_days), 1)

    expected_hours = DAILY_HOURS_TARGET * days
    expected_trips = DAILY_TRIPS_TARGET * days

    # 50% hours score
    hrs_ratio = hours_online / expected_hours if expected_hours > 0 else 0
    hrs_score = min(hrs_ratio, 1.0) * 100 * 0.50

    # 50% trips score
    trp_ratio = trips_taken / expected_trips if expected_trips > 0 else 0
    trp_score = min(trp_ratio, 1.0) * 100 * 0.50

    score = round(hrs_score + trp_score, 1)

    if score >= 85:
        status = "Top Performer"
    elif score >= 70:
        status = "Good"
    elif score >= 50:
        status = "Needs Improvement"
    else:
        status = "Urgent Attention"

    return score, status


# ─────────────────────────────────────────────────────────────────────────────
# kpi_fully_met
# CHANGE 3 — simple binary: 50h AND 35 trips
# ─────────────────────────────────────────────────────────────────────────────
def kpi_fully_met(hours_online, trips_taken, report_days=1, hotspot_name=None):
    """
    KPI compliant when:
      Hours Online >= 50  AND  Total Trips >= 35
    report_days and hotspot_name accepted for API compatibility but ignored.
    """
    return (
        hours_online >= WEEKLY_HOURS_TARGET and
        trips_taken  >= WEEKLY_TRIPS_TARGET
    )


# ─────────────────────────────────────────────────────────────────────────────
# get_remaining_targets
# CHANGE 4 — pace-based on-track flags, no hotspot
# ─────────────────────────────────────────────────────────────────────────────
def get_remaining_targets(hours_online, trips_taken, progress, report_days=1, hotspot_name=None):
    """
    Returns remaining work and on-track flags relative to weekly pace.

    on-track logic:
      expected_pace_hours = 50 * progress
      expected_pace_trips = 35 * progress
      hours_on_track = hours_online >= expected_pace_hours
      trips_on_track = trips_taken  >= expected_pace_trips

    Example (Thursday, progress ≈ 0.571):
      expected_pace_hours = 28.6h  expected_pace_trips = 20
      driver with 35h / 25 trips → both on_track = True
      driver with 20h / 12 trips → both on_track = False
    """
    # Weekly remaining
    hours_needed = round(max(WEEKLY_HOURS_TARGET - hours_online, 0), 1)
    trips_needed = max(WEEKLY_TRIPS_TARGET - int(trips_taken), 0)

    # Pace on-track
    safe_progress        = max(progress, 0.01)
    pace_hours_expected  = round(WEEKLY_HOURS_TARGET * safe_progress, 1)
    pace_trips_expected  = round(WEEKLY_TRIPS_TARGET * safe_progress, 1)
    hours_on_track       = hours_online >= pace_hours_expected
    trips_on_track       = trips_taken  >= pace_trips_expected

    return {
        "hours_needed":        hours_needed,
        "trips_needed":        trips_needed,
        "hours_on_track":      hours_on_track,
        "trips_on_track":      trips_on_track,
        "hours_weekly":        round(hours_online, 1),
        "trips_weekly":        int(trips_taken),
        "pace_hours_expected": pace_hours_expected,
        "pace_trips_expected": int(pace_trips_expected),
    }


# ─────────────────────────────────────────────────────────────────────────────
# get_coaching_message
# CHANGE 5 — clear current/remaining numbers, escalating tone, no hotspot
# ─────────────────────────────────────────────────────────────────────────────
def get_coaching_message(score, remaining, week_info, hotspot_name=None):
    """
    Builds a day-aware coaching message showing current totals and remaining
    targets. Tone escalates across the week:

      Mon/Tue  (day 0–1) → friendly pace reminder
      Wed/Thu  (day 2–3) → midweek pace check, gentle nudge
      Fri/Sat  (day 4–5) → strong urgency, direct numbers
      Sun      (day 6)   → final week summary

    hotspot_name accepted for API compatibility but ignored.
    """
    day_name   = week_info.get("day_name", "Today")
    days_left  = week_info.get("days_left", 0)
    day_number = week_info.get("day_number", 0)   # Mon=0 … Sun=6

    hrs     = remaining["hours_weekly"]
    trips   = remaining["trips_weekly"]
    hrs_rem = remaining["hours_needed"]
    trp_rem = remaining["trips_needed"]
    h_ok    = remaining["hours_on_track"]
    t_ok    = remaining["trips_on_track"]

    # ── Core facts line (always shown) ──────────────────────────────────
    current_line = f"Current: {hrs}h online, {trips} trips."

    if hrs_rem == 0 and trp_rem == 0:
        target_line = "Weekly targets fully met — great work!"
    elif hrs_rem == 0:
        target_line = f"Hours target met. Still need {trp_rem} more trips this week."
    elif trp_rem == 0:
        target_line = f"Trips target met. Still need {hrs_rem}h more online this week."
    else:
        target_line = f"You need {hrs_rem}h and {trp_rem} more trips to reach target."

    # ── Pace indicator ───────────────────────────────────────────────────
    if h_ok and t_ok:
        pace_line = "✅ Ahead of weekly pace on both hours and trips."
    elif h_ok and not t_ok:
        pace_line = f"⚠️ Hours pace on track, but trips are behind ({trips} vs {remaining['pace_trips_expected']} expected by now)."
    elif not h_ok and t_ok:
        pace_line = f"⚠️ Trips pace on track, but hours are behind ({hrs}h vs {remaining['pace_hours_expected']}h expected by now)."
    else:
        pace_line = (
            f"🔴 Behind pace on both. Expected by now: "
            f"{remaining['pace_hours_expected']}h and {remaining['pace_trips_expected']} trips."
        )

    body = f"{current_line} {target_line} {pace_line}"

    # ── Day-based tone prefix ────────────────────────────────────────────
    if day_number <= 1:
        # Mon / Tue — no pressure
        if score >= 85:
            prefix = f"🌟 Excellent start to the week ({day_name})!"
        elif score >= 70:
            prefix = f"✅ Good start ({day_name}). Keep this pace up."
        elif score >= 50:
            prefix = f"📋 Early in the week ({day_name}) — time to build momentum."
        else:
            prefix = f"📋 Week just started ({day_name}). Focus on getting online and completing trips."

    elif day_number <= 3:
        # Wed / Thu — midweek check
        if score >= 85:
            prefix = f"🌟 Strong midweek performance ({day_name}, {days_left} day(s) left)!"
        elif score >= 70:
            prefix = f"✅ On track midweek ({day_name}). {days_left} day(s) to finish strong."
        elif score >= 50:
            prefix = f"⚠️ Midweek check ({day_name}) — you need to pick up the pace. {days_left} day(s) left."
        else:
            prefix = f"🚨 Midweek alert ({day_name}) — falling significantly behind. {days_left} day(s) left."

    elif day_number <= 5:
        # Fri / Sat — urgent
        if score >= 85:
            prefix = f"🌟 Outstanding! ({day_name}) — only {days_left} day(s) left and you're well ahead."
        elif score >= 70:
            prefix = f"⚠️ {day_name} — {days_left} day(s) left. Close the gap now."
        elif score >= 50:
            prefix = f"🚨 {day_name} — {days_left} day(s) left. Urgent action needed to reach target."
        else:
            prefix = f"🚨 CRITICAL — {day_name}, {days_left} day(s) left. Maximum effort required NOW."

    else:
        # Sun — recap
        if score >= 85:
            prefix = "🏆 Week complete — Top Performer. Excellent work this week!"
        elif score >= 70:
            prefix = "✅ Week complete — Good performance overall."
        elif score >= 50:
            prefix = "📋 Week complete — target was partially met. Plan for a stronger start next Monday."
        else:
            prefix = "🚨 Week complete — targets not met. Let's discuss a plan for next week."

    return f"{prefix}  {body}"