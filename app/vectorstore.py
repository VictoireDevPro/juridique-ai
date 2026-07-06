from dotenv import load_dotenv
load_dotenv()


# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


QDRANT_PATH = "./qdrant_storage"
COLLECTION_NAME = "base_juridique"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2" 
# EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2" 

def get_embeddings():
  """
  Modèle multilingue - supporte très bien le français juridique.
  Se télécharger automatiquement au premier appel (120MB).
  """

  return HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
  )

_qdrant_client: QdrantClient | None = None

def get_qdrant_client() -> QdrantClient:
  """Retourne un client Qdrant connecté au stockage local (singleton)."""
  global _qdrant_client
  if _qdrant_client is None:
    _qdrant_client = QdrantClient(path=QDRANT_PATH)
  # return _qdrant_client local pour tests, sinon client distant pour production
  return QdrantClient(host="localhost", port=6333) # QdrantClient(path=QDRANT_PATH)

def init_collection(client: QdrantClient):
  """
  Crée la collection Qdrant si elle n'existe pas encore.
  Dimension 384 = taille des vecteurs du modèle MiniLM.
  """
  collections = [c.name for c in client.get_collections().collections]

  if COLLECTION_NAME not in collections:
    client.create_collection(
      collection_name=COLLECTION_NAME,
      vectors_config=VectorParams(
        size=384, # dimension du modèle MiniLM
        distance=Distance.COSINE # similarité cosinus = standard pour texte
      )
    )
    print(f"✅ Collection '{COLLECTION_NAME}' créée dans Qdrant.")
  else:
    print(f"ℹ️ Collection '{COLLECTION_NAME}' existe déjà dans Qdrant.")


def index_documents(chunks: list) -> QdrantVectorStore:
  """
  Prend les chunks du Module 3 et les indexe dans Qdrant.
  Retourne le vectorstore prêt à être utilisé comme retriever.
  """
  print(f"🔍 Indexation de {len(chunks)} chunks en cours...")

  embeddings = get_embeddings()
  client = get_qdrant_client()
  init_collection(client)

  vectorstore = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
  )
  vectorstore.add_documents(chunks)
  print(f"✅ {len(chunks)} chunks indexés dans Qdrant", )
  return vectorstore

def load_vectorstore() -> QdrantVectorStore:
  """
  Charge le vectorstore depuis le disque sans ré-indexer.
  À utiliser après la première indexation.
  """
  embeddings = get_embeddings()
  client = get_qdrant_client()

  vectorstore = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
  )
  print(f"✅ Vectorstore chargé depuis {QDRANT_PATH} avec collection '{COLLECTION_NAME}'")
  return vectorstore

def search(query: str, k: int = 4) -> list:
  """
  Recherche les k chunks les plus proches sémantiquement de la query.
  """
  vectorstore = load_vectorstore()
  results = vectorstore.similarity_search(query, k=k)
  print(f"🔎 Recherche pour : '{query}'")
  return results