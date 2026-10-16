import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score

# --- Perillas: de dónde leer y dónde guardar ---
ARCHIVO_ENTRENAMIENTO = "data/respaldo_2015_16/tiros_laliga.csv"   # con esto aprende
ARCHIVO_NUEVO = "data/tiros_laliga.csv"                            # esto es 2018/19
ARCHIVO_SALIDA = "data/tiros_con_xg.csv"                           # lo que se va a crear

ARCO_X, CENTRO_Y, POSTE_1, POSTE_2 = 120, 40, 36, 44
VARIABLES = ["distancia", "angulo", "cabeza"]


# Una "receta guardada con nombre": prepara una tabla de tiros.
# La definimos una vez y la usamos dos veces, para no repetir el código.
def preparar(df):
    df = df[df["shot_type"] == "Open Play"].copy()            # solo jugadas abiertas
    df["gol"] = (df["shot_outcome"] == "Goal").astype(int)    # 1 = gol, 0 = no gol

    dx = ARCO_X - df["x"]
    df["distancia"] = np.sqrt(dx**2 + (CENTRO_Y - df["y"])**2)

    v1y = POSTE_1 - df["y"]
    v2y = POSTE_2 - df["y"]
    cruz = dx * v2y - v1y * dx
    punto = dx * dx + v1y * v2y
    df["angulo"] = np.abs(np.arctan2(cruz, punto))

    df["cabeza"] = (df["shot_body_part"] == "Head").astype(int)
    return df                                                  # devuelve la tabla lista


# 1. Preparar las dos tablas con la misma receta
entrenamiento = preparar(pd.read_csv(ARCHIVO_ENTRENAMIENTO))
nuevo = preparar(pd.read_csv(ARCHIVO_NUEVO))

# 2. Aprender SOLO con la temporada de entrenamiento (2015/16)
modelo = LogisticRegression()
modelo.fit(entrenamiento[VARIABLES], entrenamiento["gol"])

# 3. Aplicar lo aprendido a la temporada nueva (2018/19)
nuevo["xg_propio"] = modelo.predict_proba(nuevo[VARIABLES])[:, 1]

# 4. Examen: ¿qué tal le fue en una temporada que nunca vio?
print(f"Tiros de entrenamiento (2015/16): {len(entrenamiento)}")
print(f"Tiros nuevos (2018/19):           {len(nuevo)}")
print("\n=== RESULTADOS EN LA TEMPORADA NUEVA ===")
print("Goles reales:      ", nuevo["gol"].sum())
print("xG de mi modelo:   ", round(nuevo["xg_propio"].sum(), 1))
print("xG de StatsBomb:   ", round(nuevo["shot_statsbomb_xg"].sum(), 1))
print("\nBrier (menor es mejor):")
print("  Mi modelo: ", round(brier_score_loss(nuevo["gol"], nuevo["xg_propio"]), 4))
print("  StatsBomb: ", round(brier_score_loss(nuevo["gol"], nuevo["shot_statsbomb_xg"]), 4))
print("\nAUC (0.5 = azar, 1 = perfecto):")
print("  Mi modelo: ", round(roc_auc_score(nuevo["gol"], nuevo["xg_propio"]), 3))
print("  StatsBomb: ", round(roc_auc_score(nuevo["gol"], nuevo["shot_statsbomb_xg"]), 3))

# 5. Guardar para los análisis siguientes
nuevo.to_csv(ARCHIVO_SALIDA, index=False)
print(f"\nGuardado en {ARCHIVO_SALIDA}")