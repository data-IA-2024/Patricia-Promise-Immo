"""Chargement des bibliothèques nécessaires"""
# Pour manipuler les données
import pandas as pd

# Pour gérer les chemins de fichiers
from pathlib import Path

# Import des modèles de sklearn
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

# Pour sauvegarder les modèles
import joblib

# Définition des constantes
RANDOM_STATE = 42

# Définition des chemins
base_dir = Path().resolve().parents[1]
path_data = base_dir / "Patricia-Promise-Immo" / "data"/"processed"
features_path = path_data / "features_immo_data.csv"

# Chargement des données
df = pd.read_csv(f"{features_path}")

# Sélection des colonnes permettant de faire des prédictions
y = df["Valeur fonciere"]
#features_column = ["Code postal", "Code departement", "Code commune", "Type local","Surface reelle bati", "Nombre pieces principales", "Surface terrain","prixm2" ]
X = df.drop(columns=["Valeur fonciere"]) 

# Déclaration des données en ensembles d'entraînement et de test 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE, shuffle=True)

# Visualiser les colonnes du Dataframe
df.columns.tolist()

# Déclaration du modèle pipeline
model = RandomForestRegressor(n_estimators=100, max_depth=None, min_samples_split=2, n_jobs=-1, random_state=RANDOM_STATE)

# Entrainement du modèle
model.fit(X_train, y_train)

# Faire la prédiction
prediction = model.predict(X_test)

"""# Définir le validateur KFold
cv = KFold(n_splits=5, shuffle=True, random_state=42)"""

# Evaluation du modele
mae  = mean_absolute_error(y_test, prediction)
rmse = mean_squared_error(y_test, prediction)
r2   = r2_score(y_test, prediction)

# Affichages des métrics
print("=== Scores du test ===")
print(f"Moyenne des erreurs absolues :{mae:,.0f}")
print(f"Moyenne carrée des erreurs :{rmse:,.0f}")
print(f"Coefficient de détyermination :{r2:,.3f}")

# definir le chemin de sauvegarde du modèle
base_dir = Path().resolve().parents[1]
artefact_path = base_dir/"Patricia-Promise-Immo"/"artefacts"
if not artefact_path.exists():
    artefact_path.mkdir(parents = True)
print(artefact_path)

# Chemin de output du modèle
model_path = artefact_path/"Modèle_prix_dvf.joblib"

# Sauvegarder le pipeline
joblib.dump("model",f"{model_path}_v1")
print(f"Sauvegarde du pipeline du modèle éffectuée avec succès ==> {model_path}")