
def get_country_data():
    import streamlit as st
    import re
    from streamlit_folium import st_folium
    import folium
    from folium import Map, Element
    import pandas as  pd
    from tabs_data.credentials import cred # type: ignore
    from docx import Document # type: ignore
    engine=cred() 
    left_col , right_col = st.columns([4,5])
    with left_col:  

        @st.cache_data
        def load_data():
            # Fetch temperature forecast for only the last 7 days
            query = """
                SELECT * FROM temperature_forecast
                WHERE date BETWEEN 
                (SELECT MAX(date) FROM temperature_forecast) - INTERVAL '7 days'
                AND (SELECT MAX(date) FROM temperature_forecast)
            """
            forecast_df = pd.read_sql(query, engine)

            # Fetch stations data
            stations_df = pd.read_sql("SELECT * FROM stations", engine)

            forecast_df['date'] = pd.to_datetime(forecast_df['date'])
            forecast_df['station_code'] = forecast_df['station_code'].astype(str)
            stations_df['station_code'] = stations_df['station_code'].astype(str)

            df = pd.merge(forecast_df, stations_df, on='station_code', how='left')
            df = df.dropna(subset=['latitude', 'longitude', 'min_temp', 'max_temp', 'risk_level'])

            df['day'] = df.groupby('station_code')['date'].rank(method='dense').astype(int)
            df['min_temp'] = df['min_temp'].round(2)
            df['max_temp'] = df['max_temp'].round(2)

            return df

        @st.cache_data
        def load_dates():
            # Fetch distinct dates from the last 7 days for the slider
            query_dates = """
                SELECT DISTINCT date FROM temperature_forecast
                WHERE date BETWEEN 
                (SELECT MAX(date) FROM temperature_forecast) - INTERVAL '7 days'
                AND (SELECT MAX(date) FROM temperature_forecast)
                ORDER BY date
            """
            dates_df = pd.read_sql(query_dates, engine)
            dates_df['date'] = pd.to_datetime(dates_df['date'])
            return dates_df['date'].dt.date.tolist()  # List of python date objects

        # Load data and dates
        data = load_data()
        available_dates = load_dates()

        # Slider to select actual date instead of day number
        selected_date = st.slider("Select forecast date", min_value=min(available_dates), max_value=max(available_dates), value=max(available_dates), format="YYYY-MM-DD")

        # Filter data for the selected date
        df_day = data[data['date'].dt.date == selected_date].copy()

        
        def map_condition(risk):
            if 'H' in risk:
                return "Heat Wave"
            elif 'L' in risk:
                return "Cold Wave"
            else:
                return "Normal"
            
        df_day["condition"] = df_day["risk_level"].apply(map_condition)

        # Tooltip text
        df_day["hover_text"] = (
            "<b>📍 " + df_day["station_name"] + "</b><br>" +
            "🌡️ Min Temp: " + df_day["min_temp"].astype(str) + "°C<br>" +
            "🌞 Max Temp: " + df_day["max_temp"].astype(str) + "°C<br>" +
            " Date: " + data['date'].astype(str) +
            "⚠️ Condition: <b>" + df_day["condition"] + "</b>"
        )

        # Color mapping based on risk_level
        def get_color(risk):
            if 'H' in risk:
                return "red"
            elif 'L' in risk:
                return "blue"
            else:
                return "green"       

        # Your CSS + JS wrapped in a string, refining cursor control
        style_js = """
        <style>
        html, body, .leaflet-container, * {
            cursor: default !important;
            -webkit-user-drag: none;
        }

        /* Standard Leaflet marker (icon) pointer cursor */
        .leaflet-marker-icon {
            cursor: pointer !important;
        }

        </style>
        <script>
        document.querySelectorAll('.leaflet-container').forEach(mapEl => {
        mapEl.style.cursor = 'default';
        });
        </script>
        """

        cursor_js = """
        <script>
        function setCircleMarkerCursorPointer() {
            var mapContainers = document.getElementsByClassName('leaflet-container');
            for (var i = 0; i < mapContainers.length; i++) {
            var mapContainer = mapContainers[i];
            var svgCircles = mapContainer.querySelectorAll('circle.leaflet-interactive');
            svgCircles.forEach(function(circle) {
                circle.addEventListener('mouseover', function() {
                mapContainer.style.cursor = 'pointer';
                });
                circle.addEventListener('mouseout', function() {
                mapContainer.style.cursor = 'default';
                });
            });
            }
        }
        
        setTimeout(setCircleMarkerCursorPointer, 500);
        </script>
        """
        # Create map instance
        m = folium.Map(location=[-38.5, -40.6], zoom_start=4)
        
        full_style_js = style_js + cursor_js
        m.get_root().html.add_child(Element(full_style_js))

        # Add markers
        for _, row in df_day.iterrows():
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=5,
                color=get_color(row["risk_level"]),
                fill=True,
                fill_color=get_color(row["risk_level"]),
                fill_opacity=0.8,
                tooltip=folium.Tooltip(row["hover_text"], sticky=True),
            ).add_to(m)

        # Display map
        st.subheader(f"Forecast Summary — Day {selected_date}")
        st_folium(m, width=900, height=650)

    with right_col: 
        def basic_sent_tokenize(text):
            return re.split(r'(?<=[.?!]) +', text.strip())

        def extract_sections(file_path):

            doc = Document(file_path)
            sections = []
            current = {"heading": None, "style": None, "text": ""}

            for para in doc.paragraphs:
                text = para.text.strip()
                style = para.style.name

                if not text:
                    continue

                if style == "Heading":
                    if current["heading"]:
                        sections.append(current)
                    current = {"heading": text, "style": "H1", "text": ""}

                elif style == "Heading 2":
                    if current["heading"]:
                        sections.append(current)
                    current = {"heading": text, "style": "H2", "text": ""}

                elif style == "Heading 3":
                    if current["heading"]:
                        sections.append(current)
                    current = {"heading": text, "style": "H3", "text": ""}

                elif style == "Normal" and current["heading"]:
                    current["text"] += " " + text

            if current["heading"]:
                sections.append(current)

            return sections

        input_file = "docs/CountryProfile.docx"
        sections = extract_sections(input_file)
        results = []

        for section in sections:
            heading = section["heading"]
            style = section["style"]
            text = section["text"].strip()

            if style == "H1":
                results.append({
                    "style": "H1",
                    "heading": heading
                })

            elif style == "H2":
                entry = {
                    "style": "H2",
                    "heading": heading
                }
                if text:
                    entry["bullets"] = basic_sent_tokenize(text)
                results.append(entry)

            elif style == "H3":
                bullets = basic_sent_tokenize(text) if text else []
                results.append({
                    "style": "H3",
                    "heading": heading,
                    "bullets": bullets
                })

        data = results  

        st.markdown("""
            <style>
            h2.red-heading {
                color: #d00000;
                font-weight: 500;
                font-size: 20px; /* ✅ Font size added */
                margin-top: 1.2em;
                margin-bottom: 0.4em;
            }
            .bullet-list li {
                font-size: 15px;
                font-weight: 500;
                color: #000;
                margin-bottom: 4px;
            }
            </style>
        """, unsafe_allow_html=True)

        for section in data:
            style = section.get("style")
            heading = section.get("heading")
            bullets = section.get("bullets", [])

            if style == "H1":
                st.header(heading)

            elif style == "H2":
                # Styled red heading
                st.markdown(f"<h2 class='red-heading'>{heading}</h2>", unsafe_allow_html=True)
                if bullets:
                    st.markdown("<ul class='bullet-list'>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>", unsafe_allow_html=True)

            elif style == "H3":
                # ✅ Proper markdown bullets inside expander
                with st.expander(heading):
                    if bullets:
                        st.markdown('\n'.join([f"- {b}" for b in bullets]))