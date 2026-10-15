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
  Raccord (deux prises qui se touchent : une phrase partagee pour changer de cadre sur un mot) :
  aucun saut d'image, la frontiere se deduit du debut reel de la prise d'avant, a l'image pres.

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
    (10.00, 12.60, "On garde tes mots."),
    (15.20, 17.80, "On retire les silences."),
    (21.50, 24.10, "Le rythme change tout."),
]

# Pads appliques au derush (brand.config.json -> derush.padStart / padEnd).
PAD_START, PAD_END = 0.04, 0.02

# Si derush/build_derush.py existe, ses ISLANDS ecrasent la liste ci-dessus : UNE SEULE source
# de verite. Recopier les prises a la main est le meilleur moyen de les desynchroniser (une
# borne modifiee d'un cote, oubliee de l'autre -> les frontieres de section sont fausses).
_BUILD = ROOT / "derush/build_derush.py"
if _BUILD.exists():
    import ast as _ast
    _consts = {t.id: _ast.literal_eval(n.value)
               for n in _ast.parse(_BUILD.read_text(encoding="utf-8")).body
               if isinstance(n, _ast.Assign)
               for t in n.targets if isinstance(t, _ast.Name)
               and t.id in ("ISLANDS", "PAD_START", "PAD_END")}
    if "ISLANDS" in _consts:
        ISLANDS = _consts["ISLANDS"]
        PAD_START = _consts.get("PAD_START", PAD_START)
        PAD_END = _consts.get("PAD_END", PAD_END)
        print(f"prises lues depuis {_BUILD.relative_to(ROOT)} ({len(ISLANDS)} prises)")
TOL = 0.35   # fenetre de rapprochement theorique <-> detecte
RACCORD = 0.005   # deux prises qui se touchent = une prise partagee (changement de cadre sans coupe)
IMAGE = 1001 / 30000   # duree d'une image du derush (-r 30000/1001)

if not CUT.exists():
    print(f"ERREUR : {CUT.relative_to(ROOT)} introuvable.")
    print("Ce script mesure les coupes DANS le MP4 derushe : fais d'abord l'etape derush,")
    print("puis mets a jour CUT / OUT / ISLANDS en tete de ce fichier pour TON Reel.")
    sys.exit(1)

# --- bornes THEORIQUES (cumul des prises padees) -------------------------------
theo = [0.0]
for s, e, _ in ISLANDS:
    theo.append(round(theo[-1] + (e + PAD_END) - max(s - PAD_START, 0.0), 3))

# Raccords : la prise k reprend le rush la ou la prise k-1 s'arrete (derush/build_derush.py les
# monte d'un seul tenant). Pas de saut d'image a detecter : la frontiere se deduit du debut REEL
# de la prise d'avant, a l'image pres.
raccord = [False] + [abs((ISLANDS[k - 1][1] + PAD_END) - max(ISLANDS[k][0] - PAD_START, 0.0)) <= RACCORD
                     for k in range(1, len(ISLANDS))]

# --- coupes REELLES (scene change dans le fichier livre) -----------------------
proc = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", str(CUT),
     "-filter:v", "select='gt(scene,0.015)',metadata=print:file=-", "-an", "-f", "null", "-"],
    capture_output=True, encoding="utf-8", errors="replace")
detected = [float(x) for x in re.findall(r"pts_time:([\d.]+)", proc.stdout)]

dur = float(subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(CUT)],
    capture_output=True, encoding="utf-8", errors="replace").stdout.strip())

bounds, drifts = [0.0], []
for k, m in enumerate(theo[1:-1], start=1):
    if raccord[k]:
        bounds.append(round(round((bounds[-1] + theo[k] - theo[k - 1]) / IMAGE) * IMAGE, 3))
        continue
    near = [d for d in detected if abs(d - m) < TOL]
    if not near:
        raise SystemExit(f"coupe introuvable pres de {m:.3f}s : baisser le seuil scene ou verifier ISLANDS")
    d = min(near, key=lambda x: abs(x - m))
    bounds.append(round(d, 3))
    drifts.append(d - m)
bounds.append(round(dur, 3))

assert len(bounds) == len(ISLANDS) + 1, "nb de bornes != nb de prises + 1"
assert bounds == sorted(bounds), "bornes non croissantes"

takes = [{"i": i, "start": bounds[i], "end": bounds[i + 1], "text": ISLANDS[i][2]}
         for i in range(len(ISLANDS))]
for i in range(1, len(ISLANDS)):
    if raccord[i]:
        takes[i]["raccord"] = True   # suit la prise d'avant sans coupe (changement de cadre seul)
OUT.write_text(json.dumps(
    {"source": str(CUT.relative_to(ROOT)), "duration": round(dur, 3),
     "method": "scene-change detection (gt(scene,0.015)) recale sur le cumul des ISLANDS",
     "takes": takes}, ensure_ascii=False, indent=2), encoding="utf-8")

n_raccords = sum(raccord)
print(f"{len(takes)} prises, {len(drifts)} coupes" + (f" + {n_raccords} raccord(s)" if n_raccords else "")
      + f" -> {OUT.relative_to(ROOT)}")
if drifts:
    print(f"derive moyenne reel-vs-theorique : {sum(drifts)/len(drifts):+.3f}s  (max {max(drifts):+.3f}s)")
for t in takes:
    print(f"  {t['i']:>2}  {t['start']:6.3f} -> {t['end']:6.3f}   {t['text'][:52]}"
          + ("   (raccord : changement de cadre, sans coupe)" if t.get("raccord") else ""))
