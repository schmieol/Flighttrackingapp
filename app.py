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
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url(
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(25, 95, 170, 0.18),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(0, 170, 255, 0.08),
            transparent 25%
        ),
        #080d16;
    color: #f5f7fa;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #0b111d 0%,
            #080c14 100%
        );
    border-right: 1px solid #1d2939;
}

[data-testid="stSidebar"] > div {
    padding-top: 2rem;
}

[data-testid="stSidebar"] .stRadio label {
    color: #9ba8b8;
    font-size: 14px;
}

[data-testid="stSidebar"] .stRadio label:hover {
    color: white;
}

/* Headings */

h1 {
    font-size: 36px !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2 {
    font-size: 25px !important;
    font-weight: 700 !important;
}

h3 {
    font-size: 18px !important;
    font-weight: 700 !important;
}

/* Metrics */

[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            rgba(21, 31, 48, 0.96),
            rgba(13, 20, 32, 0.96)
        );

    border: 1px solid #243247;

    border-radius: 16px;

    padding: 20px;

    box-shadow:
        0 10px 35px rgba(0, 0, 0, 0.18);
}

[data-testid="stMetricLabel"] {
    color: #8492a6 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 28px !important;
    font-weight: 800 !important;
}

/* Buttons */

.stButton > button {
    background:
        linear-gradient(
            135deg,
            #1677ff,
            #0758c7
        );

    color: white;

    border: none;

    border-radius: 10px;

    padding: 10px 18px;

    font-weight: 600;

    transition: 0.2s;
}

.stButton > button:hover {
    background:
        linear-gradient(
            135deg,
            #2d89ff,
            #1267dc
        );

    box-shadow:
        0 8px 25px rgba(22, 119, 255, 0.25);
}

/* Inputs */

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {

    background-color: #0e1623 !important;

    color: white !important;

    border: 1px solid #26364c !important;

    border-radius: 10px !important;
}

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {

    background-color: #0e1623 !important;

    border-color: #26364c !important;

    border-radius: 10px !important;
}

/* Tabs */

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    background: #101927;
    border-radius: 8px;
    padding: 8px 16px;
}

/* Dataframes */

[data-testid="stDataFrame"] {
    border: 1px solid #26364c;
    border-radius: 12px;
    overflow: hidden;
}

/* Dividers */

hr {
    border-color: #1d2939 !important;
}

/* Cards */

.flight-card {

    background:
        linear-gradient(
            145deg,
            rgba(19, 29, 44, 0.95),
            rgba(11, 17, 28, 0.95)
        );

    border: 1px solid #233147;

    border-radius: 16px;

    padding: 20px;

    margin-bottom: 12px;

    box-shadow:
        0 10px 30px rgba(0, 0, 0, 0.15);
}

.flight-card:hover {
    border-color: #315176;
}

.flight-route {

    font-size: 20px;

    font-weight: 800;

    color: white;

    letter-spacing: 0.5px;
}

.flight-meta {

    color: #8b9ab0;

    font-size: 13px;

    margin-top: 7px;
}

.section-title {

    font-size: 12px;

    color: #6f8097;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: 1.2px;

    margin-bottom: 10px;
}

.hero {

    padding:
        10px 0 25px 0;
}

.hero-title {

    font-size: 42px;

    line-height: 1.05;

    font-weight: 800;

    letter-spacing: -1.5px;

    margin-bottom: 10px;
}

.hero-subtitle {

    color: #8d9caf;

    font-size: 15px;
}

