from app.rag import build_rag_chain, build_contrat_chain, generate_clauses_base_on_existing

# ── Test 1 : Question juridique via RAG ───────────────────────────────
print("=" * 50)
print("TEST 1 — Question juridique avec RAG")
print("=" * 50)

rag_chain = build_rag_chain()

questions = [
    "Quelles sont les conditions de validité d'un contrat ?",
    "Qu'est ce que la liberté contractuelle selon l'OHADA ?",
    "Comment se forme un contrat valablement ?"
]

for question in questions:
    print(f"\n🔍 Question : {question}")
    print("-" * 40)
    response = rag_chain.invoke(question)
    print("=========> Response :")
    print(response)
    print()

# ── Test 2 : Analyse de contrat ───────────────────────────────────────
print("=" * 50)
print("TEST 2 — Analyse de contrat")
print("=" * 50)

contrat_chain = build_contrat_chain()

contrat_test = """
CONTRAT DE PRESTATION DE SERVICES

Entre :
- La société TECH CONGO SARL, représentée par M. Moukala Pierre, Directeur Général
- M. Batantou Serge, développeur indépendant

Objet : Développement d'une application mobile de gestion de stock

Durée : 3 mois à compter du 1er juin 2025

Rémunération : 2 500 000 FCFA payable à la livraison

Fait à Brazzaville, le 1er juin 2025
"""

print(f"\n📄 Contrat soumis à l'analyse...")
print("-" * 40)
response = contrat_chain.invoke({"contrat": contrat_test})
print("=========> Response :")
print(response)


# ── Test 3 : Génération de clauses ───────────────────────────────────────

print("=" * 50)
print("TEST 3 — Génération de clauses")
print("=" * 50)

generate_clauses_chain = generate_clauses_base_on_existing()

demande_test = "Contrat de prestation de services informatiques"
print(f"\n📄 Demande de génération de clauses : {demande_test}")
print("-" * 40)
print("=========> Response :")
response = generate_clauses_chain.invoke({"demande": demande_test})
print(response)