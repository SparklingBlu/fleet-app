# teams.py
# Team rosters + Hotspot-aligned driver assignments
# Aligned with Fleet Operational Strategy (May 25 – June 14, 2026)

# ── SBV MASTER LIST ─────────────────────────────────────────────────────────
SBV_DRIVERS = [
    "Akimu Soko", "Alfred Sanny Tshabalala", "Alli Mabvuto", "Alnord Nyirenda",
    "Amazing Calvin Servazio", "Andrew Gracious Phiri", "Anthonio Haston Bikausi",
    "Asanda Nyembe", "Blessings Maseko Sinosi", "Brian Chiremba",
    "Brian Losen Mkandla", "Bright Jere",
    "Davie Staliko", "Desmond Farai Murondi", "Esrom Maswekana",
    "Faidon Safali", "Francis Phwitiko", "Gift Obrey", "Gift Tenyiko Baloyi",
    "Gilbert Babou Marifa", "Hlayisane Mawelela",
    "Ibrahim Rishard", "Idelito Valexy", "Innocent Grant Chapotera",
    "Ishmael Mussah", "Jacob Murondi", "Jefule Mustafa", "John Msosa",
    "Jolter Sizwe Ndlovu", "Joshua Mtisi", "Junior Ishumeal", "Justin Alli",
    "Kado Genuen", "Kagiso Khoza", "Kago Ramasike", "Katleho Mahane Mahamo",
    "Khulerani Tshabalala", "Kimia Gedeon Beloko", "Lebohang Molefe",
    "Lehlohonolo Lucky Moloi", "Lester Banda", "Loshani Sakisoni",
    "Louis Suntche", "Lucas Inkosinathi Dhlamini", "Matata Samuel Netshandama",
    "Mgcini Moyo", "Mpho Mofokeng", "Nathan Ronald Nanchu", "Nekias Nkiwane",
    "Nelson Zangirai", "Ntokozo Godfrey Shwaye", "Paulo Antonio",
    "Percy Mabuza", "Raphael Banda", "Robert Nzuy Ngamuna", "Sabelo Vumasi",
    "Sam Haba", "Samuel German", "Sanele Nkosi", "Siphesihle Mdebuka",
    "Stephen Mohali", "Stiven Banda", "Tebogo Sathekge", "Vincent Tonex",
    "Vumbhoni Owen Mathye", "Vuyisa Mdebuka", "Willard Bakali",
    "Winson Chimfwembe Mwasinga", "Ofentse Matias Leballo", "Richard Laston",
]
SBV_TOTAL = len(SBV_DRIVERS)


def is_sbv_driver(name):
    """Returns True if a driver name matches any SBV driver."""
    name_lower = name.strip().lower()
    for sbv in SBV_DRIVERS:
        sbv_lower = sbv.strip().lower()
        parts = sbv_lower.split()
        if len(parts) >= 2:
            if parts[0] in name_lower and parts[-1] in name_lower:
                return True
        if sbv_lower in name_lower or name_lower in sbv_lower:
            return True
    return False


def mark_sbv_drivers(df):
    """Adds an 'Is SBV' boolean column to the dataframe."""
    df = df.copy()
    df["Is SBV"] = df["Driver"].apply(is_sbv_driver)
    return df


