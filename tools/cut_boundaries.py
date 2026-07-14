#!/usr/bin/env python3
"""Mesure les VRAIS points de coupe du derush et les ecrit dans <cut>_cuts.json.

POURQUOI (bug corrige le 2026-07-14) :
  Les frontieres de section du montage etaient prises dans le timeline.json issu de la
  RE-TRANSCRIPTION Whisper du cut. Or un debut de segment Whisper tombe ~0.1-0.25 s TROP TOT
  (il englobe le souffle/silence qui precede la parole). Resultat : la fenetre du visage
  s'ouvrait AVANT le jump-cut -> on voyait la fin de la prise precedente (Alex regarde ailleurs).

  S'ajoute une derive d'encodage : le concat ffmpeg arrondit chaque prise a la frame, donc les
  bornes REELLES du fichier sont ~+0.07 s en moyenne apres les bornes theoriques (cumul des
  ISLANDS de build_derush.py), et la derive grandit le long de la timeline (+0.12 s a la fin).

COMMENT :
  Les jump-cuts sont des changements de plan -> `select=gt(scene,X)` les detecte a la frame pres,
  directement dans le fichier livre. On croise avec les bornes theoriques (cumul des ISLANDS) pour
  s'assurer qu'on a bien N-1 coupes et zero faux positif.

Sortie = LA source de verite des frontieres de section (montage) ET des bornes de phrase (sous-titres).
"""
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
DER = ROOT / "derush/2026-07-14_codes-claude"
CUT = DER / "codes_claude_enhanced.mp4"
OUT = DER / "codes_claude_cuts.json"

# Les prises gardees (identiques a build_derush.py) : bornes dans le RUSH d'origine.
ISLANDS = [
    (44.27, 46.21, "Sept codes secrets à utiliser sur Claude."),
    (50.45, 52.17, "Numéro un, slash grill."),
    (54.15, 58.99, "Tu le mets à la fin de ta demande et Claude t'interroge d'abord sur tout ce qui lui manque, avant d'écrire une seule ligne."),
    (60.96, 62.78, "Numéro deux, slash devil."),
    (64.81, 68.68, "Claude arrête de te flatter et attaque ton idée avec les meilleurs arguments contre toi."),
    (71.28, 73.02, "Numéro trois, slash brief."),
    (76.81, 79.33, "Une réponse en trois lignes maximum. Fini les pavés."),
    (80.77, 82.55, "Numéro quatre, slash roast."),
    (87.35, 91.01, "Par défaut, Claude trouve tout génial. Là, il te dit vraiment ce qu'il trouve mauvais."),
    (94.47, 96.21, "Numéro cinq, slash steal."),
    (98.52, 103.45, "Tu colles une pub ou un email qui a cartonné, et il te ressort les mécaniques exactes pour les réutiliser chez toi."),
    (105.56, 107.19, "Numéro six, slash ghost."),
    (109.00, 113.59, "Il traque tout ce qui sonne IA dans ton texte. Les tirets longs. Les formules toutes faites. Et il réécrit."),
    (117.08, 119.23, "Et numéro sept, slash premortem."),
    (121.44, 125.88, "Claude imagine que ton projet a échoué dans six mois, et il te liste toutes les raisons possibles."),
    (126.10, 127.57, "Tu vois les problèmes avant de les vivre."),
    (144.53, 145.77, "Et si t'en veux neuf autres,"),
    (147.08, 148.08, "commente CODES"),
    (153.01, 155.30, "et je t'envoie la liste complète, directement en DM."),
]
PAD_START, PAD_END = 0.04, 0.02
TOL = 0.35   # fenetre de rapprochement theorique <-> detecte

# --- bornes THEORIQUES (cumul des prises padee) -------------------------------
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
     "takes": takes}, ensure_ascii=False, indent=2))

print(f"{len(takes)} prises, {len(drifts)} coupes -> {OUT.relative_to(ROOT)}")
print(f"derive moyenne reel-vs-theorique : {sum(drifts)/len(drifts):+.3f}s  (max {max(drifts):+.3f}s)")
for t in takes:
    print(f"  {t['i']:>2}  {t['start']:6.3f} -> {t['end']:6.3f}   {t['text'][:52]}")
