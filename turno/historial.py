"""Historial de batallas: registros serializables + exportar/importar JSON.

Aislado a propósito: si más adelante se quiere persistencia real
(Google Sheets, Supabase...) solo hay que sustituir este módulo.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from datetime import datetime

from .motor import Ejercito, Resultado

VERSION = 1
CLAVES_OBLIGATORIAS = {"id", "fecha", "atacante", "defensor", "terreno",
                       "ciudadela", "ganador", "rondas"}


def _ejercito(e: Ejercito) -> dict:
    return {"raza": e.raza.nombre, "tropas": e.tropas,
            "bonificador": e.bonificador, "tercer_ataque_orco": e.tercer_ataque_orco}


def crear_registro(atacante: Ejercito, defensor: Ejercito, terreno: str,
                   ciudadela: bool, resultado: Resultado) -> dict:
    return {
        "id": uuid.uuid4().hex,
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "atacante": _ejercito(atacante),
        "defensor": _ejercito(defensor),
        "terreno": terreno,
        "ciudadela": ciudadela,
        "ganador": resultado.ganador,
        "tropas_finales": {"atacante": resultado.tropas_atacante,
                           "defensor": resultado.tropas_defensor},
        "interrumpida": resultado.interrumpida,
        "rondas": [asdict(r) for r in resultado.rondas],
    }


def exportar_json(registros: list[dict]) -> str:
    return json.dumps({"version": VERSION, "registros": registros},
                      ensure_ascii=False, indent=2)


def importar_json(texto: str) -> list[dict]:
    """Lee un export. Lanza ValueError si el archivo no es válido."""
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON no válido: {e}") from e
    if not isinstance(datos, dict) or not isinstance(datos.get("registros"), list):
        raise ValueError("El archivo no tiene el formato de historial de Turno")
    for r in datos["registros"]:
        if not isinstance(r, dict) or not CLAVES_OBLIGATORIAS <= r.keys():
            raise ValueError("Hay registros incompletos en el archivo")
    return datos["registros"]


def fusionar(existentes: list[dict], nuevos: list[dict]) -> tuple[list[dict], int]:
    """Añade los registros nuevos sin duplicar ids. Devuelve (lista, añadidos)."""
    ids = {r["id"] for r in existentes}
    añadir = [r for r in nuevos if r["id"] not in ids]
    return existentes + añadir, len(añadir)
