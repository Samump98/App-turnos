# Turno · Simulador de batallas

App en Streamlit para resolver los combates del juego de mesa **Turno** (estrategia por escuadrones).
Elige terreno, razas, tropas y bonificadores, simula el combate y consulta el log de tiradas.

## Arranque rápido

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
streamlit run app.py
pytest
```

## Estructura

| Ruta | Contenido |
|---|---|
| `turno/razas.py` | Razas y terrenos como datos (aquí se añaden pasivos) |
| `turno/motor.py` | Motor de combate en Python puro |
| `turno/historial.py` | Registros, exportar/importar JSON |
| `vistas/` | Pantallas Streamlit: inicio, batalla, historial |
| `tests/` | Tests unitarios, de paridad con el C++ y estadísticos |
| `docs/` | Especificación, arquitectura, plan de pruebas, despliegue |

## Documentación
- [Especificación de reglas](docs/ESPECIFICACION.md)
- [Arquitectura](docs/ARQUITECTURA.md)
- [Plan de pruebas](docs/PLAN_DE_PRUEBAS.md)
- [Despliegue en Streamlit Cloud](docs/DESPLIEGUE.md)
