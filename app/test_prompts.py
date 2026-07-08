from app.llm import get_llm
from app.prompts import prompt_question, prompt_analyse_contrat, prompt_generate_clauses
from langchain_core.output_parsers import StrOutputParser


llm = get_llm()


# ── Test 1 : question juridique simple ────────────────────────────────

print("=" * 50)
print("TEST 1 — Question juridique")
print("=" * 50)

# chain_question = prompt_question | llm | StrOutputParser()
chain_question = prompt_question | llm
response = chain_question.invoke({
    "question": "Quelles sont les conditions de validité d'un contrat selon l'OHADA ?"
})

# print(response)
print(response)

# # ── Test 2 : analyse d'un mini contrat ───────────────────────────────
print("\n" + "=" * 50)
print("TEST 2 — Analyse de contrat")
print("=" * 50)

chain_contrat = prompt_analyse_contrat | llm | StrOutputParser()
mini_contrat = """
CONTRAT DE VENTE

Entre M. Dupont Jean, vendeur, et Mme Mbongo Claire, acheteur.
Objet : Vente d'un véhicule Toyota Corolla 2019.
Prix : 8 000 000 FCFA payable en 3 versements.
Fait à Brazzaville, le 15 mai 2025.
Signatures : ...
"""

response = chain_contrat.invoke({
    "contrat": mini_contrat
})

print(response)

# ── Test 3 : génération de clauses ─────────────────────────────────────
print("\n" + "=" * 50)
print("TEST 3 — Génération de clauses")

chain_generate_clauses  = prompt_generate_clauses | llm | StrOutputParser()
response = chain_generate_clauses.invoke({
    "demande": "Contrat de prestation de services informatiques",
#     "contrat": """
# Entreprise A fournit des services de développement logiciel
# à Entreprise B pour une durée de 12 mois.
# """
})

print(response)