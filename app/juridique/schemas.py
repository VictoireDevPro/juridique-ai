from pydantic import BaseModel, Field

class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=5,
        description="La question juridique à poser"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "Quelles sont les conditions de validité d'un contrat ?"
            }
        }
    }


class ContratRequest(BaseModel):
    contrat: str = Field(
        ...,
        min_length=50,
        description="Le texte du contrat à analyser"
    )

    model_config = {
        "json_schema_extra":{
            "example": {
                "contrat": "CONTRAT DE VENTE\nEntre M. Dupont..."
            }
        }
    }

class QuestionResponse(BaseModel):
    reponse: str
    session_id: str
    statut: str = "succes"


class ContratResponse(BaseModel):
    analyse: str
    statut: str = "succes"


class SessionResponse(BaseModel):
    message: str
    session_id: str


class HealthResponse(BaseModel):
    statut: str
    version: str
    services: dict