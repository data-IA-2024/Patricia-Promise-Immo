
import requests
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score
import os
import joblib
import shap
import matplotlib.pyplot as plt

class ImmoData:
    def __init__(self, output_path, artefact_path):
        self.output_path = output_path
        self.artefact_path = artefact_path 
        self.mrse = 0
    
    def get_immo_data(self):
        """Réccupération des données immobiliaires"""
        print("start of the data retrival")
        response = requests.get('https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20251018-234857/valeursfoncieres-2024.txt.zip', stream=True)
        with open(f'{self.output_path}/immo_entries_2024.txt.zip', 'wb') as file:
            for chunk in response.iter_content(chunk_size=10_000):
                file.write(chunk)
        print("successful retrival")

    def get_cities_data(self):
        """Réccupération des données sur les communes"""
        print("start of the data retrival")
        response = requests.get('https://static.data.gouv.fr/resources/communes-et-villes-de-france-en-csv-excel-json-parquet-et-feather/20250221-162232/communes-france-2025.csv', stream=True)
        with open(f'{self.output_path}/communes_france.csv', 'wb') as file:
            for chunk in response.iter_content(chunk_size=10_000):
                file.write(chunk)
        print("successful retrival")

    def merging_and_to_parquet(self):
        df = pd.read_csv(f'{self.output_path}/immo_entries_2024.txt.zip', nrows=200_000, on_bad_lines='skip', low_memory=False, sep='|', decimal=',', dtype={'Code postal':str, 'Valeur fonciere':np.float64})
        # Création du code INSEE
        df['Code INSEE'] = (
            df['Code departement'].astype(str).str.zfill(2) + 
            df['Code commune'].astype(str).str.zfill(3)
        )
        # chargement communes
        df2 = pd.read_csv(f'{self.output_path}/communes_france.csv', on_bad_lines='skip', low_memory=False)
        df2 = df2[['code_insee','population','superficie_hectare','densite','altitude_moyenne','altitude_minimale','altitude_maximale','latitude_mairie','longitude_mairie','latitude_centre','longitude_centre']]
        # merge
        df_merged = pd.merge(
            df, df2,
            left_on='Code INSEE',
            right_on='code_insee',
            how='left'   # ou 'inner' selon ton besoin
        )
        df_merged.to_csv(f'{self.output_path}/all_immo_entries.csv')
        df = pd.read_csv(f'{self.output_path}/all_immo_entries.csv', low_memory=False)
        # creation d'un perimètre spécifique
        df_perimeter = df[df['Code departement'] == 1]
        df_perimeter.to_parquet(f'{self.output_path}/all_immo_entries.parquet')

    def preprocessing_pipeline(self):  
        emptyness_infos = []
        df = pd.read_parquet(f'{self.output_path}/all_immo_entries.parquet')
        df = df.drop_duplicates()
        df = df.drop(columns=['Unnamed: 0','No voie','No disposition','Surface reelle bati','code_insee','Code postal','Code departement','Code commune'])

        # nombre total de lignes
        total_rows = df.shape[0] 
        # liste des colonnes
        columns = df.columns.tolist()

        # pour chaque colones calcul du pourcentage de vide
        for column in columns: 
            column_emptyness = df[df[column].isna()].shape[0] #nombre total de lignes vide dans la colone
            column_emptyness_rate = column_emptyness / total_rows * 100

            info = {
                'name': column,
                'pourcentage_vide' : column_emptyness_rate
            }

            emptyness_infos.append(info)

                
        df_emptyness =  pd.DataFrame(emptyness_infos)


        rempli = []
        completement_vide = []
        assez_rempli = []

        for index, row in enumerate(df_emptyness.iterrows()):
            current_column = df_emptyness.iloc[index]
            # si pourcentage de vide superieur a 96% ajout a la liste 'trop vide'
            if current_column['pourcentage_vide'] <= 96:
                rempli.append(current_column['name'])

            # si pourcentage de vide egal à 100% ajout a la liste 'completement vide'
            if current_column['pourcentage_vide'] == 100 :
                completement_vide.append(current_column['name'])
            


        print(len(assez_rempli))

        df[rempli].to_parquet(f'{self.output_path}/all_immo_no_empty.parquet')



        df = pd.read_parquet(f'{self.output_path}/all_immo_no_empty.parquet')


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

        # Replace Nan or None with 0

        df_no_nan = df.fillna(value=-999)


        # drop all objects (not very pertinant insights)
        df_final = df_no_nan.drop(columns=objects)

        # drop the remaining useless columns
        # df_final = df_final.drop(columns=['Unnamed: 0','No voie','Prefixe de section','No disposition','Type local','Surface reelle bati'])

        # 
        df_final.to_parquet(f'{self.output_path}/features_immo_data.parquet')

    def model_training_pipeline(self):
        df = pd.read_parquet(f'{self.output_path}/features_immo_data.parquet')
        correlations = df.corr(method="spearman")['Valeur fonciere']
        correlations_sorted = correlations.abs().sort_values(ascending=False)
        selected_features = correlations[abs(correlations) >=0.1]
        print(selected_features)
        features_cols_list = selected_features.index.tolist()
        print(features_cols_list)
                
        # Sélection de colonnes
        df_features = df[features_cols_list].drop(columns=['Valeur fonciere'])
        # # Initialisation du scaler
        # scaler = StandardScaler()
        # # Entraînement + transformation sur les features
        # features_scaled = scaler.fit_transform(df_features)
        # # Conversion en DataFrame pour garder les noms de colonnes
        # features_scaled = pd.DataFrame(features_scaled, columns=df_features.columns)




        df_target = df['Valeur fonciere']


        # Séparation train/test
        X_train, X_test, y_train, y_test = train_test_split(df_features, df_target, test_size=0.2, random_state=42)
        background = X_train.sample(200, random_state=42)
        joblib.dump(background, f"{self.artefact_path}/shap_background.pkl")
        # Modèle
        model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)



        # Évaluation
        y_pred = model.predict(X_test)

        # --- 8. Calcul des métriques ---
        rmse = root_mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        joblib.dump(model, f"{self.artefact_path}/model.pkl")

        # --- 9. Affichage des résultats ---
        print("📊 Évaluation du modèle :")
        print(f"R² (coefficient de détermination) : {r2:.4f}")
        print(f"RMSE (Mean Squared Error) : {rmse:.2f}")
        print(f"MAE (Mean Absolute Error) : {mae:.2f}")

        

    def root_mean_squared_error(y_true, y_pred):
        return np.sqrt(((y_true - y_pred) ** 2).mean())

    def model_training_pipeline2(self):
        # --- Chargement des données ---
        df = pd.read_parquet(f'{self.output_path}/features_immo_data.parquet')

        # --- Sélection des features ---
        correlations = df.corr(method="spearman")['Valeur fonciere']
        selected_features = correlations[abs(correlations) >= 0.1]
        features_cols_list = selected_features.index.tolist()
        df_features = df[features_cols_list].drop(columns=['Valeur fonciere'])
        df_target = df['Valeur fonciere']

        # --- Split ---
        X_train, X_test, y_train, y_test = train_test_split(df_features, df_target, test_size=0.2, random_state=42)
        background = X_train.sample(200, random_state=42)
        joblib.dump(background, f"{self.artefact_path}/shap_background.pkl")
        # --- Hyperparamètres ---
        params = {
            "n_estimators": 200,
            "random_state": 42,
            "n_jobs": -1
        }

        # --- Config MLflow ---
        
        
        mlflow.set_tracking_uri('https://mlflow.datalab.centreia.fr/')
        mlflow.set_experiment("immo_group1")

        with mlflow.start_run():
            # Log des paramètres
            mlflow.log_params(params)

            # Entraînement
            model = RandomForestRegressor(**params)
            model.fit(X_train, y_train)

            # Prédiction et métriques
            y_pred = model.predict(X_test)
            rmse = root_mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            # Log des métriques
            mlflow.log_metric("rmse", float(rmse))
            mlflow.log_metric("mae", float(mae))
            mlflow.log_metric("r2", float(r2))

            # Log du modèle (sklearn)
            # mlflow.sklearn.log_model(model, name="model_immo_v2")
            joblib.dump(model, f"{self.artefact_path}/model.pkl")
            

            # Affichage console
            print("📊 Évaluation du modèle :")
            print(f"R² : {r2:.4f}")
            print(f"RMSE : {rmse:.2f}")
            self.mrse = rmse
            print(self.mrse)
            print(f"MAE : {mae:.2f}")

    def make_prediction(self, raw_inputs):
        model = joblib.load(f"{self.artefact_path}/model.pkl")
        inputs = pd.DataFrame(raw_inputs)
        predicted_price = model.predict(inputs)[0]

        mlflow.set_tracking_uri("https://mlflow.datalab.centreia.fr/")
        exp = mlflow.get_experiment_by_name("immo_group1")

        runs = mlflow.search_runs([exp.experiment_id], order_by=["start_time DESC"], max_results=1)
        rmse = float(runs.loc[0, "metrics.rmse"])
        print(rmse)
        confidence = max(0, 1-(rmse / predicted_price))
        confidence_score = round(confidence * 100, 2)
       

        return predicted_price, confidence_score
    
        background = joblib.load(f"{self.artefact_path}/shap_background.pkl")
        explainer = shap.Explainer(model, background)

        shap_values = explainer(inputs)
        

        plt.figure(figsize=(15, 6))  # plus large
        shap.plots.waterfall(shap_values[0], show=False)

        plt.gcf().subplots_adjust(left=0.50)  # + d'espace à gauche (ajuste 0.25 -> 0.45)
        plt.show()

        # shap.plots.bar(shap_values)
