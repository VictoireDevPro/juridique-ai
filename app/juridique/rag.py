from app.juridique.ingestion import load_and_split_base_juridique
from app.juridique.llm import get_llm
from langchain_core.output_parsers import StrOutputParser
from app.juridique.prompts import prompt_question, prompt_analyse_contrat, prompt_generate_clauses
from app.juridique.vectorstore import get_retriever, index_documents
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter


# ── Formater les documents récupérés en texte lisible ─────────────────

def format_docs(docs: list) -> str:
  """
  Transforme la liste de Documents en texte structuré
  pour l'injecter dans le prompt.
  """
  result = []

  for i, doc in enumerate(docs):
    source = doc.metadata.get("source", "source inconnue")
    categorie = doc.metadata.get("categorie", "")
    result.append(
        f"[Source {i+1} — {categorie} — {source}]\n{doc.page_content}"
    )

  print(f"🔗 {len(docs)} documents formatés pour le prompt +++++=> ${"\n\n---\n\n".join(result)}")
  return "\n\n---\n\n".join(result)


# ── Chain RAG pour les questions juridiques ───────────────────────────
def build_rag_chain():
    """
    Construit le pipeline RAG complet :
    question → retriever → format → prompt → llm → string
    """
    llm = get_llm()
    retriever = get_retriever(k=4)

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt_question
        | llm
        | StrOutputParser()
    )

    return chain

# ── Chain pour analyse de contrat ─────────────────────────────────────
def build_contrat_chain():
    """
    Pipeline pour analyser un contrat soumis.
    Pas de retriever ici — le contrat est directement dans le prompt.
    Pour la V2 on ajoutera le retriever pour croiser avec la base juridique.
    """
    llm = get_llm()

    chain = prompt_analyse_contrat | llm | StrOutputParser()

    return chain

def generate_clauses_base_on_existing():
    """
    Pipeline pour générer des clauses à partir d'un contrat existant.
    Pas de retriever ici — le contrat est directement dans le prompt.
    Pour la V2 on ajoutera le retriever pour croiser avec la base juridique.
    """
    llm = get_llm()
    retriever = get_retriever(k=1)
    chain = (
        {
            "context": itemgetter("demande") | retriever | format_docs,
            "demande": itemgetter("demande")
        }
        | prompt_generate_clauses
        | llm
        | StrOutputParser()
    )

    return chain

# ── Initialiser la base juridique (premier lancement) ─────────────────
def init_base_juridique():
    """
    À appeler une seule fois pour indexer les documents.
    Les lancements suivants utilisent load_vectorstore() directement.
    """
    print("🔄 Initialisation de la base juridique...")
    chunks = load_and_split_base_juridique()
    index_documents(chunks)
    print("✅ Base juridique prête")