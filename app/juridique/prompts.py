from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ── Prompt système : le "caractère" de ton assistant ──────────────────
SYSTEM_JURIDIQUE = """
Tu es un juriste expert spécialisé dans :
- Le droit OHADA (Organisation pour l'Harmonisation en Afrique du Droit des Affaires)
- La législation de la République du Congo

Tes règles absolues :
1. Tu réponds uniquement sur la base des textes juridiques fournis dans le contexte
2. Si l'information n'est pas dans le contexte, tu dis explicitement "Je ne trouve pas cette information dans les textes fournis"
3. Tu cites toujours l'article ou la source précise de ta réponse
4. Tu réponds en français juridique clair et accessible
5. Tu ne fais jamais de supposition ou d'invention juridique

Format de tes réponses :
- Réponse directe à la question
- Base légale (article, acte uniforme, loi)
- Explication si nécessaire
"""

# ── Prompt pour les questions générales ───────────────────────────────
prompt_question = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_JURIDIQUE),
    ("human", """
CONTEXTE :
{context}

QUESTION :
{question}
""")
])

# ── Prompt pour l'analyse de contrat ──────────────────────────────────
prompt_analyse_contrat = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_JURIDIQUE),
    ("human", """
Analyse ce contrat selon le droit OHADA et la législation congolaise.

CONTRAT :
{contrat}

Fournis :
1. Nature juridique du contrat
2. Parties identifiées
3. Clauses conformes au droit OHADA
4. Clauses manquantes ou non conformes
5. Risques juridiques identifiés
6. Recommandations
""")
])

# ── Prompt pour la génération de clauses ───────────────────────────────
prompt_generate_clauses = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_JURIDIQUE),

    ("human", """
CONTEXTE :
{context}

DEMANDE :
{demande}

INSTRUCTIONS :
- Utilise un style juridique professionnel
- Les clauses doivent être directement intégrables dans un contrat
- Cite les bases légales OHADA lorsque pertinent
- Ne génère aucune clause non conforme au droit OHADA

FORMAT :
## Clause générale
...

## Clause spécifique
...

## Clause de garantie
...
""")
])



# ── Prompt RAG avec mémoire conversationnelle ─────────────────────────
prompt_rag_avec_memoire = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_JURIDIQUE),
    MessagesPlaceholder(variable_name="chat_history"),  # historique injecté ici
    ("human", """
Contexte juridique pertinent :
{context}

Question :
{question}
""")
])

# ── Prompt pour reformuler la question avec l'historique ──────────────
prompt_reformulation = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant qui reformule les questions.
Étant donné l'historique de conversation et la nouvelle question,
reformule la question pour qu'elle soit autonome et compréhensible
sans l'historique. Si la question est déjà autonome, retourne-la telle quelle.
Réponds uniquement avec la question reformulée, rien d'autre."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])