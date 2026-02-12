import streamlit as st
import pandas as pd
from streamlit_geolocation import streamlit_geolocation

st.title("Geolocalização")

loc = streamlit_geolocation()

st.write("Sua localização:")
if loc:
    st.write(f"Latitude: {loc['latitude']}")
    st.write(f"Longitude: {loc['longitude']}")
    map_data = pd.DataFrame({
        'lat': [loc['latitude']],
        'lon': [loc['longitude']]
    })
    st.map(map_data, use_container_width=True)
else:
    st.write("Aguardando permissão de geolocalização..")