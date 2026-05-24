from pydub import AudioSegment
from pydub.silence import detect_silence
import os


def alongar_silencios_percentual(
    arquivo_entrada,
    arquivo_saida,

    # silêncio mínimo detectável
    silencio_minimo_ms=200,

    # threshold de silêncio
    threshold_db=-55,

    # percentual de aumento
    aumento_percentual=70,

    # proteção contra corte da voz
    margem_ms=80
):
    """
    Aumenta proporcionalmente cada trecho de silêncio.

    Exemplo:
    ----------
    aumento_percentual = 70

    silêncio de 1000 ms -> 1700 ms
    silêncio de 500 ms  -> 850 ms
    silêncio de 200 ms  -> 340 ms
    """

    audio = AudioSegment.from_file(arquivo_entrada)

    silencios = detect_silence(
        audio,
        min_silence_len=silencio_minimo_ms,
        silence_thresh=threshold_db,
        seek_step=1
    )

    print(f"Silêncios detectados: {len(silencios)}")

    if not silencios:
        print("Nenhum silêncio detectado.")

        audio.export(
            arquivo_saida,
            format=os.path.splitext(arquivo_saida)[1][1:]
        )
        return

    resultado = AudioSegment.empty()

    cursor = 0

    for inicio, fim in silencios:

        # protege bordas da voz
        inicio_real = max(cursor, inicio + margem_ms)
        fim_real = max(inicio_real, fim - margem_ms)

        if fim_real <= inicio_real:
            continue

        # duração do silêncio detectado
        duracao_silencio = fim_real - inicio_real

        # quanto adicionar proporcionalmente
        silencio_extra_ms = int(
            duracao_silencio * (aumento_percentual / 100.0)
        )

        # adiciona trecho até o fim do silêncio original
        resultado += audio[cursor:fim_real]

        # adiciona silêncio proporcional
        resultado += AudioSegment.silent(
            duration=silencio_extra_ms
        )

        cursor = fim_real

    # adiciona final do áudio
    resultado += audio[cursor:]

    # exporta
    resultado.export(
        arquivo_saida,
        format=os.path.splitext(arquivo_saida)[1][1:]
    )

    print()
    print(f"Duração original : {len(audio)/1000:.2f}s")
    print(f"Duração final    : {len(resultado)/1000:.2f}s")
    print(f"Arquivo salvo em : {arquivo_saida}")


# =====================================
# EXEMPLO DE USO
# =====================================

alongar_silencios_percentual(
    arquivo_entrada="entrada.mp3",
    arquivo_saida="saida.mp3",

    # detecta pausas acima de X ms
    silencio_minimo_ms=50,

    # threshold
    threshold_db=-55,

    # aumenta cada silêncio em 110%
    aumento_percentual=110,

    # proteção
    margem_ms=80
)