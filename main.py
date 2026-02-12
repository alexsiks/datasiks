import streamlit as st
from streamlit_geolocation import streamlit_geolocation

st.title("Geolocalização")

loc = streamlit_geolocation()

st.write("Sua localização:")
if loc:
    st.write(f"Latitude: {loc['coords']['latitude']}")
    st.write(f"Longitude: {loc['coords']['longitude']}")
    st.map(data=None, zoom=None, use_container_width=True)
else:
    st.write("Aguardando permissão de geolocalização..")