# teams.py
# Team rosters — SBV Team Groupings (current structure)

# ── SBV MASTER LIST ───────────────────────────────────────────────────────
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


# ── TEAM ROSTERS (current structure — SBV Team Groupings) ──────────────────
TEAMS = {
    "Team 1": {
        "leader": "Sailence Matolo",
        "drivers": [
            "Sailence Matolo", "Nekias Nkiwane", "Stephen Mohali",
            "Nicholas Bafana Mahlangu", "Eid Kazembe", "Sihle Tivane",
            "Haston Bikausi", "Ramsey Mdumuka", "Samuel German",
            "Asanda Nyembe", "Ndumiso Humphrey Bukwana", "Maganga Chikondi",
        ],
    },
    "Team 2": {
        "leader": "John Msosa",
        "drivers": [
            "John Msosa", "Sakhele Siboniso Percy Mabuza", "Mgcini Moyo",
            "Gian Manda", "Jali Useni Bvumbwe", "Vusi Rodgers Mtwiche",
            "Nhlokomo Selby Thomo", "Desmond Farai Murondi", "Joshua Mtisi",
            "Sanele Sydwell Nkosi", "Jacob Murondi", "Kabela Danny Chauke",
        ],
    },
    "Team 3": {
        "leader": "Jolter Ndlovu",
        "drivers": [
            "Jolter Ndlovu", "Loshani Loshani", "Haroon Kimu",
            "Winson Mwasinga", "William Ozil Banda", "Sthembiso Josia Mbuli",
            "Katleho Mahase Mahamo", "Peter Tedious Chirefu", "Lebohang Molefe",
            "Magetsi Daudi", "Gilbert Babou Kapanda", "Alex Edward Mabuka",
        ],
    },
    "Team 4": {
        "leader": "Brian Losen Mkandla",
        "drivers": [
            "Brian Losen Mkandla", "Nelson Zangirai", "Twesta Ebelo",
            "Alnord Nyirenda", "Ibrahim Rishard", "Willard Bakali",
            "Anele Sithole", "Mpendulo Prince Ndlovu", "Amazing Calvin Servazio",
            "Lehlohonolo Lucky-Boy Moloi", "Junior Ishumeal", "Katleho Morgan Khanye",
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
    """Hotspot concept retired — teams are no longer hotspot-based.
    Kept only so any older code still calling this doesn't break."""
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
