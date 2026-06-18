# hotspots.py — SparklingBlu Hotspot Configuration & Benchmarks
# Aligned with Fleet Operational Strategy (May 25 – June 14, 2026)

HOTSPOTS = {
    "Kempton Park Cluster": {
        "anchor": "Birchgate / Terenure",
        "leader": "John Msosa",
        "trip_mix": {"Courier Connect": 43, "Eats Delivery": 78},
        "total_historical_trips": 121,
        "shift_hours": "8-10 Hours",
        "primary_type": "Courier & Eats Mix",
        "doable_trips_target": "12-14 Trips",
        "daily_gross_yield": "R380-R500",
        "peak_blocks": ["Morning (07:00-10:00)", "Dinner (17:00-21:00)"],
        "fuel_deployment_rule": "Restrict drivers to localized delivery legs",
    },
    "Soweto Cluster": {
        "anchor": "Orlando East / Dlamini",
        "leader": "Vusi Rodgers",
        "trip_mix": {"Courier Connect": 66, "Eats Delivery": 53},
        "total_historical_trips": 119,
        "shift_hours": "8-10 Hours",
        "primary_type": "50% Courier / 50% Eats",
        "doable_trips_target": "10-12 Trips",
        "daily_gross_yield": "R380-R500",
        "peak_blocks": ["Morning (07:00-10:00)"],
        "fuel_deployment_rule": "Deploy local Soweto-based drivers exclusively",
    },
    "Midrand Hub": {
        "anchor": "KFC Yarona / KFC Ebony",
        "leader": "Musa Glenda",
        "trip_mix": {"Courier Connect": 1, "Eats Delivery": 107},
        "total_historical_trips": 108,
        "shift_hours": "8-10 Hours",
        "primary_type": "Uber Eats Delivery",
        "doable_trips_target": "12-15 Trips",
        "daily_gross_yield": "R350-R450",
        "peak_blocks": ["Lunch (11:30-14:30)"],
        "fuel_deployment_rule": "Enforce absolute engine-off parking rule",
        "top_drivers": {
            "KFC Yarona": {"driver": "John Msosa", "peak_weekly_trips": 38},
            "KFC Sophiatown": {"driver": "Pemphero Mika", "peak_weekly_trips": 25},
            "KFC Ebony": {"driver": "Vusi Rodgers / Ramsey", "peak_weekly_trips": 22},
            "KFC Evergreens": {"driver": "Musa Glenda / Samuel", "peak_weekly_trips": 17},
            "KFC Phumula": {"driver": "Paul", "peak_weekly_trips": 14},
        },
    },
    "JHB CBD / Braamfontein Node": {
        "anchor": "Inner City Hub",
        "leader": "Nickson Saini",
        "trip_mix": {"Courier Connect": 4, "Eats Delivery": 40},
        "total_historical_trips": 44,
        "shift_hours": "8-10 Hours",
        "primary_type": "Uber Eats Dominant",
        "doable_trips_target": "10-13 Trips",
        "daily_gross_yield": "R400-R550",
        "peak_blocks": ["Lunch (11:30-14:30)"],
        "fuel_deployment_rule": "Ideal for rapid short-distance order turnarounds",
    },
    "Roodepoort / West Rand Cluster": {
        "anchor": "West Rand",
        "leader": "TBD",
        "trip_mix": {"Courier Connect": 18, "Eats Delivery": 25},
        "total_historical_trips": 43,
        "shift_hours": "8-10 Hours",
        "primary_type": "Mixed",
        "doable_trips_target": "8-10 Trips",
        "daily_gross_yield": "R300-R420",
        "peak_blocks": ["Morning (07:00-10:00)"],
        "fuel_deployment_rule": "Pair only with drivers residing in West Rand",
    },
    "Norwood / Orange Grove Node": {
        "anchor": "Commercial Strip",
        "leader": "Moses",
        "trip_mix": {"Courier Connect": 8, "Eats Delivery": 30},
        "total_historical_trips": 38,
        "shift_hours": "6-8 Hours (Peak)",
        "primary_type": "Premium Eats Delivery",
        "doable_trips_target": "8-10 Trips",
        "daily_gross_yield": "R350-R450",
        "peak_blocks": ["Dinner (17:00-21:00)"],
        "fuel_deployment_rule": "Prime node for premium evening dinner deliveries",
    },
}

