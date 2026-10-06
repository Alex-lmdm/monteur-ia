#!/usr/bin/env python3
"""EXPORT FINAL en ffmpeg — assemble la vidéo livrable (visage NET).

╔══════════════════════════════════════════════════════════════════════════════╗
║ Rien a changer ici d'un Reel a l'autre : tout vient de tools/sections.py et   ║
║ de brand.config.json. Lance-le apres avoir rendu le calque :                  ║
║     python3 tools/build_overlay.py --render                                   ║
║     python3 tools/build_final.py                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

POURQUOI CE SCRIPT EXISTE
Le render HyperFrames RASTERISE la couche video : le visage en ressort mou. L'export final se
fait donc en ffmpeg, en recomposant les couches natives :

    fond de marque
      + le VISAGE croppe dans le DERUSH EN PLEINE RESOLUTION (moitie basse sur les sections
        "split", plein cadre sur les sections "face")
      + les B-ROLLS (sections {"media": ...}), eux aussi natifs
      + work/overlay.mov : tout le motion design + les sous-titres (alpha)
      + l'audio de base.mp4

D'OU VIENT LE VISAGE
Le visage est une petite zone agrandie : en split, ~771x714 px de base.mp4 remplissent 1080x1000.
Lu dans base.mp4 (reduit en 1080x1920), il ne garde que ~1/3 du detail du rush. Le derush, lui,
est garde en pleine resolution (ex. 1728x3072 pour une DJI) et porte les MEMES images aux MEMES
instants (base.mp4 n'en est que la reduction) : on y relit la meme zone, 1,6x plus de pixels, et
le visage garde ~80 % du detail. Le fichier est celui que <cut>_cuts.json designe ("source").
Si ce derush manque, est deja en 1080, est en HDR ou ne montre pas les memes images que
base.mp4, on revient sur base.mp4 (visage moins net, mais juste) et on dit pourquoi.

Le crop du visage DOIT correspondre exactement au transform CSS du master, sinon le cadrage est
faux a l'export alors qu'il etait bon dans le studio. Ce script le lit dans brand.config.json
(montage.faceCrop / montage.fullFaceCrop, calibres par /setup, en pixels de base.mp4) et, s'ils
sont absents, le CALCULE depuis le transform avec la formule du skill — plus personne n'a a le
retrouver a la main. Il le met ensuite a l'echelle du derush.
"""
import json
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import brand_style
import sections
from lieux import MAISON  # réglages du client, partagés par tous les Reels

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "assets/video/base.mp4"
OVERLAY = ROOT / "work/overlay.mov"
OUT = ROOT / "exports/FINAL.mp4"

SEC = sections.sections()
DUR = sections.DURATION
WINS = sections.face_windows()          # visage en split (moitie basse)
WINSFULL = sections.facefull_windows()  # visage plein ecran (sections "face")
MEDIAS = [s for s in SEC if s.get("media")]


def load_config():
    for name in ("brand.config.json", "brand.config.example.json"):
        p = MAISON / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return {}


CFG = (load_config().get("montage") or {})


# Le calcul du cadrage est partagé avec tools/build_faces.py (export natif) : même zone du rush.
from cadrage import crops, face_source as _face_source, scale_crop  # noqa: E402

FACE_CROP, FULLFACE_CROP = crops(CFG)

if not BASE.exists() or not OVERLAY.exists():
    manquant = BASE if not BASE.exists() else OVERLAY
    print(f"ERREUR : {manquant.relative_to(ROOT)} introuvable.")
    print("Il faut la base derushee ET le calque rendu :")
    print("  python3 tools/build_overlay.py --render")
    raise SystemExit(1)


def face_source():
    """Ou relire le visage : (fichier, facteur d'echelle vs base.mp4, raison si repli sur base)."""
    return _face_source(ROOT, BASE, sections.CUTS, DUR)


def enable(wins):
    return "+".join(f"between(t,{a:.3f},{a + d:.3f})" for a, d in wins)


