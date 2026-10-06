#!/usr/bin/env python3
"""CADRAGE DU VISAGE : source unique du calcul « transform CSS du master -> zone du rush ».

Partagé par tools/build_faces.py (prépare les vidéos du visage déjà cadrées, en pleine
résolution, pour l'export natif HyperFrames) et tools/build_final.py (ancien export ffmpeg,
gardé en secours). Les deux lisent donc EXACTEMENT la même zone du rush : impossible que le
visage soit cadré d'une façon dans l'un et d'une autre dans l'autre.

Les transforms viennent de brand.config.json -> montage.splitTransform / fullFaceTransform /
fullFaceOrigin (calibrés par /setup), ou des crops explicites montage.faceCrop / fullFaceCrop.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

# Replis livrés : les mêmes que build_master.py (DEFAULT_SPLIT_TRANSFORM, DEFAULT_FULLFACE_*).
DEFAULT_FACE_CROP = "771:714:154:364"
DEFAULT_FULLFACE_CROP = "771:1371:154:187"


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


def crop_from_transform(transform, top, origin=None):
    """Traduit un `transform` CSS du master en `crop=w:h:x:y` ffmpeg (pixels de base.mp4).

    La <video> du master est une surface plein cadre 1080x1920 transformée. Deux cas :

    - SPLIT : `transform-origin: 0 0` + `translate(Tx, Ty) scale(S)`. La zone SOURCE visible
      dans la fenêtre [top .. 1920] est `src_x = (0 .. 1080 - Tx) / S`,
      `src_y = (top - Ty .. 1920 - Ty) / S`.
    - PLEIN ÉCRAN : `scale(S)` autour d'un `transform-origin` (ox, oy). L'agrandissement se fait
      AUTOUR de ce point, donc la zone visible est décalée de `o * taille * (1 - 1/S)`.
      Ignorer l'origin donnerait un visage décentré à l'export alors qu'il était bon au studio.
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


def crops(montage: dict) -> tuple[str, str]:
    """(crop split, crop plein écran) en pixels de base.mp4, depuis le bloc `montage` des réglages."""
    face = montage.get("faceCrop") or crop_from_transform(montage.get("splitTransform"), 920) \
        or DEFAULT_FACE_CROP
    full = montage.get("fullFaceCrop") or crop_from_transform(
        montage.get("fullFaceTransform"), 0, montage.get("fullFaceOrigin") or "center 34%") \
        or DEFAULT_FULLFACE_CROP
    return face, full


def probe(path):
    """(largeur, hauteur, color_transfer, durée) du flux vidéo."""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,color_transfer,duration", "-of", "json", str(path)],
                         capture_output=True, encoding="utf-8", errors="replace").stdout
    s = (json.loads(out or "{}").get("streams") or [{}])[0]
    return (int(s.get("width") or 0), int(s.get("height") or 0), s.get("color_transfer") or "",
            float(s.get("duration") or 0))


def same_images(base, hq, t):
    """PSNR d'une image de base.mp4 contre la même image du dérush réduite : > 30 dB = même vidéo."""
    g = "[0:v]scale=1080:1920[a];[1:v]scale=1080:1920:flags=lanczos[b];[a][b]psnr"
    err = subprocess.run(["ffmpeg", "-nostdin", "-ss", f"{t:.3f}", "-i", str(base), "-ss", f"{t:.3f}",
                          "-i", str(hq), "-filter_complex", g, "-frames:v", "1", "-f", "null", "-"],
                         capture_output=True, encoding="utf-8", errors="replace").stderr
    m = re.search(r"average:(inf|[\d.]+)", err)
    return bool(m) and (m.group(1) == "inf" or float(m.group(1)) > 30)


def face_source(root: Path, base: Path, cuts: dict, duree: float):
    """Où relire le visage : (fichier, facteur d'échelle vs base.mp4, raison si repli sur base)."""
    src = cuts.get("source")
    hq = root / src if src else None
    if not hq or not hq.exists():
        return base, 1.0, f"dérush pleine résolution introuvable ({src or 'aucune source dans le cuts.json'})"
    w, h, trc, dur = probe(hq)
    k = w / 1080
    if k < 1.05:
        return base, 1.0, None   # rush déjà en 1080 : base.mp4 porte déjà tout le détail
    if abs(h - 1920 * k) > 2:
        return base, 1.0, f"le dérush ({w}x{h}) n'est pas au format 9:16 de base.mp4"
    if trc in ("arib-std-b67", "smpte2084"):
        return base, 1.0, "le dérush est en HDR (base.mp4 est tonemappé, les couleurs différeraient)"
    if abs(dur - probe(base)[3]) > 0.1 or not same_images(base, hq, duree / 2):
        return base, 1.0, f"{src} ne montre pas les mêmes images que base.mp4 (base.mp4 à refaire depuis ce dérush ?)"
    return hq, k, None


def scale_crop(crop, k, src_w, src_h):
    """`w:h:x:y` en pixels de base.mp4 -> la même zone dans une source k fois plus grande."""
    w, h, x, y = (round(float(v) * k) for v in crop.split(":"))
    x, y = min(max(x, 0), src_w - 2), min(max(y, 0), src_h - 2)
    return f"{min(w, src_w - x)}:{min(h, src_h - y)}:{x}:{y}"
