import pandas as pd

df = pd.read_csv("data/tiros_laliga.csv")

print("Filas y columnas:", df.shape)
print("\nColumnas disponibles:")
print(df.columns.tolist())

print("\nResultado de los tiros:")
print(df["shot_outcome"].value_counts())

print("\nTipo de tiro (jugada abierta, penal, tiro libre...):")
print(df["shot_type"].value_counts())

print("\nParte del cuerpo:")
print(df["shot_body_part"].value_counts())

print("\nCeldas vacías por columna:")
print(df.isnull().sum())

# Creamos una columna "gol": 1 si fue gol, 0 si no
df["gol"] = (df["shot_outcome"] == "Goal").astype(int)
print("\nGoles:", df["gol"].sum(), "de", len(df), "tiros")
print("Porcentaje de conversión:", round(df["gol"].mean() * 100, 1), "%")

print("\nMáximos goleadores de la temporada:")
print(df[df["gol"] == 1]["player"].value_counts().head(5))