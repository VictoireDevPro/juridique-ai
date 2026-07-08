from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.vectorstore import load_vectorstore


DATA_DIR = Path("data/juridique")

def load_pdf(filepath: str) -> list:
    """Charge un fichier PDF et retourne une liste de Documents."""
    loader = PyPDFLoader(filepath)
    documents = loader.load()
    print(f"✅ PDF chargé : {len(documents)} pages — {filepath}")
    return documents

def load_txt(filepath: str) -> list:
    """Charge un fichier TXT et retourne une liste de Documents."""
    loader = TextLoader(filepath, encoding="utf-8")
    # print(f" ============== loader {loader}")
    documents = loader.load()
    print(f"✅ TXT chargé : {len(documents)} documents — {filepath}")
    # print(f" +++++++++++++++++++++Document loaded: {documents}")
    return documents

def load_directory(directory: str, extension: str = ".txt") -> list:
    """Charge tous les fichiers d'un répertoire avec une extension donnée."""
    loader = DirectoryLoader(
        directory,
        glob=f"**/*{extension}",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True
    )
    documents = loader.load()
    print(f"✅ Total documents chargés : {len(documents)} depuis {directory}")
    return documents

def load_base_juridique() -> list:
    """Charge tous les textes juridiques OHADA + Congo."""
    all_documents = []

    # Charger OHADA
    ohada_dir = DATA_DIR / "ohada"
    if ohada_dir.exists():
        docs_ohada = load_directory(str(ohada_dir))
        # Ajouter metadata source
        for doc in docs_ohada:
            doc.metadata["categorie"] = "OHADA"
        all_documents.extend(docs_ohada)

    # Charger législation Congo
    congo_dir = DATA_DIR / "congo"
    if congo_dir.exists():
        docs_congo = load_directory(str(congo_dir))
        for doc in docs_congo:
            doc.metadata["categorie"] = "Congo"
        all_documents.extend(docs_congo)

    print(f"\n📚 Base juridique totale : {len(all_documents)} documents")
    return all_documents


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """j
    RecursiveCharacterTextSplitter essaie de couper dans cet ordre :
    1. Double saut de ligne (entre paragraphes)
    2. Saut de ligne simple
    3. Point
    4. Espace
    → Idéal pour les textes de loi structurés en articles
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "],
        length_function=len
    )

def load_and_split_base_juridique() -> list:
  """Pipeline complet : charge et découpe tous les textes juridiques."""
  documents = load_base_juridique()
  splitter = get_text_splitter()
  chunks = splitter.split_documents(documents)

  print(f"✂️  Découpage : {len(documents)} documents → {len(chunks)} chunks")
  return chunks