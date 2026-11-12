"""Parte D: consultas de horario y tabla comparativa de nodos explorados.

Uso: python consultas.py > salida_consultas.txt
"""
import campus_data
import grafo
import busquedas as b

H_1745 = 17 * 60 + 45
H_1815 = 18 * 60 + 15

NOM = campus_data.NOMBRES
IDX = {n: i for i, n in enumerate(NOM)}


def consultar(g, origen, destino, hora):
    """Ruta accesible con A*. Si no hay, explica POR QUE (horario vs. estructura)."""
    r = b.astar(g, origen, destino, hora, solo_accesible=True)
    print(f"--- {NOM[origen]} -> {NOM[destino]} a las {b.hhmm(hora)} ---")
    print(r.describir())
    if not r.encontrada:
        sin_horario = b.astar(g, origen, destino, hora=None, solo_accesible=True)
        if sin_horario.encontrada:
            print("    Diagnostico: SI existe ruta accesible cuando las puertas estan abiertas "
                  f"(costo {sin_horario.costo:.1f}); el bloqueo es por el horario de cierre (18:00).")
            print("    Respuesta para Bienestar: a esta hora NO hay ruta accesible; "
                  "consultar de nuevo antes de las 18:00 o pedir que se habilite la puerta.")
        else:
            print("    Diagnostico: no hay ruta accesible ni siquiera con puertas abiertas "
                  "(escaleras u obras aislan el destino).")
    print()
    return r


def main():
    g = grafo.construir(grafo.ListaAdyacencia)
    print("=== PARTE D: consultas de horario (A*, solo tramos accesibles) ===\n")
    for o, d in (("Entrada Principal", "Lab. Sistemas"),
                 ("Entrada Principal", "Laboratorio de Redes")):
        for h in (H_1745, H_1815):
            consultar(g, IDX[o], IDX[d], h)

    print("=== PARTE C: nodos explorados por algoritmo (misma consulta) ===\n")
    for o, d in (("Entrada Principal", "Laboratorio de Redes"),
                 ("Biblioteca", "Zona Verde"),
                 ("Plazoleta de Banderas", "Sala de Estudio")):
        print(b.comparar(g, IDX[o], IDX[d], H_1745))
        print()

    print("=== Mismas rutas con las tres representaciones (deben coincidir) ===")
    tramos = grafo.cargar_tramos()
    for clase in grafo.REPRESENTACIONES:
        gg = grafo.construir(clase, tramos)
        r = b.astar(gg, IDX["Entrada Principal"], IDX["Laboratorio de Redes"], H_1745)
        print(f"{clase.nombre:<24} costo {r.costo:.1f}  explorados {r.explorados}")


if __name__ == "__main__":
    main()
