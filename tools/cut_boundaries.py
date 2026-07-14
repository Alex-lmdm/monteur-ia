#!/usr/bin/env python3
"""Mesure les VRAIS points de coupe du derush et les ecrit dans <video>_cuts.json.

╔══════════════════════════════════════════════════════════════════════════════╗
║ CE FICHIER EST ADAPTE A CHAQUE REEL :                                          ║
║  - CUT / OUT  : le MP4 derushe (audio nettoye) de TON Reel + le json de sortie.║
║  - ISLANDS    : les prises gardees au derush (recopiees de build_derush.py),   ║
║    bornes dans le RUSH D'ORIGINE + texte de la prise.                          ║
║ La demo pointe sur derush/exemple_enhanced.mp4 (3 prises) — le json livre      ║
║ (derush/exemple_cuts.json) a ete produit avec ces valeurs.                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

POURQUOI :
  Si les frontieres de section du montage sont prises dans le timeline.json issu de la
  RE-TRANSCRIPTION Whisper du cut, elles tombent ~0.1-0.25 s TROP TOT (un debut de segment
  Whisper englobe le souffle/silence qui precede la parole). Resultat : la fenetre du visage
  s'ouvre AVANT le jump-cut -> on voit la fin de la prise precedente.

  S'ajoute une derive d'encodage : le concat ffmpeg arrondit chaque prise a la frame, donc les
  bornes REELLES du fichier livre derivent de quelques centiemes par rapport aux bornes
  theoriques (cumul des ISLANDS), et la derive grandit le long de la timeline.

COMMENT :
  Les jump-cuts sont des changements de plan -> `select=gt(scene,X)` les detecte a la frame pres,
  directement dans le fichier livre. On croise avec les bornes theoriques (cumul des ISLANDS) pour
  s'assurer qu'on a bien N-1 coupes et zero faux positif.

Sortie = LA source de verite des frontieres de section (montage) ET des bornes de phrase
(sous-titres) — consommee par tools/sections.py.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# >>> A CHANGER A CHAQUE NOUVEAU REEL : le cut livre (audio nettoye) et le json de sortie.
CUT = ROOT / "derush/exemple_enhanced.mp4"
OUT = ROOT / "derush/exemple_cuts.json"

# >>> A REMPLIR A CHAQUE NOUVEAU REEL : les prises gardees (identiques a celles du derush),
#     bornes dans le RUSH D'ORIGINE + texte lu. DEMO : 3 prises fictives de ~2.6 s.
ISLANDS = [
    (10.00, 12.60, "Voici une section témoin."),
    (15.20, 17.80, "Duplique ce fichier pour la tienne."),
    (21.50, 24.10, "Garde les invariants un à sept."),
]

# Pads appliques au derush (brand.config.json -> derush.padStart / padEnd).
PAD_START, PAD_END = 0.04, 0.02
TOL = 0.35   # fenetre de rapprochement theorique <-> detecte

if not CUT.exists():
    print(f"ERREUR : {CUT.relative_to(ROOT)} introuvable.")
    print("Ce script mesure les coupes DANS le MP4 derushe : fais d'abord l'etape derush,")
    print("puis mets a jour CUT / OUT / ISLANDS en tete de ce fichier pour TON Reel.")
    sys.exit(1)

# --- bornes THEORIQUES (cumul des prises padees) -------------------------------
theo = [0.0]
for s, e, _ in ISLANDS:
    theo.append(round(theo[-1] + (e + PAD_END) - (s - PAD_START), 3))

# --- coupes REELLES (scene change dans le fichier livre) -----------------------
proc = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", str(CUT),
     "-filter:v", "select='gt(scene,0.015)',metadata=print:file=-", "-an", "-f", "null", "-"],
    capture_output=True, text=True)
detected = [float(x) for x in re.findall(r"pts_time:([\d.]+)", proc.stdout)]

dur = float(subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(CUT)],
    capture_output=True, text=True).stdout.strip())

bounds, drifts = [0.0], []
for m in theo[1:-1]:
    near = [d for d in detected if abs(d - m) < TOL]
    if not near:
        raise SystemExit(f"coupe introuvable pres de {m:.3f}s — baisser le seuil scene ou verifier ISLANDS")
    d = min(near, key=lambda x: abs(x - m))
    bounds.append(round(d, 3))
    drifts.append(d - m)
bounds.append(round(dur, 3))

assert len(bounds) == len(ISLANDS) + 1, "nb de bornes != nb de prises + 1"
assert bounds == sorted(bounds), "bornes non croissantes"

takes = [{"i": i, "start": bounds[i], "end": bounds[i + 1], "text": ISLANDS[i][2]}
         for i in range(len(ISLANDS))]
OUT.write_text(json.dumps(
    {"source": str(CUT.relative_to(ROOT)), "duration": round(dur, 3),
     "method": "scene-change detection (gt(scene,0.015)) recale sur le cumul des ISLANDS",
     "takes": takes}, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"{len(takes)} prises, {len(drifts)} coupes -> {OUT.relative_to(ROOT)}")
print(f"derive moyenne reel-vs-theorique : {sum(drifts)/len(drifts):+.3f}s  (max {max(drifts):+.3f}s)")
for t in takes:
    print(f"  {t['i']:>2}  {t['start']:6.3f} -> {t['end']:6.3f}   {t['text'][:52]}")
