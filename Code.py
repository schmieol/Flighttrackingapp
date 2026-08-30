import streamlit as st
import sqlite3
import pandas as pd
import pydeck as pdk

# ============================================================
# KONFIGURATION
# ============================================================

st.set_page_config(
    page_title="My Flight Network",
    page_icon="✈️",
    layout="wide"
)

DB_FILE = "flights.db"


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
            date TEXT,
            airline TEXT,
            flight_number TEXT,
            aircraft TEXT,
            departure TEXT,
            arrival TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_flight(
    date,
    airline,
    flight_number,
    aircraft,
    departure,
    arrival
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO flights
        (
            date,
            airline,
            flight_number,
            aircraft,
            departure,
            arrival
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        date,
        airline,
        flight_number,
        aircraft,
        departure,
        arrival
    ))

    conn.commit()
    conn.close()


def get_flights():
    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM flights
        ORDER BY date DESC
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
# FLUGHAFEN-DATEN
# ============================================================
#
# Beispiel-Flughäfen.
# Diese Datenbank kann später problemlos durch eine
# vollständige ICAO-Datenbank ersetzt werden.
#

AIRPORTS = {

    # Deutschland
    "EDDH": ("Hamburg", 53.6304, 9.9882),
    "EDDF": ("Frankfurt", 50.0379, 8.5622),
    "EDDM": ("Munich", 48.3538, 11.7861),
    "EDDB": ("Berlin", 52.3667, 13.5033),
    "EDDL": ("Düsseldorf", 51.2895, 6.7668),
    "EDDS": ("Stuttgart", 48.6899, 9.2219),
    "EDDK": ("Cologne", 50.8659, 7.1427),

    # Großbritannien
    "EGLL": ("London Heathrow", 51.4700, -0.4543),
    "EGCC": ("Manchester", 53.3537, -2.2750),
    "EGPH": ("Edinburgh", 55.9500, -3.3725),

    # Frankreich
    "LFPG": ("Paris CDG", 49.0097, 2.5479),
    "LFPO": ("Paris Orly", 48.7233, 2.3794),

    # Niederlande / Belgien
    "EHAM": ("Amsterdam", 52.3105, 4.7683),
    "EBBR": ("Brussels", 50.9010, 4.4856),

    # Europa
    "LOWW": ("Vienna", 48.1103, 16.5697),
    "LSZH": ("Zurich", 47.4581, 8.5555),
    "LIRF": ("Rome", 41.8003, 12.2389),
    "LEMD": ("Madrid", 40.4983, -3.5676),
    "LEBL": ("Barcelona", 41.2974, 2.0833),

    # USA
    "KJFK": ("New York JFK", 40.6413, -73.7781),
    "KLAX": ("Los Angeles", 33.9416, -118.4085),
    "KORD": ("Chicago O'Hare", 41.9742, -87.9073),
    "KATL": ("Atlanta", 33.6407, -84.4277),
    "KMIA": ("Miami", 25.7959, -80.2870),
    "KSFO": ("San Francisco", 37.6213, -122.3790),

    # Naher Osten
    "OMDB": ("Dubai", 25.2532, 55.3657),
    "OTHH": ("Doha", 25.2731, 51.6081),

    # Asien
    "RJTT": ("Tokyo Haneda", 35.5494, 139.7798),
    "WSSS": ("Singapore", 1.3644, 103.9915),

    # Australien
    "YSSY": ("Sydney", -33.9399, 151.1753),
}


# ============================================================
# AIRLINE-FARBEN
# ============================================================

AIRLINE_COLORS = {

    "Lufthansa": [0, 90, 180],
    "Eurowings": [180, 0, 90],
    "Ryanair": [0, 100, 200],
    "easyJet": [255, 100, 0],
    "British Airways": [40, 70, 180],
    "Air France": [50, 80, 200],
    "KLM": [0, 140, 210],
    "Emirates": [210, 30, 30],
    "Qatar Airways": [100, 0, 80],
    "Turkish Airlines": [220, 0, 0],
    "United": [0, 80, 170],
    "American Airlines": [0, 90, 180],
    "Delta": [200, 0, 40],
    "Singapore Airlines": [255, 150, 0],
    "Qantas": [200, 0, 0],
}


