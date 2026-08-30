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
# MODERNES DESIGN
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html,
    body,
    [class*="css"] {
        font-family: "Inter", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 15% 5%,
                rgba(20, 90, 180, 0.16),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(0, 170, 255, 0.08),
                transparent 25%
            ),
            #080b11;
        color: #f5f7fa;
    }

    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0a0f17 0%,
                #080c13 100%
            );

        border-right:
            1px solid #1d2633;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }

    section[data-testid="stSidebar"] hr {
        border-color: #202a38;
    }

    /* ======================================================
       TITLES
       ====================================================== */

    h1 {
        font-size: 38px !important;
        font-weight: 800 !important;
        letter-spacing: -1.5px;
        color: #ffffff !important;
    }

    h2 {
        font-weight: 750 !important;
        color: #ffffff !important;
    }

    h3 {
        font-weight: 700 !important;
        color: #f1f5f9 !important;
    }

    /* ======================================================
       METRICS
       ====================================================== */

    [data-testid="stMetric"] {

        background:
            linear-gradient(
                145deg,
                rgba(20, 28, 40, 0.96),
                rgba(12, 17, 26, 0.96)
            );

        border:
            1px solid #222e3e;

        border-radius: 18px;

        padding:
            20px 20px 18px 20px;

        box-shadow:
            0 10px 35px
            rgba(0, 0, 0, 0.18);

        transition:
            transform 0.2s ease,
            border-color 0.2s ease;
    }

    [data-testid="stMetric"]:hover {

        transform:
            translateY(-2px);

        border-color:
            #285b91;
    }

    [data-testid="stMetricLabel"] {

        color: #718096 !important;

        font-size: 10px !important;

        font-weight: 700 !important;

        text-transform:
            uppercase;

        letter-spacing:
            1px;
    }

    [data-testid="stMetricValue"] {

        color: #ffffff !important;

        font-size: 28px !important;

        font-weight: 800 !important;
    }

    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {

        background:
            linear-gradient(
                135deg,
                #1479ff,
                #0755bd
            );

        color: white;

        border:
            1px solid
            rgba(80, 160, 255, 0.25);

        border-radius:
            11px;

        font-weight:
            700;

        min-height:
            42px;

        transition:
            all 0.2s ease;

        box-shadow:
            0 6px 18px
            rgba(0, 102, 255, 0.16);
    }

    .stButton > button:hover {

        background:
            linear-gradient(
                135deg,
                #2d8aff,
                #1266d7
            );

        border-color:
            rgba(80, 160, 255, 0.45);

        transform:
            translateY(-1px);

        box-shadow:
            0 8px 24px
            rgba(0, 102, 255, 0.25);
    }

    /* ======================================================
       INPUTS
       ====================================================== */

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {

        background-color:
            #0d141f !important;

        color:
            #ffffff !important;

        border:
            1px solid #263448 !important;

        border-radius:
            11px !important;
    }

    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {

        border-color:
            #287eff !important;

        box-shadow:
            0 0 0 1px
            rgba(40, 126, 255, 0.25);
    }

    /* ======================================================
       SELECTBOX / MULTISELECT
       ====================================================== */

    div[data-baseweb="select"] > div {

        background-color:
            #0d141f !important;

        border:
            1px solid #263448 !important;

        border-radius:
            11px !important;

        color:
            white !important;
    }

    /* ======================================================
       DATAFRAME
       ====================================================== */

    [data-testid="stDataFrame"] {

        border:
            1px solid #202b3a;

        border-radius:
            14px;

        overflow:
            hidden;
    }

    /* ======================================================
       ALERTS
       ====================================================== */

    .stAlert {

        background:
            rgba(18, 28, 42, 0.9);

        border-radius:
            12px;

        border:
            1px solid #26364c;
    }

    /* ======================================================
       DIVIDER
       ====================================================== */

    hr {

        border-color:
            #1b2635 !important;
    }

    /* ======================================================
       CUSTOM ELEMENTS
       ====================================================== */

    .brand {

        padding:
            5px 0 18px 0;
    }

    .brand-title {

        font-size:
            21px;

        font-weight:
            800;

        color:
            #ffffff;

        letter-spacing:
            -0.6px;
    }

    .brand-subtitle {

        font-size:
            9px;

        color:
            #65758a;

        font-weight:
            700;

        letter-spacing:
            1.4px;

        margin-top:
            5px;
    }

    .page-header {

        padding:
            5px 0 25px 0;
    }

    .page-kicker {

        display:
            inline-block;

        color:
            #4da0ff;

        background:
            rgba(30, 125, 255, 0.10);

        border:
            1px solid
            rgba(50, 140, 255, 0.20);

        border-radius:
            20px;

        padding:
            5px 10px;

        font-size:
            9px;

        font-weight:
            800;

        letter-spacing:
            1px;

        text-transform:
            uppercase;

        margin-bottom:
            10px;
    }

    .page-title {

        font-size:
            42px;

        font-weight:
            800;

        letter-spacing:
            -1.8px;

        color:
            white;

        line-height:
            1.05;
    }

    .page-description {

        color:
            #78879b;

        font-size:
            14px;

        margin-top:
            8px;
    }

    .section-label {

        font-size:
            10px;

        color:
            #63748a;

        font-weight:
            800;

        letter-spacing:
            1.3px;

        text-transform:
            uppercase;

        margin-bottom:
            12px;
    }

    .flight-card {

        background:
            linear-gradient(
                145deg,
                #121a26,
                #0d131d
            );

        border:
            1px solid #202d3e;

        border-radius:
            16px;

        padding:
            18px;

        margin-bottom:
            12px;

        transition:
            all 0.2s ease;
    }

    .flight-card:hover {

        border-color:
            #2c496b;

        transform:
            translateY(-1px);
    }

    .route {

        font-size:
            20px;

        font-weight:
            800;

        color:
            #ffffff;

        letter-spacing:
            -0.5px;
    }

    .route-arrow {

        color:
            #388cff;

        padding:
            0 5px;
    }

    .flight-meta {

        color:
            #738399;

        font-size:
            12px;

        margin-top:
            8px;
    }

    .stat-card {

        background:
            linear-gradient(
                145deg,
                rgba(18, 27, 40, 0.95),
                rgba(11, 16, 25, 0.95)
            );

        border:
            1px solid #202d3e;

        border-radius:
            16px;

        padding:
            20px;

        height:
            100%;
    }

    .stat-title {

        color:
            #718197;

        font-size:
            10px;

        font-weight:
            800;

        letter-spacing:
            1px;

        text-transform:
            uppercase;
    }

    .stat-value {

        color:
            #ffffff;

        font-size:
            27px;

        font-weight:
            800;

        margin-top:
            7px;
    }

    .stat-small {

        color:
            #63748a;

        font-size:
            11px;

        margin-top:
            4px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATENBANK
# ============================================================

def get_connection():

    return sqlite3.connect(
        DB_FILE
    )


def init_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
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
        """
    )

    cursor.execute(
        """
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
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS database_info (

            key TEXT PRIMARY KEY,

            value TEXT
        )
        """
    )

    conn.commit()

    conn.close()


# ============================================================
# AIRPORT DATENBANK
# ============================================================

def download_airports():

    try:

        response = requests.get(
            AIRPORT_DATABASE_URL,
            timeout=60
        )

        response.raise_for_status()

        return pd.read_csv(
            io.BytesIO(
                response.content
            )
        )

    except Exception as error:

        st.error(
            f"Fehler beim Herunterladen: {error}"
        )

        return None


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

    df = df[
        available
    ].copy()

    df = df.rename(

        columns={

            "latitude_deg":
                "latitude",

            "longitude_deg":
                "longitude",

            "elevation_ft":
                "elevation"
        }
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
        df["type"].isin(
            airport_types
        )
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

    cursor.execute(

        """
        INSERT OR REPLACE INTO database_info
        (key, value)
        VALUES (?, ?)
        """,

        (
            "airports_updated",
            str(
                pd.Timestamp.now()
            )
        )
    )

    conn.commit()

    conn.close()

    return True


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
# AIRPORT SUCHE
# ============================================================

def search_airports(search):

    conn = get_connection()

    search = search.upper().strip()

    like = f"%{search}%"

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

            UPPER(ident)
            LIKE ?

            OR UPPER(
                COALESCE(
                    iata_code,
                    ''
                )
            )
            LIKE ?

            OR UPPER(name)
            LIKE ?

            OR UPPER(
                COALESCE(
                    municipality,
                    ''
                )
            )
            LIKE ?

        ORDER BY

            CASE

                WHEN UPPER(ident) = ?
                THEN 0

                WHEN UPPER(
                    COALESCE(
                        iata_code,
                        ''
                    )
                ) = ?

                THEN 1

                ELSE 2

            END,

            name

        LIMIT 50
    """

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
# FLÜGE
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

    cursor.execute(

        """
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
        """,

        (

            flight_date,
            airline,
            flight_number,
            aircraft,
            departure,
            arrival,
            flight_time,
            distance,
            notes
        )
    )

    conn.commit()

    conn.close()


def get_flights():

    conn = get_connection()

    df = pd.read_sql_query(

        """
        SELECT *

        FROM flights

        ORDER BY
            date DESC,
            id DESC
        """,

        conn
    )

    conn.close()

    return df


def delete_flight(
    flight_id
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        "DELETE FROM flights WHERE id = ?",

        (
            flight_id,
        )
    )

    conn.commit()

    conn.close()


# ============================================================
# DISTANZ
# ============================================================

def calculate_distance(

    lat1,
    lon1,
    lat2,
    lon2

):

    radius = 6371.0

    lat1 = math.radians(
        lat1
    )

    lon1 = math.radians(
        lon1
    )

    lat2 = math.radians(
        lat2
    )

    lon2 = math.radians(
        lon2
    )

    dlat = lat2 - lat1

    dlon = lon2 - lon1

    a = (

        math.sin(
            dlat / 2
        ) ** 2

        +

        math.cos(lat1)

        *

        math.cos(lat2)

        *

        math.sin(
            dlon / 2
        ) ** 2
    )

    c = 2 * math.atan2(

        math.sqrt(a),

        math.sqrt(
            1 - a
        )
    )

    return radius * c


# ============================================================
# AIRLINE FARBEN
# ============================================================

AIRLINE_COLORS = {

    "Lufthansa":
        [0, 90, 180],

    "Eurowings":
        [180, 0, 90],

    "Ryanair":
        [0, 100, 200],

    "easyJet":
        [255, 100, 0],

    "British Airways":
        [50, 80, 190],

    "Air France":
        [60, 90, 210],

    "KLM":
        [0, 150, 220],

    "Emirates":
        [220, 30, 30],

    "Qatar Airways":
        [130, 0, 80],

    "Turkish Airlines":
        [220, 0, 0],

    "United Airlines":
        [0, 90, 180],

    "American Airlines":
        [0, 80, 170],

    "Delta Air Lines":
        [200, 0, 50],

    "Singapore Airlines":
        [250, 150, 0],

    "Qantas":
        [200, 0, 0]
}


DEFAULT_COLOR = [
    80,
    150,
    255
]


def get_airline_color(
    airline
):

    return AIRLINE_COLORS.get(

        airline,

        DEFAULT_COLOR
    )


# ============================================================
# INITIALISIERUNG
# ============================================================

init_database()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(

    """
    <div class="brand">

        <div class="brand-title">
            MY FLIGHT NETWORK
        </div>

        <div class="brand-subtitle">
            MSFS 2024 FLIGHT LOGBOOK
        </div>

    </div>
    """,

    unsafe_allow_html=True
)

st.sidebar.divider()

page = st.sidebar.radio(

    "NAVIGATION",

    [

        "Dashboard",

        "Streckennetz",

        "Flug hinzufügen",

        "Flugbuch",

        "Statistik",

        "Flughafendatenbank"

    ]
)

st.sidebar.divider()

st.sidebar.markdown(

    """
    <div style="
        color:#526277;
        font-size:9px;
        font-weight:700;
        letter-spacing:1px;
        text-transform:uppercase;
    ">
        LOCAL STORAGE
    </div>

    <div style="
        color:#8897aa;
        font-size:12px;
        margin-top:5px;
    ">
        SQLite Database
    </div>
    """,

    unsafe_allow_html=True
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    flights = get_flights()

    st.markdown(

        """
        <div class="page-header">

            <div class="page-kicker">
                MSFS 2024
            </div>

            <div class="page-title">
                Your Flight Network
            </div>

            <div class="page-description">
                Dein persönliches Flugbuch,
                Streckennetz und deine Flugstatistiken.
            </div>

        </div>
        """,

        unsafe_allow_html=True
    )

    if flights.empty:

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Flüge",
            "0"
        )

        c2.metric(
            "Flugstunden",
            "0"
        )

        c3.metric(
            "Kilometer",
            "0"
        )

        c4.metric(
            "Flughäfen",
            "0"
        )

        st.divider()

        st.markdown(

            """
            <div class="stat-card">

                <div class="stat-title">
                    Noch keine Flüge
                </div>

                <div class="stat-value">
                    Dein Netzwerk wartet.
                </div>

                <div class="stat-small">
                    Füge deinen ersten MSFS-2024-Flug
                    hinzu, um dein persönliches
                    Streckennetz aufzubauen.
                </div>

            </div>
            """,

            unsafe_allow_html=True
        )

    else:

        total_flights = len(
            flights
        )

        total_hours = flights[
            "flight_time"
        ].sum()

        total_distance = flights[
            "distance"
        ].sum()

        airports = (

            set(
                flights["departure"]
            )

            |

            set(
                flights["arrival"]
            )
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Flüge",
            f"{total_flights:,}"
        )

        c2.metric(
            "Flugstunden",
            f"{total_hours:.1f}"
        )

        c3.metric(
            "Kilometer",
            f"{total_distance:,.0f}"
        )

        c4.metric(
            "Flughäfen",
            f"{len(airports):,}"
        )

        st.divider()

        st.markdown(

            '<div class="section-label">'
            'NETWORK OVERVIEW'
            '</div>',

            unsafe_allow_html=True
        )

        # ====================================================
        # DASHBOARD KARTE
        # ====================================================

        routes = []

        for _, flight in flights.iterrows():

            dep = get_airport(
                flight["departure"]
            )

            arr = get_airport(
                flight["arrival"]
            )

            if not dep or not arr:

                continue

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
                    get_airline_color(
                        flight["airline"]
                    )
            })

        routes_df = pd.DataFrame(
            routes
        )

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

            deck = pdk.Deck(

                layers=[
                    route_layer
                ],

                initial_view_state=pdk.ViewState(

                    latitude=30,

                    longitude=10,

                    zoom=1.45,

                    pitch=20
                ),

                tooltip={

                    "html": """
                        <b>{flight_number}</b><br/>
                        Airline: {airline}<br/>
                        Flugzeug: {aircraft}<br/>
                        Route: {departure} → {arrival}<br/>
                        Datum: {date}<br/>
                        Distanz: {distance} km
                    """,

                    "style": {

                        "backgroundColor":
                            "#101722",

                        "color":
                            "white",

                        "fontSize":
                            "13px",

                        "padding":
                            "12px",

                        "border":
                            "1px solid #26364c"
                    }
                }
            )

            st.pydeck_chart(

                deck,

                use_container_width=True
            )

        st.divider()

        left, right = st.columns(
            [1.4, 1]
        )

        with left:

            st.markdown(

                '<div class="section-label">'
                'RECENT FLIGHTS'
                '</div>',

                unsafe_allow_html=True
            )

            for _, flight in flights.head(
                5
            ).iterrows():

                st.markdown(

                    f"""
                    <div class="flight-card">

                        <div class="route">

                            {flight["departure"]}

                            <span class="route-arrow">
                                →
                            </span>

                            {flight["arrival"]}

                        </div>

                        <div class="flight-meta">

                            {flight["airline"]}
                            &nbsp;&nbsp;·&nbsp;&nbsp;
                            {flight["flight_number"]}
                            &nbsp;&nbsp;·&nbsp;&nbsp;
                            {flight["aircraft"]}
                            &nbsp;&nbsp;·&nbsp;&nbsp;
                            {flight["date"]}

                        </div>

                    </div>
                    """,

                    unsafe_allow_html=True
                )

        with right:

            st.markdown(

                '<div class="section-label">'
                'TOP AIRLINES'
                '</div>',

                unsafe_allow_html=True
            )

            airline_counts = (

                flights[
                    "airline"
                ]

                .value_counts()

                .rename(
                    "Flüge"
                )
            )

            st.dataframe(

                airline_counts.head(
                    8
                ),

                use_container_width=True
            )


