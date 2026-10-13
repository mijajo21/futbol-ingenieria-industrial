from statsbombpy import sb

competiciones = sb.competitions()
laliga = competiciones[competiciones["competition_name"] == "La Liga"]
print(laliga[["season_name", "competition_id", "season_id"]])