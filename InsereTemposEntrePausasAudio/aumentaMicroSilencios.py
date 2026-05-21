from pydub import AudioSegment
from pydub.silence import detect_silence
import os


def suavizar_fala_rapida(
    arquivo_entrada,
    arquivo_saida,

    # detecta micro pausas
    silencio_minimo_ms=30,

    # ignora pausas longas
    silencio_maximo_ms=200,

    # threshold mais alto
    threshold_db=-40,

    # aumento percentual
    aumento_percentual=35,

    # proteção da fala
    margem_ms=15
):
    """
    Suaviza fala muito rápida aumentando apenas micro pausas.

    Ideal para:
    - TTS acelerado
    - narração corrida
    - leitura automática
    - voz IA muito rápida

    Ignora pausas longas.
    Atua apenas nas micro separações entre palavras.
    """

    audio = AudioSegment.from_file(arquivo_entrada)

    silencios = detect_silence(
        audio,
        min_silence_len=silencio_minimo_ms,
        silence_thresh=threshold_db,
        seek_step=1
    )

    print(f"Silêncios detectados: {len(silencios)}")

    resultado = AudioSegment.empty()

    cursor = 0

    sil_processados = 0

    for inicio, fim in silencios:

        duracao_original = fim - inicio

        # IGNORA pausas longas
        if duracao_original > silencio_maximo_ms:
            continue

        # protege bordas da fala
        inicio_real = max(cursor, inicio + margem_ms)
        fim_real = max(inicio_real, fim - margem_ms)

        duracao_real = fim_real - inicio_real

        if duracao_real <= 0:
            continue

        # silêncio proporcional extra
        silencio_extra_ms = int(
            duracao_real * (aumento_percentual / 100.0)
        )

        # mantém tudo até o fim do silêncio original
        resultado += audio[cursor:fim_real]

        # injeta micro pausa extra
        resultado += AudioSegment.silent(
            duration=silencio_extra_ms
        )

        cursor = fim_real

        sil_processados += 1

    # restante final
    resultado += audio[cursor:]

    resultado.export(
        arquivo_saida,
        format=os.path.splitext(arquivo_saida)[1][1:]
    )

    print()
    print(f"Micro pausas alteradas : {sil_processados}")
    print(f"Duração original       : {len(audio)/1000:.2f}s")
    print(f"Duração final          : {len(resultado)/1000:.2f}s")
    print(f"Arquivo salvo em       : {arquivo_saida}")


# ==========================================
# EXEMPLO
# ==========================================

suavizar_fala_rapida(
    arquivo_entrada="entrada.mp3",
    arquivo_saida="saida.mp3",

    # micro pausas
    silencio_minimo_ms=30,

    # ignora pausas maiores
    silencio_maximo_ms=200,

    # threshold mais agressivo
    threshold_db=-40,

    # aumento leve
    aumento_percentual=35,

    # proteção
    margem_ms=15
)