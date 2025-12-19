
from immo_data import ImmoData

_init = False
_training = True

immo_data_ = ImmoData(output_path='../data', artefact_path='../artefacts')

if _init:
    immo_data_.get_immo_data()
    immo_data_.get_cities_data()
    immo_data_.merging_and_to_parquet()
    immo_data_.preprocessing_pipeline()

if _training:
    immo_data_.model_training_pipeline2()

house = [{
    'Nombre de lots': 1, 
    'Code type local': 1,
    'Nombre pieces principales': 1, 
    'Surface terrain': 20,
    'population': 20000, 
    'densite': 300
}]  
immo_data_.make_prediction(house)
