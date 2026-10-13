import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/tiros_con_xg.csv")
df["gol"] = (df["shot_outcome"] == "Goal").astype(int)

# 1. Resumen por equipo
resumen = df.groupby("team").agg(
    tiros=("gol", "size"),
    goles=("gol", "sum"),
    xg=("xg_propio", "sum"),
).round(1)

resumen["rendimiento"] = (resumen["goles"] / resumen["xg"]).round(2)   # mayor a 1 = rinde por encima de lo esperado
resumen["xg_por_tiro"] = (resumen["xg"] / resumen["tiros"]).round(3)   # calidad promedio de sus tiros

# 2. Qué porcentaje de sus tiros termina en cada resultado
resultados = pd.crosstab(df["team"], df["shot_outcome"], normalize="index") * 100
resumen["pct_bloqueados"] = resultados["Blocked"].round(1)
resumen["pct_desviados"] = resultados["Off T"].round(1)
resumen["pct_atajados"] = resultados["Saved"].round(1)

print("=== LOS 8 EQUIPOS QUE MÁS xG GENERARON ===")
print(resumen.sort_values("xg", ascending=False).head(8).to_string())

print("\n=== PROMEDIO DE LA LIGA (% de todos los tiros) ===")
liga = df["shot_outcome"].value_counts(normalize=True) * 100
print(liga.round(1))

# 3. Gráfico: calidad de ocasiones vs goles reales
fig, ax = plt.subplots(figsize=(9, 7))
ax.scatter(resumen["xg"], resumen["goles"], color="steelblue")

maximo = max(resumen["xg"].max(), resumen["goles"].max()) + 5
ax.plot([0, maximo], [0, maximo], color="gray", linestyle="--", label="Goles = xG")

from adjustText import adjust_text

textos = [ax.text(f["xg"], f["goles"], e, fontsize=8) for e, f in resumen.iterrows()]
adjust_text(textos, ax=ax)

ax.set_xlabel("xG (calidad de las ocasiones creadas)")
ax.set_ylabel("Goles reales")
ax.set_title("Rendimiento ofensivo por equipo - La Liga 2015/16 (jugadas abiertas)")
ax.legend()
plt.savefig("benchmark_equipos.png", dpi=300, bbox_inches="tight")
plt.show()