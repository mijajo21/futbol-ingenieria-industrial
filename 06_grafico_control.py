import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsbombpy import sb

warnings.filterwarnings("ignore")

EQUIPO = "Barcelona"

# 1. Datos: xG de tu modelo, sumado por partido
tiros = pd.read_csv("data/tiros_con_xg.csv")
partidos = sb.matches(competition_id=11, season_id=27)[["match_id", "match_date"]]
partidos["match_date"] = pd.to_datetime(partidos["match_date"])

por_partido = (
    tiros[tiros["team"] == EQUIPO]
    .groupby("match_id")["xg_propio"].sum()
    .reset_index()
)
por_partido = (
    por_partido.merge(partidos, on="match_id")
    .sort_values("match_date")
    .reset_index(drop=True)
)

# 2. Línea central y límites de control
valores = por_partido["xg_propio"]
media = valores.mean()
rango_movil = valores.diff().abs().mean()   # cambio promedio entre partidos seguidos
sigma = rango_movil / 1.128                 # constante estándar de este tipo de gráfico
LCS = media + 3 * sigma                     # límite de control superior
LCI = max(media - 3 * sigma, 0)             # límite de control inferior

print(f"Media: {media:.2f} | LCS: {LCS:.2f} | LCI: {LCI:.2f}")

# 3. Señales de alerta
fuera = por_partido[(valores > LCS) | (valores < LCI)]
print("\nPartidos fuera de los límites (causa especial):")
print(fuera[["match_date", "xg_propio"]] if len(fuera) else "Ninguno")

lado = np.sign(valores - media).to_numpy()
racha = 1
for i in range(1, len(lado)):
    racha = racha + 1 if lado[i] == lado[i - 1] else 1
    if racha == 8:
        fecha = por_partido.loc[i, "match_date"].date()
        print(f"\nRacha de 8 partidos seguidos del mismo lado de la media, termina el {fecha}")

# 4. Gráfico
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(por_partido["match_date"], valores, marker="o", color="navy", alpha=0.7)
ax.axhline(media, color="green", label=f"Media ({media:.2f})")
ax.axhline(LCS, color="red", linestyle="--", label=f"LCS ({LCS:.2f})")
ax.axhline(LCI, color="red", linestyle="--", label=f"LCI ({LCI:.2f})")
ax.scatter(fuera["match_date"], fuera["xg_propio"], color="red", s=120, zorder=5)
ax.set_title(f"Gráfico de control: xG por partido - {EQUIPO} 2015/16")
ax.set_ylabel("xG (jugadas abiertas)")
ax.legend()
plt.savefig("grafico_control_barcelona.png", dpi=300, bbox_inches="tight")
plt.show()