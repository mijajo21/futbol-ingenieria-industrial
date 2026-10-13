import numpy as np
import pandas as pd

df = pd.read_csv("data/tiros_con_xg.csv")
df["gol"] = (df["shot_outcome"] == "Goal").astype(int)

rng = np.random.default_rng(42)
N = 10000

filas = []
for jugador, g in df.groupby("player"):
    if len(g) < 40:          # solo jugadores con al menos 40 tiros
        continue
    probs = g["xg_propio"].to_numpy()
    sims = (rng.random((N, len(probs))) < probs).sum(axis=1)
    reales = int(g["gol"].sum())
    filas.append({
        "jugador": jugador,
        "equipo": g["team"].iloc[0],
        "tiros": len(g),
        "goles": reales,
        "xg": round(probs.sum(), 1),
        "xg_statsbomb": round(g["shot_statsbomb_xg"].sum(), 1),
        "diferencia": round(reales - probs.sum(), 1),
        "percentil": round((sims < reales).mean() * 100, 1),
    })

tabla = (pd.DataFrame(filas).set_index("jugador")
         .sort_values("diferencia", ascending=False))

print(f"Jugadores analizados: {len(tabla)}")
print("\n=== MÁS GOLES DE LOS ESPERADOS ===")
print(tabla.head(10).to_string())
print("\n=== MENOS GOLES DE LOS ESPERADOS ===")
print(tabla.tail(8).to_string())
print("\n=== MESSI ===")
print(tabla[tabla.index.str.contains("Messi")].to_string())

print("\n=== TOP 5 comparado con el xG de StatsBomb ===")
print(tabla.head(5)[["goles", "xg", "xg_statsbomb"]].to_string())