import streamlit as st
import sqlite3
import pandas as pd
import pydeck as pdk
import requests
import io
import math
from datetime import date


# ============================================================
# KONFIGURATION
# ============================================================

st.set_page_config(
    page_title="My Flight Network",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "flights.db"

AIRPORT_DATABASE_URL = (
    "https://ourairports.com/data/airports.csv"
)


# ============================================================
# DESIGN
# ============================================================

st.markdown("""
<style>

:root {
    --background: #0b1120;
    --card: #111827;
    --card-hover: #172033;
    --border: #263247;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --accent-dark: #0284c7;
}

/* ============================================================
   APP HINTERGRUND
   ============================================================ */

html,
body,
[data-testid="stAppViewContainer"] {

    background:
        radial-gradient(
            circle at top right,
            rgba(14, 165, 233, 0.10),
            transparent 35%
        ),
        radial-gradient(
            circle at bottom left,
            rgba(99, 102, 241, 0.08),
            transparent 35%
        ),
        #0b1120 !important;

    color: #f1f5f9;
}

/* ============================================================
   HAUPTBEREICH
   ============================================================ */

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #0f172a 0%,
            #0b1120 100%
        ) !important;

    border-right: 1px solid #1e293b;
}

section[data-testid="stSidebar"] h1 {

    font-weight: 700;
    letter-spacing: -0.5px;
}

section[data-testid="stSidebar"] .stRadio label {

    border-radius: 8px;
    padding: 7px 10px;
}

/* ============================================================
   ÜBERSCHRIFTEN
   ============================================================ */

h1,
h2,
h3 {

    color: #f8fafc !important;
    letter-spacing: -0.4px;
}

h1 {
    font-size: 2.1rem !important;
}

h2 {
    font-size: 1.5rem !important;
}

h3 {
    font-size: 1.15rem !important;
}

/* ============================================================
   METRIKEN
   ============================================================ */

div[data-testid="stMetric"] {

    background:
        linear-gradient(
            145deg,
            #111827,
            #0f172a
        ) !important;

    border: 1px solid #263247;

    padding: 18px;

    border-radius: 14px;

    box-shadow:
        0 8px 25px rgba(0, 0, 0, 0.18);
}

div[data-testid="stMetric"]:hover {

    border-color: #334155;
}

/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {

    border-radius: 9px;

    border: 1px solid #334155;

    background:
        linear-gradient(
            135deg,
            #1e293b,
            #172033
        ) !important;

    color: #f8fafc !important;

    font-weight: 600;

    transition:
        all 0.15s ease;
}

.stButton > button:hover {

    border-color: #38bdf8 !important;

    background:
        linear-gradient(
            135deg,
            #164e63,
            #1e293b
        ) !important;

    color: white !important;
}

/* ============================================================
   PRIMÄRE BUTTONS
   ============================================================ */

button[kind="primary"] {

    background:
        linear-gradient(
            135deg,
            #0284c7,
            #2563eb
        ) !important;

    border: none !important;
}

button[kind="primary"]:hover {

    background:
        linear-gradient(
            135deg,
            #0369a1,
            #1d4ed8
        ) !important;
}

/* ============================================================
   NORMALE INPUT FELDER
   ============================================================ */

div[data-baseweb="input"] {

    background-color: #0b1120 !important;

    border-radius: 9px !important;

    border-color: #0b1120 !important;
}

div[data-baseweb="input"] > div {

    background-color: #0b1120 !important;

    border-color: #0b1120 !important;
}

div[data-baseweb="input"] input {

    background-color: #0b1120 !important;

    color: #f8fafc !important;
}

div[data-baseweb="input"]:focus-within {

    border-color: #0b1120 !important;

    box-shadow: none !important;
}

/* ============================================================
   TEXTAREA
   ============================================================ */

textarea {

    background-color: #0b1120 !important;

    color: #f8fafc !important;

    border-color: #0b1120 !important;

    border-radius: 9px !important;
}

textarea:focus {

    border-color: #0b1120 !important;

    box-shadow: none !important;
}

/* ============================================================
   SELECTBOX
   ============================================================ */

div[data-baseweb="select"] {

    background-color: #0b1120 !important;

    border-radius: 9px !important;
}

div[data-baseweb="select"] > div {

    background-color: #0b1120 !important;

    border-color: #0b1120 !important;

    border-radius: 9px !important;

    box-shadow: none !important;
}

div[data-baseweb="select"] > div:hover {

    border-color: #0b1120 !important;
}

div[data-baseweb="select"] > div:focus-within {

    border-color: #0b1120 !important;

    box-shadow: none !important;
}

/* ============================================================
   MULTISELECT
   ============================================================ */

/*
   Streamlit / BaseWeb verwendet je nach Version mehrere
   verschachtelte Elemente. Deshalb werden hier alle
   relevanten Ebenen auf den App-Hintergrund gesetzt.
*/

div[data-testid="stMultiSelect"] {

    background-color: #0b1120 !important;

    border-radius: 9px !important;
}

div[data-testid="stMultiSelect"] > div {

    background-color: #0b1120 !important;

    border-color: #0b1120 !important;
}

div[data-testid="stMultiSelect"] div[data-baseweb="select"] {

    background-color: #0b1120 !important;

    border-color: #0b1120 !important;
}

div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {

    background-color: #0b1120 !important;

    border: 1px solid #0b1120 !important;

    box-shadow: none !important;

    border-radius: 9px !important;

    min-height: 42px;
}

div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div:hover {

    background-color: #0b1120 !important;

    border-color: #0b1120 !important;
}

div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div:focus-within {

    background-color: #0b1120 !important;

    border-color: #0b1120 !important;

    box-shadow: none !important;
}

/* Input innerhalb des Multiselect */

div[data-testid="stMultiSelect"] input {

    background-color: #0b1120 !important;

    color: #f8fafc !important;
}

/* Placeholder */

div[data-testid="stMultiSelect"] input::placeholder {

    color: #64748b !important;
}

/* ============================================================
   AUSGEWÄHLTE MULTISELECT-EINTRÄGE
   ============================================================ */

div[data-testid="stMultiSelect"] [data-baseweb="tag"] {

    background-color: #1e293b !important;

    border: 1px solid #334155 !important;

    color: #f8fafc !important;

    border-radius: 6px !important;
}

div[data-testid="stMultiSelect"] [data-baseweb="tag"] span {

    color: #f8fafc !important;
}

/* ============================================================
   MULTISELECT DROPDOWN
   ============================================================ */

div[data-baseweb="popover"] {

    background-color: #111827 !important;

    border: 1px solid #263247 !important;
}

div[data-baseweb="menu"] {

    background-color: #111827 !important;
}

div[data-baseweb="menu"] li {

    background-color: #111827 !important;

    color: #f8fafc !important;
}

div[data-baseweb="menu"] li:hover {

    background-color: #1e293b !important;
}

/* ============================================================
   COLOR PICKER
   ============================================================ */

div[data-testid="stColorPicker"] {

    background-color: transparent !important;
}

/* ============================================================
   DATAFRAME
   ============================================================ */

[data-testid="stDataFrame"] {

    border-radius: 12px;

    overflow: hidden;

    border: 1px solid #263247;
}

/* ============================================================
   DIVIDER
   ============================================================ */

hr {

    border-color: #1e293b;
}

/* ============================================================
   INFO / SUCCESS / WARNING
   ============================================================ */

div[data-testid="stAlert"] {

    border-radius: 10px;
}

/* ============================================================
   TEXT
   ============================================================ */

.small-muted {

    color: #94a3b8;

    font-size: 0.9rem;
}

/* ============================================================
   AIRLINE-FARBKARTEN
   ============================================================ */

.airline-color-card {

    background:
        linear-gradient(
            145deg,
            #111827,
            #0f172a
        );

    border: 1px solid #263247;

    border-radius: 12px;

    padding: 12px 14px;

    margin-bottom: 8px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATENBANK
# ============================================================

def get_connection():

    return sqlite3.connect(DB_FILE)


def init_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            date TEXT NOT NULL,

            airline TEXT NOT NULL,

            flight_number TEXT,

            aircraft TEXT NOT NULL,

            departure TEXT NOT NULL,

            arrival TEXT NOT NULL,

            flight_time REAL DEFAULT 0,

            distance REAL DEFAULT 0,

            notes TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS airports (

            ident TEXT PRIMARY KEY,

            type TEXT,

            name TEXT,

            latitude REAL,

            longitude REAL,

            elevation REAL,

            continent TEXT,

            iso_country TEXT,

            iso_region TEXT,

            municipality TEXT,

            iata_code TEXT,

            home_link TEXT,

            wikipedia_link TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS database_info (

            key TEXT PRIMARY KEY,

            value TEXT
        )
    """)

    conn.commit()

    conn.close()


# ============================================================
# FLUGHAFENDATENBANK HERUNTERLADEN
# ============================================================

def download_airports():

    try:

        response = requests.get(
            AIRPORT_DATABASE_URL,
            timeout=60
        )

        response.raise_for_status()

        return pd.read_csv(
            io.BytesIO(response.content)
        )

    except Exception as error:

        st.error(
            f"Fehler beim Herunterladen: {error}"
        )

        return None


# ============================================================
# FLUGHÄFEN IMPORTIEREN
# ============================================================

def import_airports(df):

    if df is None or df.empty:

        return False

    conn = get_connection()

    required_columns = [

        "ident",
        "type",
        "name",
        "latitude_deg",
        "longitude_deg",
        "elevation_ft",
        "continent",
        "iso_country",
        "iso_region",
        "municipality",
        "iata_code",
        "home_link",
        "wikipedia_link"
    ]

    available = [

        column
        for column in required_columns
        if column in df.columns
    ]

    df = df[available].copy()

    rename = {

        "latitude_deg":
            "latitude",

        "longitude_deg":
            "longitude",

        "elevation_ft":
            "elevation"
    }

    df = df.rename(
        columns=rename
    )

    for column in [

        "type",
        "name",
        "latitude",
        "longitude",
        "elevation",
        "continent",
        "iso_country",
        "iso_region",
        "municipality",
        "iata_code",
        "home_link",
        "wikipedia_link"

    ]:

        if column not in df.columns:

            df[column] = None

    airport_types = [

        "large_airport",
        "medium_airport",
        "small_airport",
        "heliport",
        "seaplane_base",
        "balloonport",
        "closed"
    ]

    df = df[
        df["type"].isin(airport_types)
    ]

    df["ident"] = (

        df["ident"]

        .fillna("")

        .astype(str)

        .str.upper()

        .str.strip()
    )

    df = df[
        df["ident"] != ""
    ]

    df.to_sql(

        "airports",

        conn,

        if_exists="replace",

        index=False
    )

    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO database_info
        (key, value)
        VALUES (?, ?)
    """, (

        "airports_updated",

        str(pd.Timestamp.now())
    ))

    conn.commit()

    conn.close()

    return True


# ============================================================
# PRÜFEN, OB AIRPORT-DATENBANK VORHANDEN IST
# ============================================================

def airport_database_exists():

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            "SELECT COUNT(*) FROM airports"
        )

        count = cursor.fetchone()[0]

        conn.close()

        return count > 0

    except Exception:

        conn.close()

        return False


# ============================================================
# FLUGHAFEN SUCHEN
# ============================================================

def search_airports(search):

    conn = get_connection()

    search = search.upper().strip()

    query = """
        SELECT
            ident,
            iata_code,
            name,
            municipality,
            iso_country,
            latitude,
            longitude
        FROM airports
        WHERE
            UPPER(ident) LIKE ?
            OR UPPER(COALESCE(iata_code, '')) LIKE ?
            OR UPPER(name) LIKE ?
            OR UPPER(COALESCE(municipality, '')) LIKE ?
        ORDER BY
            CASE
                WHEN UPPER(ident) = ?
                THEN 0
                WHEN UPPER(COALESCE(iata_code, '')) = ?
                THEN 1
                ELSE 2
            END,
            name
        LIMIT 50
    """

    like = f"%{search}%"

    df = pd.read_sql_query(

        query,

        conn,

        params=[

            like,
            like,
            like,
            like,
            search,
            search
        ]
    )

    conn.close()

    return df


# ============================================================
# EINEN FLUGHAFEN LADEN
# ============================================================

def get_airport(icao):

    conn = get_connection()

    df = pd.read_sql_query(

        """
        SELECT *
        FROM airports
        WHERE ident = ?
        LIMIT 1
        """,

        conn,

        params=[
            icao.upper()
        ]
    )

    conn.close()

    if df.empty:

        return None

    return df.iloc[0].to_dict()


# ============================================================
# FLUG SPEICHERN
# ============================================================

def add_flight(

    flight_date,
    airline,
    flight_number,
    aircraft,
    departure,
    arrival,
    flight_time,
    distance,
    notes

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO flights (

            date,
            airline,
            flight_number,
            aircraft,
            departure,
            arrival,
            flight_time,
            distance,
            notes

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        flight_date,
        airline,
        flight_number,
        aircraft,
        departure,
        arrival,
        flight_time,
        distance,
        notes
    ))

    conn.commit()

    conn.close()


# ============================================================
# FLÜGE LADEN
# ============================================================

def get_flights():

    conn = get_connection()

    df = pd.read_sql_query(

        """
        SELECT *
        FROM flights
        ORDER BY date DESC, id DESC
        """,

        conn
    )

    conn.close()

    return df


# ============================================================
# FLUG LÖSCHEN
# ============================================================

def delete_flight(flight_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        "DELETE FROM flights WHERE id = ?",

        (flight_id,)
    )

    conn.commit()

    conn.close()


# ============================================================
# DISTANZ BERECHNEN
# ============================================================

def calculate_distance(

    lat1,
    lon1,
    lat2,
    lon2

):

    radius = 6371.0

    lat1 = math.radians(lat1)

    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)

    lon2 = math.radians(lon2)

    dlat = lat2 - lat1

    dlon = lon2 - lon1

    a = (

        math.sin(dlat / 2) ** 2

        +

        math.cos(lat1)

        * math.cos(lat2)

        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(

        math.sqrt(a),

        math.sqrt(1 - a)
    )

    return radius * c


# ============================================================
# STANDARD-AIRLINE-FARBEN
# ============================================================

DEFAULT_AIRLINE_COLORS = {

    "Lufthansa":
        "#005AB9",

    "Eurowings":
        "#B4005A",

    "Ryanair":
        "#0064C8",

    "easyJet":
        "#FF6400",

    "British Airways":
        "#3250BE",

    "Air France":
        "#3C5AD2",

    "KLM":
        "#0096DC",

    "Emirates":
        "#DC1E1E",

    "Qatar Airways":
        "#820050",

    "Turkish Airlines":
        "#DC0000",

    "United Airlines":
        "#005AB4",

    "American Airlines":
        "#0050AA",

    "Delta Air Lines":
        "#C80032",

    "Singapore Airlines":
        "#FA9600",

    "Qantas":
        "#C80000"
}


FALLBACK_AIRLINE_COLORS = [

    "#38BDF8",
    "#818CF8",
    "#A78BFA",
    "#F472B6",
    "#FB7185",
    "#FB923C",
    "#FACC15",
    "#4ADE80",
    "#2DD4BF",
    "#22D3EE",
    "#60A5FA",
    "#C084FC"
]


# ============================================================
# AIRLINE-FARBE ERMITTELN
# ============================================================

def get_default_airline_color(

    airline,
    index=0

):

    if airline in DEFAULT_AIRLINE_COLORS:

        return DEFAULT_AIRLINE_COLORS[
            airline
        ]

    return FALLBACK_AIRLINE_COLORS[
        index % len(FALLBACK_AIRLINE_COLORS)
    ]


# ============================================================
# HEX → RGB
# ============================================================

def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return [

        int(hex_color[0:2], 16),

        int(hex_color[2:4], 16),

        int(hex_color[4:6], 16)
    ]


# ============================================================
# INITIALISIERUNG
# ============================================================

init_database()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "My Flight Network"
)

st.sidebar.caption(
    "Flight Logbook"
)

st.sidebar.divider()

page = st.sidebar.radio(

    "Navigation",

    [

        "Streckennetz",

        "Flug hinzufügen",

        "Flugbuch",

        "Statistik",

        "Flughafendatenbank"
    ]
)


# ============================================================
# FLUGHAFENDATENBANK
# ============================================================

if page == "Flughafendatenbank":

    st.title(
        "Flughafendatenbank"
    )

    st.write(

        "Die Flughafendaten werden lokal "
        "in deiner SQLite-Datenbank gespeichert."
    )

    st.divider()

    if airport_database_exists():

        conn = get_connection()

        count = pd.read_sql_query(

            "SELECT COUNT(*) AS count FROM airports",

            conn

        ).iloc[0]["count"]

        conn.close()

        st.success(

            f"Flughafendatenbank aktiv: "
            f"{count:,} Flughäfen gespeichert."
        )

    else:

        st.warning(

            "Noch keine Flughafendatenbank vorhanden."
        )

    st.subheader(
        "Datenbank aktualisieren"
    )

    st.write(

        "Hiermit wird die aktuelle weltweite "
        "Flughafendatenbank heruntergeladen."
    )

    if st.button(

        "Flughafendatenbank herunterladen",

        type="primary",

        use_container_width=True

    ):

        with st.spinner(

            "Flughafendaten werden heruntergeladen..."
        ):

            airport_df = download_airports()

        if airport_df is not None:

            with st.spinner(

                "Daten werden lokal gespeichert..."
            ):

                success = import_airports(
                    airport_df
                )

            if success:

                st.success(

                    f"{len(airport_df):,} "
                    "Flughäfen wurden importiert."
                )

                st.rerun()

    st.divider()

    if airport_database_exists():

        st.subheader(
            "Flughafen suchen"
        )

        search = st.text_input(

            "ICAO, IATA, Name oder Stadt",

            placeholder=(
                "Beispiel: EDDH, HAM oder Hamburg"
            )
        )

        if search:

            results = search_airports(
                search
            )

            if results.empty:

                st.warning(
                    "Kein Flughafen gefunden."
                )

            else:

                results = results.rename(

                    columns={

                        "ident":
                            "ICAO",

                        "iata_code":
                            "IATA",

                        "name":
                            "Flughafen",

                        "municipality":
                            "Stadt",

                        "iso_country":
                            "Land",

                        "latitude":
                            "Latitude",

                        "longitude":
                            "Longitude"
                    }
                )

                st.dataframe(

                    results,

                    use_container_width=True,

                    hide_index=True
                )


# ============================================================
# FLUG HINZUFÜGEN
# ============================================================

elif page == "Flug hinzufügen":

    st.title(
        "Flug hinzufügen"
    )

    if not airport_database_exists():

        st.warning(

            "Die Flughafendatenbank ist noch nicht installiert."
        )

        if st.button(

            "Flughafendatenbank jetzt laden",

            type="primary"
        ):

            with st.spinner(

                "Daten werden heruntergeladen..."
            ):

                df = download_airports()

            if df is not None:

                import_airports(df)

                st.success(

                    "Flughafendatenbank wurde installiert."
                )

                st.rerun()

        st.stop()

    # --------------------------------------------------------
    # ALLGEMEINE FLUGDATEN
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        flight_date = st.date_input(

            "Flugdatum",

            value=date.today()
        )

        airline = st.text_input(

            "Airline",

            placeholder="Beispiel: Lufthansa"
        )

        flight_number = st.text_input(

            "Flugnummer",

            placeholder="Beispiel: LH206"
        )

        aircraft = st.text_input(

            "Flugzeug",

            placeholder="Beispiel: Airbus A320neo"
        )

    with col2:

        # ----------------------------------------------------
        # ABFLUG
        # ----------------------------------------------------

        st.write(
            "Abflughafen"
        )

        departure_search = st.text_input(

            "Suche nach Abflughafen",

            placeholder=(
                "ICAO, IATA oder Flughafenname"
            ),

            key="departure_search"
        )

        departure = ""

        if departure_search:

            departure_results = search_airports(

                departure_search
            )

            if not departure_results.empty:

                departure_options = {

                    (
                        f"{row['ident']} | "
                        f"{row['iata_code'] or '-'} | "
                        f"{row['name']} | "
                        f"{row['municipality'] or '-'}"
                    ):

                        row["ident"]

                    for _, row
                    in departure_results.iterrows()
                }

                selected_departure = st.selectbox(

                    "Abflughafen auswählen",

                    list(
                        departure_options.keys()
                    ),

                    key="departure_select"
                )

                departure = departure_options[
                    selected_departure
                ]

            else:

                st.warning(
                    "Kein Flughafen gefunden."
                )

        # ----------------------------------------------------
        # ZIEL
        # ----------------------------------------------------

        st.write(
            "Zielflughafen"
        )

        arrival_search = st.text_input(

            "Suche nach Zielflughafen",

            placeholder=(
                "ICAO, IATA oder Flughafenname"
            ),

            key="arrival_search"
        )

        arrival = ""

        if arrival_search:

            arrival_results = search_airports(

                arrival_search
            )

            if not arrival_results.empty:

                arrival_options = {

                    (
                        f"{row['ident']} | "
                        f"{row['iata_code'] or '-'} | "
                        f"{row['name']} | "
                        f"{row['municipality'] or '-'}"
                    ):

                        row["ident"]

                    for _, row
                    in arrival_results.iterrows()
                }

                selected_arrival = st.selectbox(

                    "Zielflughafen auswählen",

                    list(
                        arrival_options.keys()
                    ),

                    key="arrival_select"
                )

                arrival = arrival_options[
                    selected_arrival
                ]

            else:

                st.warning(
                    "Kein Flughafen gefunden."
                )

    # --------------------------------------------------------
    # FLUGZEIT
    # --------------------------------------------------------

    flight_time = st.number_input(

        "Flugzeit in Stunden",

        min_value=0.0,

        max_value=30.0,

        value=1.0,

        step=0.1
    )

    notes = st.text_area(

        "Notizen",

        placeholder=(

            "Beispiel: VATSIM, schlechtes Wetter, "
            "ILS-Anflug, manuelle Landung..."
        )
    )

    # --------------------------------------------------------
    # DISTANZ
    # --------------------------------------------------------

    distance = 0

    if departure and arrival:

        dep = get_airport(
            departure
        )

        arr = get_airport(
            arrival
        )

        if dep and arr:

            distance = calculate_distance(

                dep["latitude"],
                dep["longitude"],

                arr["latitude"],
                arr["longitude"]
            )

            st.info(

                f"Entfernung: "
                f"{distance:,.0f} km"
            )

    st.divider()

    # --------------------------------------------------------
    # SPEICHERN
    # --------------------------------------------------------

    if st.button(

        "Flug speichern",

        type="primary",

        use_container_width=True

    ):

        if not airline:

            st.error(
                "Bitte eine Airline eingeben."
            )

        elif not aircraft:

            st.error(
                "Bitte ein Flugzeug eingeben."
            )

        elif not departure:

            st.error(
                "Bitte einen Abflughafen auswählen."
            )

        elif not arrival:

            st.error(
                "Bitte einen Zielflughafen auswählen."
            )

        elif departure == arrival:

            st.error(

                "Abflug und Ziel dürfen nicht identisch sein."
            )

        else:

            add_flight(

                str(flight_date),

                airline,

                flight_number,

                aircraft,

                departure,

                arrival,

                flight_time,

                distance,

                notes
            )

            st.success(

                "Flug wurde erfolgreich gespeichert."
            )


# ============================================================
# STRECKENNETZ
# ============================================================

elif page == "Streckennetz":

    st.title(
        "Mein Streckennetz"
    )

    flights = get_flights()

    if flights.empty:

        st.info(
            "Noch keine Flüge vorhanden."
        )

    else:

        # ----------------------------------------------------
        # AIRLINES / FLUGZEUGE
        # ----------------------------------------------------

        airlines = sorted(

            flights["airline"]

            .dropna()

            .unique()
        )

        aircraft = sorted(

            flights["aircraft"]

            .dropna()

            .unique()
        )

        # ----------------------------------------------------
        # STANDARD-FARBEN FÜR NEUE AIRLINES
        # ----------------------------------------------------

        if "airline_colors" not in st.session_state:

            st.session_state.airline_colors = {}

        for index, airline_name in enumerate(airlines):

            if airline_name not in st.session_state.airline_colors:

                st.session_state.airline_colors[
                    airline_name
                ] = get_default_airline_color(

                    airline_name,

                    index
                )

        # ----------------------------------------------------
        # FILTER
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            selected_airlines = st.multiselect(

                "Airlines anzeigen",

                airlines,

                default=airlines,

                key="network_airlines"
            )

        with col2:

            selected_aircraft = st.multiselect(

                "Flugzeugtypen anzeigen",

                aircraft,

                default=aircraft,

                key="network_aircraft"
            )

        # ----------------------------------------------------
        # AIRLINE-FARBEN
        # ----------------------------------------------------

        st.subheader(
            "Routenfarben"
        )

        st.caption(

            "Lege hier für jede Airline eine eigene "
            "Farbe für die Kartenrouten fest."
        )

        # Nur Airlines anzeigen, die aktuell
        # im Filter ausgewählt sind.

        color_airlines = [

            airline_name

            for airline_name in airlines

            if airline_name in selected_airlines
        ]

        if color_airlines:

            # Maximal 4 Farben pro Reihe

            for start in range(
                0,
                len(color_airlines),
                4
            ):

                row_airlines = color_airlines[
                    start:start + 4
                ]

                color_columns = st.columns(
                    len(row_airlines)
                )

                for column, airline_name in zip(

                    color_columns,

                    row_airlines

                ):

                    with column:

                        current_color = (
                            st.session_state
                            .airline_colors
                            .get(
                                airline_name,
                                "#38BDF8"
                            )
                        )

                        st.markdown(

                            f"""
                            <div class="airline-color-card">
                                <strong>
                                    {airline_name}
                                </strong>
                            </div>
                            """,

                            unsafe_allow_html=True
                        )

                        new_color = st.color_picker(

                            f"Farbe für {airline_name}",

                            current_color,

                            key=(
                                f"airline_color_"
                                f"{airline_name}"
                            )
                        )

                        st.session_state.airline_colors[
                            airline_name
                        ] = new_color

        else:

            st.info(
                "Wähle mindestens eine Airline aus."
            )

        st.divider()

        # ----------------------------------------------------
        # FILTER ANWENDEN
        # ----------------------------------------------------

        filtered = flights[

            flights["airline"].isin(
                selected_airlines
            )

            &

            flights["aircraft"].isin(
                selected_aircraft
            )
        ]

        # ----------------------------------------------------
        # METRIKEN
        # ----------------------------------------------------

        m1, m2, m3, m4 = st.columns(4)

        with m1:

            st.metric(
                "Flüge",
                len(filtered)
            )

        with m2:

            st.metric(

                "Strecken",

                filtered[
                    [
                        "departure",
                        "arrival"
                    ]
                ]
                .drop_duplicates()
                .shape[0]
            )

        with m3:

            st.metric(

                "Flughäfen",

                len(

                    set(
                        filtered["departure"]
                    )

                    |

                    set(
                        filtered["arrival"]
                    )
                )
            )

        with m4:

            st.metric(

                "Kilometer",

                f"{filtered['distance'].sum():,.0f}"
            )

        st.divider()

        # ----------------------------------------------------
        # ROUTEN UND FLUGHÄFEN
        # ----------------------------------------------------

        routes = []

        airports = {}

        for _, flight in filtered.iterrows():

            dep = get_airport(

                flight["departure"]
            )

            arr = get_airport(

                flight["arrival"]
            )

            if not dep or not arr:

                continue

            # ------------------------------------------------
            # AIRLINE-FARBE
            # ------------------------------------------------

            airline_name = flight["airline"]

            color_hex = (

                st.session_state
                .airline_colors
                .get(

                    airline_name,

                    "#38BDF8"
                )
            )

            color_rgb = hex_to_rgb(
                color_hex
            )

            routes.append({

                "from_lon":
                    dep["longitude"],

                "from_lat":
                    dep["latitude"],

                "to_lon":
                    arr["longitude"],

                "to_lat":
                    arr["latitude"],

                "airline":
                    flight["airline"],

                "flight_number":
                    flight["flight_number"],

                "aircraft":
                    flight["aircraft"],

                "departure":
                    flight["departure"],

                "arrival":
                    flight["arrival"],

                "date":
                    flight["date"],

                "distance":
                    flight["distance"],

                "color":
                    color_rgb
            })

            airports[
                flight["departure"]
            ] = dep

            airports[
                flight["arrival"]
            ] = arr

        routes_df = pd.DataFrame(
            routes
        )

        if not routes_df.empty:

            # ------------------------------------------------
            # ROUTEN
            # ------------------------------------------------

            route_layer = pdk.Layer(

                "ArcLayer",

                data=routes_df,

                get_source_position=[

                    "from_lon",
                    "from_lat"
                ],

                get_target_position=[

                    "to_lon",
                    "to_lat"
                ],

                get_source_color=[

                    "color[0]",
                    "color[1]",
                    "color[2]",
                    220
                ],

                get_target_color=[

                    "color[0]",
                    "color[1]",
                    "color[2]",
                    220
                ],

                get_width=4,

                pickable=True,

                auto_highlight=True
            )

            # ------------------------------------------------
            # KARTE
            # ------------------------------------------------

            deck = pdk.Deck(

                layers=[
