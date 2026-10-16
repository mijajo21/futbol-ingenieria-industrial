import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression

# --- Perillas ---
ARCHIVO_ENTRENAMIENTO = "data/respaldo_2015_16/tiros_laliga.csv"
ARCHIVO_BARCELONA = "data/tiros_barcelona_temporadas.csv"
ARCHIVO_SALIDA = "data/barcelona_temporadas_con_xg.csv"
EQUIPO = "Barcelona"
MINIMO_TIROS = 40        # tiros mínimos de un jugador en una temporada para contarlo

ARCO_X, CENTRO_Y, POSTE_1, POSTE_2 = 120, 40, 36, 44
VARIABLES = ["distancia", "angulo", "cabeza"]


def preparar(df):
    df = df[df["shot_type"] == "Open Play"].copy()
    df["gol"] = (df["shot_outcome"] == "Goal").astype(int)
    dx = ARCO_X - df["x"]
    df["distancia"] = np.sqrt(dx**2 + (CENTRO_Y - df["y"])**2)
    v1y = POSTE_1 - df["y"]
    v2y = POSTE_2 - df["y"]
    cruz = dx * v2y - v1y * dx
    punto = dx * dx + v1y * v2y
    df["angulo"] = np.abs(np.arctan2(cruz, punto))
    df["cabeza"] = (df["shot_body_part"] == "Head").astype(int)
    return df


# 1. Entrenar el modelo UNA vez, con 2015/16 (toda la liga)
entrenamiento = preparar(pd.read_csv(ARCHIVO_ENTRENAMIENTO))
modelo = LogisticRegression()
modelo.fit(entrenamiento[VARIABLES], entrenamiento["gol"])

# 2. Aplicarlo a los tiros de las seis temporadas
barca = preparar(pd.read_csv(ARCHIVO_BARCELONA))
barca["xg_propio"] = modelo.predict_proba(barca[VARIABLES])[:, 1]
barca.to_csv(ARCHIVO_SALIDA, index=False)

# 3. Nos quedamos solo con los tiros del Barcelona (sin los de sus rivales)
propios = barca[barca["team"] == EQUIPO]

# 4. Resumen del EQUIPO por temporada
equipo = propios.groupby("temporada").agg(
    tiros=("gol", "size"),
    goles=("gol", "sum"),
    xg=("xg_propio", "sum"),
    xg_statsbomb=("shot_statsbomb_xg", "sum"),
).round(1)
equipo["diferencia"] = (equipo["goles"] - equipo["xg"]).round(1)
print("=== EL EQUIPO, TEMPORADA POR TEMPORADA ===")
print(equipo)

# 5. Cada jugador, temporada por temporada
jug = (propios.groupby(["player", "temporada"])
       .agg(tiros=("gol", "size"), goles=("gol", "sum"), xg=("xg_propio", "sum"))
       .reset_index())
jug = jug[jug["tiros"] >= MINIMO_TIROS]
jug["diferencia"] = (jug["goles"] - jug["xg"]).round(1)

# pivot: jugadores en las filas, temporadas en las columnas
tabla = jug.pivot(index="player", columns="temporada", values="diferencia")
tiros = jug.pivot(index="player", columns="temporada", values="tiros")

# solo jugadores que cumplen el mínimo en al menos 2 temporadas
validos = tabla.notna().sum(axis=1) >= 2
tabla = tabla[validos]
tiros = tiros[validos]

print("\n=== DIFERENCIA (goles - xG) POR JUGADOR Y TEMPORADA ===")
print(tabla.to_string())
print("\n=== TIROS EN CADA CASO ===")
print(tiros.to_string())

# 6. Gráfico: ¿se repite el exceso de cada jugador?
fig, ax = plt.subplots(figsize=(11, 6))
for jugador, fila in tabla.iterrows():
    ax.plot(tabla.columns, fila.values, marker="o", label=jugador)
ax.axhline(0, color="gray", linestyle="--")
ax.set_ylabel("Goles - xG (jugadas abiertas)")
ax.set_title(f"{EQUIPO}: goles sobre el xG por jugador y temporada")
ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1, 0.5))
plt.savefig("imagenes/persistencia_jugadores.png", dpi=300, bbox_inches="tight")
plt.show()