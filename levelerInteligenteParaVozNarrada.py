# ============================================================
# LEVELER INTELIGENTE PARA VOZ NARRADA - 48 kHz
# ============================================================
#
# OBJETIVO
# --------
# Nivelar automaticamente:
# - trechos muito baixos
# - trechos muito altos
#
# Preservando:
# - naturalidade
# - dinâmica
# - inteligibilidade
#
# Evitando:
# - clipping
# - pumping
# - respiração exagerada
#
# ============================================================
#
# PIPELINE
# --------
#
# 1. Remove DC offset
# 2. High-pass filter
# 3. De-hum automático
# 4. Divisão inteligente em segmentos
# 5. Loudness por segmento
# 6. Suavização entre segmentos
# 7. Compressão leve global
# 8. Loudness final
# 9. Limiter final
#
# ============================================================

import numpy as np
import soundfile as sf
import pyloudnorm as pyln

from scipy.signal import (
    butter,
    lfilter,
    iirnotch
)

from pedalboard import (
    Pedalboard,
    Compressor,
)

# ============================================================
# CONFIGURAÇÕES
# ============================================================

INPUT_FILE = "entrada1.wav"
OUTPUT_FILE = "saida_levelada.wav"

SAMPLE_RATE = 48000

TARGET_LUFS_SEGMENT = -22.0
TARGET_LUFS_FINAL = -18.0

SEGMENT_DURATION = 2.0
OVERLAP_DURATION = 0.25

MIN_GAIN_DB = -8
MAX_GAIN_DB = 8

FINAL_PEAK_LIMIT = 0.92

# ============================================================
# UTILIDADES
# ============================================================

def db_to_linear(db):
    return 10 ** (db / 20)


def linear_to_db(x):
    return 20 * np.log10(max(x, 1e-9))


# ============================================================
# REMOVE DC OFFSET
# ============================================================

def remove_dc_offset(audio):

    mean_value = np.mean(audio)

    print(f"DC Offset detectado: {mean_value:.8f}")

    return audio - mean_value


# ============================================================
# HIGH PASS
# ============================================================

def butter_highpass(cutoff, fs, order=4):

    nyquist = 0.5 * fs

    normal_cutoff = cutoff / nyquist

    b, a = butter(
        order,
        normal_cutoff,
        btype='high'
    )

    return b, a


def apply_highpass(data, cutoff=80, fs=48000):

    b, a = butter_highpass(cutoff, fs)

    return lfilter(b, a, data)


# ============================================================
# DE-HUM
# ============================================================

def apply_notch_filter(data, freq, fs=48000, q=30):

    b, a = iirnotch(freq, q, fs)

    return lfilter(b, a, data)


def remove_hum(data, fs):

    hum_frequencies = [
        60,
        120,
        180,
        240,
        300
    ]

    processed = data.copy()

    for freq in hum_frequencies:

        processed = apply_notch_filter(
            processed,
            freq,
            fs
        )

    return processed


# ============================================================
# MEDIÇÃO LUFS
# ============================================================

meter = pyln.Meter(SAMPLE_RATE)


def get_loudness(audio):

    try:
        return meter.integrated_loudness(audio)

    except:
        return -60.0


# ============================================================
# LIMITADOR DE GANHO
# ============================================================

def clamp_gain_db(gain_db):

    gain_db = max(gain_db, MIN_GAIN_DB)
    gain_db = min(gain_db, MAX_GAIN_DB)

    return gain_db


# ============================================================
# LEVELER POR SEGMENTOS
# ============================================================

