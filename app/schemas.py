from pydantic import BaseModel, Field

class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=5, 
        description="La question juridique à poser"
    )
    session_id: str = Field(
        default="default",
        description="Identifiant de session pour la mémoire conversationnelle"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "Quelles sont les conditions de validité d'un contrat ?",
                "session_id": "user123"
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

class SessionRequest(BaseModel):
    session_id: str = Field(
        ...,
        description="Identifiant de session à effacer"
    )

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