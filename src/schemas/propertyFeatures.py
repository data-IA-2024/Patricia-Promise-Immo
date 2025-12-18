from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class PropertyTypeEnum(str,Enum):
    """Enumération des types de biens immobiliers"""
    Maison = "1"
    Appartement = "2"


class PropertyPriceRequest(BaseModel):
    nombre_de_lots: int = Field(description="Nombre de lots du bien ommobilier. Ex: 1 pour un lot unique")
    code_type_local: PropertyTypeEnum= Field(description="Code correspondant au type de bien immobilier. Ex: 1 pour maison, 2 pour appartement")
    nombre_pieces_principales: int = Field(description="Nombre de pièce contenant le bien immobilier")
    surface_terrain: Optional[float] = Field(description="Surface du terrain du bien immobilier")
    population: int = Field(description="Population de la commune où se situe le bien immobilier")
    densite: float = Field(description="Valeur foncière du bien immobilier")

class PropertyPriceResponse(BaseModel):
    pricePrediction: float = Field(description="Prix prédit du bien immobilier")
    currency: str = "EUR"
    confidence_score: Optional[float] = None
