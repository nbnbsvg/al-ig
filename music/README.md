# Background music provenance

All background tracks for ask_lawyer_co_il videos are generated from scratch by
`make_music.py` (Python, numpy/scipy): sine-wave pads, synthesized bell tones, and a
synthetic reverb. No samples, recordings, loops, or third-party melodies are used.
Pitches of the bell line come from a seeded random walk over a scale.

Moods: calm, warm, light, deep. Command: `python3 make_music.py <out.wav> <mood> <seed> <seconds>`

| Track | Command | Used in |
|---|---|---|
| calm | `python3 make_music.py calm.wav calm 101 23` | reel-2/license-reel-music.mp4 |
| warm | `python3 make_music.py warm.wav warm 202 23` | reel-3/system-reel-music.mp4 |
| light | `python3 make_music.py light.wav light 303 23` | sample only (samples/sample_3_light.mp3) |
| deep | `python3 make_music.py deep.wav deep 404 23` | sample only (samples/sample_4_deep.mp3) |

New tracks: pick a new mood/seed pair so each video gets its own piece.
