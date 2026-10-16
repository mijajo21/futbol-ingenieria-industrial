import numpy as np
import pandas as pd

# --- Perillas ---
ARCHIVO = "data/barcelona_temporadas_con_xg.csv"    # lo creó el script 15
EQUIPO = "Barcelona"
JUGADORES = ["Messi", "Luis Alberto Suárez"]      # basta con una parte del nombre
MINIMO_TIROS = 40
N = 10000                            # temporadas simuladas

rng = np.random.default_rng(42)

df = pd.read_csv(ARCHIVO)
df = df[df["team"] == EQUIPO]        # solo los tiros del Barcelona


def simular(probs):
    # igual que en el script 09: una fila por temporada simulada, una columna por tiro
    sim = rng.random((N, len(probs))) < probs
    return sim.sum(axis=1)           # goles de cada temporada simulada


def resumir(nombre, g):
    # Una función que recibe un grupo de tiros y devuelve su resumen
    probs = g["xg_propio"].to_numpy()
    sims = simular(probs)
    reales = int(g["gol"].sum())
    bajo, alto = np.percentile(sims, [2.5, 97.5])
    return {
        "grupo": nombre,
        "tiros": len(g),
        "goles": reales,
        "esperado": round(probs.sum(), 1),
        "ruido": round(sims.std(), 1),                 # cuánto varían los goles por pura suerte
        "rango_95": f"{bajo:.0f} - {alto:.0f}",
        "azar_igualo": int((sims >= reales).sum()),    # de las 10,000, cuántas llegaron a los goles reales
    }


# --- PARTE A: el equipo, temporada por temporada y las seis juntas ---
filas_equipo = []
for temporada in sorted(df["temporada"].unique()):
    filas_equipo.append(resumir(temporada, df[df["temporada"] == temporada]))
filas_equipo.append(resumir("6 TEMPORADAS JUNTAS", df))

print("=== EQUIPO ===")
print(pd.DataFrame(filas_equipo).set_index("grupo").to_string())

# --- PARTE B: cada jugador, temporada por temporada y todas juntas ---
filas_jug = []
for jugador in JUGADORES:
    sub = df[df["player"].str.contains(jugador, na=False)]
    for temporada in sorted(sub["temporada"].unique()):
        g = sub[sub["temporada"] == temporada]
        if len(g) >= MINIMO_TIROS:
            filas_jug.append(resumir(f"{jugador} {temporada}", g))
    filas_jug.append(resumir(f"{jugador} TODAS JUNTAS", sub))

print("\n=== JUGADORES ===")
print(pd.DataFrame(filas_jug).set_index("grupo").to_string())