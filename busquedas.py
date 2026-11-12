"""BFS, DFS y A* sobre cualquiera de las tres representaciones de grafo.py.

Convenciones comunes (para que la tabla de nodos explorados sea comparable):
- "Nodo explorado" = nodo que sale de la frontera y se procesa (incluido el destino).
- Todos marcan nodos visitados, asi que no se cuelgan con ciclos.
- Todos respetan las mismas restricciones: obras, accesibilidad y horario de puertas.
- Si no hay ruta, devuelven un Resultado con ruta=None y un motivo legible; no lanzan
  excepcion ni devuelven una lista vacia sin explicacion.
"""
import heapq
import math
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, List, Optional

import campus_data
from grafo import Grafo


def hhmm(minutos: Optional[int]) -> str:
    return "sin horario" if minutos is None else f"{minutos // 60:02d}:{minutos % 60:02d}"


@dataclass
class Resultado:
    algoritmo: str
    origen: int
    destino: int
    ruta: Optional[List[int]]
    costo: Optional[float]
    explorados: int
    orden: List[int] = field(default_factory=list)
    motivo: str = ""

    @property
    def encontrada(self) -> bool:
        return self.ruta is not None

    def describir(self) -> str:
        nom = campus_data.NOMBRES
        if not self.encontrada:
            return f"[{self.algoritmo}] SIN RUTA {nom[self.origen]} -> {nom[self.destino]}: {self.motivo}"
        camino = " -> ".join(nom[i] for i in self.ruta)
        return (f"[{self.algoritmo}] {len(self.ruta) - 1} tramos, costo {self.costo:.1f}, "
                f"{self.explorados} nodos explorados\n    {camino}")


def _validar(g: Grafo, s: int, t: int):
    for x in (s, t):
        if not (0 <= x < g.n):
            raise ValueError(f"Nodo {x} fuera de rango (0..{g.n - 1})")  # error de uso, no "sin ruta"


def costo_ruta(g: Grafo, ruta: List[int]) -> float:
    return sum(g.tramo(u, v).costo for u, v in zip(ruta, ruta[1:]))


def _reconstruir(padre, s, t):
    ruta = [t]
    while ruta[-1] != s:
        ruta.append(padre[ruta[-1]])
    return ruta[::-1]


def _sin_ruta(nombre, g, s, t, explorados, orden, hora, solo_acc):
    modo = "accesible" if solo_acc else "cualquiera"
    motivo = (f"no existe ruta {modo} a las {hhmm(hora)} "
              f"(se exploraron {explorados} nodos alcanzables y ninguno llega al destino).")
    return Resultado(nombre, s, t, None, None, explorados, orden, motivo)


def _resultado(nombre, g, s, t, padre, explorados, orden):
    ruta = _reconstruir(padre, s, t)
    return Resultado(nombre, s, t, ruta, costo_ruta(g, ruta), explorados, orden)


def bfs(g: Grafo, s: int, t: int, hora: Optional[int] = None, solo_accesible: bool = True) -> Resultado:
    """Minimiza el NUMERO de tramos, no el costo."""
    _validar(g, s, t)
    visitado = {s}                       # marcado al encolar
    padre = {s: s}
    cola = deque([s])
    orden = []
    while cola:
        u = cola.popleft()
        orden.append(u)
        if u == t:
            return _resultado("BFS", g, s, t, padre, len(orden), orden)
        for v, tr in g.vecinos(u):
            if v not in visitado and tr.transitable(hora, solo_accesible):
                visitado.add(v)
                padre[v] = u
                cola.append(v)
    return _sin_ruta("BFS", g, s, t, len(orden), orden, hora, solo_accesible)


def dfs(g: Grafo, s: int, t: int, hora: Optional[int] = None, solo_accesible: bool = True) -> Resultado:
    """Encuentra UNA ruta (no necesariamente corta). Iterativo para no desbordar la pila."""
    _validar(g, s, t)
    visitado = set()                     # marcado al desapilar
    padre = {}
    pila = [(s, s)]
    orden = []
    while pila:
        u, p = pila.pop()
        if u in visitado:
            continue
        visitado.add(u)
        padre[u] = p
        orden.append(u)
        if u == t:
            return _resultado("DFS", g, s, t, padre, len(orden), orden)
        for v, tr in g.vecinos(u):
            if v not in visitado and tr.transitable(hora, solo_accesible):
                pila.append((v, u))
    return _sin_ruta("DFS", g, s, t, len(orden), orden, hora, solo_accesible)


def heuristica_euclidiana(u: int, t: int) -> float:
    """Distancia en linea recta (metros) entre u y t. Admisible: ver heuristica.md."""
    (x1, y1), (x2, y2) = campus_data.COORDS[u], campus_data.COORDS[t]
    return math.hypot(x1 - x2, y1 - y2)


def heuristica_cero(u: int, t: int) -> float:
    return 0.0


def astar(g: Grafo, s: int, t: int, hora: Optional[int] = None, solo_accesible: bool = True,
          h: Callable[[int, int], float] = heuristica_euclidiana, nombre: str = "A*") -> Resultado:
    """A* con costo g = suma de tramo.costo y f = g + h. Con h=0 equivale a Dijkstra."""
    _validar(g, s, t)
    mejor_g = {s: 0.0}
    padre = {s: s}
    cerrado = set()
    contador = 0                         # desempate estable en el heap
    heap = [(h(s, t), contador, s)]
    orden = []
    while heap:
        _, _, u = heapq.heappop(heap)
        if u in cerrado:                 # entrada obsoleta del heap
            continue
        cerrado.add(u)
        orden.append(u)
        if u == t:
            return _resultado(nombre, g, s, t, padre, len(orden), orden)
        for v, tr in g.vecinos(u):
            if v in cerrado or not tr.transitable(hora, solo_accesible):
                continue
            ng = mejor_g[u] + tr.costo
            if ng < mejor_g.get(v, math.inf):
                mejor_g[v] = ng
                padre[v] = u
                contador += 1
                heapq.heappush(heap, (ng + h(v, t), contador, v))
    return _sin_ruta(nombre, g, s, t, len(orden), orden, hora, solo_accesible)


def dijkstra(g, s, t, hora=None, solo_accesible=True) -> Resultado:
    return astar(g, s, t, hora, solo_accesible, h=heuristica_cero, nombre="Dijkstra (A* con h=0)")


def comparar(g, s, t, hora=None, solo_accesible=True) -> str:
    """Tabla de nodos explorados para la misma consulta."""
    res = [bfs(g, s, t, hora, solo_accesible), dfs(g, s, t, hora, solo_accesible),
           dijkstra(g, s, t, hora, solo_accesible), astar(g, s, t, hora, solo_accesible)]
    nom = campus_data.NOMBRES
    cab = f"Consulta: {nom[s]} -> {nom[t]} a las {hhmm(hora)} (solo accesible={solo_accesible})"
    lin = [cab, f"{'Algoritmo':<24}{'Explorados':>11}{'Tramos':>8}{'Costo':>10}  Optimo en costo"]
    mejor = min((r.costo for r in res if r.encontrada), default=None)
    for r in res:
        if r.encontrada:
            opt = "si" if abs(r.costo - mejor) < 1e-9 else "no"
            lin.append(f"{r.algoritmo:<24}{r.explorados:>11}{len(r.ruta) - 1:>8}{r.costo:>10.1f}  {opt}")
        else:
            lin.append(f"{r.algoritmo:<24}{r.explorados:>11}{'-':>8}{'-':>10}  sin ruta")
    return "\n".join(lin)
