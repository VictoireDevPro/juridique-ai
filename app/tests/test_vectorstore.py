from app.juridique.ingestion import load_and_split_base_juridique
from app.juridique.vectorstore import index_documents, search, reset_collection, get_qdrant_client


# ── Test 1 : indexation ───────────────────────────────────────────────
print("=" * 50)
print("TEST 1 — Indexation des documents juridiques")
print("=" * 50)

reset_collection(get_qdrant_client())
chunks = load_and_split_base_juridique()
vectorstore = index_documents(chunks)

# ── Test 2 : recherche sémantique ─────────────────────────────────────
print("\n" + "=" * 50)
print("TEST 2 — Recherche sémantique")
print("=" * 50)

queries = [
    "que dit le code civil congolais sur la comparaison entre articles similaires ?"
    # "Recherche similarité"
    # "conditions de validité d'un contrat",
    # "liberté contractuelle",
    # "formation et acceptation du contrat"
]

for query in queries:
    print(f"\n🔍 Query : '{query}'")
    results = search(query, k=2)
    for i, (doc, score) in enumerate(results):
        print(f"\n  Résultat {i+1} (score={score:.4f}) :")
        print(f"  Source : {doc.metadata.get('source', 'inconnue')}")
        print(f"  Catégorie : {doc.metadata.get('categorie', 'inconnue')}")
        print(f"  Contenu : {doc.page_content}")