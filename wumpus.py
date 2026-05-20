"""
============================================================
  SIMULADOR DEL MUNDO DE WUMPUS
  Materia: Inteligencia Artificial
  Descripción: Mundo n×n con generación aleatoria, percep-
  ciones limitadas y menú interactivo para el usuario.
  Alumno: Gonzalo Sebastian Perez Moncayo
============================================================

INSTRUCCIONES DE EJECUCIÓN:
  
  $ python wumpus_world.py

  Al iniciar puedes elegir el tamaño del mundo (defecto 4×4)
  y una semilla aleatoria para reproducibilidad.
"""

import random
import os
import sys

VACIO   = "."
POZO    = "P"
WUMPUS  = "W"
ORO     = "G"
AGENTE  = "A"

BRISA      = "Brisa"
HEDOR      = "Hedor"
RESPLANDOR = "Resplandor"
GOLPE      = "Golpe"
GRITO      = "Grito"

def generar_mundo(n: int, semilla: int) -> dict:
    """
    Crea la matriz del mundo n×n y coloca aleatoriamente:
      - k pozos  (k = 20% de n²)
      - 1 Wumpus
      - 1 Oro
    Garantiza que (0,0) esté libre.
    Devuelve un dict con la matriz y posiciones especiales.
    """
    rng = random.Random(semilla)

    grid = [[set() for _ in range(n)] for _ in range(n)]

    celdas_disponibles = [
        (r, c) for r in range(n) for c in range(n) if not (r == 0 and c == 0)
    ]
    rng.shuffle(celdas_disponibles)

    num_pozos = max(1, int(n * n * 0.20))

    for i in range(min(num_pozos, len(celdas_disponibles))):
        r, c = celdas_disponibles[i]
        grid[r][c].add(POZO)

    libres = [
        (r, c) for r in range(n) for c in range(n)
        if not (r == 0 and c == 0) and POZO not in grid[r][c]
    ]
    rng.shuffle(libres)

    pos_wumpus = libres[0]
    pos_oro    = libres[1]

    grid[pos_wumpus[0]][pos_wumpus[1]].add(WUMPUS)
    grid[pos_oro[0]][pos_oro[1]].add(ORO)

    return {
        "grid": grid,
        "n": n,
        "pos_wumpus": pos_wumpus,
        "pos_oro": pos_oro,
        "semilla": semilla,
    }

def calcular_percepciones(mundo: dict, r: int, c: int,
                           wumpus_vivo: bool, tiene_oro: bool) -> list:
    """
    Devuelve la lista de percepciones activas en la celda (r, c).
    """
    n    = mundo["n"]
    grid = mundo["grid"]
    adyacentes = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]

    percepciones = []

    for ar, ac in adyacentes:
        if 0 <= ar < n and 0 <= ac < n:
            if POZO in grid[ar][ac]:
                if BRISA not in percepciones:
                    percepciones.append(BRISA)
            if WUMPUS in grid[ar][ac] and wumpus_vivo:
                if HEDOR not in percepciones:
                    percepciones.append(HEDOR)

    if ORO in grid[r][c] and not tiene_oro:
        percepciones.append(RESPLANDOR)

    return percepciones

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_grid_agente(mundo: dict, agente_r: int, agente_c: int,
                         visitadas: set):
    """
    Muestra el mapa desde la perspectiva del agente:
    solo celdas visitadas y posición actual son visibles.
    """
    n = mundo["n"]
    print("\n  " + "  ".join(str(c+1) for c in range(n)))
    for r in range(n - 1, -1, -1):
        fila = f"{r+1} "
        for c in range(n):
            if r == agente_r and c == agente_c:
                fila += " A "
            elif (r, c) in visitadas:
                fila += " · "
            else:
                fila += " ? "
        print(fila)
    print()


def mostrar_grid_completo(mundo: dict, agente_r: int, agente_c: int,
                           wumpus_vivo: bool):
    """
    Muestra el mapa COMPLETO (para el resumen final).
    """
    n    = mundo["n"]
    grid = mundo["grid"]
    print("\n  " + "  ".join(str(c+1) for c in range(n)))
    for r in range(n - 1, -1, -1):
        fila = f"{r+1} "
        for c in range(n):
            celda = grid[r][c]
            if r == agente_r and c == agente_c:
                simbolo = " A "
            elif POZO in celda:
                simbolo = " P "
            elif WUMPUS in celda:
                simbolo = (" W " if wumpus_vivo else "💀 ")
            elif ORO in celda:
                simbolo = " G "
            else:
                simbolo = " . "
            fila += simbolo
        print(fila)
    print()


