from app.ingestion import load_and_split_base_juridique, load_txt

# ── Test 1 : inspecter un Document ────────────────────────────────────
print("=" * 50)
print("TEST 1 — Structure d'un Document LangChain")
print("=" * 50)

docs = load_txt("data/juridique/ohada/acte_uniforme_contrats.txt")
premier_doc = docs[0]
print(f"Type : {type(premier_doc)}")
print(f"Metadata : {premier_doc.metadata}")
print(f"Contenu (100 premiers caractères) :")
print(premier_doc.page_content[:100])

# ── Test 2 : pipeline complet ─────────────────────────────────────────
print("\n" + "=" * 50)
print("TEST 2 — Pipeline complet load + split")
print("=" * 50)

chunks = load_and_split_base_juridique()

print(f"\nPremier chunk :")
print(f"Contenu : {chunks[0].page_content}")
print(f"Metadata : {chunks[0].metadata}")

print(f"\nDeuxième chunk :")
print(f"Contenu : {chunks[1].page_content[:200]}")