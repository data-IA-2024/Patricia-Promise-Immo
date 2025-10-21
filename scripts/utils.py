from pathlib import Path

# Définir le chemin de base et créer le dossier 'data' s'il n'existe pas
base = Path(__file__).resolve().parents[1]
print(f"Base path: {base}")
data_path = base/"data"
if not data_path.exists():
    data_path.mkdir(parents=True)

#Définir le chemin de base et créer le dossier 'infra-mlflow' s'il n'existe pas
base = Path(__file__).resolve().parents[2]
print(f"Base path: {base}")
data_path = base/"infra-mlflow"
if not data_path.exists():
    data_path.mkdir(parents=True)





