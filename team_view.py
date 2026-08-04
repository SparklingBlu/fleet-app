# team_view.py — shared team-view renderer, used by app.py and team_1.py..team_4.py
import streamlit as st
import pandas as pd
from engine import get_week_progress, WEEKLY_HOURS_TARGET, WEEKLY_TRIPS_TARGET
from teams import TEAMS
from storage import load_fleet_data


def render_team_view(forced_team=None):
    """Renders the team performance view.
    forced_team: skips the dropdown and always shows that team
    (used by the standalone team_1.py..team_4.py apps).
    If None, falls back to a selectbox (used by app.py's ?view=team&team=...).
    """
    data = load_fleet_data()
    if not data:
        st.warning("No data available. Ask the fleet manager to publish this week's stats.")
        st.stop()

    df = pd.DataFrame(data["fleet"])
    wi = data.get("week_info", get_week_progress())
    updated = data.get("updated_at", "")

    available_teams = df["Team"].unique().tolist() if "Team" in df.columns else list(TEAMS.keys())

    if forced_team:
        selected_team = forced_team
    else:
        selected_team = st.selectbox("Select your team:", available_teams)

    if not selected_team:
        st.warning("No teams found in the current data.")
        st.stop()

    leader = TEAMS.get(selected_team, {}).get("leader", "—")
    roster = TEAMS.get(selected_team, {}).get("drivers", [])
    roster_total = len(roster)

    reported_df = df[df["Team"] == selected_team].copy()

    start_str = data.get("start_date", "")
    end_str = data.get("end_date", "")
    week_lbl = data.get("week_label", "")

    if start_str and end_str:
        period_str = f"{start_str} → {end_str}"
    else:
        period_str = f"{wi.get('day_name', '—')} | {wi.get('days_left', '—')} day(s) left"

    st.markdown(f"# 👥 {selected_team} — Weekly Performance")

    meta_parts = [f"Leader: {leader}", f"Period: {period_str}", f"Updated: {updated}"]
    if week_lbl:
        meta_parts.insert(0, f"**{week_lbl}**")
    st.markdown("*" + "  |  ".join(meta_parts) + "*")

    st.caption(f"📊 Weekly targets: {int(WEEKLY_HOURS_TARGET)}h online / {WEEKLY_TRIPS_TARGET} trips")
    st.divider()

    # Build a full-roster table: every driver on the roster, whether reported or not
    roster_df = pd.DataFrame({"Driver": roster})
    roster_df["_key"] = roster_df["Driver"].str.strip().str.upper()
    reported_df["_key"] = reported_df["Driver"].str.strip().str.upper()
    full_df = roster_df.merge(
        reported_df.drop(columns=["Driver"]), on="_key", how="left"
    ).drop(columns=["_key"])

    for col, default in [
        ("Hours Online", 0), ("Total Trips", 0), ("Score", 0),
        ("Status", "Not reported"), ("Remaining Hours", "—"),
        ("Remaining Trips", "—"), ("Coaching", ""), ("Hours on Trip", 0),
    ]:
        if col not in full_df.columns:
            full_df[col] = default
        full_df[col] = full_df[col].fillna(default)

    # On-target count: meets BOTH weekly targets
    on_target = (
        (full_df["Hours Online"].astype(float) >= WEEKLY_HOURS_TARGET) &
        (full_df["Total Trips"].astype(float) >= WEEKLY_TRIPS_TARGET)
    ).sum()

    t_avg_hrs = round(full_df["Hours Online"].astype(float).mean(), 1)
    t_avg_trp = round(full_df["Total Trips"].astype(float).mean(), 1)

    top_hours_driver, top_hours_val = "—", "—"
    if not reported_df.empty and "Hours Online" in reported_df.columns:
        idx = reported_df["Hours Online"].astype(float).idxmax()
        top_hours_driver = reported_df.loc[idx, "Driver"]
        top_hours_val = reported_df.loc[idx, "Hours Online"]

    top_trips_driver, top_trips_val = "—", "—"
    if not reported_df.empty and "Total Trips" in reported_df.columns:
        idx = reported_df["Total Trips"].astype(float).idxmax()
        top_trips_driver = reported_df.loc[idx, "Driver"]
        top_trips_val = reported_df.loc[idx, "Total Trips"]

    m1, m2, m3 = st.columns(3)
    m1.metric("On Target", f"{on_target}/{roster_total}")
    m2.metric("Avg Hours Online", f"{t_avg_hrs}h")
    m3.metric("Avg Trips", t_avg_trp)

    st.markdown("### 🏆 Top Performers This Week")
    p1, p2 = st.columns(2)
    p1.metric("⏱️ Top Hours", top_hours_driver, f"{top_hours_val}h" if top_hours_val != "—" else None)
    p2.metric("📦 Top Trips", top_trips_driver, f"{top_trips_val} trips" if top_trips_val != "—" else None)

    st.divider()

    show_cols = [
        "Driver", "Hours Online", "Hours on Trip",
        "Total Trips", "Score", "Status",
        "Remaining Hours", "Remaining Trips", "Coaching",
    ]
    show_cols = [c for c in show_cols if c in full_df.columns]
    st.dataframe(
        full_df[show_cols].sort_values("Score", ascending=False).reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"SparklingBlu Fleet  |  Updated: {updated}")
