#!/usr/bin/env python3
"""ETAPE 6 — SFX + musique par-dessus renders/FINAL.mp4 (video COPIEE, seul l'audio est remixe).

╔══════════════════════════════════════════════════════════════════════════════╗
║ CE FICHIER EST ADAPTE A CHAQUE REEL.                                           ║
║  - La MUSIQUE vient de brand.config.json -> audio.musicFile + audio.musicDb.   ║
║  - Les SFX sont les fichiers presents dans assets/sfx/.                        ║
║  - Le MAPPING/PLACEMENT (quel SFX, a quel instant, a quel volume) est PILOTE   ║
║    PAR L'AGENT : remplis la liste EVENTS ci-dessous, un evenement par SFX.     ║
║ La demo place un SFX de transition sur chaque frontiere de section — c'est un  ║
║ EXEMPLE de structure, remplace-le par le placement de TON Reel.                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Regles generales (skill motion-design / references/sfx-musique.md) :
  - Musique en fond, toute la duree, -26.5 dB par defaut (fade in 0.4 / out 1.2).
  - Volumes SFX REEQUILIBRES par niveau PERCU (pas un dB uniforme : la frappe clavier et les
    clics sont inaudibles au meme dB qu'un riser).
  - Les temps s'appuient sur sections (les VRAIES coupes) + les timelines GSAP des sections.
"""
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections

ROOT = pathlib.Path(__file__).resolve().parent.parent
SFX_DIR = ROOT / "assets/sfx"
MUSIC_DIR = ROOT / "assets/music"
SRC = ROOT / "renders/FINAL.mp4"
OUT = ROOT / "renders/FINAL_SFX_MUSIC.mp4"

SEC = sections.sections()
DUR = sections.DURATION


def die(msg):
    print("ERREUR :", msg)
    sys.exit(1)


def load_config():
    for name in ("brand.config.json", "brand.config.example.json"):
        p = ROOT / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    die("aucun brand.config.json ni brand.config.example.json trouve — lance /setup.")


# --- musique : depuis brand.config.json --------------------------------------------------------
CFG = load_config()
audio = CFG.get("audio") or {}
music_file = audio.get("musicFile")
music_db = audio.get("musicDb", -26.5)
if not music_file:
    die("audio.musicFile est vide dans brand.config.json — configure ta musique via /setup bloc E.")
MUSIC = MUSIC_DIR / music_file
if not MUSIC.exists():
    die(f"musique introuvable : {MUSIC.relative_to(ROOT)} (verifie audio.musicFile dans brand.config.json).")

if not SRC.exists():
    die(f"{SRC.relative_to(ROOT)} manquant — rends d'abord la video finale (etape export ffmpeg).")

# --- SFX disponibles ---------------------------------------------------------------------------
available = sorted(p.name for p in SFX_DIR.glob("*")
                   if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".aif", ".aiff"))
if not available:
    die(f"aucun SFX dans {SFX_DIR.relative_to(ROOT)} — depose tes effets (cf assets/sfx/README.md).")

# =============================================================================
# EVENTS = (fichier_sfx, start_s, volume_dB, trim|None)  -> A REMPLIR PAR L'AGENT.
# Ci-dessous : un EXEMPLE generique — un SFX de transition sur chaque debut de section
# (sauf la premiere). On alterne les SFX disponibles pour ne jamais jouer 2x le meme d'affilee.
# =============================================================================
events = []
transitions = [s["start"] for s in SEC[1:]]
for i, t in enumerate(transitions):
    events.append((available[i % len(available)], round(t, 3), -20, 0.45))

events.sort(key=lambda e: e[1])

# ---- ffmpeg : voix (FINAL.mp4) + N SFX + musique ---------------------------------------------
inputs, filters, mixin = ["-i", str(SRC)], [], ["[0:a]"]
for i, (f, start, vol, trim) in enumerate(events, start=1):
    inputs += ["-i", str(SFX_DIR / f)]
    ch = f"[{i}:a]"
    if trim:
        ch_f = (f"atrim=0:{trim},volume={vol}dB,aformat=channel_layouts=stereo:sample_rates=48000,"
                f"afade=t=out:st={max(trim - 0.06, 0):.3f}:d=0.06,adelay={int(start * 1000)}:all=1")
    else:
        ch_f = (f"volume={vol}dB,aformat=channel_layouts=stereo:sample_rates=48000,"
                f"adelay={int(start * 1000)}:all=1")
    filters.append(f"{ch}{ch_f}[e{i}]")
    mixin.append(f"[e{i}]")

mi = len(events) + 1
inputs += ["-i", str(MUSIC)]
filters.append(f"[{mi}:a]atrim=0:{DUR},volume={music_db}dB,aformat=channel_layouts=stereo:sample_rates=48000,"
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

print(f"{len(events)} SFX + musique ({music_file} @ {music_db} dB) -> {OUT.relative_to(ROOT)}")
for f, s, v, t in events:
    print(f"  {s:6.2f}  {v:>4} dB  {f}{'  (trim ' + str(t) + ')' if t else ''}")
