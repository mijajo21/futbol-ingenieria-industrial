import os
import time
import warnings
import pandas as pd
from statsbombpy import sb

warnings.filterwarnings("ignore")

COMPETICION_ID = 11          # La Liga
EQUIPO = "Barcelona"

# Un diccionario: nombre de la temporada -> su season_id
TEMPORADAS = {
    "2015/16": 27,
    "2016/17": 2,
    "2017/18": 1,
    "2018/19": 4,
    "2019/20": 42,
    "2020/21": 90,
}

COLUMNAS = [
    "minute", "team", "player", "location", "shot_outcome",
    "shot_body_part", "shot_type", "shot_technique", "play_pattern",
    "under_pressure", "shot_first_time", "shot_statsbomb_xg",
]

ARCHIVO_SALIDA = "data/tiros_barcelona_temporadas.csv"

os.makedirs("data", exist_ok=True)
todos = []

for nombre, season_id in TEMPORADAS.items():
    partidos = sb.matches(competition_id=COMPETICION_ID, season_id=season_id)

    # Nos quedamos solo con los partidos donde juega el Barcelona (local O visitante)
    partidos = partidos[(partidos["home_team"] == EQUIPO) | (partidos["away_team"] == EQUIPO)]
    print(f"Temporada {nombre}: {len(partidos)} partidos del {EQUIPO}")

    # iterrows() recorre la tabla fila por fila; 'fila' es cada partido
    for i, (_, fila) in enumerate(partidos.iterrows(), start=1):
        match_id = fila["match_id"]
        try:
            eventos = sb.events(match_id=match_id)
            tiros = eventos[eventos["type"] == "Shot"]
            columnas_ok = [c for c in COLUMNAS if c in tiros.columns]
            tiros = tiros[columnas_ok].copy()
            tiros["match_id"] = match_id
            tiros["fecha"] = fila["match_date"]      # NUEVO: fecha del partido
            tiros["temporada"] = nombre              # NUEVO: nombre de la temporada
            tiros["season_id"] = season_id
            todos.append(tiros)
        except Exception as e:
            print(f"  Error en partido {match_id}: {e}")

        if i % 10 == 0:
            print(f"  {i}/{len(partidos)} partidos")
        time.sleep(0.2)

df = pd.concat(todos, ignore_index=True)
df["x"] = df["location"].apply(lambda p: p[0])
df["y"] = df["location"].apply(lambda p: p[1])
df = df.drop(columns=["location"])

df.to_csv(ARCHIVO_SALIDA, index=False)

print(f"\nListo: {len(df)} tiros guardados en {ARCHIVO_SALIDA}")
print("\nTiros del Barcelona por temporada:")
print(df[df["team"] == EQUIPO].groupby("temporada").size())