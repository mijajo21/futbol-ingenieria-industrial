import warnings
from statsbombpy import sb

warnings.filterwarnings("ignore")

partidos = sb.matches(competition_id=11, season_id=4)
partidos[["match_id", "match_date"]].to_csv("data/partidos.csv", index=False)
print("Guardado data/partidos.csv:", len(partidos), "partidos")