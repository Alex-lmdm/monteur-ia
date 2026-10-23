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


def _longueur(valeur: str, taille: float) -> float:
    """« -25px », « -25 », « 10% » (de la taille de la vidéo) -> pixels."""
    v = valeur.strip()
    if v.endswith("%"):
        return float(v[:-1]) / 100 * taille
    return float(re.sub(r"px$", "", v) or 0)


def lire_transform(transform) -> tuple[tuple[float, float], tuple[float, float]]:
    """`transform` CSS -> ((Sx, Sy), (Tx, Ty)) : un point p de la vidéo va en S·p + T (avant
    l'origine). Lit translate(x[, y]), translateX, translateY, scale(s[, sy]), scaleX, scaleY, dans
    l'ordre écrit (« scale(2) translate(10px, 0) » décale de 20 px à l'écran). Le reste est ignoré."""
    sx, sy, tx, ty = 1.0, 1.0, 0.0, 0.0
    for nom, args in re.findall(r"(translateX|translateY|translate|scaleX|scaleY|scale)\(([^)]*)\)", transform or ""):
        vals = [a for a in re.split(r"[\s,]+", args.strip()) if a]
        if not vals:
            continue
        if nom == "translate":
            dx, dy = _longueur(vals[0], 1080), _longueur(vals[1], 1920) if len(vals) > 1 else 0.0
        elif nom in ("translateX", "translateY"):
            dx, dy = (_longueur(vals[0], 1080), 0.0) if nom == "translateX" else (0.0, _longueur(vals[0], 1920))
        else:
            fx = float(vals[0]) if nom != "scaleY" else 1.0
            fy = (float(vals[1]) if len(vals) > 1 else fx) if nom == "scale" else (float(vals[0]) if nom == "scaleY" else 1.0)
            sx, sy = sx * fx, sy * fy
            continue
        tx, ty = tx + sx * dx, ty + sy * dy
    return (sx, sy), (tx, ty)


def crop_from_transform(transform, top, origin=None):
    """Traduit un `transform` CSS du master en `crop=w:h:x:y` ffmpeg (pixels de base.mp4).

    La <video> du master est une surface plein cadre 1080x1920 transformée autour de son
    `transform-origin` o : un point p de la vidéo s'affiche en o + T + S·(p − o). La zone SOURCE
    visible dans la fenêtre [0..1080] x [top..1920] est donc p = o + (écran − o − T) / S :
    - SPLIT : origin `0 0` + `translate(Tx, Ty) scale(S)` -> src_x = −Tx / S, src_y = (top − Ty) / S ;
    - PLEIN ÉCRAN : `scale(S)` autour de `center 34%` -> zone décalée de o · (1 − 1/S), plus la
      translation éventuelle (`translateY(-25px) scale(1.75)` remonte la tête de 25 px).
    Ignorer l'origin ou une translation donnerait un visage décalé à l'export alors qu'il était
    bon au studio.
    """
    if not transform:
        return None
    (sx, sy), (tx, ty) = lire_transform(transform)
    if sx <= 0 or sy <= 0:
        return None
    fx, fy = parse_origin(origin)
    ox, oy = fx * 1080, fy * 1920
    w = round(1080 / sx)
    h = round((1920 - top) / sy)
    x = round(ox + (0 - ox - tx) / sx)
    y = round(oy + (top - oy - ty) / sy)

    x, y = max(x, 0), max(y, 0)
    w, h = min(w, 1080 - x), min(h, 1920 - y)
    return f"{w}:{h}:{x}:{y}"


def crops(montage: dict) -> tuple[str, str]:
    """(crop split, crop plein écran) en pixels de base.mp4, depuis le bloc `montage` des réglages.
    Origines : celles du master (tools/build_master.py), `0 0` en split, fullFaceOrigin en plein écran."""
    face = montage.get("faceCrop") or crop_from_transform(montage.get("splitTransform"), 920, "0 0") \
        or DEFAULT_FACE_CROP
    full = montage.get("fullFaceCrop") or crop_from_transform(
        montage.get("fullFaceTransform"), 0, montage.get("fullFaceOrigin") or "center 34%") \
        or DEFAULT_FULLFACE_CROP
    return face, full


def crop_decor(montage: dict):
    """Zone du rush posée sous les cartes (sections « decor »), en pixels de base.mp4 ; None = la vidéo
    entière, telle que filmée. Origine : celle du master (montage.decorOrigin, « center top » par défaut)."""
    if montage.get("decorCrop"):
        return montage["decorCrop"]
    transform = montage.get("decorTransform")
    if not transform or transform.strip() == "none":
        return None
    return crop_from_transform(transform, 0, montage.get("decorOrigin") or "center top")


def crop_detoure(montage: dict):
    """Zone du rush à détourer (sections « detoure »), en pixels de base.mp4 ; None = la vidéo entière.
    Mêmes règles que crop_decor, avec montage.detoureTransform / detoureOrigin / detoureCrop."""
    if montage.get("detoureCrop"):
        return montage["detoureCrop"]
    transform = montage.get("detoureTransform")
    if not transform or transform.strip() == "none":
        return None
    return crop_from_transform(transform, 0, montage.get("detoureOrigin") or "center top")


