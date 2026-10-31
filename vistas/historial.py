import pandas as pd
import streamlit as st

from turno.historial import exportar_json, fusionar, importar_json

st.title("📜 Historial")
registros = st.session_state["historial"]

st.caption("El historial vive en esta sesión: si recargas la página se pierde. "
           "Exporta un archivo para conservarlo e impórtalo cuando quieras.")

if registros:
    for r in reversed(registros):
        a, d = r["atacante"], r["defensor"]
        ganador = {"atacante": "Atacante", "defensor": "Defensor"}.get(r["ganador"], "Sin ganador")
        titulo = f"{r['fecha'].replace('T', ' ')} · {a['raza']} vs {d['raza']} · Gana: {ganador}"
        with st.expander(titulo):
            st.write(f"Terreno: **{r['terreno']}** · Ciudadela: **{'Sí' if r['ciudadela'] else 'No'}** · "
                     f"Tropas iniciales: {a['tropas']} vs {d['tropas']} · "
                     f"Bonificadores: {a['bonificador']:+d} / {d['bonificador']:+d}")
            if r["rondas"]:
                st.dataframe(pd.DataFrame(r["rondas"]).drop(columns=["notas"]), hide_index=True)
            if st.button("Borrar", key=f"borrar_{r['id']}"):
                st.session_state["historial"] = [x for x in registros if x["id"] != r["id"]]
                st.rerun()
else:
    st.info("Todavía no hay batallas guardadas.")

st.divider()
st.download_button("Exportar historial (JSON)", exportar_json(registros),
                   file_name="historial_turno.json", mime="application/json",
                   disabled=not registros)

archivo = st.file_uploader("Importar historial", type="json")
if archivo is not None and st.button("Importar archivo"):
    try:
        nuevos = importar_json(archivo.getvalue().decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        st.error(f"No se pudo importar: {e}")
    else:
        st.session_state["historial"], añadidos = fusionar(registros, nuevos)
        st.success(f"Importadas {añadidos} batallas nuevas")
        st.rerun()

if registros and st.button("Vaciar historial"):
    st.session_state["historial"] = []
    st.rerun()
