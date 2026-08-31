import streamlit as st
import sqlite3
import pandas as pd
import pydeck as pdk
import requests
import io
import math
import html
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
    --text: #f8fafc;
    --muted: #94a3b8;
    --accent: #38bdf8;
}

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
        var(--background);

    color: var(--text);
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
        );

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
   NORMALE TEXTE
   ============================================================ */

p,
label,
.stMarkdown,
.stCaption {
    color: #f1f5f9;
}


/* ============================================================
   METRICS
   ============================================================ */

div[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            #111827,
            #0f172a
        );

    border: 1px solid #263247;
    padding: 18px;
    border-radius: 14px;

    box-shadow:
        0 8px 25px rgba(0, 0, 0, 0.18);
}

div[data-testid="stMetric"]:hover {
    border-color: #334155;
}

div[data-testid="stMetric"] label {
    color: #f8fafc !important;
    font-weight: 600 !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 800 !important;
}

div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    color: #ffffff !important;
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
        );

    color: #f8fafc;

    font-weight: 600;

    transition:
        all 0.15s ease;
}

.stButton > button:hover {
    border-color: #38bdf8;

    background:
        linear-gradient(
            135deg,
            #164e63,
            #1e293b
        );

    color: white;
}

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
   EINGABEFELDER
   ============================================================ */

div[data-baseweb="input"],
div[data-baseweb="select"],
textarea {
    border-radius: 9px !important;
}

div[data-baseweb="select"] > div {
    border-radius: 9px;
}


/* ============================================================
   MULTISELECT
   ============================================================ */

/* Das gesamte Airline-Auswahlfeld */
[data-testid="stMultiSelect"] > div {
    background-color: #ffffff !important;
    border-radius: 9px !important;
}

/* Innerer Bereich */
[data-testid="stMultiSelect"] > div > div {
    background-color: #ffffff !important;
    border-color: #cbd5e1 !important;
    box-shadow: none !important;
}

/* Ausgewählte Airline-Tags */
[data-baseweb="tag"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 6px !important;
}

/* Text innerhalb der Airline-Tags */
[data-baseweb="tag"] span {
    color: #111827 !important;
    font-weight: 600 !important;
}

/* X zum Entfernen */
[data-baseweb="tag"] svg {
    color: #475569 !important;
}


/* ============================================================
   SELECTBOX
   ============================================================ */

[data-baseweb="select"] {
    color: #111827;
}

[data-baseweb="select"] input {
    color: #111827 !important;
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
   ALERTS
   ============================================================ */

div[data-testid="stAlert"] {
    border-radius: 10px;
}


/* ============================================================
   SCROLLBAR
   ============================================================ */

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #0b1120;
}

::-webkit-scrollbar-thumb {
    background: #263247;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #334155;
}


/* ============================================================
   DASHBOARD CARDS
   ============================================================ */

.dashboard-card {
    background:
        linear-gradient(
            145deg,
            #111827,
            #0f172a
        );

    border: 1px solid #263247;

    border-radius: 14px;

    padding: 22px;

    min-height: 120px;

    box-shadow:
        0 8px 25px rgba(0, 0, 0, 0.18);
}

.dashboard-card:hover {
    border-color: #334155;
}

.dashboard-card-title {
    color: #cbd5e1;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 8px;
}

.dashboard-card-value {
    color: #ffffff;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.1;
}


/* ============================================================
   LEGENDE
   ============================================================ */

.route-legend-wrapper {
    background: #111827;
    border: 1px solid #263247;
    border-radius: 12px;
    padding: 16px 18px;
    margin-top: 15px;
    margin-bottom: 15px;
}

.route-legend-title {
    color: #f8fafc;
    font-size: 0.95rem;
    font-weight: 700;
    margin-bottom: 14px;
}

.route-legend-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(180px, 1fr));
    gap: 10px 20px;
}

.route-legend-item {
    display: flex;
    align-items: center;
    gap: 10px;
    min-height: 28px;
}

.route-legend-color {
    width: 18px;
    height: 18px;
    min-width: 18px;
    border-radius: 5px;
    border: 1px solid rgba(255,255,255,0.25);
    box-shadow:
        0 0 8px rgba(255,255,255,0.05);
}

.route-legend-name {
    color: #f8fafc;
    font-size: 0.9rem;
    font-weight: 500;
}


/* ============================================================
   COLOR PICKER
   ============================================================ */

div[data-testid="stColorPicker"] {
    margin-bottom: 4px;
}


/* ============================================================
   FARBPICKER BESCHRIFTUNG
   ============================================================ */