# ── TEAM ROSTERS (Hotspot-Aligned) ───────────────────────────────────────────
TEAMS = {
    "Midrand Hub (KFC Yarona/Ebony)": {
        "leader": "John Msosa",
        "hotspot": "Midrand Hub",
        "drivers": [
            "John Msosa", "Joshua Mtisi", "Alnord Nyirenda",
            "Yohane Stiven Banda", "Brian Losen Mkandla", "Raphael Banda",
            "Desmond Farai Murondi", "Loshani Loshani",
            "Louis Suntche", "Esrom Maswikana Sekhobana",
            "K Tshabalala", "Alli Mabvuto", "Paul Moffat",
            "Asanda Nyembe", "Innocent Grant Chapotera", "Andrew Gracious Phiri",
        ],
    },
    "Soweto Cluster (Orlando/Dlamini)": {
        "leader": "Sabelo Vumasi",
        "hotspot": "Soweto Cluster",
        "drivers": [
            "Sabelo Vumasi", "BLESSINGS ZUZE", "Siphesihle Mdebuka", "Mgcini Moyo",
            "Vinicent Tonex", "Gilbert Babou Kapanda", "Idelito Valexy",
            "Matata Samuel Netshandama", "Robert Nzuy Ngamuna",
            "Davie Nkhoma Staliko", "Samuel German", "Kado Genuen", "Richard Laston",
            "Willard Bakali", "Sam Haba", "Jacob Murondi", "Ofentse Matias Leballo",
        ],
    },
    "Kempton Park Cluster": {
        "leader": "Stephen Mohali",
        "hotspot": "Kempton Park Cluster",
        "drivers": [
            "Stephen Mohali", "Ramsey Mdumuka", "Sanele Sydwell Nkosi",
            "Nathan Ronald Nanchu", "Lebohang Molefe",
            "Sakhele Siboniso Percy Mabuza", "Lucas Inkosinathi Dhlamini",
            "Katleho Mahase Mahamo", "Lehlohonolo Lucky-Boy Moloi",
            "Nekias Nkiwane", "Vuyisa Mdebuka", "Junior Ishumeal",
            "Amazing Calvin Servazio", "Vumbhoni Owen Mathye",
            "Mpho Mofokeng", "Brian Chiremba",
        ],
    },
    "JHB CBD / Braamfontein": {
        "leader": "Lester Gilamoto Banda",
        "hotspot": "JHB CBD / Braamfontein Node",
        "drivers": [
            "Lester Gilamoto Banda", "MPENDULO INNOCENT MPILA",
            "Vusi Rodgers Mtwiche", "Bright Jere", "Jolter Ndlovu",
            "Nelson Zangirai", "Francis Phwitiko", "Jefule Mustafa",
            "Winson Mwasinga", "Paulo Antonio", "Akimu Soko",
            "Ishmael Mussah", "Faidon Safali", "Ibrahim Rishard",
            "Anele Sithole", "Hlayisane Makhuneni Mawelela",
            "Alfred Sanny Tshabalala",
        ],
    },
    "Norwood / Orange Grove": {
        "leader": "Haston Bikausi",
        "hotspot": "Norwood / Orange Grove Node",
        "drivers": [
            "Haston Bikausi", "Moses", "Pemphero Mika",
            "Musa Glenda", "Samuel", "Paul", "Ramsey",
            "Nickson Saini", "Jolter Sizwe Ndlovu", "Brian Losen Mkandla",
        ],
    },
}


def get_team_for_driver(driver_name):
    """Returns the team name for a given driver. Case-insensitive."""
    name_lower = driver_name.strip().lower()
    for team_name, team_data in TEAMS.items():
        for d in team_data["drivers"]:
            if d.strip().lower() == name_lower:
                return team_name
    return "Unassigned"


def get_hotspot_for_driver(driver_name):
    """Returns the hotspot name for a given driver."""
    name_lower = driver_name.strip().lower()
    for team_name, team_data in TEAMS.items():
        for d in team_data["drivers"]:
            if d.strip().lower() == name_lower:
                return team_data.get("hotspot", "Unassigned")
    return "Unassigned"


def match_drivers_to_teams(df):
    """Adds Team and Hotspot columns to the dataframe."""
    df = df.copy()
    df["Team"] = df["Driver"].apply(get_team_for_driver)
    df["Hotspot"] = df["Driver"].apply(get_hotspot_for_driver)
    return df


def is_sbv_driver_dynamic(name, sbv_list):
    """Same as is_sbv_driver but uses a dynamic list."""
    name_lower = name.strip().lower()
    for sbv in sbv_list:
        sbv_lower = str(sbv).strip().lower()
        parts = sbv_lower.split()
        if len(parts) >= 2:
            if parts[0] in name_lower and parts[-1] in name_lower:
                return True
        if sbv_lower in name_lower or name_lower in sbv_lower:
            return True
    return False