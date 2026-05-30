# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 08:34:19 2024

Serve:
1. para criar um video de preview curto de um outro vídeo.
2. para criar uma versão mais curta, e menos enfadonha, de um vídeo muito longo. O usuário pode escolher a duração de cada cena e o tamanho maximo do vídeo gerado.

@author: rober
"""

from moviepy import VideoFileClip, concatenate_videoclips
from tkinter import Tk, filedialog
from datetime import datetime
import os

def selecionar_pasta_video():
    root = Tk()
    root.withdraw()  
    video_path = filedialog.askopenfilename(
        title="Selecione o vídeo", 
        filetypes=[("Arquivos de vídeo", "*.mp4;*.avi;*.mov")]
    )
    return video_path

def recortar_video_para_preview(input_video_path, tempo_max_preview, tempo_trechos):
    video = VideoFileClip(input_video_path)
    try:
        duracao_video = video.duration
        print(f"Duração do vídeo: {duracao_video}")

        tempo_total_preview = min(tempo_max_preview, duracao_video)    
        print(f"Tempo total do preview: {tempo_total_preview}")

        qtdeRecortes = int(tempo_total_preview // tempo_trechos)
        if qtdeRecortes < 1:
            qtdeRecortes = 1
        print(f"Quantidade de recortes: {qtdeRecortes}")

        tempo_salto = (duracao_video // qtdeRecortes) - tempo_trechos
        if tempo_salto < 0:
            tempo_salto = 0
        print(f"Tempo do salto: {tempo_salto}")

        trechos = []
        inicio = 0

        for i in range(qtdeRecortes):
            fim = inicio + tempo_trechos
            fim = min(fim, duracao_video)
            print(f"Início {inicio}, fim {fim}")
            trechos.append(video.subclipped(inicio, fim))
            inicio = fim + tempo_salto

        preview_video = concatenate_videoclips(trechos)

        nome_arquivo = os.path.splitext(os.path.basename(input_video_path))[0]
        data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_video_path = f"preview-{nome_arquivo}-{data_hora}.mp4"

        preview_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", bitrate="5000k", fps=30)

        print(f"Vídeo de preview gerado: {output_video_path}")

    finally:
        video.close()
        if 'preview_video' in locals():
            preview_video.close()

# Entrada do usuário para o tempo máximo do preview
strInputTempoMaxPreview = input("Digite o tempo máximo do vídeo (sugerido 10s a 60s). Enter para padrão (30s): ")
tempo_max_preview = int(strInputTempoMaxPreview) if strInputTempoMaxPreview.isdigit() else 30

# Entrada do usuário para o tempo de cada recorte
strInputTempoRecorte = input("Digite o tempo de cada trecho (enter para 3s): ")
tempo_recorte = int(strInputTempoRecorte) if strInputTempoRecorte.isdigit() else 3

input_video_path = selecionar_pasta_video()

if input_video_path:
    recortar_video_para_preview(input_video_path, tempo_max_preview, tempo_recorte)
else:
    print("Nenhum arquivo de vídeo foi selecionado.")