DEFAULT_COLOR = [100, 100, 100]


def get_airline_color(airline):
    return AIRLINE_COLORS.get(
        airline,
        DEFAULT_COLOR
    )


# ============================================================
# KARTENDATEN ERSTELLEN
# ============================================================

def create_map_data(flights):

    lines = []
    airports = {}

    for _, flight in flights.iterrows():

        departure = str(
            flight["departure"]
        ).upper().strip()

        arrival = str(
            flight["arrival"]
        ).upper().strip()

        if (
            departure not in AIRPORTS
            or arrival not in AIRPORTS
        ):
            continue

        dep_name, dep_lat, dep_lon = AIRPORTS[
            departure
        ]

        arr_name, arr_lat, arr_lon = AIRPORTS[
            arrival
        ]

        airline = flight["airline"]

        color = get_airline_color(
            airline
        )

        # ----------------------------------------------------
        # ROUTE
        # ----------------------------------------------------

        lines.append({

            "from_lon": dep_lon,
            "from_lat": dep_lat,

            "to_lon": arr_lon,
            "to_lat": arr_lat,

            "airline": airline,

            "flight_number":
                flight["flight_number"],

            "aircraft":
                flight["aircraft"],

            "departure":
                departure,

            "arrival":
                arrival,

            "date":
                flight["date"],

            "color":
                color
        })

        # ----------------------------------------------------
        # ABFLUGHAFEN
        # ----------------------------------------------------

        airports[departure] = {

            "icao": departure,

            "name": dep_name,

            "lat": dep_lat,

            "lon": dep_lon
        }

        # ----------------------------------------------------
        # ZIELFLUGHAFEN
        # ----------------------------------------------------

        airports[arrival] = {

            "icao": arrival,

            "name": arr_name,

            "lat": arr_lat,

            "lon": arr_lon
        }

    return (
        pd.DataFrame(lines),
        pd.DataFrame(
            airports.values()
        )
    )


# ============================================================
# APP START
# ============================================================

init_database()


# ============================================================
# HEADER
# ============================================================

st.title("✈️ My Flight Network")

