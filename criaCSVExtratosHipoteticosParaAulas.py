import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Pasta onde os arquivos serão salvos
output_dir = Path("extratos_bancarios")
output_dir.mkdir(exist_ok=True)

# Lista de descrições simuladas
descricoes = [
    "PIX Recebido",
    "PIX Enviado",
    "Transferência TED",
    "Pagamento Boleto",
    "Supermercado",
    "Farmácia",
    "Posto de Gasolina",
    "Restaurante",
    "Netflix",
    "Spotify",
    "Salário",
    "Aluguel",
    "Conta de Luz",
    "Conta de Água",
    "Internet",
    "Compra Cartão",
    "Cashback",
    "Padaria",
    "Uber",
    "iFood"
]

# Configurações
quantidade_arquivos = 12
linhas_por_arquivo = 60

for i in range(1, quantidade_arquivos + 1):

    nome_arquivo = output_dir / f"extrato_{i:02d}.csv"

    saldo = round(random.uniform(1000, 10000), 2)

    with open(nome_arquivo, mode="w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo, delimiter=";")

        # Cabeçalho
        writer.writerow([
            "Data",
            "Descrição",
            "Tipo",
            "Valor",
            "Saldo"
        ])

        # Data inicial aleatória
        data_atual = datetime.now() - timedelta(days=90)

        for _ in range(linhas_por_arquivo):

            data_atual += timedelta(
                days=random.randint(0, 2),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            descricao = random.choice(descricoes)

            # Define crédito ou débito
            tipo = random.choice(["Crédito", "Débito"])

            valor = round(random.uniform(8, 3500), 2)

            if tipo == "Crédito":
                saldo += valor
            else:
                saldo -= valor

            writer.writerow([
                data_atual.strftime("%d/%m/%Y %H:%M"),
                descricao,
                tipo,
                f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ])

print("12 arquivos CSV gerados com sucesso!")
print(f"Pasta: {output_dir.resolve()}")