div[data-testid="stColorPicker"] label {
    color: #f8fafc !important;
    font-weight: 600 !important;
}


/* ============================================================
   SIDEBAR TEXT
   ============================================================ */

section[data-testid="stSidebar"] * {
    color: #f1f5f9;
}


/* ============================================================
   INPUT TEXT
   ============================================================ */

input,
textarea {
    color: #f8fafc !important;
}


/* ============================================================
   PLACEHOLDER
   ============================================================ */

input::placeholder,
textarea::placeholder {
    color: #94a3b8 !important;
}


/* ============================================================
   FILE / DOWNLOAD ELEMENTE
   ============================================================ */

[data-testid="stDownloadButton"] button {
    color: #f8fafc !important;
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

        "latitude_deg": "latitude",
        "longitude_deg": "longitude",
        "elevation_ft": "elevation"
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

    if not icao:
        return None

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
            str(icao).upper()
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

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))

    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

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

    "Lufthansa": "#0050A4",
    "Eurowings": "#B4005A",
    "Ryanair": "#0064C8",
    "easyJet": "#FF6400",
    "British Airways": "#3250BE",
    "Air France": "#3C5AD2",
    "KLM": "#0096DC",
    "Emirates": "#DC1E1E",
    "Qatar Airways": "#820050",
    "Turkish Airlines": "#DC0000",
    "United Airlines": "#005AB4",
    "American Airlines": "#0050AA",
    "Delta Air Lines": "#C80032",
    "Singapore Airlines": "#FA9600",
    "Qantas": "#C80000",
    "SWISS": "#E00000",
    "Swiss": "#E00000",
    "Austrian Airlines": "#D00000",
    "Finnair": "#0066CC",
    "Iberia": "#D80027",
    "Vueling": "#FF6600",
    "Wizz Air": "#C5007D",
    "Air Baltic": "#55AADD",
    "Norwegian": "#D40000",
    "Condor": "#FFCC00",
    "TUI": "#E00055"
}


EXTRA_COLORS = [

    "#38BDF8",
    "#A855F7",
    "#22C55E",
    "#EAB308",
    "#F43F5E",
    "#0EA5E9",
    "#8B5CF6",
    "#14B8A6",
    "#F97316",
    "#EC4899",
    "#84CC16",
    "#06B6D4",
    "#6366F1",
    "#D946EF",
    "#10B981",
    "#F59E0B"
]


def get_default_color(airline):

    if airline in DEFAULT_AIRLINE_COLORS:

        return DEFAULT_AIRLINE_COLORS[
            airline
        ]

    index = (
        abs(hash(str(airline)))
        % len(EXTRA_COLORS)
    )

    return EXTRA_COLORS[index]


# ============================================================
# AIRLINE-FARBEN SESSION STATE
# ============================================================

if "airline_colors" not in st.session_state:

    st.session_state.airline_colors = {}


def get_color_for_airline(airline):

    if airline not in st.session_state.airline_colors:

        st.session_state.airline_colors[
            airline
        ] = get_default_color(airline)

    return st.session_state.airline_colors[
        airline
    ]


# ============================================================
# HEX → RGB
# ============================================================

def hex_to_rgb(hex_color):

    hex_color = str(
        hex_color
    ).lstrip("#")

    if len(hex_color) != 6:
        return [128, 128, 128]

    try:

        return [

            int(
                hex_color[0:2],
                16
            ),

            int(
                hex_color[2:4],
                16
            ),

            int(
                hex_color[4:6],
                16
            )
        ]

    except ValueError:

        return [128, 128, 128]


# ============================================================
# FARBLEGENDE
# ============================================================

