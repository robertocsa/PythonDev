# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 08:34:19 2024

Nova versão:
- Permite informar um OFFSET inicial.
- O preview será gerado apenas a partir desse ponto do vídeo.
- Útil para ignorar introduções longas, vinhetas, etc.

@author: Roberto C. Santos (código criado no ChatGPT)
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


def recortar_video_para_preview(
    input_video_path,
    tempo_max_preview,
    tempo_trechos,
    offset_inicio
):

    video = VideoFileClip(input_video_path)

    try:

        duracao_video = video.duration

        print(f"Duração total do vídeo: {duracao_video:.3f}s")
        print(f"Offset inicial: {offset_inicio:.3f}s")

        # Garante que o offset não ultrapasse o vídeo
        if offset_inicio >= duracao_video:
            raise ValueError(
                "O offset informado é maior ou igual à duração do vídeo."
            )

        # Nova duração disponível após offset
        duracao_disponivel = duracao_video - offset_inicio

        print(f"Duração disponível após offset: {duracao_disponivel:.3f}s")

        tempo_total_preview = min(
            tempo_max_preview,
            duracao_disponivel
        )

        print(f"Tempo total do preview: {tempo_total_preview:.3f}s")

        qtde_recortes = int(tempo_total_preview // tempo_trechos)

        if qtde_recortes < 1:
            qtde_recortes = 1

        print(f"Quantidade de recortes: {qtde_recortes}")

        tempo_salto = (
            (duracao_disponivel // qtde_recortes)
            - tempo_trechos
        )

        if tempo_salto < 0:
            tempo_salto = 0

        print(f"Tempo do salto: {tempo_salto:.3f}s")

        trechos = []

        inicio = offset_inicio

        for i in range(qtde_recortes):

            fim = inicio + tempo_trechos

            # Não ultrapassar o vídeo
            fim = min(fim, duracao_video)

            print(
                f"Trecho {i + 1}: "
                f"início={inicio:.3f}s | "
                f"fim={fim:.3f}s"
            )

            trecho = video.subclipped(inicio, fim)

            trechos.append(trecho)

            inicio = fim + tempo_salto

            # Evita tentar criar trechos além do vídeo
            if inicio >= duracao_video:
                break

        if not trechos:
            raise ValueError(
                "Nenhum trecho pôde ser criado."
            )

        preview_video = concatenate_videoclips(trechos)

        nome_arquivo = os.path.splitext(
            os.path.basename(input_video_path)
        )[0]

        data_hora = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        output_video_path = (
            f"preview-{nome_arquivo}-{data_hora}.mp4"
        )

        preview_video.write_videofile(
            output_video_path,
            codec="libx264",
            audio_codec="aac",
            bitrate="5000k",
            fps=30
        )

        print("\nVídeo de preview gerado com sucesso:")
        print(output_video_path)

    finally:

        video.close()

        if 'preview_video' in locals():
            preview_video.close()


# =========================================================
# ENTRADAS
# =========================================================

str_input_tempo_max_preview = input(
    "Digite o tempo máximo do preview "
    "(sugerido 10s a 60s). "
    "Enter para padrão (30s): "
)

tempo_max_preview = (
    int(str_input_tempo_max_preview)
    if str_input_tempo_max_preview.isdigit()
    else 30
)

str_input_tempo_recorte = input(
    "Digite o tempo de cada trecho "
    "(Enter para 3s): "
)

tempo_recorte = (
    int(str_input_tempo_recorte)
    if str_input_tempo_recorte.isdigit()
    else 3
)

str_input_offset = input(
    "Digite o offset inicial em segundos "
    "(Enter para 0): "
)

try:
    offset_inicio = (
        float(str_input_offset)
        if str_input_offset.strip() != ""
        else 0.0
    )

except:
    offset_inicio = 0.0


# =========================================================
# SELEÇÃO DO VÍDEO
# =========================================================

input_video_path = selecionar_pasta_video()

if input_video_path:

    recortar_video_para_preview(
        input_video_path,
        tempo_max_preview,
        tempo_recorte,
        offset_inicio
    )

else:
    print("Nenhum arquivo de vídeo foi selecionado.")
