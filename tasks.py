from invoke import task


@task
def run(c, reload=False, port=8000):
    """
    Lance le serveur FastAPI (uvicorn).
    Ex: inv run / inv run --reload / inv run --port=8001

    reload=False par défaut : --reload s'est montré instable sur cette machine
    (le worker qui bind réellement le port ne démarre pas toujours correctement).
    """
    flag = "--reload" if reload else ""
    c.run(f"venv\\Scripts\\python.exe -m uvicorn main:app {flag} --port {port}".strip())
