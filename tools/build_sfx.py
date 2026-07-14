#!/usr/bin/env python3
"""ETAPE 6 — SFX + musique par-dessus renders/FINAL.mp4 (video COPIEE, seul l'audio est remixe).

Placement (regles validees, skill motion-design / references/sfx-musique.md) :
  - Riser      -> sur le HOOK, finit PILE a la fin du hook.
  - Ballpoint  -> enchaine juste apres le riser : marque la 1re transition.
  - Shutters   -> les transitions de section (4 variantes, ALTERNEES, jamais 2x la meme de suite).
  - PC typing  -> la commande qui se tape dans chaque split + le mot-cle du CTA.
  - Mouse click-> l'apparition de chaque ligne de reponse de Claude (plein ecran).
  - Musique    -> Banana Cake, -26.5 dB, toute la duree, fade in 0.4 / out 1.2.

Volumes REEQUILIBRES par niveau percu (a -20 dB uniforme, typing et clics sont inaudibles).
Les temps viennent de sections (les VRAIES coupes) + des timelines GSAP des sections.
"""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections
from build_codes_sections import CODES

ROOT = pathlib.Path(__file__).resolve().parent.parent
SFX = ROOT / "assets/sfx"
SRC = ROOT / "renders/FINAL.mp4"
OUT = ROOT / "renders/FINAL_SFX_MUSIC.mp4"
MUSIC = ROOT / "assets/music/Banana Cake.mp3"

SEC = {s["id"]: s for s in sections.sections()}
DUR = sections.DURATION

RISER = "Riser.MP3"
BALLPOINT = "Ballpoint pen click.MP3"
TYPING = "PC typing keyboard kacha.MP3"
CLICK = "mouse single click 2.MP3"
SHUTTERS = ["camera shutter sound.MP3", "camera shutter sound kashashka.MP3",
            "Click (camera shutter sound single shot).MP3", "camera shutter sound analog.MP3"]

RISER_DUR = 0.757
events = []   # (fichier, start, volume_dB, trim|None)

# 1. Riser sur le hook, cale pour finir PILE a la fin du hook
hook_end = SEC["s0-hook"]["end"]
events.append((RISER, round(hook_end - RISER_DUR, 3), -20, None))
# 2. Ballpoint juste apres : la 1re transition (hook -> "numéro 1")
events.append((BALLPOINT, hook_end, -20, None))

# 3. Shutters sur toutes les autres transitions de section (coupes franches) — alternes
transitions = [s["start"] for s in sections.sections()[2:]]
for i, t in enumerate(transitions):
    events.append((SHUTTERS[i % 4], t, -20, 0.45))

# 4/5. Par code : la frappe de la commande (split) + les lignes de reponse (plein ecran)
for num, slug, cmd, _prompt, kind, _header, items in CODES:
    a, b = SEC[f"s{num}a-{slug}"], SEC[f"s{num}b-{slug}"]

    # frappe : demarre a 0.30 dans la section, meme stagger que la timeline GSAP
    n = len(cmd)
    stag = round(min(0.075, 0.55 / n), 3)
    events.append((TYPING, round(a["start"] + 0.30, 3), -12, round(stag * n + 0.12, 3)))

    # lignes de reponse : memes temps que les tweens (cf build_codes_sections)
    d = b["dur"]
    if kind == "collapse":
        times = [0.98 + k * 0.24 for k in range(3)]
    elif kind == "strike":
        times = [0.60 + k * 0.34 for k in range(3)] + [round(d - 1.05, 2)]
    else:
        step = round(min(0.5, max(0.24, (d - 0.60 - 0.5) / 3)), 2)
        times = [0.60 + k * step for k in range(3)]
    for t in times:
        events.append((CLICK, round(b["start"] + t, 3), -14, None))

# 6. Mot-cle du CTA qui se tape (5 lettres, stagger 0.14 -> ~0.70s)
cta = SEC["s8-cta"]
events.append((TYPING, round(cta["start"] + 1.25, 3), -12, 0.78))

events.sort(key=lambda e: e[1])

# ---- ffmpeg : voix (FINAL.mp4) + N SFX + musique -----------------------------
inputs, filters, mixin = ["-i", str(SRC)], [], ["[0:a]"]
for i, (f, start, vol, trim) in enumerate(events, start=1):
    inputs += ["-i", str(SFX / f)]
    ch = f"[{i}:a]"
    if trim:
        ch_f = (f"atrim=0:{trim},volume={vol}dB,aformat=channel_layouts=stereo:sample_rates=48000,"
                f"afade=t=out:st={max(trim - 0.06, 0):.3f}:d=0.06,adelay={int(start*1000)}:all=1")
    else:
        ch_f = (f"volume={vol}dB,aformat=channel_layouts=stereo:sample_rates=48000,"
                f"adelay={int(start*1000)}:all=1")
    filters.append(f"{ch}{ch_f}[e{i}]")
    mixin.append(f"[e{i}]")

mi = len(events) + 1
inputs += ["-i", str(MUSIC)]
filters.append(f"[{mi}:a]atrim=0:{DUR},volume=-26.5dB,aformat=channel_layouts=stereo:sample_rates=48000,"
               f"afade=t=in:st=0:d=0.4,afade=t=out:st={DUR - 1.2:.3f}:d=1.2[music]")
mixin.append("[music]")

filters.append(f"{''.join(mixin)}amix=inputs={len(mixin)}:normalize=0:dropout_transition=0,"
               f"alimiter=limit=0.97[aout]")

cmd = (["ffmpeg", "-y", "-v", "error"] + inputs +
       ["-filter_complex", ";".join(filters), "-map", "0:v", "-c:v", "copy",
        "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)])
r = subprocess.run(cmd, capture_output=True, text=True)
print("ffmpeg exit:", r.returncode)
if r.returncode:
    print(r.stderr[-1200:])
    raise SystemExit(1)

print(f"{len(events)} SFX + musique -> {OUT.relative_to(ROOT)}")
for f, s, v, t in events:
    print(f"  {s:6.2f}  {v:>4} dB  {f}{'  (trim ' + str(t) + ')' if t else ''}")
