import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Fútbol + Ingeniería Industrial", layout="wide")


@st.cache_data   # carga los datos una sola vez, para que la app sea rápida
def cargar():
    tiros = pd.read_csv("data/tiros_con_xg.csv")
    tiros["gol"] = (tiros["shot_outcome"] == "Goal").astype(int)
    partidos = pd.read_csv("data/partidos.csv", parse_dates=["match_date"])
    return tiros, partidos


tiros, partidos = cargar()

st.title("⚽ La Liga 2015/16 con enfoque de Ingeniería Industrial")
st.caption("Datos: StatsBomb Open Data. xG: modelo propio (regresión logística) "
           "sobre jugadas abiertas.")

equipos = sorted(tiros["team"].unique())
equipo = st.sidebar.selectbox("Equipo", equipos, index=equipos.index("Barcelona"))
st.sidebar.image("imagenes/statsbomb_logo.png", width=160)

tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Gráfico de control", "📊 Pareto", "🏆 Benchmark", "👤 Jugadores"]
)

# ---------- TAB 1: gráfico de control ----------
with tab1:
    datos = (tiros[tiros["team"] == equipo]
             .groupby("match_id")["xg_propio"].sum().reset_index()
             .merge(partidos, on="match_id").sort_values("match_date"))
    valores = datos["xg_propio"]
    media = valores.mean()
    sigma = valores.diff().abs().mean() / 1.128
    lcs = media + 3 * sigma
    lci = max(media - 3 * sigma, 0)
    fuera = datos[(valores > lcs) | (valores < lci)]

    c1, c2, c3 = st.columns(3)
    c1.metric("xG medio por partido", f"{media:.2f}")
    c2.metric("Límite superior (LCS)", f"{lcs:.2f}")
    c3.metric("Partidos fuera de límites", len(fuera))

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(datos["match_date"], valores, marker="o", color="navy", alpha=0.7)
    ax.axhline(media, color="green", label="Media")
    ax.axhline(lcs, color="red", linestyle="--", label="LCS")
    ax.axhline(lci, color="red", linestyle="--", label="LCI")
    ax.scatter(fuera["match_date"], fuera["xg_propio"], color="red", s=100, zorder=5)
    ax.set_ylabel("xG (jugadas abiertas)")
    ax.legend()
    st.pyplot(fig)
    st.caption("Puntos rojos = causa especial (fuera de límites). "
               "Si no hay ninguno, la variación es normal.")

# ---------- TAB 2: Pareto ----------
with tab2:
    opciones = {"Tipo de resultado": "shot_outcome", "Patrón de juego": "play_pattern"}
    nombre = st.radio("Agrupar por", list(opciones), horizontal=True)
    col = opciones[nombre]

    fallos = tiros[(tiros["team"] == equipo) & (tiros["gol"] == 0)]
    serie = fallos.groupby(col)["xg_propio"].sum().sort_values(ascending=False)
    acumulado = serie.cumsum() / serie.sum() * 100

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(serie.index, serie.values, color="steelblue")
    ax.set_ylabel("xG perdido")
    ax.tick_params(axis="x", rotation=30)
    ax2 = ax.twinx()
    ax2.plot(serie.index, acumulado.values, color="red", marker="o")
    ax2.axhline(80, color="gray", linestyle="--")
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("% acumulado")
    plt.tight_layout()
    st.pyplot(fig)

# ---------- TAB 3: benchmark ----------
with tab3:
    resumen = tiros.groupby("team").agg(goles=("gol", "sum"), xg=("xg_propio", "sum"))
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(resumen["xg"], resumen["goles"], color="lightgray")
    sel = resumen.loc[equipo]
    ax.scatter(sel["xg"], sel["goles"], color="red", s=120)
    ax.annotate(equipo, (sel["xg"], sel["goles"]), xytext=(6, 6),
                textcoords="offset points")
    maximo = max(resumen["xg"].max(), resumen["goles"].max()) + 5
    ax.plot([0, maximo], [0, maximo], color="gray", linestyle="--")
    ax.set_xlabel("xG (calidad de las ocasiones)")
    ax.set_ylabel("Goles reales")
    st.pyplot(fig)
    st.caption("Sobre la línea punteada = rinde por encima de lo esperado.")

# ---------- TAB 4: jugadores ----------
with tab4:
    minimo = st.slider("Mínimo de tiros", 10, 100, 40)
    jug = (tiros[tiros["team"] == equipo].groupby("player")
           .agg(tiros=("gol", "size"), goles=("gol", "sum"), xg=("xg_propio", "sum")))
    jug = jug[jug["tiros"] >= minimo]
    jug["diferencia"] = (jug["goles"] - jug["xg"]).round(1)
    jug["xg"] = jug["xg"].round(1)
    st.dataframe(jug.sort_values("diferencia", ascending=False))