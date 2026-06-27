import spacy

# Carrega o modelo pré-treinado em português
nlp = spacy.load("pt_core_news_lg")

texto = """
João Silva assinou o contrato com a Empresa XPTO em 15 de março 
de 2024, no valor de R$ 50.000,00. A reunião de fechamento 
aconteceu em São Paulo.
"""

doc = nlp(texto)

for entidade in doc.ents:
    print(f"{entidade.text:<25} -> {entidade.label_}")