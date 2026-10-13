import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/tiros_con_xg.csv")
df["gol"] = (df["shot_outcome"] == "Goal").astype(int)

rng = np.random.default_rng(42)
N = 10000   # número de temporadas simuladas


def simular(probs, n=N):
    # Cada fila = una temporada simulada; cada columna = un tiro.
    # El tiro es gol si un número al azar cae por debajo de su xG.
    sim = rng.random((n, len(probs))) < probs
    return sim.sum(axis=1)


filas = []
simulaciones = {}
for equipo, g in df.groupby("team"):
    probs = g["xg_propio"].to_numpy()
    sims = simular(probs)
    simulaciones[equipo] = sims
    reales = int(g["gol"].sum())
    low, high = np.percentile(sims, [2.5, 97.5])
    filas.append({
        "equipo": equipo,
        "goles_reales": reales,
        "esperado": round(probs.sum(), 1),
        "rango_normal_95": f"{low:.0f} - {high:.0f}",
        "fuera_del_rango": "SÍ" if (reales < low or reales > high) else "",
        "percentil": round((sims < reales).mean() * 100, 1),
    })

tabla = pd.DataFrame(filas).set_index("equipo")
print(tabla.sort_values("percentil", ascending=False).to_string())
print("\nEquipos fuera del rango normal:", (tabla["fuera_del_rango"] == "SÍ").sum(), "de", len(tabla))

# Gráfico: el caso del Barcelona
sims_bar = simulaciones["Barcelona"]
reales_bar = tabla.loc["Barcelona", "goles_reales"]

fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(sims_bar, bins=range(int(sims_bar.min()), int(sims_bar.max()) + 2),
        color="steelblue", alpha=0.8)
ax.axvline(reales_bar, color="red", linewidth=2, label=f"Goles reales ({reales_bar})")
ax.axvline(sims_bar.mean(), color="green", linestyle="--",
           label=f"Promedio simulado ({sims_bar.mean():.1f})")
ax.set_xlabel("Goles en la temporada (jugadas abiertas)")
ax.set_ylabel("Temporadas simuladas")
ax.set_title("Barcelona 2015/16: 10,000 temporadas simuladas vs la realidad")
ax.legend()
plt.savefig("montecarlo_barcelona.png", dpi=300, bbox_inches="tight")
plt.show()