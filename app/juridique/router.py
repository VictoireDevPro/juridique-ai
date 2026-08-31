from fastapi import APIRouter, HTTPException, Depends
from app.juridique.memory import build_rag_chain_avec_memoire, get_session_history
from app.juridique.rag import build_contrat_chain, generate_clauses_base_on_existing
from app.juridique.schemas import (
  QuestionRequest, QuestionResponse,
  ContratRequest, ContratResponse, SessionResponse
)
from app.auth.dependencies import get_current_user
from app.auth.models import User
from fastapi.responses import StreamingResponse


router = APIRouter( prefix="/juridique", tags=["juridique"])


rag_chain = build_rag_chain_avec_memoire()
contrat_chain = build_contrat_chain()
generer_clauses = generate_clauses_base_on_existing()


@router.post("/question", response_model=QuestionResponse)
async def poser_question(body: QuestionRequest, current_user: User = Depends(get_current_user)):
    """
    Pose une question juridique à l'assistant RAG.
    L'historique de conversation est maintenu par utilisateur authentifié.
    """
    try:
        session_id = str(current_user.id)
        config_session = {"configurable": {"session_id": session_id}}
        response = rag_chain.invoke(
            {"question": body.question, "source": body.source},
            config=config_session
        )

        return QuestionResponse(
            reponse=response,
            session_id=session_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement de la question : {str(e)}"
        )


@router.post("/contrat", response_model=ContratResponse)
async def analyser_contrat(body: ContratRequest, current_user: User = Depends(get_current_user)):
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
async def generer_clauses_endpoint(body: ContratRequest, current_user: User = Depends(get_current_user)):
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
async def effacer_session(current_user: User = Depends(get_current_user)):
    """
    Efface l'historique de la session conversationnelle de l'utilisateur authentifié.
    """
    session_id = str(current_user.id)
    get_session_history(session_id).clear()

    return SessionResponse(
        message="Session effacée avec succès",
        session_id=session_id
    )


@router.get("/session/historique")
async def voir_historique(current_user: User = Depends(get_current_user)):
    """
    Retourne l'historique de la session de l'utilisateur authentifié.
    Utile pour déboguer ou afficher la conversation côté client.
    """
    session_id = str(current_user.id)
    historique = get_session_history(session_id)

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

@router.post("/questions/stream")
async def poser_question_stream(body: QuestionRequest, current_user: User = Depends(get_current_user)):
        """
        Comme /question, mais streame la réponse token par token.
        """
        session_id = str(current_user.id)
        config_session = { "configurable": { "session_id": session_id }}
        
        async def generer_tokens():
            async for chunk in rag_chain.astream(
                { "question": body.question, "source": body.source },
                config=config_session
            ):
                yield chunk
        return StreamingResponse(generer_tokens(), media_type="text/plain")
