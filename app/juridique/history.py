from typing import List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.core.postgres import SessionLocal
from app.juridique.models import ChatMessage


class PostgresChatMessageHistory(BaseChatMessageHistory):
    """
    Implémentation de BaseChatMessageHistory adossée à Postgres.
    Chaque instance représente l'historique d'un seul utilisateur (user_id).
    """

    def __init__(self, user_id: int):
        self.user_id = user_id

    @property
    def messages(self) -> List[BaseMessage]:
        """
        TODO : retourner la liste des messages de self.user_id, dans l'ordre
        chronologique (created_at croissant), convertis en objets LangChain
        (HumanMessage si role == "human", AIMessage sinon).

        Étapes :
        1. Ouvrir une session : with SessionLocal() as db:
        2. db.query(ChatMessage).filter(ChatMessage.user_id == self.user_id)
             .order_by(ChatMessage.created_at).all()
        3. Convertir chaque ligne en HumanMessage(content=...) ou AIMessage(content=...)
           selon row.role
        """
        with SessionLocal() as db:
            rows = (
                db.query(ChatMessage)
                .filter(ChatMessage.user_id == self.user_id)
                .order_by(ChatMessage.created_at)
                .all()
            )
            messages = []
            for row in rows:
                if row.role == "human":
                    messages.append(HumanMessage(content=row.content))
                else:
                    messages.append(AIMessage(content=row.content))
            return messages



    def add_message(self, message: BaseMessage) -> None:
        """
        TODO : insérer `message` en base pour self.user_id.

        Étapes :
        1. with SessionLocal() as db:
        2. Créer un ChatMessage(user_id=self.user_id, role=message.type, content=message.content)
        3. db.add(...) puis db.commit()

        Indice : message.type vaut "human" pour HumanMessage, "ai" pour AIMessage —
        c'est directement compatible avec ce qu'on relit dans `messages`.
        """
        with SessionLocal() as db:
            chat_messsage = ChatMessage(
                user_id=self.user_id,
                role=message.type,
                content=message.content
            )
            db.add(chat_messsage)
            db.commit()

    def clear(self) -> None:
        """
        TODO : supprimer tous les messages de self.user_id.

        Étapes :
        1. with SessionLocal() as db:
        2. db.query(ChatMessage).filter(ChatMessage.user_id == self.user_id).delete()
        3. db.commit()
        """
        with SessionLocal() as db:
            db.query(ChatMessage).filter(ChatMessage.user_id == self.user_id).delete()
            db.commit()
