#!/usr/bin/env python3
"""FOND DÉTOURÉ (kit du style n°03 « Liste de conseils ») : prépare la vidéo posée sous les cartes
des sections « decor » marquées {"detoure": True} dans tools/sections.py.

Le cadrage détouré : fond uni du style (visual.bg), la vidéo filmée dans une FENÊTRE ARRONDIE en
bas de l'écran (décor filmé compris), et la tête de la personne qui DÉPASSE au-dessus du bord de la
fenêtre, détourée sur le fond. Monteur IA n'a pas ce cadrage : il se prépare ici, en ffmpeg, dans
la même vidéo que les sections « decor » (assets/video/visage-decor.mp4), puis le master le pose à
l'échelle 1 comme d'habitude. Les autres sections « decor » (cartes numérotées en plein visage)
gardent le zoom de montage.decorTransform.

Ordre, depuis le dossier du Reel, après tout dérush ou changement de cadrage :
    python3 tools/build_faces.py
    python3 tools/fond_detoure.py          # détourage local (1re fois : quelques minutes), puis assemblage
    python3 tools/build_master.py --write

Le détourage se fait en local, gratuitement, par `npx hyperframes remove-background` (modèle
u2net_human_seg ; téléchargé une fois par HyperFrames au premier usage) sur assets/video/base.mp4 ;
le résultat (work/detoure-matte.mov) est gardé et réutilisé. Rien n'est généré par IA : ce sont les
pixels de la vidéo du client, seulement découpés.

Réglages (constantes ci-dessous, en pixels 1080x1920, relevés sur l'original du style) :
  FENETRE   : x, haut, largeur, rayon des coins de la fenêtre (elle descend jusqu'en bas) ;
  TETE_HAUT : hauteur visée du haut de la tête (fraction de 1920) ;
  DEBORD    : marge sous le haut de la fenêtre où la découpe se fond dans la fenêtre.
L'échelle de la personne se calcule : la vidéo couvre au moins la largeur de la fenêtre, et le haut
de sa tête (mesuré sur la découpe) tombe à TETE_HAUT.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections  # noqa: E402
from cadrage import crop_decor, face_source, scale_crop  # noqa: E402
from lieux import config  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "assets/video/base.mp4"
OUT = ROOT / "assets/video/visage-decor.mp4"
MATTE = ROOT / "work/detoure-matte.mov"
MASQUES = ROOT / "work/detoure"

FENETRE = (86, 1145, 908, 56)   # x, haut, largeur, rayon : la fenêtre arrondie (original : 8 % de marge, haut à 60 %)
TETE_HAUT = 0.495                # haut de la tête à 49,5 % de la hauteur (original : 49 à 50 %)
DEBORD = 40                      # px sous le bord de la fenêtre où la découpe rejoint la fenêtre
ENCODE = ["-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart"]


def run(cmd: list[str], quoi: str) -> str:
    r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr[-2000:])
        sys.exit(f"ERREUR : {quoi}.")
    return r.stdout


def fenetres_detourees() -> list[tuple[float, float]]:
    ids = {e[0] for e in sections.LAYOUT if len(e) > 3 and (e[3] or {}).get("detoure")}
    out = []
    for s in sections.sections():
        if s["id"] in ids:
            if s["fmt"] != "decor":
                sys.exit(f"ERREUR : {s['id']} est marquée detoure mais n'est pas une section « decor ».")
            if out and abs(out[-1][1] - s["start"]) < 1e-6:
                out[-1] = (out[-1][0], s["end"])
            else:
                out.append((s["start"], s["end"]))
    return out


def matte() -> None:
    if MATTE.exists() and MATTE.stat().st_mtime >= BASE.stat().st_mtime:
        print(f"• découpe déjà faite : {MATTE.relative_to(ROOT)}")
        return
    print("• découpe de la personne (npx hyperframes remove-background, en local)…")
    MATTE.parent.mkdir(exist_ok=True)
    run(["npx", "hyperframes", "remove-background", str(BASE), "-o", str(MATTE)], "la découpe a échoué")


def haut_de_tete() -> float:
    """Haut de la tête dans base.mp4 (px, sur 1920) : médiane, sur 24 images, de la 1re ligne où la
    découpe couvre au moins 2 % de la largeur (évite un cheveu ou un reste isolé)."""
    from PIL import Image
    import io
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(MATTE)],
                    "durée de la découpe").strip())
    hauts = []
    for i in range(24):
        t = dur * (i + 0.5) / 24
        png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(MATTE), "-frames:v", "1",
                              "-vf", "alphaextract,scale=270:480", "-f", "image2pipe", "-vcodec", "png", "-"],
                             capture_output=True).stdout
        im = Image.open(io.BytesIO(png)).convert("L")
        w, h = im.size
        px = im.load()
        for y in range(h):
            if sum(1 for x in range(w) if px[x, y] > 128) >= 0.02 * w:
                hauts.append(y / h * 1920)
                break
    if not hauts:
        sys.exit("ERREUR : personne introuvable dans la découpe (vidéo sans personne ?).")
    hauts.sort()
    return hauts[len(hauts) // 2]


def masques() -> tuple[pathlib.Path, pathlib.Path]:
    """Fenêtre arrondie (blanc = fenêtre) et zone de la tête (blanc au-dessus du bord + DEBORD, fondu)."""
    from PIL import Image, ImageDraw
    MASQUES.mkdir(parents=True, exist_ok=True)
    x, haut, larg, rayon = FENETRE
    fen = Image.new("L", (1080, 1920), 0)
    ImageDraw.Draw(fen).rounded_rectangle((x, haut, x + larg, 1920 + rayon), radius=rayon, fill=255)
    tete = Image.new("L", (1080, 1920), 0)
    d = ImageDraw.Draw(tete)
    d.rectangle((0, 0, 1080, haut), fill=255)
    for k in range(DEBORD):
        d.line((0, haut + k, 1080, haut + k), fill=round(255 * (1 - k / DEBORD)))
    pf, pt = MASQUES / "fenetre.png", MASQUES / "tete.png"
    fen.save(pf)
    tete.save(pt)
    return pf, pt


def main() -> None:
    if not BASE.exists():
        sys.exit("ERREUR : assets/video/base.mp4 introuvable (fais d'abord le dérush).")
    fen = fenetres_detourees()
    if not fen:
        sys.exit('ERREUR : aucune section {"detoure": True} dans tools/sections.py.')
    cfg = config()
    bg = ((cfg.get("visual") or {}).get("bg") or "#f7f7f5").lstrip("#")
    montage = cfg.get("montage") or {}
    src, k, repli = face_source(ROOT, BASE, sections.CUTS, sections.DURATION)
    w, h = round(1080 * k), round(1920 * k)
    if repli:
        print(f"  ⚠️ visage moins net (lu en 1080) : {repli}")
    matte()

    tete_src = haut_de_tete()                       # en px de base.mp4 (1080x1920)
    x, haut, larg, rayon = FENETRE
    s = max(larg / 1080, 0.5)                        # la vidéo couvre la fenêtre en largeur
    oy = round(1920 * TETE_HAUT - s * tete_src)
    if oy + s * 1920 < 1920:                          # tête basse dans l'image : on agrandit pour couvrir le bas
        s = (1920 - 1920 * TETE_HAUT) / (1920 - tete_src)
        oy = round(1920 * TETE_HAUT - s * tete_src)
    pw, ph = round(1080 * s / 2) * 2, round(1920 * s / 2) * 2
    ox = round((1080 - pw) / 2)
    print(f"• haut de la tête dans la vidéo : {tete_src / 19.2:.1f} % ; personne à l'échelle {s:.3f}, "
          f"posée en ({ox}, {oy}) ; tête visée à {TETE_HAUT * 100:.1f} %")
    pf, pt = masques()

    # Zoom des cartes numérotées (montage.decorTransform), comme tools/build_faces.py.
    decor_crop = crop_decor(montage)
    zone = scale_crop(decor_crop, k, w, h) if decor_crop else f"{w}:{h}:0:0"
    actif = "+".join(f"between(t,{a:.4f},{b - 0.0001:.4f})" for a, b in fen)
    dur = sections.DURATION
    g = (
        f"[0:v]fps=30,crop={zone},scale=1080:1920:flags=lanczos,setsar=1[zoom];"
        f"[0:v]fps=30,scale={pw}:{ph}:flags=lanczos,setsar=1,format=yuv420p[pers];"
        f"[1:v]fps=30,alphaextract,scale={pw}:{ph}:flags=bicubic,gblur=sigma=1.2,format=gray[mat];"
        f"color=c=black:s=1080x1920:r=30:d={dur:.3f},format=yuv420p[n1];"
        f"color=c=black:s=1080x1920:r=30:d={dur:.3f},format=gray[n2];"
        f"[n1][pers]overlay={ox}:{oy}:shortest=1[pc];"
        f"[n2][mat]overlay={ox}:{oy}:shortest=1,format=gray[mc];"
        f"[2:v]format=gray,loop=-1:1:0,fps=30[fen];"
        f"[3:v]format=gray,loop=-1:1:0,fps=30[tet];"
        f"[mc][tet]blend=all_mode=multiply:shortest=1[mt];"
        f"[mt][fen]blend=all_mode=lighten:shortest=1[alpha];"
        f"[pc]format=yuva420p[pca];[pca][alpha]alphamerge[decoupe];"
        f"color=c=0x{bg}:s=1080x1920:r=30:d={dur:.3f},format=yuv420p[fond];"
        f"[fond][decoupe]overlay=0:0:shortest=1[det];"
        f"[zoom][det]overlay=0:0:enable='{actif}':shortest=1,format=yuv420p[v]"
    )
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-i", str(MATTE), "-i", str(pf), "-i", str(pt),
           "-filter_complex", g, "-map", "[v]", "-t", f"{dur:.3f}", *ENCODE, str(OUT)]
    print(f"• assemblage : {len(fen)} fenêtre(s) détourée(s), le reste en plein visage (zoom {zone})…")
    run(cmd, f"ffmpeg n'a pas pu produire {OUT.relative_to(ROOT)}")
    (MASQUES / "reglage.json").write_text(json.dumps(
        {"fenetre": FENETRE, "teteHaut": TETE_HAUT, "teteSource": round(tete_src, 1), "echelle": round(s, 4),
         "position": [ox, oy], "fenetresDetourees": fen}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {OUT.relative_to(ROOT)} prêt. Ensuite : python3 tools/build_master.py --write")


if __name__ == "__main__":
    main()
