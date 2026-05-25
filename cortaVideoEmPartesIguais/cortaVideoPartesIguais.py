import os
import math
import subprocess
from decimal import Decimal, ROUND_DOWN
from pathlib import Path


def obter_duracao_video(video_path: str) -> float:
    """
    Obtém a duração do vídeo em segundos usando ffprobe.
    """
    comando = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]

    resultado = subprocess.run(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if resultado.returncode != 0:
        raise RuntimeError(f"Erro ao obter duração:\n{resultado.stderr}")

    return float(resultado.stdout.strip())


def truncar_3_casas(valor: float) -> float:
    """
    Trunca para 3 casas decimais sem arredondar.
    """
    return float(
        Decimal(str(valor)).quantize(
            Decimal("0.001"),
            rounding=ROUND_DOWN
        )
    )


def dividir_video(video_path: str, quantidade_partes: int):
    if quantidade_partes <= 0:
        raise ValueError("A quantidade de partes deve ser maior que zero.")

    video = Path(video_path)

    if not video.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {video_path}")

    nome_base = video.stem
    extensao = video.suffix

    duracao_total = obter_duracao_video(video_path)

    # divisão inicial
    tempo_por_parte = truncar_3_casas(duracao_total / quantidade_partes)

    # regra do limite máximo
    if tempo_por_parte > 59.999:
        tempo_por_parte = 59.999
        quantidade_partes = math.ceil(duracao_total / tempo_por_parte)

    print(f"Duração total: {duracao_total:.3f}s")
    print(f"Partes finais: {quantidade_partes}")
    print(f"Tempo por parte: {tempo_por_parte:.3f}s")

    for i in range(quantidade_partes):
        inicio = truncar_3_casas(i * tempo_por_parte)

        if i == quantidade_partes - 1:
            duracao = truncar_3_casas(duracao_total - inicio)
        else:
            duracao = tempo_por_parte

        nome_saida = (
            f"{nome_base} - vídeo {i+1} de {quantidade_partes}"
            f"{extensao}"
        )

        comando = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-ss", f"{inicio:.3f}",
            "-t", f"{duracao:.3f}",

            # preserva codecs e características
            "-c", "copy",

            nome_saida
        ]

        print(f"\nGerando: {nome_saida}")
        print(f"Início: {inicio:.3f}s")
        print(f"Duração: {duracao:.3f}s")

        resultado = subprocess.run(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if resultado.returncode != 0:
            print(f"Erro ao gerar parte {i+1}:")
            print(resultado.stderr)
        else:
            print("OK")


if __name__ == "__main__":
    caminho_video = input("Digite o caminho do MP4: ").strip().strip('"')
    partes = int(input("Digite o número de partes: "))

    dividir_video(caminho_video, partes)