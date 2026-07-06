from app.ingestion import load_and_split_base_juridique
from app.vectorstore import index_documents, search


# ── Test 1 : indexation ───────────────────────────────────────────────
print("=" * 50)
print("TEST 1 — Indexation des documents juridiques")
print("=" * 50)

chunks = load_and_split_base_juridique()
vectorstore = index_documents(chunks)

# ── Test 2 : recherche sémantique ─────────────────────────────────────
print("\n" + "=" * 50)
print("TEST 2 — Recherche sémantique")
print("=" * 50)

queries = [
    "conditions de validité d'un contrat",
    "liberté contractuelle",
    "formation et acceptation du contrat"
]

for query in queries:
    print(f"\n🔍 Query : '{query}'")
    results = search(query, k=2)
    for i, doc in enumerate(results):
        print(f"\n  Résultat {i+1} :")
        print(f"  Source : {doc.metadata.get('source', 'inconnue')}")
        print(f"  Catégorie : {doc.metadata.get('categorie', 'inconnue')}")
        print(f"  Contenu : {doc.page_content[:150]}...")