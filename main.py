from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.router import router
from app.schemas import HealthResponse
from app.vectorstore import load_vectorstore, index_documents, get_qdrant_client, COLLECTION_NAME
from app.ingestion import load_and_split_base_juridique


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Vérifie que la base juridique est prête au démarrage.
    Si la collection Qdrant est absente ou vide, on indexe automatiquement.
    """
    print("🚀 Démarrage de l'API Juridique...")

    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]
    collection_vide = (
        COLLECTION_NAME not in collections
        or client.count(COLLECTION_NAME).count == 0
    )

    if collection_vide:
        print("⚠️  Base Qdrant vide — indexation en cours...")
        chunks = load_and_split_base_juridique()
        index_documents(chunks)
    else:
        print("✅ Base Qdrant existante détectée")
        load_vectorstore()

    print("✅ API prête\n")
    yield
    print("🛑 Arrêt de l'API")

app = FastAPI(
  title="Assistant Juridique OHADA",
  description="API d'analyse juridique basée sur le droit OHADA et la législation congolaise",
  version="1.0.0",
  lifespan=lifespan
)

app.include_router(router)


@app.get("/health", response_model=HealthResponse, tags=["Système"])
async def health():
    """Vérifie que l'API et ses services sont opérationnels."""
    return HealthResponse(
        statut="operationnel",
        version="1.0.0",
        services={
            "llm": "Groq — llama-3.3-70b-versatile",
            "vectorstore": "Qdrant local",
            "embeddings": "paraphrase-multilingual-MiniLM-L12-v2"
        }
    )