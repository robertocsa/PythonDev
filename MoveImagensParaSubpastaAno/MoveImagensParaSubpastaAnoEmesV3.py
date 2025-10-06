import os
import subprocess
from datetime import datetime
from PIL import Image  # Para ler metadados EXIF de imagens. Instale com: pip install pillow

# Caminho da pasta de origem (hardcoded)
pasta_origem = r"E:\Users\rober\Pictures\temp"  # Substitua pelo caminho real da pasta

# Mapeamento de meses para nomes em português
meses = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

def obter_ano_mes_arquivo(caminho_arquivo):
    """
    Obtém o ano e mês da data 'tirada em' (EXIF para imagens) ou data de modificação para outros arquivos.
    Retorna uma tupla (ano, mes).
    """
    try:
        # Para imagens, tentar ler EXIF
        if caminho_arquivo.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            with Image.open(caminho_arquivo) as img:
                exif_data = img._getexif()
                if exif_data:
                    # Tag EXIF para data tirada: 36867 (DateTimeOriginal)
                    data_exif = exif_data.get(36867)
                    if data_exif:
                        data = datetime.strptime(data_exif, '%Y:%m:%d %H:%M:%S')
                        return data.year, data.month
        
        # Se não for imagem ou não tiver EXIF, usar data de modificação do arquivo
        timestamp = os.path.getmtime(caminho_arquivo)
        data = datetime.fromtimestamp(timestamp)
        return data.year, data.month
    
    except Exception as e:
        print(f"Erro ao obter data de {caminho_arquivo}: {e}")
        return None, None

def mover_arquivo(caminho_arquivo, pasta_origem, subpasta):
    """
    Move o arquivo para a subpasta especificada usando robocopy.
    """
    arquivo = os.path.basename(caminho_arquivo)
    try:
        # Comando Robocopy: robocopy source_dir dest_dir file /MOV
        comando = ['robocopy', pasta_origem, subpasta, arquivo, '/MOV']
        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        if resultado.returncode not in (0, 1):  # Robocopy retorna 0 ou 1 para sucesso
            print(f"Erro ao mover {arquivo}: {resultado.stderr}")
        else:
            print(f"{arquivo} movido para {subpasta}")
    except Exception as e:
        print(f"Erro ao executar Robocopy para {arquivo}: {e}")

def processar_pasta():
    """
    Itera recursivamente por arquivos e subpastas a partir de pasta_origem,
    organizando arquivos em subpastas <ano>-<mes> no nível superior de pasta_origem.
    """
    for root, _, arquivos in os.walk(pasta_origem):
        print (root)
        for arquivo in arquivos:
            caminho_completo = os.path.join(root, arquivo)
            
            # Obter ano e mês do arquivo
            ano, mes = obter_ano_mes_arquivo(caminho_completo)
            if ano and mes:
                # Criar nome da subpasta no formato <ano>-<mes>
                nome_subpasta = f"{ano}-{meses[mes]}"
                subpasta = os.path.join(pasta_origem, nome_subpasta)
                
                # Criar subpasta se não existir
                if not os.path.exists(subpasta):
                    os.makedirs(subpasta)
                
                # Mover o arquivo para a subpasta
                mover_arquivo(caminho_completo, root, subpasta)

# Executar a função principal
if __name__ == "__main__":
    if not os.path.exists(pasta_origem):
        print(f"A pasta {pasta_origem} não existe!")
    else:
        processar_pasta()
        print("Organização concluída!")