""""Script de nettoyage et de préparation des données"""

# Chargement des bibliothèques nécessaires
import pandas as pd
from pathlib import Path

# Définition des chemins
base_dir = Path().resolve().parents[1]
print(f"Base directory: {base_dir}")
interim_dir = base_dir /"Patricia-Promise-Immo"/"data" / "interim"
print(f"Interim directory: {interim_dir}")
data_no_empty_path = interim_dir / "all_immo_no_empty.parquet"

# Lecture des données sans colonnes vides
df = pd.read_parquet(data_no_empty_path)

# Changement du type de la colonne 'Type local' en catégorie numérique
df['Type local'] = df['Type local'].replace({
    'Dépendance': 1,
    'Maison': 2,
    'Appartement': 3
})

# identification of different dtypes
ints = []
objects = []
floats = []
for column in df.columns.to_list():
    data_type = df[column].dtypes
    print(data_type)
    if data_type == 'int64':
        ints.append(column)
    if data_type == 'object':
        objects.append(column)
    if data_type == 'float64':
        floats.append(column)

# Remplacement des NaN ou None par 0
df_no_nan = df.fillna(value=0)

# Vérification des colonnes restantes après le remplacement des NaN
print(df_no_nan.columns)

# Dataframe avec seulement les colonnes de type objet
df_final= df_no_nan[objects]

# Dataframe final après suppression des colonnes de type objet
df_final = df_no_nan.drop(columns=objects)

# Supprimer les colonnes inutiles restantes
df_final = df_final.drop(columns=['Unnamed: 0','No voie'])

# Deinition du chemin de sauvegarde
features_immo_data_path =interim_dir / "features_immo_data.parquet"

# Sauvegarde du DataFrame final
df_final.to_parquet(features_immo_data_path)

# Visualisation des données manquantes
import missingno as msno
msno.matrix(df_final)


