"""Original ambient background music, synthesized from scratch with numpy.

No samples, no recordings, no third-party melodies or loops. Every note is
computed here from sine waves, envelopes and a synthetic reverb. The pitches
come from a seeded random walk over a scale, so each (mood, seed) pair yields
a different, original piece.

usage: make_music.py <out.wav> <mood: calm|warm> <seed> <seconds>
"""
import sys
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile

SR = 44100


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env_pad(n, attack, release):
    t = np.arange(n) / SR
    d = n / SR
    a = np.clip(t / attack, 0, 1) ** 1.5
    r = np.clip((d - t) / release, 0, 1) ** 1.5
    return a * r


def pad_note(freq, dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    # three slightly detuned voices, soft harmonics -> warm pad
    for det in (-0.07, 0.0, 0.08):
        f = freq * 2 ** (det / 12)
        ph = rng.uniform(0, 2 * np.pi)
        lfo = 1 + 0.0025 * np.sin(2 * np.pi * rng.uniform(0.15, 0.35) * t + rng.uniform(0, 6))
        for k, amp in ((1, 1.0), (2, 0.35), (3, 0.12), (4, 0.05)):
            out += amp * np.sin(2 * np.pi * f * k * t * lfo + ph * k)
    return out * env_pad(n, attack=min(2.2, dur * 0.4), release=min(2.5, dur * 0.45))


def bell_note(freq, dur=3.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = (np.sin(2 * np.pi * freq * t) * np.exp(-t * 1.6)
           + 0.35 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-t * 2.8)
           + 0.12 * np.sin(2 * np.pi * freq * 3.01 * t) * np.exp(-t * 4.5))
    a = np.clip(t / 0.01, 0, 1)
    return out * a


def reverb(x, rng, seconds=2.8, wet=0.35):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((2, n)) * np.exp(-t * 2.4)
    sos = butter(2, 5000, btype="low", fs=SR, output="sos")
    ir = sosfilt(sos, ir, axis=1)
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    wetsig = np.stack([fftconvolve(x[0], ir[0])[: x.shape[1]],
                       fftconvolve(x[1], ir[1])[: x.shape[1]]])
    return (1 - wet) * x + wet * wetsig


MOODS = {
    # chords: MIDI roots + intervals (stacked), scale for the sparse bell line
    "calm": dict(
        chords=[(50, [0, 7, 12, 15, 19]), (46, [0, 7, 12, 16, 19]),
                (43, [0, 7, 12, 15, 21]), (45, [0, 7, 12, 14, 19])],
        scale=[62, 65, 67, 69, 72, 74, 77, 79], bell_p=0.40),
    "warm": dict(
        chords=[(50, [0, 7, 12, 16, 21]), (55, [0, 7, 12, 16, 18]),
                (47, [0, 7, 12, 15, 21]), (45, [0, 7, 12, 14, 19])],
        scale=[62, 64, 66, 69, 71, 74, 76, 78], bell_p=0.55),
}


def main(out, mood, seed, seconds):
    rng = np.random.default_rng(seed)
    cfg = MOODS[mood]
    total = int(seconds * SR)
    mix = np.zeros((2, total))
    chords = cfg["chords"]
    seg = seconds / len(chords)

    # pads: each chord overlaps the next a little
    for i, (root, ivs) in enumerate(chords):
        start = i * seg
        dur = seg + 2.0
        for j, iv in enumerate(ivs):
            note = pad_note(midi(root + iv), dur, rng) * (0.9 if j < 2 else 0.55)
            pan = 0.5 + 0.35 * np.sin(j * 1.7 + i)
            s = int(start * SR)
            e = min(total, s + len(note))
            mix[0, s:e] += note[: e - s] * (1 - pan)
            mix[1, s:e] += note[: e - s] * pan

    # sparse bell line: seeded random walk over the scale, one note per half-beat slot
    scale = cfg["scale"]
    idx = int(rng.integers(2, len(scale) - 2))
    step = 0.75
    tpos = 1.2
    while tpos < seconds - 3.0:
        if rng.random() < cfg["bell_p"]:
            idx = int(np.clip(idx + rng.choice([-2, -1, -1, 1, 1, 2]), 0, len(scale) - 1))
            note = bell_note(midi(scale[idx])) * 0.22
            s = int(tpos * SR)
            e = min(total, s + len(note))
            pan = rng.uniform(0.3, 0.7)
            mix[0, s:e] += note[: e - s] * (1 - pan)
            mix[1, s:e] += note[: e - s] * pan
        tpos += step

    mix = reverb(mix, rng)

    # gentle fade in / out, normalize peak
    t = np.arange(total) / SR
    fade = np.clip(t / 1.2, 0, 1) * np.clip((seconds - t) / 2.0, 0, 1)
    mix *= fade
    mix /= np.max(np.abs(mix)) * 1.15
    wavfile.write(out, SR, (mix.T * 32767).astype(np.int16))
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]))
