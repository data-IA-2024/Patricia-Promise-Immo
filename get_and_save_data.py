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





# Telechargement, fusion et enregistrement des données en parquet

response = requests.get('https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234857/valeursfoncieres-2024.txt.zip', stream=True) #Stream = True afin d'éviter de tout charger en mémoire
    
# Enregistrement du fichier par itérations
with open(f"immo_entries_2024.txt.zip", 'wb') as file:
    for chunk in response.iter_content(chunk_size=10_000):
        file.write(chunk)


df = pd.read_csv(f"immo_entries_2024.txt.zip", nrows=100, on_bad_lines='skip', low_memory=False, sep='|', decimal=',', dtype={'Code postal':str, 'Valeur fonciere':np.float64})

 
    

first_file = True


df = pd.read_csv(f'immo_entries_2024.txt.zip', on_bad_lines='skip', low_memory=False, sep='|', decimal=',', dtype={'Code postal':str, 'Valeur fonciere':np.float64})
df.to_csv('all_immo_entries.csv')



df = pd.read_csv('all_immo_entries.csv', low_memory=False)
df.to_parquet('all_immo_entries.parquet')








