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



DOWNLOADs_ = [
    {
        'url' : 'https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234902/valeursfoncieres-2025-s1.txt.zip',
        'id' : '2025'
    },
    {
        'url' : 'https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234857/valeursfoncieres-2024.txt.zip',
        'id' : '2024'
    },
    {
        'url' : 'https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234851/valeursfoncieres-2023.txt.zip',
        'id' : '2023'
    },
    {
        'url' : 'https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234844/valeursfoncieres-2022.txt.zip',
        'id' : '2022'
    },
    {
        'url' : 'https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234836/valeursfoncieres-2021.txt.zip',
        'id' : '2021'
    },
    {
        'url' : 'https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234831/valeursfoncieres-2020-s2.txt.zip',
        'id' : '2020'
    } 
    ]

# Telechargement, fusion et enregistrement des données en parquet

all_immo_files = os.listdir('brut_data')

for immo_file in all_immo_files:
    df = pd.read_csv(f"brut_data/{immo_file}", nrows=100, on_bad_lines='skip', low_memory=False, sep='|', decimal=',', dtype={'Code postal':str, 'Valeur fonciere':np.float64})
    

first_file = True

for immo_file in all_immo_files:
    for index, chunk in enumerate(pd.read_csv(f'brut_data/{immo_file}', on_bad_lines='skip', low_memory=False, sep='|', chunksize=10_000, decimal=',', dtype={'Code postal':str, 'Valeur fonciere':np.float64})):
        df.to_csv('outputs/all_immo_entries.csv', mode = 'w' if first_file else 'a', header=first_file)
        first_file = False
    print(f'"{immo_file}" : DONE')

writer = None

for index, chunk in enumerate(pd.read_csv('outputs/all_immo_entries.csv', chunksize=10_000)):
    table = pa.Table.from_pandas(chunk, preserve_index=False)
    
    # Initialise le writer une seule fois avec le schéma du premier chunk
    if writer is None:
        writer = pq.ParquetWriter('outputs/all_immo_entries.parquet', schema=table.schema, compression="snappy")
    
    # Écrit le chunk courant
    writer.write_table(table)

# Ferme le writer à la fin
if writer is not None:
    writer.close()






