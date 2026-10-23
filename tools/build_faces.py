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
  - visage-decor-zoom-<n>.mp4, visage-plein-zoom-<n>.mp4, visage-split-zoom-<n>.mp4 : la même,
    resserrée pour les sections qui ont un zoom ({"zoom": 1.25} dans la table LAYOUT de tools/sections.py), une vidéo par niveau ;
  - visage-detoure-<n>.webm : 1080x1920 transparent, la personne sans son décor, une vidéo par
    passage détouré (sections « detoure »), détourée sur cet ordinateur par `hyperframes
    remove-background` (la première fois, le modèle de 170 Mo se télécharge ; ensuite environ 8 s de
    calcul par seconde détourée). Seuls les passages montrés sont détourés, et refaits seulement si
    la zone, le dérush ou les passages changent.

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
from cadrage import (COPIE, copie_zoom, crop_decor, crop_detoure, crops, face_source, fenetres_zoom,  # noqa: E402
                     niveaux_zoom, scale_crop, zoom_crop)
from lieux import config  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "assets/video/base.mp4"
SPLIT_OUT = ROOT / "assets/video/visage-split.mp4"
PLEIN_OUT = ROOT / "assets/video/visage-plein.mp4"
DECOR_OUT = ROOT / "assets/video/visage-decor.mp4"
DETOURE_DOSSIER = ROOT / "assets/video"
DETOURE_ETAT = ROOT / "assets/video/visage-detoure.json"   # ce qui a été détouré : évite de refaire le calcul
DETOURE_SOURCE = ROOT / "work/visage-detoure-source.mp4"


def detoure_out(n: int) -> pathlib.Path:
    """La vidéo transparente du n-ième passage détouré (fenêtres « detoure » fusionnées)."""
    return DETOURE_DOSSIER / f"visage-detoure-{n}.webm"


def effacer_detoures() -> None:
    for f in DETOURE_DOSSIER.glob("visage-detoure*.webm"):
        f.unlink()
    DETOURE_ETAT.unlink(missing_ok=True)
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


def detourer(src: pathlib.Path, zone: str, fenetres) -> None:
    """La personne sans son décor, passage par passage : chaque fenêtre « detoure » coupée dans le rush,
    cadrée en 1080x1920, puis détourée en local (vidéo transparente qui démarre au début du passage)."""
    import json
    import os
    import shlex
    etat = {"source": str(src.relative_to(ROOT)), "zone": zone, "date": src.stat().st_mtime,
            "fenetres": [[round(st, 3), round(d, 3)] for st, d in fenetres]}
    if DETOURE_ETAT.exists() and all(detoure_out(n).exists() for n in range(len(fenetres))):
        try:
            if json.loads(DETOURE_ETAT.read_text(encoding="utf-8")) == etat:
                print(f"• personne déjà détourée ({len(fenetres)} passage(s), même zone, même dérush)")
                return
        except ValueError:
            pass
    effacer_detoures()
    DETOURE_SOURCE.parent.mkdir(exist_ok=True)
    # MONTEUR_HYPERFRAMES : une autre commande hyperframes (tests, installation à part).
    hf = shlex.split(os.environ.get("MONTEUR_HYPERFRAMES") or "npx --no-install hyperframes")
    total = sum(d for _, d in fenetres)
    print(f"• détourage de la personne : {len(fenetres)} passage(s), {total:.1f} s (environ {round(total * 8 / 60) or 1} "
          "min ; la première fois, téléchargement du modèle de 170 Mo)…")
    for n, (st, d) in enumerate(fenetres):
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{st:.4f}", "-t", f"{d:.4f}", "-i", str(src), "-map", "0:v:0",
               "-vf", f"crop={zone},scale=1080:1920:flags=lanczos,setsar=1,fps=30", *ENCODE, str(DETOURE_SOURCE)]
        r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
        if r.returncode:
            print(r.stderr[-1500:])
            sys.exit("ERREUR : ffmpeg n'a pas pu couper le passage à détourer.")
        out = detoure_out(n)
        r = subprocess.run([*hf, "remove-background", str(DETOURE_SOURCE), "-o", str(out), "--quality", "balanced"],
                           capture_output=True, encoding="utf-8", errors="replace", cwd=ROOT)
        if r.returncode or not out.exists():
            print((r.stderr or r.stdout)[-1500:])
            sys.exit("ERREUR : le détourage a échoué (hyperframes remove-background). Relance ; si ça persiste, "
                     "passe ces sections en « decor ».")
        print(f"• {out.relative_to(ROOT)} : {st:.2f} s, {d:.2f} s, zone {zone} du rush, personne détourée")
    DETOURE_ETAT.write_text(json.dumps(etat), encoding="utf-8")
    DETOURE_SOURCE.unlink(missing_ok=True)


def zooms(fmt: str, base_crop, fenetres, src, k, w, h) -> None:
    """Une vidéo pré-cadrée par niveau de zoom du format (sections {"zoom": …}) ; les anciennes s'effacent."""
    niveaux = niveaux_zoom(fenetres)
    for vieux in (ROOT / "assets/video").glob(f"visage-{COPIE[fmt]}-zoom-*.mp4"):
        if vieux.name not in {pathlib.Path(copie_zoom(fmt, n)).name for n in range(len(niveaux))}:
            vieux.unlink()
    for n, (z, origine) in enumerate(niveaux):
        zone, ajuste = zoom_crop(base_crop, z, origine)
        out = ROOT / copie_zoom(fmt, n)
        cadre = ("scale=1080:1000:flags=lanczos,setsar=1,pad=1080:1920:0:920:black" if fmt == "split"
                 else "scale=1080:1920:flags=lanczos,setsar=1")
        encode(src, f"crop={scale_crop(zone, k, w, h)},{cadre}", out)
        print(f"• {out.relative_to(ROOT)} : zoom {z:g} autour de « {origine} », zone {zone} de base.mp4")
        if ajuste:
            print(f"  ⚠️ zoom {z:g} : la zone sortait de l'image filmée, elle est ramenée dedans "
                  "(un zoom sous 1 ne montre jamais plus que la vidéo filmée)")


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
    zooms("split", face_crop, fenetres_zoom(sections, "split"), src, k, w, h)
    if plein_wins:
        zone = scale_crop(full_crop, k, w, h)
        encode(src, f"crop={zone},scale=1080:1920:flags=lanczos,setsar=1", PLEIN_OUT)
        print(f"• {PLEIN_OUT.relative_to(ROOT)} : zone {zone} du rush, visage plein écran")
    else:
        PLEIN_OUT.unlink(missing_ok=True)
    zooms("face", full_crop, fenetres_zoom(sections, "face"), src, k, w, h)
    if decor_wins:
        zone = scale_crop(decor_crop, k, w, h) if decor_crop else f"{w}:{h}:0:0"
        encode(src, f"crop={zone},scale=1080:1920:flags=lanczos,setsar=1", DECOR_OUT)
        print(f"• {DECOR_OUT.relative_to(ROOT)} : zone {zone} du rush, sous les cartes")
    else:
        DECOR_OUT.unlink(missing_ok=True)
    zooms("decor", decor_crop, fenetres_zoom(sections, "decor"), src, k, w, h)
    if detoure_wins:
        detourer(src, scale_crop(detoure_crop, k, w, h) if detoure_crop else f"{w}:{h}:0:0", detoure_wins)
    else:
        effacer_detoures()
    print("Ensuite : python3 tools/build_master.py --write (le master pose ces vidéos sans les agrandir).")


if __name__ == "__main__":
    main()
