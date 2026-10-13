# ⚽ Fútbol + Ingeniería Industrial: calidad, variabilidad y rendimiento en La Liga 2015/16

Proyecto personal que aplica herramientas clásicas de la **Ingeniería Industrial y Six Sigma** (gráficos de control, diagramas de Pareto, benchmarking, simulación Monte Carlo y el ciclo DMAIC) al análisis de datos de fútbol, usando un **modelo propio de goles esperados (xG)**.

![Dashboard](imagenes/dashboard.png)

## ¿Qué pregunta responde?

> ¿Cómo genera y desaprovecha oportunidades un equipo de fútbol, y cuánto de su rendimiento es habilidad real frente a simple azar?

Tratamos cada partido como la salida de un **proceso** y cada tiro como una **unidad producida**, con una "calidad" medida por su probabilidad de gol (xG).

## Metodología (enfoque DMAIC)

| Fase | Qué se hizo | Script |
|---|---|---|
| **Define** | Definir el problema: calidad de ocasiones y aprovechamiento ofensivo en La Liga 2015/16 | — |
| **Measure** | Descarga de 380 partidos (9,168 tiros) y construcción de un modelo xG propio con regresión logística (distancia, ángulo y remate de cabeza) sobre jugadas abiertas | `02`, `05` |
| **Analyze** | Gráfico de control del xG por partido, diagramas de Pareto del xG "perdido", benchmarking entre los 20 equipos y análisis por jugador | `06`, `07`, `08`, `10` |
| **Improve** | Simulación Monte Carlo (10,000 temporadas) para separar suerte de rendimiento real | `09` |
| **Control** | Dashboard interactivo en Streamlit para monitorear cada equipo | `app.py` |

## Resultados principales

### 1. Modelo xG propio, validado contra un estándar profesional
Evaluado con el 30 % de los tiros que el modelo nunca vio, comparado con el xG de StatsBomb:

| Métrica | Modelo propio | StatsBomb |
|---|---|---|
| AUC (mayor es mejor) | 0.794 | 0.833 |
| Error Brier (menor es mejor) | 0.0849 | 0.0771 |
| xG total vs. 289 goles reales | 282.5 | 280.3 |

StatsBomb rinde algo mejor porque usa información que el modelo propio no tiene (posición del portero y defensores).

### 2. Gráfico de control (Barcelona)
El xG por partido tuvo una media de 1.98 y **ningún partido fuera de los límites de control**: las subidas y bajadas fueron variación normal, sin causas especiales. Reaccionar a una mala racha aislada habría sido sobreajustar el proceso.

![Gráfico de control](imagenes/grafico_control_barcelona.png)

### 3. Pareto del xG perdido (Barcelona)
- Por resultado: tiros atajados (33 %), desviados (32 %) y bloqueados (25 %) explican cerca del 90 % del xG perdido.
- Por patrón de juego: la jugada normal pesa 34 %, pero las reanudaciones (tiro libre, saque de banda y córner) suman otro 55 %.

![Pareto por resultado](imagenes/pareto_resultado.png)
![Pareto por patrón de juego](imagenes/pareto_patron.png)

El Pareto mide volumen, no eficiencia. Al comparar con la liga, el Barcelona tuvo un 20.0 % de tiros bloqueados frente al 22.7 % promedio: en ese punto estuvo mejor que la media, no peor.

### 4. Benchmarking de los 20 equipos
Real Madrid (99 goles con 70.7 de xG) y Barcelona (93 con 75.4) rindieron muy por encima de lo esperado; Sevilla (42 con 58.0) quedó muy por debajo.

![Benchmark](imagenes/benchmark_equipos.png)

### 5. Simulación Monte Carlo: ¿suerte o realidad?
Simulando cada temporada 10,000 veces según el xG de cada tiro, **3 de 20 equipos** quedaron fuera del rango normal del 95 % (Real Madrid y Barcelona por encima, Sevilla por debajo). Por azar puro se esperaría aproximadamente 1. El caso del Real Madrid es sólido; el del Barcelona es sugerente pero no concluyente.

![Monte Carlo](imagenes/montecarlo_barcelona.png)

### 6. Análisis por jugador
Los delanteros de élite superan al "tirador promedio" del modelo: Suárez (37 goles con 21.9 de xG) y Bale (19 con 7.6) destacan. Al usar el xG de StatsBomb, que sí considera el contexto de la jugada, la brecha se reduce en algunos casos (Cristiano, Griezmann) pero se mantiene en Suárez y Bale, lo que apunta a finalización de élite más allá de la calidad de la ocasión.

## Limitaciones

- Se analiza **una sola temporada**; la habilidad real debería confirmarse viendo si se repite en otras.
- El modelo usa solo distancia, ángulo y remate de cabeza, y **no ve** la posición del portero ni de los defensores, ni quién dispara.
- Solo jugadas abiertas (sin penales ni tiros libres directos).
- La simulación supone que los tiros son independientes entre sí.
- Algunos jugadores tienen pocos tiros (45 a 70), así que sus diferencias son poco fiables.
- El xG mide tiros, no la creación de juego (pases, asistencias).

## Cómo reproducirlo

Los datos **no se incluyen en este repositorio**: se descargan con los scripts.

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Descargar los tiros de La Liga 2015/16 (tarda unos minutos)
python 02_descargar_tiros.py

# 3. Entrenar el modelo xG
python 05_modelo_xg.py

# 4. Guardar las fechas de los partidos
python 11_guardar_fechas.py

# 5. Abrir el dashboard
streamlit run app.py
```

Los scripts `01`, `03`, `04`, `06`, `07`, `08`, `09` y `10` son los análisis individuales (exploración, mapa de tiros, gráfico de control, Pareto, benchmark, Monte Carlo y jugadores) y se ejecutan después del paso 3.

## Tecnologías
Python · pandas · NumPy · scikit-learn · matplotlib · mplsoccer · Streamlit · statsbombpy

## Datos

<img src="imagenes/statsbomb_logo.png" alt="StatsBomb" width="160">

Datos: [StatsBomb Open Data](https://github.com/hudl/open-data). Proyecto personal con fines educativos, sin afiliación con StatsBomb.

## Autor

**[Mijael Blancos Chicalla]** · Estudiante de Ingeniería Industrial · [blancosmijael66@gmail.com]