def render_route_legend(airlines):

    if not airlines:
        return

    legend_items = []

    for airline in sorted(airlines):

        color = get_color_for_airline(
            airline
        )

        safe_airline = html.escape(
            str(airline)
        )

        safe_color = html.escape(
            str(color)
        )

        legend_items.append(
            f"""
            <div class="route-legend-item">
                <div
                    class="route-legend-color"
                    style="background-color:{safe_color};"
                ></div>
                <div class="route-legend-name">
                    {safe_airline}
                </div>
            </div>
            """
        )

    legend_html = f"""
    <div class="route-legend-wrapper">
        <div class="route-legend-title">
            Routenfarben
        </div>

        <div class="route-legend-grid">
            {"".join(legend_items)}
        </div>
    </div>
    """

    # WICHTIG:
    # st.html rendert HTML als HTML.
    # Dadurch werden die HTML-Tags nicht
    # als sichtbarer Text angezeigt.

    st.html(legend_html)


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
        "Dashboard",
        "Streckennetz",
        "Flug hinzufügen",
        "Flugbuch",
        "Statistik",
        "Flughafendatenbank"
    ],
    index=0
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.title(
        "Dashboard"
    )

    st.caption(
        "Übersicht über dein persönliches Flugnetz"
    )

    flights = get_flights()

    if flights.empty:

        st.info(
            "Noch keine Flüge vorhanden. "
            "Füge deinen ersten Flug hinzu, um "
            "dein Dashboard zu füllen."
        )

        st.divider()

        st.subheader(
            "Dein Flugnetz"
        )

        st.write(
            "Sobald du Flüge speicherst, werden hier "
            "die wichtigsten Informationen angezeigt."
        )

    else:

        total_flights = len(
            flights
        )

        total_distance = flights[
            "distance"
        ].fillna(0).sum()

        airport_count = len(

            set(
                flights["departure"]
                .dropna()
            )

            |

            set(
                flights["arrival"]
                .dropna()
            )
        )

        route_count = (

            flights[
                [
                    "departure",
                    "arrival"
                ]
            ]

            .drop_duplicates()

            .shape[0]
        )

        airline_count = (

            flights["airline"]
            .dropna()
            .astype(str)
            .nunique()
        )


        # ----------------------------------------------------
        # HAUPTKENNZAHLEN
        # ----------------------------------------------------

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "Flüge",
                f"{total_flights:,}"
            )

        with c2:

            st.metric(
                "Strecken",
                f"{route_count:,}"
            )

        with c3:

            st.metric(
                "Flughäfen",
                f"{airport_count:,}"
            )

        with c4:

            st.metric(
                "Kilometer",
                f"{total_distance:,.0f}"
            )


        st.divider()


        # ----------------------------------------------------
        # ZUSATZINFORMATIONEN
        # ----------------------------------------------------

        left, right = st.columns(2)


        with left:

            st.subheader(
                "Airlines"
            )

            st.write(
                f"Du bist bisher mit "
                f"**{airline_count} Airlines** geflogen."
            )

            airline_counts = (

                flights["airline"]
                .value_counts()
                .head(5)
            )

            for airline_name, count in airline_counts.items():

                color = get_color_for_airline(
                    airline_name
                )

                safe_color = html.escape(
                    color
                )

                safe_name = html.escape(
                    str(airline_name)
                )

                st.html(
                    f"""
                    <div style="
                        display:flex;
                        align-items:center;
                        justify-content:space-between;
                        background:#111827;
                        border:1px solid #263247;
                        border-radius:10px;
                        padding:10px 13px;
                        margin-bottom:7px;
                    ">
                        <div style="
                            display:flex;
                            align-items:center;
                            gap:10px;
                            color:#f8fafc;
                            font-weight:600;
                        ">
                            <div style="
                                width:12px;
                                height:12px;
                                border-radius:4px;
                                background:{safe_color};
                            "></div>

                            {safe_name}
                        </div>

                        <div style="
                            color:#ffffff;
                            font-weight:700;
                        ">
                            {count}
                        </div>
                    </div>
                    """
                )


        with right:

            st.subheader(
                "Letzte Flüge"
            )

            recent = flights.head(5)

            for _, flight in recent.iterrows():

                airline_name = html.escape(
                    str(flight["airline"])
                )

                departure = html.escape(
                    str(flight["departure"])
                )

                arrival = html.escape(
                    str(flight["arrival"])
                )

                flight_date = html.escape(
                    str(flight["date"])
                )

                color = html.escape(
                    get_color_for_airline(
                        str(flight["airline"])
                    )
                )

                st.html(
                    f"""
                    <div style="
                        display:flex;
                        align-items:center;
                        gap:12px;
                        background:#111827;
                        border:1px solid #263247;
                        border-radius:10px;
                        padding:11px 13px;
                        margin-bottom:7px;
                    ">

                        <div style="
                            width:4px;
                            min-width:4px;
                            height:42px;
                            border-radius:5px;
                            background:{color};
                        "></div>

                        <div style="
                            flex:1;
                        ">

                            <div style="
                                color:#f8fafc;
                                font-weight:700;
                            ">
                                {departure} → {arrival}
                            </div>

                            <div style="
                                color:#94a3b8;
                                font-size:0.82rem;
                                margin-top:3px;
                            ">
                                {airline_name}
                                ·
                                {flight_date}
                            </div>

                        </div>

                    </div>
                    """
                )


        st.divider()


        # ----------------------------------------------------
        # MEISTGENUTZTE FLUGHÄFEN
        # ----------------------------------------------------

        st.subheader(
            "Häufigste Flughäfen"
        )

        airport_series = pd.concat(
            [
                flights["departure"],
                flights["arrival"]
            ]
        )

        airport_counts = (
            airport_series
            .value_counts()
            .head(8)
        )

        airport_columns = st.columns(
            min(4, max(1, len(airport_counts)))
        )

        for index, (airport, count) in enumerate(
            airport_counts.items()
        ):

            with airport_columns[
                index % len(airport_columns)
            ]:

                st.metric(
                    str(airport),
                    int(count)
                )


