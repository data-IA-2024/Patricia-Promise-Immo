# Prédire le prix d’un bien immobilier

> Application et pipeline ML pour estimer le prix d’un bien à partir de ses caractéristiques et de données DVF.

---

##  Aperçu

Ce projet propose une **application** et un **pipeline de data science** qui préparent les données, entraînent un **modèle de prédiction** et exposent une **interface** (CLI/API) pour estimer le **prix d’un bien immobilier**.

* **Données** : Demandes de Valeurs Foncières (DVF) – France (source officielle data.gouv).
* **Objectif** : fournir une estimation robuste et explicable du prix à partir de caractéristiques clés (surface, pièces, localisation, etc.).
* **Public cible** : étudiants/étude ML, POC interne, base pour produit data.

---

##  Objectifs

* Construire un **pipeline reproductible** (préparation → features → entraînement → évaluation → service).
* **Documenter** les hypothèses, limites et métriques (MAE, RMSE, R²).
* Offrir une **expérience d’usage simple** (commandes claires, exemples).

---

##  Fonctionnalités

* Préparation et nettoyage des données DVF (déduplication, filtres, outliers).
* Feature engineering minimal (prix/m², âge du bien, encodages catégoriels, géo-features).
* Entraînement d’un modèle de régression (baseline + modèle avancé type Gradient Boosting/XGBoost).
* Évaluation standard (MAE, RMSE, R²) + sauvegarde des artefacts.
* Service d’inférence (CLI et API FastAPI).

---

##  Structure du projet (suggestion)

```bash
.
├── app/                    # (optionnel) API FastAPI pour l’inférence
│   └── main.py
├── data/
│   ├── raw/               # fichiers DVF bruts
│   ├── interim/           # données nettoyées/intermédiaires
│   └── processed/         # dataset final prêt pour le ML
├── notebooks/             # EDA, prototypes
├── output/                # rapports, figures, logs
├── scripts/               # scripts CLI
│   ├── prepare_data.py
│   ├── build_features.py
│   ├── train.py
│   └── predict.py
├── artifacts/             # modèles, encodeurs, scalers
├── requirements.txt
├── README.md
└── .env.example           # variables d’environnement
```

---

##  Données

* **Source** : [data.gouv – Demandes de Valeurs Foncières]
* **Entrées attendues (exemples)** :

  * `surface_living`, `rooms`, `bedrooms`, `bathrooms`, `property_type`
  * `city`, `postal_code`, `latitude`, `longitude`
  * `year_built`, `condition`, `energy_class`
  * (optionnel) `average_price_m2_area`
* **Cible** : `price`

> Le pipeline charge les fichiers DVF (CSV), filtre les enregistrements non pertinents (ventes non représentatives, valeurs manquantes critiques), harmonise les colonnes et calcule des variables dérivées (prix/m², âge, etc.).

---

##  Prérequis

* **Python** ≥ 3.10.11  `(recommandé : 3.11.1)`
* `pip`, `virtualenv` (ou `conda`)

---

##  Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pip install dvc
```

Crée un fichier `.env` (ou copie `.env.example`) si nécessaire pour les chemins par défaut.

---

##  Outil de versionning des données
```bash
    dvc init
    git add .dvc .gitignore
    git commit -m "Initialisation de DVC"

   # Ajouter un dataset à suivre
    dvc add D:/ProjectFolderDevAI_2025-2026/Immo_project/Patricia-Promise-Immo/data # chemin absolu requis

  # Ajout dans git du dataset versionné avec DVC
    git add D:/ProjectFolderDevAI_2025-2026/Immo_project/Patricia-Promise-Immo/data.dvc .gitignore 
    git commit -m "Ajout du dataset versionné avec DVC"

```
---

##  Pipeline (pas à pas)

### 1) Préparer les données (raw → interim)

```bash
  python scripts/prepare_data.py \
  --input data/raw \
  --output data/interim
```

### 2) Construire les features (interim → processed)

```bash
python scripts/build_features.py \
  --input data/interim \
  --output data/processed/dataset.csv
```

### 3) Entraîner le modèle

```bash
python scripts/train.py \
  --data data/processed/dataset.csv \
  --model artifacts/model.pkl \
  --metrics output/metrics.json
```

### 4) Prédire (inférence CLI)

```bash
python scripts/predict.py \
  --model artifacts/model.pkl \
  --features '{"surface_living":65, "rooms":3, "bedrooms":2, "postal_code":"75011", "latitude":48.857, "longitude":2.379, "year_built":1975, "property_type":"apartment"}'
```

### (Optionnel) Lancer l’API

```bash
uvicorn app.main:app --reload
```

* **POST** `/predict` : JSON des features → prix estimé

---

##  Évaluation

* **Métriques** :

  * **MAE** (Mean Absolute Error)
  * **RMSE** (Root Mean Squared Error)
  * **R²** (coefficient de détermination)
* **Validation** : train/validation split ou K-fold ; veille à une **stratification géographique** si possible.

Les scores sont exportés dans `output/metrics.json` et les figures (importance des features, résidus) dans `output/`.

---

##  Explicabilité

* Importance globale des features (Permutation, SHAP en option).
* Sanity checks : cohérence du prix avec surface, localisation, âge.

---

##  Limites & biais

* Données DVF **hétérogènes** selon les zones et années.
* **Outliers** et ventes atypiques (droits, divisions parcelles, etc.).
* Effets **non observés** (qualité du bâti, vue, nuisances fines, étage exact avec ascenseur, rénovation récente).
* Risque de **sur-apprentissage local** si trop de features géographiques fines sans régularisation.

---

##  Roadmap

* ✅ Baseline + modèle avancé
* ⏭️ Normalisation du schéma features (schema contract + validation Pydantic)
* ⏭️ Monitoring des performances hors-échantillon (drift data)
* ⏭️ Ajout de sources contextuelles (transports, écoles, criminalité) via agrégation géospatiale
* ⏭️ Tableau de bord (Streamlit/FastAPI + templates)

---

##  Contributions

* Issues & PR bienvenues : respecter la structure, documenter les changements.

---

##  Licence

* À définir (MIT/Apache-2.0…)

---

##  Remerciements

* Source DVF – Ministère de l’Économie/Finances (via data.gouv)
* Communauté open source (pandas, scikit-learn, FastAPI, etc.)