.badge {

    display: inline-block;

    background: rgba(22, 119, 255, 0.12);

    color: #4c9aff;

    border: 1px solid rgba(22, 119, 255, 0.25);

    border-radius: 20px;

    padding: 5px 10px;

    font-size: 11px;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: 0.8px;
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
            io.BytesIO(response.content)
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

    required = [

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

        for column in required

        if column in df.columns
    ]

    df = df[available].copy()

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

        str(
            pd.Timestamp.now()
        )
    ))

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

            UPPER(ident) LIKE ?

            OR UPPER(
                COALESCE(iata_code, '')
            ) LIKE ?

            OR UPPER(name) LIKE ?

            OR UPPER(
                COALESCE(municipality, '')
            ) LIKE ?

        ORDER BY

            CASE

                WHEN UPPER(ident) = ?
                THEN 0

                WHEN UPPER(
                    COALESCE(iata_code, '')
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
# FLUGDATEN
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
# DISTANZ
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
        *
        math.cos(lat2)
        *
        math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(

        math.sqrt(a),

        math.sqrt(1 - a)
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
    70,
    130,
    200
]


def get_airline_color(airline):

    return AIRLINE_COLORS.get(

        airline,

        DEFAULT_COLOR
    )


# ============================================================
# MAP DATEN
# ============================================================

def create_map_data(flights):

    routes = []

    airports = {}

    for _, flight in flights.iterrows():

        dep = get_airport(
            flight["departure"]
        )

        arr = get_airport(
            flight["arrival"]
        )

        if not dep or not arr:
            continue

        color = get_airline_color(
            flight["airline"]
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
                color
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

    airports_df = pd.DataFrame(

        [

            {

                "icao":
                    icao,

                "name":
                    airport["name"],

                "city":
                    airport["municipality"],

                "country":
                    airport["iso_country"],

                "lat":
                    airport["latitude"],

                "lon":
                    airport["longitude"]
            }

            for icao, airport
            in airports.items()
        ]
    )

    return routes_df, airports_df


def render_map(flights):

    routes_df, airports_df = create_map_data(
        flights
    )

    if routes_df.empty:

        st.info(
            "Für die aktuelle Auswahl sind keine "
            "kartierbaren Flüge vorhanden."
        )

        return

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

    airport_layer = pdk.Layer(

        "ScatterplotLayer",

        data=airports_df,

        get_position=[
            "lon",
            "lat"
        ],

        get_radius=35000,

        get_fill_color=[
            255,
            255,
            255,
            230
        ],

        get_line_color=[
            40,
            140,
            255,
            255
        ],

        get_line_width=2,

        stroked=True,

        pickable=True
    )

    deck = pdk.Deck(

        layers=[

            route_layer,

            airport_layer
        ],

        initial_view_state=pdk.ViewState(

            latitude=30,

            longitude=10,

            zoom=1.45,

            pitch=20
        ),

        map_style=(
            "https://basemaps.cartocdn.com/"
            "gl/dark-matter-gl-style/style.json"
        ),

        tooltip={

            "html": """

                <div style="
                    padding: 8px;
                    font-family: Arial;
                ">

                    <b>{flight_number}</b><br/>

                    Airline: {airline}<br/>

                    Aircraft: {aircraft}<br/>

                    Route:
                    {departure} →
                    {arrival}<br/>

                    Date: {date}<br/>

                    Distance:
                    {distance} km

                </div>

            """
        }
    )

    st.pydeck_chart(

        deck,

        use_container_width=True
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
    <div style="
        padding: 5px 0 20px 0;
    ">

        <div style="
            color: #ffffff;
            font-size: 20px;
            font-weight: 800;
            letter-spacing: -0.5px;
        ">
            MY FLIGHT NETWORK
        </div>

        <div style="
            color: #65758a;
            font-size: 11px;
            margin-top: 5px;
            letter-spacing: 1px;
        ">
            MSFS 2024 FLIGHT LOGBOOK
        </div>

    </div>
    """,
    unsafe_allow_html=True
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

    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "LOCAL DATABASE"
)

st.sidebar.caption(
    "SQLite"
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    flights = get_flights()

    st.markdown(
        """
        <div class="hero">

            <div class="badge">
                MSFS 2024
            </div>

            <div class="hero-title">
                Your Flight Network
            </div>

            <div class="hero-subtitle">
                Dein persönliches digitales Flugbuch
                und Streckennetz.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # STATISTIK
    # --------------------------------------------------------

    if flights.empty:

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Flüge",
                "0"
            )

        with c2:
            st.metric(
                "Flugstunden",
                "0"
            )

        with c3:
            st.metric(
                "Kilometer",
                "0"
            )

        with c4:
            st.metric(
                "Flughäfen",
                "0"
            )

        st.divider()

        st.info(
            "Noch keine Flüge gespeichert. "
            "Füge deinen ersten MSFS-2024-Flug hinzu."
        )

    else:

        total_flights = len(flights)

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

        with c1:

            st.metric(
                "Flüge",
                f"{total_flights:,}"
            )

        with c2:

            st.metric(
                "Flugstunden",
                f"{total_hours:.1f}"
            )

        with c3:

            st.metric(
                "Kilometer",
                f"{total_distance:,.0f}"
            )

        with c4:

            st.metric(
                "Flughäfen",
                f"{len(airports):,}"
            )

        st.divider()

        # ----------------------------------------------------
        # MAP
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">'
            'YOUR NETWORK'
            '</div>',
            unsafe_allow_html=True
        )

        render_map(
            flights
        )

        st.divider()

        # ----------------------------------------------------
        # UNTERER BEREICH
        # ----------------------------------------------------

        left, right = st.columns(
            [1.4, 1]
        )

        with left:

            st.markdown(
                '<div class="section-title">'
                'RECENT FLIGHTS'
                '</div>',
                unsafe_allow_html=True
            )

            recent = flights.head(5)

            for _, flight in recent.iterrows():

                st.markdown(

                    f"""
                    <div class="flight-card">

                        <div class="flight-route">
                            {flight["departure"]}
                            →
                            {flight["arrival"]}
                        </div>

                        <div class="flight-meta">

                            {flight["airline"]}

                            &nbsp;&nbsp;|&nbsp;&nbsp;

                            {flight["aircraft"]}

                            &nbsp;&nbsp;|&nbsp;&nbsp;

                            {flight["date"]}

                        </div>

                    </div>
                    """,

                    unsafe_allow_html=True
                )

        with right:

            st.markdown(
                '<div class="section-title">'
                'TOP AIRLINES'
                '</div>',
                unsafe_allow_html=True
            )

            airline_counts = (

                flights[
                    "airline"
                ]

                .value_counts()

                .head(7)
            )

            st.dataframe(

                airline_counts.rename(
                    "Flights"
                ),

                use_container_width=True
            )


# ============================================================
# STRECKENNETZ
# ============================================================

elif page == "Streckennetz":

    st.title(
        "Streckennetz"
    )

    flights = get_flights()

    if flights.empty:

        st.info(
            "Noch keine Flüge gespeichert."
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

                "Airlines",

                airlines,

                default=airlines
            )

        with col2:

            selected_aircraft = st.multiselect(

                "Flugzeuge",

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

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "Flüge",
                len(filtered)
            )

        with c2:

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

        with c3:

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

        with c4:

            st.metric(

                "Kilometer",

                f"{filtered['distance'].sum():,.0f}"
            )

        st.divider()

        render_map(
            filtered
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
            "Flughafendatenbank installieren",
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

    # --------------------------------------------------------
    # DATEN
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
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
            '<div class="section-title">'
            'ROUTE'
            '</div>',
            unsafe_allow_html=True
        )

        departure_search = st.text_input(

            "Abflughafen",

            placeholder="ICAO, IATA oder Name",

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

                    "Abflug auswählen",

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

            placeholder="ICAO, IATA oder Name",

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

                    "Ziel auswählen",

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
            "Besondere Ereignisse, Wetter, "
            "Anflug, VATSIM etc."
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
                f"Entfernung: {distance:,.0f} km"
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

    st.title(
        "Flugbuch"
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
                "Airline, Flugnummer, Flughafen "
                "oder Flugzeug"
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

            list(
                options.keys()
            )
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
        "Statistik"
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
                flights["departure"]
            )

            |

            set(
                flights["arrival"]
            )
        )

        airline_count = flights[
            "airline"
        ].nunique()

        aircraft_count = flights[
            "aircraft"
        ].nunique()

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "Flüge",
                total_flights
            )

        with c2:

            st.metric(
                "Flugstunden",
                f"{total_hours:.1f}"
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

        c1, c2 = st.columns(2)

        with c1:

            st.markdown(
                '<div class="section-title">'
                'AIRLINES'
                '</div>',
                unsafe_allow_html=True
            )

            airline_stats = (

                flights[
                    "airline"
                ]

                .value_counts()

                .rename(
                    "Flüge"
                )
            )

            st.bar_chart(
                airline_stats
            )

        with c2:

            st.markdown(
                '<div class="section-title">'
                'AIRCRAFT'
                '</div>',
                unsafe_allow_html=True
            )

            aircraft_stats = (

                flights[
                    "aircraft"
                ]

                .value_counts()

                .rename(
                    "Flüge"
                )
            )

            st.bar_chart(
                aircraft_stats
            )

        st.divider()

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

        st.subheader(
            "Flüge pro Jahr"
        )

        flights["year"] = (

            pd.to_datetime(
                flights["date"]
            ).dt.year
        )

        st.bar_chart(

            flights[
                "year"
            ]
            .value_counts()
            .sort_index()
        )

        st.divider()

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Airlines",
                airline_count
            )

        with c2:

            st.metric(
                "Flugzeugtypen",
                aircraft_count
            )


# ============================================================
# FLUGHAFENDATENBANK
# ============================================================

elif page == "Flughafendatenbank":

    st.title(
        "Flughafendatenbank"
    )

    st.write(
        "Die weltweiten Flughafendaten werden "
        "lokal in SQLite gespeichert."
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
            f"{count:,} Flughäfen"
        )

    else:

        st.warning(
            "Noch keine Flughafendatenbank installiert."
        )

    st.subheader(
        "Datenbank aktualisieren"
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

            "Suche",

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
