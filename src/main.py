from fastapi import FastAPI
from schemas.propertyFeatures import PropertyPriceRequest, PropertyPriceResponse
#from artefacts.models import model

# Create FastAPI instance
app = FastAPI(title="Patricia Promise Immo API", version="1.0",
              description="API pour la prédiction du prix des biens immobiliers.")

# Define a home page route
@app.get("/", tags=["Page d'accueil"])
def home_page():
    return {"Message" : "Welcome to Patricia Promise Immo API!"}


@app.post("/predict", tags=["Prédiction du prix immobilier"])
def priceImmoPrediction(inputForModel:PropertyPriceRequest, include_confidence_score: bool = True):
    features = [inputForModel.nombre_de_lots,
                inputForModel.code_type_local,
                inputForModel.nombre_pieces_principales,
                inputForModel.surface_terrain,
                inputForModel.population,
                inputForModel.densite
    ]
   
    pricePrédiction =  0 #model.predict([features])[0]

    if include_confidence_score:
        confidence_score = 0 #model.predict_proba([features])[0].max()

    return {"Prediction": pricePrédiction,
            "currency": "EUR",
            "confidence_score": confidence_score}

