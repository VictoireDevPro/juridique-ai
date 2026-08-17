from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.llm import get_llm
from app.prompts import prompt_rag_avec_memoire, prompt_reformulation
from app.vectorstore import get_retriever, load_vectorstore
from app.rag import format_docs

# ── Store des sessions ────────────────────────────────────────────────
# En production ce serait Redis ou PostgreSQL
# Pour le dev un dict en mémoire suffit
store: dict[str, ChatMessageHistory] = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    """
    Retourne l'historique d'une session.
    Crée la session si elle n'existe pas encore.
    """
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
        print(f"🆕 Nouvelle session créée : {session_id}")
    return store[session_id]

# ── Chain de reformulation ────────────────────────────────────────────
def build_reformulation_chain():
    """
    Reformule la question en tenant compte de l'historique.

    Exemple :
      Historique : "On parlait des conditions de validité"
      Question   : "Et si l'une manque ?"
      Reformulée : "Que se passe-t-il si une condition de validité d'un contrat manque ?"
    """
    llm = get_llm()
    return prompt_reformulation | llm | StrOutputParser()

# ── Chain RAG avec mémoire ────────────────────────────────────────────
def build_rag_chain_avec_memoire():
    """
    Pipeline RAG complet avec mémoire conversationnelle.

    Flux :
    question
        │
        ▼
    reformulation (tient compte de l'historique)
        │
        ▼
    retriever (cherche dans Qdrant)
        │
        ▼
    prompt_rag_avec_memoire (system + historique + contexte + question)
        │
        ▼
    llm → réponse
    """
    llm = get_llm()
    retriever = get_retriever(k=4)
    reformulation_chain = build_reformulation_chain()

    # ── Étape 1 : reformuler la question ──────────────────────────────
    def reformuler_et_chercher(input_dict: dict) -> dict:
        """Reformule la question puis cherche dans Qdrant."""
        question_reformulee = reformulation_chain.invoke({
            "chat_history": input_dict.get("chat_history", []),
            "question": input_dict["question"]
        })

        print(f"\n🔄 Question reformulée : {question_reformulee}")

        docs = retriever.invoke(question_reformulee)
        context = format_docs(docs)

        return {
            "context": context,
            "question": input_dict["question"],  # question originale pour la réponse
            "chat_history": input_dict.get("chat_history", [])
        }

    # ── Chain finale ──────────────────────────────────────────────────
    chain = (
        RunnablePassthrough.assign(
            chat_history=lambda x: x.get("chat_history", [])
        )
        | reformuler_et_chercher
        | prompt_rag_avec_memoire
        | llm
        | StrOutputParser()
    )

    # ── Envelopper avec la gestion de l'historique ────────────────────
    chain_avec_memoire = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history"
    )

    return chain_avec_memoire

def training_memory():
    chain = build_rag_chain_avec_memoire()

    session_id = "training_session"

    config = {
        "configurable": {
            "session_id": session_id
        }
    }

    print("=" * 60)
    print("🧠 ENTRAÎNEMENT — RAG + MÉMOIRE")
    print("=" * 60)
    print("Tape 'quit' pour arrêter.\n")

    while True:
        question = input("👤 Toi : ")

        if question.lower() == "quit":
            break

        response = chain.invoke(
            {"question": question},
            config=config
        )

        print(f"\n🤖 Assistant :\n{response}\n")

if __name__ == "__main__":
    training_memory()


    