FACE_SRC, K, REPLI = face_source()
FW, FH = round(1080 * K), round(1920 * K)
FACE_CROP_SRC = scale_crop(FACE_CROP, K, FW, FH)
FULLFACE_CROP_SRC = scale_crop(FULLFACE_CROP, K, FW, FH)

# Fond de l'export : resolu par brand_style (preset + brand.config.json), jamais en dur.
BG = brand_style.style().bg_hex
parts = [f"color=c=0x{BG}:s=1080x1920:r=30000/1001:d={DUR}[bg];"]

# --- le visage, croppe dans le derush pleine resolution (sinon base.mp4) --------------------
# L'entree du visage est la DERNIERE (apres les b-rolls) ; base.mp4 (entree 0) fournit le son.
fin = f"[{2 + len(MEDIAS)}:v]"
if WINS and WINSFULL:
    parts += [
        f"{fin}split=2[b0][b1];",
        f"[b0]crop={FACE_CROP_SRC},scale=1080:1000:flags=lanczos[face];",
        f"[b1]crop={FULLFACE_CROP_SRC},scale=1080:1920:flags=lanczos[facefull];",
        f"[bg][face]overlay=0:920:enable='{enable(WINS)}'[v1];",
        f"[v1][facefull]overlay=0:0:enable='{enable(WINSFULL)}'[v2];",
    ]
    last = "[v2]"
elif WINSFULL:
    parts += [f"{fin}crop={FULLFACE_CROP_SRC},scale=1080:1920:flags=lanczos[facefull];",
              f"[bg][facefull]overlay=0:0:enable='{enable(WINSFULL)}'[v1];"]
    last = "[v1]"
else:
    parts += [f"{fin}crop={FACE_CROP_SRC},scale=1080:1000:flags=lanczos[face];",
              f"[bg][face]overlay=0:920:enable='{enable(WINS)}'[v1];"]
    last = "[v1]"

# --- les b-rolls : couche video NATIVE, sous le calque (pour que les sous-titres passent dessus)
inputs_media = []
for n, s in enumerate(MEDIAS):
    inputs_media += ["-i", str(ROOT / "assets/video" / s["media"])]
    src = f"[{2 + n}:v]"
    parts.append(f"{src}setpts=PTS+{s['start']:.3f}/TB[m{n}];")
    parts.append(f"{last}[m{n}]overlay=0:0:enable='between(t,{s['start']:.3f},{s['end']:.3f})'[mv{n}];")
    last = f"[mv{n}]"

# --- le calque (motion + sous-titres) par-dessus tout ----------------------------------------
parts.append(f"{last}[1:v]overlay=0:0[vout]")

cmd = (["ffmpeg", "-y", "-v", "error", "-i", str(BASE), "-i", str(OVERLAY)] + inputs_media +
       ["-i", str(FACE_SRC),
        "-filter_complex", "".join(parts), "-map", "[vout]", "-map", "0:a",
        "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)])

print(f"visage lu dans          : {FACE_SRC.relative_to(ROOT)} ({FW}x{FH})")
if REPLI:
    print(f"  ⚠️ visage moins net (lu en 1080) : {REPLI}")
print(f"crop visage split       : {FACE_CROP}  -> {FACE_CROP_SRC} dans la source")
if WINSFULL:
    print(f"crop visage plein ecran : {FULLFACE_CROP}  -> {FULLFACE_CROP_SRC} dans la source")
if MEDIAS:
    print(f"b-rolls natifs          : {', '.join(s['media'] for s in MEDIAS)}")
print("composite ...")
r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
print("ffmpeg exit:", r.returncode)
if r.returncode:
    print(r.stderr[-1500:])
    raise SystemExit(1)
print(f"{OUT.relative_to(ROOT)} : {DUR}s")
print("Etape suivante : python3 tools/build_sfx.py (SFX + musique), APRES validation du montage.")
