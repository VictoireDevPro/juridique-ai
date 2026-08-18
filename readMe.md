py -m app.test_vectorstore.py 

Plus tard apres avoir terminé tout les modules on va dynamiser le system prompt avec le moyen de le mettre a jour et le system prompt aura bien sur un doc template sur lequel il pourra s'appuyer, mais surtout l'IA va commencer a le batir par rapport au document uploader du coup si tu uploader des document uridique le system prompt se definir par rapport a cela, si tu uploade le document medecine il fait de mêmeêle.

## session_id retiré de /contrat et /generer_clauses

Retiré pour l'instant de `ContratRequest`/`ContratResponse` car il n'était pas utilisé par les chains (pas de mémoire conversationnelle sur ces routes, contrairement à `/question`). À réintroduire plus tard pour relier un utilisateur à ses analyses/générations, et constituer un dataset des contrats et clauses traités pour améliorer les prochaines analyses/générations.