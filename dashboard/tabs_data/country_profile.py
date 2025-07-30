
def get_country_data():
    import streamlit as st
    import re
    import streamlit_folium as st_folium
    import folium
    import pandas as  pd
    from tabs_data.credentials import cred # type: ignore
    from docx import Document # type: ignore
    engine=cred() 
    left_col , right_col = st.columns([4,5])
    with left_col:
        pass
        # @st.cache_data
        # def load_data():
        #     forecast_df = pd.read_sql("SELECT * FROM temperature_forecast", engine)
        #     stations_df = pd.read_sql("SELECT * FROM stations", engine)

        #     forecast_df['date'] = pd.to_datetime(forecast_df['date'])
        #     forecast_df['station_code'] = forecast_df['station_code'].astype(str)
        #     stations_df['station_code'] = stations_df['station_code'].astype(str)

        #     df = pd.merge(forecast_df, stations_df, on='station_code', how='left')

        #     df = df.dropna(subset=['latitude', 'longitude','min_temp', 'max_temp','heat_max', 'heat_min','cold_max', 'cold_min'])

        #     df['day'] = (df['date'] - df['date'].min()).dt.days + 1

        #     df['min_temp'] = df['min_temp'].round(2)
        #     df['max_temp'] = df['max_temp'].round(2)

        #     return df

        # data = load_data()

        # selected_day = st.slider("Select forecast day (1–7)", 1, 7, 1)

        # # ---------- Filter & Classify ----------
        # df_day = data[data['day'] == selected_day].copy()

        # def classify_condition(row):
        #     if row['min_temp'] < row['cold_min']:
        #         return "Cold Wave"
        #     elif row['max_temp'] > row['heat_max']:
        #         return "Heat Wave"
        #     else:
        #         return "Normal"

        # df_day['Condition'] = df_day.apply(classify_condition, axis=1)

        # # ---------- Custom Hover Text ----------
        # df_day["hover_text"] = (
        #     "<b>📍 " + df_day["station_name"] + "</b><br>" +
        #     "🌡️ Min Temp: " + df_day["min_temp"].astype(str) + "°C<br>" +
        #     "🌞 Max Temp: " + df_day["max_temp"].astype(str) + "°C<br>" +
        #     "⚠️ Condition: <b>" + df_day["Condition"] + "</b>"
        # )

        # # ---------- Color and Size Mapping ----------
        # color_map = {
        #     "Cold Wave": "blue",
        #     "Heat Wave": "red",
        #     "Normal": "green"
        # }

        # # ---------- Map Plot ----------
        # m = folium.Map(location=[-38.5, -40.6], zoom_start=3.6)

        # for _, row in df_day.iterrows():
        #     folium_color = {
        #         "Cold Wave": "blue",
        #         "Heat Wave": "red",
        #         "Normal": "green"
        #     }.get(row["Condition"], "green")
            
        #     folium.CircleMarker(
        #         location=[row["latitude"], row["longitude"]],
        #         radius=5,  # Size of the dot
        #         color=folium_color,
        #         fill=True,
        #         fill_color=folium_color,
        #         fill_opacity=0.8,
        #         tooltip=folium.Tooltip(row["hover_text"], sticky=True),  # On-hover info
        #     ).add_to(m)

        # # ---------- Dashboard Output ----------
        # st.subheader(f"Forecast Summary — Day {selected_day}")
        # st_folium(m, width=900, height=650)
        
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