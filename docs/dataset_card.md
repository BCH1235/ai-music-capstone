# Dataset Card (Step 1.7)

Intended use
- Train our own symbolic generators (Melody Transformer + Drum-Groove VAE) for 30-second BGM.
- Training data is MIDI only. Outputs are rendered to audio with fixed SoundFonts.

Datasets shortlist (verify licenses before download)
- MAESTRO (MIDI-only) — License: CC BY-NC-SA 4.0 — Use: melody/harmony (piano). Source URL: TODO
- Groove MIDI (GMD) — License: CC BY 4.0 — Use: human drums. Source URL: TODO
- E-GMD — License: CC BY 4.0 — Use: human drums (expanded). Source URL: TODO
- Slakh2100 — License: CC BY-SA 4.0 — Use: optional instrument hints / render refs. Source URL: TODO
- GiantMIDI-Piano (optional) — License/terms: verify — Use: melody/harmony (classical). Source URL: TODO

Inclusion criteria
- Clean MIDI with clear timing; 4/4 preferred; length ≥ 4 bars.

Exclusion rules
- Licensing conflicts; corrupted timing; extreme tempo instability.

Preprocessing plan
- Normalize BPM to a small set; quantize to 16th notes; extract 4/8/16-bar crops.
- Detect key/scale; write token files for melody and drum subsets.

Ethics & IP
- Research/education use only; keep a list of sources and attributions.
- Do not redistribute original copyrighted material.