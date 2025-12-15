"""Chargement des librairies"""
import pandas as pd
import requests 
import os
import numpy as np
from pathlib import Path
import glob, zipfile, io, logging

#---
# Configuration du logging
logging.basicConfig(level = logging.INFO, format="%(levelname)s - %(message)s")

#--- Déclarations des variables globales
# Configuration statique de la liste des fichiers à télécharger par année via leurs URLs
DOWNLOADS_ = [
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

CHUNK = 200_000

#---
# définition du repertoire racine
def root_dir()->Path:
    return Path(__file__).resolve().parents[2]


#--- Création des dossiers data, raw et raw_csv
def ensure_dir(base: Path):
    # Definition des dossiers
    data_dir = base/"Patricia-Promise-Immo"/"data"
    raw_dir = data_dir/"raw"
    csv_dir = data_dir/"raw_csv"
    # Création des dossiers s'ils n'existent pas
    raw_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    return data_dir, raw_dir, csv_dir

#---
"""Téléchargement et extraction des fichiers de données foncières depuis data.gouv.fr"""
def download_file(raw_dir:Path):
    session = requests.Session()
    # Téléchargement des fichiers par année
    for item in DOWNLOADS_ :
        url = item["url"]
        out = raw_dir/f"immo_entries_{item['year']}.txt.zip"
        if out.exists() and out.stat().st_size>0:
            logging.info(f"Le fichier {out.name} existe déjà. Téléchargement ignoré.")
            continue
        logging.info(f"Téléchargement du fichierndepuis l'url:{url} vers le chemin: {out}")
        # Enregistrement du fichier par itérations
        try:
            with session.get(url, stream=True, timeout=(5,30)) as response:
                response.raise_for_status()
                with open(out, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=1024 * 64):
                        if chunk:
                            file.write(chunk)
            logging.info(f"Téléchargement terminé et enregistré dans le repertoire: {out.name}")
        except Exception as e:
            logging.error(f"Téléchargement échouè de {url}:{e}")

#---
"""Extration des fichiers .txt.zip téléchargès en fichiers .csv"""

def unzip_txt_to_csv(raw_dir:Path, csv_dir:Path):

    # Récupération des fichiers .txt.zip pour conversion en .csv
    files_texts = sorted(glob.glob("*.txt.zip", root_dir=raw_dir))
    logging.info(f"{len(files_texts)} fichiers trouvés pour extraction et conversions en csv dans {raw_dir.name}")

    # Definition du chemin des fichiers qui seront convertis en .csv
  
    for f in files_texts:
        zip_path = raw_dir/f
        out_name = Path(f).name.replace(".txt.zip", ".csv") # On recupère juste le nom du futur fichier
        out_path = csv_dir/out_name
    
        # Vérification du chemin out_path
        if out_path.exists():
            out_path.unlink() # Supprime le ficchier qui existe déjà avant de créer un nouveau
        try:  
            # Lire le .txt.zip compréssé à l'interieur du .zip
            with zipfile.ZipFile(zip_path, "r") as zf:
                names=[n for n in zf.namelist() if n.lower().endswith(".txt")]
                if not names:
                    logging.warning(f"Aucun fichier .txt trouvé dans {zip_path.name}, skip.")
                    continue
                first = True
                with zf.open(names[0], "r") as fb:
                    stream_txt = io.TextIOWrapper(fb, encoding="utf-8", errors="ignore")
                    # Convertir chaque élément en DataFrame  et l'écrire en .csv par chunks
                    for chunk in pd.read_csv(stream_txt, sep="|", chunksize= CHUNK,  low_memory=False, decimal=',', dtype={'Code postal':str, 'Valeur fonciere':np.float64}, on_bad_lines='skip'):
                        # Sauvegarde du DataFrame eb fichier .csv
                        chunk.to_csv(out_path, index=False, mode = "a", header= first)
                        first = False # Après la première écriture du header, il faut plus écrire l'entête et on le désactive pour les chunhs suivants avcec first = False
            logging.info(f"Récupération du fichier en .csv terminé avec succès et enregistré dans {out_path.name}")
        except Exception as e:
            logging.error(f"Erreur lors de l'extration des ficihiers :{e}")
   
def main():
    # définition du repertoire racine
    base = root_dir()
    logging.info(f"Le repertoire racine est: {base}")

    # Création des dossierrs data, raw et raw_csv
    data_dir, raw_dir, csv_dir = ensure_dir(base)
    logging.info(f"Le repertoire data est: {data_dir}")

    # Téléchargement des fichiers depuis data.gouv.fr
    download_file(raw_dir)
    logging.info(f"Téléchargement des fichiers terminé.")

    # Visualisation de la liste des fichiers téléchargés
    all_immo_files = sorted(f.name for f in raw_dir.iterdir() if f.is_file())
    logging.info("Fichiers téléchargés : \n" + "\n".join(f"- {f}" for f in all_immo_files))   
    
    # Extration des fichiers textes zippés en fichiers .csv
    unzip_txt_to_csv(raw_dir, csv_dir)
    logging.info(f"Extraction des fichiers .csv terminées")

if __name__ == "__main__":
    main()