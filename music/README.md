# Background music provenance

All background tracks for ask_lawyer_co_il videos are generated from scratch by
`make_music.py` (numpy/scipy): sine-wave pads, synthesized bell tones, and a
synthetic reverb. No samples, recordings, loops, or third-party melodies are used.

| Track | Command | Used in |
|---|---|---|
| calm | `python3 make_music.py calm.wav calm 101 23` | reel-2/license-reel-music.mp4 |
| warm | `python3 make_music.py warm.wav warm 202 23` | reel-3/system-reel-music.mp4 |

New tracks: pick a new mood/seed pair, so each video gets its own piece.
