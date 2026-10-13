import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

df = pd.read_csv("data/tiros_laliga.csv")

messi = df[df["player"].str.contains("Messi", na=False)]
goles = messi[messi["shot_outcome"] == "Goal"]
fallidos = messi[messi["shot_outcome"] != "Goal"]

pitch = Pitch(pitch_type="statsbomb", half=True,
              pitch_color="grass", line_color="white")
fig, ax = pitch.draw(figsize=(10, 7))

pitch.scatter(fallidos.x, fallidos.y, ax=ax, s=60,
              c="blue", alpha=0.5, label="No gol")
pitch.scatter(goles.x, goles.y, ax=ax, s=120,
              c="gold", edgecolors="black", label="Gol")

ax.legend()
plt.title("Tiros de Messi - La Liga 2015/16")
plt.show()