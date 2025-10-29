# %%
import pandas as pd
pd.options.display.max_rows = 999
pd.options.display.max_columns = 999
import requests 
import os
import numpy as np
import pyarrow
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path



# %%
# Definition des dossiers
git_folder = "Patricia-Promise-Immo"
folder_entries = "data"
base_dir = Path().resolve().parents[1]
data_dir = base_dir/git_folder/folder_entries
if not data_dir.exists():
    data_dir.mkdir(parents=True)
print(f"Data directory is set to : {data_dir}")

# %%
# Liste des fichiers à télécharger par année via leurs URLs
DOWNLOADs_ = [
    {
        'url' : 'https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234902/valeursfoncieres-2025-s1.txt.zip',
        'year' : '2025'
    },
    {
        'url' : 'https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234857/valeursfoncieres-2024.txt.zip',
        'year' : '2024'
    },
    {
        'url' : 'https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234851/valeursfoncieres-2023.txt.zip',
        'year' : '2023'
    },
    {
        'url' : 'https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234844/valeursfoncieres-2022.txt.zip',
        'year' : '2022'
    },
    {
        'url' : 'https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234836/valeursfoncieres-2021.txt.zip',
        'year' : '2021'
    },
    {
        'url' : 'https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234831/valeursfoncieres-2020-s2.txt.zip',
        'year' : '2020'
    }
    
    ]

# Téléchargement des fichiers par année
for immo_file in DOWNLOADs_ :
    response = requests.get(immo_file['url'], stream=True) #Stream = True afin d'éviter de tout charger en mémoire
    
    # Création du dossier 'raw' s'il n'existe pas pour stocker les fichiers téléchargés
    raw_dir = data_dir/"raw"
    if not raw_dir.exists():
        raw_dir.mkdir(parents=True)
        
    # Enregistrement du fichier par itérations
    with open(f"{raw_dir}/immo_entries_{immo_file['year']}.txt.zip", 'wb') as file:
        for chunk in response.iter_content(chunk_size=10_000):
            file.write(chunk)

print("Téléchargement terminé.")

# %%
# Liste des fichiers téléchargés
all_immo_files = os.listdir(raw_dir)
print("Fichiers téléchargés :")
for f in all_immo_files:
    print(f" - {f}")    

# %%
# Exploration des fichiers téléchargés et conversion en DataFrame Pandas
for immo_file in all_immo_files:
    df = pd.read_csv(f"{raw_dir}/{immo_file}", nrows=100, on_bad_lines='skip', low_memory=False, sep='|', decimal=',', dtype={'Code postal':str, 'Valeur fonciere':np.float64})
    print(df.columns.to_list())


# %%
"""
    Objectif: enregistrement des csv en 1 seul par chunks pour gérer efficacement la mémoire de la machine
    fichier final: all_immo_entries.csv dans un dossier 'interim'

"""
# Initialisation de la variable pour gérer l'écriture du header
first_file = True

# Création du dossier 'interim' s'il n'existe pas pour stocker les fichiers téléchargés
interim_dir = data_dir/"interim"
if not interim_dir.exists():
    interim_dir.mkdir(parents=True)

# Chemin du fichier de sortie
output_path = interim_dir/"all_immo_entries.csv"

for immo_file in all_immo_files:
    for index, chunk in enumerate(pd.read_csv(f'{raw_dir}/{immo_file}', on_bad_lines='skip', low_memory=False, sep='|', chunksize=10_000, decimal=',', dtype={'Code postal':str, 'Valeur fonciere':np.float64})):
        df.to_csv(f"{output_path}", mode = 'w' if first_file else 'a', header=first_file)
        first_file = False
    print(f'"{immo_file}" : DONE')

# %%
parquet_path= interim_dir/"all_immo_entries.parquet"
print(parquet_path)

writer = None

for index, chunk in enumerate(pd.read_csv(f"{output_path}", chunksize=10_000)):
    table = pa.Table.from_pandas(chunk, preserve_index=False)
    
    # Initialise le writer une seule fois avec le schéma du premier chunk
    if writer is None:
        writer = pq.ParquetWriter(parquet_path, schema=table.schema, compression="snappy")
    
    # Écrit le chunk courant
    writer.write_table(table)

# Ferme le writer à la fin
if writer is not None:
    writer.close()



# %%
df = pd.read_parquet(parquet_path)

print("Parquet file info:")
df.head(20)
df.info()


# %%
df.shape


