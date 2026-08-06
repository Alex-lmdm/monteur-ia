#!/usr/bin/env python3
"""Transcription MOT-A-MOT du cut -> derush/<video>_words.json (timestamps absolus).

╔══════════════════════════════════════════════════════════════════════════════╗
║ A CHANGER A CHAQUE REEL : CUT (le MP4 derushe) — le reste est generique.      ║
╚══════════════════════════════════════════════════════════════════════════════╝

POURQUOI CE FICHIER EXISTE
Sans lui, tools/montage_captions.py time les sous-titres en repartissant chaque phrase
PROPORTIONNELLEMENT AU NOMBRE DE CARACTERES. Approximation qui DERIVE : les premiers chunks
durent trop et tous les suivants arrivent en retard. Ca s'entend (« le sous-titre arrive un peu
apres ma voix ») sans qu'on sache le nommer. Avec les vrais mots, chaque sous-titre demarre
PILE sur le mot qu'il affiche.

COMMENT
whisper-cli en mode mot-a-mot (-ml 1 -sow), PRISE PAR PRISE. Sur le fichier entier ce mode
hallucine ; sur des slices de 1-4 s il est fiable. Les bornes des prises viennent du meme
<video>_cuts.json que les sections et le master — une seule source de verite.

Usage : python3 tools/build_words.py
Puis relance tools/montage_captions.py : il detecte le fichier et cale tout dessus.
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections

ROOT = pathlib.Path(__file__).resolve().parent.parent

# >>> A CHANGER : le MP4 derushe (audio nettoye) de TON Reel.
CUT = ROOT / "derush/exemple_enhanced.mp4"
OUT = sections.CUTS_PATH.with_name(sections.CUTS_PATH.name.replace("_cuts.json", "_words.json"))

# Modele Whisper. `large-v3` donne les meilleurs timestamps FR ; les modeles `.en` ne marchent pas.
MODEL = pathlib.Path.home() / ".cache/hyperframes/whisper/models/ggml-large-v3.bin"

LINE = re.compile(r"\[(\d+):(\d+):([\d.]+) --> (\d+):(\d+):([\d.]+)\]\s*(.*)")


def secs(h, m, s):
    return int(h) * 3600 + int(m) * 60 + float(s)


if not CUT.exists():
    print(f"ERREUR : {CUT.relative_to(ROOT)} introuvable.")
    print("Mets a jour CUT en tete de ce fichier pour pointer sur TON cut derushe.")
    raise SystemExit(1)
if not MODEL.exists():
    print(f"ERREUR : modele Whisper introuvable ({MODEL}).")
    print("Installe-le, ou saute cette etape : montage_captions.py retombe alors sur un timing")
    print("approximatif (proportionnel au texte) — moins bien cale sur la voix.")
    raise SystemExit(1)

words = []
with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    for take in sections.TAKES:
        wav = tmp / f"t{take['i']:02d}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(take["start"]),
                        "-to", str(take["end"]), "-i", str(CUT),
                        "-ar", "16000", "-ac", "1", str(wav)], check=True)
        proc = subprocess.run(["whisper-cli", "-m", str(MODEL), "-l", "fr",
                               "-ml", "1", "-sow", "-wt", "0.01", "-np", str(wav)],
                              capture_output=True, text=True)
        for line in proc.stdout.split("\n"):
            m = LINE.match(line.strip())
            if not m:
                continue
            text = m.group(7).strip()
            if not text:
                continue
            words.append({
                "w": text,
                "start": round(take["start"] + secs(*m.group(1, 2, 3)), 3),
                "end": round(take["start"] + secs(*m.group(4, 5, 6)), 3),
                "take": take["i"],
            })

OUT.write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(words)} mots -> {OUT.relative_to(ROOT)}")
for w in words[:10]:
    print(f"  {w['start']:6.3f} -> {w['end']:6.3f}  {w['w']}")
