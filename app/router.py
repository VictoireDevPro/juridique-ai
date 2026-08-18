from fastapi import APIRouter, HTTPException
from app.memory import build_rag_chain_avec_memoire, get_session_history, store
from app.rag import build_contrat_chain, generate_clauses_base_on_existing
from app.schemas import (
  QuestionRequest, QuestionResponse,
  ContratRequest, ContratResponse, SessionRequest, SessionResponse
)

router = APIRouter( prefix="/juridique", tags=["juridique"])


rag_chain = build_rag_chain_avec_memoire()
contrat_chain = build_contrat_chain()
generer_clauses = generate_clauses_base_on_existing()


@router.post("/question", response_model=QuestionResponse)
async def poser_question(body: QuestionRequest):
    """
    Pose une question juridique à l'assistant RAG.
    L'historique de conversation est maintenu par session_id.
    """
    try: 
        config_session = {"configurable": {"session_id": body.session_id}}
        response = rag_chain.invoke(
            {"question": body.question},
            config=config_session
        )

        return QuestionResponse(
            reponse=response,
            session_id=body.session_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement de la question : {str(e)}"
        )


@router.post("/contrat", response_model=ContratResponse)
async def analyser_contrat(body: ContratRequest):
    """
    Analyse un contrat selon le droit OHADA et la législation congolaise.
    """
    try:
        analyse = contrat_chain.invoke({"contrat": body.contrat})

        return ContratResponse(analyse=analyse)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse du contrat : {str(e)}"
        )


@router.post("/generer_clauses", response_model=ContratResponse)
async def generer_clauses_endpoint(body: ContratRequest):
    """
    Génère des clauses à partir d'un contrat existant.
    """
    try:
        clauses = generer_clauses.invoke({"demande": body.contrat})

        return ContratResponse(analyse=clauses)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération des clauses : {str(e)}"
        )


@router.delete("/session", response_model=SessionResponse)
async def effacer_session(body: SessionRequest):
    """
    Efface l'historique d'une session conversationnelle.
    """
    if body.session_id in store:
      del store[body.session_id]
      return SessionResponse(
          message=f"Session effacée avec succès",
          session_id=body.session_id
      )

    return SessionResponse(
        message=f"Session introuvable ou déjà effacée",
        session_id=body.session_id
    )


@router.get("/session/{session_id}/historique")
async def voir_historique(session_id: str):
    """
    Retourne l'historique d'une session.
    Utile pour déboguer ou afficher la conversation côté client.
    """
    historique = get_session_history(session_id)

    print(f"🔍 Historique de la session {session_id} =+===> {historique}")
    messages = []
    for msg in historique.messages:
        messages.append({
            "role": "humain" if msg.type == "human" else "assistant",
            "contenu": msg.content
        })

    return {
        "session_id": session_id,
        "nombre_messages": len(messages),
        "messages": messages
    }