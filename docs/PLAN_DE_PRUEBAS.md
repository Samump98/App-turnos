# Plan de pruebas

Ejecutar con `pytest` (355 casos).

| Nivel | Archivo | Qué comprueba |
|---|---|---|
| Unitario | `test_motor.py` | Ganador, empates, bonos negativos, tropas 0, validaciones, no mutación, combate infinito |
| Unitario | `test_motor.py` | Dado fijo Humano/Corrupto (rondas 3 y 6, ambos a la vez, sin consumir tirada) |
| Unitario | `test_motor.py` | Ciudadela: total 2 sin efecto, total 3 daña, cuenta el bonificador, defensor normal |
| Unitario | `test_motor.py` | Tabla de pasivos por raza, rol y terreno; Orco atacante y defensor |
| Paridad | `test_paridad_original.py` | 300 combates aleatorios idénticos a una traducción literal del C++ (misma semilla) |
| Estadístico | `test_estadistica.py` | d4 uniforme, combate simétrico ≈50%, más tropas gana más, el bono del elfo y la ciudadela mueven la tasa |
| Historial | `test_historial.py` | Registro, ida y vuelta JSON, archivos inválidos, sin duplicados |

## Pruebas manuales de interfaz
1. Inicio → "Iniciar batalla" abre la pantalla de batalla.
2. Elegir Orco como atacante muestra "Ataque potenciado"; como defensor, "Defensa debilitada".
3. Los pasivos activos cambian al variar terreno y raza.
4. "Ronda a ronda" muestra el log progresivamente; "De golpe" lo muestra entero.
5. Guardar → aparece en Historial; exportar, vaciar e importar restaura las batallas sin duplicar.
6. Tropas a 0 muestra aviso y no falla.

## Comparación opcional con el ejecutable C++
Para validar contra el programa real, compilar el original con dados controlados y comparar con `simular(..., tirar=Secuencia(...))` usando las mismas tiradas.
