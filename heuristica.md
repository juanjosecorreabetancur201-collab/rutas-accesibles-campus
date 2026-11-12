# Heurística de A*: distancia en línea recta

## Definición

Para un nodo `u` y el destino `t`, con coordenadas `(x, y)` en metros:

```
h(u, t) = sqrt( (x_u − x_t)² + (y_u − y_t)² )
```

Implementada en `busquedas.py` como `heuristica_euclidiana`.

## Qué significa "admisible"

`h` es admisible si **nunca sobreestima** el costo real mínimo `h*(u, t)` para llegar de `u` a `t`: `h(u, t) ≤ h*(u, t)` para todo `u`. Si lo cumple, A* devuelve una ruta de costo mínimo.

## Argumento

El costo de un tramo es `costo = dist × (1 + pendiente/10)`, y cada tramo cumple dos cosas por construcción:

1. `dist ≥ línea recta entre sus dos extremos`. Un camino real no atraviesa edificios, así que nunca es más corto que la recta. En los datos (`campus_data.tramos_crudos`) se garantiza con `dist = ceil(euclidiana × factor × 10)/10` con `factor ≥ 1`, de modo que el redondeo siempre va hacia arriba.
2. `pendiente ≥ 0`, luego `costo ≥ dist`.

Por lo tanto, para cada tramo `(a, b)`: `costo(a, b) ≥ dist(a, b) ≥ ‖a − b‖`.

Sea una ruta óptima `u = v0, v1, …, vk = t` de costo `h*(u, t)`. Entonces

```
h*(u, t) = Σ costo(v_i, v_{i+1})
         ≥ Σ ‖v_i − v_{i+1}‖        (por 1 y 2, tramo a tramo)
         ≥ ‖u − t‖ = h(u, t)        (desigualdad triangular)
```

Así `h(u, t) ≤ h*(u, t)`: **la heurística nunca sobreestima**. ∎

Las restricciones (obras, escaleras, puertas cerradas) solo **quitan** aristas, lo que puede aumentar `h*` pero nunca disminuirlo; la desigualdad se mantiene. Si no hay ruta, `h*= ∞` y también se cumple.

## Consistencia

La misma desigualdad `h(a, t) ≤ costo(a, b) + h(b, t)` se obtiene de `costo(a,b) ≥ ‖a − b‖` y la desigualdad triangular. Es decir, `h` es además **consistente**, por eso la implementación puede cerrar un nodo la primera vez que sale de la frontera sin perder optimalidad.

## Qué pasaría con una heurística no admisible

Si se usara, por ejemplo, `h' = 2 × línea recta`, A* podría cerrar un nodo con un camino peor y devolver una ruta más cara que la óptima. Se puede comprobar cambiando el argumento `h` de `astar(...)`; con `h = heuristica_cero` el resultado coincide con Dijkstra.

## Verificación empírica (no sustituye la prueba)

`test_actividad7.py` comprueba:

- `h(a, b) ≤ costo` para los 90 tramos (`test_heuristica_admisible_en_cada_tramo`);
- `h(s, t) ≤ costo óptimo` calculado con Dijkstra para 40 pares (`test_heuristica_admisible_vs_costo_optimo`);
- que A* y Dijkstra devuelven el mismo costo en todas las consultas y que el costo coincide con `networkx.dijkstra_path_length` (usado **solo para contrastar**, no en el código de la herramienta).
