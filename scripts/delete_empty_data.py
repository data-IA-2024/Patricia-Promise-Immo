"""Script pour supprimer les colonnes trop vides dans le jeu de données immobilier"""
# chargement des librairies
import pandas as pd
from pathlib import Path



# Création du dossier 'interim' s'il n'existe pas pour stocker les fichiers téléchargés
git_folder = "Patricia-Promise-Immo"
folder_entries = "data"
base_dir = Path().resolve().parents[1]
data_dir = base_dir/git_folder/folder_entries
interim_dir = data_dir/"interim"
if not interim_dir.exists():
    interim_dir.mkdir(parents=True)
    

# Définition des chemins
base_dir = Path().resolve().parents[1]
print(f"Base directory: {base_dir}")
data_dir = base_dir /"Patricia-Promise-Immo"/"data" 
print(f"Interim directory: {data_dir}")
data_path = data_dir / "immo_entries_2024.txt.zip"

# Lecture des données du parquet 
df = pd.read_csv(data_path)

"""Réccupération d'uniquement les colonnes remplies"""

# liste pour stocker les colonnes vides
emptyness_infos = []

# nombre total de lignes
total_rows = df.shape[0] 
print(f"Total rows: {total_rows}")

# Définition de la liste des colonnes
columns = df.columns.tolist()

# pour chaque colonnes calcul du pourcentage de vide
for column in columns: 
    column_emptyness = df[df[column].isna()].shape[0] #nombre total de lignes vide dans la colone
    column_emptyness_rate = column_emptyness / total_rows * 100

    # création du dictionnaire d'information pour la colone
    info = {
        'name': column,
        'pourcentage_vide' : column_emptyness_rate
    }

    # ajout des informations à la liste
    emptyness_infos.append(info)

# création du dataframe d'informations sur la vacuité des colonnes
df_emptyness =  pd.DataFrame(emptyness_infos)
print(df_emptyness)

#--- Affichage du dataframe des colonnes vides ---
df_emptyness
rempli = []
completement_vide = []
assez_rempli = []

""""
    Séparation des colonnes en trois listes :
    - rempli : colonnes sans aucune valeur vide
    - complètement_vide : colonnes avec 100% de valeurs vides
    - assez_rempli : colonnes avec au moins une valeur remplie
"""
for index, row in enumerate(df_emptyness.iterrows()):
    current_column = df_emptyness.iloc[index]
    # si pourcentage de vide superieur a 96% ajout a la liste 'trop vide'
    if current_column['pourcentage_vide'] == 0:
        rempli.append(current_column['name'])

    # si pourcentage de vide egal à 100% ajout a la liste 'completement vide'
    if current_column['pourcentage_vide'] == 100 :
        completement_vide.append(current_column['name'])
    
    if current_column['pourcentage_vide'] < 100 :
        assez_rempli.append(current_column['name'])

# Definition du nouveau jeu de données sans les colonnes trop vides
data_no_empty_path =interim_dir / "all_immo_no_empty.csv"

# Sauvegarde du nouveau jeu de données sans les colonnes trop vides
df[assez_rempli].to_csv(data_no_empty_path)