# ============================================================
# STRECKENNETZ
# ============================================================

elif page == "Streckennetz":

    st.markdown(

        """
        <div class="page-header">

            <div class="page-kicker">
                NETWORK
            </div>

            <div class="page-title">
                Mein Streckennetz
            </div>

            <div class="page-description">
                Alle deine geflogenen Routen
                auf einer interaktiven Weltkarte.
            </div>

        </div>
        """,

        unsafe_allow_html=True
    )

    flights = get_flights()

    if flights.empty:

        st.info(
            "Noch keine Flüge vorhanden."
        )

    else:

        col1, col2 = st.columns(2)

        airlines = sorted(

            flights[
                "airline"
            ]

            .dropna()

            .unique()
        )

        aircraft = sorted(

            flights[
                "aircraft"
            ]

            .dropna()

            .unique()
        )

        with col1:

            selected_airlines = st.multiselect(

                "AIRLINES",

                airlines,

                default=airlines
            )

        with col2:

            selected_aircraft = st.multiselect(

                "FLUGZEUGE",

                aircraft,

                default=aircraft
            )

        filtered = flights[

            flights[
                "airline"
            ].isin(
                selected_airlines
            )

            &

            flights[
                "aircraft"
            ].isin(
                selected_aircraft
            )
        ]

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "Flüge",
            len(filtered)
        )

        m2.metric(

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

        m3.metric(

            "Flughäfen",

            len(

                set(
                    filtered[
                        "departure"
                    ]
                )

                |

                set(
                    filtered[
                        "arrival"
                    ]
                )
            )
        )

        m4.metric(

            "Kilometer",

            f"{filtered['distance'].sum():,.0f}"
        )

        st.divider()

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
                    get_airline_color(
                        flight["airline"]
                    )
            })

        routes_df = pd.DataFrame(
            routes
        )

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

            deck = pdk.Deck(

                layers=[
                    route_layer
                ],

                initial_view_state=pdk.ViewState(

                    latitude=30,

                    longitude=10,

                    zoom=1.5,

                    pitch=20
                ),

                tooltip={

                    "html": """
                        <b>{flight_number}</b><br/>
                        Airline: {airline}<br/>
                        Flugzeug: {aircraft}<br/>
                        Route: {departure} → {arrival}<br/>
                        Datum: {date}<br/>
                        Distanz: {distance} km
                    """,

                    "style": {

                        "backgroundColor":
                            "#101722",

                        "color":
                            "white",

                        "fontSize":
                            "13px",

                        "padding":
                            "12px"
                    }
                }
            )

            st.pydeck_chart(

                deck,

                use_container_width=True
            )

        else:

            st.warning(
                "Keine Kartenrouten vorhanden."
            )


