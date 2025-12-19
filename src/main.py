from fastapi import FastAPI, Request
from .schemas.propertyFeatures import PropertyPriceRequest, PropertyPriceResponse
from fastapi.templating import Jinja2Templates 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from prometheus_fastapi_instrumentator import Instrumentator
from scripts import immo_data

#from artefacts.models import model

# Define base directory
base_dir = Path(__file__).resolve().parent  # Path to the directory containing main.py (Patricia-promise-immo/src/main.py)
print(base_dir)
root_dir = base_dir.parent  # Path to the root directory (Patricia-promise-immo/)
print(root_dir)

# Initialize ImmoData instance
immo_data_ = immo_data.ImmoData(output_path =str(root_dir/"data"), artefact_path=str(root_dir/"artefacts"))

# Create FastAPI instance
app = FastAPI(title="Patricia Promise Immo API", version="1.0",
              description="API pour la prédiction du prix des biens immobiliers.")

# Set up prometheus intrumentor
Instrumentator().instrument(app).expose(app)

# Mount static files
app.mount("/static", 
          StaticFiles(directory=str(root_dir/"static")), 
          name="static"
)

# Set up Jinja2 templates
template = Jinja2Templates(directory=str(root_dir/"templates"))

# Define a home page route
@app.get("/", response_class=HTMLResponse, tags=["Formulaire de prédiction"])
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

    house = [{
    'Nombre de lots': inputForModel.nombre_de_lots, 
    'Code type local': inputForModel.code_type_local,
    'Nombre pieces principales': inputForModel.nombre_pieces_principales, 
    'Surface terrain': inputForModel.surface_terrain,
    'population': inputForModel.population, 
    'densite': inputForModel.densite
    }]

   
    pricePrediction, confidence_score =  immo_data_.make_prediction(house)


    response_predict = PropertyPriceResponse(
        pricePrediction = pricePrediction,
        currency="EUR",
        confidence_score= confidence_score
    )

    if include_confidence_score:
        confidence_score = confidence_score

    return template.TemplateResponse(
        "reponsePredict.html",
        {"request": request,  "pricePrediction": round(pricePrediction,2), "confidence_score" : confidence_score}
    )

@app.get("/health", tags=["Health Check"])
def health_check():
    """Endpoint pour vérifier la santé de l'API."""
    return {"status": "ok", "message": "L'API fonctionne correctement."}