# ============================================================
# FLUGHAFENDATENBANK
# ============================================================

elif page == "Flughafendatenbank":

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

                airline.strip(),

                flight_number.strip(),

                aircraft.strip(),

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
        # FILTER
        # ----------------------------------------------------

        col1, col2 = st.columns(2)


        airlines = sorted(
            flights["airline"]
            .dropna()
            .astype(str)
            .unique()
        )


        aircraft_types = sorted(
            flights["aircraft"]
            .dropna()
            .astype(str)
            .unique()
        )


        with col1:

            selected_airlines = st.multiselect(
                "Airlines",
                airlines,
                default=airlines,
                key="network_airlines"
            )


        with col2:

            selected_aircraft = st.multiselect(
                "Flugzeugtypen",
                aircraft_types,
                default=aircraft_types,
                key="network_aircraft"
            )


        # ----------------------------------------------------
        # FARBEN
        # ----------------------------------------------------

        if selected_airlines:

            st.subheader(
                "Routenfarben"
            )

            st.caption(
                "Wähle die Farbe für die jeweilige Airline."
            )


            number_of_columns = min(
                4,
                max(
                    1,
                    len(selected_airlines)
                )
            )


            color_columns = st.columns(
                number_of_columns
            )


            for index, airline_name in enumerate(
                selected_airlines
            ):

                column = color_columns[
                    index % number_of_columns
                ]

                with column:

                    current_color = (
                        get_color_for_airline(
                            airline_name
                        )
                    )


                    new_color = st.color_picker(
                        airline_name,
                        value=current_color,
                        key=(
                            "airline_color_"
                            + airline_name
                        )
                    )


                    st.session_state.airline_colors[
                        airline_name
                    ] = new_color


        # ----------------------------------------------------
        # FILTER DATEN
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
        # ROUTEN ERSTELLEN
        # ----------------------------------------------------

        routes = []


        for _, flight in filtered.iterrows():

            dep = get_airport(
                flight["departure"]
            )

            arr = get_airport(
                flight["arrival"]
            )


            if not dep or not arr:
                continue


            airline_color = (
                get_color_for_airline(
                    flight["airline"]
                )
            )


            rgb_color = hex_to_rgb(
                airline_color
            )


            routes.append({

                "from_lon":
                    float(dep["longitude"]),

                "from_lat":
                    float(dep["latitude"]),

                "to_lon":
                    float(arr["longitude"]),

                "to_lat":
                    float(arr["latitude"]),

                "airline":
                    str(flight["airline"]),

                "flight_number":
                    str(
                        flight["flight_number"]
                        or ""
                    ),

                "aircraft":
                    str(flight["aircraft"]),

                "departure":
                    str(flight["departure"]),

                "arrival":
                    str(flight["arrival"]),

                "date":
                    str(flight["date"]),

                "distance":
                    round(
                        float(
                            flight["distance"]
                            or 0
                        ),
                        0
                    ),

                "r":
                    rgb_color[0],

                "g":
                    rgb_color[1],

                "b":
                    rgb_color[2]
            })


        routes_df = pd.DataFrame(
            routes
        )


        # ----------------------------------------------------
        # KARTE
        # ----------------------------------------------------

        if not routes_df.empty:

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
                    "r",
                    "g",
                    "b",
                    240
                ],

                get_target_color=[
                    "r",
                    "g",
                    "b",
                    240
                ],

                get_width=4,

                pickable=True,

                auto_highlight=True
            )


            deck = pdk.Deck(

                layers=[
                    route_layer
                ],

                initial_view_state=pdk.ViewState(

                    latitude=25,

                    longitude=10,

                    zoom=1.25,

                    pitch=20
                ),

                map_style=(
                    "https://basemaps.cartocdn.com/"
                    "gl/dark-matter-gl-style/"
                    "style.json"
                ),

                tooltip={

                    "html": """
                        <div style="
                            background:#111827;
                            color:#f8fafc;
                            padding:12px 14px;
                            border-radius:8px;
                            border:1px solid #334155;
                            font-family:Arial,sans-serif;
                            line-height:1.5;
                        ">

                            <div style="
                                font-size:16px;
                                font-weight:700;
                                margin-bottom:5px;
                            ">
                                {flight_number}
                            </div>

                            <div>
                                Airline: {airline}
                            </div>

                            <div>
                                Flugzeug: {aircraft}
                            </div>

                            <div>
                                Route:
                                {departure} → {arrival}
                            </div>

                            <div>
                                Datum: {date}
                            </div>

                            <div>
                                Distanz: {distance} km
                            </div>

                        </div>
                    """
                }
            )


            st.pydeck_chart(
                deck,
                use_container_width=True
            )


            # ------------------------------------------------
            # FARBLEGENDE
            # ------------------------------------------------

            render_route_legend(
                selected_airlines
            )


        else:

            st.warning(
                "Keine Kartenrouten vorhanden."
            )


