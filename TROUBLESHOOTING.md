# Troubleshooting

## Téléchargement d'un modèle Hugging Face bloqué à 0%

### Symptôme
Lors du premier appel à un modèle `sentence-transformers` / `transformers`
(ex: `HuggingFaceEmbeddings`), le téléchargement des petits fichiers
(`config.json`, `tokenizer.json`, ...) réussit instantanément, mais le gros
fichier de poids (`model.safetensors` ou `pytorch_model.bin`) reste bloqué
à `0.00/XXXM` sans jamais progresser.

### Cause
Depuis 2025, Hugging Face sert les gros fichiers via un nouveau protocole
appelé **Xet** (backend `hf_xet`), activé automatiquement dès que le
package `hf_xet` est installé. Sur certains réseaux (FAI restrictifs,
proxy d'entreprise, filtrage géographique...), les connexions Xet sont
bloquées silencieusement — pas d'erreur, juste un blocage permanent — alors
que le HTTPS classique vers Hugging Face fonctionne très bien.

### Diagnostic rapide
1. Vérifier que `huggingface.co` répond mais que le téléchargement du gros
   fichier ne progresse jamais après plusieurs dizaines de secondes.
2. Confirmer que le réseau fonctionne en testant l'URL réelle avec `curl` :
   ```bash
   curl -s -D - -o /dev/null -L --max-time 15 \
     "https://huggingface.co/<repo_id>/resolve/main/<fichier>"
   ```
   Si ça retourne `200 OK`, le réseau est bon — le souci vient du client Python.

### Solution 1 — Désactiver Xet (à essayer en premier)
```bash
export HF_HUB_DISABLE_XET=1   # ou set sous PowerShell : $env:HF_HUB_DISABLE_XET=1
```
Force `huggingface_hub` à utiliser son téléchargeur HTTP classique
(`httpx`) au lieu du protocole Xet. Dans la plupart des cas, ça suffit.

### Solution 2 — Si la connexion reste instable (coupures en cours de route)
Si le téléchargement avance puis se coupe (`RemoteProtocolError: peer
closed connection...`) avant la fin, c'est un problème d'instabilité
réseau, pas de Xet. Le problème est que `huggingface_hub` crée un fichier
temporaire à nom aléatoire à chaque tentative — relancer le script ne
reprend donc pas depuis la coupure précédente.

Solution : télécharger manuellement avec des requêtes `Range` en écrivant
directement dans le blob du cache, pour garantir une vraie reprise entre
tentatives :

```python
import os, time, requests

REPO_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
FILENAME = "model.safetensors"
URL = f"https://huggingface.co/{REPO_ID}/resolve/main/{FILENAME}"

# Récupérer le hash du blob et la taille attendue :
# - lancer une première fois le téléchargement normal (même s'il échoue),
#   il crée un fichier `<hash>.<random>.incomplete` dans
#   ~/.cache/huggingface/hub/models--.../blobs/
# - "hash" = la partie avant le premier point du nom de fichier
# - taille attendue = Content-Length renvoyé par une requête HEAD sur l'URL

CACHE_DIR = os.path.join(
    os.path.expanduser("~"), ".cache", "huggingface", "hub",
    f"models--{REPO_ID.replace('/', '--')}"
)
BLOB_HASH = "<a completer>"
BLOB_PATH = os.path.join(CACHE_DIR, "blobs", BLOB_HASH)
EXPECTED_SIZE = 470641600  # a completer

for attempt in range(40):
    size = os.path.getsize(BLOB_PATH) if os.path.exists(BLOB_PATH) else 0
    if size >= EXPECTED_SIZE:
        print("DONE", BLOB_PATH)
        break
    headers = {"Range": f"bytes={size}-"} if size else {}
    try:
        with requests.get(URL, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            mode = "ab" if size else "wb"
            with open(BLOB_PATH, mode) as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
    except Exception as e:
        print("Echec:", e)
        time.sleep(2)
```

Une fois le blob complet, si `huggingface_hub` ne le reconnaît toujours
pas comme "en cache" (car on a contourné la librairie), il manque le lien
dans le dossier `snapshots/` :

```bash
CACHE=~/.cache/huggingface/hub/models--<org>--<model>
REV_DIR=$(ls -d "$CACHE/snapshots"/*/)
ln -s "../../blobs/<BLOB_HASH>" "${REV_DIR}model.safetensors"
```

### Vérification finale
```bash
HF_HUB_OFFLINE=1 python -c "
from app.vectorstore import get_embeddings
emb = get_embeddings()
print(len(emb.embed_query('test')))
"
```
Si ça affiche la dimension du modèle (384 pour MiniLM) sans erreur réseau,
le modèle est bien en cache et utilisable hors-ligne.