def mostrar_estado(mundo: dict, agente_r: int, agente_c: int,
                   visitadas: set, percepciones: list,
                   historial: list, tiene_oro: bool,
                   flecha_disp: bool, wumpus_vivo: bool,
                   grito: bool):
    limpiar()
    print("=" * 50)
    print("   MUNDO DE WUMPUS")
    print(f"   Tamaño: {mundo['n']}×{mundo['n']}  |  Semilla: {mundo['semilla']}")
    print("=" * 50)

    mostrar_grid_agente(mundo, agente_r, agente_c, visitadas)

    print(f"  Posición actual : ({agente_c+1}, {agente_r+1})")
    print(f"  Oro en mochila  : {'SÍ ✓' if tiene_oro else 'No'}")
    print(f"  Flecha          : {'Disponible' if flecha_disp else 'Usada'}")
    print()

    print("  PERCEPCIONES:")
    if percepciones:
        for p in percepciones:
            print(f"    • {p}")
    else:
        print("    (ninguna — celda segura)")
    if grito:
        print(f"    • {GRITO} — ¡el Wumpus ha sido eliminado!")
    print()

    print("  HISTORIAL (últimas 5 acciones):")
    ultimas = historial[-5:]
    for entrada in ultimas:
        print(f"    {entrada}")
    print()


def menu_acciones(puede_tomar: bool, puede_salir: bool,
                  flecha_disp: bool) -> str:
    print("  ACCIONES DISPONIBLES:")
    print("    M  → Mover")
    if flecha_disp:
        print("    D  → Disparar flecha")
    if puede_tomar:
        print("    T  → Tomar oro")
    if puede_salir:
        print("    S  → Salir del mundo")
    print("    Q  → Abandonar partida")
    print()
    return input("  Elige acción: ").strip().upper()


def pedir_direccion() -> tuple:
    print("  Dirección: [N]orte  [S]ur  [E]ste  [O]este")
    d = input("  Dirección: ").strip().upper()
    direcciones = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "O": (0, -1)}
    mapa = {"N": (1, 0), "S": (-1, 0), "E": (0, 1), "O": (0, -1)}
    return mapa.get(d, None), d

