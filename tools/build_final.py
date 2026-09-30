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
      + renders/overlay.mov : tout le motion design + les sous-titres (alpha)
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

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "assets/video/base.mp4"
OVERLAY = ROOT / "renders/overlay.mov"
OUT = ROOT / "renders/FINAL.mp4"

SEC = sections.sections()
DUR = sections.DURATION
WINS = sections.face_windows()          # visage en split (moitie basse)
WINSFULL = sections.facefull_windows()  # visage plein ecran (sections "face")
MEDIAS = [s for s in SEC if s.get("media")]


def load_config():
    for name in ("brand.config.json", "brand.config.example.json"):
        p = ROOT / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return {}


CFG = (load_config().get("montage") or {})


def crop_from_transform(transform, top, origin=None):
    """Traduit un `transform` CSS du master en `crop=w:h:x:y` ffmpeg.

    La <video> du master est une surface plein cadre 1080x1920 transformee. Deux cas, selon
    comment le master cadre le visage (cf skill motion-design §3) :

    - SPLIT — `transform-origin: 0 0` + `translate(Tx, Ty) scale(S)`. La zone SOURCE visible
      dans la fenetre [top .. 1920] est `src_x = (0 .. 1080 - Tx) / S`,
      `src_y = (top - Ty .. 1920 - Ty) / S`.
    - PLEIN ECRAN — `scale(S)` autour d'un `transform-origin` (ox, oy). L'agrandissement se fait
      AUTOUR de ce point, donc la zone visible est decalee de `o * taille * (1 - 1/S)`.
      Ignorer l'origin donnerait un cadrage faux (visage decentre a l'export alors qu'il etait
      bon dans le studio) — c'est exactement le piege que ce script supprime.
    """
    if not transform:
        return None
    scale = re.search(r"scale\(([\d.]+)\)", transform)
    trans = re.search(r"translate\(\s*(-?[\d.]+)px\s*,\s*(-?[\d.]+)px\s*\)", transform)
    s = float(scale.group(1)) if scale else 1.0
    w = round(1080 / s)
    h = round((1920 - top) / s)

    if trans:
        tx, ty = float(trans.group(1)), float(trans.group(2))
        x = round(-tx / s)
        y = round((top - ty) / s)
    else:
        ox, oy = parse_origin(origin)
        x = round(ox * 1080 * (1 - 1 / s))
        y = round(oy * 1920 * (1 - 1 / s))

    x, y = max(x, 0), max(y, 0)
    w, h = min(w, 1080 - x), min(h, 1920 - y)
    return f"{w}:{h}:{x}:{y}"


def parse_origin(origin):
    """`transform-origin` CSS -> fractions (ox, oy). Accepte « center 34% », « 50% 34% », « 0 0 »."""
    mots = {"left": 0.0, "center": 0.5, "right": 1.0, "top": 0.0, "bottom": 1.0}
    parts = (origin or "center center").split()
    vals = []
    for i, mot in enumerate(parts[:2]):
        if mot in mots:
            vals.append(mots[mot])
        elif mot.endswith("%"):
            vals.append(float(mot[:-1]) / 100)
        else:
            vals.append(float(re.sub(r"[^\d.\-]", "", mot) or 0) / (1080 if i == 0 else 1920))
    while len(vals) < 2:
        vals.append(0.5)
    return vals[0], vals[1]


FACE_CROP = CFG.get("faceCrop") or crop_from_transform(CFG.get("splitTransform"), 920) \
    or "771:714:154:364"
FULLFACE_CROP = CFG.get("fullFaceCrop") or crop_from_transform(
    CFG.get("fullFaceTransform"), 0, CFG.get("fullFaceOrigin") or "center 34%") \
    or "771:1371:154:187"

if not BASE.exists() or not OVERLAY.exists():
    manquant = BASE if not BASE.exists() else OVERLAY
    print(f"ERREUR : {manquant.relative_to(ROOT)} introuvable.")
    print("Il faut la base derushee ET le calque rendu :")
    print("  python3 tools/build_overlay.py --render")
    raise SystemExit(1)


def probe(path):
    """(largeur, hauteur, color_transfer, duree) du flux video."""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,color_transfer,duration", "-of", "json", str(path)],
                         capture_output=True, text=True).stdout
    s = (json.loads(out or "{}").get("streams") or [{}])[0]
    return (int(s.get("width") or 0), int(s.get("height") or 0), s.get("color_transfer") or "",
            float(s.get("duration") or 0))


def same_images(hq, t):
    """PSNR d'une image de base.mp4 contre la meme image du derush reduite : > 30 dB = meme video."""
    g = "[0:v]scale=1080:1920[a];[1:v]scale=1080:1920:flags=lanczos[b];[a][b]psnr"
    err = subprocess.run(["ffmpeg", "-nostdin", "-ss", f"{t:.3f}", "-i", str(BASE), "-ss", f"{t:.3f}",
                          "-i", str(hq), "-filter_complex", g, "-frames:v", "1", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"average:(inf|[\d.]+)", err)
    return bool(m) and (m.group(1) == "inf" or float(m.group(1)) > 30)


def face_source():
    """Ou relire le visage : (fichier, facteur d'echelle vs base.mp4, raison si repli sur base)."""
    src = sections.CUTS.get("source")
    hq = ROOT / src if src else None
    if not hq or not hq.exists():
        return BASE, 1.0, f"derush pleine resolution introuvable ({src or 'aucune source dans le cuts.json'})"
    w, h, trc, dur = probe(hq)
    k = w / 1080
    if k < 1.05:
        return BASE, 1.0, None   # rush deja en 1080 : base.mp4 porte deja tout le detail
    if abs(h - 1920 * k) > 2:
        return BASE, 1.0, f"le derush ({w}x{h}) n'est pas au format 9:16 de base.mp4"
    if trc in ("arib-std-b67", "smpte2084"):
        return BASE, 1.0, "le derush est en HDR (base.mp4 est tonemappe, les couleurs differeraient)"
    if abs(dur - probe(BASE)[3]) > 0.1 or not same_images(hq, DUR / 2):
        return BASE, 1.0, f"{src} ne montre pas les memes images que base.mp4 (base.mp4 a refaire depuis ce derush ?)"
    return hq, k, None


def scale_crop(crop, k, src_w, src_h):
    """`w:h:x:y` en pixels de base.mp4 -> la meme zone dans une source k fois plus grande."""
    w, h, x, y = (round(float(v) * k) for v in crop.split(":"))
    x, y = min(max(x, 0), src_w - 2), min(max(y, 0), src_h - 2)
    return f"{min(w, src_w - x)}:{min(h, src_h - y)}:{x}:{y}"


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
r = subprocess.run(cmd, capture_output=True, text=True)
print("ffmpeg exit:", r.returncode)
if r.returncode:
    print(r.stderr[-1500:])
    raise SystemExit(1)
print(f"{OUT.relative_to(ROOT)} — {DUR}s")
print("Etape suivante : python3 tools/build_sfx.py (SFX + musique), APRES validation du montage.")
