# Este app distribui as imagens e videos em pastas de seus respectivos anos de criação ou modificação
# Cuidado: pouco experimentado. Use em uma pasta isolada, livre de subpastas
import os
import subprocess
from datetime import datetime
from PIL import Image  # Para ler metadados EXIF de imagens. Instale com: pip install pillow

# Defina a pasta de origem onde estão as fotos e vídeos
pasta_origem = r"E:\Users\rober\Pictures\temp"  # Substitua pelo caminho real da pasta

# Defina o nome ou expressao que aparece depois do ano
expressao_apos_o_ano="anotacoes manuais quadros de aula"

# Extensões de arquivos a considerar (fotos e vídeos)
extensoes_validas = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.mp4', '.mov', '.avi', '.mkv')

def obter_ano_arquivo(caminho_arquivo):
    """
    Obtém o ano da data 'tirada em' (EXIF para imagens) ou data de modificação para outros arquivos.
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
                        return data.year
        
        # Se não for imagem ou não tiver EXIF, usar data de modificação do arquivo
        timestamp = os.path.getmtime(caminho_arquivo)
        data = datetime.fromtimestamp(timestamp)
        return data.year
    
    except Exception as e:
        print(f"Erro ao obter data de {caminho_arquivo}: {e}")
        return None

# Percorrer todos os arquivos na pasta de origem (não recursivo, apenas arquivos diretos)
for arquivo in os.listdir(pasta_origem):
    caminho_completo = os.path.join(pasta_origem, arquivo)
    
    if os.path.isfile(caminho_completo) and caminho_completo.lower().endswith(extensoes_validas):
        ano = obter_ano_arquivo(caminho_completo)        
        if ano:
            subpasta = os.path.join(pasta_origem, str(ano))
            if expressao_apos_o_ano:
                subpasta = subpasta + "-" + expressao_apos_o_ano
            
            # Criar subpasta se não existir
            if not os.path.exists(subpasta):
                os.makedirs(subpasta)
            
            # Usar Robocopy para mover o arquivo
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