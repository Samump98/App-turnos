# Especificación de reglas

## Combate
1. Cada ronda, atacante y defensor tiran un d4 (1-4). **Total = dado + bonificador manual + pasivos.**
2. Gana la ronda el total mayor; el perdedor pierde 1 tropa. **Empate: no pasa nada**, pero la ronda cuenta.
3. El combate acaba cuando un ejército llega a 0 tropas. Si alguno empieza con 0, no hay combate.
4. Orden de tirada: primero atacante, luego defensor (igual que el C++ original).
5. Seguridad: máximo 1000 rondas. Si se alcanza, el combate se marca como *interrumpido*
   (solo puede ocurrir en ciudadela con bonos muy negativos del atacante).

## Ciudadela
El atacante solo elimina una tropa si gana la ronda **y su total (dado + bonos) es 3 o más**.
Si gana con menos, la ronda queda sin efecto. El defensor gana con normalidad.

## Terrenos
Llanura (sin efecto), Montaña, Bosque, Río.

## Pasivos de raza
| Raza | Efecto |
|---|---|
| Humano | Rondas 3, 6, 9...: su dado no se tira y vale 4 |
| Corrupto | Igual que Humano |
| Enano | +1 atacando **y** defendiendo en Montaña |
| Elfo | +1 siempre que ataca. +1 defendiendo en Bosque (*) |
| Elfo oscuro | +1 siempre que defiende |
| Orco | Ver abajo |

Si ambos bandos tienen dado fijo en la misma ronda, ambos sacan 4.

### Orco (control manual)
Al elegir Orco aparece una casilla:
- **Atacante → "Ataque potenciado"**: +2 al ataque.
- **Defensor → "Defensa debilitada"**: -1 a la defensa, solo si el terreno es Montaña.

## Bonificador manual
Entero (positivo o negativo) por ejército, para cartas u otros efectos. Se suma a los pasivos.

## Supuestos pendientes de confirmar
- (*) Las notas hablaban de elfos "en determinadas áreas": se ha asumido **Bosque**. Es un cambio de una línea en `razas.py`.
- La casilla del orco se aplica a **toda la batalla simulada**, no solo a una ronda concreta.
- Los efectos de cartas se introducen siempre como bonificador manual.