def jugar(mundo: dict):
    n         = mundo["n"]
    grid      = mundo["grid"]
    agente_r  = 0
    agente_c  = 0
    tiene_oro = False
    flecha    = True
    wumpus_v  = True
    grito     = False
    visitadas = {(0, 0)}
    historial = []  
    resultado = None

    while True:
        percepciones = calcular_percepciones(
            mundo, agente_r, agente_c, wumpus_v, tiene_oro
        )

        mostrar_estado(mundo, agente_r, agente_c, visitadas,
                       percepciones, historial, tiene_oro,
                       flecha, wumpus_v, grito)
        grito = False  # se muestra solo un turno

        puede_tomar = RESPLANDOR in percepciones and not tiene_oro
        puede_salir = (agente_r == 0 and agente_c == 0)

        accion = menu_acciones(puede_tomar, puede_salir, flecha)

        if accion == "M":
            delta, letra = pedir_direccion()
            if delta is None:
                historial.append(f"Dirección inválida.")
                continue
            dr, dc = delta
            nr, nc = agente_r + dr, agente_c + dc

            if not (0 <= nr < n and 0 <= nc < n):
                historial.append(
                    f"[{letra}] Intento mover → GOLPE con pared en ({agente_c+1},{agente_r+1})"
                )
                percepciones_up = list(percepciones)
                if GOLPE not in percepciones_up:
                    percepciones_up.append(GOLPE)
                mostrar_estado(mundo, agente_r, agente_c, visitadas,
                               percepciones_up, historial, tiene_oro,
                               flecha, wumpus_v, False)
                input("  [Enter para continuar]")
                continue

            agente_r, agente_c = nr, nc
            visitadas.add((agente_r, agente_c))
            nuevas = calcular_percepciones(
                mundo, agente_r, agente_c, wumpus_v, tiene_oro
            )
            historial.append(
                f"Mover {letra} → ({agente_c+1},{agente_r+1}) | percepciones: "
                + (", ".join(nuevas) if nuevas else "ninguna")
            )

            if POZO in grid[agente_r][agente_c]:
                limpiar()
                mostrar_grid_completo(mundo, agente_r, agente_c, wumpus_v)
                print("  💀 ¡Caíste en un pozo! Juego terminado.\n")
                resultado = "MUERTE_POZO"
                break
            if WUMPUS in grid[agente_r][agente_c] and wumpus_v:
                limpiar()
                mostrar_grid_completo(mundo, agente_r, agente_c, wumpus_v)
                print("  💀 ¡El Wumpus te devoró! Juego terminado.\n")
                resultado = "MUERTE_WUMPUS"
                break

        elif accion == "D" and flecha:
            delta, letra = pedir_direccion()
            if delta is None:
                continue
            flecha = False
            dr, dc = delta
            tr, tc = agente_r + dr, agente_c + dc
            impacto = (
                0 <= tr < n and 0 <= tc < n
                and WUMPUS in grid[tr][tc]
                and wumpus_v
            )
            if impacto:
                wumpus_v = False
                grito    = True
                historial.append(
                    f"Disparar {letra} → ({tc+1},{tr+1}) | ¡WUMPUS ELIMINADO! Grito escuchado."
                )
            else:
                historial.append(
                    f"Disparar {letra} → sin impacto. Flecha perdida."
                )

        elif accion == "T" and puede_tomar:
            tiene_oro = True
            grid[agente_r][agente_c].discard(ORO)
            historial.append(
                f"Tomar oro en ({agente_c+1},{agente_r+1}) ✓"
            )

        elif accion == "S" and puede_salir:
            resultado = "ESCAPE_CON_ORO" if tiene_oro else "ESCAPE_SIN_ORO"
            break

        elif accion == "Q":
            resultado = "ABANDONO"
            break

        else:
            historial.append("Acción no disponible en este momento.")

    return resultado, historial, agente_r, agente_c, wumpus_v

def mostrar_resumen(mundo: dict, resultado: str, historial: list,
                    agente_r: int, agente_c: int, wumpus_vivo: bool):
    limpiar()
    print("=" * 50)
    print("   RESUMEN FINAL")
    print("=" * 50)

    mensajes = {
        "ESCAPE_CON_ORO"  : "¡Victoria! Escapaste con el oro.",
        "ESCAPE_SIN_ORO"  : "Saliste con vida, pero sin el oro.",
        "MUERTE_POZO"     : "Caíste en un pozo.",
        "MUERTE_WUMPUS"   : "Fuiste devorado por el Wumpus.",
        "ABANDONO"        : "Partida abandonada.",
    }
    print(f"\n  Resultado: {mensajes.get(resultado, resultado)}\n")

    print("  MAPA INICIAL (estado real del mundo):")
    mostrar_grid_completo(mundo, agente_r, agente_c, wumpus_vivo)

    print(f"  REGISTRO DE DECISIONES ({len(historial)} acciones):")
    for i, entrada in enumerate(historial, 1):
        print(f"    {i:>3}. {entrada}")

    print("\n" + "=" * 50)

def main():
    limpiar()
    print("=" * 50)
    print("   MUNDO DE WUMPUS — Simulador")
    print("=" * 50)
    print()

    while True:
        try:
            n = int(input("  Tamaño del mundo (defecto 4): ") or "4")
            if n < 2:
                print("  El tamaño mínimo es 2.")
                continue
            break
        except ValueError:
            print("  Ingresa un número entero.")

    while True:
        try:
            semilla_raw = input("  Semilla aleatoria (defecto 42): ") or "42"
            semilla = int(semilla_raw)
            break
        except ValueError:
            print("  Ingresa un número entero.")

    while True:
        mundo = generar_mundo(n, semilla)
        resultado, historial, fin_r, fin_c, wumpus_v = jugar(mundo)
        mostrar_resumen(mundo, resultado, historial, fin_r, fin_c, wumpus_v)

        otra = input("\n  ¿Jugar de nuevo? [s/N]: ").strip().lower()
        if otra != "s":
            break
        semilla_raw = input("  Nueva semilla (Enter = misma): ").strip()
        if semilla_raw:
            try:
                semilla = int(semilla_raw)
            except ValueError:
                pass

    print("\n  ¡Hasta luego!\n")


if __name__ == "__main__":
    main()
