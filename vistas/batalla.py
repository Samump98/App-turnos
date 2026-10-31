import time

import pandas as pd
import streamlit as st

from turno import (ATACANTE, DEFENSOR, MONTANA, RAZAS, TERRENOS, Ejercito,
                   bonos_pasivos, simular)
from turno.historial import crear_registro

ETIQUETAS = {"atacante": "Gana atacante", "defensor": "Gana defensor",
             "empate": "Empate", "sin_efecto": "Sin efecto (ciudadela)"}


def panel(titulo: str, clave: str) -> Ejercito:
    st.subheader(titulo)
    raza = RAZAS[st.selectbox("Raza", list(RAZAS), key=f"{clave}_raza",
                              format_func=lambda i: RAZAS[i].nombre)]
    tropas = st.number_input("Tropas", 0, 999, 10, 1, key=f"{clave}_tropas")
    bon = st.number_input("Bonificador (cartas, etc.)", -20, 20, 0, 1, key=f"{clave}_bon")
    tercer = False
    if raza.bono_tercer_ataque:
        etiqueta = ("Ataque potenciado (3.er ataque)" if clave == "atq"
                    else "Defensa debilitada (tras ataque potenciado)")
        tercer = st.checkbox(etiqueta, key=f"{clave}_orco")
    return Ejercito(raza, int(tropas), int(bon), tercer)


def mostrar_pasivos(ej: Ejercito, rol: str, terreno: str):
    bonos = bonos_pasivos(ej, rol, terreno)
    if bonos:
        st.caption("Pasivos activos: " + " · ".join(f"{n} ({b:+d})" for n, b in bonos))
    else:
        st.caption("Sin pasivos activos")


def tabla(res) -> pd.DataFrame:
    return pd.DataFrame([{
        "Ronda": r.numero, "Dado atq": r.dado_ataque, "Dado def": r.dado_defensa,
        "Total atq": r.total_ataque, "Total def": r.total_defensa,
        "Resultado": ETIQUETAS[r.resultado],
        "Tropas atq": r.tropas_atacante, "Tropas def": r.tropas_defensor,
        "Notas": "; ".join(r.notas),
    } for r in res.rondas])


st.title("⚔️ Batalla")

c1, c2 = st.columns(2)
terreno = c1.selectbox("Terreno", TERRENOS)
ciudadela = c2.checkbox("Combate en ciudadela")

col_a, col_d = st.columns(2)
with col_a:
    atq = panel("Atacante", "atq")
    mostrar_pasivos(atq, ATACANTE, terreno)
with col_d:
    dfn = panel("Defensor", "dfn")
    mostrar_pasivos(dfn, DEFENSOR, terreno)

modo = st.radio("Mostrar log", ["De golpe", "Ronda a ronda"], horizontal=True)
animar = False

if st.button("Simular batalla", type="primary"):
    res = simular(atq, dfn, terreno, ciudadela)
    st.session_state["ultima"] = {"res": res, "atq": atq, "dfn": dfn, "terreno": terreno,
                                  "ciudadela": ciudadela, "guardada": False}
    animar = modo == "Ronda a ronda"

ultima = st.session_state.get("ultima")
if ultima:
    res = ultima["res"]
    st.divider()
    if res.ganador is None and not res.rondas:
        st.warning("No hay combate: algún ejército no tiene tropas.")
    elif res.interrumpida:
        st.warning(f"Combate interrumpido tras {len(res.rondas)} rondas sin resolverse "
                   "(el atacante no puede dañar en ciudadela con esos bonos).")
    else:
        nombre = ultima["atq"].raza.nombre if res.ganador == ATACANTE else ultima["dfn"].raza.nombre
        st.success(f"🏆 Gana el **{res.ganador}** ({nombre}) en {len(res.rondas)} rondas")
    m1, m2 = st.columns(2)
    m1.metric("Tropas atacante", res.tropas_atacante)
    m2.metric("Tropas defensor", res.tropas_defensor)

    df = tabla(res)
    if animar and len(df):
        hueco = st.empty()
        pausa = min(0.6, 6 / len(df))
        for i in range(1, len(df) + 1):
            hueco.dataframe(df.iloc[:i], hide_index=True)
            time.sleep(pausa)
    elif len(df):
        st.dataframe(df, hide_index=True)

    if st.button("Guardar en historial", disabled=ultima["guardada"]) and not ultima["guardada"]:
        st.session_state["historial"].append(
            crear_registro(ultima["atq"], ultima["dfn"], ultima["terreno"],
                           ultima["ciudadela"], res))
        ultima["guardada"] = True
    if ultima["guardada"]:
        st.success("Guardada en el historial ✔")
