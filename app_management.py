import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from storage import load_fleet_data

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SparklingBlu — Fleet Management",
    page_icon="📊",
    layout="wide",
)

# ─────────────────────────────────────────────
# THEME / CSS
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Base */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', Roboto, sans-serif;
        }

        /* Metric cards */
        div[data-testid="metric-container"] {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }

        /* Insight cards */
        .insight-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }
        .insight-card h4 {
            margin: 0 0 6px 0;
            color: #1a1a2e;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .insight-card p {
            margin: 0;
            font-size: 22px;
            font-weight: 700;
            color: #0066cc;
        }
        .insight-card small {
            color: #666;
            font-size: 12px;
        }

        /* Status badges */
        .badge-green  { background:#d4edda; color:#155724; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:600; }
        .badge-yellow { background:#fff3cd; color:#856404; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:600; }
        .badge-orange { background:#ffe5b4; color:#7d4e00; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:600; }
        .badge-red    { background:#f8d7da; color:#721c24; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:600; }

        /* Section headers */
        .section-header {
            font-size: 18px;
            font-weight: 700;
            color: #1a1a2e;
            margin: 24px 0 12px 0;
            border-left: 4px solid #0066cc;
            padding-left: 10px;
        }

        /* Chat box */
        .sparky-answer {
            background: #f0f7ff;
            border: 1px solid #b3d4f5;
            border-radius: 10px;
            padding: 14px 18px;
            color: #0a3d62;
            font-size: 15px;
            margin-top: 10px;
        }

        /* Download button */
        div[data-testid="stDownloadButton"] button {
            background-color: #0066cc;
            color: white;
            border-radius: 8px;
            border: none;
        }
        div[data-testid="stDownloadButton"] button:hover {
            background-color: #0052a3;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
SBV_DRIVERS = [
    "Stephen Mohali", "Sanele Nkosi", "Ramsey Mdumuka", "Robert Nzuy Ngamuna",
    "Raphael Banda", "Nelson Zangirai", "Anthonio Haston Bikausi", "Sabelo Vumasi",
    "Tebogo Sathekge", "Loshani Sakisoni", "Winson Chimfwembe Mwasinga", "Percy Mabuza",
    "Bright Jere", "Jacob Murondi", "Jolter Sizwe Ndlovu", "Lebohang Molefe",
    "Gilbert Babou Marifa", "Brian Losen Mkandla", "Davie Staliko", "Asanda Nyembe",
    "Samuel German", "John Msosa", "Alnord Nyirenda", "Nhlokomo Selby Thomo",
    "Desmond Farai Murondi", "Esrom Maswekana", "Lehlohonolo Lucky Moloi", "Joshua Mtisi",
    "Blessings Maseko Sinosi", "Takwana Jonga", "Jefule Mustafa", "Katleho Mahane Mahamo",
    "Vincent Tonex", "Vuyisa Mdebuka", "Lester Banda", "Innocent Grant Chapotera",
    "Stiven Banda", "Louis Suntche", "Mgcini Moyo", "Lucas Inkosinathi Dhlamini",
    "Sam Haba", "Anele Sithole", "Kimia Gedeon Beloko", "Siphesihle Mdebuka",
    "Richard Ibrahim", "Khulerani Tshabalala", "Willard Bakali", "Ishmael Mussah",
    "Faidon Safali", "Idelito Valexy", "Alfred Sanny Tshabalala", "Bafana Nicholas Mahlangu",
    "Brian Chiremba", "Blessings Zuze", "Richard Laston", "Amazing Calvin Servazio",
    "Francis Phwitiko", "Vusi Rodgers Mtwiche", "Akimu Soko", "Vumbhoni Owen Mathye",
    "Junior Ishumeal", "Alli Mabvuto",
]

EXPECTED_HOURS_PER_DAY = 10
EXPECTED_TRIPS_PER_DAY = 10

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def match_sbv_driver(name: str) -> bool:
    """Return True if name partially matches any SBV driver (case-insensitive)."""
    if not isinstance(name, str):
        return False
    name_lower = name.lower().strip()
    name_parts = name_lower.split()
    for sbv in SBV_DRIVERS:
        sbv_lower = sbv.lower()
        sbv_parts = sbv_lower.split()
        # Check if at least first + last name part of SBV name appear in driver name
        if len(sbv_parts) >= 2:
            first = sbv_parts[0]
            last = sbv_parts[-1]
            if first in name_lower and last in name_lower:
                return True
        # Or if the full SBV name is contained in the driver name
        if sbv_lower in name_lower or name_lower in sbv_lower:
            return True
        # Or if all name parts of SBV appear in the driver name
        if all(part in name_lower for part in sbv_parts if len(part) > 2):
            return True
    return False


def get_day_aware_coaching(row) -> tuple:
    """
    Returns (status_str, coaching_message) based on current weekday progress.

    Monday=0 … Sunday=6.
    days_elapsed = weekday + 1  (Monday → 1, Tuesday → 2, …)
    Expected hours = days_elapsed * 10
    Expected trips = days_elapsed * 10
    """
    today = datetime.now()
    weekday = today.weekday()  # Monday=0
    days_elapsed = weekday + 1  # 1–7

    expected_hours = days_elapsed * EXPECTED_HOURS_PER_DAY
    expected_trips = days_elapsed * EXPECTED_TRIPS_PER_DAY

    try:
        actual_hours = float(row.get("Hours Online", 0) or 0)
    except (ValueError, TypeError):
        actual_hours = 0

    try:
        actual_trips = int(row.get("Total Trips", 0) or 0)
    except (ValueError, TypeError):
        actual_trips = 0

    hours_gap = expected_hours - actual_hours
    trips_gap = expected_trips - actual_trips

    # Status based on hours gap
    if hours_gap <= 0:
        status = "On Track"
        msg = (
            f"✅ On track! {actual_hours:.1f}h / {expected_hours}h target. "
            f"{actual_trips} trips vs {expected_trips} expected."
        )
    elif hours_gap <= 5:
        status = "Slightly Behind"
        msg = (
            f"🟡 Slightly behind. {actual_hours:.1f}h vs {expected_hours}h target. "
            f"Close the {hours_gap:.1f}h gap today."
        )
    elif hours_gap <= 15:
        status = "Behind"
        msg = (
            f"🟠 Behind target by {hours_gap:.1f}h. {actual_hours:.1f}h vs {expected_hours}h. "
            f"Push for more hours to catch up."
        )
    else:
        status = "Significantly Behind"
        msg = (
            f"🔴 Significantly behind — {hours_gap:.1f}h gap. {actual_hours:.1f}h vs {expected_hours}h. "
            f"Immediate action needed."
        )

    return status, msg


def get_sparky_response(question: str, df: pd.DataFrame) -> str:
    """Simple rule-based fleet chatbot."""
    q = question.lower().strip()

    if not isinstance(df, pd.DataFrame) or df.empty:
        return "No fleet data available right now. Try refreshing."

    today = datetime.now()
    weekday = today.weekday()
    days_elapsed = weekday + 1
    expected_hours = days_elapsed * EXPECTED_HOURS_PER_DAY

    # Ensure numeric columns
    hours_col = "Hours Online"
    trips_col = "Total Trips"
    score_col = "Score"
    driver_col = "Driver"
    team_col = "Team"

    for col in [hours_col, trips_col, score_col]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "top driver" in q:
        if hours_col in df.columns and driver_col in df.columns:
            top = df.loc[df[hours_col].idxmax()]
            return (
                f"🏆 Top driver by hours: **{top[driver_col]}** "
                f"with {top.get(hours_col, 0):.1f}h online, "
                f"{int(top.get(trips_col, 0))} trips, "
                f"score {top.get(score_col, 0):.1f}."
            )
        return "Driver data not available."

    elif "behind target" in q or "behind" in q:
        if hours_col in df.columns:
            behind = df[df[hours_col] < expected_hours]
            return (
                f"⚠️ {len(behind)} of {len(df)} drivers are below the expected "
                f"{expected_hours}h target for today ({today.strftime('%A')})."
            )
        return "Hours data not available."

    elif "most trips" in q:
        if team_col in df.columns and trips_col in df.columns:
            hotspot = df.groupby(team_col)[trips_col].sum().idxmax()
            total = int(df.groupby(team_col)[trips_col].sum().max())
            return f"🗺️ Hotspot with most trips: **{hotspot}** — {total} total trips."
        return "Hotspot/trip data not available."

    elif "average score" in q or "avg score" in q:
        if score_col in df.columns:
            avg = df[score_col].mean()
            return f"📊 Fleet average score: **{avg:.2f}**."
        return "Score data not available."

    elif "sbv" in q:
        matched = df[df[driver_col].apply(match_sbv_driver)] if driver_col in df.columns else pd.DataFrame()
        names = matched[driver_col].tolist() if not matched.empty else []
        if names:
            return (
                f"🚛 {len(names)} SBV drivers found in current data:\n" +
                "\n".join(f"• {n}" for n in names)
            )
        return "No SBV drivers matched in current data."

    elif "lowest hours" in q:
        if hours_col in df.columns and driver_col in df.columns:
            bottom3 = df.nsmallest(3, hours_col)[[driver_col, hours_col]]
            lines = [f"• {r[driver_col]}: {r[hours_col]:.1f}h" for _, r in bottom3.iterrows()]
            return "⏱️ Bottom 3 drivers by hours online:\n" + "\n".join(lines)
        return "Hours data not available."

    elif "fleet size" in q or "how many drivers" in q:
        return f"🚗 Total fleet size: **{len(df)} drivers**."

    else:
        return (
            "🤖 I can tell you about top drivers, SBV drivers, fleet stats, and more. "
            "Try asking about:\n"
            "• Top driver\n"
            "• Drivers behind target\n"
            "• Most trips\n"
            "• Average score\n"
            "• SBV drivers\n"
            "• Lowest hours\n"
            "• Fleet size"
        )


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    # ── Header ──────────────────────────────
    col_title, col_refresh = st.columns([5, 1])
    with col_title:
        st.title("📊 SparklingBlu — Fleet Management Dashboard")
        st.caption(f"📅 {datetime.now().strftime('%A, %d %B %Y  |  %H:%M')}")
    with col_refresh:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.divider()

    # ── Data Loading ─────────────────────────
    raw_data = load_fleet_data()

    if not raw_data:
        st.warning("⚠️ No fleet data available. Please wait for the admin to publish updated stats.")
        st.stop()

    # Extract the fleet list from the stored dictionary
    if isinstance(raw_data, dict):
        fleet_list = raw_data.get("fleet", [])
    elif isinstance(raw_data, list):
        fleet_list = raw_data
    else:
        st.warning("⚠️ Unexpected data format.")
        st.stop()

    if not fleet_list:
        st.warning("⚠️ No fleet data available. Please wait for the admin to publish updated stats.")
        st.stop()

    df = pd.DataFrame(fleet_list)

    # Normalise key numeric columns
    for col in ["Hours Online", "Hours on Trip", "Total Trips", "Score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    driver_col = "Driver"
    team_col = "Team"
    hours_col = "Hours Online"
    trip_hours_col = "Hours on Trip"
    trips_col = "Total Trips"
    score_col = "Score"

    # ── Section 1: Fleet Overview ────────────
    st.markdown('<div class="section-header">Fleet Overview</div>', unsafe_allow_html=True)

    total_drivers = len(df)
    avg_hours = df[hours_col].mean() if hours_col in df.columns else 0
    avg_trips = df[trips_col].mean() if trips_col in df.columns else 0
    total_trips = int(df[trips_col].sum()) if trips_col in df.columns else 0
    avg_score = df[score_col].mean() if score_col in df.columns else 0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("👥 Total Drivers", total_drivers)
    m2.metric("⏱️ Avg Hours Online", f"{avg_hours:.1f}h")
    m3.metric("🚗 Avg Trips", f"{avg_trips:.1f}")
    m4.metric("🔢 Total Trips", f"{total_trips:,}")
    m5.metric("⭐ Avg Score", f"{avg_score:.2f}")

    # Fuel cost estimate
    fuel_km_per_trip = 5
    fuel_cost_per_km = 2.53
    estimated_fuel = total_trips * fuel_km_per_trip * fuel_cost_per_km
    st.caption(
        f"⛽ Estimated fuel cost (@ {fuel_km_per_trip}km/trip × R{fuel_cost_per_km}/km): "
        f"**R{estimated_fuel:,.2f}**"
    )

    st.divider()

    # ── Section 2: Key Insights ──────────────
    st.markdown('<div class="section-header">Key Insights</div>', unsafe_allow_html=True)

    ins_left, ins_right = st.columns(2)

    with ins_left:
        if hours_col in df.columns and driver_col in df.columns:
            top_by_hours_name = df.loc[df[hours_col].idxmax(), driver_col]
            top_by_hours_val = df[hours_col].max()
            st.markdown(
                f'<div class="insight-card"><h4>🏆 Top Driver by Hours</h4>'
                f'<p>{top_by_hours_name}</p>'
                f'<small>{top_by_hours_val:.1f} hours online</small></div>',
                unsafe_allow_html=True,
            )

        if score_col in df.columns and driver_col in df.columns:
            top_scorer_name = df.loc[df[score_col].idxmax(), driver_col]
            top_scorer_val = df[score_col].max()
            st.markdown(
                f'<div class="insight-card"><h4>⭐ Top Scorer</h4>'
                f'<p>{top_scorer_name}</p>'
                f'<small>Score: {top_scorer_val:.2f}</small></div>',
                unsafe_allow_html=True,
            )

        if hours_col in df.columns and score_col in df.columns:
            top_performers = df[(df[hours_col] >= 40) & (df[score_col] >= 4.5)]
            st.markdown(
                f'<div class="insight-card"><h4>🌟 Top Performers</h4>'
                f'<p>{len(top_performers)}</p>'
                f'<small>Drivers with ≥40h & score ≥4.5</small></div>',
                unsafe_allow_html=True,
            )

    with ins_right:
        if trips_col in df.columns and driver_col in df.columns:
            top_by_trips_name = df.loc[df[trips_col].idxmax(), driver_col]
            top_by_trips_val = int(df[trips_col].max())
            st.markdown(
                f'<div class="insight-card"><h4>🚗 Top Driver by Trips</h4>'
                f'<p>{top_by_trips_name}</p>'
                f'<small>{top_by_trips_val} total trips</small></div>',
                unsafe_allow_html=True,
            )

        if hours_col in df.columns:
            below_10h = int((df[hours_col] < 10).sum())
            st.markdown(
                f'<div class="insight-card"><h4>⚠️ Below 10h Online</h4>'
                f'<p>{below_10h}</p>'
                f'<small>Drivers under 10 hours online</small></div>',
                unsafe_allow_html=True,
            )

        if trips_col in df.columns:
            below_5t = int((df[trips_col] < 5).sum())
            st.markdown(
                f'<div class="insight-card"><h4>🔻 Below 5 Trips</h4>'
                f'<p>{below_5t}</p>'
                f'<small>Drivers with fewer than 5 trips</small></div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Section 3: Hotspot Performance ───────
    st.markdown('<div class="section-header">Hotspot Performance</div>', unsafe_allow_html=True)

    if team_col in df.columns:
        hotspot_groups = df.groupby(team_col)
        hotspot_stats = hotspot_groups.agg(
            driver_count=(driver_col, "count") if driver_col in df.columns else (team_col, "count"),
            avg_hours=(hours_col, "mean") if hours_col in df.columns else (team_col, "count"),
            avg_score=(score_col, "mean") if score_col in df.columns else (team_col, "count"),
        ).reset_index()

        # Top driver per hotspot
        if driver_col in df.columns and hours_col in df.columns:
            top_per_hotspot = (
                df.loc[df.groupby(team_col)[hours_col].idxmax()][[team_col, driver_col]]
                .set_index(team_col)
            )
        else:
            top_per_hotspot = pd.DataFrame()

        n_hotspots = len(hotspot_stats)
        cols_per_row = 3
        for i in range(0, n_hotspots, cols_per_row):
            row_cols = st.columns(cols_per_row)
            for j, col_widget in enumerate(row_cols):
                idx = i + j
                if idx >= n_hotspots:
                    break
                row = hotspot_stats.iloc[idx]
                hotspot_name = row[team_col]
                top_driver = (
                    top_per_hotspot.loc[hotspot_name, driver_col]
                    if hotspot_name in top_per_hotspot.index
                    else "N/A"
                )
                with col_widget:
                    st.metric(
                        label=f"🏙️ {hotspot_name}",
                        value=f"{int(row.get('driver_count', 0))} drivers",
                        delta=f"Avg {row.get('avg_hours', 0):.1f}h | Score {row.get('avg_score', 0):.2f}",
                    )
                    st.caption(f"Top: {top_driver}")
    else:
        st.info("No 'Team' column found in data for hotspot grouping.")

    st.divider()

    # ── Section 4: SBV Drivers ────────────────
    st.markdown('<div class="section-header">SBV Driver Tracking</div>', unsafe_allow_html=True)

    with st.expander("🚛 SBV Fleet Tracking", expanded=False):
        if driver_col in df.columns:
            sbv_mask = df[driver_col].apply(match_sbv_driver)
            sbv_df = df[sbv_mask].copy()

            active_count = len(sbv_df)
            total_sbv = len(SBV_DRIVERS)

            st.metric(
                "SBV Drivers Active",
                f"{active_count} of {total_sbv}",
                delta=f"{total_sbv - active_count} not found in data",
                delta_color="inverse",
            )

            if not sbv_df.empty:
                # Build display table
                display_cols = [c for c in [driver_col, team_col, hours_col, trips_col, score_col] if c in sbv_df.columns]
                sbv_display = sbv_df[display_cols].copy()

                # Add coaching status
                status_list = []
                for _, r in sbv_df.iterrows():
                    status, _ = get_day_aware_coaching(r)
                    status_list.append(status)
                sbv_display["Status"] = status_list

                st.dataframe(sbv_display, use_container_width=True, hide_index=True)
            else:
                st.info("No SBV drivers found in current fleet data.")

            # List missing SBV drivers
            matched_names = sbv_df[driver_col].tolist() if not sbv_df.empty else []
            missing_sbv = []
            for sbv_name in SBV_DRIVERS:
                sbv_lower = sbv_name.lower()
                sbv_parts = sbv_lower.split()
                in_data = False
                for m in matched_names:
                    m_lower = m.lower()
                    if len(sbv_parts) >= 2:
                        if sbv_parts[0] in m_lower and sbv_parts[-1] in m_lower:
                            in_data = True
                            break
                    if sbv_lower in m_lower or m_lower in sbv_lower:
                        in_data = True
                        break
                if not in_data:
                    missing_sbv.append(sbv_name)

            if missing_sbv:
                st.markdown(
                    "**SBV Drivers Not in Current Data:** " + ", ".join(missing_sbv)
                )
        else:
            st.warning("Driver column not found in data.")

    st.divider()

    # ── Section 5: Driver Table + Coaching ───
    st.markdown('<div class="section-header">Driver Performance Table</div>', unsafe_allow_html=True)

    today = datetime.now()
    weekday = today.weekday()
    days_elapsed = weekday + 1
    expected_hours_today = days_elapsed * EXPECTED_HOURS_PER_DAY
    expected_trips_today = days_elapsed * EXPECTED_TRIPS_PER_DAY

    df_table = df.copy()

    # Day-aware columns
    df_table["Day Target"] = expected_hours_today
    if hours_col in df_table.columns:
        df_table["Gap"] = (df_table["Day Target"] - df_table[hours_col]).round(2)
    else:
        df_table["Gap"] = 0

    coaching_statuses = []
    coaching_messages = []
    for _, row in df_table.iterrows():
        status, msg = get_day_aware_coaching(row)
        coaching_statuses.append(status)
        coaching_messages.append(msg)

    df_table["Status"] = coaching_statuses
    df_table["Coaching"] = coaching_messages

    # Search / filter
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_query = st.text_input(
            "🔍 Search by driver name, team, or hotspot",
            placeholder="e.g. Bright, Sandton, Team A …",
        )
    with search_col2:
        st.write("")
        st.write("")

    if search_query:
        mask = pd.Series([False] * len(df_table), index=df_table.index)
        for col in [driver_col, team_col]:
            if col in df_table.columns:
                mask |= df_table[col].astype(str).str.contains(search_query, case=False, na=False)
        df_table = df_table[mask]

    # Column order
    preferred_cols = [
        driver_col, team_col, hours_col, trip_hours_col, trips_col,
        score_col, "Day Target", "Gap", "Status", "Coaching",
    ]
    display_cols = [c for c in preferred_cols if c in df_table.columns]
    remaining = [c for c in df_table.columns if c not in display_cols]
    df_table = df_table[display_cols + remaining]

    st.caption(
        f"📅 Today is **{today.strftime('%A')}** — day {days_elapsed} of the week. "
        f"Expected target: **{expected_hours_today}h** / **{expected_trips_today} trips**."
    )
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    # Download CSV
    csv_data = df_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Fleet Data (CSV)",
        data=csv_data,
        file_name=f"sparklingblu_fleet_{today.strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=False,
    )

    st.divider()

    # ── Section 6: Sparky Chatbot ─────────────
    st.markdown('<div class="section-header">Ask Sparky</div>', unsafe_allow_html=True)

    with st.expander("🤖 Ask Sparky — Fleet Assistant", expanded=False):
        example_questions = [
            "Who is the top driver?",
            "How many drivers are behind target?",
            "Which hotspot has the most trips?",
            "What is the average score?",
            "Show me SBV drivers",
            "Who has the lowest hours?",
            "What is the fleet size?",
        ]

        st.markdown("**Quick questions:**")
        chip_cols = st.columns(len(example_questions))
        selected_example = None
        for i, q in enumerate(example_questions):
            with chip_cols[i]:
                if st.button(q, key=f"chip_{i}", use_container_width=True):
                    selected_example = q

        sparky_input = st.text_input(
            "Ask Sparky a question:",
            value=selected_example if selected_example else "",
            placeholder="e.g. Who is the top driver?",
            key="sparky_input",
        )

        if sparky_input:
            answer = get_sparky_response(sparky_input, df)
            st.markdown(
                f'<div class="sparky-answer">🤖 <strong>Sparky:</strong><br>{answer}</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Footer ────────────────────────────────
    st.caption(
        "SparklingBlu Fleet Management | Data refreshes when admin publishes new stats"
    )


if __name__ == "__main__":
    main()