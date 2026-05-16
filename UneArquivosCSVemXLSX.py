import pandas as pd
import glob
import os

# Pasta onde estão os CSVs
PASTA_CSV = r"C:\caminho\da\pasta"

# Nome do arquivo Excel final
ARQUIVO_SAIDA = "arquivo_unificado.xlsx"

# Busca todos os arquivos CSV da pasta
arquivos_csv = glob.glob(os.path.join(PASTA_CSV, "*.csv"))

# Lista para armazenar os DataFrames
lista_dfs = []

# Lê cada CSV
for arquivo in arquivos_csv:
    try:
        df = pd.read_csv(arquivo)

        # Opcional: adiciona o nome do arquivo como coluna
        df["arquivo_origem"] = os.path.basename(arquivo)

        lista_dfs.append(df)

        print(f"Lido com sucesso: {arquivo}")

    except Exception as e:
        print(f"Erro ao ler {arquivo}: {e}")

# Une todos os DataFrames
if lista_dfs:
    df_final = pd.concat(lista_dfs, ignore_index=True)

    # Salva em XLSX
    df_final.to_excel(ARQUIVO_SAIDA, index=False)

    print(f"\nArquivo Excel gerado: {ARQUIVO_SAIDA}")
else:
    print("Nenhum CSV válido encontrado.")