def segment_leveler(audio, sr):

    print("Aplicando leveler inteligente...")

    segment_samples = int(
        SEGMENT_DURATION * sr
    )

    overlap_samples = int(
        OVERLAP_DURATION * sr
    )

    step = (
        segment_samples - overlap_samples
    )

    output = np.zeros_like(audio)

    weights = np.zeros_like(audio)

    total_segments = 0

    for start in range(
        0,
        len(audio),
        step
    ):

        end = min(
            start + segment_samples,
            len(audio)
        )

        segment = audio[start:end]

        if len(segment) < 2048:
            continue

        loudness = get_loudness(segment)

        gain_db = (
            TARGET_LUFS_SEGMENT - loudness
        )

        gain_db = clamp_gain_db(gain_db)

        gain = db_to_linear(gain_db)

        processed = segment * gain

        fade = np.ones(len(processed))

        fade_size = min(
            overlap_samples,
            len(processed) // 2
        )

        if fade_size > 0:

            fade_in = np.linspace(
                0,
                1,
                fade_size
            )

            fade_out = np.linspace(
                1,
                0,
                fade_size
            )

            fade[:fade_size] *= fade_in
            fade[-fade_size:] *= fade_out

        output[start:end] += (
            processed * fade
        )

        weights[start:end] += fade

        total_segments += 1

    weights[weights == 0] = 1.0

    output /= weights

    print(f"Segmentos processados: {total_segments}")

    return output


# ============================================================
# COMPRESSÃO SUAVE GLOBAL
# ============================================================

def apply_compression(audio, sr):

    board = Pedalboard([

        Compressor(
            threshold_db=-18,
            ratio=2.0,
            attack_ms=15,
            release_ms=180,
        )
    ])

    return board(audio, sr)


# ============================================================
# NORMALIZAÇÃO FINAL
# ============================================================

def normalize_final(audio):

    loudness = get_loudness(audio)

    print(f"Loudness antes final: {loudness:.2f} LUFS")

    normalized = pyln.normalize.loudness(
        audio,
        loudness,
        TARGET_LUFS_FINAL
    )

    return normalized


# ============================================================
# LIMITER FINAL
# ============================================================

def final_limiter(audio):

    peak = np.max(np.abs(audio))

    print(f"Peak antes limiter: {peak:.4f}")

    if peak > FINAL_PEAK_LIMIT:

        gain = FINAL_PEAK_LIMIT / peak

        print(f"Redução aplicada: {gain:.4f}")

        audio *= gain

    peak_after = np.max(np.abs(audio))

    print(f"Peak final: {peak_after:.4f}")

    return audio


# ============================================================
# PROCESSAMENTO PRINCIPAL
# ============================================================

print("Carregando áudio...")

audio, sr = sf.read(INPUT_FILE)

# ============================================================
# VALIDA SAMPLE RATE
# ============================================================

if sr != SAMPLE_RATE:

    raise ValueError(
        f"O áudio precisa estar em 48kHz. "
        f"Atual: {sr}"
    )

# ============================================================
# MONO OPCIONAL
# ============================================================

if len(audio.shape) > 1:

    print("Convertendo para mono...")

    audio = np.mean(audio, axis=1)

# ============================================================
# DC OFFSET
# ============================================================

print("Removendo DC offset...")

audio = remove_dc_offset(audio)

# ============================================================
# HIGH PASS
# ============================================================

print("Aplicando high-pass...")

audio = apply_highpass(
    audio,
    cutoff=80,
    fs=sr
)

# ============================================================
# DE-HUM
# ============================================================

print("Aplicando de-hum...")

audio = remove_hum(audio, sr)

# ============================================================
# LEVELER INTELIGENTE
# ============================================================

audio = segment_leveler(
    audio,
    sr
)

# ============================================================
# COMPRESSÃO GLOBAL SUAVE
# ============================================================

print("Aplicando compressão suave...")

audio = apply_compression(
    audio,
    sr
)

# ============================================================
# HEADROOM PREVENTIVO
# ============================================================

audio *= 0.85

# ============================================================
# NORMALIZAÇÃO FINAL
# ============================================================

print("Aplicando loudness final...")

audio = normalize_final(audio)

# ============================================================
# LIMITER FINAL
# ============================================================

print("Aplicando limiter final...")

audio = final_limiter(audio)

# ============================================================
# CLIP SAFETY
# ============================================================

audio = np.clip(audio, -1.0, 1.0)

# ============================================================
# EXPORTAÇÃO
# ============================================================

print("Exportando áudio...")

sf.write(
    OUTPUT_FILE,
    audio,
    sr,
    subtype='PCM_24'
)

# ============================================================
# FINAL
# ============================================================

print("\nProcessamento concluído.")
print(f"Arquivo gerado: {OUTPUT_FILE}")
print(f"Loudness final alvo: {TARGET_LUFS_FINAL} LUFS")