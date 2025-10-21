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


class DATA_PREP:
    def __init__(self, downloads:object, base_folder, output_folder):
        self.downloads = downloads # liste d'objet contenant les liens vers les datasets
        self.base_folder = base_folder # chemin du dossier ou sauvegarder datasets brut
        self.output_folder = output_folder

    # NON CALLABLE MOTHODS (HIDDEN METHODS)
    def get_datasets(self):
        """
        Cette fonction permet de telecharger des datasets grace a requests (txt ou csv).
        """
        for immo_file in self.downloads :
            response = requests.get(immo_file['url'], stream=True) #Stream = True afin d'éviter de tout charger en mémoire
            
            # Enregistrement du fichier par itérations
            with open(f"{self.base_folder}/immo_entries_{immo_file['id']}.txt.zip", 'wb') as file:
                for chunk in response.iter_content(chunk_size=10_000):
                    file.write(chunk)
    
    def merge_and_save_as_parquet(self, sep_='|', decimal_=',', dtype_={'Code postal':str, 'Valeur fonciere':np.float64}):
        """
        Fontion pour fusionner les datasets en parquets
        """
        all_immo_files = os.listdir('data')
        # Ajout des ficher dans 1 csv unique
        first_file = True
        for immo_file in all_immo_files:
            for index, chunk in enumerate(pd.read_csv(f'{self.base_folder}/{immo_file}', on_bad_lines='skip', low_memory=False, sep=sep_, chunksize=10_000, decimal=decimal_, dtype=dtype_)):
                chunk.to_csv(f'{self.output_folder}/all_immo_entries.csv', mode = 'w' if first_file else 'a', header=first_file)
                first_file = False
            print(f'"{immo_file}" : DONE')

        # Create as parquet
        writer = None

        for index, chunk in enumerate(pd.read_csv(f'{self.output_folder}/all_immo_entries.csv', chunksize=10_000)):
            table = pa.Table.from_pandas(chunk, preserve_index=False)
            
            # Initialise le writer une seule fois avec le schéma du premier chunk
            if writer is None:
                writer = pq.ParquetWriter(f'{self.output_folder}/all_immo_entries.parquet', schema=table.schema, compression="snappy")
            
            # Écrit le chunk courant
            writer.write_table(table)

        # Ferme le writer à la fin
        if writer is not None:
            writer.close()


            