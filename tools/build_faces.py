#!/usr/bin/env python3
"""VISAGES PRÉ-CADRÉS : prépare, depuis le dérush en pleine résolution, les vidéos du visage déjà
cadrées que le montage pose à l'échelle 1. C'est ce qui rend l'export natif (`hyperframes render`,
bouton Export de l'app HyperFrames) aussi net que l'ancien export ffmpeg.

Usage (depuis le dossier du Reel) :
    python3 tools/build_faces.py
    python3 tools/build_master.py --write      # le master pose alors ces vidéos, sans agrandir

Produit dans assets/video/ :
  - visage-split.mp4 : 1080x1920, le visage cadré dans la moitié basse (sous la jointure, y=920),
    le haut reste noir et caché par le clip-path du master ;
  - visage-plein.mp4 : 1080x1920, le visage plein écran (sections « face ») ;
  - visage-decor.mp4 : 1080x1920, la vidéo filmée posée sous les cartes (sections « decor »), entière
    ou cadrée par montage.decorTransform.

Pourquoi des vidéos plein cadre : une <video> qui ne couvre qu'une partie de l'écran peut ne pas
se peindre dans le studio (bug « carré noir », motion-design/references/visage-carre-noir.md).
La forme éprouvée reste donc « surface plein cadre + clip-path », mais à l'échelle 1 : le
navigateur n'agrandit plus une copie réduite, il affiche les pixels du rush.

Même zone du rush que l'ancien export (tools/cadrage.py). Relancer après tout nouveau dérush ou
changement de cadrage (montage.splitTransform, fullFaceTransform, fullFaceOrigin).
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections  # noqa: E402
from cadrage import crop_decor, crops, face_source, scale_crop  # noqa: E402
from lieux import config  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "assets/video/base.mp4"
SPLIT_OUT = ROOT / "assets/video/visage-split.mp4"
PLEIN_OUT = ROOT / "assets/video/visage-plein.mp4"
DECOR_OUT = ROOT / "assets/video/visage-decor.mp4"
# Fichier de travail quasi sans perte : il est ré-encodé une seule fois, au rendu final.
ENCODE = ["-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p",
          "-an", "-movflags", "+faststart"]


def encode(src: pathlib.Path, filtre: str, out: pathlib.Path) -> None:
    # 30 im/s exactement, la cadence du rendu : une source à 29,97 y est lue avec une image de retard
    # qui varie (l'image affichée est la dernière dont l'horodatage précède l'instant rendu).
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-map", "0:v:0", "-vf", f"{filtre},fps=30", *ENCODE, str(out)]
    r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr[-1500:])
        sys.exit(f"ERREUR : ffmpeg n'a pas pu produire {out.relative_to(ROOT)}.")


def main() -> None:
    if not BASE.exists():
        sys.exit("ERREUR : assets/video/base.mp4 introuvable (fais d'abord le dérush).")
    split_wins, plein_wins = sections.face_windows(), sections.facefull_windows()
    decor_wins = getattr(sections, "decor_windows", lambda: [])()   # un sections.py d'avant n'en a pas
    montage = config().get("montage") or {}
    face_crop, full_crop = crops(montage)
    decor_crop = crop_decor(montage)
    src, k, repli = face_source(ROOT, BASE, sections.CUTS, sections.DURATION)
    w, h = round(1080 * k), round(1920 * k)
    print(f"visage lu dans : {src.relative_to(ROOT)} ({w}x{h})")
    if repli:
        print(f"  ⚠️ visage moins net (lu en 1080) : {repli}")

    if split_wins:
        zone = scale_crop(face_crop, k, w, h)
        encode(src, f"crop={zone},scale=1080:1000:flags=lanczos,setsar=1,pad=1080:1920:0:920:black", SPLIT_OUT)
        print(f"• {SPLIT_OUT.relative_to(ROOT)} : zone {zone} du rush, visage sous la jointure")
    else:
        SPLIT_OUT.unlink(missing_ok=True)
    if plein_wins:
        zone = scale_crop(full_crop, k, w, h)
        encode(src, f"crop={zone},scale=1080:1920:flags=lanczos,setsar=1", PLEIN_OUT)
        print(f"• {PLEIN_OUT.relative_to(ROOT)} : zone {zone} du rush, visage plein écran")
    else:
        PLEIN_OUT.unlink(missing_ok=True)
    if decor_wins:
        zone = scale_crop(decor_crop, k, w, h) if decor_crop else f"{w}:{h}:0:0"
        encode(src, f"crop={zone},scale=1080:1920:flags=lanczos,setsar=1", DECOR_OUT)
        print(f"• {DECOR_OUT.relative_to(ROOT)} : zone {zone} du rush, sous les cartes")
    else:
        DECOR_OUT.unlink(missing_ok=True)
    print("Ensuite : python3 tools/build_master.py --write (le master pose ces vidéos sans les agrandir).")


if __name__ == "__main__":
    main()
