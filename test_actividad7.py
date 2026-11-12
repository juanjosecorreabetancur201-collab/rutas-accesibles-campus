import itertools
import math

import pytest

import busquedas as b
import campus_data
import grafo

H_1745, H_1815 = 17 * 60 + 45, 18 * 60 + 15
IDX = {n: i for i, n in enumerate(campus_data.NOMBRES)}


@pytest.fixture(scope="module")
def tramos():
    return grafo.cargar_tramos()


@pytest.fixture(scope="module", params=grafo.REPRESENTACIONES, ids=lambda c: c.__name__)
def g(request, tramos):
    return grafo.construir(request.param, tramos)


def test_tamano_del_campus(tramos):
    assert len(campus_data.NOMBRES) == 60
    assert len(tramos) == 90


def test_representaciones_equivalentes(tramos):
    gs = [grafo.construir(c, tramos) for c in grafo.REPRESENTACIONES]
    for u in range(60):
        vec = [sorted((v, t) for v, t in x.vecinos(u)) if False else sorted(v for v, _ in x.vecinos(u)) for x in gs]
        assert vec[0] == vec[1] == vec[2]
    assert all(x.num_aristas_dirigidas() == 180 for x in gs)


def test_memoria_teorica_campus():
    m = grafo.memoria_teorica(60, 90)
    assert m["Matriz n x n"] == 3600 * 8
    assert m["Lista de adyacencia"] < m["Matriz n x n"] / 10
    assert m["Matriz dispersa (CSR)"] < m["Matriz n x n"] / 10


def test_heuristica_admisible_en_cada_tramo(tramos):
    """h(u,v) <= costo del tramo u-v: condicion suficiente para admisibilidad y consistencia."""
    for t in tramos:
        assert t.dist >= b.heuristica_euclidiana(t.a, t.b) - 1e-9
        assert t.costo >= t.dist
        assert b.heuristica_euclidiana(t.a, t.b) <= t.costo + 1e-9


def test_heuristica_admisible_vs_costo_optimo(g):
    """h(u,t) <= costo optimo real (Dijkstra) para muchos pares."""
    for s, t in itertools.islice(itertools.product(range(0, 60, 7), range(3, 60, 11)), 40):
        r = b.dijkstra(g, s, t, H_1745)
        if r.encontrada:
            assert b.heuristica_euclidiana(s, t) <= r.costo + 1e-9


def test_astar_igual_que_dijkstra_y_explora_menos(g):
    ahorro = 0
    for s, t in [(0, 44), (5, 49), (10, 36), (0, 59)]:
        a, d = b.astar(g, s, t, H_1745), b.dijkstra(g, s, t, H_1745)
        assert a.encontrada and d.encontrada
        assert a.costo == pytest.approx(d.costo)
        assert a.explorados <= d.explorados
        ahorro += d.explorados - a.explorados
    assert ahorro > 0


def test_bfs_dfs_terminan_con_ciclos_y_marcan_visitados(g):
    for alg in (b.bfs, b.dfs):
        r = alg(g, 0, 59, H_1745)
        assert r.encontrada
        assert len(set(r.orden)) == len(r.orden)  # ningun nodo se explora dos veces
        assert r.ruta[0] == 0 and r.ruta[-1] == 59


def test_rutas_validas(g):
    for alg in (b.bfs, b.dfs, b.astar):
        r = alg(g, 0, IDX["Laboratorio de Redes"], H_1745)
        for u, v in zip(r.ruta, r.ruta[1:]):
            assert g.tramo(u, v).transitable(H_1745, True)


def test_consulta_horario_con_ruta_a_las_1745(g):
    r = b.astar(g, IDX["Entrada Principal"], IDX["Lab. Sistemas"], H_1745)
    assert r.encontrada
    assert IDX["Sala de Computo 1"] in r.ruta  # entra por la puerta (22,23)


def test_sin_ruta_a_las_1815_no_falla_en_silencio(g):
    r = b.astar(g, IDX["Entrada Principal"], IDX["Lab. Sistemas"], H_1815)
    assert not r.encontrada
    assert r.ruta is None and r.costo is None
    assert "no existe ruta accesible" in r.motivo and "18:15" in r.motivo
    for alg in (b.bfs, b.dfs):
        assert not alg(g, IDX["Entrada Principal"], IDX["Lab. Sistemas"], H_1815).encontrada


def test_desvio_mas_largo_a_las_1815(g):
    s, t = IDX["Entrada Principal"], IDX["Laboratorio de Redes"]
    antes, despues = b.astar(g, s, t, H_1745), b.astar(g, s, t, H_1815)
    assert antes.encontrada and despues.encontrada
    assert despues.costo > antes.costo


def test_origen_igual_destino(g):
    r = b.astar(g, 5, 5, H_1745)
    assert r.ruta == [5] and r.costo == 0


def test_nodo_invalido_es_error_de_uso(g):
    with pytest.raises(ValueError):
        b.bfs(g, 0, 999)


def test_contraste_opcional_con_networkx(tramos):
    nx = pytest.importorskip("networkx")  # solo para contrastar, no se usa en el codigo
    G = nx.Graph()
    for t in tramos:
        if t.transitable(H_1745, True):
            G.add_edge(t.a, t.b, weight=t.costo)
    gl = grafo.construir(grafo.ListaAdyacencia, tramos)
    for s, t in [(0, 44), (5, 49), (10, 36)]:
        esperado = nx.dijkstra_path_length(G, s, t)
        assert b.astar(gl, s, t, H_1745).costo == pytest.approx(esperado)
