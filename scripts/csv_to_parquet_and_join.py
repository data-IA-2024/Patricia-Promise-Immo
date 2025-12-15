"""Récuperation des fichiers .csv, conversion en parquet partitionné par année et jointure avec les données des communes INSEE"""
# Chargement des bibliothèques nécessaires
import pandas as pd
import logging
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path


# Configuration des logs
logging .basicConfig(level = logging.INFO, format="%(levelname)s - %(message)s")

# Variable globales 
CHUNK = 200_000

# Definition des chemins
base = Path(__file__).resolve().parents[1]
raw_csv_dir = Path(base/"data"/"raw_csv")
out_dir = Path(base/"data"/"interim")
out_dir.mkdir(parents=True, exist_ok=True)

communes_path = Path(base/"data"/"raw_csv"/"communes_france_2025.csv")

# Definition de la fonction qui recupère les années de la colonne 'date_mutation'
def get_year_from_date(df: pd.DataFrame)->pd.DataFrame:
    cols = {c.lower().strip(): c for c in df.columns}
    if "date mutation" not in cols:
        logging.error("La colonne \"date mutation\" n'existe pas dans le DataFrame")
    date_col = cols["date mutation"]
    s = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
    df["years"] = s.dt.year.astype("Int16")
    return df

# Definition de la fonction qui va normalyser la colonne " code insee"
def normalize_code_insee(s: pd.Series)->pd.Series:
    return (s.astype("string")
            .str.strip()
            .str.replace(r"\s+", "", regex= True)
            .str.zfill(5))

# Fonction principale qui convertit lesz fichiers .csv en parquet partitionné par année et joint avec les données des communes INSEE
def main():
    # Traitement du fichier des communes
    df_com =pd.read_csv(communes_path, on_bad_lines="skip", low_memory=False, sep=",", dtype="string")
    df_com.columns = df_com.columns.str.lower().str.strip()
    if "code_insee" not in df_com.columns:
        logging.error("La colonne 'code insee' n'existe pas dans le fichier des communes")
    df_com["code_insee"]= normalize_code_insee(df_com["code_insee"])

    writers = {}
    schemas = {}
    try:
        # récupération des fichiers .csv
        for csv_file in sorted(raw_csv_dir.glob("*.csv")):
            # Ignorer le fichier du referentiel des commune dans raw_csv/
            print(csv_file.name)
            if csv_file.name == "communes_france_2025.csv":
                logging.info(f"Ignorer le fichier de communes: {csv_file.name}")
                continue

            logging.info(f"Traitement des fichiers:{csv_file.name}")
            for chunk in pd.read_csv(csv_file, sep=",",chunksize=CHUNK, low_memory=False, dtype="string", on_bad_lines="skip"):

                # Récupération de l'année à partir de la date de mutation
                chunk=get_year_from_date(chunk)
                if "years" not in chunk.columns:
                    logging.error(f"'years' manquante dans {csv_file.name}, chunk ignoré")
                    continue

                # Composition du code INSEE à partir des codes département et commune
                chunk['Code INSEE'] = (chunk['Code departement'] + chunk['Code commune'])
                print(chunk['Code INSEE'])
                # normalisation de la colonne "code insee"
                chunk_cols={c.lower().strip(): c for c in chunk.columns}
                
                if "code insee" in chunk_cols:                
                    key = chunk_cols["code insee"]
                    chunk["Code INSEE"] = normalize_code_insee(chunk["Code INSEE"])
                    dvf_key = key
                elif "code commune" in chunk_cols:
                    dvf_key = "code insee"
                    chunk[dvf_key] = normalize_code_insee(chunk[chunk_cols["code commune"]])
                else:
                    dvf_key = None
                    logging.error(f"Aucune colonne code insee ou code commune n'existe dans le fichier .scv : {csv_file.name}")

                # jointure avec le referentiel des communes sur la colonne "code insee" pour l'année 2025
                if dvf_key is not None:
                    mask_2025 = chunk["years"] == 2025
                    if mask_2025.any():
                        part_2025 = chunk.loc[mask_2025].merge(df_com, how = "left", left_on = dvf_key, right_on="code_insee")
                        chunk = pd.concat([chunk.loc[~mask_2025], part_2025], ignore_index=True)
                
                for year in chunk["years"].dropna().unique():
                    year = int(year)
                    part = chunk.loc[chunk["years"] == year]

                    # Conversion du chunk en parquet partitionné par année
                    table = pa.Table.from_pandas(part, preserve_index= False)

                    # Ecriture du fichier parquet partitionné par année
                    if year not in writers:
                        # Chemin du fichier parquet de sortie
                        out_path = out_dir/f"immo_entries_{year}.parquet"
                        if out_path.exists():
                            out_path.unlink() 

                        writers[year] = pq.ParquetWriter(out_path, table.schema, compression="snappy")
                        schemas[year] = table.schema
                    else:
                        if table.schema != schemas[year]:
                            cols = [col.name for col in schemas[year]]
                            part = part.reindex(columns=cols)
                            pa.Table.from_pandas(part, preserve_index= False)
                
                    writers[year].write_table(table)
                    logging.info(f"Fichier parquet écrit avec succès dans le répertoire: {out_dir} partitionné par année")
    finally:
        for w in writers.values():
            w.close()
        logging.info(f"Écriture terminée : 1 fichier .parquet enregistré dans {out_dir}")

if "__name__" == "__name__":
    main()