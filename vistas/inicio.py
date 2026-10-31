import streamlit as st

st.title("⚔️ Turno")
st.caption("Simulador de batallas entre escuadrones")

if st.button("Iniciar batalla", type="primary"):
    st.switch_page("vistas/batalla.py")

n = len(st.session_state.get("historial", []))
st.write(f"📜 Batallas guardadas en esta sesión: **{n}**")
st.caption("Menú lateral (☰ en móvil) → Historial")
