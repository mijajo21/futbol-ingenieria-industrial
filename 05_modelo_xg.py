import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import brier_score_loss, roc_auc_score

df = pd.read_csv("data/tiros_laliga.csv")

# 1. Solo jugadas abiertas (sin penales, tiros libres ni córners)
df = df[df["shot_type"] == "Open Play"].copy()

# 2. Lo que queremos predecir: 1 = gol, 0 = no gol
df["gol"] = (df["shot_outcome"] == "Goal").astype(int)

# 3. Distancia y ángulo (arco en x=120, postes en y=36 y y=44)
ARCO_X, CENTRO_Y, POSTE_1, POSTE_2 = 120, 40, 36, 44

dx = ARCO_X - df["x"]
df["distancia"] = np.sqrt(dx**2 + (CENTRO_Y - df["y"])**2)

# Ángulo entre las líneas que van del tiro a cada poste
v1y = POSTE_1 - df["y"]
v2y = POSTE_2 - df["y"]
cruz = dx * v2y - v1y * dx
punto = dx * dx + v1y * v2y
df["angulo"] = np.abs(np.arctan2(cruz, punto))

# 4. Cabeza: 1 si fue de cabeza, 0 si no
df["cabeza"] = (df["shot_body_part"] == "Head").astype(int)

# 5. Separar: 70% para aprender, 30% para el "examen sorpresa"
X = df[["distancia", "angulo", "cabeza"]]
y = df["gol"]
X_train, X_test, y_train, y_test, sb_train, sb_test = train_test_split(
    X, y, df["shot_statsbomb_xg"], test_size=0.3, random_state=42
)

# 6. Entrenar el modelo
modelo = LogisticRegression()
modelo.fit(X_train, y_train)

# 7. Evaluar en el examen sorpresa
xg_propio = modelo.predict_proba(X_test)[:, 1]

print("=== RESULTADOS EN EL EXAMEN (tiros que el modelo no vio) ===")
print("Goles reales:        ", y_test.sum())
print("xG de mi modelo:     ", round(xg_propio.sum(), 1))
print("xG de StatsBomb:     ", round(sb_test.sum(), 1))

print("\nError promedio (Brier, menor es mejor):")
print("  Mi modelo:  ", round(brier_score_loss(y_test, xg_propio), 4))
print("  StatsBomb:  ", round(brier_score_loss(y_test, sb_test), 4))

print("\nCapacidad de ordenar tiros de menos a más peligrosos (AUC, 0.5 = azar, 1 = perfecto):")
print("  Mi modelo:  ", round(roc_auc_score(y_test, xg_propio), 3))
print("  StatsBomb:  ", round(roc_auc_score(y_test, sb_test), 3))

# 8. Guardar el xG de mi modelo para usarlo después
df["xg_propio"] = modelo.predict_proba(X)[:, 1]
df.to_csv("data/tiros_con_xg.csv", index=False)
print("\nGuardado en data/tiros_con_xg.csv")