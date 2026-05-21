from app.llm import get_llm

llm = get_llm()

response = llm.invoke("Qu'est ce que le droit OHADA en 3 lignes ?")
print(response.content)