# --- zoom par section ---------------------------------------------------------------------------
# Une section « decor », « face » ou « split » peut se montrer plus serrée que le cadrage du Reel :
# ("s3", "decor", [3], {"zoom": 1.25}) dans la table LAYOUT de tools/sections.py, et en option
# {"zoomOrigin": "center 30%"} (le point qui reste fixe, en général les yeux). Chaque niveau de zoom
# a sa propre vidéo pré-cadrée en pleine résolution (tools/build_faces.py) : le visage reste net.
# Zoom PROGRESSIF : {"zoom": [1.25, 1], "zoomDuree": 0.8} part de 1.25 au début de la section et
# arrive à 1 en 0,8 s. La vidéo est pré-cadrée au plus large des deux, le navigateur l'agrandit
# pendant le mouvement (un léger flou de bougé, invisible ; 1,3 au plus d'écart). Sections « decor » et
# « face » seulement : en écran partagé, le zoom est sec.
ZOOM_ORIGIN = "center 30%"
ZOOM_FORMATS = ("decor", "face", "split")
COPIE = {"decor": "decor", "face": "plein", "split": "split"}


def zoom_crop(crop, zoom: float, origin=None, base=(1080, 1920)):
    """La zone `crop` (w:h:x:y, ou None = l'image entière) resserrée `zoom` fois autour de `origin`
    (fractions de la zone, « center 30% » par défaut). Renvoie (zone, ramenée_dans_l_image)."""
    w, h, x, y = (float(v) for v in crop.split(":")) if crop else (*base, 0.0, 0.0)
    fx, fy = parse_origin(origin or ZOOM_ORIGIN)
    ox, oy = x + fx * w, y + fy * h
    nw, nh = w / zoom, h / zoom
    nx, ny = ox - fx * nw, oy - fy * nh
    bw, bh = base
    ajuste = nw > bw + 0.5 or nh > bh + 0.5 or nx < -0.5 or ny < -0.5 or nx + nw > bw + 0.5 or ny + nh > bh + 0.5
    nw, nh = min(nw, bw), min(nh, bh)
    nx, ny = min(max(nx, 0), bw - nw), min(max(ny, 0), bh - nh)
    return f"{round(nw)}:{round(nh)}:{round(nx)}:{round(ny)}", ajuste


def _nombre(v, mini, maxi):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return round(v, 3) if mini <= v <= maxi else None


def _zoom_de(entree, fmt: str = "decor"):
    """(zoom, origine) d'une ligne de LAYOUT ; zoom = un nombre, ou (départ, arrivée, durée)."""
    opts = (entree[3] if len(entree) > 3 else None) or {}
    brut = opts.get("zoom") or 1
    if isinstance(brut, (list, tuple)) and fmt == "split":
        raise SystemExit(f"ERREUR : section {entree[0]} : zoom progressif en écran partagé impossible "
                         "(sections decor et face seulement) : un zoom sec, {\"zoom\": 1.15}.")
    if isinstance(brut, (list, tuple)):
        ab = [_nombre(v, 0.5, 3) for v in brut]
        duree = _nombre(opts.get("zoomDuree", 0.8), 0.1, 5)
        if len(ab) != 2 or None in ab or duree is None or max(ab) / min(ab) > 1.3 + 1e-9:
            raise SystemExit(f"ERREUR : section {entree[0]} : zoom progressif {brut!r} invalide ([départ, arrivée] entre "
                             "0.5 et 3, 1,3 fois d'écart au plus ; zoomDuree entre 0.1 et 5 s).")
        z = (ab[0], ab[1], duree) if ab[0] != ab[1] else ab[0]
    else:
        z = _nombre(brut, 0.5, 3)
        if z is None:
            raise SystemExit(f"ERREUR : section {entree[0]} : zoom {brut!r} invalide (un nombre entre 0.5 et 3, "
                             "1.25 = un quart plus serré).")
    return z, str(opts.get("zoomOrigin") or ZOOM_ORIGIN)


def niveau(z) -> tuple[float, str]:
    """(zoom de la vidéo pré-cadrée, origine) : le plus large des deux pour un zoom progressif."""
    spec, origine = z
    return (min(spec[0], spec[1]) if isinstance(spec, tuple) else spec), origine


def fenetres_zoom(sec, fmt: str):
    """Fenêtres d'un format, avec le zoom de chaque section : [(début, durée, (zoom, origine))].
    Deux sections contiguës ne se fusionnent qu'à zoom fixe égal (un zoom progressif part du début
    de SA section). Lit la table LAYOUT, donc marche aussi avec le tools/sections.py d'un Reel plus
    ancien (l'option y est simplement ignorée jusqu'ici)."""
    wins = []
    for s, entree in zip(sec.sections(), sec.LAYOUT):
        if s["fmt"] != fmt:
            continue
        z = _zoom_de(entree, fmt) if fmt in ZOOM_FORMATS else (1.0, ZOOM_ORIGIN)
        if wins and abs(wins[-1][1] - s["start"]) < 1e-6 and wins[-1][2] == z and not isinstance(z[0], tuple):
            wins[-1] = (wins[-1][0], s["end"], z)
        else:
            wins.append((s["start"], s["end"], z))
    return [(round(a, 3), round(b - a, 3), z) for a, b, z in wins]


def niveaux_zoom(fenetres) -> list:
    """Les niveaux de vidéo pré-cadrée différents de 1, dans un ordre stable : le n-ième a sa vidéo `-zoom-<n>`."""
    vus = []
    for _, _, z in fenetres:
        n = niveau(z)
        if n[0] != 1 and n not in vus:
            vus.append(n)
    return vus


def copie_zoom(fmt: str, n: int) -> str:
    """Chemin (depuis le Reel) de la vidéo pré-cadrée du n-ième zoom d'un format."""
    return f"assets/video/visage-{COPIE[fmt]}-zoom-{n}.mp4"


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
