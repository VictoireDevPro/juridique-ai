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

_embeddings: HuggingFaceEmbeddings | None = None

def get_embeddings():
  """
  Modèle multilingue - supporte très bien le français juridique.
  Se télécharger automatiquement au premier appel (120MB).
  charge en local (CPU) le modèle paraphrase-multilingual-MiniLM-L12-v2, qui transforme n'importe quel texte en un vecteur de 384 nombres décimaux (un point dans un espace à 384 dimensions). Deux textes proches en sens auront des vecteurs proches dans cet espace.
  Mis en cache (singleton) pour ne charger les poids qu'une seule fois par process.
  """
  global _embeddings
  if _embeddings is None:
    _embeddings = HuggingFaceEmbeddings(
      model_name=EMBEDDING_MODEL,
      model_kwargs={"device": "cpu"},
      encode_kwargs={"normalize_embeddings": True}
    )
  return _embeddings

_qdrant_client: QdrantClient | None = None

def get_qdrant_client() -> QdrantClient:
  """Retourne le client Qdrant connecté au serveur Docker (singleton, réutilisé entre les appels)."""
  global _qdrant_client
  if _qdrant_client is None:
    _qdrant_client = QdrantClient(host="localhost", port=6333)
  return _qdrant_client

def reset_collection(client: QdrantClient):
  """
  Supprime la collection si elle existe, pour repartir d'une base propre.
  Utile en dev/test pour éviter d'accumuler des points dupliqués à chaque ré-indexation.
  """
  collections = [c.name for c in client.get_collections().collections]

  if COLLECTION_NAME in collections:
    client.delete_collection(COLLECTION_NAME)
    print(f"🗑️  Collection '{COLLECTION_NAME}' supprimée.")

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
  Charge le vectorstore depuis qdrant sans ré-indexer.
  À utiliser après la première indexation.
  """
  embeddings = get_embeddings()
  client = get_qdrant_client()

  vectorstore = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
  )
  print(f"✅ Vectorstore chargé avec collection '{COLLECTION_NAME}'")
  return vectorstore

def search(query: str, k: int = 4) -> list:
  """
  Recherche les k chunks les plus proches sémantiquement de la query.
  Retourne une liste de tuples (Document, score) — score = similarité cosinus (0 à 1, plus haut = plus proche).
  """
  vectorstore = load_vectorstore()
  results = vectorstore.similarity_search_with_score(query, k=k)
  print(f"🔎 Recherche pour : '{query}'")
  return results


def get_retriever(k: int = 4):
    """
    Retourne un retriever prêt à être branché dans une chain LCEL.
    k = nombre de chunks retournés par recherche
    """
    vectorestore = load_vectorstore()

    retriever = vectorestore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )
    
    print(f"✅ Retriever prêt — top {k} résultats par recherche")
    return retriever