# ============================================================
# FLUG HINZUFÜGEN
# ============================================================

elif page == "Flug hinzufügen":

    st.markdown(

        """
        <div class="page-header">

            <div class="page-kicker">
                LOG FLIGHT
            </div>

            <div class="page-title">
                Flug hinzufügen
            </div>

            <div class="page-description">
                Speichere deinen nächsten MSFS-2024-Flug
                in deinem persönlichen Flugbuch.
            </div>

        </div>
        """,

        unsafe_allow_html=True
    )

    if not airport_database_exists():

        st.warning(
            "Die Flughafendatenbank ist noch nicht installiert."
        )

        if st.button(
            "Flughafendatenbank laden",
            type="primary"
        ):

            with st.spinner(
                "Flughafendaten werden heruntergeladen..."
            ):

                df = download_airports()

            if df is not None:

                import_airports(
                    df
                )

                st.success(
                    "Flughafendatenbank wurde installiert."
                )

                st.rerun()

        st.stop()

    st.markdown(

        '<div class="section-label">'
        'FLIGHT INFORMATION'
        '</div>',

        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        flight_date = st.date_input(

            "Flugdatum",

            value=date.today()
        )

        airline = st.text_input(

            "Airline",

            placeholder="Lufthansa"
        )

        flight_number = st.text_input(

            "Flugnummer",

            placeholder="LH206"
        )

        aircraft = st.text_input(

            "Flugzeug",

            placeholder="Airbus A320neo"
        )

    with col2:

        st.markdown(

            '<div class="section-label">'
            'ROUTE'
            '</div>',

            unsafe_allow_html=True
        )

        departure_search = st.text_input(

            "Abflughafen",

            placeholder=(
                "ICAO, IATA oder Flughafenname"
            ),

            key="departure_search"
        )

        departure = ""

        if departure_search:

            results = search_airports(
                departure_search
            )

            if not results.empty:

                options = {

                    (
                        f"{row['ident']} | "
                        f"{row['iata_code'] or '-'} | "
                        f"{row['name']} | "
                        f"{row['municipality'] or '-'}"
                    ):
                        row["ident"]

                    for _, row
                    in results.iterrows()
                }

                selected = st.selectbox(

                    "Abflughafen auswählen",

                    list(
                        options.keys()
                    ),

                    key="departure_select"
                )

                departure = options[
                    selected
                ]

            else:

                st.warning(
                    "Kein Flughafen gefunden."
                )

        arrival_search = st.text_input(

            "Zielflughafen",

            placeholder=(
                "ICAO, IATA oder Flughafenname"
            ),

            key="arrival_search"
        )

        arrival = ""

        if arrival_search:

            results = search_airports(
                arrival_search
            )

            if not results.empty:

                options = {

                    (
                        f"{row['ident']} | "
                        f"{row['iata_code'] or '-'} | "
                        f"{row['name']} | "
                        f"{row['municipality'] or '-'}"
                    ):
                        row["ident"]

                    for _, row
                    in results.iterrows()
                }

                selected = st.selectbox(

                    "Zielflughafen auswählen",

                    list(
                        options.keys()
                    ),

                    key="arrival_select"
                )

                arrival = options[
                    selected
                ]

            else:

                st.warning(
                    "Kein Flughafen gefunden."
                )

    st.divider()

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
            "Wetter, Anflug, VATSIM, "
            "besondere Ereignisse..."
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
# FLUGBUCH
# ============================================================

elif page == "Flugbuch":

    st.markdown(

        """
        <div class="page-header">

            <div class="page-kicker">
                LOGBOOK
            </div>

            <div class="page-title">
                Mein Flugbuch
            </div>

            <div class="page-description">
                Übersicht über alle deine
                gespeicherten Simulator-Flüge.
            </div>

        </div>
        """,

        unsafe_allow_html=True
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

            search = search.lower()

            mask = (

                display

                .astype(str)

                .apply(

                    lambda column:

                    column.str
                    .lower()
                    .str.contains(
                        search,
                        na=False
                    )
                )

                .any(
                    axis=1
                )
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

            list(
                options.keys()
            )
        )

        if st.button(
            "Flug löschen"
        ):

            delete_flight(

                options[
                    selected
                ]
            )

            st.success(
                "Flug wurde gelöscht."
            )

            st.rerun()


# ============================================================
# STATISTIK
# ============================================================

elif page == "Statistik":

    st.markdown(

        """
        <div class="page-header">

            <div class="page-kicker">
                ANALYTICS
            </div>

            <div class="page-title">
                Flugstatistik
            </div>

            <div class="page-description">
                Analysiere deine Flüge, Airlines,
                Flugzeuge und Strecken.
            </div>

        </div>
        """,

        unsafe_allow_html=True
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

        total_hours = flights[
            "flight_time"
        ].sum()

        total_distance = flights[
            "distance"
        ].sum()

        airport_count = len(

            set(
                flights[
                    "departure"
                ]
            )

            |

            set(
                flights[
                    "arrival"
                ]
            )
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Flüge",
            total_flights
        )

        c2.metric(
            "Flugstunden",
            f"{total_hours:.1f}"
        )

        c3.metric(
            "Kilometer",
            f"{total_distance:,.0f}"
        )

        c4.metric(
            "Flughäfen",
            airport_count
        )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(

                '<div class="section-label">'
                'AIRLINES'
                '</div>',

                unsafe_allow_html=True
            )

            st.bar_chart(

                flights[
                    "airline"
                ].value_counts()
            )

        with col2:

            st.markdown(

                '<div class="section-label">'
                'AIRCRAFT'
                '</div>',

                unsafe_allow_html=True
            )

            st.bar_chart(

                flights[
                    "aircraft"
                ].value_counts()
            )

        st.divider()

        st.markdown(

            '<div class="section-label">'
            'MOST FLOWN ROUTES'
            '</div>',

            unsafe_allow_html=True
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

            routes[
                "departure"
            ]

            + " → "

            + routes[
                "arrival"
            ]
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

        st.divider()

        st.markdown(

            '<div class="section-label">'
            'FLIGHTS PER YEAR'
            '</div>',

            unsafe_allow_html=True
        )

        flights["year"] = (

            pd.to_datetime(

                flights[
                    "date"
                ]
            )

            .dt.year
        )

        st.bar_chart(

            flights[
                "year"
            ]

            .value_counts()

            .sort_index()
        )


# ============================================================
# FLUGHAFENDATENBANK
# ============================================================

elif page == "Flughafendatenbank":

    st.markdown(

        """
        <div class="page-header">

            <div class="page-kicker">
                DATABASE
            </div>

            <div class="page-title">
                Flughafendatenbank
            </div>

            <div class="page-description">
                Weltweite Flughafendaten für die
                automatische ICAO- und IATA-Suche.
            </div>

        </div>
        """,

        unsafe_allow_html=True
    )

    if airport_database_exists():

        conn = get_connection()

        count = pd.read_sql_query(

            """
            SELECT COUNT(*) AS count
            FROM airports
            """,

            conn
        ).iloc[0]["count"]

        conn.close()

        st.success(

            f"Flughafendatenbank aktiv · "
            f"{count:,} Flughäfen gespeichert."
        )

    else:

        st.warning(
            "Noch keine Flughafendatenbank vorhanden."
        )

    st.markdown(

        '<div class="section-label">'
        'DATABASE MANAGEMENT'
        '</div>',

        unsafe_allow_html=True
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

        st.markdown(

            '<div class="section-label">'
            'AIRPORT SEARCH'
            '</div>',

            unsafe_allow_html=True
        )

        search = st.text_input(

            "Flughafen suchen",

            placeholder=(
                "ICAO, IATA, Flughafenname "
                "oder Stadt"
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

