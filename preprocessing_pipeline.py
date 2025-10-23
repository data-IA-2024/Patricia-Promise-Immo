import pandas as pd






# Réccupération d'uniquement les collones remplies

emptyness_infos = []
df = pd.read_parquet('outputs/all_immo_entries.parquet')
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
    if current_column['pourcentage_vide'] == 0:
        rempli.append(current_column['name'])

    # si pourcentage de vide egal à 100% ajout a la liste 'completement vide'
    if current_column['pourcentage_vide'] == 100 :
        completement_vide.append(current_column['name'])
    
    if current_column['pourcentage_vide'] < 100 :
        assez_rempli.append(current_column['name'])




print(len(assez_rempli))

df[assez_rempli].to_parquet('outputs/all_immo_no_empty.parquet')








df = pd.read_parquet('outputs/all_immo_no_empty.parquet')


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

df_no_nan = df.fillna(value=0)


# drop all objects (not very pertinant insights)
df_final = df_no_nan.drop(columns=objects)

# drop the remaining useless columns
df_final = df_final.drop(columns=['Unnamed: 0','No voie','Prefixe de section','No disposition','Type local','Surface reelle bati'])

# 
df_final.to_parquet('outputs/features_immo_data.parquet')




