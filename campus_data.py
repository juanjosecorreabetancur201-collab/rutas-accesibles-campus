"""Datos del campus (mapa simplificado) para la Actividad 7.

El campus se modela como una cuadricula de 10 columnas x 6 filas = 60 puntos de
interes. De las 104 conexiones posibles de la cuadricula se quitan 14 (barreras
fisicas, edificios, desniveles) y quedan exactamente 90 tramos.

IMPORTANTE: los nombres y coordenadas son una simplificacion. Para la
sustentacion conviene reemplazarlos por los de tu campus real: basta con
editar NOMBRES, la funcion _coord y los conjuntos de abajo; el resto del
codigo no cambia.
"""
import math

COLUMNAS, FILAS = 10, 6

NOMBRES = [
    # fila 0
    "Entrada Principal", "Porteria Norte", "Bloque A", "Bloque B", "Cafeteria Central",
    "Biblioteca", "Auditorio", "Bloque C", "Parqueadero Norte", "Coliseo",
    # fila 1
    "Plazoleta de Banderas", "Bienestar Universitario", "Aula Maxima", "Sala de Profesores",
    "Admisiones", "Hemeroteca", "Lab. Fluidos e Hidraulica", "Lab. Geotecnia y Pavimentos", "Bloque D", "Gimnasio",
    # fila 2
    "Tesoreria", "Registro Academico", "Lab. Sistemas", "Sala de Computo 1", "Sala de Computo 2",
    "Media LAB Aula Mac", "Cancha Multiple", "Bloque E", "Clinica Odontologica", "Piscina",
    # fila 3
    "Bloque F", "Consultorio Psicologico", "NAF Contable y Fiscal", "Jardin Botanico", "Cafeteria Sur",
    "Kiosco", "Sala de Estudio", "Bloque G", "Estudio de Television", "Vivero",
    # fila 4
    "Capilla", "Consultorio Juridico", "Bloque H", "Aula 401", "Laboratorio de Redes",
    "Fotocopiadora", "Impact Campus", "Bloque I", "Cancha de Tenis", "Zona Verde",
    # fila 5
    "Porteria Sur", "Parqueadero Sur", "Bloque J", "Teatro al Aire Libre", "Estudio de Radio",
    "Aula 501", "Bloque K", "Bloque L", "Porteria Oriente", "Bodega",
]
assert len(NOMBRES) == COLUMNAS * FILAS == 60


def _coord(i):
    """Coordenadas (x, y) en metros. Cuadricula de ~45 x 40 m con desfases fijos."""
    r, c = divmod(i, COLUMNAS)
    x = c * 45 + ((r * 7 + c * 3) % 5) * 4
    y = r * 40 + ((c * 5 + r * 2) % 4) * 5
    return float(x), float(y)


COORDS = [_coord(i) for i in range(60)]

# Conexiones de la cuadricula que NO existen (14), asi quedan 104 - 14 = 90 tramos.
QUITADOS = {
    (2, 3), (14, 15), (26, 27), (33, 34), (45, 46), (57, 58),
    (6, 16), (8, 18), (21, 31), (28, 38), (35, 45), (37, 47), (42, 52), (22, 32),
}

# Tramos con escalera sin rampa (no accesibles).
ESCALERAS = {(11, 12), (21, 22), (31, 41), (35, 36), (46, 47), (55, 56)}

# Tramos en obra (cerrados para todos).
OBRAS = {(12, 22), (24, 25), (43, 44), (53, 54)}

# Puertas que se cierran: tramo -> minuto del dia en que cierra (18:00 = 1080).
PUERTAS = {(22, 23): 18 * 60, (13, 14): 18 * 60, (24, 34): 18 * 60}

# Pendientes fijas (%) para tramos especialmente empinados (> 8 % no es accesible).
PENDIENTES_ALTAS = {(40, 41): 11.0, (25, 26): 10.0}


def _par(a, b):
    return (a, b) if a < b else (b, a)


def _dist_euclid(a, b):
    (x1, y1), (x2, y2) = COORDS[a], COORDS[b]
    return math.hypot(x1 - x2, y1 - y2)


def tramos_crudos():
    """Devuelve la lista de 90 tramos como tuplas
    (a, b, dist_m, pendiente_pct, escalera, en_obra, cierra_min_o_None).

    La distancia recorrida es la euclidiana multiplicada por un factor >= 1
    (los caminos no son rectos) y redondeada hacia ARRIBA, de modo que
    dist >= distancia en linea recta siempre. Eso es lo que hace admisible
    la heuristica (ver heuristica.md).
    """
    pares = []
    for r in range(FILAS):
        for c in range(COLUMNAS):
            i = r * COLUMNAS + c
            if c + 1 < COLUMNAS:
                pares.append((i, i + 1))
            if r + 1 < FILAS:
                pares.append((i, i + COLUMNAS))
    pares = [p for p in pares if p not in QUITADOS]

    tramos = []
    for a, b in pares:
        factor = 1.0 + ((a * 5 + b * 3) % 4) * 0.05  # 1.00, 1.05, 1.10 o 1.15
        dist = math.ceil(_dist_euclid(a, b) * factor * 10) / 10
        pend = PENDIENTES_ALTAS.get((a, b), float((a * 3 + b * 5) % 9))  # 0..8 %
        tramos.append((a, b, dist, pend, (a, b) in ESCALERAS, (a, b) in OBRAS,
                       PUERTAS.get((a, b))))
    assert len(tramos) == 90, len(tramos)
    return tramos
