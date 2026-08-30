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
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "flights.db"

# OurAirports Open Data
AIRPORT_DATABASE_URL = (
    "https://ourairports.com/data/airports.csv"
)


# ============================================================
# DESIGN
# ============================================================

st.markdown("""
<style>

[data-testid="stMetric"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    padding: 15px;
    border-radius: 12px;
}

.stButton > button {
    border-radius: 8px;
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

    # --------------------------------------------------------
    # FLÜGE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # FLUGHÄFEN
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # DATENBANK-INFORMATION
    # --------------------------------------------------------

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
# FLUGHÄFEN IN SQLITE SPEICHERN
# ============================================================

def import_airports(df):

    if df is None or df.empty:

        return False

    conn = get_connection()

    # --------------------------------------------------------
    # Nur relevante Spalten
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Spalten umbenennen
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Fehlende Spalten hinzufügen
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Nur Flughäfen
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Leere ICAOs entfernen
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # In SQLite schreiben
    # --------------------------------------------------------

    df.to_sql(
        "airports",
        conn,
        if_exists="replace",
        index=False
    )

    # --------------------------------------------------------
    # Zeitpunkt speichern
    # --------------------------------------------------------

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


# ============================================================
# FLUGHAFENDATENBANK PRÜFEN
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

    except:

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
# AIRLINE-FARBEN
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
    130,
    130,
    130
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

st.sidebar.title(
    "✈️ My Flight Network"
)

st.sidebar.caption(
    "MSFS 2024 Flight Logbook"
)

st.sidebar.divider()

page = st.sidebar.radio(

    "Navigation",

    [

        "🌍 Streckennetz",

        "➕ Flug hinzufügen",

        "📋 Flugbuch",

        "📊 Statistik",

        "🗄️ Flughafendatenbank"

    ]
)


# ============================================================
# FLUGHAFENDATENBANK VERWALTUNG
# ============================================================

if page == "🗄️ Flughafendatenbank":

    st.title(
        "🗄️ Flughafendatenbank"
    )

    st.write(
        "Die Flughäfen werden lokal in deiner "
        "SQLite-Datenbank gespeichert."
    )

    st.divider()

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if airport_database_exists():

        conn = get_connection()

        count = pd.read_sql_query(
            "SELECT COUNT(*) AS count FROM airports",
            conn
        ).iloc[0]["count"]

        conn.close()

        st.success(
            f"✅ Flughafendatenbank aktiv – "
            f"{count:,} Flughäfen gespeichert."
        )

    else:

        st.warning(
            "⚠️ Noch keine Flughafendatenbank "
            "vorhanden."
        )

    # --------------------------------------------------------
    # AKTUALISIEREN
    # --------------------------------------------------------

    st.subheader(
        "🔄 Datenbank aktualisieren"
    )

    st.write(
        "Lädt die aktuelle weltweite "
        "Flughafendatenbank herunter und "
        "speichert sie lokal."
    )

    if st.button(
        "🌍 Flughafendatenbank herunterladen",
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
                    f"✅ {len(airport_df):,} "
                    "Flughäfen importiert."
                )

                st.rerun()

    st.divider()

    # --------------------------------------------------------
    # SUCHE
    # --------------------------------------------------------

    if airport_database_exists():

        st.subheader(
            "🔎 Flughafen suchen"
        )

        search = st.text_input(

            "ICAO, IATA, Name oder Stadt",

            placeholder=(
                "z. B. EDDH, HAM, Hamburg "
                "oder Frankfurt"
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

elif page == "➕ Flug hinzufügen":

    st.title(
        "➕ Flug hinzufügen"
    )

    if not airport_database_exists():

        st.warning(
            "⚠️ Die Flughafendatenbank ist noch "
            "nicht installiert."
        )

        if st.button(
            "🌍 Flughafendatenbank jetzt laden"
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
    # DATUM / AIRLINE
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        flight_date = st.date_input(
            "📅 Flugdatum",
            value=date.today()
        )

        airline = st.text_input(
            "🏢 Airline",
            placeholder="z. B. Lufthansa"
        )

        flight_number = st.text_input(
            "🔢 Flugnummer",
            placeholder="z. B. LH206"
        )

        aircraft = st.text_input(
            "✈️ Flugzeug",
            placeholder=(
                "z. B. Airbus A320neo"
            )
        )

    with col2:

        # ----------------------------------------------------
        # ABFLUG
        # ----------------------------------------------------

        st.write(
            "🛫 **Abflughafen**"
        )

        departure_search = st.text_input(

            "Suche",

            placeholder=(
                "ICAO, IATA oder Flughafenname"
            ),

            key="departure_search"
        )

        departure = ""

        if departure_search:

            departure_results = (
                search_airports(
                    departure_search
                )
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

                selected_departure = (
                    st.selectbox(
                        "Flughafen auswählen",
                        list(
                            departure_options.keys()
                        ),
                        key="departure_select"
                    )
                )

                departure = (
                    departure_options[
                        selected_departure
                    ]
                )

            else:

                st.warning(
                    "Kein Flughafen gefunden."
                )

        # ----------------------------------------------------
        # ZIEL
        # ----------------------------------------------------

        st.write(
            "🛬 **Zielflughafen**"
        )

        arrival_search = st.text_input(

            "Suche",

            placeholder=(
                "ICAO, IATA oder Flughafenname"
            ),

            key="arrival_search"
        )

        arrival = ""

        if arrival_search:

            arrival_results = (
                search_airports(
                    arrival_search
                )
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

                selected_arrival = (
                    st.selectbox(
                        "Flughafen auswählen",
                        list(
                            arrival_options.keys()
                        ),
                        key="arrival_select"
                    )
                )

                arrival = (
                    arrival_options[
                        selected_arrival
                    ]
                )

            else:

                st.warning(
                    "Kein Flughafen gefunden."
                )

    # --------------------------------------------------------
    # FLUGZEIT
    # --------------------------------------------------------

    flight_time = st.number_input(

        "⏱️ Flugzeit in Stunden",

        min_value=0.0,

        max_value=30.0,

        value=1.0,

        step=0.1
    )

    notes = st.text_area(

        "📝 Notizen",

        placeholder=(
            "z. B. VATSIM, schlechtes Wetter, "
            "ILS-Anflug..."
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
                f"📏 Entfernung: "
                f"**{distance:,.0f} km**"
            )

    # --------------------------------------------------------
    # SPEICHERN
    # --------------------------------------------------------

    st.divider()

    if st.button(

        "💾 Flug speichern",

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
                "Abflug und Ziel dürfen nicht "
                "identisch sein."
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
                "✈️ Flug erfolgreich gespeichert!"
            )


# ============================================================
# STRECKENNETZ
# ============================================================

elif page == "🌍 Streckennetz":

    st.title(
        "🌍 Mein Streckennetz"
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

        c1, c2 = st.columns(2)

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

        with c1:

            selected_airlines = st.multiselect(

                "🏢 Airlines",

                airlines,

                default=airlines
            )

        with c2:

            selected_aircraft = st.multiselect(

                "✈️ Flugzeuge",

                aircraft,

                default=aircraft
            )

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
                "✈️ Flüge",
                len(filtered)
            )

        with m2:

            st.metric(
                "🛫 Strecken",
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
                "🌍 Flughäfen",
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

        with m4:

            st.metric(
                "📏 Kilometer",
                f"{filtered['distance'].sum():,.0f}"
            )

        # ----------------------------------------------------
        # ROUTEN
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

        if not routes_df.empty:

            # ------------------------------------------------
            # ROUTEN-LAYER
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
            # AIRPORT LAYER
            # ------------------------------------------------

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
                    240
                ],

                get_line_color=[
                    0,
                    150,
                    255,
                    255
                ],

                get_line_width=2,

                stroked=True,

                pickable=True
            )

            # ------------------------------------------------
            # KARTE
            # ------------------------------------------------

            deck = pdk.Deck(

                layers=[
                    route_layer,
                    airport_layer
                ],

                initial_view_state=pdk.ViewState(

                    latitude=30,

                    longitude=10,

                    zoom=1.5,

                    pitch=20
                ),

                tooltip={

                    "html": """
                        <b>✈️ {flight_number}</b><br/>
                        <b>Airline:</b> {airline}<br/>
                        <b>Flugzeug:</b> {aircraft}<br/>
                        <b>Route:</b>
                        {departure} → {arrival}<br/>
                        <b>Datum:</b> {date}<br/>
                        <b>Distanz:</b>
                        {distance} km
                    """,

                    "style": {

                        "backgroundColor":
                            "#111827",

                        "color":
                            "white",

                        "fontSize":
                            "14px",

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
# FLUGBUCH
# ============================================================

elif page == "📋 Flugbuch":

    st.title(
        "📋 Mein Flugbuch"
    )

    flights = get_flights()

    if flights.empty:

        st.info(
            "Noch keine Flüge gespeichert."
        )

    else:

        search = st.text_input(
            "🔎 Flug suchen"
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
                    "Flugzeit h",

                "distance":
                    "Distanz km",

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
            "🗑️ Flug löschen"
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
            "🗑️ Flug löschen"
        ):

            delete_flight(
                options[selected]
            )

            st.success(
                "Flug gelöscht."
            )

            st.rerun()


# ============================================================
# STATISTIK
# ============================================================

elif page == "📊 Statistik":

    st.title(
        "📊 Flugstatistik"
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

        # ----------------------------------------------------
        # METRIKEN
        # ----------------------------------------------------

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "✈️ Flüge",
                total_flights
            )

        with c2:

            st.metric(
                "⏱️ Flugstunden",
                f"{total_hours:.1f}"
            )

        with c3:

            st.metric(
                "📏 Kilometer",
                f"{total_distance:,.0f}"
            )

        with c4:

            st.metric(
                "🌍 Flughäfen",
                airport_count
            )

        st.divider()

        # ----------------------------------------------------
        # AIRLINES
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "🏢 Airlines"
            )

            st.bar_chart(
                flights[
                    "airline"
                ].value_counts()
            )

        with col2:

            st.subheader(
                "✈️ Flugzeuge"
            )

            st.bar_chart(
                flights[
                    "aircraft"
                ].value_counts()
            )

        # ----------------------------------------------------
        # ROUTEN
        # ----------------------------------------------------

        st.subheader(
            "🛫 Häufigste Strecken"
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

        # ----------------------------------------------------
        # JAHRE
        # ----------------------------------------------------

        st.subheader(
            "📅 Flüge pro Jahr"
        )

        flights["year"] = (
            pd.to_datetime(
                flights["date"]
            ).dt.year
        )

        st.bar_chart(
            flights[
                "year"
            ].value_counts()
            .sort_index()
        )
