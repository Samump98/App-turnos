import streamlit as st

st.set_page_config(page_title="Turno · Batallas", page_icon="⚔️", layout="centered")

if "historial" not in st.session_state:
    st.session_state["historial"] = []

pagina = st.navigation([
    st.Page("vistas/inicio.py", title="Inicio", icon="🏠", default=True),
    st.Page("vistas/batalla.py", title="Batalla", icon="⚔️"),
    st.Page("vistas/historial.py", title="Historial", icon="📜"),
])
pagina.run()
