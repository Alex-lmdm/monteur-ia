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
    ou cadrée par montage.decorTransform ;
  - visage-detoure.webm : 1080x1920 transparent, la personne sans son décor (sections « detoure »),
    détourée sur cet ordinateur par `hyperframes remove-background` (la première fois, le modèle de
    170 Mo se télécharge ; ensuite quelques minutes pour un Reel). Refaite seulement si la zone ou le
    dérush changent.

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
from cadrage import crop_decor, crop_detoure, crops, face_source, scale_crop  # noqa: E402
from lieux import config  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "assets/video/base.mp4"
SPLIT_OUT = ROOT / "assets/video/visage-split.mp4"
PLEIN_OUT = ROOT / "assets/video/visage-plein.mp4"
DECOR_OUT = ROOT / "assets/video/visage-decor.mp4"
DETOURE_OUT = ROOT / "assets/video/visage-detoure.webm"
DETOURE_ETAT = ROOT / "assets/video/visage-detoure.json"   # ce qui a été détouré : évite de refaire 3 minutes de calcul
DETOURE_SOURCE = ROOT / "work/visage-detoure-source.mp4"
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


def detourer(src: pathlib.Path, zone: str) -> None:
    """La personne sans son décor : la zone cadrée en 1080x1920, puis le détourage local (vidéo transparente)."""
    import json
    import os
    import shlex
    etat = {"source": str(src.relative_to(ROOT)), "zone": zone, "date": src.stat().st_mtime}
    if DETOURE_OUT.exists() and DETOURE_ETAT.exists():
        try:
            if json.loads(DETOURE_ETAT.read_text(encoding="utf-8")) == etat:
                print(f"• {DETOURE_OUT.relative_to(ROOT)} : déjà détourée (même zone, même dérush)")
                return
        except ValueError:
            pass
    DETOURE_SOURCE.parent.mkdir(exist_ok=True)
    encode(src, f"crop={zone},scale=1080:1920:flags=lanczos,setsar=1", DETOURE_SOURCE)
    # MONTEUR_HYPERFRAMES : une autre commande hyperframes (tests, installation à part).
    hf = shlex.split(os.environ.get("MONTEUR_HYPERFRAMES") or "npx --no-install hyperframes")
    print("• détourage de la personne (la première fois, téléchargement du modèle de 170 Mo)…")
    r = subprocess.run([*hf, "remove-background", str(DETOURE_SOURCE), "-o", str(DETOURE_OUT), "--quality", "balanced"],
                       capture_output=True, encoding="utf-8", errors="replace", cwd=ROOT)
    if r.returncode or not DETOURE_OUT.exists():
        print((r.stderr or r.stdout)[-1500:])
        sys.exit("ERREUR : le détourage a échoué (hyperframes remove-background). Relance ; si ça persiste, "
                 "passe ces sections en « decor ».")
    DETOURE_ETAT.write_text(json.dumps(etat), encoding="utf-8")
    DETOURE_SOURCE.unlink(missing_ok=True)
    print(f"• {DETOURE_OUT.relative_to(ROOT)} : zone {zone} du rush, personne détourée")


def main() -> None:
    if not BASE.exists():
        sys.exit("ERREUR : assets/video/base.mp4 introuvable (fais d'abord le dérush).")
    split_wins, plein_wins = sections.face_windows(), sections.facefull_windows()
    decor_wins = getattr(sections, "decor_windows", lambda: [])()   # un sections.py d'avant n'en a pas
    detoure_wins = getattr(sections, "detoure_windows", lambda: [])()
    montage = config().get("montage") or {}
    face_crop, full_crop = crops(montage)
    decor_crop = crop_decor(montage)
    detoure_crop = crop_detoure(montage)
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
    if detoure_wins:
        detourer(src, scale_crop(detoure_crop, k, w, h) if detoure_crop else f"{w}:{h}:0:0")
    else:
        DETOURE_OUT.unlink(missing_ok=True)
        DETOURE_ETAT.unlink(missing_ok=True)
    print("Ensuite : python3 tools/build_master.py --write (le master pose ces vidéos sans les agrandir).")


if __name__ == "__main__":
    main()
