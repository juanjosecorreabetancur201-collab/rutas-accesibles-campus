# Actividad 7 — Rutas accesibles en el campus

Estructuras de Datos (ID 706132) · Universidad Cooperativa de Colombia

## Archivos

| Archivo | Contenido |
|---|---|
| `modelo.md` | Nodos, aristas, atributos, costo y mapa del campus (Parte A) |
| `campus_data.py` | Datos del campus: 60 nodos, 90 tramos |
| `grafo.py` | Matriz, lista y matriz dispersa (CSR) + tabla de memoria (Parte B) |
| `busquedas.py` | BFS, DFS, A* (y Dijkstra como referencia) + tabla de nodos explorados (Parte C) |
| `heuristica.md` | Heurística y prueba de admisibilidad (Parte C) |
| `consultas.py` → `salida_consultas.txt` | Consultas 17:45 vs 18:15 y comparación de algoritmos (Partes C y D) |
| `tabla_memoria.txt` | Salida de `python grafo.py` |
| `test_actividad7.py` | Pruebas (`pytest`) |

## Cómo ejecutar

```
python grafo.py          # tabla de memoria
python consultas.py      # consultas de horario y tabla de nodos explorados
pytest                   # 32 pruebas
```

Solo se necesita Python 3 y `pytest`. `networkx` es opcional y únicamente contrasta resultados en una prueba (se omite si no está instalado).

## Decisión de representación (Parte B)

Con 60 nodos y 90 aristas (180 entradas dirigidas), solo el **5 %** de las 3.600 celdas de la matriz está ocupado:

| Representación | Bytes (modelo: índice 4 B, peso 8 B) | vs matriz |
|---|---|---|
| Matriz 60×60 | 28.800 | 100 % |
| Lista de adyacencia | 2.400 | 8,3 % (12× menos) |
| Matriz dispersa CSR | 2.404 | 8,3 % |

Si el campus crece a 600 nodos y 900 aristas, la matriz pasa a 2.880.000 B y la lista a 24.000 B (120× menos), porque la matriz crece con n² y la lista con n + m.

**Se elige la lista de adyacencia.** Gasta lo mismo que CSR, pero recorrer los vecinos de un nodo cuesta O(grado) (la matriz cuesta O(n)), y permite agregar o quitar un tramo sin reconstruir la estructura (algo que en CSR obliga a reordenar los arreglos). CSR sería preferible solo si el grafo fuera estático y se hicieran operaciones por filas en bloque.

## Resultados de la comparación (consulta Entrada Principal → Laboratorio de Redes, 17:45)

| Algoritmo | Nodos explorados | Costo |
|---|---|---|
| BFS | 32 | 524,0 (no óptimo) |
| DFS | 18 | 1045,7 (no óptimo) |
| Dijkstra (A* con h=0) | 33 | 523,2 |
| A* | 26 | 523,2 |

DFS explora menos porque se conforma con cualquier ruta, no con la mejor. BFS minimiza tramos, no costo. A* explora menos que Dijkstra con el mismo costo óptimo. La ventaja es moderada en este campus pequeño y de cuadrícula; en la consulta Biblioteca → Zona Verde baja de 56 a 29 nodos.

## Notas honestas

- El mapa es una **simplificación** con nombres genéricos de un campus. El enunciado pide un mapa "simplificado, pero real": reemplaza nombres y coordenadas en `campus_data.py` por los de tu campus antes de entregar.
- La columna "Medido Python" de la tabla de memoria usa `tracemalloc` y varía un poco entre ejecuciones; la decisión se justifica con el modelo teórico.
- Antes de entregar: sube todo a GitHub, comprueba `pytest` en una máquina limpia y verifica que el último commit sea anterior al domingo de la semana 14, 23:59.
