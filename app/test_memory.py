from app.memory import build_rag_chain_avec_memoire, get_session_history

chain = build_rag_chain_avec_memoire()

# Config de session — chaque utilisateur a son propre historique
config_session = {"configurable": {"session_id": "session_test_001"}}

print("=" * 50)
print("SESSION JURIDIQUE — Conversation continue")
print("=" * 50)

# ── Tour 1 ────────────────────────────────────────────────────────────
print("\n👤 Question 1 : conditions de validité d'un contrat ?")
print("-" * 40)
reponse_1 = chain.invoke(
    {"question": "Quelles sont les conditions de validité d'un contrat ?"},
    config=config_session
)
print(reponse_1)

# ── Tour 2 : question qui dépend du tour 1 ────────────────────────────
print("\n👤 Question 2 : Et si l'une de ces conditions manque ?")
print("-" * 40)
reponse_2 = chain.invoke(
    {"question": "Et si l'une de ces conditions manque ?"},
    config=config_session
)
print(reponse_2)

# ── Tour 3 : encore plus contextuel ───────────────────────────────────
print("\n👤 Question 3 : Donne moi un exemple concret")
print("-" * 40)
reponse_3 = chain.invoke(
    {"question": "Donne moi un exemple concret pour le Congo"},
    config=config_session
)
print(reponse_3)

# ── Inspecter l'historique ────────────────────────────────────────────
print("\n" + "=" * 50)
print("HISTORIQUE DE LA SESSION")
print("=" * 50)

historique = get_session_history("session_test_001")
for msg in historique.messages:
    role = "👤 Humain" if msg.type == "human" else "🤖 Assistant"
    print(f"\n{role} :")
    print(msg.content[:200])