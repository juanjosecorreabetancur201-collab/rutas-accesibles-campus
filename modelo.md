# Modelo del problema — Rutas accesibles en el campus

> Se documentó **antes** de programar: las decisiones de esta página son las que implementan `campus_data.py` y `grafo.py`.

## 1. Nodos

Un nodo es un **punto de interés** del campus (portería, bloque, laboratorio, cafetería, etc.) con coordenadas `(x, y)` en metros. Hay **60 nodos**, numerados 0–59 (`id = fila*10 + columna`).

Se eligen los puntos de interés como nodos (y no las esquinas de los caminos) porque las consultas son "de un lugar a otro" y porque así el campus coincide con los ~60 puntos y ~90 tramos del enunciado.

## 2. Aristas

Una arista es un **tramo caminable entre dos puntos contiguos**. Es **no dirigida** (se puede caminar en ambos sentidos con el mismo costo). Hay **90 aristas** = 180 entradas dirigidas.

| Atributo | Tipo | Para qué sirve |
|---|---|---|
| `dist` | metros | Distancia real caminando. Siempre ≥ distancia en línea recta (garantiza la heurística, ver `heuristica.md`). |
| `pendiente` | % | Entra en el costo y decide si el tramo es accesible. |
| `escalera` | bool | Escalera sin rampa → tramo no accesible. |
| `en_obra` | bool | Tramo cerrado para todos. |
| `cierra` | minuto del día o `None` | Puerta que se cierra (18:00 = 1080). Desde esa hora el tramo no se puede usar. |

Reglas derivadas:

- **Accesible** = no tiene escalera **y** `pendiente ≤ 8 %`.
- **Transitable(hora)** = no está en obra, es accesible (en modo accesible) y `hora < cierra` si tiene puerta.

## 3. Costo (lo que se minimiza)

```
costo(tramo) = dist × (1 + pendiente / 10)
```

Una rampa larga y suave cuesta cerca de sus metros; un atajo corto pero empinado se encarece hasta 1,8× (con 8 %). Así "una rampa larga puede ser mejor que un atajo con pendiente fuerte".

Como `pendiente ≥ 0`, `costo ≥ dist ≥ línea recta`, que es la propiedad que necesita A*.

## 4. Mapa usado

### Origen del mapa (qué es real y qué es simulado)

- **Real:** nueve de los puntos llevan nombres de ambientes que la UCC publica para la sede Medellín - Envigado (Lab. Fluidos e Hidráulica, Lab. Geotecnia y Pavimentos, Media LAB Aula Mac, Estudio de Televisión, Estudio de Radio, Clínica Odontológica, Consultorio Psicológico, Consultorio Jurídico, Impact Campus, NAF Contable y Fiscal).
- **Simulado:** la disposición, las coordenadas, las distancias, las pendientes, las escaleras, las obras y las puertas que cierran a las 18:00 son datos **inventados** para probar el algoritmo. No corresponden a un plano oficial del campus y no deben leerse como tales.
- **Construcción:** cuadrícula de 10 columnas × 6 filas con desfases fijos de coordenadas. Se partió de las 104 conexiones posibles y se quitaron 14 (edificios/desniveles) → **90 tramos**.

Para reemplazarlo por datos medidos en el campus basta editar `campus_data.py`; el resto del código no cambia.

| Fila | Col 0 | Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 | Col 7 | Col 8 | Col 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 Entrada Principal | 1 Portería Norte | 2 Bloque A | 3 Bloque B | 4 Cafetería Central | 5 Biblioteca | 6 Auditorio | 7 Bloque C | 8 Parqueadero Norte | 9 Coliseo |
| 1 | 10 Plazoleta de Banderas | 11 Bienestar Univ. | 12 Aula Máxima | 13 Sala de Profesores | 14 Admisiones | 15 Hemeroteca | 16 Lab. Física | 17 Lab. Química | 18 Bloque D | 19 Gimnasio |
| 2 | 20 Tesorería | 21 Registro Académico | 22 **Lab. Sistemas** | 23 Sala de Cómputo 1 | 24 Sala de Cómputo 2 | 25 Media LAB Aula Mac | 26 Cancha Múltiple | 27 Bloque E | 28 Enfermería | 29 Piscina |
| 3 | 30 Bloque F | 31 Papelería | 32 NAF Contable y Fiscal | 33 Jardín Botánico | 34 Cafetería Sur | 35 Kiosco | 36 Sala de Estudio | 37 Bloque G | 38 Taller de Diseño | 39 Vivero |
| 4 | 40 Capilla | 41 Consultorio Jurídico | 42 Bloque H | 43 Aula 401 | 44 **Laboratorio de Redes** | 45 Fotocopiadora | 46 Impact Campus | 47 Bloque I | 48 Cancha de Tenis | 49 Zona Verde |
| 5 | 50 Portería Sur | 51 Parqueadero Sur | 52 Bloque J | 53 Teatro al Aire Libre | 54 Sala de Música | 55 Aula 501 | 56 Bloque K | 57 Bloque L | 58 Portería Oriente | 59 Bodega |

### Restricciones del mapa

| Tipo | Tramos (ids de nodos) |
|---|---|
| Escalera sin rampa | 11–12, 21–22, 31–41, 35–36, 46–47, 55–56 |
| Pendiente > 8 % | 40–41 (11 %), 25–26 (10 %) |
| En obra | 12–22, 24–25, 43–44, 53–54 |
| Puerta que cierra 18:00 | 22–23, 13–14, 24–34 |

El diseño del caso incómodo es intencional: **Lab. Sistemas (22)** queda con una escalera (21–22), una obra (12–22) y una única entrada accesible, la puerta 22–23. A las 17:45 hay ruta; a las 18:15 no existe ninguna.

## 5. Consultas que el modelo debe poder responder

1. Ruta de menor costo entre dos puntos solo con tramos accesibles → `costo`, `pendiente`, `escalera`.
2. La misma ruta a una hora dada → `cierra`.
3. "No hay ruta accesible" cuando el destino queda aislado → el algoritmo devuelve un resultado explícito, no una excepción.
