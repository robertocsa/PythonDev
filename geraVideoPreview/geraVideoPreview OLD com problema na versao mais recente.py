# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 08:34:19 2024

Serve:

1. para criar um video de preview curto de um outro vídeo.
2. para criar uma versão mais curta, e menos enfadonha, de um vídeo muito longo. O usuário pode escolher a duração de cada cena e o tamanho maximo do vídeo gerado.

Não funciona bem no Spyder. Só consegui rodar chamando o python dentro de uma janela de CMD

@author: rober
"""
#from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy import VideoFileClip, concatenate_videoclips

from tkinter import Tk, filedialog
from datetime import datetime
import os

def selecionar_pasta_video():
    # Criar uma instância da janela Tkinter
    root = Tk()
    root.withdraw()  # Ocultar a janela principal (não vamos precisar dela)

    # Abrir a janela para selecionar o arquivo de vídeo
    video_path = filedialog.askopenfilename(
        title="Selecione o vídeo", 
        filetypes=[("Arquivos de vídeo", "*.mp4;*.avi;*.mov")]
    )
    
    # Retornar o caminho do arquivo selecionado
    return video_path

def recortar_video_para_preview(input_video_path, tempo_max_preview, tempo_trechos):
    # Abrir o vídeo original
    video = VideoFileClip(input_video_path)
    
    '''
    # Garantir que o tempo máximo do preview está entre 10s e 60s
    if tempo_max_preview < 10:
        tempo_max_preview = 10
    elif tempo_max_preview > 60:
        tempo_max_preview = 60
    '''
    
    print(f"Tempo dos trechos: {tempo_trechos}")
    
    # Calcular a duração total para o preview
    duracao_video = video.duration
    print(f"Duração do vídeo: {duracao_video}")
    
    tempo_total_preview = min(tempo_max_preview, duracao_video)    
    print(f"Tempo total do preview: {tempo_total_preview}")
    
    # Calcular a qtde de frames:
    qtdeRecortes=int(tempo_total_preview // tempo_trechos)
    print(f"Quantidade de recortes: {qtdeRecortes}")
    
    # Calcular o tempo entre o final de um bloco e o início do próximo
    tempo_salto=(duracao_video // qtdeRecortes)-tempo_trechos
    print(f"Tempo do salto: {tempo_salto}")

    # Lista para armazenar os trechos de x segundos
    trechos = []

    # Adicionar os recortes de n segundos a partir de intervalos regulares
    inicio = 0
    for i in range(qtdeRecortes):        
        fim = inicio + tempo_trechos
        fim = min(fim, duracao_video)
        print(f"Início {inicio}, fim:{fim}")
        trechos.append(video.subclip(inicio, fim))
        inicio = fim + tempo_salto # Atualiza o início do próximo recorte
    
    # Concatenar os trechos para formar o preview
    preview_video = concatenate_videoclips(trechos)
    
    # Extrair o nome do arquivo de vídeo original (sem extensão)
    nome_arquivo = os.path.splitext(os.path.basename(input_video_path))[0]
    
    # Gerar nome do arquivo com a data e hora de criação e o nome do arquivo original
    data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_video_path = f"preview-{nome_arquivo}-{data_hora}.mp4"
    
    # Salvar o vídeo final de preview
    preview_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", bitrate="5000k", fps=30)
    
    print(f"Vídeo de preview gerado: {output_video_path}")

# Entrada do usuário para o tempo máximo do preview (entre 10s e 60 segundos)
strInputTempoMaxPreview=input("Digite o tempo máximo do vídeo (sugerido p/ vídeos de preview algo entre 10s e 60s). Dê enter para selecionar o valor padrão (30s de vídeo): ")
if (strInputTempoMaxPreview!=""):
    tempo_max_preview = int(strInputTempoMaxPreview)
if (strInputTempoMaxPreview=="" or tempo_max_preview==0):
    tempo_max_preview=30

# Entrada do usuário para o tempo de cada recorte
strInputTempoRecorte=input("Digite o tempo de cada trecho de recorte (ou enter para 3s): ")
if (strInputTempoRecorte!=""):
    tempo_recorte= int(strInputTempoRecorte)
if (strInputTempoRecorte=="" or tempo_recorte==0):
    tempo_recorte=3   

# Solicitar ao usuário a seleção do arquivo de vídeo
input_video_path = selecionar_pasta_video()

if input_video_path:
    # Chamar a função para recortar o vídeo
    recortar_video_para_preview(input_video_path, tempo_max_preview, tempo_recorte)
else:
    print("Nenhum arquivo de vídeo foi selecionado.")