# ============================================================
# FLUGBUCH
# ============================================================

elif page == "Flugbuch":

    st.title(
        "Mein Flugbuch"
    )

    flights = get_flights()


    if flights.empty:

        st.info(
            "Noch keine Flüge gespeichert."
        )

    else:

        search = st.text_input(
            "Flug suchen",
            placeholder=(
                "Airline, Flugnummer, "
                "Flughafen oder Flugzeug"
            )
        )


        display = flights.copy()


        if search:

            search_lower = search.lower()


            mask = (

                display
                .astype(str)
                .apply(

                    lambda column:

                    column.str
                    .lower()
                    .str.contains(
                        search_lower,
                        na=False
                    )
                )

                .any(axis=1)
            )


            display = display[
                mask
            ]


        display = display.rename(

            columns={

                "date":
                    "Datum",

                "airline":
                    "Airline",

                "flight_number":
                    "Flugnummer",

                "aircraft":
                    "Flugzeug",

                "departure":
                    "Abflug",

                "arrival":
                    "Ziel",

                "flight_time":
                    "Flugzeit",

                "distance":
                    "Distanz",

                "notes":
                    "Notizen"
            }
        )


        display = display.drop(

            columns=[
                "id",
                "created_at"
            ],

            errors="ignore"
        )


        st.dataframe(

            display,

            use_container_width=True,

            hide_index=True
        )


        st.divider()


        st.subheader(
            "Flug löschen"
        )


        options = {

            (
                f"{row['date']} | "
                f"{row['flight_number']} | "
                f"{row['departure']} → "
                f"{row['arrival']} | "
                f"{row['aircraft']}"
            ):

                row["id"]

            for _, row
            in flights.iterrows()
        }


        selected = st.selectbox(

            "Flug auswählen",

            list(options.keys())
        )


        if st.button(
            "Flug löschen"
        ):

            delete_flight(
                options[selected]
            )

            st.success(
                "Flug wurde gelöscht."
            )

            st.rerun()


# ============================================================
# STATISTIK
# ============================================================

elif page == "Statistik":

    st.title(
        "Flugstatistik"
    )

    flights = get_flights()


    if flights.empty:

        st.info(
            "Noch keine Flüge vorhanden."
        )

    else:

        total_flights = len(
            flights
        )


        total_distance = flights[
            "distance"
        ].sum()


        airport_count = len(

            set(
                flights["departure"]
            )

            |

            set(
                flights["arrival"]
            )
        )


        route_count = (

            flights[
                [
                    "departure",
                    "arrival"
                ]
            ]

            .drop_duplicates()

            .shape[0]
        )


        # ----------------------------------------------------
        # KENNZAHLEN
        # ----------------------------------------------------

        c1, c2, c3, c4 = st.columns(4)


        with c1:

            st.metric(
                "Flüge",
                total_flights
            )


        with c2:

            st.metric(
                "Strecken",
                route_count
            )


        with c3:

            st.metric(
                "Kilometer",
                f"{total_distance:,.0f}"
            )


        with c4:

            st.metric(
                "Flughäfen",
                airport_count
            )


        st.divider()


        # ----------------------------------------------------
        # ROUTEN
        # ----------------------------------------------------

        st.subheader(
            "Häufigste Strecken"
        )


        routes = (

            flights

            .groupby(
                [
                    "departure",
                    "arrival"
                ]
            )

            .size()

            .reset_index(
                name="Flüge"
            )

            .sort_values(
                "Flüge",
                ascending=False
            )
        )


        routes["Strecke"] = (

            routes["departure"]

            + " → "

            + routes["arrival"]
        )


        st.dataframe(

            routes[
                [
                    "Strecke",
                    "Flüge"
                ]
            ],

            use_container_width=True,

            hide_index=True
        )
