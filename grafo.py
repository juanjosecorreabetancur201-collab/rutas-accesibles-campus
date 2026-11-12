"""Tres representaciones del grafo del campus: matriz, lista y matriz dispersa (CSR).

Todo esta construido a mano: no se usa networkx ni scipy.sparse.
Las tres exponen la misma interfaz (vecinos / tramo) para que BFS, DFS y A*
funcionen igual sobre cualquiera de ellas.

Ejecutar `python grafo.py` imprime la tabla de memoria comparada.
"""
import tracemalloc
from dataclasses import dataclass
from typing import Iterator, Optional, Tuple

import campus_data

PENDIENTE_MAX = 8.0  # % maxima para considerar un tramo accesible (referencia usual de rampas)


@dataclass(frozen=True)
class Tramo:
    """Arista no dirigida con sus atributos."""
    a: int
    b: int
    dist: float            # metros reales caminando
    pendiente: float       # porcentaje
    escalera: bool         # escalera sin rampa
    en_obra: bool          # tramo cerrado por obra
    cierra: Optional[int]  # minuto del dia en que se cierra la puerta (None = siempre abierto)

    @property
    def accesible(self) -> bool:
        return (not self.escalera) and self.pendiente <= PENDIENTE_MAX

    @property
    def costo(self) -> float:
        """Costo = metros * (1 + pendiente/10). Siempre >= dist (pendiente >= 0)."""
        return self.dist * (1.0 + self.pendiente / 10.0)

    def transitable(self, hora_min: Optional[int] = None, solo_accesible: bool = True) -> bool:
        if self.en_obra:
            return False
        if solo_accesible and not self.accesible:
            return False
        if self.cierra is not None and hora_min is not None and hora_min >= self.cierra:
            return False
        return True


def cargar_tramos():
    return [Tramo(*t) for t in campus_data.tramos_crudos()]


class Grafo:
    """Interfaz comun."""
    nombre = "base"

    def __init__(self, n: int):
        self.n = n

    def vecinos(self, u: int) -> Iterator[Tuple[int, Tramo]]:
        raise NotImplementedError

    def tramo(self, u: int, v: int) -> Optional[Tramo]:
        for w, t in self.vecinos(u):
            if w == v:
                return t
        return None

    def num_aristas_dirigidas(self) -> int:
        return sum(1 for u in range(self.n) for _ in self.vecinos(u))


class MatrizAdyacencia(Grafo):
    nombre = "Matriz n x n"

    def __init__(self, n, tramos):
        super().__init__(n)
        self.m = [[None] * n for _ in range(n)]
        for t in tramos:
            self.m[t.a][t.b] = t
            self.m[t.b][t.a] = t

    def vecinos(self, u):
        fila = self.m[u]
        for v in range(self.n):  # hay que recorrer n celdas aunque casi todas esten vacias
            if fila[v] is not None:
                yield v, fila[v]


class ListaAdyacencia(Grafo):
    nombre = "Lista de adyacencia"

    def __init__(self, n, tramos):
        super().__init__(n)
        self.adj = [[] for _ in range(n)]
        for t in tramos:
            self.adj[t.a].append((t.b, t))
            self.adj[t.b].append((t.a, t))

    def vecinos(self, u):
        return iter(self.adj[u])


class MatrizDispersa(Grafo):
    """Formato CSR (Compressed Sparse Row) implementado a mano.

    - row_ptr[u]..row_ptr[u+1] delimita las entradas de la fila u
    - col_idx[k] es la columna (vecino) de la entrada k
    - valores[k] es el Tramo de la entrada k
    Solo se guardan las 2*90 = 180 celdas no vacias.
    """
    nombre = "Matriz dispersa (CSR)"

    def __init__(self, n, tramos):
        super().__init__(n)
        entradas = []
        for t in tramos:
            entradas.append((t.a, t.b, t))
            entradas.append((t.b, t.a, t))
        entradas.sort(key=lambda e: (e[0], e[1]))
        self.row_ptr = [0] * (n + 1)
        self.col_idx = []
        self.valores = []
        for u, v, t in entradas:
            self.row_ptr[u + 1] += 1
            self.col_idx.append(v)
            self.valores.append(t)
        for i in range(n):
            self.row_ptr[i + 1] += self.row_ptr[i]

    def vecinos(self, u):
        for k in range(self.row_ptr[u], self.row_ptr[u + 1]):
            yield self.col_idx[k], self.valores[k]

    def get(self, u, v):
        """Equivalente a m[u][v] de la matriz densa (None si la celda esta vacia)."""
        return self.tramo(u, v)


REPRESENTACIONES = (MatrizAdyacencia, ListaAdyacencia, MatrizDispersa)


def construir(clase, tramos=None, n=None):
    tramos = cargar_tramos() if tramos is None else tramos
    n = len(campus_data.NOMBRES) if n is None else n
    return clase(n, tramos)


# ----------------------------------------------------------------------------
# Memoria
# ----------------------------------------------------------------------------
# Modelo teorico (tamanos tipo C): indice/puntero = 4 bytes, peso float64 = 8 bytes.
# El peso es lo unico que se cuenta por celda/entrada, para comparar estructuras y no atributos.
B_IDX, B_PESO = 4, 8


def memoria_teorica(n: int, m: int) -> dict:
    """Bytes teoricos para n nodos y m aristas NO dirigidas (2m entradas)."""
    e = 2 * m
    return {
        "Matriz n x n": n * n * B_PESO,
        "Lista de adyacencia": e * (B_IDX + B_PESO) + n * B_IDX,
        "Matriz dispersa (CSR)": e * B_PESO + e * B_IDX + (n + 1) * B_IDX,
    }


def memoria_medida(clase, tramos):
    """Bytes realmente asignados por Python al construir la estructura (tracemalloc).
    Los objetos Tramo se crean antes y se comparten, asi que solo se mide la estructura."""
    n = len(campus_data.NOMBRES)
    tracemalloc.start()
    base = tracemalloc.get_traced_memory()[0]
    g = clase(n, tramos)
    actual = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    return actual - base, g


def tabla_memoria(n=60, m=90) -> str:
    tramos = cargar_tramos()
    teo = memoria_teorica(n, m)
    lineas = []
    lineas.append(f"Campus: {n} nodos, {m} aristas no dirigidas ({2 * m} celdas no vacias de {n * n}).")
    lineas.append(f"Densidad de la matriz: {2 * m / (n * n):.1%} de celdas ocupadas.")
    lineas.append("")
    lineas.append(f"{'Representacion':<24}{'Teorico (bytes)':>16}{'Medido Python (bytes)':>24}{'vs matriz':>12}")
    base = teo["Matriz n x n"]
    for clase in REPRESENTACIONES:
        med, _ = memoria_medida(clase, tramos)
        t = teo[clase.nombre]
        lineas.append(f"{clase.nombre:<24}{t:>16,}{med:>24,}{t / base:>11.1%}")
    lineas.append("")
    lineas.append("Proyeccion si el campus crece (grado medio constante, m = 1.5 n):")
    lineas.append(f"{'nodos':>7}{'aristas':>9}{'Matriz':>14}{'Lista':>12}{'CSR':>12}")
    for nn in (60, 600, 6000):
        mm = int(nn * 1.5)
        p = memoria_teorica(nn, mm)
        lineas.append(f"{nn:>7}{mm:>9}{p['Matriz n x n']:>14,}{p['Lista de adyacencia']:>12,}"
                      f"{p['Matriz dispersa (CSR)']:>12,}")
    return "\n".join(lineas)


if __name__ == "__main__":
    print(tabla_memoria())
