from fastapi import FastAPI, Request
from schemas.propertyFeatures import PropertyPriceRequest, PropertyPriceResponse
from fastapi.templating import Jinja2Templates 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

#from artefacts.models import model

# Create FastAPI instance
app = FastAPI(title="Patricia Promise Immo API", version="1.0",
              description="API pour la prédiction du prix des biens immobiliers.")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
template = Jinja2Templates(directory="templates")

# Define a home page route
@app.get("/", response_class=HTMLResponse, tags=["Page d'accueil"])
def formPageToPredict(request: Request):
    return template.TemplateResponse("index.html", {"request" : request})
                                     

@app.post("/predict", tags=["Prédiction du prix immobilier"])
def priceImmoPrediction(request:Request, inputForModel:PropertyPriceRequest, include_confidence_score: bool = True):
    """Endpoint pour prédire le prix d'un bien immobilier en fonction de ses caractéristiques."""

    confidence_score = None

    features = [inputForModel.nombre_de_lots,
                inputForModel.code_type_local,
                inputForModel.nombre_pieces_principales,
                inputForModel.surface_terrain,
                inputForModel.population,
                inputForModel.densite
    ]
   
    pricePrédiction =  0 #model.predict([features])[0]

    response_predict = PropertyPriceResponse(
        pricePrediction=pricePrédiction,
        currency="EUR",
        confidence_score= confidence_score
    )

    if include_confidence_score:
        confidence_score = 0 #model.predict_proba([features])[0].max()

    return template.TemplateResponse(
        "reponsePredict.html",
        {"request": request, "response_predict": response_predict}
    )


