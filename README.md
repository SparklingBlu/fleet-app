# SparklingBlu Fleet Management System

A multi-app Streamlit platform for managing and coaching a vehicle-supplier driver
fleet operating on Uber's platform (Gauteng, South Africa). Pulls live performance
data from the Uber API, scores drivers against weekly targets, and publishes
shareable links for drivers, team leaders, and management — no logins required for
drivers, password-protected for management.

## Live Apps

| View | Purpose | Link |
|---|---|---|
| **Admin** | Fetch live Uber data, review, publish | *(internal — admin only)* |
| **Drivers** | Drivers look up their own weekly stats | `app.py?view=drivers` |
| **Team 1** | Team 1 leader/roster view | https://fleet-app-t6p76dt6jssgfgbbgdoaga.streamlit.app |
| **Team 2** | Team 2 leader/roster view | https://fleet-app-7m2selsgmrcjivbbumchuf.streamlit.app |
| **Team 3** | Team 3 leader/roster view | https://fleet-app-ebcqtmjfr9ffomjwkvcz8r.streamlit.app |
| **Team 4** | Team 4 leader/roster view | https://fleet-app-gjp7xvjjln2xa9eq8w3kes.streamlit.app |
| **Management** | Full fleet dashboard, insights, Sparky chatbot | `app_management.py` (password protected) |

## Architecture

```
app.py              # Admin panel — fetches Uber API data, scores drivers, publishes to Gist
                     # Also serves the public Drivers and Fleet (redirect) views via ?view=
team_view.py         # Shared render_team_view() used by all four standalone team apps
team_1.py            # Standalone deployment — Team 1 (imports team_view.py)
team_2.py            # Standalone deployment — Team 2 (imports team_view.py)
team_3.py            # Standalone deployment — Team 3 (imports team_view.py)
team_4.py            # Standalone deployment — Team 4 (imports team_view.py)
app_management.py   # Password-protected management dashboard (insights, hotspots, Sparky)
engine.py            # Scoring engine — weekly targets, performance score, coaching messages
teams.py             # Team/hotspot definitions and driver-to-team matching
storage.py           # Read/write fleet data to a GitHub Gist (shared state across apps)
uber_client.py       # Uber API client — auth + fetch driver metrics
```

### Data flow

1. **Admin** (`app.py`) fetches live driver metrics from the Uber API for a chosen
   date range.
2. Each driver is scored (`engine.py`) against universal weekly targets —
   **50 hours online / 35 trips** — and assigned a status:
   `Top Performer (85+) → Good (70–84) → Needs Improvement (50–69) → Urgent Attention (<50)`.
3. Admin reviews the table, then **publishes** the dataset to a GitHub Gist
   (`storage.py`). This Gist is the single source of truth shared between all apps.
4. **Drivers**, all four **Team** apps, and **Management** all read from that
   same Gist — so every permanent link always shows the latest published data,
   with zero redeploys needed after publishing. Each team app is its own
   Streamlit Cloud deployment (main file `team_1.py`–`team_4.py`), sharing the
   same `GIST_ID`/`GITHUB_TOKEN` secrets as the admin app.

### Views in `app.py`

- `?view=admin` — fetch, score, and publish (default)
- `?view=drivers` — driver self-lookup by name
- `?view=fleet` — redirects to the management app

Team views used to be served via `?view=team&team=<name>` off `app.py`. They are
now four standalone apps (`team_1.py`-`team_4.py`), each deployed separately on
Streamlit Community Cloud and sharing `team_view.py`'s `render_team_view()`. The
admin panel's Team Links now point directly at those four app URLs instead of
a query string.

### Management dashboard (`app_management.py`)

Password-gated (`MANAGEMENT_PASSWORD` in Streamlit Secrets). Includes:
- Fleet overview metrics (drivers, hours, trips, score, estimated fuel cost)
- Key insights (top performers, drivers below threshold)
- Hotspot/team breakdown
- SBV driver tracking (hardcoded roster matched via fuzzy name matching)
- Full driver performance table with day-aware coaching messages
- **Sparky** — a simple rule-based fleet Q&A chatbot
- CSV export

## Setup

### 1. GitHub Gist (shared data store)
1. Create a personal access token with `gist` scope at
   [github.com/settings/tokens](https://github.com/settings/tokens).
2. Create a secret Gist at [gist.github.com](https://gist.github.com) named
   `fleet_data.json` with content `{}`.
3. Copy the Gist ID from its URL.

### 2. Uber API credentials
Requires an approved Uber Fleet API app with `vehicle_suppliers.organizations.read`
and `solutions.suppliers.metrics.read` scopes.

### 3. Streamlit Secrets
In each deployed app's **Settings → Secrets**:

```toml
GITHUB_TOKEN         = "ghp_..."
GIST_ID              = "..."
UBER_CLIENT_ID       = "..."
UBER_CLIENT_SECRET   = "..."
UBER_ORG_UUID        = "..."
MANAGEMENT_PASSWORD  = "..."   # app_management.py only
```

> ⚠️ Never commit real secrets to this repo. Rotate immediately if a credential is
> ever pasted into a file, screenshot, or commit by mistake.

### 4. Run locally

```bash
pip install -r requirements.txt
streamlit run app.py              # Admin / Drivers / Team
streamlit run app_management.py   # Management dashboard
```

## Weekly Targets

Universal targets, no hotspot-dependent scaling:

- **50 hours online** per week
- **35 trips** per week
- Daily pace ≈ 7.14h / 5 trips/day

Coaching tone escalates across the week (friendly early-week nudge →
midweek pace check → urgent Fri/Sat push → Sunday recap).

## Tech Stack

Python · Streamlit · pandas · Uber Fleet API · GitHub Gist (data layer) ·
Streamlit Community Cloud (hosting)

## Notes

- Drivers and team leaders need **no login** — links are permanent and
  always reflect the latest published data.
- Management dashboard is password protected.
- Fuel cost estimates use a fixed `R/km` rate and 5km/trip average — update
  `FUEL_COST_PER_KM` in `app.py` when local fuel prices change.