# Weekly performance benchmarks per hotspot
HOTSPOT_WEEKLY_TARGETS = {
    "Midrand Hub": {
        "weekly_hours_min": 40,
        "weekly_hours_max": 50,
        "weekly_trips_min": 60,
        "weekly_trips_max": 75,
    },
    "Kempton Park Cluster": {
        "weekly_hours_min": 40,
        "weekly_hours_max": 50,
        "weekly_trips_min": 60,
        "weekly_trips_max": 75,
    },
    "Soweto Cluster": {
        "weekly_hours_min": 40,
        "weekly_hours_max": 50,
        "weekly_trips_min": 50,
        "weekly_trips_max": 65,
    },
    "JHB CBD / Braamfontein Node": {
        "weekly_hours_min": 40,
        "weekly_hours_max": 50,
        "weekly_trips_min": 50,
        "weekly_trips_max": 65,
    },
    "Roodepoort / West Rand Cluster": {
        "weekly_hours_min": 40,
        "weekly_hours_max": 50,
        "weekly_trips_min": 40,
        "weekly_trips_max": 55,
    },
    "Norwood / Orange Grove Node": {
        "weekly_hours_min": 40,
        "weekly_hours_max": 50,
        "weekly_trips_min": 40,
        "weekly_trips_max": 50,
    },
}
# Hotspot proximity map — used by coaching engine to recommend a NEARBY
# busier hotspot when a driver is behind pace, rather than any random
# hotspot fleet-wide. Based on Gauteng geography (Midrand/Kempton Park
# are both north-east; Soweto/JHB CBD/Roodepoort are south/west; Norwood
# sits between JHB CBD and Midrand).
#
# ⚠️ REVIEW THIS — adjust pairings based on actual driver travel patterns.
NEARBY_HOTSPOTS = {
    "Midrand Hub": ["Kempton Park Cluster", "Norwood / Orange Grove Node"],
    "Kempton Park Cluster": ["Midrand Hub", "JHB CBD / Braamfontein Node"],
    "Soweto Cluster": ["Roodepoort / West Rand Cluster", "JHB CBD / Braamfontein Node"],
    "JHB CBD / Braamfontein Node": ["Norwood / Orange Grove Node", "Soweto Cluster", "Kempton Park Cluster"],
    "Roodepoort / West Rand Cluster": ["Soweto Cluster"],
    "Norwood / Orange Grove Node": ["JHB CBD / Braamfontein Node", "Midrand Hub"],
}


def get_busier_nearby_hotspot(current_hotspot):
    """
    Returns the name of the nearest hotspot with a HIGHER weekly trips
    target than the driver's current hotspot, or None if their current
    hotspot is already the busiest nearby option.
    """
    if current_hotspot not in HOTSPOT_WEEKLY_TARGETS:
        return None

    current_target = HOTSPOT_WEEKLY_TARGETS[current_hotspot]["weekly_trips_min"]
    candidates = NEARBY_HOTSPOTS.get(current_hotspot, [])

    best_name   = None
    best_target = current_target

    for candidate in candidates:
        cand_target = HOTSPOT_WEEKLY_TARGETS.get(candidate, {}).get("weekly_trips_min", 0)
        if cand_target > best_target:
            best_target = cand_target
            best_name   = candidate

    return best_name

# Fuel cost constants (Inland 95 Petrol @ R28.06/L)
FUEL_PRICE_PER_LITRE = 28.06
URBAN_CONSUMPTION_L_PER_100KM = 9.0
COST_PER_KM = (FUEL_PRICE_PER_LITRE * URBAN_CONSUMPTION_L_PER_100KM) / 100  # R2.53/km

# Peak time blocks
PEAK_BLOCKS = {
    "Morning": {"start": 7, "end": 10, "strategy": "Route 70% to Soweto & Kempton Park"},
    "Lunch": {"start": 11.5, "end": 14.5, "strategy": "Route to Midrand & JHB CBD"},
    "Dinner": {"start": 17, "end": 21, "strategy": "Position in Norwood & Kempton Park"},
}

def get_hotspot_for_driver(driver_name):
    """Assign driver to hotspot based on team/proximity"""
    # This will be enhanced with actual driver-to-hotspot mapping
    # For now, returns None — assignment done via teams.py
    return None

def get_current_peak_block():
    """Return the current peak block based on time of day"""
    from datetime import datetime
    now = datetime.now()
    hour = now.hour + now.minute / 60
    
    for block_name, block_info in PEAK_BLOCKS.items():
        if block_info["start"] <= hour <= block_info["end"]:
            return block_name, block_info["strategy"]
    
    return "Off-Peak", "Maintain position at assigned hotspot"