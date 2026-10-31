# Arquitectura

```
app.py            navegación (st.navigation) y estado de sesión
vistas/           interfaz: sin reglas de juego
turno/motor.py    reglas de combate, sin dependencias de Streamlit
turno/razas.py    datos de razas y terrenos
turno/historial.py serialización del historial
```

## Decisiones
- **Lógica separada de la interfaz.** El motor es Python puro y se testea sin arrancar Streamlit.
- **Razas como datos.** Un pasivo nuevo es un campo de `Raza`; si el pasivo es de un tipo nuevo, solo se amplía `bonos_pasivos()`.
- **Dado inyectable.** `simular(..., tirar=...)` recibe una función; los tests pasan secuencias fijas o con semilla.
- **Historial en sesión + JSON.** Streamlit Cloud no guarda archivos de forma duradera. `historial.py` está aislado para sustituirlo por Google Sheets o Supabase sin tocar el resto.
- **Resultado en `session_state`.** Tras pulsar "Guardar" Streamlit reejecuta el script; guardar la última simulación evita perderla.
- **Navegación.** Home → Batalla → Historial desde el menú lateral (☰ en móvil).

## Cómo añadir una raza
Añadir una entrada a `RAZAS` en `turno/razas.py` y, si introduce un efecto nuevo, un test en `tests/test_motor.py`.