st.caption(
    "Dein persönliches Streckennetz aus deinen "
    "Simulator-Flügen."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("✈️ Navigation")

page = st.sidebar.radio(
    "Bereich",
    [
        "🌍 Streckennetz",
        "➕ Flug hinzufügen",
        "📋 Flugliste",
        "📊 Statistik"
    ]
)


# ============================================================
# FLUG HINZUFÜGEN
# ============================================================

if page == "➕ Flug hinzufügen":

    st.header("➕ Flug hinzufügen")

    st.write(
        "Trage hier einen Flug aus deinem Simulator ein."
    )

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # LINKE SEITE
    # --------------------------------------------------------

    with col1:

        date = st.date_input(
            "📅 Flugdatum"
        )

        airline = st.text_input(
            "🏢 Airline",
            placeholder="z. B. Lufthansa"
        )

        flight_number = st.text_input(
            "🔢 Flugnummer",
            placeholder="z. B. LH206"
        )

    # --------------------------------------------------------
    # RECHTE SEITE
    # --------------------------------------------------------

    with col2:

        aircraft = st.text_input(
            "✈️ Flugzeugtyp",
            placeholder="z. B. Airbus A320neo"
        )

        departure = st.text_input(
            "🛫 Abflug – ICAO",
            placeholder="z. B. EDDH"
        ).upper()

        arrival = st.text_input(
            "🛬 Ziel – ICAO",
            placeholder="z. B. EDDF"
        ).upper()

    st.divider()

    if st.button(
        "💾 Flug speichern",
        type="primary",
        use_container_width=True
    ):

        if not departure:
            st.error(
                "Bitte einen Abflughafen eingeben."
            )

        elif not arrival:
            st.error(
                "Bitte einen Zielflughafen eingeben."
            )

        elif departure == arrival:
            st.error(
                "Abflug und Ziel dürfen nicht identisch sein."
            )

        else:

            add_flight(
                date=str(date),
                airline=airline,
                flight_number=flight_number,
                aircraft=aircraft,
                departure=departure,
                arrival=arrival
            )

            st.success(
                "✈️ Flug erfolgreich gespeichert!"
            )

            # Warnung bei unbekannten Flughäfen
            if departure not in AIRPORTS:

                st.warning(
                    f"{departure} ist momentan nicht "
                    "in der Kartendatenbank."
                )

            if arrival not in AIRPORTS:

                st.warning(
                    f"{arrival} ist momentan nicht "
                    "in der Kartendatenbank."
                )


# ============================================================
# STRECKENNETZ
# ============================================================

elif page == "🌍 Streckennetz":

    st.header("🌍 Mein Streckennetz")

    flights = get_flights()

    if flights.empty:

        st.info(
            "Noch keine Flüge vorhanden. "
            "Füge zuerst einen Flug hinzu."
        )

    else:

        # ====================================================
        # FILTER
        # ====================================================

        st.subheader("🔎 Filter")

        filter_col1, filter_col2 = st.columns(2)

        airlines = sorted(
            [
                a for a in flights["airline"]
                .dropna()
                .unique()
                if a
            ]
        )

        aircraft_types = sorted(
            [
                a for a in flights["aircraft"]
                .dropna()
                .unique()
                if a
            ]
        )

        with filter_col1:

            selected_airlines = st.multiselect(
                "Airlines",
                airlines,
                default=airlines
            )

        with filter_col2:

            selected_aircraft = st.multiselect(
                "Flugzeugtypen",
                aircraft_types,
                default=aircraft_types
            )

        filtered_flights = flights[
            flights["airline"].isin(
                selected_airlines
            )
            &
            flights["aircraft"].isin(
                selected_aircraft
            )
        ]

        # ====================================================
        # ZAHLEN
        # ====================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "✈️ Flüge",
                len(filtered_flights)
            )

        with col2:

            unique_routes = (
                filtered_flights[
                    ["departure", "arrival"]
                ]
                .drop_duplicates()
                .shape[0]
            )

            st.metric(
                "🛫 Strecken",
                unique_routes
            )

        with col3:

            airport_count = len(
                set(
                    filtered_flights["departure"]
                )
                |
                set(
                    filtered_flights["arrival"]
                )
            )

            st.metric(
                "🌍 Flughäfen",
                airport_count
            )

        with col4:

            airline_count = (
                filtered_flights["airline"]
                .nunique()
            )

            st.metric(
                "🏢 Airlines",
                airline_count
            )

        st.divider()

        # ====================================================
        # KARTE
        # ====================================================

        lines, airports = create_map_data(
            filtered_flights
        )

        if not lines.empty:

            # ------------------------------------------------
            # ROUTEN
            # ------------------------------------------------

            route_layer = pdk.Layer(

                "ArcLayer",

                data=lines,

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

                get_width=3,

                get_tilt=20,

                pickable=True,

                auto_highlight=True
            )

            # ------------------------------------------------
            # FLUGHÄFEN
            # ------------------------------------------------

            airport_layer = pdk.Layer(

                "ScatterplotLayer",

                data=airports,

                get_position=[
                    "lon",
                    "lat"
                ],

                get_fill_color=[
                    255,
                    255,
                    255,
                    230
                ],

                get_line_color=[
                    0,
                    120,
                    255,
                    255
                ],

                get_radius=35000,

                get_line_width=2,

                stroked=True,

                pickable=True
            )

            # ------------------------------------------------
            # KARTENANSICHT
            # ------------------------------------------------

            view_state = pdk.ViewState(

                latitude=30,

                longitude=10,

                zoom=1.8,

                pitch=20
            )

            # ------------------------------------------------
            # INTERAKTIVE KARTE
            # ------------------------------------------------

            deck = pdk.Deck(

                map_style=None,

                initial_view_state=view_state,

                layers=[
                    route_layer,
                    airport_layer
                ],

                tooltip={

                    "html": """
                        <b>✈️ {flight_number}</b><br/>
                        <b>Airline:</b> {airline}<br/>
                        <b>Flugzeug:</b> {aircraft}<br/>
                        <b>Strecke:</b>
                        {departure} → {arrival}<br/>
                        <b>Datum:</b> {date}
                    """,

                    "style": {
                        "backgroundColor": "#111827",
                        "color": "white",
                        "fontSize": "14px",
                        "padding": "10px"
                    }
                }
            )

            st.pydeck_chart(
                deck,
                use_container_width=True
            )

        else:

            st.warning(
                "Für die ausgewählten Filter "
                "wurden keine bekannten Flughäfen gefunden."
            )

        # ====================================================
        # LEGENDE
        # ====================================================

        st.subheader("🎨 Airline-Legende")

        legend_cols = st.columns(
            min(
                max(len(selected_airlines), 1),
                4
            )
        )

        for index, airline in enumerate(
            selected_airlines
        ):

            color = get_airline_color(
                airline
            )

            with legend_cols[
                index % len(legend_cols)
            ]:

                st.markdown(
                    f"""
                    <div style="
                        display:flex;
                        align-items:center;
                        margin-bottom:8px;
                    ">
                        <div style="
                            width:18px;
                            height:18px;
                            background-color:
                                rgb(
                                    {color[0]},
                                    {color[1]},
                                    {color[2]}
                                );
                            border-radius:50%;
                            margin-right:8px;
                        "></div>

                        <span>
                            {airline}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# FLUGLISTE
# ============================================================

elif page == "📋 Flugliste":

    st.header("📋 Meine Flüge")

    flights = get_flights()

    if flights.empty:

        st.info(
            "Noch keine Flüge gespeichert."
        )

    else:

        display_df = flights.copy()

        display_df = display_df.rename(
            columns={
                "date": "Datum",
                "airline": "Airline",
                "flight_number": "Flugnummer",
                "aircraft": "Flugzeug",
                "departure": "Abflug",
                "arrival": "Ziel"
            }
        )

        display_df = display_df.drop(
            columns=["id"]
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("🗑️ Flug löschen")

        flight_options = {

            f"{row['date']} | "
            f"{row['flight_number']} | "
            f"{row['departure']} → "
            f"{row['arrival']} | "
            f"{row['aircraft']}":
                row["id"]

            for _, row in flights.iterrows()
        }

        selected_flight = st.selectbox(
            "Flug auswählen",
            list(
                flight_options.keys()
            )
        )

        if st.button(
            "🗑️ Flug löschen"
        ):

            delete_flight(
                flight_options[
                    selected_flight
                ]
            )

            st.success(
                "Flug wurde gelöscht."
            )

            st.rerun()


# ============================================================
# STATISTIK
# ============================================================

elif page == "📊 Statistik":

    st.header("📊 Flugstatistik")

    flights = get_flights()

    if flights.empty:

        st.info(
            "Noch keine Flüge vorhanden."
        )

    else:

        # ----------------------------------------------------
        # GRUNDSTATISTIK
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "✈️ Flüge",
                len(flights)
            )

        with col2:

            st.metric(
                "🏢 Airlines",
                flights["airline"].nunique()
            )

        with col3:

            st.metric(
                "✈️ Flugzeugtypen",
                flights["aircraft"].nunique()
            )

        with col4:

            airports_count = len(
                set(
                    flights["departure"]
                )
                |
                set(
                    flights["arrival"]
                )
            )

            st.metric(
                "🌍 Flughäfen",
                airports_count
            )

        st.divider()

        # ----------------------------------------------------
        # AIRLINES
        # ----------------------------------------------------

        st.subheader(
            "🏢 Flüge pro Airline"
        )

        airline_counts = (
            flights["airline"]
            .value_counts()
        )

        st.bar_chart(
            airline_counts
        )

        # ----------------------------------------------------
        # FLUGZEUGE
        # ----------------------------------------------------

        st.subheader(
            "✈️ Geflogene Flugzeugtypen"
        )

        aircraft_counts = (
            flights["aircraft"]
            .value_counts()
        )

        st.bar_chart(
            aircraft_counts
        )

        # ----------------------------------------------------
        # STRECKEN
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
                ["Strecke", "Flüge"]
            ],
            use_container_width=True,
            hide_index=True
        )
