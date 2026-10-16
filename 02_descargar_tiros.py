import os
import time
import warnings
import pandas as pd
from statsbombpy import sb

warnings.filterwarnings("ignore")

COMPETICION_ID = 11      # La Liga
TEMPORADAS = [4]        # 27 = 2018/2019

COLUMNAS = [
    "minute", "team", "player", "location", "shot_outcome",
    "shot_body_part", "shot_type", "shot_technique", "play_pattern",
    "under_pressure", "shot_first_time", "shot_statsbomb_xg",
]

os.makedirs("data", exist_ok=True)
todos = []

for temporada in TEMPORADAS:
    partidos = sb.matches(competition_id=COMPETICION_ID, season_id=temporada)
    print(f"Temporada {temporada}: {len(partidos)} partidos")

    for i, match_id in enumerate(partidos["match_id"], start=1):
        try:
            eventos = sb.events(match_id=match_id)
            tiros = eventos[eventos["type"] == "Shot"]
            columnas_ok = [c for c in COLUMNAS if c in tiros.columns]
            tiros = tiros[columnas_ok].copy()
            tiros["match_id"] = match_id
            tiros["season_id"] = temporada
            todos.append(tiros)
        except Exception as e:
            print(f"  Error en partido {match_id}: {e}")

        if i % 10 == 0:
            print(f"  {i}/{len(partidos)} partidos")
        time.sleep(0.2)

df = pd.concat(todos, ignore_index=True)

# La ubicación viene como [x, y]; la separamos en dos columnas
df["x"] = df["location"].apply(lambda p: p[0])
df["y"] = df["location"].apply(lambda p: p[1])
df = df.drop(columns=["location"])

df.to_csv("data/tiros_laliga.csv", index=False)
print(f"\nListo: {len(df)} tiros guardados en data/tiros_laliga.csv")
print(df.head())