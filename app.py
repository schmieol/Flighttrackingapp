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
   METRIKEN
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
   EINGABEFELDER
   ============================================================ */

div[data-baseweb="input"],
div[data-baseweb="select"],
textarea {

    border-radius: 9px !important;
}


/* ============================================================
   STRECKENNETZ FILTER
   ============================================================ */

div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {

    background-color: #0b1120 !important;

    border: 1px solid #0b1120 !important;

    box-shadow: none !important;
}

div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div:hover {

    border-color: #0b1120 !important;
}

div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div:focus-within {

    border-color: #0b1120 !important;

    box-shadow: none !important;
}


/* Ausgewählte Elemente */

div[data-testid="stMultiSelect"] [data-baseweb="tag"] {

    background-color: #1e293b !important;

    border-color: #1e293b !important;

    color: #f8fafc !important;
}


/* ============================================================
   DATAFRAMES
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
   SELECTBOX
   ============================================================ */

div[data-baseweb="select"] > div {

    border-radius: 9px;
}


/* ============================================================
   TEXT
   ============================================================ */

.small-muted {

    color: #94a3b8;

    font-size: 0.9rem;
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

        # ====================================================
        # FILTER
        # ====================================================

        airlines = sorted(

            flights["airline"]
            .dropna()
            .unique()
            .tolist()
        )

        aircraft_types = sorted(

            flights["aircraft"]
            .dropna()
            .unique()
            .tolist()
        )

        # ----------------------------------------------------
        # FILTER + FARBAUSWAHL
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(
            [1, 1, 0.35]
        )

        with col1:

            selected_airlines = st.multiselect(

                "Airlines",

                options=airlines,

                default=airlines,

                key="network_airlines"
            )

        with col2:

            selected_aircraft = st.multiselect(

                "Flugzeugtypen",

                options=aircraft_types,

                default=aircraft_types,

                key="network_aircraft"
            )

        with col3:

            route_color = st.color_picker(

                "Routenfarbe",

                value="#38BDF8",

                key="network_route_color"
            )

        # ====================================================
        # FILTER ANWENDEN
        # ====================================================

        filtered = flights[
            flights["airline"].isin(
                selected_airlines
            )
            &
            flights["aircraft"].isin(
                selected_aircraft
            )
        ].copy()

        # ====================================================
        # FARBE UMRECHNEN
        # ====================================================

        hex_color = route_color.replace(
            "#",
            ""
        )

        try:

            route_rgb = [

                int(hex_color[0:2], 16),

                int(hex_color[2:4], 16),

                int(hex_color[4:6], 16)
            ]

        except (ValueError, IndexError):

            route_rgb = [
                56,
                189,
                248
            ]

        # ====================================================
        # METRIKEN
        # ====================================================

        m1, m2, m3, m4 = st.columns(4)

        with m1:

            st.metric(

                "Flüge",

                len(filtered)
            )

        with m2:

            unique_routes = (

                filtered[
                    [
                        "departure",
                        "arrival"
                    ]
                ]

                .drop_duplicates()
            )

            st.metric(

                "Strecken",

                len(unique_routes)
            )

        with m3:

            unique_airports = (

                set(
                    filtered["departure"]
                    .dropna()
                )

                |

                set(
                    filtered["arrival"]
                    .dropna()
                )
            )

            st.metric(

                "Flughäfen",

                len(unique_airports)
            )

        with m4:

            total_distance = pd.to_numeric(

                filtered["distance"],

                errors="coerce"
            ).fillna(0).sum()

            st.metric(

                "Kilometer",

                f"{total_distance:,.0f}"
            )

        st.divider()

        # ====================================================
        # ROUTEN ERSTELLEN
        # ====================================================

        routes = []

        for _, flight in filtered.iterrows():

            dep = get_airport(
                flight["departure"]
            )

            arr = get_airport(
                flight["arrival"]
            )

            if dep is None or arr is None:

                continue

            # -----------------------------------------------
            # Prüfen, ob Koordinaten vorhanden sind
            # -----------------------------------------------

            if (
                dep["latitude"] is None
                or dep["longitude"] is None
                or arr["latitude"] is None
                or arr["longitude"] is None
            ):

                continue

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
                        if pd.notna(
                            flight["flight_number"]
                        )
                        else ""
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
                            if pd.notna(
                                flight["distance"]
                            )
                            else 0
                        )
                    ),

                "color_r":
                    route_rgb[0],

                "color_g":
                    route_rgb[1],

                "color_b":
                    route_rgb[2]
            })

        routes_df = pd.DataFrame(routes)

        # ====================================================
        # KARTE
        # ====================================================

        if not routes_df.empty:

            # ------------------------------------------------
            # ARC LAYER
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
                    "color_r",
                    "color_g",
                    "color_b",
                    230
                ],

                get_target_color=[
                    "color_r",
                    "color_g",
                    "color_b",
                    230
                ],

                get_width=4,

                pickable=True,

                auto_highlight=True
            )

            # ------------------------------------------------
            # VIEW STATE
            # ------------------------------------------------

            view_state = pdk.ViewState(

                latitude=30,

                longitude=10,

                zoom=1.5,

                pitch=20
            )

            # ------------------------------------------------
            # TOOLTIP
            # ------------------------------------------------

            tooltip = {

                "html": """
                    <div>
                        <b>{flight_number}</b><br/>
                        Airline: {airline}<br/>
                        Flugzeug: {aircraft}<br/>
                        Route: {departure} → {arrival}<br/>
                        Datum: {date}<br/>
                        Distanz: {distance} km
                    </div>
                """,

                "style": {

                    "backgroundColor":
                        "#111827",

                    "color":
                        "white",

                    "fontSize":
                        "14px",

                    "padding":
                        "12px",

                    "border":
                        "1px solid #334155",

                    "borderRadius":
                        "8px"
                }
            }

            # ------------------------------------------------
            # DECK ERSTELLEN
            # ------------------------------------------------

            deck = pdk.Deck(

                layers=[
                    route_layer
                ],

                initial_view_state=view_state,

                tooltip=tooltip
            )

            # ------------------------------------------------
            # KARTE ANZEIGEN
            # ------------------------------------------------

            st.pydeck_chart(

                deck,

                use_container_width=True
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

            display = display[mask]

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

        total_hours = pd.to_numeric(

            flights["flight_time"],

            errors="coerce"

        ).fillna(0).sum()

        total_distance = pd.to_numeric(

            flights["distance"],

            errors="coerce"

        ).fillna(0).sum()

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

        # ====================================================
        # KENNZAHLEN
        # ====================================================

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

        # ====================================================
        # AIRLINES UND FLUGZEUGE
        # ====================================================

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "Flüge pro Airline"
            )

            st.bar_chart(

                flights[
                    "airline"
                ].value_counts()
            )

        with col2:

            st.subheader(
                "Flüge pro Flugzeug"
            )

            st.bar_chart(

                flights[
                    "aircraft"
                ].value_counts()
            )

        # ====================================================
        # ROUTEN
        # ====================================================

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

        # ====================================================
        # FLÜGE PRO JAHR
        # ====================================================

        st.subheader(
            "Flüge pro Jahr"
        )

        flights["year"] = (

            pd.to_datetime(

                flights["date"],

                errors="coerce"
            ).dt.year
        )

        st.bar_chart(

            flights[
                "year"
            ]
            .value_counts()
            .sort_index()
        )
