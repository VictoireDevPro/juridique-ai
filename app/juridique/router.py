from fastapi import APIRouter, File, Form, HTTPException, Depends, UploadFile
from app.juridique.ingestion import DATA_DIR, load_document, get_text_splitter 
from app.juridique.memory import build_rag_chain_avec_memoire, get_session_history
from app.juridique.rag import build_contrat_chain, build_contrat_chain_structure, generate_clauses_base_on_existing
from app.juridique.schemas import (
  AnalyseContrat, DocumentIndexeResponse, DocumentInfo, QuestionRequest, QuestionResponse,
  ContratRequest, ContratResponse, SessionResponse
)
from app.auth.dependencies import get_current_user
from app.auth.models import User
from fastapi.responses import StreamingResponse
from pathlib import Path
from app.juridique.vectorstore import index_documents, list_documents_indexes


router = APIRouter( prefix="/juridique", tags=["juridique"])


rag_chain = build_rag_chain_avec_memoire()
contrat_chain = build_contrat_chain()
contrat_chain_structure = build_contrat_chain_structure()
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


@router.post("/contrat/structure", response_model=AnalyseContrat)
async def analyser_contrat_structure(body: ContratRequest, current_user: User = Depends(get_current_user)):
    """
    Comme /contrat, mais retourne une analyse structurée en JSON typé.
    """
    try:
        return contrat_chain_structure.invoke({"contrat": body.contrat})

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse structurée du contrat : {str(e)}"
        )


@router.post("/admin/document", response_model=DocumentIndexeResponse)
async def ajouter_document(
    fichier: UploadFile = File(),
    categorie: str = Form("OHADA"),
    current_user: User = Depends(get_current_user)
):
    """
    Upload un document (PDF ou TXT), l'indexe immédiatement dans Qdrant.
    """

    extension = Path(fichier.filename).suffix.lower()
    if extension not in [".pdf", ".txt"]:
        raise HTTPException(status_code=400, detail="Seuls les fichiers .pdf et .txt sont acceptés")

    try:
        build_path = DATA_DIR / Path(fichier.filename)
        content  = await fichier.read()

        #write on the disk in binary mode "wb"
        with open(build_path, "wb") as f:
            f.write(content)

        document_loaded = load_document(str(build_path))
        for doc in document_loaded:
            doc.metadata["categorie"] = categorie
        documents_chunks = get_text_splitter().split_documents(document_loaded)
        index_documents(documents_chunks)

        return DocumentIndexeResponse(
            nom_fichier=fichier.filename,
            categorie=categorie,
            nombre_chunks=len(documents_chunks)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'ajout du document : {str(e)}"
        )


@router.get("/admin/documents", response_model=list[DocumentInfo])
async def lister_documents(current_user: User = Depends(get_current_user)):
    """Liste les documents indexés dans Qdrant avec leur nombre de chunks."""
    return list_documents_indexes()