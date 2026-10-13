import pandas as pd
import matplotlib.pyplot as plt

EQUIPO = "Barcelona"

df = pd.read_csv("data/tiros_con_xg.csv")
df = df[df["team"] == EQUIPO]
fallos = df[df["shot_outcome"] != "Goal"]   # los "defectos": tiros que no fueron gol


def pareto(serie, titulo, archivo):
    serie = serie.sort_values(ascending=False)
    acumulado = serie.cumsum() / serie.sum() * 100

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(serie.index, serie.values, color="steelblue")
    ax.set_ylabel("xG perdido")
    ax.tick_params(axis="x", rotation=30)

    ax2 = ax.twinx()
    ax2.plot(serie.index, acumulado.values, color="red", marker="o")
    ax2.axhline(80, color="gray", linestyle="--")
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("% acumulado")

    ax.set_title(titulo)
    plt.tight_layout()
    plt.savefig(archivo, dpi=300)
    plt.show()

    print(titulo)
    print(pd.DataFrame({"xG perdido": serie.round(1),
                        "% acumulado": acumulado.round(1)}))
    print()


pareto(fallos.groupby("shot_outcome")["xg_propio"].sum(),
       f"Pareto: xG perdido por tipo de resultado - {EQUIPO}",
       "pareto_resultado.png")

pareto(fallos.groupby("play_pattern")["xg_propio"].sum(),
       f"Pareto: xG perdido por patrón de juego - {EQUIPO}",
       "pareto_patron.png")